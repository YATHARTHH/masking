from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import os
import uuid
import zipfile
import base64
import time
from typing import List, Optional

from src.db.database import (
    get_audit_logs, 
    get_analytics_summary, 
    add_audit_log, 
    create_job, 
    update_job, 
    get_job,
    get_db_connection
)
from src.core.security import calculate_sha256, generate_api_key
from src.services.compliance_reporter import generate_html_compliance_report
from src.services.fallback_engine import detect_pii_offline
from src.middleware.auth_middleware import verify_api_key
from src.utils.image_utils import process_image
from src.utils.text_utils import process_text

router = APIRouter(prefix="/api/v1", tags=["Enterprise V1"])

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@router.get("/analytics/stats")
async def get_analytics():
    """Retrieve enterprise dashboard analytics and system performance metrics."""
    return get_analytics_summary()

@router.get("/audit/logs")
async def fetch_audit_logs(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    """Fetch paginated audit log ledger records."""
    logs = get_audit_logs(limit=limit, offset=offset)
    return {"status": "success", "count": len(logs), "logs": logs}

@router.get("/audit/export", response_class=HTMLResponse)
async def export_audit_report():
    """Export compliance proof report for GDPR/HIPAA audits."""
    logs = get_audit_logs(limit=100)
    html_content = generate_html_compliance_report(logs)
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/keys")
async def create_new_api_key(name: str = Form(...), role: str = Form("operator")):
    """Generate a new enterprise API key."""
    raw_key, key_hash = generate_api_key(name)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO api_keys (key_hash, name, role, created_at) VALUES (?, ?, ?, ?)", 
                   (key_hash, name, role, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return {
        "success": True,
        "api_key": raw_key,
        "name": name,
        "role": role,
        "note": "Save this key securely. It will not be shown again."
    }

@router.post("/batch")
async def process_batch_files(
    files: List[UploadFile] = File(...),
    pii_category: str = Form(...),
    highlight_mode: str = Form(...)
):
    """Process multiple files in a single batch and return a summary with processed outputs."""
    results = []
    start_time = time.time()
    
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
            
        ext = file.filename.split(".")[-1].lower()
        file_hash = calculate_sha256(file_path)
        
        try:
            if ext in ["png", "jpg", "jpeg"]:
                output = process_image(file_path, pii_category, highlight_mode, facial=False)
            elif ext in ["txt"]:
                output = process_text(file_path, pii_category, highlight_mode)
            else:
                # Basic fallback text processor if format is text-based or generic
                output = process_text(file_path, pii_category, highlight_mode)
                
            proc_filename = os.path.basename(output)
            cats_list = [c.strip() for c in pii_category.replace('[', '').replace(']', '').replace('"', '').split(',')]
            
            # Log to SQLite Audit
            add_audit_log(
                filename=file.filename,
                file_hash=file_hash,
                pii_categories=cats_list,
                masking_type=highlight_mode,
                processing_time_ms=(time.time() - start_time) * 1000,
                file_size=os.path.getsize(file_path)
            )
            
            results.append({
                "filename": file.filename,
                "status": "SUCCESS",
                "processed_filename": proc_filename,
                "download_url": f"/download/{proc_filename}"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "FAILED",
                "error": str(e)
            })
            
    return {
        "success": True,
        "batch_size": len(files),
        "processed_files": results
    }

@router.post("/preview")
async def preview_hitl(
    file: UploadFile = File(...),
    pii_category: str = Form(...)
):
    """Human-in-the-loop preview endpoint returning detected PII items before masking."""
    content = await file.read()
    text_content = content.decode('utf-8', errors='ignore')
    cats = [c.strip() for c in pii_category.replace('[', '').replace(']', '').replace('"', '').split(',')]
    
    # Run offline scanner to get detected item coordinates / matches
    offline_results = detect_pii_offline(text_content, cats)
    
    return {
        "filename": file.filename,
        "file_size": len(content),
        "categories_requested": cats,
        "detected_items": offline_results["pii_matches"],
        "total_matches": offline_results["total_detected"],
        "recommendation": "Ready for Human Approval" if offline_results["total_detected"] > 0 else "No PII Found"
    }

@router.get("/jobs/{job_id}")
async def fetch_job_status(job_id: str):
    """Check progress of asynchronous processing job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found")
    return job
