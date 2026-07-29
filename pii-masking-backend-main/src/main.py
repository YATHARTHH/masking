from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import base64
import time
import asyncio

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import Enterprise Modules
from src.core.config import settings
from src.core.security import calculate_sha256
from src.db.database import init_db, add_audit_log
from src.middleware.audit_middleware import AuditMiddleware
from src.services.ttl_cleaner import run_ttl_cleanup_loop
from src.api.v1.router import router as v1_router

# Import existing utility functions
from src.utils.pdf_utils import process_pdf
from src.utils.image_utils import process_image
from src.utils.csv_utils import process_csv
from src.utils.docx_utils import process_docx
from src.utils.audio_utils import process_audio
from src.utils.text_utils import process_text
from src.utils.video_utils import process_video_optimized
from src.utils.ppt_utils import process_ppt

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs"
)

# Enterprise Middleware & Router Setup
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

PROCESSED_FOLDER = "processed"
UPLOAD_FOLDER = "uploads"
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    # Initialize SQLite Database Tables
    init_db()
    # Launch Background TTL Shredder Task
    asyncio.create_task(run_ttl_cleanup_loop())
    print("[Enterprise Core] SQLite Database initialized & TTL Cleaner daemon running.")

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    pii_category: str = Form(...),
    highlight_mode: str = Form(...)
):
    start_time = time.time()
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    ext = file.filename.split(".")[-1].lower()
    file_hash = calculate_sha256(file_path)

    try:
        if ext in ["png", "jpg", "jpeg"]:
            output = process_image(file_path, pii_category, highlight_mode, facial=False)

        elif ext == "pdf":
            output = process_pdf(file_path, pii_category, highlight_mode, facial=False)

        elif ext == "csv":
            output = process_csv(file_path, pii_category, highlight_mode)

        elif ext in ["wav", "mp3", "aiff", "aac", "ogg", "flac"]:
            output = process_audio(file_path, pii_category, highlight_mode)

        elif ext in ["txt"]:
            output = process_text(file_path, pii_category, highlight_mode)

        elif ext in ["docx"]:
            output = process_docx(file_path, pii_category, highlight_mode)
            
        elif ext in ["mp4", "mov"]:
            output = await process_video_optimized(file_path, pii_category, highlight_mode)

        elif ext in ["pptx", "ppt"]:
            output = await process_ppt(file_path, pii_category, highlight_mode)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        processed_filename = os.path.basename(output)
        pii_categories_list = [cat.strip() for cat in pii_category.replace('[', '').replace(']', '').replace('"', '').split(',')]
        
        # Calculate execution latency
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Log to Enterprise Audit Ledger
        if settings.ENABLE_AUDIT:
            add_audit_log(
                filename=file.filename,
                file_hash=file_hash,
                pii_categories=pii_categories_list,
                masking_type=highlight_mode,
                processing_time_ms=elapsed_ms,
                file_size=os.path.getsize(file_path),
                status="SUCCESS"
            )

        # Create response with file encoded as base64 for download
        with open(output, "rb") as f:
            file_data = f.read()
            file_base64 = base64.b64encode(file_data).decode('utf-8')
    
        download_url = f"/download/{processed_filename}"
        
        response_data = {
            "success": True,
            "message": "File processed successfully",
            "processing_info": {
                "pii_categories_detected": pii_categories_list,
                "masking_type": highlight_mode,
                "total_categories": len(pii_categories_list),
                "processing_time_ms": round(elapsed_ms, 2),
                "file_sha256": file_hash
            },
            "download": {
                "file_data": file_base64,
                "filename": processed_filename
            }
        }

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        # Log error to Audit Ledger
        add_audit_log(
            filename=file.filename,
            file_hash=file_hash,
            pii_categories=[],
            masking_type=highlight_mode,
            processing_time_ms=(time.time() - start_time) * 1000,
            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            status="FAILED"
        )
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to process file",
                "file_info": {
                    "original_filename": file.filename,
                    "file_type": ext
                }
            }, 
            status_code=500
        )

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download endpoint for processed files."""
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/healthcheck")
async def health_check(request: Request):
    """Health check endpoint verifying API status."""
    query_params = dict(request.query_params)
    if "force_fail" in query_params:
        return JSONResponse(
            status_code=500,
            content={"status": "FAIL", "reason": "Forced Failure"}
        )
    return JSONResponse(
        status_code=200,
        content={
            "status": "200, OK",
            "reason": "Healthy",
            "enterprise_mode": "Active",
            "db": "SQLite Connected"
        }
    )