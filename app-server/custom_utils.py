import os
import time

import ast
from openai import OpenAI
import pandas as pd
import os
from scipy import spatial
import tiktoken
import json
from flask import jsonify
from tenacity import retry, wait_random_exponential, stop_after_attempt, RetryError
from pdfminer.high_level import extract_text
from docx import Document
import textract

EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"

client = OpenAI()
client.api_key = os.environ.get("OPENAI_API_KEY")
# Existing DataFrame
df = pd.DataFrame(columns=["text", "embedding"])
#embeddings_path = os.path.join("uploads", "winter_olympics_2022.csv")
# embeddings_path = os.path.join("uploads", "uploaded_docs_embeddings.csv")   
#df = pd.read_csv(embeddings_path)
# if os.path.exists(embeddings_path):
#     df = pd.read_csv(embeddings_path)
# else:
#     data = {
#         'embedding': ['text', 'embedding']  # Replace with your actual data
#     }
#     df = pd.DataFrame(data)

#df['embedding'] = df['embedding'].apply(ast.literal_eval)


def submit_message(client,assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(client,thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(client,DOCU_ASSISTANT_ID,user_input):
    thread = client.beta.threads.create()
    run = submit_message(client,DOCU_ASSISTANT_ID, thread, user_input)
    return thread, run

# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

# Waiting in a loop
def wait_on_run(client,run, thread):
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

# search function
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int
) -> str:
    # Fill NaN values in 'Age' column with 0
    #df['embedding'] = df['embedding'].fillna(0)
    #df["embedding"] = df["embedding"].apply(convert_to_list)
    print ("BEFORE ", df)
    print("HEAD ", df['embedding'].head())
    print("SAMPLE ", df["embedding"].sample())
    df.dropna(subset=['embedding'])
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    #df['embedding'] = df['embedding'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    print("AFTER ", df)
    print("HEAD ", df['embedding'].head())
    print("SAMPLE ", df["embedding"].sample())
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'Use the below articles on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nWikipedia article section:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    return message + question

def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    print ("QUERY ", query)
    print ("INside ask ", df)
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You answer questions about the 2022 Winter Olympics."},
        {"role": "user", "content": message},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    print(response)

    print(response.choices[0].message)
    print(response.choices[0].message.content)
    print(response.choices[0].message.role)
    # Convert the object to a JSON-serializable format
    # serializable_data = {
    #         'data': [
    #             {
    #                 'message': [
    #                     {
    #                         'content': mes.content,
    #                         'role': mes.role
    #                     }
    #                 ] 
    #             } for mes in response.choices[0].message
    #         ]
    # }
        
    ser_data = {
        "data": [
            {
                "content":  response.choices[0].message.content,
                "role": response.choices[0].message.role
            } 
        ]
    }

    print ("SER DATA ", ser_data)

    # Serialize the data to JSON
    #response_message = json.dumps(ser_data, indent=2)
    response_message = ser_data
    # Serialize the data to JSON
    #return response_message
    print ( " RESPONSE MESSA ", response_message)
    return response_message

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text, model="text-embedding-3-small"):
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y)
    text = text.replace("\n", " ")
    print ("TEXT ", text)
    embed = client.embeddings.create(input = [text], model=model).data[0].embedding
    #print("EMBEDDING ", embed)

    # query_embedding = embed
    # strings_and_relatednesses = [
    #     (row["text"], relatedness_fn(query_embedding, row["embedding"]))
    #     for i, row in df.iterrows()
    # ]
    # strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    # print("STRING READINESSS:  ", strings_and_relatednesses)
    return embed

# Function to extract text from PDF document
def extract_text_from_pdf(file_path):

    text = textract.process(file_path,method="pdfminer").decode("utf-8")
    #text = textract.process("../uploads/uber_2021.pdf",method="pdfminer").decode("utf-8")

    clean_text = text.replace("  ", " ").replace("\n","; ").replace(';',' ')
    return clean_text
    # with open(file_path, 'rb') as f:
    #     text = extract_text(f)
    # return text

# Function to extract text from Word document
def extract_text_from_word(file_path):
    doc = Document(file_path)
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Function to extract text from any file
def extract_text_from_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_word(file_path)
    else:
        # Use textract for other file types (requires installation of textract library)
        return textract.process(file_path).decode('utf-8', errors='ignore')

def process_and_save_embeddings(file_path, output_csv):
    embeddings = None
    # Existing DataFrame
    df = pd.DataFrame(columns=["text", "embedding"])
    try:
        text = extract_text_from_file(file_path)

        tokenizer = tiktoken.get_encoding("cl100k_base")
        results = []

        chunks = create_chunk(text, 1000, tokenizer)

        text_chunks = [tokenizer.decode(chunk) for chunk in chunks]
        for chunk in text_chunks:
            results.append(chunk)
        
        print("CHUNKS   " , results[1])
        #embeddings = generate_embeddings(text)  # Generate embeddings for the text
        #print(" EXtract TEXT:", text)
        for single_result in results:
            embeddings = get_embedding(single_result)
            #print("SINGLE EMBEDDING ", embeddings)
            #new_df = pd.DataFrame({"text": [text], "embedding": [embeddings]})
            new_df = pd.DataFrame({"text":[text], "embedding":[embeddings]})
            print("NEW DF ", new_df)
            df = pd.concat([df, new_df],ignore_index=True)
            print("CONCAT DF", df)
        #     df.to_csv(output_csv, mode='a', header=True, index=False)

        df.to_csv(output_csv, mode='a', header=True, index=False)

        print (df)
        #print("EMBDEEING AFTER dataframe : ", embeddings)
        #print ( "EMBDEEING BEFORE dataframe : ", embeddings)
        # Create DataFrame with text and embeddings
        #df = pd.DataFrame({"text": [text], "embedding": [embeddings]})
        # Append values to the DataFrame
        
        # Save DataFrame to CSV file
        
    except RetryError as e:
        # Handle the error if all attempts fail
        print("Failed to fetch embeddings after multiple attempts:", e)
    
def create_chunk(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    """Yield successive n-sized chunks from text."""
    i = 0
    while i < len(tokens):
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        
        if j == i + int(0.5 * n):
            j = min( i + n , len(tokens))
        yield tokens[i:j]
        i = j


def convert_to_list(x):
  """
  This function attempts to convert a string representation of a list to an actual list,
  handling potential "nan" values.

  Args:
      x (str): The string containing the list representation.

  Returns:
      list: The converted list, or None if conversion fails.
  """
  try:
    # Try converting using eval (cautious approach)
    return eval(x)
  except (SyntaxError, NameError):
    pass

  # If eval fails, try simpler parsing (assuming list of numbers)
  try:
    return [float(num) for num in x.strip('[]').split(',') if num != 'nan']
  except ValueError:
    pass

  # Return None if conversion fails altogether
  return None
