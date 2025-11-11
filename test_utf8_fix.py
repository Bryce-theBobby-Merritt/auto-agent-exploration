#!/usr/bin/env python3
"""Test script to verify UTF-8 handling in ToolSearchAndReplace"""

import asyncio
from tools import ToolSearchAndReplace

async def test_utf8_search_replace():
    """Test that ToolSearchAndReplace can handle UTF-8 files"""

    # Create a tool instance
    tool = ToolSearchAndReplace(
        pattern="coffee",
        replacement="coffee",
        directory="."
    )

    # Run the tool
    result = await tool()

    print("Tool result:", result)

    # Check if the file was modified correctly
    try:
        with open('test_utf8.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        print("File content after replacement:", repr(content))
        print("Human readable:", content)
    except UnicodeDecodeError as e:
        print("UTF-8 decode error:", e)
        # Try to read as binary to see what's there
        with open('test_utf8.txt', 'rb') as f:
            binary_content = f.read()
        print("Binary content:", binary_content[:100])

if __name__ == "__main__":
    asyncio.run(test_utf8_search_replace())
