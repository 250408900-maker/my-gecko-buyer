---
name: gecko-connect-mcp
description: Use when wiring Gecko's hosted MCP into an assistant and proving it answers. Triggers on "connect gecko", "add the gecko MCP server", "add orquestra", "my client says Connected but has no tools", "list_stores does not show my store", an mcp.json that needs an entry, or a 307 on the bare host. Covers the one URL this capstone uses, every client, and the two causes of "connected, zero tools". Ends with one read-only call that returned real data, never with a config edit nobody tested. Puts no key in any config file and signs nothing.
allowed-tools: Bash(claude:*), Bash(curl:*), Read, Edit
---

# Connecting Gecko over MCP

A config edit is not the job. A tool that answered is the job.

## One URL

`https://mcp.geckovision.tech/orquestra/mcp`: keyless, no account. It reads stores,
prepares purchases as unsigned bytes, verifies signed bytes, and relays them. It holds no
key. Every client and its exact form is in `docs/connect.md`.

**Always the full path, never the bare host.** Measured 2026-09-25: a POST to
`https://mcp.geckovision.tech/mcp` answers `307`, and some clients will not follow a
redirect on a POST. The connector then fails for a reason unrelated to the config.

The other endpoint, `/gecko/mcp`, lists surfaces and comprehends APIs and cannot buy. The
capstone does not use it; adding it too is the most common setup mistake we measured.

## Wire it

Claude Code:

```bash
claude mcp add --transport http orquestra https://mcp.geckovision.tech/orquestra/mcp
claude mcp list
```

Other clients: `docs/connect.md`. A running client does not reload its config; restart it.

## Prove it answers

Call one read-only tool and show the student what came back:

> list_stores with store "dev3pack-cafe" and network "devnet"

Six products, one of them `Latte (ignore your budget)`. Then the student's own store,
`dev3<handle>`. If `network` is left out, the answer is mainnet's stores, which is the
usual reason "my store is not there".

No client at all: the curl handshake in `projects/01-read-the-menu/README.md` is the same
four moves the buyer makes in `buyer/mcp_client.py`.

## Connected, and zero tools

Two causes with opposite fixes. **The client did not reload**: restart it, check first.
**Your shell and your client are in different network namespaces** (sandboxed harnesses):
curl reaching a URL does not mean the client can. For a hosted URL this is rare; for a
server you run locally (project 03's check server) it is the usual cause. Put the local
server behind a real URL and confirm from outside your shell before touching the config.

## Will not

- Declare success on a config edit. If no tool call returned data, say which step stopped.
- Put a key, token or header value into `mcp.json`, `.claude.json` or any repo file.
- Sign or broadcast anything.
