import os
import random
from dotenv import load_dotenv

class GeminiKeyRotator:
    def __init__(self, env_var_name='GEMINI_KEYS', prompts_per_key=10):
        load_dotenv()
        raw_keys = os.getenv(env_var_name)

        if not raw_keys:
            raise ValueError(f"No API keys found in environment variable: {env_var_name}")

        self.api_keys = [k.strip() for k in raw_keys.split(',') if k.strip()]
        if not self.api_keys:
            raise ValueError("No valid API keys found after parsing.")
        random.shuffle(self.api_keys)  # Distribute usage

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
