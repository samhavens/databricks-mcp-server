"""
API for managing Databricks jobs.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.utils import DatabricksAPIError, make_api_request

# Configure logging
logger = logging.getLogger(__name__)


async def create_job(job_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new Databricks job.
    
    Args:
        job_config: Job configuration
        
    Returns:
        Response containing the job ID
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Creating new job")
    return make_api_request("POST", "/api/2.0/jobs/create", data=job_config)


async def run_job(job_id: int, notebook_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run a job now.
    
    Args:
        job_id: ID of the job to run
        notebook_params: Optional parameters for the notebook
        
    Returns:
        Response containing the run ID
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Running job: {job_id}")
    
    run_params = {"job_id": job_id}
    if notebook_params:
        run_params["notebook_params"] = notebook_params
        
    return make_api_request("POST", "/api/2.0/jobs/run-now", data=run_params)


async def list_jobs(limit: Optional[int] = None, page_token: Optional[str] = None) -> Dict[str, Any]:
    """
    List jobs with optional pagination.
    
    Args:
        limit: Maximum number of jobs to return (1-100, default: 20)
        page_token: Token for pagination (from previous response's next_page_token)
    
    Returns:
        Response containing a list of jobs and optional next_page_token
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    params = {}
    if limit is not None:
        # Databricks API limits: 1-100 for jobs list
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100
        params["limit"] = limit
    if page_token is not None:
        params["page_token"] = page_token
        
    logger.info(f"Listing jobs (limit={limit}, page_token={'***' if page_token else None})")
    return make_api_request("GET", "/api/2.0/jobs/list", params=params if params else None)


async def get_job(job_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job.
    
    Args:
        job_id: ID of the job
        
    Returns:
        Response containing job information
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for job: {job_id}")
    return make_api_request("GET", "/api/2.0/jobs/get", params={"job_id": job_id})


async def update_job(job_id: int, new_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing job.
    
    Args:
        job_id: ID of the job to update
        new_settings: New job settings
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Updating job: {job_id}")
    
    update_data = {
        "job_id": job_id,
        "new_settings": new_settings
    }
    
    return make_api_request("POST", "/api/2.0/jobs/update", data=update_data)


async def delete_job(job_id: int) -> Dict[str, Any]:
    """
    Delete a job.
    
    Args:
        job_id: ID of the job to delete
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting job: {job_id}")
    return make_api_request("POST", "/api/2.0/jobs/delete", data={"job_id": job_id})


async def get_run(run_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job run.
    
    Args:
        run_id: ID of the run
        
    Returns:
        Response containing run information
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for run: {run_id}")
    return make_api_request("GET", "/api/2.0/jobs/runs/get", params={"run_id": run_id})


async def cancel_run(run_id: int) -> Dict[str, Any]:
    """
    Cancel a job run.
    
    Args:
        run_id: ID of the run to cancel
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Cancelling run: {run_id}")
    return make_api_request("POST", "/api/2.0/jobs/runs/cancel", data={"run_id": run_id})


async def list_runs(job_id: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    List job runs, optionally filtered by job_id.
    
    Args:
        job_id: ID of the job to list runs for (optional)
        limit: Maximum number of runs to return (optional)
        
    Returns:
        Response containing a list of job runs
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    params = {}
    if job_id is not None:
        params["job_id"] = job_id
    if limit is not None:
        params["limit"] = limit
        
    logger.info(f"Listing runs (job_id={job_id}, limit={limit})")
    return make_api_request("GET", "/api/2.0/jobs/runs/list", params=params if params else None) 