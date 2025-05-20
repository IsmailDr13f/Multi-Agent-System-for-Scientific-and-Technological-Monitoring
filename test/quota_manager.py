from collections import defaultdict
import threading
import time
import logging
import os
from typing import List



# 1. Intelligent Quota Manager (QuotaManager)

class QuotaManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.model_usage = defaultdict(list)  # Stores timestamp of each API call
        self.cooldown_until = defaultdict(float)  # Timestamp when model will be available again
        
    def _refresh_counters(self):
        """Remove timestamps older than 60 seconds"""
        current_time = time.time()
        for model in self.model_usage:
            self.model_usage[model] = [t for t in self.model_usage[model] 
                                    if current_time - t < 60]
                                    
    def _is_model_available(self, model: str) -> bool:
        """Check if a model is available or in cooldown"""
        if time.time() < self.cooldown_until[model]:
            return False
            
        # Prevent exceeding 12 requests per minute (below the actual limit of 15)
        # This gives us a safety buffer
        return len(self.model_usage[model]) < 12
        
    def record_usage(self, model: str):
        """Record that we've used a model"""
        with self.lock:
            self.model_usage[model].append(time.time())
            
    def get_available_model(self, preferred_model: str) -> str:
        """Return the best available model currently"""
        with self.lock:
            self._refresh_counters()
            
            # Check if preferred model is available
            if self._is_model_available(preferred_model):
                return preferred_model
                
            # Otherwise, use model cascade
            model_cascade = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
            for model in model_cascade:
                if self._is_model_available(model) and model != preferred_model:
                    return model
                    
            # If no models available, return the one with fewest recent calls
            return min(self.model_usage.items(), key=lambda x: len(x[1]))[0]
            
    def set_cooldown(self, model: str, seconds: int = 60):
        """Put a model in cooldown when we hit quota limits"""
        with self.lock:
            self.cooldown_until[model] = time.time() + seconds
            logging.info(f"Model {model} in cooldown for {seconds} seconds")
            

# 2. API Key Rotation System (APIKeyManager)
class APIKeyManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.api_keys = self._load_api_keys()
        self.current_index = 0
        
    def _load_api_keys(self) -> List[str]:
        """Load API keys from environment and .env file"""
        keys = []
        
        # Get keys from environment variables
        env_key = os.environ.get("GEMINI_API_KEY")
        if env_key:
            keys.append(env_key)
            
        # Get additional keys from .env.apikeys file
        try:
            with open(".env.apikeys", "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        keys.append(line.strip())
        except FileNotFoundError:
            pass
            
        if not keys:
            raise ValueError("No API keys found in environment or .env.apikeys file")
            
        logging.info(f"Loaded {len(keys)} API keys")
        return keys
        
    def get_next_key(self) -> str:
        """Get the next API key in rotation"""
        with self.lock:
            key = self.api_keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            return key 


# 3. Automatic Rate Limiting
class RateLimiter:
    def __init__(self, requests_per_minute: int = 12):
        self.lock = threading.Lock()
        self.min_interval = 60 / requests_per_minute  # Minimum seconds between requests
        self.last_request_time = 0
        
    def wait_if_needed(self):
        """Wait if we're making requests too quickly"""
        with self.lock:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                logging.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                
            self.last_request_time = time.time()
            
class BackoffStrategy:
    def __init__(self, base_delay: float = 2.0, max_retries: int = 5):
        self.base_delay = base_delay
        self.max_retries = max_retries
        
    def get_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        if attempt >= self.max_retries:
            raise ValueError(f"Maximum retries ({self.max_retries}) exceeded")
            
        return self.base_delay ** attempt 


# 4. Model Cascade Implementation
class ModelCascade:
    def __init__(self, quota_manager: QuotaManager):
        self.quota_manager = quota_manager
        self.primary_models = {
            "fast": "gemini-2.0-flash",
            "balanced": "gemini-1.5-flash",
            "powerful": "gemini-pro"
        }
        
    def get_model(self, preference: str = "balanced") -> str:
        """Get the best available model based on preference and availability"""
        preferred_model = self.primary_models.get(preference, "gemini-1.5-flash")
        return self.quota_manager.get_available_model(preferred_model) 



# 5. Robust Error Handling and Retry Logic
class GeminiClient:
    def __init__(self, api_key_manager: APIKeyManager, quota_manager: QuotaManager,
                 rate_limiter: RateLimiter, backoff: BackoffStrategy):
        self.api_key_manager = api_key_manager
        self.quota_manager = quota_manager
        self.rate_limiter = rate_limiter
        self.backoff = backoff
        
    def _is_quota_error(self, error) -> bool:
        """Determine if an error is related to quota limits"""
        if hasattr(error, 'code') and error.code == 429:
            return True
            
        if hasattr(error, 'message') and "quota" in error.message.lower():
            return True
            
        return False
        
    def generate_content(self, model: str, prompt: str, max_retries: int = 3) -> str:
        """Generate content with automatic retry and fallback"""
        attempts = 0
        used_models = set()
        
        while attempts < max_retries:
            try:
                # Apply rate limiting
                self.rate_limiter.wait_if_needed()
                
                # Get the current model to use
                current_model = model if model not in used_models else self.quota_manager.get_available_model(model)
                used_models.add(current_model)
                
                # Get the next API key
                api_key = self.api_key_manager.get_next_key()
                
                # Create Gemini client
                genai.configure(api_key=api_key)
                gemini_model = genai.GenerativeModel(current_model)
                
                # Record usage and make the actual API call
                self.quota_manager.record_usage(current_model)
                response = gemini_model.generate_content(prompt)
                
                return response.text
                
            except Exception as e:
                attempts += 1
                logging.warning(f"Attempt {attempts} failed: {str(e)}")
                
                if self._is_quota_error(e):
                    # Handle quota error
                    self.quota_manager.set_cooldown(current_model)
                    continue  # Try again immediately with different model
                    
                # For other errors, use exponential backoff
                try:
                    delay = self.backoff.get_delay(attempts)
                    logging.info(f"Backing off for {delay} seconds")
                    time.sleep(delay)
                except ValueError:
                    # Max retries exceeded
                    raise
                    
        raise Exception(f"Failed to generate content after {max_retries} attempts") 
    


# Putting It All Together
def create_gemini_client() -> GeminiClient:
    """Factory function to create a fully configured Gemini client"""
    api_key_manager = APIKeyManager()
    quota_manager = QuotaManager()
    rate_limiter = RateLimiter(requests_per_minute=12)
    backoff = BackoffStrategy(base_delay=2.0, max_retries=5)
    
    return GeminiClient(
        api_key_manager=api_key_manager,
        quota_manager=quota_manager,
        rate_limiter=rate_limiter,
        backoff=backoff
    )





