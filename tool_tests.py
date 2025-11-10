
import asyncio
import pytest
from tools import ToolEditFile

@pytest.mark.asyncio
async def test_tool_edit_file(tmpdir):
    test_file_path = tmpdir.join('test_file.txt')
    edit_tool = ToolEditFile(file_path=str(test_file_path), content="Hello World!\n")
    result = await edit_tool()
    assert "File edited successfully" in result
    
    # Check if content was appended
    with open(test_file_path, 'r') as f:
        content = f.read()
        assert "Hello World!" in content
