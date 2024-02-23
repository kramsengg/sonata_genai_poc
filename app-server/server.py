from flask import Flask, render_template, request, jsonify
#from elasticsearch import Elasticsearch
from tika import parser
import os
#import openai
import json
from openai import OpenAI
from flask_cors import CORS
import time
openai = OpenAI()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai

# Directory to store uploaded documents
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DOCU_ASSISTANT_ID = os.environ.get("ASSISTANT_ID")

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Indexing function for documents
def index_document(file_path):
    with open(file_path, 'r', encoding="utf-8", errors="ignore") as file:
        content = file.read()

    es.index(index='documents', body={'content': content, 'file_path': file_path})
    
# Endpoint to upload documents
@app.route('/uploadold', methods=['POST'])
def upload_document():
    print("FILES", request.files)

    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Index the document
    index_document(file_path)

    return jsonify({'message': 'Document uploaded successfully'})

# Endpoint to search documents using OpenAI's GPT-3
@app.route('/searchold', methods=['POST'])
def search_documents():
    print("QUERY", request)
    #query = request.json['testing']
    query = "testing"
    if request.method == 'POST':
        query = request.get_json()
        print("QUERY", query)

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

@app.route('/testold/<int:num>', methods=['GET'])
def test_results(num):
    print("test results",num)
    response = jsonify({'data': num**2})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def display(*objs, **kwargs):
  """
  Prints objects to the console.

  Args:
    *objs: Objects to be printed.
    **kwargs: Additional keyword arguments for formatting (e.g., rich library).
  """

  print(*objs, **kwargs)

def show_json(obj):
    display(json.loads(obj.model_dump_json()))

@app.route('/upload', methods=['POST'])
def upload_file():
    print("FILES", request.files)
    file_upload = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_upload.filename)
    file_upload.save(file_path)
    print("FILE PATH", file_path)
    # Upload the file
    file = openai.files.create(
        file=open(
            file_path, # "data/language_models_are_unsupervised_multitask_learners.pdf",
            "rb",
        ),
        purpose="assistants",
    )
    # Update Assistant
    assistant = openai.beta.assistants.update(
        DOCU_ASSISTANT_ID,
        tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
        file_ids=[file.id],
    )
    show_json(assistant)
    return jsonify({'message': 'assistant'})

@app.route('/search', methods=['POST'])
def search_indocuments():
    print("QUERY", request)
    #query = request.json['testing']
    query = "testing"
    if request.method == 'POST':
        query = request.get_json()
        print("QUERY", query)

    thread_id = os.environ.get("ASSIST_THREAD_ID")
    thread = None
    if thread_id is None:
        thread = client.beta.threads.create()
        show_json(thread)
        thread_id = thread.id
        # Create a new environment variable
        create_environment_variable("ASSIST_THREAD_ID", thread_id)
    else:
        print("THREAD ID", thread_id)

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
    )
    show_json(message)

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=DOCU_ASSISTANT_ID,
    )
    show_json(run)

    # Delete the environment variable
    #delete_environment_variable("ASSIST_THREAD_ID")
    return jsonify({'response': thread_id, 'search_results': thread_id})

@app.route('/searchnew', methods=['GET','POST'])
def search():
    data = {}
    # Your search logic here
    if request.method == 'GET':
        #query = request.form['query']
        data = {'results': ['apple', 'banana', 'cherry']}
    else:
      query = request.json['query']
      # data = {'results': [query]}

    thread_id = os.environ.get("ASSIST_THREAD_ID")
    thread = None
    if thread_id is None:
        thread = client.beta.threads.create()
        show_json(thread)
        thread_id = thread.id
        # Create a new environment variable
        create_environment_variable("ASSIST_THREAD_ID", thread_id)
    else:
        print("THREAD ID", thread_id)

    print("THREAD ID", thread_id)
    # message = client.beta.threads.messages.create(
    #     thread_id=thread.id,
    #     role="user",
    #     content=query,
    # )
    # show_json(message)

    # run = client.beta.threads.runs.create(
    #     thread_id=thread.id,
    #     assistant_id=DOCU_ASSISTANT_ID,
    # )
    # show_json(run)

    # # Emulating concurrent user requests
    thread1, run1 = create_thread_and_run(
        query
    )

    # Wait for Run 1
    run1 = wait_on_run(run1, thread1)
    pretty_print(get_response(thread1))
    
    

    data1 = get_response(thread1)
    print("data1 RESPONSE ", data1)
    # Convert the object to a JSON-serializable format
    serializable_data = {
        'data': [
            {
                'id': message.id,
                'assistant_id': message.assistant_id,
                'content': [
                    {
                        'text': content.text.value,
                        'type': content.type
                    } for content in message.content
                ],
                'created_at': message.created_at,
                'file_ids': message.file_ids,
                'metadata': message.metadata,
                'object': message.object,
                'role': message.role,
                'run_id': message.run_id,
                'thread_id': message.thread_id
            } for message in data1.data
        ],
        'object': data1.object,
        'first_id': data1.first_id,
        'last_id': data1.last_id,
        'has_more': data1.has_more
    }


    # Serialize the data to JSON
    json_data = json.dumps(serializable_data, indent=2)
    #json_data = json.loads(data1)
    data = {'response': thread_id, 'search_results': data1}
    #return jsonify({'response': thread_id, 'search_results': thread_id})
    return jsonify(json_data)

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(DOCU_ASSISTANT_ID, thread, user_input)
    return thread, run

# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def create_environment_variable(variable_name, variable_value):
    """
    Create a new environment variable.

    Args:
    - variable_name (str): Name of the environment variable.
    - variable_value (str): Value to assign to the environment variable.
    """
    os.environ[variable_name] = variable_value
    print(f"Created environment variable: {variable_name}={variable_value}")

def delete_environment_variable(variable_name):
    """
    Delete an existing environment variable.

    Args:
    - variable_name (str): Name of the environment variable to delete.
    """
    if variable_name in os.environ:
        del os.environ[variable_name]
        print(f"Deleted environment variable: {variable_name}")
    else:
        print(f"Environment variable {variable_name} does not exist.")

if __name__ == '__main__':
    app.run(debug=True)