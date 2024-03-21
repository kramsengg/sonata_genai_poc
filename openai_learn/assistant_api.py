import json

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

from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>"))


assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-3.5-turbo-1106",
)
show_json(assistant)