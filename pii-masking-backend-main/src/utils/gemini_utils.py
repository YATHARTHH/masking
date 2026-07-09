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

def filter_pii_by_categories(detected_pii: list, pii_category_str: str) -> list:
    """
    Filters detected PII items based on the user-selected categories.
    Handles normalizing names (e.g. converting "name" user selection to match "Full Name", "First Name", etc.)
    """
    if not pii_category_str:
        return detected_pii
        
    # Normalize categories: convert "name, address" to ["name", "address"]
    normalized_categories = []
    # Strip brackets, quotes, and whitespace
    clean_str = pii_category_str.replace("[", "").replace("]", "").replace('"', "").replace("'", "")
    for cat in clean_str.split(","):
        cat_clean = cat.strip().lower()
        if cat_clean:
            # Map standard frontend categories to broader/similar terms
            if cat_clean == "name":
                normalized_categories.extend(["name", "individual", "person"])
            elif cat_clean == "contact_number":
                normalized_categories.extend(["contact", "phone", "mobile", "number", "tel"])
            elif cat_clean == "aadhaar_number":
                normalized_categories.extend(["aadhaar", "aadhar"])
            elif cat_clean == "tax_identification_number":
                normalized_categories.extend(["tax", "pan", "tin"])
            elif cat_clean == "financial_account":
                normalized_categories.extend(["account", "card", "bank", "credit", "debit"])
            else:
                # Add specific custom category
                normalized_categories.append(cat_clean)
                
    filtered_pii = []
    for pii in detected_pii:
        pii_type = pii.get("type", "").lower()
        
        # Special case: If user selected ONLY 'name', do NOT match numbers/accounts/IDs.
        # This prevents other IDs (like Challan Number) from being kept if they have "number" in their type.
        is_name_only = len(normalized_categories) == 1 and "name" in normalized_categories
        if is_name_only and any(x in pii_type for x in ["number", "account", "id", "card", "ssn", "aadhaar", "pan"]):
            continue
            
        # If any selected category matches (partial string match) the PII type, keep it
        if any(cat in pii_type for cat in normalized_categories):
            filtered_pii.append(pii)
            
    return filtered_pii

