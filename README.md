# Databricks MCP Server - Working Version

A **fixed** version of the Databricks MCP Server that properly works with Claude Code and other MCP clients.

## 🔧 What Was Fixed

This is a **working fork** of the original Databricks MCP server that fixes critical issues preventing it from working with Claude Code and other MCP clients.

**Original Repository**: https://github.com/JustTryAI/databricks-mcp-server

### The Problems
1. **Asyncio event loop conflict**: Original server used `asyncio.run()` inside MCP tool functions, causing `asyncio.run() cannot be called from a running event loop` errors when used with Claude Code (which already runs in an async context)

2. **Command spawning issues**: Claude Code's MCP client can only spawn single executables, not commands with arguments like `databricks-mcp start`

3. **SQL API issues**: Byte limit too high (100MB vs 25MB max), no API endpoint fallback for different Databricks workspace configurations

### The Solutions
1. **Fixed async patterns**: Created `simple_databricks_mcp_server.py` that follows the working iPython MCP pattern - changed all tools to use `async def` with `await` instead of `asyncio.run()`

2. **Simplified CLI**: Modified the CLI to default to starting the server when no command is provided, eliminating the need for wrapper scripts

3. **SQL API improvements**: 
   - Reduced byte_limit from 100MB to 25MB (Databricks maximum allowed)
   - Added API endpoint fallback: tries `/statements` first, then `/statements/execute`
   - Better error logging when SQL APIs fail

## 🚀 Quick Start for Claude Code Users

1. **Install directly from GitHub**:
```bash
uv tool install git+https://github.com/samhavens/databricks-mcp-server.git
```

Or **clone and install locally**:
```bash
git clone https://github.com/samhavens/databricks-mcp-server.git
cd databricks-mcp-server
uv tool install --editable .
```

2. **Configure credentials**:
```bash
cp .env.example .env
# Edit .env with your Databricks host and token
```

3. **Add to Claude Code**:
```bash
claude mcp add databricks "databricks-mcp"
```

4. **Test it works**:
```
> list all databricks clusters
```

### Why no arguments needed?

The CLI now defaults to starting the server when no command is provided, making it compatible with Claude Code's MCP client (which can only spawn single executables without arguments).

---

## About This MCP Server

A Model Completion Protocol (MCP) server for Databricks that provides access to Databricks functionality via the MCP protocol. This allows LLM-powered tools to interact with Databricks clusters, jobs, notebooks, and more.

## Features

- **MCP Protocol Support**: Implements the MCP protocol to allow LLMs to interact with Databricks
- **Databricks API Integration**: Provides access to Databricks REST API functionality
- **Tool Registration**: Exposes Databricks functionality as MCP tools
- **Async Support**: Built with asyncio for efficient operation

## Available Tools

The Databricks MCP Server exposes the following tools:

- **list_clusters**: List all Databricks clusters
- **create_cluster**: Create a new Databricks cluster
- **terminate_cluster**: Terminate a Databricks cluster
- **get_cluster**: Get information about a specific Databricks cluster
- **start_cluster**: Start a terminated Databricks cluster
- **list_jobs**: List all Databricks jobs
- **run_job**: Run a Databricks job
- **list_notebooks**: List notebooks in a workspace directory
- **export_notebook**: Export a notebook from the workspace
- **list_files**: List files and directories in a DBFS path
- **execute_sql**: Execute a SQL statement

## Installation

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended for MCP servers)

### Setup

1. Install `uv` if you don't have it already:

   ```bash
   # MacOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows (in PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   ```

   Restart your terminal after installation.

2. Clone the repository:
   ```bash
   git clone https://github.com/samhavens/databricks-mcp-server.git
   cd databricks-mcp-server
   ```

3. Set up the project with `uv`:
   ```bash
   # Create and activate virtual environment
   uv venv
   
   # On Windows
   .\.venv\Scripts\activate
   
   # On Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies in development mode
   uv pip install -e .
   
   # Install development dependencies
   uv pip install -e ".[dev]"
   ```

4. Set up environment variables:
   ```bash
   # Windows
   set DATABRICKS_HOST=https://your-databricks-instance.azuredatabricks.net
   set DATABRICKS_TOKEN=your-personal-access-token
   
   # Linux/Mac
   export DATABRICKS_HOST=https://your-databricks-instance.azuredatabricks.net
   export DATABRICKS_TOKEN=your-personal-access-token
   ```

   You can also create an `.env` file based on the `.env.example` template.

## Running the MCP Server

To start the MCP server, run:

```bash
# Windows
.\start_mcp_server.ps1

# Linux/Mac
./start_mcp_server.sh
```

These wrapper scripts will execute the actual server scripts located in the `scripts` directory. The server will start and be ready to accept MCP protocol connections.

You can also directly run the server scripts from the scripts directory:

```bash
# Windows
.\scripts\start_mcp_server.ps1

# Linux/Mac
./scripts/start_mcp_server.sh
```

## Querying Databricks Resources

The repository includes utility scripts to quickly view Databricks resources:

```bash
# View all clusters
uv run scripts/show_clusters.py

# View all notebooks
uv run scripts/show_notebooks.py
```

## Project Structure

```
databricks-mcp-server/
├── src/                             # Source code
│   ├── __init__.py                  # Makes src a package
│   ├── __main__.py                  # Main entry point for the package
│   ├── main.py                      # Entry point for the MCP server
│   ├── api/                         # Databricks API clients
│   ├── core/                        # Core functionality
│   ├── server/                      # Server implementation
│   │   ├── databricks_mcp_server.py # Main MCP server
│   │   └── app.py                   # FastAPI app for tests
│   └── cli/                         # Command-line interface
├── tests/                           # Test directory
├── scripts/                         # Helper scripts
│   ├── start_mcp_server.ps1         # Server startup script (Windows)
│   ├── run_tests.ps1                # Test runner script
│   ├── show_clusters.py             # Script to show clusters
│   └── show_notebooks.py            # Script to show notebooks
├── examples/                        # Example usage
├── docs/                            # Documentation
└── pyproject.toml                   # Project configuration
```

See `project_structure.md` for a more detailed view of the project structure.

## Development

### Code Standards

- Python code follows PEP 8 style guide with a maximum line length of 100 characters
- Use 4 spaces for indentation (no tabs)
- Use double quotes for strings
- All classes, methods, and functions should have Google-style docstrings
- Type hints are required for all code except tests

### Linting

The project uses the following linting tools:

```bash
# Run all linters
uv run pylint src/ tests/
uv run flake8 src/ tests/
uv run mypy src/
```

## Testing

The project uses pytest for testing. To run the tests:

```bash
# Run all tests with our convenient script
.\scripts\run_tests.ps1

# Run with coverage report
.\scripts\run_tests.ps1 -Coverage

# Run specific tests with verbose output
.\scripts\run_tests.ps1 -Verbose -Coverage tests/test_clusters.py
```

You can also run the tests directly with pytest:

```bash
# Run all tests
uv run pytest tests/

# Run with coverage report
uv run pytest --cov=src tests/ --cov-report=term-missing
```

A minimum code coverage of 80% is the goal for the project.

## Documentation

- API documentation is generated using Sphinx and can be found in the `docs/api` directory
- All code includes Google-style docstrings
- See the `examples/` directory for usage examples

## Examples

Check the `examples/` directory for usage examples. To run examples:

```bash
# Run example scripts with uv
uv run examples/direct_usage.py
uv run examples/mcp_client_usage.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Ensure your code follows the project's coding standards
2. Add tests for any new functionality
3. Update documentation as necessary
4. Verify all tests pass before submitting

## 🔍 Technical Details

The key fix was changing from:
```python
@mcp.tool()
def list_clusters() -> str:
    result = asyncio.run(clusters.list_clusters())  # ❌ Breaks in async context
    return json.dumps(result)
```

To:
```python
@mcp.tool()
async def list_clusters() -> str:
    result = await clusters.list_clusters()  # ✅ Works in async context
    return json.dumps(result)
```

This pattern was applied to all 11 MCP tools in the server.

## 📝 Original Repository

Based on: https://github.com/JustTryAI/databricks-mcp-server

## 🐛 Issues Fixed

- ✅ `asyncio.run() cannot be called from a running event loop`
- ✅ `spawn databricks-mcp start ENOENT` (command with arguments not supported)
- ✅ MCP server connection failures with Claude Code
- ✅ Proper async/await patterns for MCP tools
- ✅ SQL execution byte limit issues (100MB → 25MB)
- ✅ SQL API endpoint compatibility across different Databricks workspaces
- ✅ Better error handling and logging for SQL operations

## License

This project is licensed under the MIT License - see the LICENSE file for details. 