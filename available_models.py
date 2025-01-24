import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    models = openai.Model.list()
    print("Available models:", [model['id'] for model in models['data']])
except Exception as e:
    print(f"Error: {e}")

