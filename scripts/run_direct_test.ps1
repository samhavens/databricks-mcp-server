#!/usr/bin/env pwsh
# PowerShell script to run the direct test

# Check if the virtual environment exists
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please create it first:"
    Write-Host "uv venv"
    exit 1
}

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Check if environment variables are set
if (-not (Get-Item -Path Env:DATABRICKS_HOST -ErrorAction SilentlyContinue) -or 
    -not (Get-Item -Path Env:DATABRICKS_TOKEN -ErrorAction SilentlyContinue)) {
    Write-Host "Warning: DATABRICKS_HOST and/or DATABRICKS_TOKEN environment variables are not set."
    Write-Host "Please set them before running the test."
    exit 1
}

# Run the direct test
Write-Host "Running direct test at $(Get-Date)"
Write-Host "Databricks Host: $env:DATABRICKS_HOST"

uv run -m tests.direct_test

Write-Host "Test completed at $(Get-Date)" 