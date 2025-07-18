#!/bin/bash
# Wrapper script to run the MCP server start script from scripts directory

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the actual server script
"$SCRIPT_DIR/scripts/start_mcp_server.sh" 