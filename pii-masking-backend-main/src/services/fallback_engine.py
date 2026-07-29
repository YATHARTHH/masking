import re
from typing import List, Dict, Any

# Enterprise Regex Patterns for Local Air-Gapped PII Detection
PATTERNS = {
    "Email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "Phone Number": r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
    "Credit Card": r'\b(?:\d[ -]*?){13,16}\b',
    "IP Address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    "Date of Birth": r'\b(0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b',
    "API Key": r'\b[A-Za-z0-9_-]{32,64}\b',
    "Aadhaar Number": r'\b\d{4}\s?\d{4}\s?\d{4}\b',
}

def detect_pii_offline(text: str, categories: List[str]) -> Dict[str, Any]:
    """Offline PII detection scanner using local regular expressions."""
    detected = {}
    total_found = 0
    
    for cat in categories:
        clean_cat = cat.strip()
        pattern = PATTERNS.get(clean_cat)
        if pattern:
            matches = list(set(re.findall(pattern, text)))
            if matches:
                # Handle regex tuple groups if present
                clean_matches = [m[0] if isinstance(m, tuple) else m for m in matches]
                detected[clean_cat] = clean_matches
                total_found += len(clean_matches)
                
    return {
        "engine": "Local Offline Regex Fallback Engine",
        "total_detected": total_found,
        "pii_matches": detected
    }

def mask_text_offline(text: str, categories: List[str], mask_mode: str = "general") -> str:
    """Mask text using local offline regex rules."""
    result = text
    for cat in categories:
        clean_cat = cat.strip()
        pattern = PATTERNS.get(clean_cat)
        if pattern:
            if mask_mode == "general":
                replacement = f"[{clean_cat.upper()}_MASKED]"
            elif mask_mode == "x_mask":
                replacement = "XXXXXX"
            else:
                replacement = f"[{clean_cat}]"
            result = re.sub(pattern, replacement, result)
    return result
