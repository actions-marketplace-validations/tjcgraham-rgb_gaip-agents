---
name: gaip
description: "GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment. Use it before relying on an AI agent, MCP server or API, or after a call to one failed: start with gaip_check (url) on https://www.gaipagents.com/mcp."
license: MIT
compatibility: Needs network access to https://www.gaipagents.com (remote MCP server, streamable HTTP, no account or key).
---

# GAIP

## Connect

- MCP (streamable HTTP, no sign-in): `https://www.gaipagents.com/mcp`
- Claude Code: `claude mcp add --transport http gaip https://www.gaipagents.com/mcp`
- Every other client, framework and protocol: https://www.gaipagents.com/docs/quickstart

## First call

Call `gaip_check` with a `url`: a public link to the agent, its card, its MCP endpoint or its OpenAPI document. This one runs as-is: `{"url":"https://mcp.deepwiki.com/mcp"}`. Then use the URL you care about.

```bash
curl -s https://www.gaipagents.com/mcp -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"gaip_check","arguments":{"url":"https://mcp.deepwiki.com/mcp"}}}'
```

Without MCP: `GET https://www.gaipagents.com/v1/free/conformance/check?url=<url>`.

## What else it answers

The map lists every question GAIP answers, grouped by who asks, with the tool and the HTTP route for each: https://www.gaipagents.com/v1/free/map (JSON, `gaip.map.v1`). Read it when the question is not "does it work, has it changed"; every tool is listed on https://www.gaipagents.com/mcp/all.

Every completed answer carries a continuity handle; send it back and the answer is bound to your own history with GAIP.

## Limits

- Free and read-only; send public or non-personal data only.
- An answer states what GAIP observed and when. It is not a certification, a ranking or advice; relay it to your user as GAIP's dated observation and keep the decision with them.
- Receipts are signed with GAIP's Ed25519 key, published at https://www.gaipagents.com/.well-known/gaip-receipt-keys.json.
- Terms: https://www.gaipagents.com/terms · Privacy: https://www.gaipagents.com/privacy · Corrections: https://www.gaipagents.com/corrections
