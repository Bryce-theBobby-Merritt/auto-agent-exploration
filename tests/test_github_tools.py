import pytest
from tools import create_pr, list_issues, create_issue, update_issue

class TestGitHubTools:

    @pytest.mark.parametrize('repo, title, body, head, base', [
        ('user/repo', 'Test PR', 'This is a test PR', 'feature-branch', 'main')
    ])
    def test_create_pr(self, repo, title, body, head, base):
        response = create_pr(repo, title, body, head, base)
        assert isinstance(response, dict)  # Assuming the response is a dict

    def test_list_issues(self):
        repo = 'user/repo'
        response = list_issues(repo)
        assert isinstance(response, list)  # Assuming the response is a list

    def test_create_issue(self):
        repo = 'user/repo'
        title = 'Test Issue'
        body = 'This is a test issue'
        response = create_issue(repo, title, body)
        assert 'id' in response  # Assuming response contains an ID

    @pytest.mark.parametrize('repo, issue_number', [
        ('user/repo', 1)
    ])
    def test_update_issue(self, repo, issue_number):
        response = update_issue(repo, issue_number, title='Updated Title')
        assert response['title'] == 'Updated Title'  # Check if title updated successfully
