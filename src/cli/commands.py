"""
Command-line interface for the Databricks MCP server.

This module provides command-line functionality for interacting with the Databricks MCP server.
"""

import argparse
import asyncio
import logging
import sys
from typing import List, Optional

from src.server.simple_databricks_mcp_server import main as server_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Databricks MCP Server CLI")
    
    # Create subparsers for different commands (optional - defaults to starting server)
    subparsers = parser.add_subparsers(dest="command", help="Command to run (default: start server)")
    
    # Start server command
    start_parser = subparsers.add_parser("start", help="Start the MCP server")
    start_parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    
    # List tools command
    list_parser = subparsers.add_parser("list-tools", help="List available tools")
    
    # Version command
    subparsers.add_parser("version", help="Show server version")
    
    return parser.parse_args(args)


def show_version() -> None:
    """Show the server version."""
    print(f"\nDatabricks MCP Server v0.1.0")


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parsed_args = parse_args(args)
    
    # Set log level
    if hasattr(parsed_args, "debug") and parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Execute the appropriate command
    if parsed_args.command == "start":
        logger.info("Starting Databricks MCP server")
        server_main()
    elif parsed_args.command == "list-tools":
        print("\nAvailable tools: list_clusters, create_cluster, terminate_cluster, get_cluster, start_cluster, list_jobs, list_job_runs, run_job, list_notebooks, export_notebook, list_files, execute_sql, execute_sql_nonblocking, get_sql_status, create_notebook, create_job")
    elif parsed_args.command == "version":
        show_version()
    else:
        # If no command is provided, start the server (for Claude Code compatibility)
        logger.info("No command provided, starting Databricks MCP server")
        server_main()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 