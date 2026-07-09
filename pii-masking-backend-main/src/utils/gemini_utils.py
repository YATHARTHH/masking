import time
from google.genai import Client

def generate_content_with_retry(client: Client, model: str, contents, **kwargs):
    """
    Generate content using Gemini API client with automatic retry on 429 rate limit (RESOURCE_EXHAUSTED).
    Supports exponential backoff.
    """
    max_retries = kwargs.pop('max_retries', 5)
    initial_backoff = kwargs.pop('initial_backoff', 2)
    backoff = initial_backoff
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                **kwargs
            )
            return response
        except Exception as e:
            err_msg = str(e).lower()
            # Catch Google API Resource Exhausted (429) rate limit errors
            if "429" in err_msg or "resource_exhausted" in err_msg or "exhausted" in err_msg or "rate limit" in err_msg:
                if attempt == max_retries - 1:
                    print(f"Rate limit retry failed after {max_retries} attempts.")
                    raise e
                print(f"Rate limited (429). Retrying in {backoff} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(backoff)
                backoff *= 2
            else:
                raise e
