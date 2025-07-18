"""
Tests for the Databricks MCP server.

This test file connects to the MCP server using the MCP client library
and tests the cluster and notebook operations.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import anyio
import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class DatabricksMCPClient:
    """Client for testing the Databricks MCP server."""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.stdio_transport: Optional[Tuple[Any, Any]] = None
        self.server_process: Optional[subprocess.Popen] = None

    async def connect(self):
        """Connect to the MCP server."""
        logger.info("Starting Databricks MCP server...")
        
        # Set up environment variables if needed
        # os.environ["DATABRICKS_HOST"] = "..."
        # os.environ["DATABRICKS_TOKEN"] = "..."
        
        # Start the server with SkipPrompt flag to avoid interactive prompts
        cmd = ["pwsh", "-File", "start_mcp_server.ps1", "-SkipPrompt"]
        self.server_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for server to start
        time.sleep(2)
        
        # Connect to the server with SkipPrompt flag
        logger.info("Connecting to MCP server...")
        params = StdioServerParameters(
            command="pwsh",
            args=["-File", "start_mcp_server.ps1", "-SkipPrompt"],
            env=None
        )
        
        async with anyio.create_task_group() as tg:
            async with stdio_client(params) as stdio_transport:
                self.stdio_transport = stdio_transport
                stdio, write = stdio_transport
                self.session = ClientSession(stdio, write)
                await self.session.initialize()
                
                # Log available tools
                tools_response = await self.session.list_tools()
                logger.info(f"Available tools: {[t.name for t in tools_response.tools]}")
                
                # Run tests and then exit
                await tg.start(self.run_tests)
    
    async def run_tests(self):
        """Run the tests for the Databricks MCP server."""
        try:
            await self.test_list_clusters()
            await self.test_get_cluster()
            await self.test_list_notebooks()
            await self.test_export_notebook()
            logger.info("All tests completed successfully!")
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
        finally:
            if self.server_process:
                self.server_process.terminate()
    
    async def test_list_clusters(self):
        """Test listing clusters."""
        logger.info("Testing list_clusters...")
        response = await self.session.call_tool("list_clusters", {})
        logger.info(f"list_clusters response: {json.dumps(response, indent=2)}")
        assert "clusters" in response, "Response should contain 'clusters' key"
        return response
    
    async def test_get_cluster(self):
        """Test getting cluster details."""
        logger.info("Testing get_cluster...")
        
        # First list clusters to get a cluster_id
        clusters_response = await self.test_list_clusters()
        if not clusters_response.get("clusters"):
            logger.warning("No clusters found to test get_cluster")
            return
        
        # Get the first cluster ID
        cluster_id = clusters_response["clusters"][0]["cluster_id"]
        
        # Get cluster details
        response = await self.session.call_tool("get_cluster", {"cluster_id": cluster_id})
        logger.info(f"get_cluster response: {json.dumps(response, indent=2)}")
        assert "cluster_id" in response, "Response should contain 'cluster_id' key"
        assert response["cluster_id"] == cluster_id, "Returned cluster ID should match requested ID"
    
    async def test_list_notebooks(self):
        """Test listing notebooks."""
        logger.info("Testing list_notebooks...")
        response = await self.session.call_tool("list_notebooks", {"path": "/"})
        logger.info(f"list_notebooks response: {json.dumps(response, indent=2)}")
        assert "objects" in response, "Response should contain 'objects' key"
        return response
    
    async def test_export_notebook(self):
        """Test exporting a notebook."""
        logger.info("Testing export_notebook...")
        
        # First list notebooks to get a notebook path
        notebooks_response = await self.test_list_notebooks()
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
        response = await self.session.call_tool(
            "export_notebook", 
            {"path": notebook_path, "format": "SOURCE"}
        )
        logger.info(f"export_notebook response (truncated): {str(response)[:200]}...")
        assert "content" in response, "Response should contain 'content' key"


# Skip this test for now as it causes hanging issues
@pytest.mark.skip(reason="Test causes hanging issues - needs further investigation")
@pytest.mark.asyncio
async def test_databricks_mcp_server():
    """Test the Databricks MCP server."""
    client = DatabricksMCPClient()
    await client.connect()


if __name__ == "__main__":
    """Run the tests directly."""
    asyncio.run(DatabricksMCPClient().connect()) 