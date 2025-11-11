#!/usr/bin/env python3
"""
Quick test to verify the spawn subagent tool is properly integrated.
"""

import asyncio
from simple_ui import SimpleUI

async def test_agent_initialization():
    """Test that the agent initializes with the spawn subagent tool."""
    ui = SimpleUI()
    ui.initialize_agent()

    # Check if ToolSpawnSubagent is in the tools
    tool_names = [tool.__name__ for tool in ui.agent.tools]
    print("Available tools:", tool_names)

    if "ToolSpawnSubagent" in tool_names:
        print("SUCCESS: ToolSpawnSubagent successfully added to tools list")
    else:
        print("ERROR: ToolSpawnSubagent not found in tools list")

    # Test creating a ToolSpawnSubagent instance
    from tools import ToolSpawnSubagent
    test_tool = ToolSpawnSubagent(task="Test task for verification")
    print(f"SUCCESS: ToolSpawnSubagent instance created with task: '{test_tool.task}'")

if __name__ == "__main__":
    asyncio.run(test_agent_initialization())
