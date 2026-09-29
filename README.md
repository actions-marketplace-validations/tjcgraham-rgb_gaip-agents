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
- Official MCP Registry: `io.github.tjcgraham-rgb/gaip-broker` plus ten specialists

This repository holds GAIP's public face only: registry records, the listing kit, a small
Python client, a GitHub Action, examples and logos. The service itself runs at
www.gaipagents.com.

## Products

| Product | What it does | Agents |
|---|---|---|
| Agent Observatory & Conformance | Checks A2A, MCP and OpenAPI declarations and handshakes; keeps a hash-chained log of published manifest changes | integration-protocol |
| Supplier Reliability | Watches the suppliers you depend on for material change and diagnoses failed calls with a bounded repair plan | supplier-watch, integration-repair |
| Delivery Assurance | Records the checks a buyer expects, witnesses what came back and checks that cited pages contain the quoted text | witness, buyer-assurance, procurement-verify, opportunity-broker |
| Evidence Ledger | Verifies retained receipts, compiles evidence packs and incident bundles | trust-assurance, outcome-value |
| Provenance showcase | A method showcase for rights-clear art collections | art-intelligence |

Each specialist has its own MCP endpoint (`https://www.gaipagents.com/mcp/agents/<agent-id>`)
and A2A card (`https://www.gaipagents.com/agents/<agent-id>/.well-known/agent-card.json`).

## Try it

MCP, no input needed:

```bash
curl -s https://www.gaipagents.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"gaip_quickstart","arguments":{}}}'
```

Check an agent by its card URL (REST):

```bash
curl -s 'https://www.gaipagents.com/v1/free/observatory/lookup?url=https://agent.example/.well-known/agent-card.json'
```

A2A, plain text works:

```bash
curl -s https://www.gaipagents.com/a2a/agentverse -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"message/send","params":{"message":{"kind":"message","role":"user","messageId":"m1","parts":[{"kind":"text","text":"check https://agent.example/.well-known/agent-card.json"}]}}}'
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
| `assets/` | GAIP logo and the ten specialist icons (SVG) |

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
