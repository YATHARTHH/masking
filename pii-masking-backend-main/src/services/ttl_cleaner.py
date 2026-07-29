import os
import time
import asyncio
from src.core.config import settings

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

async def run_ttl_cleanup_loop():
    """Background worker that periodically deletes files older than FILE_TTL_SECONDS."""
    while True:
        try:
            now = time.time()
            ttl = settings.FILE_TTL_SECONDS
            
            for folder in [UPLOAD_DIR, PROCESSED_DIR]:
                if os.path.exists(folder):
                    for fname in os.listdir(folder):
                        fpath = os.path.join(folder, fname)
                        if os.path.isfile(fpath):
                            file_age = now - os.path.getmtime(fpath)
                            if file_age > ttl:
                                try:
                                    os.remove(fpath)
                                    print(f"[TTL Cleaner] Safely shredded expired file: {fname} (Age: {int(file_age)}s)")
                                except Exception as e:
                                    print(f"[TTL Cleaner] Error deleting {fname}: {e}")
        except Exception as err:
            print(f"[TTL Cleaner Error] {err}")
            
        await asyncio.sleep(60)  # Check every 60 seconds
