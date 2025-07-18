# Databricks MCP Server Examples

This directory contains examples of how to use the Databricks MCP server.

## Example Files

1. **Direct Usage (direct_usage.py)**
   
   This example shows how to directly instantiate and use the Databricks MCP server
   without going through the MCP protocol. It demonstrates:
   
   - Creating a server instance
   - Calling tools directly
   - Processing the results

   To run this example:
   ```bash
   uv run examples/direct_usage.py
   ```

2. **MCP Client Usage (mcp_client_usage.py)**
   
   This example shows how to use the MCP client to connect to the Databricks MCP server
   and call its tools through the MCP protocol. It demonstrates:
   
   - Connecting to the server using the MCP protocol
   - Listing available tools
   - Calling tools through the MCP protocol
   - Processing the results

   To run this example:
   ```bash
   uv run examples/mcp_client_usage.py
   ```

## Running Examples

Make sure you have the following prerequisites:

1. Python 3.10+ installed
2. `uv` package manager installed (see project README for installation instructions)
3. Project environment set up with `uv venv`
4. Dependencies installed with `uv add`
5. Environment variables set (DATABRICKS_HOST, DATABRICKS_TOKEN)

First, make sure you're in the project root directory and the virtual environment is activated:

```bash
# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

Then you can run the examples as shown above.

## Example Outputs

### Direct Usage Example Output

```
Databricks MCP Server - Direct Usage Example
===========================================

Databricks Clusters:
====================

Cluster 1:
  ID: 0220-221815-kzacbcps
  Name: Lloyd Burley's Cluster LTS
  State: TERMINATED
  Spark Version: 15.4.x-scala2.12
  Node Type: Standard_DS3_v2

Databricks Notebooks in /:
================================

Notebook: /Shared/example_notebook
Directory: /Users/

Databricks Jobs:
================

Job 1:
  ID: 12345
  Name: Daily ETL Job
  Created: 1740089895875
```

### MCP Client Usage Example Output

```
Databricks MCP Server - MCP Client Usage Example
=============================================
2025-03-13 10:05:23,456 - __main__ - INFO - Connecting to Databricks MCP server...
2025-03-13 10:05:23,457 - __main__ - INFO - Launching server process...
2025-03-13 10:05:23,789 - __main__ - INFO - Server launched, creating session...
2025-03-13 10:05:23,790 - __main__ - INFO - Initializing session...

Available Tools:
================
- list_clusters: List all Databricks clusters
- create_cluster: Create a new Databricks cluster with parameters: cluster_name (required), spark_version (required), node_type_id (required), num_workers, autotermination_minutes
- terminate_cluster: Terminate a Databricks cluster with parameter: cluster_id (required)
- get_cluster: Get information about a specific Databricks cluster with parameter: cluster_id (required)
- start_cluster: Start a terminated Databricks cluster with parameter: cluster_id (required)
- list_jobs: List all Databricks jobs
- run_job: Run a Databricks job with parameters: job_id (required), notebook_params (optional)
- list_notebooks: List notebooks in a workspace directory with parameter: path (required)
- export_notebook: Export a notebook from the workspace with parameters: path (required), format (optional, one of: SOURCE, HTML, JUPYTER, DBC)
- list_files: List files and directories in a DBFS path with parameter: dbfs_path (required)
- execute_sql: Execute a SQL statement with parameters: statement (required), warehouse_id (required), catalog (optional), schema (optional)

Select a tool to run (or 'quit' to exit):
1. list_clusters
2. create_cluster
3. terminate_cluster
4. get_cluster
5. start_cluster
6. list_jobs
7. run_job
8. list_notebooks
9. export_notebook
10. list_files
11. execute_sql
``` 