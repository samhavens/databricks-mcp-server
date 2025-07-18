# Tests for Databricks MCP Server

This directory contains test scripts for the Databricks MCP server.

## Test Files

1. **Direct Test (direct_test.py)**
   
   This test directly instantiates the Databricks MCP server and calls its tools
   without going through the MCP protocol. It's useful for testing the core
   functionality without the overhead of the MCP protocol.

2. **MCP Client Test (mcp_client_test.py)**
   
   This test uses the MCP client to connect to the Databricks MCP server and test
   its tools through the MCP protocol. It's useful for testing the server's
   compatibility with the MCP protocol.

3. **List Tools Test (list_tools_test.py)**
   
   This test connects to the Databricks MCP server using the MCP client and lists
   all available tools. It's a simple test to verify that the server is running
   and properly responding to the MCP protocol.

## Running Tests

You can run the tests using the provided shell scripts in the project root:

### Windows (PowerShell)

```powershell
.\run_direct_test.ps1     # Run the direct test
.\run_list_tools.ps1      # Run the list tools test
.\run_mcp_client_test.ps1 # Run the MCP client test
```

### Linux/Mac

```bash
./run_direct_test.sh     # Run the direct test
./run_list_tools.sh      # Run the list tools test
./run_mcp_client_test.sh # Run the MCP client test
```

## Running Tests Manually

If you want to run the tests manually:

```bash
# Activate the environment
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\activate   # Windows

# Run the tests
uv run -m tests.direct_test
uv run -m tests.list_tools_test
uv run -m tests.mcp_client_test
```

## Adding New Tests

When adding new tests, please follow these guidelines:

1. Create a new Python file in the `tests` directory.
2. Import the necessary modules from the `src` directory.
3. Create a shell script in the project root to run the test.
4. Document the test in this README. 