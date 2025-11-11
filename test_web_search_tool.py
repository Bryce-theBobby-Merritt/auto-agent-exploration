import requests

# Update the base URL to the IP of the Docker container
base_url = 'http://172.17.0.2:5000'  # Adjust this IP according to the container's network details

# Test /open_url endpoint
url_response = requests.post(f'{base_url}/open_url', json={'url': 'http://example.com'})
print('Response from /open_url:', url_response.json())

# Test /search endpoint
search_response = requests.get(f'{base_url}/search', params={'query': 'Flask'})
print('Response from /search:', search_response.json())