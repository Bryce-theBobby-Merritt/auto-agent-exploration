import unittest
from tools import ToolRunCommandInDevContainer, ToolUpsertFile, ToolSearchAndReplace


class TestToolRunCommandInDevContainer(unittest.TestCase):
    def test_run_command(self):
        tool = ToolRunCommandInDevContainer(command="echo 'Hello World'")
        result = tool._run()
        self.assertIn('Hello World', result)


class TestToolUpsertFile(unittest.TestCase):
    def test_upsert_file(self):
        tool = ToolUpsertFile(file_path='test_file.txt', content='Test content')
        result = tool._run()
        self.assertEqual(result, 'File created/updated successfully.')  # Adjust based on return value


class TestToolSearchAndReplace(unittest.TestCase):
    def test_search_and_replace(self):
        tool = ToolSearchAndReplace(pattern='foo', replacement='bar', directory='.')
        result = tool._run()
        self.assertEqual(result, "Search and replace completed successfully.")  # Adjust based on return value


if __name__ == '__main__':
    unittest.main()  
