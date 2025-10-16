import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Add these two lines to set httpx logging to DEBUG
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("httpx").setLevel(logging.DEBUG)


"""
Make sure:
1. The server is running before running this script.
2. The server is configured to use streamable-http transport.
3. The server is listening on port 8050.

To run the server:
uv run server.py
"""


async def main():
    # Connect to the server using Streamable HTTP
    # async with streamablehttp_client("http://marquez-mcp.marquez.svc.cluster.local/mcp") as (
    async with streamablehttp_client("http://marquez-mcp.kolya.fun/mcp") as (
        read_stream,
        write_stream,
        get_session_id,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()

            print("Number of tools:", len(tools_result.tools))


if __name__ == "__main__":
    asyncio.run(main())
