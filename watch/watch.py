"""GAIP Watch for GitHub Actions: has anything my agent depends on changed since the last look?

Calls GAIP's free dependency check (POST /v1/free/watch/check) with the URLs the workflow names, prints one
annotation per target that changed (error for a breaking class, notice otherwise), writes a job summary and the
full JSON answer to a file, and exits non-zero when a breaking change was recorded (configurable).

Facts GAIP recorded, never a verdict: a changed tool list is not a sign of wrongdoing; the decision stays with
you. No account or secret is needed. A GAIP continuity handle (issued on the first completed answer) is kept in
the Actions cache, or passed in as a repository secret, so your runs are linked; it is never printed.
Standard library only.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_ENDPOINT = "https://www.gaipagents.com/v1/free/watch/check"
USER_AGENT = "gaip-watch-action-client/1.0"
RESULT_FILE = ".gaip-watch/result.json"
MAX_URLS = 25
_DAYS = re.compile(r"^(\d{1,3})d$")


class WatchError(RuntimeError):
    pass


def _truthy(value: str | None, default: bool) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_urls(raw: str | None) -> list[str]:
    urls: list[str] = []
    for part in re.split(r"[\s,]+", raw or ""):
        part = part.strip()
        if part and part not in urls:
            urls.append(part)
    if not urls:
        raise WatchError("Input `urls` is required: the public https:// URLs your agent depends on.")
    if len(urls) > MAX_URLS:
        raise WatchError(f"At most {MAX_URLS} urls per run (got {len(urls)}).")
    bad = [u for u in urls if not u.startswith("https://")]
    if bad:
        raise WatchError(f"Every url must start with https://: {bad[0]}")
    return urls


def parse_since(raw: str | None, now: datetime | None = None) -> str:
    """'7d' -> the RFC 3339 time 7 days ago; a date or RFC 3339 time passes through."""
    value = (raw or "7d").strip()
    now = now or datetime.now(timezone.utc)
    match = _DAYS.match(value)
    if match:
        return (now - timedelta(days=int(match.group(1)))).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return value


def load_handle(env: dict[str, str]) -> Any:
    raw = (env.get("GAIP_WATCH_CONTINUITY") or "").strip()
    if raw:
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise WatchError("continuity-handle must be the JSON object GAIP returned.") from exc
    path = env.get("GAIP_WATCH_CONTINUITY_FILE")
    if path and Path(path).is_file():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def save_handle(env: dict[str, str], result: dict[str, Any]) -> None:
    """Keep the handle GAIP issued (never printed) for the cache step, unless one came from a secret."""
    if (env.get("GAIP_WATCH_CONTINUITY") or "").strip():
        return
    handle = result.get("continuity_handle")
    path = env.get("GAIP_WATCH_CONTINUITY_FILE")
    if not path or not isinstance(handle, dict):
        return
    target = Path(path)
    if target.is_file():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(handle), encoding="utf-8")


def request_check(urls: list[str], since: str, *, capture_unknown: bool, handle: Any = None,
                  endpoint: str = DEFAULT_ENDPOINT, timeout: float = 60.0,
                  opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    body: dict[str, Any] = {"urls": urls, "since": since, "capture_unknown": capture_unknown}
    if isinstance(handle, dict):
        body["continuity_handle"] = handle
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(endpoint, data=data, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
            status = getattr(response, "status", 200)
    except urllib.error.HTTPError as exc:
        raw, status = exc.read(), exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise WatchError(f"GAIP could not be reached: {exc}") from exc
    try:
        result = json.loads(raw.decode("utf-8") or "null")
    except ValueError as exc:
        raise WatchError(f"GAIP answered HTTP {status} without JSON.") from exc
    if not isinstance(result, dict):
        raise WatchError(f"GAIP answered HTTP {status} with an unexpected body.")
    if status == 429:
        raise WatchError(f"GAIP rate limit reached; retry after {result.get('retry_after_s')} seconds.")
    return result


def _escape(text: str) -> str:
    return str(text).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def report(result: dict[str, Any], out: Callable[[str], None] = print) -> None:
    for row in result.get("targets") or []:
        url, state = row.get("url"), row.get("state")
        classes = ", ".join(row.get("change_classes") or [])
        receipts = ", ".join(c.get("receipt_url") for c in (row.get("changes") or []) if c.get("receipt_url"))
        if row.get("breaking"):
            out(f"::error title=GAIP Watch breaking change::{_escape(url)}: {_escape(', '.join(row.get('breaking_classes') or []))}"
                f" recorded since {_escape(result.get('since'))}. All classes: {_escape(classes)}. Receipts: {_escape(receipts or 'see history link')}")
        elif classes:
            out(f"::notice title=GAIP Watch change recorded::{_escape(url)}: {_escape(classes)} (not in the breaking set). Receipts: {_escape(receipts or 'see history link')}")
        elif row.get("known") is False:
            out(f"::notice title=GAIP Watch no record yet::{_escape(url)}: {_escape(state)}"
                + (" (first record saved now)" if state == "FIRST_RECORD_SAVED_NOW" else " (set capture-unknown: true to save one)"))
    summary = result.get("summary") or {}
    out(f"GAIP Watch: {summary.get('checked', 0)} checked, {summary.get('changed', 0)} changed, "
        f"{summary.get('breaking', 0)} breaking, {summary.get('unknown', 0)} unknown since {result.get('since')}.")
    out(str(result.get("meaning") or ""))


def _class_count(result: dict[str, Any], change_class: str) -> int:
    """Targets whose change classes since the date include ``change_class`` (counted from the rows, so an older GAIP
    answer without the summary field still gives a number)."""
    summary = result.get("summary") or {}
    key = {"declared_ingredients_changed": "ingredients_changed", "hosting_changed": "hosting_changed"}.get(change_class)
    if key and isinstance(summary.get(key), int):
        return summary[key]
    return sum(1 for row in result.get("targets") or [] if change_class in (row.get("change_classes") or []))


def _write_outputs(result: dict[str, Any], env: dict[str, str], result_file: str) -> None:
    summary = result.get("summary") or {}
    path = env.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"breaking={'true' if result.get('breaking') else 'false'}\n")
            fh.write(f"changed={summary.get('changed', 0)}\n")
            fh.write(f"unknown={summary.get('unknown', 0)}\n")
            # Round two (decision #52, 9 Oct 2026): the two informational classes as their own outputs, beside breaking
            fh.write(f"ingredients-changed={_class_count(result, 'declared_ingredients_changed')}\n")
            fh.write(f"hosting-changed={_class_count(result, 'hosting_changed')}\n")
            fh.write(f"result-file={result_file}\n")
    summary_path = env.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        lines = ["## GAIP Watch", "",
                 f"Since {result.get('since')}: {summary.get('checked', 0)} dependencies checked, "
                 f"{summary.get('changed', 0)} changed, **{summary.get('breaking', 0)} breaking**, "
                 f"{summary.get('unknown', 0)} without a record yet.", "",
                 "| Dependency | State | Change classes since | Last change (UTC) |", "| --- | --- | --- | --- |"]
        for row in result.get("targets") or []:
            lines.append(f"| {row.get('url')} | {row.get('state')} | {', '.join(row.get('change_classes') or []) or '-'} "
                         f"| {row.get('last_change_at_utc') or '-'} |")
        lines += ["", str(result.get("meaning") or ""), "",
                  f"Method and corrections: {(result.get('links') or {}).get('page', 'https://www.gaipagents.com/watch')}"]
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def main(env: dict[str, str] | None = None, opener: Callable[..., Any] = urllib.request.urlopen,
         out: Callable[[str], None] = print, now: datetime | None = None) -> int:
    env = dict(os.environ if env is None else env)
    try:
        urls = parse_urls(env.get("GAIP_WATCH_URLS"))
        since = parse_since(env.get("GAIP_WATCH_SINCE"), now)
        timeout = float(env.get("GAIP_WATCH_TIMEOUT_SECONDS") or 60)
        result = request_check(urls, since, capture_unknown=_truthy(env.get("GAIP_WATCH_CAPTURE_UNKNOWN"), True),
                               handle=load_handle(env), endpoint=env.get("GAIP_WATCH_ENDPOINT") or DEFAULT_ENDPOINT,
                               timeout=timeout, opener=opener)
    except WatchError as exc:
        out(f"::error title=GAIP Watch not completed::{_escape(str(exc))}")
        return 2
    result_file = env.get("GAIP_WATCH_RESULT_FILE") or RESULT_FILE
    Path(result_file).parent.mkdir(parents=True, exist_ok=True)
    Path(result_file).write_text(json.dumps({k: v for k, v in result.items() if k != "continuity_handle"},
                                            indent=2, sort_keys=True), encoding="utf-8")
    if result.get("status") == "BLOCKED":
        out(f"::error title=GAIP Watch refused::{_escape(result.get('error'))}: {_escape(result.get('message') or '')}")
        return 2
    save_handle(env, result)
    report(result, out)
    _write_outputs(result, env, result_file)
    summary = result.get("summary") or {}
    if result.get("breaking") and _truthy(env.get("GAIP_WATCH_FAIL_ON_BREAKING"), True):
        return 1
    if summary.get("unknown") and _truthy(env.get("GAIP_WATCH_FAIL_ON_UNKNOWN"), False):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
