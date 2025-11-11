#!/usr/bin/env python3
"""Test script for the new ToolCurlCommand"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import ToolCurlCommand

async def test_curl():
    print("Testing ToolCurlCommand...")

    # Test 1: Search endpoint
    print("\n=== Test 1: Search endpoint ===")
    tool1 = ToolCurlCommand(command='-X GET "http://localhost:8889/search?query=test%20curl%20tool"')
    result1 = await tool1()
    print(result1)

    # Test 2: URL fetch endpoint
    print("\n=== Test 2: URL fetch endpoint ===")
    tool2 = ToolCurlCommand(command='-X GET "http://localhost:8889/open_url?url=https://httpbin.org/json"')
    result2 = await tool2()
    print(result2)

    # Test 3: Invalid endpoint (should show error)
    print("\n=== Test 3: Invalid endpoint ===")
    tool3 = ToolCurlCommand(command='-X GET "http://localhost:8889/nonexistent"')
    result3 = await tool3()
    print(result3)

    print("\n=== Curl tool tests completed ===")

if __name__ == "__main__":
    asyncio.run(test_curl())
