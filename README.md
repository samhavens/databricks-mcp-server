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

The Databricks MCP Server exposes **20 comprehensive tools** across all major Databricks functionality areas:

### Cluster Management (5 tools)
- **list_clusters**: List all Databricks clusters with status and configuration details
- **create_cluster**: Create a new Databricks cluster with specified configuration
- **terminate_cluster**: Terminate a Databricks cluster
- **get_cluster**: Get detailed information about a specific Databricks cluster
- **start_cluster**: Start a terminated Databricks cluster

### Job Management (4 tools) 
- **list_jobs**: List Databricks jobs with **advanced pagination, creator filtering, and run status tracking**
- **list_job_runs**: List recent job runs with detailed execution status, duration, and result information
- **run_job**: Execute a Databricks job with optional parameters
- **create_job**: Create a new job to run a notebook (supports **serverless compute by default**)

### Notebook Management (3 tools)
- **list_notebooks**: List notebooks in a workspace directory with metadata
- **export_notebook**: Export a notebook from the workspace in various formats (Jupyter, Python, etc.)
- **create_notebook**: Create a new notebook in the workspace with specified content and language

### File System (4 tools)
- **list_files**: List files and directories in DBFS paths with size and modification details
- **upload_file_to_volume**: **Upload files to Unity Catalog volumes** with progress tracking and large file support
- **upload_file_to_dbfs**: **Upload files to DBFS** with chunked upload for large files  
- **list_volume_files**: **List files and directories in Unity Catalog volumes** with detailed metadata

### SQL Execution (3 tools)
- **execute_sql**: Execute SQL statement and wait for completion (blocking) - perfect for quick queries
- **execute_sql_nonblocking**: **Start SQL execution and return immediately** with statement_id for long-running queries
- **get_sql_status**: **Monitor and retrieve results** of non-blocking SQL executions by statement_id

### Enhanced Features

#### Advanced Job Management
- **Pagination support**: `list_jobs` includes pagination with configurable limits and offsets
- **Creator filtering**: Filter jobs by creator email (case-insensitive)  
- **Run status integration**: Automatically includes latest run status and execution duration
- **Duration calculations**: Real-time tracking of job execution times

#### Unity Catalog Integration  
- **Volume operations**: Full support for Unity Catalog volumes using **Databricks SDK**
- **Large file handling**: Optimized upload with progress tracking for multi-GB files
- **Path validation**: Automatic validation of volume paths and permissions

#### Non-blocking SQL Execution
- **Asynchronous execution**: Start long-running SQL queries without blocking
- **Status monitoring**: Real-time status tracking with detailed error reporting
- **Result retrieval**: Fetch results when queries complete successfully

## Key Features

### Serverless Compute Support
The `create_job` tool supports **serverless compute by default**, eliminating the need for cluster management:

```python
# Serverless execution (default - no cluster needed)
mcp__databricks__create_job(
    job_name="My Data Pipeline",
    notebook_path="/Users/your.email@company.com/MyNotebook",
    timeout_seconds=3600,
    parameters={"param1": "value1"}
)

# Or explicitly specify serverless
mcp__databricks__create_job(
    job_name="My Pipeline",
    notebook_path="/path/to/notebook",
    use_serverless=True  # Default
)

# Still supports cluster-based execution
mcp__databricks__create_job(
    job_name="My Pipeline",
    notebook_path="/path/to/notebook", 
    use_serverless=False,
    cluster_id="your-cluster-id"
)
```

**Benefits of serverless:**
- No cluster creation permissions required
- Auto-scaling compute resources
- Cost-efficient - pay only for execution time
- Faster job startup

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

## Usage with Claude Code

The MCP server is automatically started by Claude Code when needed. No manual server startup is required.

After installation and configuration:

1. **Start using Databricks tools in Claude Code**:
   ```
   > list all databricks clusters
   > create a job to run my notebook
   > execute SQL: SHOW CATALOGS
   ```

2. **Check available tools**:
   ```bash
   databricks-mcp list-tools
   ```

## Querying Databricks Resources

You can test the MCP server tools directly or use them through Claude Code once installed.

## Project Structure

```
databricks-mcp-server/
├── src/                                      # Source code
│   ├── __init__.py                           # Makes src a package
│   ├── __main__.py                           # Main entry point for the package
│   ├── api/                                  # Databricks API clients
│   │   ├── clusters.py                       # Cluster management APIs
│   │   ├── dbfs.py                          # DBFS file system APIs
│   │   ├── jobs.py                          # Job management APIs
│   │   ├── notebooks.py                     # Notebook workspace APIs
│   │   └── sql.py                           # SQL execution APIs
│   ├── core/                                # Core functionality
│   │   ├── config.py                        # Configuration management
│   │   ├── auth.py                          # Authentication
│   │   └── utils.py                         # Utility functions
│   ├── server/                              # Server implementation
│   │   └── simple_databricks_mcp_server.py  # Main MCP server
│   └── cli/                                 # Command-line interface
│       └── commands.py                      # CLI commands
├── tests/                                   # Test directory
│   ├── test_clusters.py                     # Unit tests for API functions
│   ├── test_direct.py                       # Integration tests
│   ├── test_tools.py                        # MCP tool tests
│   └── test_validation.py                   # Import/schema validation tests
└── pyproject.toml                           # Project configuration
```

## Development

### Linting

The project includes optional linting tools for code quality:

```bash
# Run linters (if installed in dev dependencies)
uv run pylint src/ tests/
uv run flake8 src/ tests/
uv run mypy src/
```

## Testing

The project uses pytest for testing with async support. Tests are automatically configured to run with pytest-asyncio.

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test files
uv run pytest tests/test_clusters.py -v
uv run pytest tests/test_direct.py -v
uv run pytest tests/test_tools.py -v

# Run with coverage report (if coverage is installed)
uv run pytest --cov=src tests/ --cov-report=term-missing
```

**Test Status**: ✅ 12 passed, 5 skipped (intentionally disabled)

**Test Types**:
- **Unit tests** (`test_clusters.py`): Test API functions with mocks
- **Integration tests** (`test_direct.py`, `test_tools.py`): Test MCP tools directly (requires Databricks credentials)
- **Validation tests** (`test_validation.py`): Test import and schema validation

**Note**: Integration tests will show errors if Databricks credentials are not configured, but this is expected behavior.

## Documentation

- API documentation is generated using Sphinx and can be found in the `docs/api` directory
- All code includes Google-style docstrings
- See the `examples/` directory for usage examples

## Examples

### Volume Upload Operations

**Upload a local file to Unity Catalog volume:**
```python
# Upload dataset to Unity Catalog volume
mcp__databricks__upload_file_to_volume(
    local_file_path='./data/large_dataset.json',
    volume_path='/Volumes/catalog/schema/volume/large_dataset.json',
    overwrite=True
)

# List files in the volume to verify
mcp__databricks__list_volume_files(
    volume_path='/Volumes/catalog/schema/volume/'
)
```

**Upload to DBFS for temporary processing:**
```python
# Upload script to DBFS 
mcp__databricks__upload_file_to_dbfs(
    local_file_path='./scripts/analysis.py',
    dbfs_path='/tmp/analysis.py',
    overwrite=True  
)
```

### Non-blocking SQL Execution

**Start long-running query and monitor progress:**
```python
# Start a long-running query (non-blocking)
statement_result = mcp__databricks__execute_sql_nonblocking(
    statement="SELECT COUNT(*) FROM large_table GROUP BY category",
    warehouse_id="your-warehouse-id"
)
statement_id = statement_result['statement_id']

# Check status periodically
status = mcp__databricks__get_sql_status(statement_id=statement_id)
print(f"Status: {status['state']}")  # PENDING, RUNNING, SUCCEEDED, FAILED

# When complete, retrieve results
if status['state'] == 'SUCCEEDED':
    results = status['result']
```

### Advanced Job Management  

**List jobs with filtering and pagination:**
```python
# List jobs created by specific user with pagination
jobs = mcp__databricks__list_jobs(
    limit=25,
    offset=0,
    created_by='user@company.com',
    include_run_status=True  # Include latest run info
)

# Get detailed run history for a specific job
runs = mcp__databricks__list_job_runs(
    job_id=12345,
    limit=10
)
```

For more examples, check the `examples/` directory:

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

This pattern was applied to all 20 MCP tools in the server.

## 🏗️ Implementation Architecture

### SDK vs REST API Approach

The MCP server uses a **hybrid implementation approach** optimized for reliability and performance:

#### Databricks SDK (Preferred)
**Used for**: Volume operations, authentication, and core workspace interactions
- **Benefits**: Automatic authentication, better error handling, type safety
- **Tools using SDK**: `upload_file_to_volume`, `list_volume_files`, authentication layer
- **Authentication**: Automatically discovers credentials from environment, CLI config, or instance metadata

#### REST API (Legacy)  
**Used for**: SQL execution, some job operations
- **Benefits**: Direct control over API calls, established patterns
- **Tools using REST**: `execute_sql`, `execute_sql_nonblocking`, `get_sql_status`
- **Authentication**: Uses manual token-based authentication

#### Migration Status
- ✅ **Volume operations**: Migrated to SDK (fixes 404 errors from REST)
- 🔄 **In progress**: Additional tools being evaluated for SDK migration
- 📝 **Future**: Plan to migrate remaining tools for consistency

**Recommendation**: New tools should use the Databricks SDK for better maintainability and error handling.

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