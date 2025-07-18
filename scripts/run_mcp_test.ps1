#!/usr/bin/env pwsh
# Start MCP server and run tests

# Check if the virtual environment exists
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please create it first:"
    Write-Host "uv venv"
    exit 1
}

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Make sure there are no existing MCP server processes
$serverProcesses = Get-Process -Name pwsh | Where-Object { $_.CommandLine -like "*start_mcp_server.ps1*" }
if ($serverProcesses) {
    Write-Host "Found existing MCP server processes, stopping them first..."
    $serverProcesses | ForEach-Object { 
        Stop-Process -Id $_.Id -Force 
        Write-Host "Stopped process $($_.Id)"
    }
}

# Start the MCP server in a new PowerShell window
$serverProcess = Start-Process pwsh -ArgumentList "-File", "scripts\start_mcp_server.ps1" -PassThru -WindowStyle Minimized

# Give it time to initialize
Write-Host "Waiting for MCP server to initialize..."
Start-Sleep -Seconds 5

try {
    # Run the test
    Write-Host "Running test against the MCP server..."
    uv run test_running_server.py
}
finally {
    # Clean up: stop the server
    if ($serverProcess -and !$serverProcess.HasExited) {
        Write-Host "Stopping MCP server..."
        Stop-Process -Id $serverProcess.Id -Force
    }
    
    # Make sure all MCP server processes are stopped
    $serverProcesses = Get-Process -Name pwsh | Where-Object { $_.CommandLine -like "*start_mcp_server.ps1*" }
    if ($serverProcesses) {
        $serverProcesses | ForEach-Object { 
            Stop-Process -Id $_.Id -Force 
            Write-Host "Stopped process $($_.Id)"
        }
    }
} 