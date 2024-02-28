import os
import time

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
