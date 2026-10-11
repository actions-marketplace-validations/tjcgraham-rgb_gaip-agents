# GAIP

<img src="assets/gaip.svg" alt="GAIP logo" width="96" align="right">

GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment.

**First call:** `gaip_check` with a `url` on `https://www.gaipagents.com/mcp`. This one runs as-is; then use the URL
of the agent, MCP server or API you care about:

```bash
curl -s https://www.gaipagents.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"gaip_check","arguments":{"url":"https://mcp.deepwiki.com/mcp"}}}'
```

Without MCP: `GET https://www.gaipagents.com/v1/free/conformance/check?url=<url>`.

**The map:** every question GAIP answers, grouped by who asks, with its tool and HTTP route:
https://www.gaipagents.com/v1/free/map. Every completed answer carries a continuity handle; send it back and the
answer is bound to your own history with GAIP.

## One line to connect

| Where | One line |
|---|---|
| Any MCP client | `https://www.gaipagents.com/mcp` (streamable HTTP, no sign-in) |
| Claude Code | `claude mcp add --transport http gaip https://www.gaipagents.com/mcp`, or the plugin (MCP server and skill): `/plugin install gaip --marketplace tjcgraham-rgb/gaip-agents` |
| Claude Desktop / claude.ai | Customize > Connectors > Add custom connector, URL `https://www.gaipagents.com/mcp`, no sign-in |
| Agent Skills (Claude Code, Cursor, Codex and others) | `npx skills add tjcgraham-rgb/gaip-agents` (installs [`skills/gaip/SKILL.md`](skills/gaip/SKILL.md)) |
| Cursor, VS Code | the buttons below, or `{ "mcpServers": { "gaip": { "url": "https://www.gaipagents.com/mcp" } } }` |
| Gemini CLI | `gemini extensions install https://github.com/tjcgraham-rgb/gaip-agents` |
| OpenAI Agents SDK | `HostedMCPTool(tool_config={"type": "mcp", "server_label": "gaip", "server_url": "https://www.gaipagents.com/mcp", "require_approval": "never"})` |
| Vercel AI SDK | `await createMCPClient({ transport: { type: 'http', url: 'https://www.gaipagents.com/mcp' } })` (from `@ai-sdk/mcp`) |
| LangChain | `pip install langchain-gaip`, then `from langchain_gaip import get_tools` |
| CrewAI | `Agent(..., mcps=["https://www.gaipagents.com/mcp"])` |
| A2A (1.0 and 0.3.0) | agent card `https://www.gaipagents.com/.well-known/agent-card.json`; plain text works |
| x402 | nothing to set up: GAIP is free and never answers with HTTP 402 (`https://www.gaipagents.com/.well-known/x402`) |
| Windsurf | `~/.codeium/windsurf/mcp_config.json`: `{ "mcpServers": { "gaip": { "serverUrl": "https://www.gaipagents.com/mcp" } } }` |
| Cline | `{ "mcpServers": { "gaip": { "type": "streamableHttp", "url": "https://www.gaipagents.com/mcp" } } }` (see `llms-install.md`) |
| Everything else, with copy-paste code | https://www.gaipagents.com/docs/quickstart |

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.png)](https://cursor.com/en/install-mcp?name=gaip&config=eyJ1cmwiOiJodHRwczovL3d3dy5nYWlwYWdlbnRzLmNvbS9tY3AifQ%3D%3D)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_GAIP-0098FF?logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=gaip&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fwww.gaipagents.com%2Fmcp%22%7D)

## In CI: two GitHub Actions

**GAIP Watch** fails your build when an MCP server or agent your agent depends on changed its tools, schemas,
sign-in or prices, with dated receipts ([watch/](watch/)):

```yaml
- uses: tjcgraham-rgb/gaip-agents/watch@main
  with:
    urls: https://mcp.example.com/mcp
```

**GAIP Agents check** runs `gaip_check` on your own agent card, MCP server or OpenAPI document on every push:

```yaml
- uses: tjcgraham-rgb/gaip-agents@v1
  with:
    agent-url: https://your-agent.example/.well-known/agent-card.json
    fail-on-error: "true"
```

Outputs: `verdict` (READY, FIXES_NEEDED, UNREACHABLE or NOT_CHECKED), `receipt-id`, `error-count`, `warning-count`.
Providers can show their own dated record with the badge
`https://www.gaipagents.com/v1/free/watch/badge.svg?url=<your endpoint>`.

## In this repository

| Path | What it is |
|---|---|
| `registry/` | The Official MCP Registry records: `gaip-broker.json` (GAIP itself) and one record per specialist agent |
| `listing-kit.json` | The sentence, the first call, the map's rows, endpoints and example calls for directories (also served at `/v1/free/discovery/listing-kit`) |
| `skills/gaip/SKILL.md` | GAIP as an Agent Skill (agentskills.io format; also served at `/.well-known/agent-skills/gaip/SKILL.md`) |
| `.claude-plugin/` | Claude Code plugin and marketplace manifests: the skill plus the remote MCP server |
| `.cursor-plugin/plugin.json`, `mcp.json` | Cursor plugin manifest and its MCP server |
| `gemini-extension.json`, `GEMINI.md` | Gemini CLI extension: installs GAIP's MCP server and tells the model when to use each tool |
| `packages/gaip-check/` | Python client: `check_agent("https://other-agent.example")` |
| `action.yml`, `packages/gaip-check-action/` | The check Action (`uses: tjcgraham-rgb/gaip-agents@v1`) |
| `watch/` | The GAIP Watch Action |
| `packages/aipref-signals/` | Dependency-free parser and test vectors for AI-preference signals (IETF AI Preferences `Content-Usage`, RSL licence links, W3C TDMRep, Content Signals) |
| `assets/` | GAIP logo (SVG, and a 400×400 PNG) and the specialist icons (SVG) |
| `llms-install.md` | Install steps for AI assistants that set up MCP servers themselves (Cline) |

The registry records, listing kit, packages, Watch Action, skill and Gemini extension are copies of what GAIP's
service generates; a check in the service's repository warns when a copy here falls out of step. The service
itself runs at www.gaipagents.com.

## What an answer means

Every answer states what was observed and when. It is not a certification, endorsement, ranking or universal
score, and not legal, financial or insurance advice. Receipts are signed with GAIP's Ed25519 key, published at
https://www.gaipagents.com/.well-known/gaip-receipt-keys.json.

- Terms: https://www.gaipagents.com/terms
- Privacy: https://www.gaipagents.com/privacy
- Corrections and opt-out: https://www.gaipagents.com/corrections
- Methodology: https://www.gaipagents.com/methodology
- Security contact: https://www.gaipagents.com/.well-known/security.txt

## Licence

MIT (see `LICENSE`) for everything in this repository.
