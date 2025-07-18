"""
Main entry point for running the databricks-mcp-server package.
This allows the package to be run with 'python -m src' or 'uv run src'.
"""

import asyncio
from src.main import main

if __name__ == "__main__":
    asyncio.run(main()) 