# gaip-check

Check an AI agent **before** your agent calls it. One line, no key, free.

About GAIP: GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment. What it answers, by who asks: https://www.gaipagents.com/v1/free/map.

```python
from gaip_check import check_agent

report = check_agent("https://other-agent.example")   # a domain or a card/MCP/OpenAPI URL
if report["verdict"] != "READY":
    print(report["fixes"])        # what is wrong, concretely
print(report["receipt_id"])       # verifiable GAIP receipt
```

Command line:

```
gaip-check https://other-agent.example
```

GAIP fetches the agent's public card (A2A `/.well-known/agent-card.json`, MCP or
OpenAPI), validates it, tests that the declared endpoint answers, and returns
`READY`, `FIXES_NEEDED` or `UNREACHABLE` with fixes and a receipt.

It is read-only and free. It is a point-in-time readiness check, not identity
proof, endorsement or a trust score. Public results feed the index at
https://www.gaipagents.com/v1/free/agent-readiness.

Other GAIP specialists (delivery witness, supplier change watch, claim checks,
integration repair and more): https://www.gaipagents.com
