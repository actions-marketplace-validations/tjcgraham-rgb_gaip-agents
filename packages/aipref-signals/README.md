# aipref-signals

A small parser for the machine-readable signals a website can publish to say what AI systems may do with
its content, with a table of conformance test vectors. One Python file, Python 3.9 or later, no
dependencies, no network access. MIT licence.

About GAIP: GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment. What it answers, by who asks: https://www.gaipagents.com/v1/free/map. GAIP uses this parser to record what each site's signals said on a date (`gaip_record_permissions`).

| Signal | Where | Version followed |
| --- | --- | --- |
| IETF AI preferences | `Content-Usage` header and robots.txt rule | draft-ietf-aipref-vocab-08 (14 Sep 2026), draft-ietf-aipref-attach-05 (19 Aug 2026) |
| RSL | robots.txt `License:`, `Link` header, HTML `<link rel="license">` (not the inline `<script>` form) | RSL 1.0 (RSL-SPEC-1.0, 10 Dec 2025) |
| W3C TDMRep | `/.well-known/tdmrep.json`, `TDM-Reservation` header | Final Community Group Report |
| Content Signals | robots.txt `Content-Signal:` | Content Signals Policy |

The aipref drafts are still changing. `aipref_signals.FOLLOWS` names the versions this release follows,
and the test vectors record what each version means for edge cases.

## Use

```python
import aipref_signals as ap

ap.usage_preferences("train-ai=n, search=y")
# {'prefs': {'train-ai': 'n', 'search': 'y'}, 'ignored': []}

ap.usage_preferences("Train-AI=n")      # uppercase keys: the preferences are unknown
# None

ap.robots_signals(robots_txt_text, "example.com")
# {'follows': {...}, 'content_usage': [...], 'content_signals': [...], 'rsl_licences': [...]}

ap.header_signals(response_headers, "example.com")
ap.tdmrep_facts(status, body_bytes)
```

How the IETF parse follows the drafts:

- The value is an RFC 9651 Structured Fields Dictionary. The parser in this file handles the whole
  dictionary syntax: tokens, strings, numbers, booleans, byte sequences, dates, display strings, inner lists
  and parameters.
- Labels are case sensitive. If the dictionary does not parse, the result is `None` (preferences unknown).
  That includes uppercase keys, a trailing comma, a missing comma and a `#` comment in a header.
- Only `train-ai`, `ai-use` and `search` with the tokens `y` or `n` count. Any other key, or a known key
  with another value, is listed under `ignored`. When a key repeats, the last value wins. Parameters are
  ignored.
- robots.txt: the rule name is matched without regard to case, as RFC 9309 does for its rules. `#`
  comments are removed. An optional path comes before the preference, separated by a space or tab. Each
  rule keeps the user-agent group it belongs to (`[]` before any group).

The lenient readers (`parse_usage`, `content_usage_from_robots`, `content_signals`) are the ones the GAIP
Agent Observatory has recorded with since 2 October 2026. Their output is frozen so that recorded rows keep
the same hash. Prefer `usage_preferences` and `robots_signals` for new work.

## Test vectors

`test_vectors.json` lists cases as `{"function", "name", "args", "expected"}`. Compare the result after a
JSON round trip, and UTF-8 encode the arguments listed in `bytes_arguments`. To run them:

```
python3 -m unittest test_aipref_signals
```

The vectors cover letter case, comments, whitespace, unknown keys, duplicate keys, several lines and
groups, and malformed input. Ports to other languages can use the same file.

## Adoption figures

The GAIP Agent Observatory uses this parser to count, each month, how many agent hosts and panel shops
carry each signal. It publishes aggregates only: no site is named, and no count under 5 is shown. See
https://www.gaipagents.com/state-of-agents.

A parse reports what the text said when it was read. It is not legal advice, and it does not assess any
site.
