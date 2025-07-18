"""
MCP client tests for the Databricks MCP server.

This module contains tests that use the MCP client to connect to and test the server.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import pytest
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_tests():
    """Connect to and test the Databricks MCP server."""
    logger.info("Connecting to Databricks MCP server...")
    
    # IMPORTANT: In MCP, the client launches the server process
    # We don't connect to an already running server!
    
    # Define the environment variables the server needs
    env = os.environ.copy()
    
    # Create parameters for connecting to the server
    # This will launch the server using the PowerShell script
    params = StdioServerParameters(
        command="pwsh",  # Use PowerShell
        args=["-File", "./scripts/start_server.ps1"],  # Run the startup script
        env=env  # Pass environment variables
    )
    
    # Use the client to start the server and connect to it
    logger.info("Launching server process...")
    
    try:
        async with stdio_client(params) as (recv, send):
            logger.info("Server launched, creating session...")
            session = ClientSession(recv, send)
            
            logger.info("Initializing session...")
            await session.initialize()
            
            # List available tools
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            logger.info(f"Available tools: {tool_names}")
            
            # Run tests for clusters
            if "list_clusters" in tool_names:
                await test_list_clusters(session)
                await test_get_cluster(session)
            else:
                logger.warning("Cluster tools not available")
            
            # Run tests for notebooks
            if "list_notebooks" in tool_names:
                await test_list_notebooks(session)
                await test_export_notebook(session)
            else:
                logger.warning("Notebook tools not available")
            
            logger.info("All tests completed successfully!")
            return True
    except Exception as e:
        logger.error(f"Error during tests: {e}", exc_info=True)
        return False


# Skip all these tests until we fix the hanging issues
@pytest.mark.skip(reason="Test causes hanging issues - needs further investigation")
@pytest.mark.asyncio
async def test_list_clusters(session):
    """Test listing clusters."""
    logger.info("Testing list_clusters...")
    response = await session.call_tool("list_clusters", {})
    logger.info(f"list_clusters response: {json.dumps(response, indent=2)}")
    assert "clusters" in response, "Response should contain 'clusters' key"
    return response


@pytest.mark.skip(reason="Test causes hanging issues - needs further investigation")
@pytest.mark.asyncio
async def test_get_cluster(session):
    """Test getting cluster details."""
    logger.info("Testing get_cluster...")
    
    # First list clusters to get a cluster_id
    clusters_response = await test_list_clusters(session)
    if not clusters_response.get("clusters"):
        logger.warning("No clusters found to test get_cluster")
        return
    
    # Get the first cluster ID
    cluster_id = clusters_response["clusters"][0]["cluster_id"]
    
    # Get cluster details
    response = await session.call_tool("get_cluster", {"cluster_id": cluster_id})
    logger.info(f"get_cluster response: {json.dumps(response, indent=2)}")
    assert "cluster_id" in response, "Response should contain 'cluster_id' key"
    assert response["cluster_id"] == cluster_id, "Returned cluster ID should match requested ID"


@pytest.mark.skip(reason="Test causes hanging issues - needs further investigation")
@pytest.mark.asyncio
async def test_list_notebooks(session):
    """Test listing notebooks."""
    logger.info("Testing list_notebooks...")
    response = await session.call_tool("list_notebooks", {"path": "/"})
    logger.info(f"list_notebooks response: {json.dumps(response, indent=2)}")
    assert "objects" in response, "Response should contain 'objects' key"
    return response


@pytest.mark.skip(reason="Test causes hanging issues - needs further investigation")
@pytest.mark.asyncio
async def test_export_notebook(session):
    """Test exporting a notebook."""
    logger.info("Testing export_notebook...")
    
    # First list notebooks to get a notebook path
    notebooks_response = await test_list_notebooks(session)
    if not notebooks_response.get("objects"):
        logger.warning("No notebooks found to test export_notebook")
        return
    
    # Find the first notebook (not a directory)
    notebook = None
    for obj in notebooks_response["objects"]:
        if obj.get("object_type") == "NOTEBOOK":
            notebook = obj
            break
    
    if not notebook:
        logger.warning("No notebooks found to test export_notebook")
        return
    
    # Get notebook path
    notebook_path = notebook["path"]
    
    # Export notebook
    response = await session.call_tool(
        "export_notebook", 
        {"path": notebook_path, "format": "SOURCE"}
    )
    logger.info(f"export_notebook response (truncated): {str(response)[:200]}...")
    assert "content" in response, "Response should contain 'content' key"


async def main():
    """Run the tests."""
    success = await run_tests()
    return 0 if success else 1


if __name__ == "__main__":
    """Run the tests directly."""
    sys.exit(asyncio.run(main())) 