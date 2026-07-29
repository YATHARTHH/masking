# PII Shield Enterprise - Master Interview Q&A Guide

This is the ultimate, end-to-end technical reference and interview guide for the **PII Shield Enterprise System**. It covers all **36 deep-dive questions**, system design decisions, technology stack justifications, file-processing pipelines, security architectures, and scenario-based interview responses.

---

## 📑 Table of Contents
1. [Pillar 1: Project Overview & Business Value (Q1 - Q4)](#pillar-1-project-overview--business-value)
2. [Pillar 2: Technology Stack Justifications (Q5 - Q11)](#pillar-2-technology-stack-justifications)
3. [Pillar 3: Per-Format Processing Pipelines (Q12 - Q19)](#pillar-3-per-format-processing-pipelines)
4. [Pillar 4: Enterprise Security & Governance (Q20 - Q25)](#pillar-4-enterprise-security--governance)
5. [Pillar 5: System Design & Production Scaling (Q26 - Q30)](#pillar-5-system-design--production-scaling)
6. [Pillar 6: Developer Quality & Operations (Q31 - Q33)](#pillar-6-developer-quality--operations)
7. [Pillar 7: Quick-Reference Cheat Sheet & Interview Numbers (Q34 - Q36)](#pillar-7-quick-reference-cheat-sheet--interview-numbers)

---

## 🎯 Pillar 1: Project Overview & Business Value

### Q1: Can you explain your project in 60 seconds?
> **Answer:**  
> "PII Shield Enterprise is an AI-powered, full-stack monorepo system designed to automatically detect and mask Personally Identifiable Information (PII) across 7 file format families: Images, PDFs, Word docs, PowerPoints, Spreadsheets, Audio files, and Video files.
> 
> On the backend, we use **FastAPI** paired with **Google's Gemini 2.0 Flash** for semantic context detection, **YOLOv8** for real-time computer vision face blurring, and **EasyOCR/PaddleOCR** for coordinate-based visual text masking. 
> 
> On the frontend, we built an interactive dashboard using **React, TypeScript, and Vite** featuring single-file masking, batch processing, a Human-in-the-Loop review queue, a searchable SQLite audit ledger, and automated GDPR/HIPAA compliance report generation. Everything is built with strict privacy controls—including local AES-256 storage encryption at rest and an automated background file shredder."

### Q2: What real-world compliance regulations does this system help solve?
> **Answer:**  
> 1. **GDPR (EU General Data Protection Regulation)**: Enforces "Data Minimization" and the "Right to Erasure" (Articles 5 & 17). Our automated TTL shredder and redaction engine ensure sensitive user data is scrubbed before public sharing.
> 2. **HIPAA (Health Insurance Portability and Accountability Act)**: Requires sanitizing 18 categories of Protected Health Information (PHI) in medical records, patient receipts, and doctor-patient call recordings.
> 3. **CCPA (California Consumer Privacy Act)**: Gives consumers the right to restrict disclosure of sensitive personal data.
> 4. **SOC 2 Type II**: Requires immutable logging of data processing activities, fulfilled by our SQLite audit ledger.

### Q3: What is the high-level system architecture?
> **Answer:**  
> We use a modern **SPA + Async REST API** architecture:
> - **Frontend**: React 19 + TypeScript single-page app communicating via HTTP/REST.
> - **Backend Gateway**: FastAPI app with CORS middleware, Audit logging middleware, and API Key security dependencies.
> - **AI & Vision Pipeline**: Gemini 2.0 Flash for semantic classification, EasyOCR for spatial coordinates, YOLOv8 for biometric faces.
> - **Persistence & Storage**: Embedded SQLite database (`pii_enterprise.db`) and AES-256 encrypted local storage with background TTL cleanup.

### Q4: What file format families does the system support?
> **Answer:**  
> We support 7 core format families:
> - **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`
> - **Documents**: `.pdf`
> - **Word / Text**: `.docx`, `.txt`
> - **Presentations**: `.pptx`, `.ppt`
> - **Tabular Data**: `.csv`, `.xlsx`
> - **Audio**: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`
> - **Video**: `.mp4`, `.mov`, `.avi`

---

## 🛠️ Pillar 2: Technology Stack Justifications

### Q5: Why did you choose FastAPI over Flask or Django?
> **Answer:**  
> 1. **Asynchronous Performance (ASGI)**: FastAPI is built on Starlette and supports native `async/await`, crucial for handling high concurrency during streaming file uploads and AI API calls.
> 2. **Automatic Pydantic Validation**: Validates request parameters and schemas automatically at compile/runtime.
> 3. **Automatic OpenAPI/Swagger Spec**: Generates interactive documentation at `/docs` out-of-the-box.
> 4. **Lightweight Microservice Footprint**: Unlike Django's heavy ORM boilerplate, FastAPI allows building a modular API gateway.

### Q6: Why React 19 + TypeScript + Vite on the Frontend?
> **Answer:**  
> 1. **Vite**: Provides instant Hot Module Replacement (HMR) powered by `esbuild` under the hood, speeding up developer iteration.
> 2. **TypeScript**: Provides compile-time type safety across complex data objects like PII bounding boxes, upload states, and audit log items, eliminating runtime `TypeError` crashes.
> 3. **React 19**: Component-driven architecture allowing easy state management across 5 enterprise pages (Workbench, Batch, Preview, Audit, Analytics).

### Q7: Why Gemini 2.0 Flash over OpenAI GPT-4 or local Llama models?
> **Answer:**  
> 1. **Semantic Intelligence over Regex**: Regex fails on context (e.g., distinguishing a serial number from a credit card, or a person's name from a business name). Gemini understands context.
> 2. **Speed & Multimodal Support**: Gemini 2.0 Flash offers low-latency token generation, supports direct image/audio inputs, and provides a 1M+ token context window.

### Q8: Why YOLOv8 for Face Detection over OpenCV Haar Cascades?
> **Answer:**  
> OpenCV Haar Cascades are outdated, lighting-sensitive, and produce high false-positive rates. **YOLOv8 (You Only Look Once)** is a single-pass convolutional neural network (CNN) that detects human faces in real time with high accuracy, even under motion blur, rotation, or partial occlusion.

### Q9: Why combine EasyOCR with Levenshtein Distance for visual text masking?
> **Answer:**  
> LLMs like Gemini tell us *what* sensitive text exists in an image, but cannot give exact pixel bounding box coordinates (`x, y, w, h`). We run EasyOCR to extract spatial coordinates of all visual words, then use **Levenshtein Distance fuzzy string matching** to align OCR words with Gemini's detected PII strings.

### Q10: Why SQLite for local database persistence?
> **Answer:**  
> SQLite is zero-configuration, serverless, and self-contained. It allows the enterprise edition of this application to run out-of-the-box on any local developer or edge server without requiring external container orchestrations (like PostgreSQL or MySQL), while still guaranteeing ACID transaction compliance for our audit ledger.

### Q11: Why Fernet AES-256 for local storage encryption?
> **Answer:**  
> Fernet guarantees that data encrypted with AES-256 in CBC mode using a 128-bit AES key and HMAC-SHA256 authentication cannot be read or manipulated without the secret key, protecting files at rest on disk.

---

## 🎨 Pillar 3: Per-Format Processing Pipelines

### Q12: How does the Image & Visual Document Masking Pipeline work?
> **Answer:**  
> 1. **Detection**: Image is passed to Gemini 2.0 Flash to extract a list of target PII strings.
> 2. **Spatial Localization**: EasyOCR extracts all bounding boxes `(x_min, y_min, x_max, y_max)` and text strings on the canvas.
> 3. **Fuzzy Matching**: Levenshtein distance compares EasyOCR words to Gemini PII strings (similarity threshold $\ge 0.85$).
> 4. **Dynamic Padding**: A $10\% + 2\text{px}$ padding is added to box bounds to prevent edge leakage.
> 5. **Heavy Blurring**: ROI is downsampled to 10% resolution (physically destroying text details), resized back up, and smoothed with a Gaussian blur.

### Q13: How does high-resolution PDF rendering work?
> **Answer:**  
> Default PyMuPDF (`fitz`) PDF page rendering exports at 72 DPI, where small text appears pixelated and unreadable to OCR.  
> We solve this in `pdf_utils.py` by applying a zoom matrix `zoom = 300 / 72 = 4.166x` to render pages at **300 DPI**. This produces razor-sharp image canvas conversions before forwarding each page to `process_image`.

### Q14: How does Audio PII Masking work?
> **Answer:**  
> 1. Gemini transcribes the audio file and returns a JSON array of sensitive words along with precise `start_time` and `end_time` timestamps (e.g., `00:01:12` to `00:01:14`).
> 2. `pydub` loads the audio waveform into memory.
> 3. `pydub.generators.Sine(300)` generates a 300 Hz sine-wave beep tone.
> 4. The audio segment between `start_ms` and `end_ms` is sliced out and replaced with the generated beep tone.

### Q15: How does Video PII Masking achieve high FPS performance?
> **Answer:**  
> Sequential frame processing in Python is too slow (e.g., 30 FPS for 1 minute = 1,800 frames).  
> We implemented **parallel thread-pool processing** using Python's `concurrent.futures.ThreadPoolExecutor`:
> 1. OpenCV `VideoCapture` streams frames into an indexed queue.
> 2. Worker threads process batches of frames concurrently running YOLOv8 face detection and OCR frame masking.
> 3. Processed frames are re-assembled in order and re-encoded using OpenCV `VideoWriter` and FFmpeg.

### Q16: How are Microsoft Word (`.docx`) and PowerPoint (`.pptx`) documents masked?
> **Answer:**  
> - **Word (`.docx`)**: We use `python-docx` to iterate through document paragraph XML nodes and table cells. Matched PII text strings are replaced directly in the text node elements while preserving styling.
> - **PowerPoint (`.pptx`)**: We use `python-pptx` to iterate across slides, shape frames, and text frames, substituting matched strings paragraph by paragraph.

### Q17: "Do you use Levenshtein distance for all file formats, including Word (.docx) and PowerPoint (.pptx)?"
> **Answer:**  
> "No, we use Levenshtein distance selectively based on whether OCR is involved:
> 1. **WHERE IT IS USED**: EasyOCR visual text extraction on **Images, PDFs, Video frames, and PowerPoint slide images** (`image_utils.py`, `video_utils.py`). Visual OCR engines often introduce minor recognition typos (e.g., `'123-45-6789'` vs `'I23-45-6789'`). We use `textdistance.Levenshtein()` to fuzzy-match OCR word boxes with Gemini's detected text so minor OCR typos don't cause missed redactions.
> 2. **WHERE IT IS NOT USED**: Digital text in **Word documents (`.docx`)** (`docx_utils.py`), **Plain Text (`.txt`)**, and **Spreadsheets (`.csv`)**. Because text is extracted directly from clean digital XML text nodes in memory (`para.text`), there are no OCR typos. Therefore, `.docx` and `.txt` use exact Python string matching (`para.text.replace(pii_text, replacement)`), which is faster and prevents false-positive fuzzy replacements."

### Q18: How do you scale CSV / Excel spreadsheet masking for 100,000+ rows?
> **Answer:**  
> Passing 100,000 rows to Gemini would exceed LLM token limits and cost thousands of dollars.  
> We use a **Schema Sampling Technique**:
> 1. Pandas loads the dataframe and extracts column headers + a random 15-row sample.
> 2. Gemini inspects only the 15-row sample to identify column-level PII mapping (e.g. Column B = Email).
> 3. Pandas applies vectorized local regex transformations across all 100,000 rows in milliseconds with zero LLM API cost.

### Q19: What text redaction modes are supported for documents?
> **Answer:**  
> 1. **General Replacement**: Replaces sensitive words with `[MASKED]`.
> 2. **Named Replacement**: Replaces words with category labels like `[Full Name]` or `[Credit Card]`.
> 3. **X-Character Mapping**: Replaces each character with `X` (e.g., "John" $\rightarrow$ "XXXX") to preserve line length.

---

## 🔒 Pillar 4: Enterprise Security & Governance

### Q20: How does the Air-Gapped Offline Fallback Engine work?
> **Answer:**  
> Located in `src/services/fallback_engine.py`. If Gemini API fails or if `OFFLINE_MODE=true` is set, requests route to a local Python regex scanner containing compiled patterns for Email, Phone Numbers, SSNs, Credit Cards, IP Addresses, and Dates of Birth, allowing complete air-gapped operation.

### Q21: How does the Automatic File Shredder (TTL Cleaner) enforce zero-retention?
> **Answer:**  
> Located in `src/services/ttl_cleaner.py`. On server startup, an async background task (`asyncio.create_task`) is spawned. Every 60 seconds, it checks file modification times in `uploads/` and `processed/` folders, permanently deleting any file older than `FILE_TTL_SECONDS` (default: 3600s / 1 hour).

### Q22: How does the Audit Ledger & Compliance Exporter work?
> **Answer:**  
> Every request automatically logs `job_id`, `timestamp`, `filename`, `file_hash_sha256`, `pii_categories`, `masking_type`, and `processing_time_ms` into SQLite.  
> The endpoint `GET /api/v1/audit/export` reads this ledger and uses `compliance_reporter.py` to generate downloadable HTML/PDF audit verification certificates for GDPR/HIPAA compliance officers.

### Q23: How is API Key Authentication handled?
> **Answer:**  
> API keys are passed in the `X-API-Key` request header. `auth_middleware.py` hashes the incoming key using SHA-256 and queries the `api_keys` SQLite table to verify active status and role permissions before allowing request execution.

### Q24: How do middleware layers enhance security and tracing?
> **Answer:**  
> `AuditMiddleware` intercepts all HTTP traffic to compute processing latency and inject enterprise security headers (`X-Enterprise-Processing-Time-MS`, `X-Enterprise-Security-Level: AES-256-Local`) into HTTP responses.

### Q25: How do you prevent file collisions when multiple users upload files with the same name?
> **Answer:**  
> Incoming files are renamed on disk with a UUID v4 prefix and epoch timestamp (e.g., `uploads/a1b2c3d4_1719827361_invoice.pdf`). The original filename is stored safely in metadata.

---

## 🚀 Pillar 5: System Design & Production Scaling

### Q26: "What happens if a user uploads a 500-page PDF?"
> **Answer:**  
> Processing 500 pages synchronously risks HTTP timeouts. We handle large files asynchronously:
> 1. Document is split into page batches using `pypdf`.
> 2. Request is submitted to `/api/v1/jobs`, returning a `202 Accepted` response with a `job_id` immediately.
> 3. Frontend polls `/api/v1/jobs/{job_id}` for progress updates.
> 4. Temporary page images are garbage-collected after each batch to keep memory utilization under 512MB.

### Q27: "How would you scale this system to 1,000,000 files/day in production?"
> **Answer:**  
> 1. **Stateless Kubernetes Cluster**: Deploy FastAPI backend as stateless Docker pods on Kubernetes with Horizontal Pod Autoscaling (HPA).
> 2. **Distributed Task Queue**: Replace local job queue with **Celery + Redis / RabbitMQ** workers dedicated to heavy GPU video/OCR processing.
> 3. **Cloud Storage**: Move local disk uploads to **AWS S3 / Google Cloud Storage** with S3 Lifecycle policies for automatic object expiration.
> 4. **Database & Caching**: Move SQLite to **AWS Aurora PostgreSQL** with read-replicas for audit queries, and use Redis for file hash deduplication caching.

### Q28: How do you handle Gemini API Rate Limits (HTTP 429)?
> **Answer:**  
> We wrap GenAI API calls in an exponential backoff retry function (`generate_content_with_retry`). If an HTTP 429 or `resource_exhausted` error occurs, the helper sleeps for `initial_backoff * 2^attempt` seconds up to 5 retries before failing.

### Q29: How do you handle False Positives and False Negatives?
> **Answer:**  
> 1. **Levenshtein Ratio Thresholding**: String similarity must meet or exceed 85% (`ratio >= 0.85`), with strict 100% exact matching enforced for short words ($\le 3$ chars).
> 2. **Human-in-the-Loop Queue (`/preview`)**: Pre-inspection workbench allows operators to visually review detected entities before triggering destructive masking.

### Q30: Why choose a Monorepo architecture over Polyrepo?
> **Answer:**  
> 1. **Atomic Commits**: Frontend and backend API changes are committed together, eliminating breaking contract mismatches.
> 2. **Unified Quality Tooling**: Shared pre-commit hooks (Ruff, Biome, Gitleaks, Semgrep) run across both frontend and backend in a single developer workflow.

---

## 🛠️ Pillar 6: Developer Quality & Operations

### Q31: What static analysis and security scanning tools are integrated?
> **Answer:**  
> - **Gitleaks**: Scans git commits for leaked API keys or secrets.
> - **Ruff**: High-speed Python linter enforcing PEP 8.
> - **Bandit**: Static security analyzer detecting insecure Python code patterns (e.g. `eval`, hardcoded passwords).
> - **Semgrep**: Static analysis checking FastAPI route security.

### Q32: How do you verify build correctness before deployment?
> **Answer:**  
> 1. **Backend**: Python syntax and import validation using `python -m py_compile`.
> 2. **Frontend**: TypeScript type-checking using `tsc --noEmit` and Vite build bundling (`npm run build`).

### Q33: What logging standard is used for troubleshooting?
> **Answer:**  
> We use structured JSON logging with custom trace IDs, capturing timestamps, route names, HTTP status codes, execution latency, and error tracebacks.

---

## 💡 Pillar 7: Quick-Reference Cheat Sheet & Interview Numbers

### Q34: Core Technology Matrix
| Domain | Technology Selected | Key Function |
| :--- | :--- | :--- |
| **Backend API** | FastAPI + Python 3.11 | Async ASGI Web Gateway |
| **Frontend UI** | React 19 + TypeScript + Vite | Enterprise Dashboard SPA |
| **AI LLM Engine** | Google Gemini 2.0 Flash | Multimodal Contextual PII Detection |
| **Computer Vision** | YOLOv8 Nano | Real-Time Biometric Face Blurring |
| **OCR Engine** | EasyOCR / PaddleOCR | Spatial Word Bounding Box Extraction |
| **Database** | SQLite3 (`pii_enterprise.db`) | Local Audit Ledger & Job Tracking |
| **Encryption** | Fernet AES-256 | Storage at Rest Security |

### Q35: Top 10 One-Word Memory Anchors for Interviews
1. **FastAPI**: Async ASGI
2. **Vite**: Instant HMR
3. **Gemini 2.0**: Multimodal Context
4. **YOLOv8**: Single-Pass CNN
5. **EasyOCR**: Bounding Box Localization
6. **Levenshtein**: Selective Fuzzy Matching (OCR Only)
7. **SQLite**: Zero-Config Persistence
8. **Fernet**: AES-256 Storage Security
9. **TTL Cleaner**: Zero Retention Shredding
10. **Pandas**: Vectorized Schema Sampling

### Q36: Key Metrics to Quote in Interviews
- **300 DPI**: High-resolution PyMuPDF page rendering matrix ($300 / 72 = 4.166\times$).
- **85% Similarity Ratio**: Minimum Levenshtein fuzzy match threshold for OCR word alignment.
- **10% + 2px**: Dynamic border padding added around OCR bounding boxes to prevent edge leakage.
- **3600 Seconds**: Default TTL age threshold before background file shredding.
- **200 ms**: Average single-image processing latency.
