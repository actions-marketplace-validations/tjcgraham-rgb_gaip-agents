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

## GAIP Watch: watch the agents your agent depends on

Fail your build when an MCP server or agent your agent depends on changed its tools, schemas, sign-in or prices,
with dated receipts. Free, no account: `uses: tjcgraham-rgb/gaip-agents/watch@main` (see [watch/](watch/)), or
call `https://www.gaipagents.com/v1/free/watch/check` directly. Providers can show their own dated record with the
badge `https://www.gaipagents.com/v1/free/watch/badge.svg?url=<your endpoint>`. Facts, never a verdict:
https://www.gaipagents.com/watch

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

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.png)](https://cursor.com/en/install-mcp?name=gaip&config=eyJ1cmwiOiJodHRwczovL3d3dy5nYWlwYWdlbnRzLmNvbS9tY3AifQ%3D%3D)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_GAIP-0098FF?logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=gaip&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fwww.gaipagents.com%2Fmcp%22%7D)

| Client | How |
|---|---|
| Claude Code | `claude mcp add --transport http gaip https://www.gaipagents.com/mcp` |
| Claude Desktop / claude.ai | Customize > Connectors > Add custom connector, URL `https://www.gaipagents.com/mcp`, no sign-in |
| Cursor, VS Code | the buttons above, or `{ "mcpServers": { "gaip": { "url": "https://www.gaipagents.com/mcp" } } }` |
| Gemini CLI | `gemini extensions install https://github.com/tjcgraham-rgb/gaip-agents` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json`: `{ "mcpServers": { "gaip": { "serverUrl": "https://www.gaipagents.com/mcp" } } }` |
| Cline | `{ "mcpServers": { "gaip": { "type": "streamableHttp", "url": "https://www.gaipagents.com/mcp" } } }` (see `llms-install.md`) |
| Anything else | https://www.gaipagents.com/docs/quickstart |

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
| `packages/aipref-signals/` | Dependency-free parser and test vectors for AI-preference signals (IETF AI Preferences `Content-Usage`, RSL licence links, W3C TDMRep, Content Signals) |
| `assets/` | GAIP logo (SVG, and a 400×400 PNG) and the specialist icons (SVG) |
| `gemini-extension.json`, `GEMINI.md` | Gemini CLI extension: installs GAIP's MCP server and tells the model when to use each tool |
| `llms-install.md` | Install steps for AI assistants that set up MCP servers themselves (Cline) |

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
