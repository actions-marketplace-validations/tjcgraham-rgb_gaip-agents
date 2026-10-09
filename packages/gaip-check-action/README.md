# GAIP agent check (GitHub Action)

Run GAIP's free, public readiness check against your agent in CI. The action sends
the agent URL to GAIP, prints each finding as a GitHub annotation, writes a short
job summary, and (by default) fails the step when GAIP reports an `ERROR`
finding or cannot reach the agent.

About GAIP: GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment. What it answers, by who asks: https://www.gaipagents.com/v1/free/map.

No account, API key or secret is needed. It is the CI form of GAIP's first call, `gaip_check` (the map's "Check and GAIP Watch" row).

## Usage

```yaml
name: Agent conformance
on: [push, pull_request]
jobs:
  gaip-check:
    runs-on: ubuntu-latest
    steps:
      - uses: tjcgraham-rgb/gaip-agents/packages/gaip-check-action@main
        id: gaip
        with:
          agent-url: https://agent.example.com/.well-known/agent-card.json
          fail-on-error: "true"      # set "false" to report without failing
      - run: echo "GAIP verdict ${{ steps.gaip.outputs.verdict }}, receipt ${{ steps.gaip.outputs.receipt-id }}"
```

Pin to a commit SHA instead of `@main` for reproducible builds.

### Inputs

| Input | Default | Meaning |
|---|---|---|
| `agent-url` | (required) | Public `https://` URL: a domain, or the direct URL of an A2A card, MCP server card/`server.json` or OpenAPI document |
| `fail-on-error` | `true` | Fail on `ERROR` findings or an unreachable agent |
| `gaip-endpoint` | `https://www.gaipagents.com/a2a/agentverse` | GAIP endpoint that runs the check |
| `timeout-seconds` | `60` | Request timeout |

### Outputs

`verdict` (`READY`, `FIXES_NEEDED`, `UNREACHABLE` or `NOT_CHECKED`), `receipt-id`,
`error-count`, `warning-count`.

Exit codes: `0` passed (or `fail-on-error: false`), `1` findings or refusal, `2` GAIP could not be reached.

### Run locally

```bash
GAIP_AGENT_URL=https://agent.example.com python3 packages/gaip-check-action/check.py
```

## What GAIP does and does not do

GAIP fetches the public document at the URL you give (and standard well-known
discovery paths), checks it against its published conformance rules, tests that
the declared endpoint answers over public HTTPS, and returns findings with a
verifiable receipt. The URL and a summary of the result are retained as a
public receipt, so only check public agents you are entitled to point GAIP at.

## Disclaimer

GAIP reports what it observed at the time of the check, from public metadata
only. A result is not certification, endorsement, a security or penetration
test, a ranking, or legal, financial or insurance advice, and a passing check
does not mean an agent is fit for any particular use. See the
[terms of use](https://www.gaipagents.com/terms),
[privacy notice](https://www.gaipagents.com/privacy) and
[methodology](https://www.gaipagents.com/methodology) (drafts pending legal
review).

Publishing this action to the GitHub Marketplace is a founder decision and has
not been done.
