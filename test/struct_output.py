from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from dotenv import load_dotenv
from agno.models.google import Gemini
import os

class GeminiKeyRotator:
    def __init__(self, env_var_name='GEMINI_KEYS', prompts_per_key=10):
        load_dotenv()  # Load .env into environment variables
        raw_keys = os.getenv(env_var_name)

        if not raw_keys:
            raise ValueError(f"No API keys found in environment variable: {env_var_name}")

        self.api_keys = [k.strip() for k in raw_keys.split(',') if k.strip()]
        self.key_index = 0
        self.prompt_count = 0
        self.prompts_per_key = prompts_per_key

    def get_current_key(self):
        return self.api_keys[self.key_index]

    def rotate_key_if_needed(self):
        self.prompt_count += 1
        if self.prompt_count >= self.prompts_per_key:
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            self.prompt_count = 0
            print(f"🔁 Rotated to key index: {self.key_index}")

    def force_rotate_key(self):
        self.key_index = (self.key_index + 1) % len(self.api_keys)
        self.prompt_count = 0
        print(f"⚠️ Forced key rotation to index: {self.key_index}")

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
rotator = GeminiKeyRotator()

class MovieScript(BaseModel):
    name: str = Field(..., description="Name of the movie.")
    setting: str = Field(..., description="Provide a setting for the movie.")
    ending: str = Field(..., description="Describe the movie ending.")
    genre: str = Field(..., description="Genre of the movie.")
    characters: List[str] = Field(..., description="List of characters.")
    storyline: str = Field(..., description="A 3-sentence storyline.")

agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=rotator.get_current_key()),
    instructions=["Generate a movie script outline.", "Provide a detailed plot summary."],
    response_model=MovieScript,
    markdown=True,
)

agent.print_response("Generate a movie script outline for a sci-fi adventure.")