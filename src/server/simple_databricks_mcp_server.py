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

from src.api import clusters, dbfs, jobs, notebooks, sql, volumes
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
async def list_jobs(
    limit: int = 25, 
    offset: int = 0, 
    created_by: Optional[str] = None,
    include_run_status: bool = True
) -> str:
    """List Databricks jobs with pagination and filtering.
    
    Args:
        limit: Number of jobs to return (default: 25, keeps response under token limits)
        offset: Starting position for pagination (default: 0, use pagination_info.next_offset for next page)
        created_by: Filter by creator email (e.g. 'user@company.com'), case-insensitive, optional
        include_run_status: Include latest run status and duration (default: true, set false for faster response)
    
    Returns:
        JSON with jobs array and pagination_info. Each job includes latest_run with state, duration_minutes, etc.
        Use pagination_info.next_offset for next page. Total jobs shown in pagination_info.total_jobs.
    """
    logger.info(f"Listing jobs (limit={limit}, offset={offset}, created_by={created_by})")
    try:
        # Fetch all jobs from API
        result = await jobs.list_jobs()
        
        if "jobs" in result:
            all_jobs = result["jobs"]
            
            # Filter by creator if specified
            if created_by:
                all_jobs = [job for job in all_jobs 
                           if job.get("creator_user_name", "").lower() == created_by.lower()]
            
            total_jobs = len(all_jobs)
            
            # Apply client-side pagination
            start_idx = offset
            end_idx = offset + limit
            paginated_jobs = all_jobs[start_idx:end_idx]
            
            # Enhance jobs with run status if requested
            if include_run_status and paginated_jobs:
                enhanced_jobs = []
                for job in paginated_jobs:
                    enhanced_job = job.copy()
                    
                    # Get most recent run for this job
                    try:
                        runs_result = await jobs.list_runs(job_id=job["job_id"], limit=1)
                        if "runs" in runs_result and runs_result["runs"]:
                            latest_run = runs_result["runs"][0]
                            
                            # Add run status info
                            enhanced_job["latest_run"] = {
                                "run_id": latest_run.get("run_id"),
                                "state": latest_run.get("state", {}).get("life_cycle_state"),
                                "result_state": latest_run.get("state", {}).get("result_state"),
                                "start_time": latest_run.get("start_time"),
                                "end_time": latest_run.get("end_time"),
                            }
                            
                            # Calculate duration if both times available
                            start_time = latest_run.get("start_time")
                            end_time = latest_run.get("end_time")
                            if start_time and end_time:
                                duration_ms = end_time - start_time
                                enhanced_job["latest_run"]["duration_seconds"] = duration_ms // 1000
                                enhanced_job["latest_run"]["duration_minutes"] = duration_ms // 60000
                        else:
                            enhanced_job["latest_run"] = {"status": "no_runs"}
                            
                    except Exception as e:
                        enhanced_job["latest_run"] = {"error": f"Failed to get run info: {str(e)}"}
                    
                    enhanced_jobs.append(enhanced_job)
                
                paginated_jobs = enhanced_jobs
            
            # Create paginated response
            paginated_result = {
                "jobs": paginated_jobs,
                "pagination_info": {
                    "total_jobs": total_jobs,
                    "returned": len(paginated_jobs),
                    "limit": limit,
                    "offset": offset,
                    "has_more": end_idx < total_jobs,
                    "next_offset": end_idx if end_idx < total_jobs else None,
                    "filtered_by": {"created_by": created_by} if created_by else None
                }
            }
            
            return json.dumps(paginated_result)
        else:
            return json.dumps(result)
            
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def list_job_runs(job_id: Optional[int] = None, limit: int = 10) -> str:
    """List recent job runs with detailed status and duration information.
    
    Args:
        job_id: Specific job ID to list runs for (optional, omit to see runs across all jobs)
        limit: Number of runs to return (default: 10, most recent first)
    
    Returns:
        JSON with runs array. Each run includes state (RUNNING/SUCCESS/FAILED), result_state, 
        duration_minutes for completed runs, current_duration_minutes for running jobs.
    """
    logger.info(f"Listing job runs (job_id={job_id}, limit={limit})")
    try:
        result = await jobs.list_runs(job_id=job_id, limit=limit)
        
        if "runs" in result:
            enhanced_runs = []
            for run in result["runs"]:
                enhanced_run = run.copy()
                
                # Calculate duration if both times available
                start_time = run.get("start_time")
                end_time = run.get("end_time")
                if start_time and end_time:
                    duration_ms = end_time - start_time
                    enhanced_run["duration_seconds"] = duration_ms // 1000
                    enhanced_run["duration_minutes"] = duration_ms // 60000
                elif start_time and not end_time:
                    # Running job - calculate current duration
                    import time
                    current_time = int(time.time() * 1000)
                    duration_ms = current_time - start_time
                    enhanced_run["current_duration_seconds"] = duration_ms // 1000
                    enhanced_run["current_duration_minutes"] = duration_ms // 60000
                
                enhanced_runs.append(enhanced_run)
            
            result["runs"] = enhanced_runs
        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error listing job runs: {str(e)}")
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
    schema_name: Optional[str] = None
) -> str:
    """Execute a SQL statement and wait for completion (blocking)"""
    logger.info(f"Executing SQL statement (blocking): {statement[:100]}...")
    try:
        result = await sql.execute_and_wait(
            statement=statement,
            warehouse_id=warehouse_id, 
            catalog=catalog,
            schema=schema_name,
            timeout_seconds=300  # 5 minutes max
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error executing SQL: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def execute_sql_nonblocking(
    statement: str,
    warehouse_id: str,
    catalog: Optional[str] = None,
    schema_name: Optional[str] = None
) -> str:
    """Start SQL statement execution and return immediately with statement_id (non-blocking)"""
    logger.info(f"Executing SQL statement (non-blocking): {statement[:100]}...")
    try:
        result = await sql.execute_statement(statement, warehouse_id, catalog, schema_name)
        
        # Add helpful info about checking status
        status = result.get("status", {}).get("state", "")
        if status == "PENDING":
            result["note"] = "Query started. Use get_sql_status with the statement_id to check progress."
            
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error executing SQL: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_sql_status(statement_id: str) -> str:
    """Get the status and results of a SQL statement by statement_id"""
    logger.info(f"Getting status for SQL statement: {statement_id}")
    try:
        result = await sql.get_statement_status(statement_id)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error getting SQL status: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def create_notebook(
    path: str,
    content: str,
    language: str = "PYTHON",
    overwrite: bool = False
) -> str:
    """Create a new notebook in the Databricks workspace"""
    logger.info(f"Creating notebook at path: {path}")
    try:
        result = await notebooks.import_notebook(
            path=path,
            content=content,
            format="SOURCE",
            language=language.upper(),
            overwrite=overwrite
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error creating notebook: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def create_job(
    job_name: str,
    notebook_path: str,
    timeout_seconds: int = 3600,
    parameters: Optional[dict] = None,
    cluster_id: Optional[str] = None,
    use_serverless: bool = True
) -> str:
    """Create a new Databricks job to run a notebook (uses serverless by default)"""
    logger.info(f"Creating job: {job_name}")
    try:
        task_config = {
            "task_key": "main_task",
            "notebook_task": {
                "notebook_path": notebook_path,
                "base_parameters": parameters or {}
            },
            "timeout_seconds": timeout_seconds
        }
        
        # Configure compute: serverless vs cluster  
        if use_serverless:
            # For serverless compute, simply don't specify any cluster configuration
            # Databricks will automatically use serverless compute
            pass
        elif cluster_id:
            task_config["existing_cluster_id"] = cluster_id
        else:
            raise ValueError("Must specify either use_serverless=True or provide cluster_id")
            
        job_config = {
            "name": job_name,
            "tasks": [task_config],
            "format": "MULTI_TASK"
        }
        
        result = await jobs.create_job(job_config)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def upload_file_to_volume(
    local_file_path: str,
    volume_path: str,
    overwrite: bool = False
) -> str:
    """
    Upload a local file to a Databricks Unity Catalog volume.

    Args:
        local_file_path: Path to local file (e.g. './data/products.json')
        volume_path: Full volume path (e.g. '/Volumes/catalog/schema/volume/file.json')
        overwrite: Whether to overwrite existing file (default: False)

    Returns:
        JSON with upload results including success status, file size in MB, and upload time.
        
    Example:
        # Upload large dataset to volume
        result = upload_file_to_volume(
            local_file_path='./stark_export/products_full.json',
            volume_path='/Volumes/kbqa/stark_mas_eval/stark_raw_data/products_full.json',
            overwrite=True
        )
        
    Note: Handles large files (multi-GB) with progress tracking and proper error handling.
    Perfect for uploading extracted datasets to Unity Catalog volumes for processing.
    """
    logger.info(f"Uploading file from {local_file_path} to volume: {volume_path}")
    try:
        result = await volumes.upload_file_to_volume(
            local_file_path=local_file_path,
            volume_path=volume_path,
            overwrite=overwrite
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error uploading file to volume: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "volume_path": volume_path
        })

@mcp.tool()
async def upload_file_to_dbfs(
    local_file_path: str,
    dbfs_path: str,
    overwrite: bool = True
) -> str:
    """
    Upload a local file to Databricks File System (DBFS).

    Args:
        local_file_path: Path to local file (e.g. './data/notebook.py')
        dbfs_path: DBFS path (e.g. '/tmp/uploaded/notebook.py')
        overwrite: Whether to overwrite existing file (default: True)

    Returns:
        JSON with upload results including success status, file size, and upload time.
        
    Example:
        # Upload script to DBFS
        result = upload_file_to_dbfs(
            local_file_path='./scripts/analysis.py',
            dbfs_path='/tmp/analysis.py',
            overwrite=True
        )
        
    Note: For large files (>10MB), uses chunked upload with proper retry logic.
    DBFS is good for temporary files, scripts, and smaller datasets.
    """
    logger.info(f"Uploading file from {local_file_path} to DBFS: {dbfs_path}")
    try:
        import os
        import time
        
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        # Get file info
        start_time = time.time()
        file_size = os.path.getsize(local_file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Choose upload method based on file size
        if file_size > 10 * 1024 * 1024:  # > 10MB
            result = await dbfs.upload_large_file(
                dbfs_path=dbfs_path,
                local_file_path=local_file_path,
                overwrite=overwrite
            )
        else:
            # Read and upload small file
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            result = await dbfs.put_file(
                dbfs_path=dbfs_path,
                file_content=file_content,
                overwrite=overwrite
            )
        
        end_time = time.time()
        upload_time = end_time - start_time
        
        return json.dumps({
            "success": True,
            "file_size_mb": round(file_size_mb, 1),
            "upload_time_seconds": round(upload_time, 1),
            "dbfs_path": dbfs_path,
            "file_size_bytes": file_size
        })
        
    except Exception as e:
        logger.error(f"Error uploading file to DBFS: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "dbfs_path": dbfs_path
        })

@mcp.tool()
async def list_volume_files(volume_path: str) -> str:
    """
    List files and directories in a Unity Catalog volume.

    Args:
        volume_path: Volume path to list (e.g. '/Volumes/catalog/schema/volume/directory')

    Returns:
        JSON with directory listing including file names, sizes, and modification times.
        
    Example:
        # List files in volume directory
        files = list_volume_files('/Volumes/kbqa/stark_mas_eval/stark_raw_data/')
        
    Note: Returns detailed file information including sizes for managing large datasets.
    """
    logger.info(f"Listing volume files in: {volume_path}")
    try:
        result = volumes.list_volume_files(volume_path)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error listing volume files: {str(e)}")
        return json.dumps({"error": str(e)})

def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Databricks MCP server")
    logger.info(f"Databricks host: {settings.DATABRICKS_HOST}")
    
    # Same pattern as iPython MCP server
    mcp.run()

if __name__ == "__main__":
    main()