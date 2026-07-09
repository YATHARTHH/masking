from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import base64

# Import all utility functions
from src.utils.pdf_utils import process_pdf
from src.utils.image_utils import process_image
from src.utils.csv_utils import process_csv
from src.utils.docx_utils import process_docx
from src.utils.audio_utils import process_audio
from src.utils.text_utils import process_text
from src.utils.video_utils import process_video_optimized
from src.utils.ppt_utils import process_ppt


app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UPLOAD_FOLDER = "static/uploads"
PROCESSED_FOLDER = "processed"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    pii_category: str = Form(...),
    highlight_mode: str = Form(...)
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    ext = file.filename.split(".")[-1].lower()

    try:
        if ext in ["png", "jpg", "jpeg"]:
            output = process_image(file_path, pii_category, highlight_mode, facial=False)

        elif ext == "pdf":
            output = process_pdf(file_path, pii_category, highlight_mode, facial=False)

        elif ext == "csv":
            output = process_csv(file_path, pii_category, highlight_mode)

        elif ext in ["wav", "mp3", "aiff","aac","ogg","flac"]:
            output = process_audio(file_path, pii_category, highlight_mode)

        elif ext in ["txt"]:
            output = process_text(file_path, pii_category, highlight_mode)

        elif ext in ["docx"]:
            output = process_docx(file_path, pii_category, highlight_mode)
            
        elif ext in ["mp4","mov"]:
            output=await process_video_optimized(file_path, pii_category, highlight_mode)

        elif ext in ["pptx", "ppt"]:
            output = await process_ppt(file_path, pii_category, highlight_mode)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

    # except Exception as e:
    #     return JSONResponse(content={"error": str(e)}, status_code=500)

    # return output
        processed_filename = os.path.basename(output)
        pii_categories_list = [cat.strip() for cat in pii_category.replace('[', '').replace(']', '').replace('"', '').split(',')]
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
                "total_categories": len(pii_categories_list)
            },
            "download": {
                "file_data": file_base64,
                "filename": processed_filename
            }
        }

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
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


@app.get("/healthcheck")
async def health_check(request: Request):
    """
    Health check endpoint to verify API status
    Returns 200 OK if healthy, 500 if force_fail parameter is present
    """
    # Get all query parameters
    query_params = dict(request.query_params)
    
    # Define allowed query parameters
    allowed_keys = {"force_fail"}
    request_keys = set(query_params.keys())
    
    # Check for unexpected query parameters
    unexpected_params = request_keys - allowed_keys
    if unexpected_params:
        return JSONResponse(
            status_code=400,
            content={
                "status": "FAIL",
                "reason": f"Unexpected Query Parameters: {list(unexpected_params)}"
            }
        )
    
    # Check if force_fail parameter is present
    if "force_fail" in query_params:
        force_fail_value = query_params.get("force_fail")
        return JSONResponse(
            status_code=500,
            content={
                "status": "FAIL",
                "reason": f"Unhealthy, Manually Forced Failure (value: {force_fail_value})"
            }
        )
    
    # Return healthy status
    return JSONResponse(
        status_code=200,
        content={
            "status": "200, OK",
            "reason": "Healthy"
        }
    )