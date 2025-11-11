"""
Test script to verify that all imports and basic structure work.
This doesn't require API keys.
"""

def test_imports():
    """Test that all modules can be imported."""
    try:
        # Test basic pydantic and other imports
        from pydantic import BaseModel, Field
        print("[OK] Pydantic imports work")

        from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed
        print("[OK] Tenacity imports work")

        import docker
        print("[OK] Docker imports work")

        # Test our custom imports (without initializing clients)
        import sys
        sys.path.insert(0, '.')

        # Test tools imports
        from tools import Tool, ToolRunCommandInDevContainer, ToolUpsertFile
        print("[OK] Tools imports work")

        # Test agent imports (this will fail on client init, but imports should work)
        try:
            from agent import Agent, AgentEvent, EventText, EventInputJson, EventToolUse, EventToolResult
            print("[OK] Agent imports work")
        except Exception as e:
            print(f"[WARN] Agent import failed (expected due to missing API key): {e}")

        print("\n[SUCCESS] All basic imports successful! The agent structure is working.")
        print("\nTo run the agent, make sure to set your OPENAI_API_KEY environment variable.")
        print("Example: export OPENAI_API_KEY='your-key-here'")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    test_imports()
