"""
Databricks MCP Server

This module implements a standalone MCP server that provides tools for interacting
with Databricks APIs. It follows the Model Context Protocol standard, communicating
via stdio and directly connecting to Databricks when tools are invoked.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional, Union, cast

from mcp.server import FastMCP
from mcp.types import TextContent
from mcp.server.stdio import stdio_server

from src.api import clusters, dbfs, jobs, notebooks, sql
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabricksMCPServer(FastMCP):
    """An MCP server for Databricks APIs."""
    
    def __init__(self):
        """Initialize the Databricks MCP server."""
        super().__init__(name="databricks-mcp", 
                         version="1.0.0", 
                         instructions="Use this server to manage Databricks resources")
        logger.info("Initializing Databricks MCP server")
        logger.info(f"Databricks host: {settings.DATABRICKS_HOST}")
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all Databricks MCP tools with proper type annotations."""
        
        # Cluster management tools
        @self.tool(
            name="list_clusters",
            description="List all Databricks clusters. Use this to see available clusters in your workspace."
        )
        async def list_clusters() -> str:
            """List all clusters in the Databricks workspace."""
            logger.info("Listing clusters")
            try:
                result = await clusters.list_clusters()
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error listing clusters: {str(e)}")
                return json.dumps({"error": str(e)})

        @self.tool(
            name="create_cluster",
            description="Create a new Databricks cluster with specified configuration."
        )
        async def create_cluster(
            cluster_name: str,
            spark_version: str,
            node_type_id: str,
            num_workers: int = 1,
            cluster_log_conf: Optional[Dict[str, Any]] = None,
            enable_elastic_disk: bool = True
        ) -> str:
            """Create a new Databricks cluster."""
            logger.info(f"Creating cluster: {cluster_name}")
            try:
                cluster_config = {
                    "cluster_name": cluster_name,
                    "spark_version": spark_version,
                    "node_type_id": node_type_id,
                    "num_workers": num_workers,
                    "enable_elastic_disk": enable_elastic_disk
                }
                if cluster_log_conf:
                    cluster_config["cluster_log_conf"] = cluster_log_conf
                    
                result = await clusters.create_cluster(cluster_config)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error creating cluster: {str(e)}")
                return json.dumps({"error": str(e)})

        @self.tool(
            name="terminate_cluster",
            description="Terminate a specific Databricks cluster."
        )
        async def terminate_cluster(cluster_id: str) -> str:
            """Terminate a Databricks cluster by ID."""
            logger.info(f"Terminating cluster: {cluster_id}")
            try:
                result = await clusters.terminate_cluster(cluster_id)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error terminating cluster: {str(e)}")
                return json.dumps({"error": str(e)})

        @self.tool(
            name="get_cluster",
            description="Get detailed information about a specific Databricks cluster."
        )
        async def get_cluster(cluster_id: str) -> str:
            """Get details of a specific cluster."""
            logger.info(f"Getting cluster info: {cluster_id}")
            try:
                result = await clusters.get_cluster(cluster_id)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error getting cluster info: {str(e)}")
                return json.dumps({"error": str(e)})

        @self.tool(
            name="start_cluster",
            description="Start a stopped Databricks cluster."
        )
        async def start_cluster(cluster_id: str) -> str:
            """Start a Databricks cluster by ID."""
            logger.info(f"Starting cluster: {cluster_id}")
            try:
                result = await clusters.start_cluster(cluster_id)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error starting cluster: {str(e)}")
                return json.dumps({"error": str(e)})

        # Job management tools
        @self.tool(
            name="list_jobs",
            description="List all Databricks jobs. Use this to see available jobs in your workspace."
        )
        async def list_jobs() -> str:
            """List all jobs in the Databricks workspace."""
            logger.info("Listing jobs")
            try:
                result = await jobs.list_jobs()
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error listing jobs: {str(e)}")
                return json.dumps({"error": str(e)})

        @self.tool(
            name="run_job",
            description="Run a Databricks job with optional parameters."
        )
        async def run_job(job_id: str, notebook_params: Optional[Dict[str, str]] = None) -> str:
            """Run a Databricks job by ID with optional notebook parameters."""
            logger.info(f"Running job: {job_id}")
            try:
                params = notebook_params or {}
                result = await jobs.run_job(job_id, params)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error running job: {str(e)}")
                return json.dumps({"error": str(e)})

        # Notebook management tools
        @self.tool(
            name="list_notebooks",
            description="List notebooks in a workspace directory."
        )
        async def list_notebooks(path: str = "/") -> str:
            """List notebooks in the specified workspace directory."""
            logger.info(f"Listing notebooks in path: {path}")
            try:
                result = await notebooks.list_notebooks(path)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error listing notebooks: {str(e)}")
                return json.dumps({"error": str(e)})

        @self.tool(
            name="export_notebook",
            description="Export a notebook from the workspace in the specified format."
        )
        async def export_notebook(
            path: str, 
            format: str = "JUPYTER"
        ) -> str:
            """Export a notebook from the workspace."""
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

        # DBFS tools
        @self.tool(
            name="list_files",
            description="List files and directories in DBFS (Databricks File System)."
        )
        async def list_files(dbfs_path: str = "/") -> str:
            """List files and directories in the specified DBFS path."""
            logger.info(f"Listing files in DBFS path: {dbfs_path}")
            try:
                result = await dbfs.list_files(dbfs_path)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error listing files: {str(e)}")
                return json.dumps({"error": str(e)})

        # SQL tools
        @self.tool(
            name="execute_sql",
            description="Execute a SQL statement in Databricks SQL warehouse."
        )
        async def execute_sql(
            statement: str,
            warehouse_id: str,
            catalog: Optional[str] = None,
            schema: Optional[str] = None
        ) -> str:
            """Execute a SQL statement in the specified warehouse."""
            logger.info(f"Executing SQL: {statement[:100]}...")
            try:
                result = await sql.execute_sql(statement, warehouse_id, catalog, schema)
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error executing SQL: {str(e)}")
                return json.dumps({"error": str(e)})

async def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Databricks MCP server")
        server = DatabricksMCPServer()
        
        # Use the built-in method for stdio servers
        # This is the recommended approach for MCP servers
        await server.run_stdio_async()
            
    except Exception as e:
        logger.error(f"Error in Databricks MCP server: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    # Turn off buffering in stdout
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(line_buffering=True)
    
    asyncio.run(main()) 