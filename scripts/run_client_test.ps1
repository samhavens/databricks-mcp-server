#!/usr/bin/env pwsh
# PowerShell script to run the MCP client test

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

# Set timeout in seconds
$timeout = 60

# Run the test with a timeout
Write-Host "Running MCP client test with a $timeout second timeout..."
$job = Start-Job -ScriptBlock { 
    cd $using:PWD
    uv run mcp_client_test.py 
}

# Monitor the job and output in real-time
$start = Get-Date
while ($job.State -eq "Running") {
    # Get any new output
    $output = Receive-Job -Job $job
    if ($output) {
        Write-Host $output
    }
    
    # Check if we've hit the timeout
    $elapsed = (Get-Date) - $start
    if ($elapsed.TotalSeconds -gt $timeout) {
        Write-Host "Test is taking too long, terminating..."
        Stop-Job -Job $job
        break
    }
    
    # Sleep briefly
    Start-Sleep -Seconds 1
}

# Output final results
$output = Receive-Job -Job $job
if ($output) {
    Write-Host $output
}

Remove-Job -Job $job -Force

# Clean up any leftover processes
$serverProcesses = Get-Process -Name pwsh | Where-Object { $_.CommandLine -like "*start_mcp_server.ps1*" }
if ($serverProcesses) {
    Write-Host "Cleaning up any remaining MCP server processes..."
    $serverProcesses | ForEach-Object { 
        Stop-Process -Id $_.Id -Force 
        Write-Host "Stopped process $($_.Id)"
    }
} 