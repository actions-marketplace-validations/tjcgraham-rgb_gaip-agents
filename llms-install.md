# Installing GAIP (for AI assistants such as Cline)

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
