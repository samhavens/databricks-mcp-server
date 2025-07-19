"""
Test script to validate and inspect Databricks MCP server tool schemas.
This demonstrates how type annotations are converted to JSON schemas for Gemini API.
"""

import asyncio
import sys
import os
import json
from pprint import pprint

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# from src.server.databricks_mcp_server import DatabricksMCPServer
# Server class not available, just run basic validation of imports
from src.server.simple_databricks_mcp_server import mcp


async def inspect_tool_schemas():
    """Basic validation that imports work."""
    print("🔍 Validating Databricks MCP Server imports\n")
    
    # Just check that the MCP instance exists
    print(f"📊 MCP server instance: {mcp}")
    print(f"📊 Available tools: {len(mcp._tools)} registered\n")
    
    for i, (tool_name, tool_func) in enumerate(mcp._tools.items(), 1):
        print(f"🛠️  Tool {i}: {tool_name}")
        print(f"    Function: {tool_func.__name__}")
        print()
        print(f"    Description: {tool.description}")
        
        # Show the input schema (this is what Gemini sees)
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            print(f"    Input Schema (for Gemini API):")
            pprint(tool.inputSchema, indent=8, width=80)
            
            # Detailed parameter breakdown
            if 'properties' in tool.inputSchema:
                properties = tool.inputSchema['properties']
                required = tool.inputSchema.get('required', [])
                print(f"    Parameters ({len(properties)}):")
                for param_name, param_def in properties.items():
                    is_required = param_name in required
                    param_type = param_def.get('type', 'unknown')
                    description = param_def.get('description', 'No description')
                    status = "required" if is_required else "optional"
                    print(f"      - {param_name} ({param_type}, {status}): {description}")
            else:
                print(f"    Parameters: None")
        else:
            print(f"    Input Schema: None (this would cause Gemini validation errors)")
            
        print("\n" + "="*60 + "\n")


async def validate_gemini_compatibility():
    """Check if all tools have proper schemas for Gemini compatibility."""
    print("🚀 Validating Gemini API Compatibility\n")
    
    server = DatabricksMCPServer()
    tools = await server.list_tools()
    
    validation_results = []
    
    for tool in tools:
        result = {
            'name': tool.name,
            'has_schema': bool(hasattr(tool, 'inputSchema') and tool.inputSchema),
            'has_properties': False,
            'required_defined': False,
            'gemini_compatible': False
        }
        
        if result['has_schema']:
            schema = tool.inputSchema
            result['has_properties'] = 'properties' in schema
            result['required_defined'] = 'required' in schema
            
            # Check if all required parameters are defined in properties
            if result['has_properties'] and result['required_defined']:
                properties = schema.get('properties', {})
                required = schema.get('required', [])
                all_required_defined = all(req in properties for req in required)
                result['gemini_compatible'] = all_required_defined
            elif result['has_properties'] and not result['required_defined']:
                # No required params is also valid
                result['gemini_compatible'] = True
        
        validation_results.append(result)
    
    # Print validation summary
    compatible_count = sum(1 for r in validation_results if r['gemini_compatible'])
    print(f"✅ Gemini Compatible Tools: {compatible_count}/{len(validation_results)}")
    print(f"❌ Incompatible Tools: {len(validation_results) - compatible_count}/{len(validation_results)}\n")
    
    # Show detailed results
    for result in validation_results:
        status = "✅" if result['gemini_compatible'] else "❌"
        print(f"{status} {result['name']}")
        if not result['gemini_compatible']:
            print(f"    Issues: Schema={result['has_schema']}, Properties={result['has_properties']}, Required={result['required_defined']}")
    
    return compatible_count == len(validation_results)


async def main():
    """Main test function."""
    print("=" * 80)
    print("DATABRICKS MCP SERVER SCHEMA VALIDATION")
    print("=" * 80 + "\n")
    
    # Inspect all tool schemas
    await inspect_tool_schemas()
    
    # Validate Gemini compatibility
    all_compatible = await validate_gemini_compatibility()
    
    print("\n" + "=" * 80)
    if all_compatible:
        print("🎉 SUCCESS: All tools are Gemini API compatible!")
        print("No more 'property is not defined' errors should occur.")
    else:
        print("⚠️  WARNING: Some tools may cause Gemini validation errors.")
    print("=" * 80)
    
    return all_compatible


if __name__ == "__main__":
    # Run the validation
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
