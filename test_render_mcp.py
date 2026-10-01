import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


URL = "https://manaal.onrender.com/mcp"


async def main():
    async with streamable_http_client(URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "check_purchase",
                {
                    "intent": {},
                    "prepared_answer": {},
                    "rpc_url": "https://127.0.0.1",
                },
            )

            print(result)


if __name__ == "__main__":
    asyncio.run(main())