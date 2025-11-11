import requests

class GitHubTools:
    def __init__(self, token, repo):
        self.headers = {'Authorization': f'token {token}'}
        self.repo = repo

    def create_pr(self, title, body, base='main', head='feature-branch'):
        url = f'https://api.github.com/repos/{self.repo}/pulls'
        data = {'title': title, 'body': body, 'base': base, 'head': head}
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def list_issues(self):
        url = f'https://api.github.com/repos/{self.repo}/issues'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def update_issue(self, issue_number, title=None, body=None):
        url = f'https://api.github.com/repos/{self.repo}/issues/{issue_number}'
        data = {}
        if title:
            data['title'] = title
        if body:
            data['body'] = body
        response = requests.patch(url, headers=self.headers, json=data)
        return response.json()

    def delete_issue(self, issue_number):
        url = f'https://api.github.com/repos/{self.repo}/issues/{issue_number}'
        response = requests.delete(url, headers=self.headers)
        return response.status_code
