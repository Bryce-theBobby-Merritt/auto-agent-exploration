from flask import Flask, jsonify, request
from flask_limiter import Limiter
import requests

app = Flask(__name__)  
limiter = Limiter(app)

@app.route('/search', methods=['GET'])
@limiter.limit('5 per minute')  # limit to 5 requests per minute
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required.'}), 400
    # Use DuckDuckGo instant answer API (free and doesn't require API key)
    try:
        response = requests.get(f'https://api.duckduckgo.com/?q={query}&format=json&no_html=1')
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/open_url', methods=['GET'])
@limiter.limit('5 per minute')  # limit to 5 requests per minute
def open_url():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required.'}), 400
    # Replace with a call to an actual API or service
    data = requests.get(url).text
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)