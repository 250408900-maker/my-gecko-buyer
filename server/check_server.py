from typing import Any

from mcp.server.mcpserver import MCPServer

from buyer.intent import IntentRecord
from buyer.prepared import Prepared
from buyer.check import check_all

from server.guard import is_public_url


server = MCPServer("buyer-check")


@server.tool()
def check_purchase(
    intent: dict[str, Any],
    prepared_answer: dict[str, Any],
    rpc_url: str | None = None,
) -> dict[str, Any]:
    """
    Check whether a prepared purchase matches the buyer's pinned intent.

    This server is keyless: it never loads or uses a signer.
    """

    # Refuse unsafe RPC URLs before anything could fetch them.
    if rpc_url is not None and not is_public_url(rpc_url):
        return {
            "passed": False,
            "field": "rpc_url",
            "asked": "public https URL",
            "found": rpc_url,
        }

    pinned = IntentRecord(**intent)
    prepared = Prepared.from_answer(prepared_answer)

    verdict = check_all(pinned, prepared)

    if verdict.passed:
        return {
            "passed": True,
            "field": None,
            "asked": None,
            "found": None,
        }

    if verdict.refusal is not None:
        refusal = verdict.refusal

        # FieldResult stores the field name as its first dataclass field.
        field_name = getattr(
            refusal,
            "field_name",
            getattr(refusal, "field", None),
        )

        return {
            "passed": False,
            "field": field_name,
            "asked": refusal.asked,
            "found": refusal.found,
        }

    # A check exists but has not been implemented.
    if verdict.unwritten is not None:
        return {
            "passed": False,
            "field": "unwritten",
            "asked": None,
            "found": str(verdict.unwritten),
        }

    return {
        "passed": False,
        "field": "unknown",
        "asked": None,
        "found": None,
    }


if __name__ == "__main__":
    import asyncio
    import os

    port = int(os.environ.get("PORT", "8000"))

    asyncio.run(
        server.run_streamable_http_async(
            host="0.0.0.0",
            port=port,
            streamable_http_path="/mcp",
        )
    )