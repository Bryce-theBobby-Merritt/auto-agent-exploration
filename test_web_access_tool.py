import unittest
from web_access_tool import WebAccessTool
import requests
from unittest.mock import patch

class TestWebAccessTool(unittest.TestCase):
    def setUp(self):
        self.tool = WebAccessTool(base_url="http://localhost:8000")

    @patch('requests.get')
    def test_search(self, mock_get):
        # Mock the response from the /search endpoint
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{'title': 'Example Result 1', 'url': 'https://example.com/1'}]

        result = self.tool.search("example")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Example Result 1')

    @patch('requests.get')
    def test_open_url(self, mock_get):
        # Mock the response from the /open_url endpoint
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'content': 'Some sanitized content'}

        result = self.tool.open_url("http://example.com")
        self.assertEqual(result['content'], 'Some sanitized content')

if __name__ == '__main__':
    unittest.main()