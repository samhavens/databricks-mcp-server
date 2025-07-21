"""
API for managing Databricks Unity Catalog volumes.
"""

import base64
import logging
import os
import time
from typing import Any, Dict, Optional

from src.core.utils import DatabricksAPIError, make_api_request

# Configure logging
logger = logging.getLogger(__name__)


async def upload_file_to_volume(
    local_file_path: str,
    volume_path: str,
    overwrite: bool = False,
    chunk_size: int = 8 * 1024 * 1024,  # 8MB chunks
) -> Dict[str, Any]:
    """
    Upload a local file to a Databricks Unity Catalog volume.
    
    Args:
        local_file_path: Path to local file to upload
        volume_path: Full volume path (e.g. '/Volumes/catalog/schema/volume/file.json')
        overwrite: Whether to overwrite existing file
        chunk_size: Size of chunks for large file uploads (default: 8MB)
        
    Returns:
        Dict containing upload results with success status, file size, and timing
        
    Raises:
        FileNotFoundError: If local file doesn't exist
        DatabricksAPIError: If API request fails
    """
    start_time = time.time()
    
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"Local file not found: {local_file_path}")
    
    # Get file size
    file_size = os.path.getsize(local_file_path)
    file_size_mb = file_size / (1024 * 1024)
    
    logger.info(f"Uploading {file_size_mb:.1f}MB from {local_file_path} to {volume_path}")
    
    try:
        # For volumes, we use the Files API
        with open(local_file_path, 'rb') as f:
            file_content = f.read()
        
        # Upload via PUT request to Files API
        # We'll use requests directly for binary uploads
        import requests
        from src.core.config import get_api_headers, get_databricks_api_url
        
        url = get_databricks_api_url(f"/api/2.1/fs/files{volume_path}")
        headers = get_api_headers()
        headers["Content-Type"] = "application/octet-stream"
        
        response = requests.put(
            url=url,
            headers=headers,
            data=file_content,
            params={"overwrite": str(overwrite).lower()}
        )
        
        response.raise_for_status()
        
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
        Response containing the directory listing
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Listing volume files in: {volume_path}")
    
    return make_api_request(
        "GET", 
        f"/api/2.1/fs/directories{volume_path}"
    )


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