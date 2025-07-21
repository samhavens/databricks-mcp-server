"""
API for managing Databricks Unity Catalog volumes.

NOTE: This module now uses the Databricks SDK for reliable authentication and API access.
TODO: Migrate remaining REST API calls in other modules (clusters.py, jobs.py, etc.) to SDK approach.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

from databricks.sdk import WorkspaceClient

# Configure logging
logger = logging.getLogger(__name__)


def _get_workspace_client() -> WorkspaceClient:
    """Get authenticated Databricks workspace client."""
    # WorkspaceClient automatically handles authentication from:
    # 1. Environment variables (DATABRICKS_HOST, DATABRICKS_TOKEN)
    # 2. Databricks CLI profiles 
    # 3. Azure/AWS instance metadata
    return WorkspaceClient()


async def upload_file_to_volume(
    local_file_path: str,
    volume_path: str,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Upload a local file to a Databricks Unity Catalog volume.
    
    Args:
        local_file_path: Path to local file to upload
        volume_path: Full volume path (e.g. '/Volumes/catalog/schema/volume/file.json')
        overwrite: Whether to overwrite existing file (default: False)
        
    Returns:
        Dict containing upload results with success status, file size, and timing
        
    Raises:
        FileNotFoundError: If local file doesn't exist
    """
    start_time = time.time()
    
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"Local file not found: {local_file_path}")
    
    # Get file size
    file_size = os.path.getsize(local_file_path)
    file_size_mb = file_size / (1024 * 1024)
    
    logger.info(f"Uploading {file_size_mb:.1f}MB from {local_file_path} to {volume_path}")
    
    try:
        # Use Databricks SDK for upload
        w = _get_workspace_client()
        
        # Read file content
        with open(local_file_path, 'rb') as f:
            file_content = f.read()
        
        # Upload using SDK - handles authentication, chunking, retries automatically
        w.files.upload(
            file_path=volume_path,
            contents=file_content,
            overwrite=overwrite
        )
        
        end_time = time.time()
        upload_time = end_time - start_time
        
        return {
            "success": True,
            "file_size_mb": round(file_size_mb, 1),
            "upload_time_seconds": round(upload_time, 1),
            "volume_path": volume_path,
            "file_size_bytes": file_size
        }
        
    except Exception as e:
        logger.error(f"Error uploading file to volume: {str(e)}")
        end_time = time.time()
        upload_time = end_time - start_time
        
        return {
            "success": False,
            "error": str(e),
            "file_size_mb": round(file_size_mb, 1),
            "failed_after_seconds": round(upload_time, 1),
            "volume_path": volume_path
        }


def list_volume_files(volume_path: str) -> Dict[str, Any]:
    """
    List files and directories in a Unity Catalog volume.
    
    Args:
        volume_path: Volume path to list (e.g. '/Volumes/catalog/schema/volume/directory')
        
    Returns:
        Response containing the directory listing with files and subdirectories
        
    Raises:
        Exception: If the SDK request fails
    """
    logger.info(f"Listing volume files in: {volume_path}")
    
    try:
        w = _get_workspace_client()
        
        # List directory contents using SDK
        files = w.files.list_directory_contents(directory_path=volume_path)
        
        # Convert to dict format similar to REST API response
        file_list = []
        for file_info in files:
            file_list.append({
                "path": file_info.path,
                "is_directory": file_info.is_directory,
                "file_size": file_info.file_size,
                "last_modified": file_info.last_modified
            })
        
        return {
            "files": file_list,
            "path": volume_path
        }
        
    except Exception as e:
        logger.error(f"Error listing volume files: {str(e)}")
        return {"error": str(e)}


def get_volume_file_info(volume_path: str) -> Dict[str, Any]:
    """
    Get information about a file in a Unity Catalog volume.
    
    Args:
        volume_path: Full path to the file in the volume
        
    Returns:
        File information including size, modification time, etc.
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting volume file info: {volume_path}")
    
    return make_api_request(
        "HEAD",
        f"/api/2.1/fs/files{volume_path}"
    )


def delete_volume_file(
    volume_path: str,
    recursive: bool = False
) -> Dict[str, Any]:
    """
    Delete a file or directory from a Unity Catalog volume.
    
    Args:
        volume_path: Path to delete
        recursive: Whether to recursively delete directories
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting volume path: {volume_path}")
    
    params = {}
    if recursive:
        params["recursive"] = "true"
    
    return make_api_request(
        "DELETE",
        f"/api/2.1/fs/files{volume_path}",
        params=params
    )