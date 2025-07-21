# API Implementation Notes

## SDK vs REST Approach

This MCP server uses a **mixed approach** for Databricks API access:

### ✅ **SDK-Based Modules** (Recommended)
- `src/api/volumes.py` - Uses Databricks SDK `WorkspaceClient`

**Benefits:**
- Automatic authentication handling (CLI profiles, env vars, instance metadata)
- Built-in error handling and retries
- Type safety and better IDE support
- Automatic API versioning and endpoint management
- Handles complex operations (file chunking, pagination) automatically

### ⚠️ **REST API Modules** (Legacy - Should Migrate)
- `src/api/clusters.py` - Uses manual REST calls
- `src/api/jobs.py` - Uses manual REST calls  
- `src/api/notebooks.py` - Uses manual REST calls
- `src/api/sql.py` - Uses manual REST calls
- `src/api/dbfs.py` - Uses manual REST calls

**Issues with REST approach:**
- Manual authentication token management
- Manual error handling and retries
- Hardcoded API endpoints that may change
- Complex operations require manual implementation

## Migration Plan

**Priority Order:**
1. **High**: `sql.py` - SQL operations are core functionality
2. **Medium**: `jobs.py` - Job management is frequently used  
3. **Medium**: `notebooks.py` - Notebook operations
4. **Low**: `clusters.py` - Cluster management (less frequent)
5. **Low**: `dbfs.py` - DBFS operations (volumes are preferred)

## SDK Examples

```python
from databricks.sdk import WorkspaceClient

def _get_workspace_client() -> WorkspaceClient:
    """Get authenticated client - handles auth automatically."""
    return WorkspaceClient()

# Example usage
w = _get_workspace_client()

# Files operations
w.files.upload(file_path="/Volumes/path/file.txt", contents=data)
w.files.list_directory_contents("/Volumes/path/")

# SQL operations  
w.statement_execution.execute_statement(statement="SELECT 1", warehouse_id="abc123")

# Jobs operations
w.jobs.run_now(job_id=123, notebook_params={"param": "value"})
```

## Implementation Status

- ✅ Volume upload/list operations (SDK-based)
- ⚠️ SQL execution (REST-based, needs migration)  
- ⚠️ Job management (REST-based, needs migration)
- ⚠️ Notebook operations (REST-based, needs migration)
- ⚠️ Cluster management (REST-based, needs migration)
- ⚠️ DBFS operations (REST-based, needs migration)