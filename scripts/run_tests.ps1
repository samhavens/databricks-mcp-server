#!/usr/bin/env pwsh
# Run tests for the Databricks MCP server

param(
    [string]$TestPath = "tests/",
    [switch]$Coverage,
    [switch]$Verbose
)

# Check if the virtual environment exists
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please create it first:"
    Write-Host "uv venv"
    exit 1
}

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Base command
$cmd = "uv run pytest"

# Add verbose flag if specified
if ($Verbose) {
    $cmd += " -v"
}

# Add coverage if specified
if ($Coverage) {
    $cmd += " --cov=src --cov-report=term-missing"
}

# Add test path
$cmd += " $TestPath"

Write-Host "Running: $cmd"
Invoke-Expression $cmd

# Print summary
Write-Host "`nTest run completed at $(Get-Date)" 