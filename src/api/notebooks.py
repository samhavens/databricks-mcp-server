"""
API for managing Databricks notebooks.
"""

import base64
import logging
from typing import Any, Dict, List, Optional

from src.core.utils import DatabricksAPIError, make_api_request

# Configure logging
logger = logging.getLogger(__name__)


async def import_notebook(
    path: str,
    content: str,
    format: str = "SOURCE",
    language: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """
    Import a notebook into the workspace.
    
    Args:
        path: The path where the notebook should be stored
        content: The content of the notebook (base64 encoded)
        format: The format of the notebook (SOURCE, HTML, JUPYTER, DBC)
        language: The language of the notebook (SCALA, PYTHON, SQL, R)
        overwrite: Whether to overwrite an existing notebook
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Importing notebook to path: {path}")
    
    # Ensure content is base64 encoded
    if not is_base64(content):
        content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    import_data = {
        "path": path,
        "format": format,
        "content": content,
        "overwrite": overwrite,
    }
    
    if language:
        import_data["language"] = language
        
    return make_api_request("POST", "/api/2.0/workspace/import", data=import_data)


async def export_notebook(
    path: str,
    format: str = "SOURCE",
) -> Dict[str, Any]:
    """
    Export a notebook from the workspace.
    
    Args:
        path: The path of the notebook to export
        format: The format to export (SOURCE, HTML, JUPYTER, DBC)
        
    Returns:
        Response containing the notebook content
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Exporting notebook from path: {path}")
    
    params = {
        "path": path,
        "format": format,
    }
    
    response = make_api_request("GET", "/api/2.0/workspace/export", params=params)
    
    # Optionally decode base64 content
    if "content" in response and format in ["SOURCE", "JUPYTER"]:
        try:
            response["decoded_content"] = base64.b64decode(response["content"]).decode("utf-8")
        except Exception as e:
            logger.warning(f"Failed to decode notebook content: {str(e)}")
            
    return response


async def list_notebooks(path: str) -> Dict[str, Any]:
    """
    List notebooks in a workspace directory.
    
    Args:
        path: The path to list
        
    Returns:
        Response containing the directory listing
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Listing notebooks in path: {path}")
    return make_api_request("GET", "/api/2.0/workspace/list", params={"path": path})


async def delete_notebook(path: str, recursive: bool = False) -> Dict[str, Any]:
    """
    Delete a notebook or directory.
    
    Args:
        path: The path to delete
        recursive: Whether to recursively delete directories
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting path: {path}")
    return make_api_request(
        "POST", 
        "/api/2.0/workspace/delete", 
        data={"path": path, "recursive": recursive}
    )


async def create_directory(path: str) -> Dict[str, Any]:
    """
    Create a directory in the workspace.
    
    Args:
        path: The path to create
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Creating directory: {path}")
    return make_api_request("POST", "/api/2.0/workspace/mkdirs", data={"path": path})


def is_base64(content: str) -> bool:
    """
    Check if a string is already base64 encoded.
    
    Args:
        content: The string to check
        
    Returns:
        True if the string is base64 encoded, False otherwise
    """
    try:
        return base64.b64encode(base64.b64decode(content)) == content.encode('utf-8')
    except Exception:
        return False 