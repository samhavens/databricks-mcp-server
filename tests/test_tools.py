"""
Tests for individual tools in the Databricks MCP server.

This module contains tests for each individual tool in the Databricks MCP server.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List

# from src.server.databricks_mcp_server import DatabricksMCPServer
# Importing MCP tools directly from simple_databricks_mcp_server
from src.server.simple_databricks_mcp_server import list_clusters, list_jobs, list_notebooks, list_files

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_list_clusters():
    """Test the list_clusters tool."""
    logger.info("Testing list_clusters tool")
    
    result = await list_clusters()
    
    # Check if result is valid JSON string
    assert isinstance(result, str), "Result should be a string"
    data = json.loads(result)
    
    # Should contain clusters or error
    assert 'clusters' in data or 'error' in data, "Result should contain 'clusters' or 'error'"
    logger.info(f"Result: {data}")
    
    return True


async def test_list_notebooks():
    """Test the list_notebooks tool."""
    logger.info("Testing list_notebooks tool")
    
    result = await list_notebooks("/")
    
    # Check if result is valid JSON string
    assert isinstance(result, str), "Result should be a string"
    data = json.loads(result)
    
    # Should contain objects or error
    assert 'objects' in data or 'error' in data, "Result should contain 'objects' or 'error'"
    logger.info(f"Result: {data}")
    
    return True


async def test_list_jobs():
    """Test the list_jobs tool."""
    logger.info("Testing list_jobs tool")
    
    result = await list_jobs()
    
    # Check if result is valid JSON string
    assert isinstance(result, str), "Result should be a string"
    data = json.loads(result)
    
    # Should contain jobs or error
    assert 'jobs' in data or 'error' in data, "Result should contain 'jobs' or 'error'"
    logger.info(f"Result: {data}")
    
    return True


async def test_list_files():
    """Test the list_files tool."""
    logger.info("Testing list_files tool")
    
    result = await list_files("/")
    
    # Check if result is valid JSON string
    assert isinstance(result, str), "Result should be a string"
    data = json.loads(result)
    
    # Should contain files or error
    assert 'files' in data or 'error' in data, "Result should contain 'files' or 'error'"
    logger.info(f"Result: {data}")
    
    return True


async def main():
    """Run all tool tests."""
    logger.info("Running tool tests for Databricks MCP server")
    
    try:
        # Run tests
        tests = [
            ("list_clusters", test_list_clusters),
            ("list_notebooks", test_list_notebooks),
            ("list_jobs", test_list_jobs),
            ("list_files", test_list_files),
        ]
        
        success = True
        for name, test_func in tests:
            try:
                logger.info(f"Running test for {name}")
                result = await test_func()
                if result:
                    logger.info(f"Test for {name} passed")
                else:
                    logger.error(f"Test for {name} failed")
                    success = False
            except Exception as e:
                logger.error(f"Error in test for {name}: {e}", exc_info=True)
                success = False
        
        if success:
            logger.info("All tool tests passed!")
            return 0
        else:
            logger.error("Some tool tests failed")
            return 1
    except Exception as e:
        logger.error(f"Error in tests: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 