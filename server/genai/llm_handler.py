import os
from langchain_fireworks import ChatFireworks
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()

class LLMHandler:
    def __init__(self):
        self.model = ChatFireworks(
            model="accounts/fireworks/models/llama-v3p1-8b-instruct",
            max_tokens=None,
            temperature=0,
            api_key=SecretStr(os.environ.get("FIREWORKS_API_KEY"))
        )
