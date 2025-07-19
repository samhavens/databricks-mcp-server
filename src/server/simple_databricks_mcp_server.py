#!/usr/bin/env python3
"""
Simple Databricks MCP Server

A Model Context Protocol server that provides tools for interacting
with Databricks APIs. Uses the same pattern as the working iPython MCP server.
"""

from mcp.server.fastmcp import FastMCP
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional, Union

from src.api import clusters, dbfs, jobs, notebooks, sql
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the MCP server (same pattern as iPython)
mcp = FastMCP("databricks-mcp")

@mcp.tool()
async def list_clusters() -> str:
    """List all Databricks clusters"""
    logger.info("Listing clusters")
    try:
        result = await clusters.list_clusters()
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error listing clusters: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def create_cluster(
    cluster_name: str,
    spark_version: str,
    node_type_id: str,
    num_workers: int = 1
) -> str:
    """Create a new Databricks cluster"""
    logger.info(f"Creating cluster: {cluster_name}")
    try:
        cluster_config = {
            "cluster_name": cluster_name,
            "spark_version": spark_version,
            "node_type_id": node_type_id,
            "num_workers": num_workers,
            "enable_elastic_disk": True
        }
        result = await clusters.create_cluster(cluster_config)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error creating cluster: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def terminate_cluster(cluster_id: str) -> str:
    """Terminate a Databricks cluster"""
    logger.info(f"Terminating cluster: {cluster_id}")
    try:
        result = await clusters.terminate_cluster(cluster_id)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error terminating cluster: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_cluster(cluster_id: str) -> str:
    """Get information about a specific Databricks cluster"""
    logger.info(f"Getting cluster info: {cluster_id}")
    try:
        result = await clusters.get_cluster(cluster_id)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error getting cluster info: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def start_cluster(cluster_id: str) -> str:
    """Start a terminated Databricks cluster"""
    logger.info(f"Starting cluster: {cluster_id}")
    try:
        result = await clusters.start_cluster(cluster_id)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error starting cluster: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def list_jobs() -> str:
    """List all Databricks jobs"""
    logger.info("Listing jobs")
    try:
        result = await jobs.list_jobs()
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def run_job(job_id: str, notebook_params: Optional[Dict[str, Any]] = None) -> str:
    """Run a Databricks job"""
    logger.info(f"Running job: {job_id}")
    try:
        if notebook_params is None:
            notebook_params = {}
        result = await jobs.run_job(job_id, notebook_params)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error running job: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def list_notebooks(path: str) -> str:
    """List notebooks in a workspace directory"""
    logger.info(f"Listing notebooks in: {path}")
    try:
        result = await notebooks.list_notebooks(path)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error listing notebooks: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def export_notebook(path: str, format: str = "JUPYTER") -> str:
    """Export a notebook from the workspace"""
    logger.info(f"Exporting notebook: {path} in format: {format}")
    try:
        result = await notebooks.export_notebook(path, format)
        
        # For notebooks, we might want to trim the response for readability
        content = result.get("content", "")
        if len(content) > 1000:
            summary = f"{content[:1000]}... [content truncated, total length: {len(content)} characters]"
            result["content"] = summary
        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error exporting notebook: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def list_files(dbfs_path: str = "/") -> str:
    """List files and directories in DBFS"""
    logger.info(f"Listing files in: {dbfs_path}")
    try:
        result = await dbfs.list_files(dbfs_path)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def execute_sql(
    statement: str,
    warehouse_id: str,
    catalog: Optional[str] = None,
    schema: Optional[str] = None
) -> str:
    """Execute a SQL statement with smart timeout handling"""
    logger.info(f"Executing SQL statement: {statement[:100]}...")
    try:
        # Check if this looks like a quick query (metadata operations, simple selects)
        quick_query_keywords = ['SHOW', 'DESCRIBE', 'EXPLAIN', 'CREATE', 'DROP']
        is_quick = any(statement.strip().upper().startswith(keyword) for keyword in quick_query_keywords)
        
        # For simple SELECT with LIMIT, also treat as quick
        if statement.strip().upper().startswith('SELECT') and 'LIMIT' in statement.upper():
            is_quick = True
            
        if is_quick:
            # Use execute_and_wait with short timeout for quick queries
            logger.info("Quick query detected - using execute_and_wait with 30s timeout")
            result = await sql.execute_and_wait(
                statement=statement,
                warehouse_id=warehouse_id, 
                catalog=catalog,
                schema=schema,
                timeout_seconds=30
            )
        else:
            # For complex queries, just start execution and return statement_id
            logger.info("Complex query detected - starting async execution")
            result = await sql.execute_statement(statement, warehouse_id, catalog, schema)
            
            # If it completed quickly, great! If not, user gets the statement_id to check later
            status = result.get("status", {}).get("state", "")
            if status == "PENDING":
                result["note"] = "Query is running in background. Use the statement_id to check status."
                
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error executing SQL: {str(e)}")
        return json.dumps({"error": str(e)})

def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Databricks MCP server")
    logger.info(f"Databricks host: {settings.DATABRICKS_HOST}")
    
    # Same pattern as iPython MCP server
    mcp.run()

if __name__ == "__main__":
    main()