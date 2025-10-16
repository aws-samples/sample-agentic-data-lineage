#!/usr/bin/env python3
"""
Simple MCP client for testing Marquez MCP server
"""

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test MCP server connection and basic functionality"""

    # Get current directory and Python executable
    current_dir = Path(__file__).parent
    python_exe = sys.executable
    server_script = current_dir / "server.py"

    print("🔧 Testing MCP server...")

    # Define server parameters
    server_params = StdioServerParameters(
        command=python_exe, args=[str(server_script)], env=dict(os.environ)
    )

    try:
        # Connect to server
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ Connected to MCP server")

                # Initialize connection
                await session.initialize()
                print("✅ Session initialized")

                # List available tools
                tools_result = await session.list_tools()
                print(f"✅ Found {len(tools_result.tools)} tools")

                # Display first few tools
                for i, tool in enumerate(tools_result.tools[:3], 1):
                    print(f"   {i}. {tool.name}")

                if len(tools_result.tools) > 3:
                    print(f"   ... and {len(tools_result.tools) - 3} more")

                print("🎉 MCP server test successful!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
