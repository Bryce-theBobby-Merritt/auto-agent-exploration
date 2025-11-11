#!/usr/bin/env python3
"""Test script to validate path handling in tools."""

import asyncio
from tools import ToolUpsertFile, ToolRunCommandInDevContainer

async def test_command_validation():
    """Test that commands with Windows paths are rejected."""
    print("Testing command validation...")
    tool = ToolRunCommandInDevContainer(command='python C:\\Windows\\python.exe')
    result = await tool()
    print(f"Command validation result: {result}")
    assert "Windows-style executable path" in result

async def test_file_path_validation():
    """Test that file paths with backslashes are rejected."""
    print("Testing file path validation...")
    tool = ToolUpsertFile(file_path='C:\\Windows\\test.py', content='print("hello")')
    result = await tool()
    print(f"File path validation result: {result}")
    assert "backslashes" in result

async def main():
    await test_command_validation()
    await test_file_path_validation()
    print("All validation tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
