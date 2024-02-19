from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
from tika import parser
import os
#import openai
from openai import OpenAI
openai = OpenAI()

app = Flask(__name__)

# Initialize OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize Elasticsearch client
#es = Elasticsearch()

# Replace 'localhost' and '9200' with the appropriate values for your Elasticsearch server
es = Elasticsearch("http://localhost:9200")


# Directory to store uploaded documents
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Indexing function for documents
def index_document(file_path):
    with open(file_path, 'r', encoding="utf-8", errors="ignore") as file:
        content = file.read()

    # es.index(index='documents', doc_type='_doc', body={'content': content, 'file_path': file_path})

# Endpoint to upload documents
@app.route('/upload', methods=['POST'])
def upload_document():
    print("FILES", request.files)
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Index the document
    index_document(file_path)

    return jsonify({'message': 'Document uploaded successfully'})

# Endpoint to search documents using OpenAI's GPT-3
@app.route('/search', methods=['POST'])
def search_documents():
    print("QUERY", request)
    #query = request.json['testing']
    query = "testing"

    # Use OpenAI to generate a response based on the query
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Search for documents related to: {query}",
        temperature=0.7,
        max_tokens=150
    )
    print("response ", response)
    print("response ", response.choices[0].text)
    search_query = response.choices[0].text
    print("search query",search_query)
    # Search Elasticsearch index
    search_results = es.search(index='documents', body={'query': {'match': {'content': search_query}}})
    print("search results", search_results)
    hits = search_results.get('hits', {}).get('hits', [])

    results = [{'file_path': hit['_source']['file_path']} for hit in hits]

    return jsonify({'response': search_query, 'search_results': results})

if __name__ == '__main__':
    app.run(debug=True)
