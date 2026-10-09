# Installing GAIP (for AI assistants such as Cline)

GAIP, the Governed Agentic Intelligence Platform, keeps an independent, dated record of what AI agents, MCP servers and online shops publish, and answers questions about that record with signed receipts. Free, read-only, no key; facts at a stated time, never an assessment. What it answers, by who asks: https://www.gaipagents.com/v1/free/map.

GAIP is a remote MCP server: nothing to download, build or run, and no API key.

1. Add this server to the MCP settings file (`cline_mcp_settings.json` in Cline):

```json
{
  "mcpServers": {
    "gaip": {
      "type": "streamableHttp",
      "url": "https://www.gaipagents.com/mcp"
    }
  }
}
```

2. Check it works: call the `gaip_check` tool with `{"url": "https://mcp.deepwiki.com/mcp"}`. A result with a
   `status` and a `continuity_handle` means GAIP is connected.

Other clients use the same URL; formats for Claude, Cursor, VS Code, Gemini CLI, Windsurf and ChatGPT are at
https://www.gaipagents.com/docs/quickstart. Free, read-only; send public, non-personal data only.
