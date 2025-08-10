import time
from functools import wraps

def with_key_rotation(rotator, max_attempts=5, backoff_seconds=5):
    def decorator(agent_func):
        @wraps(agent_func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    result = agent_func(*args, **kwargs)
                    rotator.rotate_key_if_needed()
                    return result
                except Exception as e:
                    if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                        print(f"⚠️ Quota error. Rotating key and retrying (attempt {attempt+1}/{max_attempts})")
                        rotator.force_rotate_key()
                        time.sleep(backoff_seconds)
                        continue
                    last_exception = e
                    break
            raise RuntimeError("❌ All Gemini API keys exhausted or failed.") from last_exception
        return wrapper
    return decorator
