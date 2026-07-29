import sqlite3
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.core.config import settings

DB_FILE = settings.DATABASE_URL.replace("sqlite:///", "")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for Enterprise features."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_hash TEXT,
        pii_categories TEXT,
        masking_type TEXT,
        status TEXT DEFAULT 'SUCCESS',
        processing_time_ms REAL DEFAULT 0,
        file_size_bytes INTEGER DEFAULT 0
    )
    """)
    
    # API Keys Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_hash TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'operator',
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)
    
    # Async Jobs Queue Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_queue (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        pii_categories TEXT NOT NULL,
        masking_mode TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        progress INTEGER DEFAULT 0,
        result_filename TEXT,
        error_message TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # Insert default admin API Key if empty
    cursor.execute("SELECT COUNT(*) FROM api_keys")
    if cursor.fetchone()[0] == 0:
        # Default key hash for 'pii_live_default_admin_key_12345'
        import hashlib
        default_raw = "pii_live_default_admin_key_12345"
        default_hash = hashlib.sha256(default_raw.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO api_keys (key_hash, name, role, created_at) VALUES (?, ?, ?, ?)",
            (default_hash, "Default Enterprise Admin", "admin", datetime.utcnow().isoformat())
        )
    
    conn.commit()
    conn.close()

# Database Helper Functions
def add_audit_log(filename: str, file_hash: str, pii_categories: List[str], masking_type: str, processing_time_ms: float = 0, file_size: int = 0, status: str = "SUCCESS"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (timestamp, filename, file_hash, pii_categories, masking_type, status, processing_time_ms, file_size_bytes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        filename,
        file_hash,
        json.dumps(pii_categories),
        masking_type,
        status,
        processing_time_ms,
        file_size
    ))
    conn.commit()
    conn.close()

def get_audit_logs(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["pii_categories"] = json.loads(item["pii_categories"])
        except Exception:
            item["pii_categories"] = []
        results.append(item)
    return results

def get_analytics_summary() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(file_size_bytes), AVG(processing_time_ms) FROM audit_logs WHERE status = 'SUCCESS'")
    total_count, total_bytes, avg_latency = cursor.fetchone()
    
    cursor.execute("SELECT pii_categories FROM audit_logs")
    rows = cursor.fetchall()
    
    category_counts = {}
    for r in rows:
        try:
            cats = json.loads(r[0])
            for c in cats:
                category_counts[c] = category_counts.get(c, 0) + 1
        except Exception:
            pass
            
    conn.close()
    
    return {
        "total_files_processed": total_count or 0,
        "total_bytes_processed": total_bytes or 0,
        "avg_processing_time_ms": round(avg_latency or 0, 2),
        "pii_category_distribution": category_counts,
        "engine_health": "100% Operational"
    }

def create_job(job_id: str, filename: str, pii_categories: str, masking_mode: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_queue (id, filename, pii_categories, masking_mode, status, progress, created_at)
        VALUES (?, ?, ?, ?, 'pending', 0, ?)
    """, (job_id, filename, pii_categories, masking_mode, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"job_id": job_id, "status": "pending"}

def update_job(job_id: str, status: str, progress: int = 0, result_filename: Optional[str] = None, error: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE job_queue SET status = ?, progress = ?, result_filename = ?, error_message = ? WHERE id = ?
    """, (status, progress, result_filename, error, job_id))
    conn.commit()
    conn.close()

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_queue WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
