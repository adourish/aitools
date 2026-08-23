---
name: mcp-servers
description: Configure, build and debug MCP servers for Claude Code and other clients — server setup, transport and config files, and authoring a new server. Use for "add an MCP server", "my MCP server isn't connecting", "build an MCP integration", or any request naming MCP.
---

# MCP servers

| Task | Guide |
|------|-------|
| Install and configure an MCP server for a client | `system/skill_mcp_server_setup.md` |
| Build a new MCP server (full package) | `development/mcp-builder/SKILL.md` |
| Local server in this repo | `_tools/server.py` (with `drive_tools.py`, `filesystem_tools.py`) |

Server credentials come from the KeePass vault — never inline a token in an MCP config file that
gets committed.
