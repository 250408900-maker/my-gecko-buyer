# Check server deployment

## Public endpoint

The buyer check server is deployed publicly using Streamable HTTP.

Endpoint:

`https://manaal.onrender.com/mcp`

The server is keyless and does not load the buyer's signing key.

## Deployment

The service is deployed from the `main` branch of my GitHub repository on Render.

Build command:

`pip install uv && uv sync`

Start command:

`uv run python server/check_server.py`

The server reads Render's `PORT` environment variable and starts the MCP Streamable HTTP transport on `/mcp`.

To redeploy, I push the latest committed version to `main`:

`git push origin main`

Render then deploys the updated service.

## check_purchase call

I connected to the public MCP endpoint and called `check_purchase` with a private RPC URL:

`https://127.0.0.1`

The deployed server answered:

```json
{
  "passed": false,
  "field": "rpc_url",
  "asked": "public https URL",
  "found": "https://127.0.0.1"
}