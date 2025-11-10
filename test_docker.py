"""
Test script to verify Docker integration is working properly.
"""

from clients import docker_client
from tools import start_python_dev_container, check_container_status, ToolRunCommandInDevContainer, ToolUpsertFile
import asyncio


def test_docker_setup():
    """Test basic Docker setup and container operations."""
    print("[TEST] Testing Docker Integration")
    print("=" * 50)

    # Test 1: Docker client availability
    if docker_client is None:
        print("[FAIL] Docker client not available. Please ensure Docker is running.")
        return False

    print("[OK] Docker client available")

    # Test 2: Check if python:3.12 image exists
    try:
        images = docker_client.images.list(name="python:3.12")
        if not images:
            print("[WARN] Python 3.12 image not found locally. It will be downloaded when starting container.")
        else:
            print("[OK] Python 3.12 image available")
    except Exception as e:
        print(f"[WARN] Could not check for Python image: {e}")

    # Test 3: Start container
    print("\n[START] Starting Python development container...")
    success = start_python_dev_container("python-dev")

    if not success:
        print("[FAIL] Failed to start container. Check Docker status and try again.")
        return False

    # Test 4: Check container status
    status = check_container_status("python-dev")
    print(f"[STATUS] Container status: {status}")

    if "running" not in status:
        print("[FAIL] Container is not running properly.")
        return False

    print("[OK] Container started successfully")

    # Test 5: Test tool operations (async)
    print("\n[TOOL_TEST] Testing tool operations...")

    async def test_tools():
        # Test command execution
        cmd_tool = ToolRunCommandInDevContainer(command="echo 'Hello from Docker!' && pwd")
        result = await cmd_tool()
        print(f"Command result: '{result.strip()}'")

        if "Hello from Docker!" in result and "/app" in result:
            print("[OK] Command execution working")
        else:
            print(f"[FAIL] Command execution failed: '{result}'")

        # Test file creation
        file_tool = ToolUpsertFile(file_path="/app/test.txt", content="This is a test file\nWith multiple lines")
        result = await file_tool()
        print(f"File creation result: '{result}'")

        if "successfully" in result:
            print("[OK] File creation working")
        else:
            print(f"[FAIL] File creation failed: '{result}'")

        # List directory to see what files exist
        list_tool = ToolRunCommandInDevContainer(command="ls -la /app/")
        list_result = await list_tool()
        print(f"Directory contents: '{list_result}'")

        # Verify file was created and read
        verify_tool = ToolRunCommandInDevContainer(command="cat /app/test.txt 2>/dev/null || echo 'File does not exist'")
        result = await verify_tool()
        if "This is a test file" in result and "With multiple lines" in result:
            print("[OK] File verification successful")
        else:
            print(f"[FAIL] File verification failed: '{result}'")

    asyncio.run(test_tools())

    print("\n[SUCCESS] Docker integration test completed!")
    return True


if __name__ == "__main__":
    test_docker_setup()
