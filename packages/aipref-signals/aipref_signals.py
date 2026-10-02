"""aipref-signals: parse machine-readable AI-preference signals. One file, Python 3.9+, no dependencies, no network.

Four families of signal a site can publish to say what AI systems may do with its content:

* **IETF AI preferences** (aipref working group). Vocabulary: draft-ietf-aipref-vocab-08 (14 Sep 2026), labels
  ``train-ai``, ``ai-use`` and ``search``, values ``y`` / ``n``, serialised as an RFC 9651 Structured Fields
  Dictionary (labels are case sensitive, unknown labels are ignored, the last duplicate wins, a dictionary that
  does not parse means the preferences are unknown). Attachment: draft-ietf-aipref-attach-05 (19 Aug 2026), the
  ``Content-Usage`` HTTP header field and the ``Content-Usage:`` robots.txt rule (an optional path, whitespace,
  then the preference, inside a user-agent group). ``usage_preferences`` and ``robots_content_usage`` follow
  these drafts; the drafts may still change, so ``FOLLOWS`` names the versions.
* **RSL 1.0** (Really Simple Licensing): a ``License:`` line in robots.txt, a ``Link: <...>; rel="license";
  type="application/rsl+xml"`` response header, or the same ``<link>`` element in an HTML page (the inline
  ``<script type="application/rsl+xml">`` form is not read). Only https URLs of at most 300 characters are
  kept; the licence file itself is not read.
* **W3C TDMRep** (TDM Reservation Protocol, Final Community Group Report): ``/.well-known/tdmrep.json`` and the
  ``TDM-Reservation`` / ``TDM-Policy`` response headers.
* **Content Signals** (the Content Signals Policy, contentsignals.org): ``Content-Signal:`` lines in robots.txt
  with ``search``, ``ai-input`` and ``ai-train`` set to ``yes`` / ``no``.

Two layers. ``robots_signals`` / ``header_signals`` / ``usage_preferences`` are the standards-following view.
The lower-level functions (``parse_usage``, ``content_usage_from_robots``, ``content_signals``,
``rsl_from_robots``, ``rsl_from_link_header``, ``rsl_from_html``, ``tdmrep_facts``) are the lenient readers
the GAIP Agent Observatory has recorded with since 2 Oct 2026; their output is frozen so that recorded rows keep
the same hash, and the test vectors pin it.

A parse is a fact about the text read at the stated time; it is not legal advice and says nothing about any
site's intent. MIT licence (see LICENSE beside this file in the public copy). Maintained by GAIP
(https://www.gaipagents.com).
"""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urljoin, urlparse

__version__ = "0.1.0"
FOLLOWS = {
    "aipref_vocab": "draft-ietf-aipref-vocab-08 (14 Sep 2026)",
    "aipref_attach": "draft-ietf-aipref-attach-05 (19 Aug 2026)",
    "rsl": "RSL 1.0 (RSL-SPEC-1.0, 10 Dec 2025)",
    "tdmrep": "W3C TDM Reservation Protocol, Final Community Group Report",
    "content_signals": "Content Signals Policy (contentsignals.org)",
}
AIPREF_LABELS = ("train-ai", "ai-use", "search")      # draft-ietf-aipref-vocab-08, section 4
AIPREF_VALUES = ("y", "n")
SIGNAL_KEYS = ("search", "ai-input", "ai-train")      # Content Signals Policy
RSL_TYPE = "application/rsl+xml"
TDMREP_PATH = "/.well-known/tdmrep.json"
MAX_ITEMS = 5
MAX_LINES = 5000
URL_MAX = 300
EXCERPT_MAX = 300

_LICENSE_LINE = re.compile(r"^\s*license\s*:\s*(\S+)", re.IGNORECASE)
_USAGE_LINE = re.compile(r"^\s*content-usage\s*:\s*(.+)$", re.IGNORECASE)
_SIGNAL_LINE = re.compile(r"^\s*content-signal\s*:\s*(.+)$", re.IGNORECASE)
_PAIR_KEY = re.compile(r"^[a-z][a-z0-9-]{0,29}$")
_LINK_TAG = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
_ATTR = re.compile(r"""([a-zA-Z-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""")


def excerpt(value: Any) -> str | None:
    """Whitespace collapsed, at most 300 characters; ``None`` when empty."""
    text = " ".join(str(value or "").split())
    return text[:EXCERPT_MAX] if text else None


def https_url(value: str, base: str | None = None) -> str | None:
    """An absolute https URL (relative values resolved against ``base``), no userinfo, at most 300 characters."""
    text = (value or "").strip().strip("<>")
    if base and text and "://" not in text:
        text = urljoin(base, text)
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.hostname or "@" in parsed.netloc or len(text) > URL_MAX:
        return None
    return text


# --------------------------------------------------------------------------- RFC 9651 dictionary (for aipref)

_KEY_FIRST = set("abcdefghijklmnopqrstuvwxyz*")
_KEY_REST = _KEY_FIRST | set("0123456789_-.")
_TCHAR = set("!#$%&'*+-.^_`|~0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ:/")
_B64 = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")


class _SFError(ValueError):
    pass


class _Reader:
    def __init__(self, text: str) -> None:
        self.s, self.i = text, 0

    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def take(self) -> str:
        ch = self.peek()
        self.i += 1
        return ch

    def skip(self, chars: str) -> None:
        while self.peek() and self.peek() in chars:
            self.i += 1

    def key(self) -> str:
        if self.peek() not in _KEY_FIRST or not self.peek():
            raise _SFError("key")
        start = self.i
        while self.peek() and self.peek() in _KEY_REST:
            self.i += 1
        return self.s[start:self.i]

    def bare_item(self) -> Any:
        ch = self.peek()
        if ch == "-" or ch.isdigit() and ch.isascii():
            return self.number()
        if ch == '"':
            return self.string()
        if ch == "*" or ch.isascii() and ch.isalpha():
            start = self.i
            self.i += 1
            while self.peek() and self.peek() in _TCHAR:
                self.i += 1
            return ("token", self.s[start:self.i])
        if ch == ":":
            self.i += 1
            start = self.i
            while self.peek() and self.peek() in _B64:
                self.i += 1
            if self.take() != ":":
                raise _SFError("bytes")
            return ("bytes", self.s[start:self.i - 1])
        if ch == "?":
            self.i += 1
            value = self.take()
            if value not in ("0", "1"):
                raise _SFError("boolean")
            return value == "1"
        if ch == "@":
            self.i += 1
            number = self.number()
            if not isinstance(number, int):
                raise _SFError("date")
            return ("date", number)
        if ch == "%":
            self.i += 1
            return ("display", self.display())
        raise _SFError("item")

    def number(self) -> Any:
        start = self.i
        if self.peek() == "-":
            self.i += 1
        digits = self.i
        while self.peek().isdigit() and self.peek().isascii():
            self.i += 1
        whole = self.i - digits
        if whole == 0:
            raise _SFError("number")
        if self.peek() != ".":
            if whole > 15:
                raise _SFError("integer")
            return int(self.s[start:self.i])
        if whole > 12:
            raise _SFError("decimal")
        self.i += 1
        frac = self.i
        while self.peek().isdigit() and self.peek().isascii():
            self.i += 1
        if not 1 <= self.i - frac <= 3:
            raise _SFError("decimal")
        return float(self.s[start:self.i])

    def string(self) -> str:
        self.i += 1
        out = []
        while True:
            ch = self.take()
            if ch == "":
                raise _SFError("string")
            if ch == "\\":
                nxt = self.take()
                if nxt not in ('"', "\\"):
                    raise _SFError("escape")
                out.append(nxt)
            elif ch == '"':
                return "".join(out)
            elif not " " <= ch <= "~":
                raise _SFError("string")
            else:
                out.append(ch)

    def display(self) -> str:
        if self.take() != '"':
            raise _SFError("display")
        raw = bytearray()
        while True:
            ch = self.take()
            if ch == "":
                raise _SFError("display")
            if ch == '"':
                try:
                    return raw.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise _SFError("display") from exc
            if ch == "%":
                pair = self.s[self.i:self.i + 2]
                if len(pair) != 2 or any(c not in "0123456789abcdef" for c in pair):
                    raise _SFError("display")
                raw.append(int(pair, 16))
                self.i += 2
            elif not " " <= ch <= "~":
                raise _SFError("display")
            else:
                raw.append(ord(ch))

    def parameters(self) -> dict[str, Any]:
        params: dict[str, Any] = {}
        while self.peek() == ";":
            self.i += 1
            self.skip(" ")
            name = self.key()
            value: Any = True
            if self.peek() == "=":
                self.i += 1
                value = self.bare_item()
            params[name] = value
        return params

    def item_or_list(self) -> tuple[Any, dict[str, Any]]:
        if self.peek() == "(":
            self.i += 1
            items = []
            while True:
                self.skip(" ")
                if self.peek() == ")":
                    self.i += 1
                    return ("list", items), self.parameters()
                items.append((self.bare_item(), self.parameters()))
                if self.peek() not in (" ", ")"):
                    raise _SFError("inner list")
        return self.bare_item(), self.parameters()


def parse_sf_dictionary(text: str) -> dict[str, tuple[Any, dict[str, Any]]] | None:
    """An RFC 9651 Dictionary as ``{key: (value, parameters)}``; ``None`` when it does not parse.

    Tokens come back as ``("token", text)``; the last of a duplicated key wins."""
    reader = _Reader(str(text or ""))
    reader.skip(" ")
    out: dict[str, tuple[Any, dict[str, Any]]] = {}
    try:
        while reader.peek():
            name = reader.key()
            if reader.peek() == "=":
                reader.i += 1
                member = reader.item_or_list()
            else:
                member = (True, reader.parameters())
            out[name] = member          # RFC 9651: a repeated key overwrites the earlier value
            reader.skip(" \t")
            if not reader.peek():
                break
            if reader.take() != ",":
                raise _SFError("separator")
            reader.skip(" \t")
            if not reader.peek():
                raise _SFError("trailing comma")
    except _SFError:
        return None
    return out


def usage_preferences(value: str) -> dict[str, Any] | None:
    """An aipref usage preference (header value or robots.txt rule value) under draft-ietf-aipref-vocab-08.

    ``{"prefs": {label: "y"|"n"}, "ignored": [...]}``: ``prefs`` holds the known labels with a ``y`` or ``n``
    token; ``ignored`` lists keys that are unknown labels or carry another value. ``None`` when the text is not
    a Structured Fields Dictionary (the preferences are then unknown, as the draft says)."""
    parsed = parse_sf_dictionary(str(value or "").strip(" \t"))
    if parsed is None:
        return None
    prefs: dict[str, str] = {}
    ignored: list[str] = []
    for name, (item, _params) in parsed.items():
        if name in AIPREF_LABELS and isinstance(item, tuple) and item[0] == "token" and item[1] in AIPREF_VALUES:
            prefs[name] = item[1]
        else:
            ignored.append(name)
    return {"prefs": prefs, "ignored": ignored}


# --------------------------------------------------------------------------- robots.txt, standards view

def robots_rules(text: str) -> list[tuple[list[str], str, str]]:
    """``(user_agents, name, value)`` for each non-user-agent line of a robots.txt file, comments removed.

    Groups follow RFC 9309: consecutive ``User-agent`` lines open a group; rules before any group get ``[]``
    (sitewide lines such as ``Sitemap:`` and ``License:``). Rule names are lower-cased (RFC 9309 matches them
    without regard to case)."""
    rules: list[tuple[list[str], str, str]] = []
    agents: list[str] = []
    in_agents = False
    for line in str(text or "").splitlines()[:MAX_LINES]:
        name, sep, value = line.split("#", 1)[0].partition(":")
        name = name.strip().lower()
        if not sep or not name:
            continue
        value = value.strip(" \t")
        if name == "user-agent":
            agents = agents + [value] if in_agents else [value]
            in_agents = True
            continue
        in_agents = False
        rules.append((list(agents), name, value))
    return rules


def robots_content_usage(text: str) -> list[dict[str, Any]]:
    """``Content-Usage`` rules (draft-ietf-aipref-attach-05, section 3.2) with their group and optional path.

    Each: ``{"user_agents", "path", "prefs", "ignored"}``; ``prefs`` is ``None`` when the preference did not
    parse (unknown preferences) or was missing."""
    found: list[dict[str, Any]] = []
    for agents, name, value in robots_rules(text):
        if name != "content-usage":
            continue
        path = None
        if value.startswith("/"):
            parts = re.split(r"[ \t]+", value, maxsplit=1)
            path, value = parts[0], (parts[1] if len(parts) > 1 else "")
        parsed = usage_preferences(value) if value else None
        found.append({"user_agents": agents, "path": path, "prefs": parsed["prefs"] if parsed else None,
                      "ignored": parsed["ignored"] if parsed else []})
    return found


def robots_content_signals(text: str) -> list[dict[str, Any]]:
    """``Content-Signal`` lines with their group: ``{"user_agents", "signals": {key: "yes"|"no"}}``.

    Only the policy's three keys with ``yes`` or ``no`` (compared without regard to case) are kept."""
    found: list[dict[str, Any]] = []
    for agents, name, value in robots_rules(text):
        if name != "content-signal":
            continue
        signals: dict[str, str] = {}
        for pair in value.split(","):
            key, sep, val = pair.partition("=")
            key, val = key.strip().lower(), val.strip().lower()
            if sep and key in SIGNAL_KEYS and val in ("yes", "no"):
                signals[key] = val
        found.append({"user_agents": agents, "signals": signals})
    return found


def robots_signals(text: str, host: str) -> dict[str, Any]:
    """All four families as found in one robots.txt file (standards view)."""
    return {"follows": dict(FOLLOWS), "content_usage": robots_content_usage(text),
            "content_signals": robots_content_signals(text), "rsl_licences": rsl_from_robots(text, host)}


def header_signals(headers: dict[str, str], host: str) -> dict[str, Any]:
    """AI-preference signals in one response's headers (names compared without regard to case)."""
    lowered = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    usage = lowered.get("content-usage")
    reservation = lowered.get("tdm-reservation")
    return {"follows": dict(FOLLOWS),
            "content_usage": usage_preferences(usage) if usage is not None else None,
            "rsl_licences": rsl_from_link_header(lowered.get("link") or "", f"https://{host}/"),
            "tdm_reservation": reservation.strip() if reservation is not None else None,
            "tdm_policy": https_url(lowered.get("tdm-policy") or "")}


# --------------------------------------------------------------------------- the recorded (lenient) readers
# Output frozen: GAIP's ai_permissions rows hash these values (see the test vectors, "recorded" cases).

def rsl_from_robots(text: str, host: str) -> list[str]:
    """``License:`` directives (RSL 1.0) in a robots.txt file, as absolute https URLs."""
    found: list[str] = []
    for line in text.splitlines()[:MAX_LINES]:
        match = _LICENSE_LINE.match(line.split("#", 1)[0])
        url = https_url(match.group(1), f"https://{host}/") if match else None
        if url and url not in found:
            found.append(url)
        if len(found) >= MAX_ITEMS:
            break
    return found


def parse_usage(value: str) -> dict[str, Any] | None:
    """One Content-Usage value, leniently: an optional leading path, then ``key=value`` pairs (comma or space
    separated, lower-cased, any key). The recorded form; ``usage_preferences`` is the draft's reading."""
    text = value.split("#", 1)[0].strip()
    path = None
    if text.startswith("/"):
        path, _sep, text = text.partition(" ")
        path = path[:120]
    prefs: dict[str, str] = {}
    for pair in re.split(r"[,\s]+", text):
        key, sep, val = pair.partition("=")
        key = key.strip().lower()
        if sep and _PAIR_KEY.match(key) and len(prefs) < 10:
            prefs[key] = val.strip().strip('"').lower()[:10]
    if not prefs:
        return None
    return {"path": path, "prefs": prefs} if path else {"prefs": prefs}


def content_usage_from_robots(text: str) -> tuple[list[dict[str, Any]], str | None]:
    """Distinct lenient ``Content-Usage`` rules of a robots.txt file (at most five) and an excerpt of the lines."""
    rules: list[dict[str, Any]] = []
    lines: list[str] = []
    for line in text.splitlines()[:MAX_LINES]:
        match = _USAGE_LINE.match(line.split("#", 1)[0])
        if not match:
            continue
        lines.append(line.strip())
        parsed = parse_usage(match.group(1))
        if parsed and parsed not in rules:
            rules.append(parsed)
        if len(rules) >= MAX_ITEMS:
            break
    return rules, excerpt(" | ".join(lines[:MAX_ITEMS]))


def content_signals(text: str) -> list[dict[str, str]]:
    """Distinct ``Content-Signal`` value sets of a robots.txt file (at most five), the policy's keys only."""
    found = []
    for line in text.splitlines()[:MAX_LINES]:
        match = _SIGNAL_LINE.match(line.split("#", 1)[0])
        if not match:
            continue
        values = {}
        for pair in match.group(1).split(","):
            key, _sep, value = pair.partition("=")
            key = key.strip().lower()
            if key in SIGNAL_KEYS:
                values[key] = value.strip().lower()[:10]
        if values and values not in found:
            found.append(values)
        if len(found) >= MAX_ITEMS:
            break
    return found


def content_signal_lines(text: str) -> list[str]:
    """The ``Content-Signal`` lines of a robots.txt file, stripped (for an excerpt)."""
    return [line.strip() for line in text.splitlines()[:MAX_LINES] if _SIGNAL_LINE.match(line.split("#", 1)[0])]


def rsl_from_link_header(value: str, base: str) -> list[str]:
    """RSL licence URLs in a ``Link`` header (``rel="license"`` with ``type="application/rsl+xml"``)."""
    found: list[str] = []
    for part in re.split(r",(?=\s*<)", value or ""):
        target, _sep, params = part.partition(">")
        lowered = params.lower().replace(" ", "")
        if 'rel="license"' in lowered or "rel=license" in lowered:
            if RSL_TYPE in lowered:
                url = https_url(target.strip().lstrip("<"), base)
                if url and url not in found:
                    found.append(url)
    return found[:MAX_ITEMS]


def rsl_from_html(body: bytes, host: str, path: str) -> list[str]:
    """``<link rel="license" type="application/rsl+xml" href>`` in the first 64 KiB of an HTML page."""
    text = body[:64 * 1024].decode("utf-8", errors="replace")
    found: list[str] = []
    for tag in _LINK_TAG.findall(text)[:500]:
        attrs = {m.group(1).lower(): (m.group(2) or m.group(3) or m.group(4) or "") for m in _ATTR.finditer(tag)}
        if "license" in attrs.get("rel", "").lower().split() and attrs.get("type", "").lower() == RSL_TYPE:
            url = https_url(attrs.get("href", ""), f"https://{host}{path}")
            if url and url not in found:
                found.append(url)
        if len(found) >= MAX_ITEMS:
            break
    return found


def _json_body(body: bytes) -> Any:
    try:
        return json.loads((body or b"").decode("utf-8"))
    except (UnicodeDecodeError, ValueError, RecursionError):
        return None


def _covers_site(location: Any) -> bool:
    text = str(location or "").strip()
    return text in {"", "/", "/*", "*", "/**"}


def tdmrep_facts(status: Any, body: bytes) -> dict[str, Any]:
    """A ``/.well-known/tdmrep.json`` response: published, rule count, whether a rule covering the whole site
    reserves TDM rights, whether any rule does, and the policy URLs' hosts."""
    if not isinstance(status, int) or not 200 <= status < 300:
        return {"s": status, "p": 0}
    document = _json_body(body)
    if not isinstance(document, list):
        return {"s": status, "p": 0, "malformed": True}
    rules = [r for r in document[:200] if isinstance(r, dict)]
    site = [r for r in rules if _covers_site(r.get("location"))]
    policy_hosts = sorted({(urlparse(str(r.get("tdm-policy"))).hostname or "").lower()
                           for r in rules if r.get("tdm-policy")} - {""})[:5]
    return {"s": status, "p": 1, "rules": len(rules),
            "site_reserved": any(str(r.get("tdm-reservation")) == "1" for r in site) if site else None,
            "any_reserved": any(str(r.get("tdm-reservation")) == "1" for r in rules),
            "policy_hosts": policy_hosts}
