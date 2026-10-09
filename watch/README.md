# GAIP Watch (GitHub Action)

Fail your build when an MCP server or agent your agent depends on changed its tools, input schemas,
authentication or prices since you last looked, with dated receipts for each change.

About GAIP: GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment. What it answers, by who asks: https://www.gaipagents.com/v1/free/map.

GAIP reads public agents and MCP servers about daily and keeps a hash-chained record of what each one
published. This action asks that record one question from your own pipeline: has anything my agent depends on
changed since the last run, and is it the kind of change I have to act on? Free, no account, no API key, no
email. Facts, never a verdict: a changed tool list is not a sign of wrongdoing; the decision stays with you.

## Usage

```yaml
name: Dependency watch
on:
  schedule:
    - cron: "17 6 * * *"      # daily
  pull_request:
jobs:
  gaip-watch:
    runs-on: ubuntu-latest
    steps:
      - uses: tjcgraham-rgb/gaip-agents/watch@main
        id: watch
        with:
          urls: |
            https://mcp.example.com/mcp
            https://agent.example.org/.well-known/agent-card.json
          since: 7d
          capture-unknown: "true"
      - run: echo "breaking=${{ steps.watch.outputs.breaking }} changed=${{ steps.watch.outputs.changed }}"
```

Pin to a commit SHA instead of `@main` for reproducible builds.

### Inputs

| Input | Default | Meaning |
|---|---|---|
| `urls` | (required) | The public `https://` URLs your agent depends on: MCP endpoints or A2A agent cards, one per line or comma-separated, up to 25 |
| `since` | `7d` | Changes recorded since: a number of days (`7d`) or a date (`YYYY-MM-DD` or RFC 3339) |
| `capture-unknown` | `true` | When GAIP has no record of a URL, save a first dated record now (up to 5 per run) so the next run has history |
| `fail-on-breaking` | `true` | Fail the step when a breaking change class was recorded |
| `fail-on-unknown` | `false` | Also fail when a URL has no record yet |
| `continuity-handle` | (none) | Optional: the GAIP continuity handle from an earlier answer, kept as a repository secret, to link your runs. Without it the action keeps one in the Actions cache |
| `gaip-endpoint` | `https://www.gaipagents.com/v1/free/watch/check` | GAIP's dependency check route |
| `timeout-seconds` | `60` | Request timeout |

### Outputs

| Output | Meaning |
|---|---|
| `breaking` | `true` when a breaking change class was recorded for any target |
| `ingredients-changed` | Number of targets whose declared provider, version, model, operator or AI self-disclosure changed since the date (`declared_ingredients_changed`, informational) |
| `hosting-changed` | Number of targets whose endpoint answered from another network or certificate issuer since the date (`hosting_changed`, informational; never the address) |
| `changed` | Targets with any change recorded since the date |
| `unknown` | Targets GAIP had no record of |
| `result-file` | Path of the full JSON answer (`.gaip-watch/result.json`) |

### What counts as breaking

A change class a dependent client usually has to act on: `tool_removed`, `schema_changed`, `auth_changed`,
`pricing_changed`, `tool_changed_beyond_stored`, `key_changed` (a signing key the host publishes was added,
removed or swapped, from GAIP's weekly key record). Recorded but not flagged: `tool_added`, `description_changed`,
`annotations_changed`, `version_changed`. The labels come from GAIP's capability and key records and describe what
the server published, not the server.

### What GAIP does and does not do

GAIP reads a server's published card or MCP tool list as any client would (robots.txt respected, never a tool
call), stores hashes and a short excerpt, and signs each day's chain head through a public transparency log. It
publishes no rankings, scores or verdicts. A target it has no record of cannot be said to have changed; the first
run with `capture-unknown` saves one. Method: <https://www.gaipagents.com/observatory>. Corrections and opt-out
for server operators: <https://www.gaipagents.com/corrections>. Terms and privacy (drafts):
<https://www.gaipagents.com/terms>, <https://www.gaipagents.com/privacy>.

MIT licence.
