# GAIP Agents

<img src="assets/gaip.svg" alt="GAIP logo" width="96" align="right">

**Free, read-only evidence on AI agents and MCP servers: conformance, change, delivery, receipts.**

GAIP checks the public declarations of AI agents and MCP servers, watches them for change,
witnesses what a delegated call returned and keeps verifiable receipts. Calls are free and
need no account or API key; public or non-personal data only.

- Website: https://www.gaipagents.com
- MCP (Streamable HTTP, no auth): `https://www.gaipagents.com/mcp`
- A2A agent card: `https://www.gaipagents.com/.well-known/agent-card.json`
- OpenAPI 3.1: `https://www.gaipagents.com/openapi.json`
- Agent-readable guide: `https://www.gaipagents.com/llms.txt`
- Official MCP Registry: `io.github.tjcgraham-rgb/gaip-broker` plus eleven specialist records (three listed faces below)

This repository holds GAIP's public face only: registry records, the listing kit, a small
Python client, a GitHub Action, examples and logos. The service itself runs at
www.gaipagents.com.

## Three public faces

| Face (product) | What it does | Agent |
|---|---|---|
| Developer checks & Observatory | Four tools on `/mcp`: `gaip_check` (does an agent, MCP server or API work, is it valid, has it changed), `gaip_diagnose` (why a call failed and the fix), `gaip_watch` and `gaip_verify`; behind them the Agent Observatory keeps a hash-chained log of what agents published | integration-protocol |
| Witness: delivery & evidence | Agreed terms, delivery, receipts, disputes and evidence: witnesses what came back, tests supplier claims and keeps verifiable receipts, evidence packs and outcome records | witness |
| Shop listing data (preview) | A shop product page as clean data for AI shopping agents, with source checks and a dated price and stock history | listing-observer |

Still callable at their own endpoints with the same tools, no longer listed separately (founder decision, 1 Oct
2026): buyer-assurance, procurement-verify, trust-assurance and outcome-value (part of Witness); supplier-watch and
integration-repair (part of the developer checks); opportunity-broker and art-intelligence (unlisted).

Each specialist has its own MCP endpoint (`https://www.gaipagents.com/mcp/agents/<agent-id>`)
and A2A card (`https://www.gaipagents.com/agents/<agent-id>/.well-known/agent-card.json`).

## Try it

First call over MCP: check a public MCP server (runs as-is; then use your own agent's URL):

```bash
curl -s https://www.gaipagents.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"gaip_check","arguments":{"url":"https://mcp.deepwiki.com/mcp"}}}'
```

What GAIP has recorded about a server (REST):

```bash
curl -s 'https://www.gaipagents.com/v1/free/observatory/lookup?url=https://mcp.deepwiki.com/mcp'
```

A2A, plain text works:

```bash
curl -s https://www.gaipagents.com/a2a/agentverse -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"message/send","params":{"message":{"kind":"message","role":"user","messageId":"m1","parts":[{"kind":"text","text":"check https://mcp.deepwiki.com/mcp"}]}}}'
```

Add GAIP to an MCP client:

```json
{ "mcpServers": { "gaip": { "type": "http", "url": "https://www.gaipagents.com/mcp" } } }
```

## Use it in CI (GitHub Action)

Check your agent card, MCP server or OpenAPI document on every push, free and with no key:

```yaml
- uses: tjcgraham-rgb/gaip-agents@v1
  with:
    agent-url: https://your-agent.example/.well-known/agent-card.json
    fail-on-error: "true"
```

Outputs: `verdict` (READY, FIXES_NEEDED, UNREACHABLE or NOT_CHECKED), `receipt-id`, `error-count`, `warning-count`.

## In this repository

| Path | What it is |
|---|---|
| `registry/` | The Official MCP Registry records: `gaip-broker.json` and one record per specialist |
| `listing-kit.json` | Names, descriptions, endpoints, categories and example calls for directories (also served at `/v1/free/discovery/listing-kit`) |
| `packages/gaip-check/` | Python client: `check_agent("https://other-agent.example")` |
| `action.yml`, `packages/gaip-check-action/` | GitHub Action that checks an agent card in CI (`uses: tjcgraham-rgb/gaip-agents@v1`) |
| `assets/` | GAIP logo and the specialist icons (SVG) |

## What a result means

Every result states what was observed and when. It is not a certification, endorsement,
ranking or universal score, and not legal, financial or insurance advice.

- Terms: https://www.gaipagents.com/terms
- Privacy: https://www.gaipagents.com/privacy
- Corrections and opt-out: https://www.gaipagents.com/corrections
- Methodology: https://www.gaipagents.com/methodology
- Security contact: https://www.gaipagents.com/.well-known/security.txt

## Licence

MIT (see `LICENSE`) for everything in this repository.
