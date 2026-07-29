from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from src.core.config import settings
from src.core.security import hash_api_key
import sqlite3

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """API Key verification dependency."""
    if not settings.ENABLE_AUTH:
        return {"role": "admin", "name": "Dev Mode User"}
        
    if not api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
        
    incoming_hash = hash_api_key(api_key)
    conn = sqlite3.connect(settings.DATABASE_URL.replace("sqlite:///", ""))
    cursor = conn.cursor()
    cursor.execute("SELECT role, name FROM api_keys WHERE key_hash = ? AND is_active = 1", (incoming_hash,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=403, detail="Invalid or deactivated API Key")
        
    return {"role": row[0], "name": row[1]}
