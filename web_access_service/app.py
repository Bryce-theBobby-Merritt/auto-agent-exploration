from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    # This is a placeholder response; actual implementation would involve calling a search API
    results = [
        {'title': 'Example Result 1', 'url': 'https://example.com/1'},
        {'title': 'Example Result 2', 'url': 'https://example.com/2'}
    ]
    return jsonify(results)

@app.route('/open_url', methods=['GET'])
def open_url():
    url = request.args.get('url')
    try:
        response = requests.get(url)
        content = response.text  # Sanitize content before returning
        return jsonify({'content': content})
    except requests.RequestException:
        return jsonify({'error': 'Failed to fetch URL.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)