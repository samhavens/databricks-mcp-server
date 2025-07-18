"""
Example of using the MCP client with the Databricks MCP server.

This example shows how to use the MCP client to connect to the Databricks MCP server
and call its tools through the MCP protocol.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def connect_and_list_tools():
    """Connect to the Databricks MCP server and list its tools."""
    logger.info("Connecting to Databricks MCP server...")
    
    # Define the environment variables the server needs
    env = os.environ.copy()
    
    # Create parameters for connecting to the server
    params = StdioServerParameters(
        command="pwsh",  # Use PowerShell
        args=["-File", "./scripts/start_server.ps1"],  # Run the startup script
        env=env  # Pass environment variables
    )
    
    # Use the client to start the server and connect to it
    logger.info("Launching server process...")
    
    async with stdio_client(params) as (recv, send):
        logger.info("Server launched, creating session...")
        session = ClientSession(recv, send)
        
        logger.info("Initializing session...")
        await session.initialize()
        
        # List available tools
        tools_response = await session.list_tools()
        tools = tools_response.tools
        
        print("\nAvailable Tools:")
        print("================")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        # Let the user select a tool to run
        if tools:
            while True:
                print("\nSelect a tool to run (or 'quit' to exit):")
                for i, tool in enumerate(tools):
                    print(f"{i+1}. {tool.name}")
                
                choice = input("Enter choice (number or name): ")
                
                if choice.lower() == 'quit':
                    break
                
                # Find the selected tool
                selected_tool = None
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(tools):
                        selected_tool = tools[idx]
                else:
                    for tool in tools:
                        if tool.name == choice:
                            selected_tool = tool
                            break
                
                if not selected_tool:
                    print("Invalid choice. Please try again.")
                    continue
                
                # Call the selected tool
                print(f"\nRunning tool: {selected_tool.name}")
                print("Enter parameters as JSON (empty for no parameters):")
                params_str = input("> ")
                
                try:
                    params = json.loads(params_str) if params_str else {}
                    result = await session.call_tool(selected_tool.name, params)
                    print("\nResult:")
                    print(json.dumps(result, indent=2))
                except Exception as e:
                    print(f"Error calling tool: {e}")


async def main():
    """Run the example."""
    print("Databricks MCP Server - MCP Client Usage Example")
    print("=============================================")
    
    try:
        await connect_and_list_tools()
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 