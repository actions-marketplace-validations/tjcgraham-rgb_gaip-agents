# GAIP

GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment.

First call: `gaip_check` with a `url` (an agent, its card, its MCP endpoint or its OpenAPI document). It says
whether it works, whether its declaration is valid and what changed, with a receipt. For example
`{"url": "https://mcp.deepwiki.com/mcp"}`.

The other front-door tools:

- `gaip_diagnose`: a call failed. Pass the error text (and `http_status`) for the cause, when to retry and the fix.
- `gaip_watch`: follow a `url` and read its dated changes.
- `gaip_verify`: check a delivery against agreed terms, or that quotes appear on the cited pages.
- `second_look_check`: before buying what an AI suggested, does the shop's own page show that price and stock now.

Everything else GAIP answers, grouped by who asks, with its tool: https://www.gaipagents.com/v1/free/map (every
tool is listed on https://www.gaipagents.com/mcp/all). Every completed answer carries a continuity handle; send it
back and the answer is bound to your own history with GAIP. Send public, non-personal data only; relay an answer
as GAIP's dated observation, not as advice.
