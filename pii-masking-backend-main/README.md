# PII Detection and Masking System

A comprehensive FastAPI-based application that automatically detects and masks Personally Identifiable Information (PII) across multiple file formats using AI-powered analysis.

## Overview

This system uses Google's Gemini AI to identify PII in various document types and applies customizable masking techniques to protect sensitive information. It supports images, PDFs, text files, CSV/Excel files, DOCX documents, audio files, and videos.

## Features

- **Multi-format Support**: Process PDF, images (PNG/JPG), text files, CSV/Excel, DOCX, audio (WAV/MP3/M4A), and video files
- **AI-Powered Detection**: Uses Gemini 2.0 Flash for intelligent PII identification
- **Flexible Masking Options**:
  - Blurring (for images/videos)
  - Rectangular boxes (for images/videos)
  - Named replacement (e.g., `[Full Name]`)
  - Generic replacement (`[MASKED]`)
  - Character masking (X's)
- **Facial Recognition**: Optional face detection and blurring using YOLOv8
- **Multi-language Support**: Detects PII in multiple languages (English, Hindi, etc.)
- **Audio Processing**: Replaces spoken PII with beep tones
- **Video Processing**: Frame-by-frame PII detection with parallel processing

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Download or Clone the Repository**
   ```bash
   # If using git
   git clone <repository-url>
   cd pii-detection-system

   # Or download the ZIP file from:
   # [Download Link - Add your repository/release URL here]
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   - Obtain a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Replace `GEMINI_API_KEY` in the utility files with your API key
   - **Important**: Never commit API keys to version control

4. **Run the Application**
   ```bash
   # Recommended: Quick start with default settings
   uvicorn app:app

   # Alternative: Development mode with auto-reload
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**
   - Open your browser and navigate to `http://localhost:8000/docs` for API documentation
   - The server runs on `http://localhost:8000` by default

## Requirements

### Core Dependencies

```bash
fastapi
uvicorn
python-multipart
pandas
pillow
opencv-python
numpy
```

### AI and OCR

```bash
google-generativeai
easyocr
paddleocr
ultralytics  # YOLOv8 for face detection
```

### Document Processing

```bash
PyMuPDF  # fitz
python-docx
pdf2image
```

### Audio/Video Processing

```bash
pydub
audioread
```

### Text Similarity

```bash
textdistance
fuzzywuzzy
rapidfuzz
```

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── app.py                  # Alternative entry point
├── utils/
│   ├── pdf_utils.py       # PDF processing
│   ├── image_utils.py     # Image processing and PII detection
│   ├── text_utils.py      # Text file processing
│   ├── csv_utils.py       # CSV/Excel processing
│   ├── docx_utils.py      # DOCX processing
│   ├── audio_utils.py     # Audio processing
│   └── video_utils.py     # Video processing
├── static/uploads/        # Uploaded files directory (auto-created)
├── processed/             # Processed output files directory (auto-created)
└── requirements.txt       # Project dependencies
```

## Running the Project

### Method 1: Quick Start (Recommended)
```bash
uvicorn app:app
```
This starts the server with default settings on `http://localhost:8000`

### Method 2: Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Features:
- **Auto-reload**: Server restarts automatically when code changes
- **Accessible from network**: Available at `http://0.0.0.0:8000` (all network interfaces)
- **Port specification**: Runs on port 8000

### Method 3: Custom Configuration
```bash
# Run on a specific port
uvicorn app:app --port 5000

# Run with multiple workers
uvicorn app:app --workers 4

# Run with custom host and port
uvicorn app:app --host 0.0.0.0 --port 3000
```

### Verify Installation
After starting the server, visit:
- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## Usage

### API Endpoint

**POST** `/upload/`

**Parameters:**
- `file` (UploadFile): The file to process
- `pii_category` (str): Comma-separated list of PII categories to detect (e.g., "Full Name, Email Address, SSN")
- `highlight_mode` (str): Masking method
  - For images/videos: `blurring`, `rectangular_box`
  - For text/documents: `named_replacement`, `replacement`, or any other value for X masking

**Example using cURL:**

```bash
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@document.pdf" \
  -F "pii_category=Full Name,Email Address,Phone Number" \
  -F "highlight_mode=blurring"
```

### Python Example

```python
import requests

url = "http://localhost:8000/upload/"
files = {"file": open("document.pdf", "rb")}
data = {
    "pii_category": "Full Name, Email Address, SSN",
    "highlight_mode": "blurring"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Supported File Formats

| Format | Extensions | Processing Method |
|--------|-----------|-------------------|
| Images | .png, .jpg, .jpeg | OCR + AI detection + visual masking |
| PDF | .pdf | Convert to images → process each page |
| Text | .txt | AI text analysis + replacement |
| Spreadsheets | .csv, .xlsx | Column-based PII detection |
| Documents | .docx | Paragraph analysis + text replacement |
| Audio | .wav, .mp3, .m4a | Speech-to-text + beep masking |
| Video | .mp4, .avi | Frame-by-frame analysis + visual masking |

## PII Categories Supported

The system can detect various types of PII including:
- Full Names
- Email Addresses
- Phone Numbers
- Social Security Numbers (SSN)
- Dates of Birth
- Addresses
- Credit Card Numbers
- Medical Information
- And more (customizable via `pii_category` parameter)

## How It Works

### Image Processing
1. Upload image → Gemini AI analyzes content
2. EasyOCR extracts text from image
3. Fuzzy matching identifies PII locations
4. Apply blurring or rectangular masking
5. Optional: YOLOv8 detects and masks faces

### Text/Document Processing
1. Extract text content
2. Gemini AI identifies PII with exact text matches
3. Replace PII with chosen masking mode
4. Save processed document

### Audio Processing
1. Upload audio to Gemini AI
2. AI identifies PII with timestamps
3. Generate beep tones for PII segments
4. Overlay beeps on original audio

### Video Processing
1. Gemini AI analyzes video frames
2. Extract PII patterns
3. Process frames in parallel using ThreadPoolExecutor
4. Apply visual masking to detected PII
5. Reconstruct video with masked frames

## Configuration

### Folders
- `uploads/`: Temporary storage for uploaded files
- `processed/`: Output directory for processed files
- Both directories are created automatically

### Performance Tuning
- **Video processing workers**: Adjust `max_workers` in `video_utils.py` (default: 8)
- **Similarity threshold**: Modify `similarity_threshold` in `image_utils.py` (default: 0.5)
- **Fuzzy matching threshold**: Change threshold in `video_utils.py` (default: 70)

## Security Considerations

⚠️ **Important Security Notes:**
1. **API Keys**: Never commit API keys to version control. Use environment variables:
   ```python
   import os
   GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
   ```

2. **File Upload Limits**: Consider adding file size restrictions in production

3. **Input Validation**: Add validation for `pii_category` and `highlight_mode` parameters

4. **CORS Configuration**: The current setup allows all origins (`"*"`). Restrict this in production:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Use a different port
uvicorn app:app --port 8001
```

**Module not found errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**API key errors:**
- Verify your Gemini API key is valid
- Check that the key has sufficient quota
- Ensure the key is properly set in the utility files

**Permission errors:**
- Ensure write permissions for `uploads/` and `processed/` directories
- Run with appropriate user permissions

## Limitations

- Video processing is computationally intensive and may be slow for long videos
- Audio PII detection accuracy depends on speech clarity
- OCR accuracy varies with image quality and text language
- Large files may cause timeout issues

## Error Handling

The system returns appropriate HTTP errors:
- `400`: Unsupported file format
- `500`: Processing errors (check server logs for details)

## Contributing

When contributing, please:
1. Add type hints to function parameters
2. Include docstrings for new functions
3. Update this README for new features
4. Test with various file formats and PII types

## Download

Get the latest version:
- **GitHub Repository**: [Add your GitHub repository URL here]
- **Latest Release**: [Add your release page URL here]
- **Direct Download**: [Add direct download link here]

## License

[Specify your license here]

## Support

For issues and questions:
- Check server logs for detailed error messages
- Ensure all dependencies are installed correctly
- Verify API keys are valid and have sufficient quota
- Visit the API documentation at `/docs` endpoint

## Future Enhancements

- [ ] Support for more file formats (PowerPoint, etc.)
- [ ] Real-time video streaming support
- [ ] Batch processing API
- [ ] Custom PII detection models
- [ ] User authentication and file history
- [ ] Asynchronous processing with webhooks
- [ ] Docker containerization

---

<!-- DEVHUB-GITHOOKS:START (managed by rollout) -->
## Git Hooks & Pre-Commit Checks

This repo is pre-configured with the DevHub git hooks — every `git commit` is automatically scanned (gitleaks, detect-secrets, Semgrep, Ruff, Biome, terraform fmt, repo hygiene).

### First-time setup

Run **once** after cloning — installs the tools and activates the hooks:

**Windows (PowerShell):**
```powershell
.\tasks\mise-install.cmd
```

**macOS / Linux / Git Bash:**
```bash
bash tasks/mise-install.sh
```

> Run this **before committing** — until you do, your commits are blocked. If `mise` was just installed, open a new terminal first.

### Get the hooks into an existing branch

These hooks are merged into `main`/`master`. To pull them into a branch you already have, **rebase onto the latest `main` and re-run setup**:

```bash
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main
.\tasks\mise-install.cmd      # Windows  (bash tasks/mise-install.sh on macOS/Linux)
```

### Run the checks manually

```bash
mise scan
```

### Troubleshooting — hook ignored on macOS / Linux

If a commit goes through **without** the checks running, Git skipped the hook because it isn't executable:

```
hint: The '.githooks/pre-commit' hook was ignored because it's not set as executable.
```

Setup (`mise-install.sh`) marks the hooks executable, but if you still hit this, fix it manually — the executable bit is tracked by Git, so committing it keeps the gate working for everyone who clones:

```bash
chmod +x .githooks/*
git add .githooks/
git commit -m "chore: make git hooks executable"
```

Verify: `ls -la .githooks/` shows `-rwxr-xr-x`, and `git config core.hooksPath` prints `.githooks`.
<!-- DEVHUB-GITHOOKS:END -->

