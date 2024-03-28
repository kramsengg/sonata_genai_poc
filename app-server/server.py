from flask import Flask, render_template, request, jsonify
#from elasticsearch import Elasticsearch
from tika import parser
import os
import requests
#import openai
import json
from openai import OpenAI
from flask_cors import CORS
import time
import custom_utils
import pandas as pd
import ast

from pdfminer.high_level import extract_text
from docx import Document
import textract

openai = OpenAI()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai

data = {
    'embedding': ['text', 'embedding']  # Replace with your actual data
}
#df = pd.DataFrame(data)

# Directory to store uploaded documents
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DOCU_ASSISTANT_ID = os.environ.get("ASSISTANT_ID")

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    embeddings_path = os.path.join("uploads", "uploaded_docs_embeddings.csv")   
    df['embedding'] = df['embedding'].apply(lambda x: custom_utils.get_embedding(x, model='text-embedding-3-small'))
    df.to_csv(embeddings_path, index=False)

    # Upload the file
    file = openai.files.create(
        file=open(
            file_path,
            "rb",
        ),
        purpose="assistants",
    )
    #List of assistant files
    try:
        headers = {
            'Authorization': 'Bearer '+os.environ.get("OPENAI_API_KEY"),
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v1'
        }
        fileids_response = requests.get('https://api.openai.com/v1/assistants/'+DOCU_ASSISTANT_ID+'/files',
                                        headers=headers)
        print("FILE RESPONSE ", fileids_response)
    except requests.RequestException as e:
        print(f'Error making API call: {str(e)}')

    fileids =[]
    if fileids_response.status_code == 200:
        fileids_attached = fileids_response.json()
        fileids = [fileid.get("id") for fileid in fileids_attached.get("data")]

    # append with existing files    
    fileids.append(file.id)
    # Update Assistant
    assistant = openai.beta.assistants.update(
        DOCU_ASSISTANT_ID,
        tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
        file_ids=fileids,
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
        custom_utils.create_environment_variable("ASSIST_THREAD_ID", thread_id)
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
        data = {'results': ['apple', 'banana', 'cherry']}
    else:
      query = request.json['query']

    thread_id = os.environ.get("ASSIST_THREAD_ID")
    thread = None
    if thread_id is None:
        thread = client.beta.threads.create()
        show_json(thread)
        thread_id = thread.id
        # Create a new environment variable
        custom_utils.create_environment_variable("ASSIST_THREAD_ID", thread_id)
    else:
        print("THREAD ID", thread_id)

    print("THREAD ID", thread_id)
    
    # # Emulating concurrent user requests
    thread1, run1 = custom_utils.create_thread_and_run(client,DOCU_ASSISTANT_ID,
        query
    )

    # Wait for Run 1
    run1 = custom_utils.wait_on_run(client,run1, thread1)
    custom_utils.pretty_print(custom_utils.get_response(client,thread1))

    data1 = custom_utils.get_response(client,thread1)
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
    return jsonify(json_data)

@app.route('/uploadfile', methods=['POST'])
def upload_file_to_process():
    print("FILES", request.files)
    file_upload = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_upload.filename)
    file_upload.save(file_path)
    print("FILE PATH", file_path)
    print (" TEXT PROCESSING and EMBEDDING Started")
    embeddings_path = os.path.join("uploads", file_upload.filename+"_embeddings.csv")   
    custom_utils.process_and_save_embeddings(file_path,embeddings_path)
    
    # df['embedding'] = df['embedding'].apply(lambda x: custom_utils.get_embedding(x, model='text-embedding-3-small'))
    # df.to_csv(embeddings_path, index=False)
    print (" TEXT PROCESSING and EMBEDDING Ended")
    return jsonify({'message': 'assistant'})

@app.route('/searchtext', methods=['GET','POST'])
def searchwithembeddings():
    #embeddings_path = os.path.join("uploads", "uploaded_docs_embeddings.csv")  
    #embeddings_path = os.path.join("uploads", "Copy_Generative AI Tutorial.docx_embeddings.csv")
    #embeddings_path = os.path.join("uploads", "winter_olympics_2022.csv") 
    # Replace 'uploads' with the path to your uploads folder
    csv_dataframes = custom_utils.read_csv_files('uploads')
    print("ALL DF ", csv_dataframes)
    
    df = csv_dataframes
    #df = pd.read_csv(embeddings_path)
    #df['embeddings'] = df['embeddings'].apply(ast.literal_eval)

    results_data = {}
    # Your search logic here
    if request.method == 'GET':
        data = {'results': ['apple', 'banana', 'cherry']}
    else:
      query = request.json['query']

    results = custom_utils.ask(query,df)

    results_data = { 'response': results }
    return jsonify(results_data)


if __name__ == '__main__':
    app.run(debug=True)