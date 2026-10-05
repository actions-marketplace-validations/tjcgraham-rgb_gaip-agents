# GAIP tools

GAIP (https://www.gaipagents.com) is a free, read-only MCP server with four tools. No key or account.
Send public, non-personal data only.

- `gaip_diagnose`: a call to an agent, MCP server or API failed. Pass the error text (and `http_status`)
  to get the likely cause, whether to retry and the exact fix.
- `gaip_check`: does an agent, MCP server or API work, is its declaration valid, and has it changed since
  GAIP last saw it? Pass its `url`.
- `gaip_watch`: follow a `url` and be told when it changes.
- `gaip_verify`: check a delivery against agreed terms, or check that quotes really appear on the cited pages.

Every completed result returns a `continuity_handle`; pass it back on later calls to link them and to ask
`gaip_since_last_call` what changed. Results are facts observed at a stated time, not certification or advice.
