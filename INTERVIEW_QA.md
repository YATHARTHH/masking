# PII Shield Enterprise - Comprehensive Interview Q&A Guide

This guide contains everything you need to confidently answer technical, system design, architectural, and scenario-based interview questions about the **PII Detection & Masking System**.

---

## 🎯 1. Project Overview & Elevator Pitch

### Q1: Can you explain your project in 60 seconds?
> **Answer:**  
> "PII Shield Enterprise is an AI-powered, full-stack monorepo system designed to automatically detect and mask Personally Identifiable Information (PII) across 7 file format families: Images, PDFs, Word docs, PowerPoints, Spreadsheets, Audio files, and Video files.
> 
> On the backend, we use **FastAPI** paired with **Google's Gemini 2.0 Flash** for semantic context detection, **YOLOv8** for real-time computer vision face blurring, and **EasyOCR/PaddleOCR** for coordinate-based visual text masking. 
> 
> On the frontend, we built an interactive dashboard using **React, TypeScript, and Vite** featuring single-file masking, batch processing, a Human-in-the-Loop review queue, a searchable SQLite audit ledger, and automated GDPR/HIPAA compliance report generation. Everything is built with strict privacy controls—including local AES-256 storage encryption at rest and an automated background file shredder."

---

## 🛠️ 2. Technology Stack & Architectural Justifications ("Why did you use...?")

### Q2: Why did you choose FastAPI over Flask or Django?
> **Answer:**  
> 1. **High Asynchronous Latency Performance (ASGI)**: FastAPI is built on Starlette and Pydantic, supporting native `async/await`. This is critical for I/O bound tasks like streaming file uploads, making multi-threaded video frame calls, and querying AI endpoints asynchronously.
> 2. **Automatic Data Validation & Serialization**: Pydantic models automatically validate incoming request parameters and sanitize output data.
> 3. **Interactive Documentation Out of the Box**: Generates OpenAPI (Swagger UI) specs automatically at `/docs`, speeding up backend-frontend contract integration.
> 4. **Lightweight Core**: Unlike Django, which includes heavy ORM/admin boilerplate we didn't need, FastAPI allows us to build a modular, high-throughput microservice.

### Q3: Why React + TypeScript + Vite on the Frontend?
> **Answer:**  
> 1. **Vite**: Provides instant Hot Module Replacement (HMR) and ultra-fast build times powered by `esbuild` under the hood (compared to older Webpack configs).
> 2. **TypeScript**: Provides compile-time type safety across complex data objects like PII bounding boxes, upload states, and audit log items, eliminating runtime `TypeError` crashes.
> 3. **React 19**: Clean component-driven architecture allowing us to reuse custom hooks, UI dropdowns, and navigation elements across 5 distinct enterprise pages.

### Q4: Why Gemini 2.0 Flash instead of Traditional Regex or OpenAI GPT-4?
> **Answer:**  
> - **Over Traditional Regex**: Regex fails on ambiguous context (e.g., distinguishing between a random serial number vs. a credit card number, or identifying a person's name vs. a company name). Gemini 2.0 Flash uses deep LLM semantic comprehension.
> - **Over GPT-4 / Heavy Models**: Gemini 2.0 Flash is significantly faster (lower latency token generation), cost-efficient, supports multimodal inputs (text, image, audio), and offers a 1M+ token context window suitable for long documents.

### Q5: Why YOLOv8 for Face Detection instead of OpenCV Haar Cascades?
> **Answer:**  
> OpenCV Haar Cascades are outdated, highly sensitive to lighting/angles, and produce high false-positive rates. **YOLOv8 (You Only Look Once)** is a state-of-the-art single-pass convolutional neural network (CNN). It detects faces in real-time with extreme precision, even under severe rotation, motion blur, or partial occlusion in video frames.

### Q6: Why SQLite for local database persistence?
> **Answer:**  
> SQLite is zero-configuration, serverless, and self-contained. It allows the enterprise edition of this application to run out-of-the-box on any local developer or edge server without requiring external container orchestrations (like PostgreSQL or MySQL), while still guaranteeing ACID transaction compliance for our audit ledger.

---

## 🏗️ 3. System Design & Core Architecture

### Q7: How does the system mask PII across different file formats?
> **Answer:**  
> Different formats require specialized parsing & masking pipelines:
> 
> | Format | Detection Engine | Redaction / Masking Execution |
> | :--- | :--- | :--- |
> | **PDF / Images** | Gemini + EasyOCR / PaddleOCR | Coordinates (`bbox`) extracted from OCR; soft blur filter or solid paint rectangle drawn onto image canvas via OpenCV/PIL. |
> | **Word (`.docx`) / Text** | Gemini string matching | XML DOM parsed; exact text nodes replaced with placeholders like `[Full Name]` or `XXXX`. |
> | **Audio (`.mp3`/`.wav`)** | Gemini Audio Transcription | Word-level timestamps extracted; audio waveform sliced and replaced with a sine-wave beep tone. |
> | **Video (`.mp4`)** | YOLOv8 + OCR + ThreadPoolExecutor | Video split into frames; parallel worker threads detect and blur faces/text; frames recombined using OpenCV/FFmpeg. |

### Q8: How does Video PII Processing achieve high FPS performance?
> **Answer:**  
> Processing video frame-by-frame sequentially in Python is extremely slow (e.g., 30 FPS for 1 minute = 1,800 images).  
> To solve this, we implemented **parallel thread-pool processing** using Python's `concurrent.futures.ThreadPoolExecutor`. 
> 1. Frames are read into a memory queue.
> 2. Multiple CPU/GPU worker threads process batches of frames simultaneously applying YOLOv8 face detection.
> 3. Processed frames are re-assembled in index order and written back using OpenCV video writer.

### Q9: How do you handle Air-Gapped or Offline environments when the Gemini API is down?
> **Answer:**  
> We implemented an **Air-Gapped Hybrid Fallback Engine** (`src/services/fallback_engine.py`).  
> If the system detects network disconnection or if `OFFLINE_MODE=true` is set, the request seamlessly bypasses Gemini and routes to our local regular expression scanner that detects Emails, SSNs, Phone Numbers, Credit Cards, IP Addresses, and Dates of Birth offline.

### Q10: How does the Automatic File Shredder (TTL Cleaner) work?
> **Answer:**  
> In compliance with GDPR's "Right to Erasure" and zero-retention policies, we created an asynchronous background daemon (`src/services/ttl_cleaner.py`).  
> On FastAPI startup, an `asyncio.create_task()` loop launches. Every 60 seconds, it scans `uploads/` and `processed/` folders, checks file modification timestamps, and permanently deletes any file whose age exceeds `FILE_TTL_SECONDS` (default: 3600s / 1 hour).

---

## 🧪 4. Scenario & Deep-Dive Interview Questions

### Q11: "What happens if a user uploads a 500-page PDF? Won't that cause memory leaks or API timeouts?"
> **Answer:**  
> "Passing a 500-page PDF in a single synchronous HTTP request would risk request timeouts.  
> To handle large documents cleanly:
> 1. We chunk the multi-page PDF into page batches using `pypdf` / `pdf2image`.
> 2. We use our **Asynchronous Job Queue API** (`/api/v1/jobs`), returning a `202 Accepted` response with a `job_id` immediately.
> 3. The frontend polls `/api/v1/jobs/{job_id}` to track progress percentages without blocking the main UI thread.
> 4. Temporary page images are garbage-collected immediately after processing each batch to keep memory utilization under 512MB."

### Q12: "How do you handle False Positives (over-masking) and False Negatives (missing PII)?"
> **Answer:**  
> "We address this at two levels:
> 1. **Automated Confidence Thresholding**: In OCR and fuzzy matching, we set an adjustable similarity threshold (`similarity_threshold = 0.85`). This prevents non-sensitive words that look slightly similar to a detected string from being mistakenly redacted.
> 2. **Human-in-the-Loop (HITL) Review Queue**: For high-risk compliance workflows, we built a dedicated pre-redaction inspection page (`/preview`). Operators can view detected PII items and bounding box coordinates prior to permanent masking, allowing manual override or approval."

### Q13: "How would you scale this application from 100 files/day to 1,000,000 files/day in production?"
> **Answer:**  
> "To scale to 1M files/day, we would transition from local single-node architecture to a cloud-native microservices topology:
> 1. **Stateless Backend Scaling**: Containerize the FastAPI backend with Docker and deploy on Kubernetes (EKS/GKE) behind an ALB with Horizontal Pod Autoscaling (HPA) based on CPU/Queue depth.
> 2. **Distributed Task Queue**: Replace local SQLite job queue with **Celery + Redis / RabbitMQ** workers dedicated to heavy GPU video/OCR processing.
> 3. **Cloud Object Storage**: Replace local disk storage with AWS S3 / Google Cloud Storage featuring S3 Lifecycle Policies for automatic object deletion (TTL).
> 4. **Database & Caching**: Replace SQLite with PostgreSQL (Amazon Aurora) with read-replicas for audit trails, and use Redis for file hash deduplication caching."

### Q14: "How do you guarantee security and prevent data leaks?"
> **Answer:**  
> 1. **Data at Rest**: Local files are encrypted using AES-256 Fernet encryption (`security.py`).
> 2. **Data in Transit**: Enforced TLS/HTTPS encryption on all client-server communication.
> 3. **Zero Secrets in Code**: Environment secrets managed strictly via `.env` files and environment variables, with pre-commit `Gitleaks` hooks actively scanning git commits.
> 4. **Audit Ledger Integrity**: Every processing action generates a cryptographic SHA-256 file fingerprint stored in an immutable audit ledger.

### Q15: "How do you handle CSV/Excel files with 100,000 rows without exceeding LLM token limits?"
> **Answer:**  
> "Sending 100,000 rows to Gemini would exceed context windows and cost thousands of dollars. Instead, we use a **Schema Inspection & Sampling** technique:
> 1. We extract column headers and a random sample of 10-20 representative data rows using Pandas.
> 2. We pass only the sample to Gemini to classify column-level PII types (e.g. Column 3 = SSN).
> 3. Once column mapping is established, we apply Pandas vectorized regex transformations across all 100,000 rows locally in milliseconds with zero LLM API overhead."

### Q16: "What is the difference between OCR Text Extraction and Gemini Vision Detection?"
> **Answer:**  
> - **Gemini Vision**: High-level semantic intelligence. Understands *what* the text means in context (e.g., recognizing that "John Doe" next to "Patient Name" is a PII item). However, Gemini does not return exact pixel bounding box coordinates (`x, y, w, h`).
> - **OCR Engine (EasyOCR)**: Low-level spatial positioning. Returns precise bounding boxes for every word on the canvas, but lacks semantic understanding.
> - **Hybrid Fusion**: We combine both! Gemini identifies the target string values, and EasyOCR locates their exact pixel coordinates on the image canvas.

### Q17: "How do you prevent Levenshtein distance fuzzy matching from blurring wrong words?"
> **Answer:**  
> "Fuzzy matching can cause false positives if two short words share similar letters (e.g., 'Cat' vs 'Bat'). We implement two safety controls:
> 1. **Length-Weighted Ratio**: We require a minimum similarity ratio of 85% (`ratio >= 0.85`), but scale strictness based on string length (strings shorter than 4 characters require 100% exact match).
> 2. **Spatial Bounding Box Padding**: Matches are verified against word boundaries so partial substrings don't trigger accidental redaction of adjacent text."

### Q18: "Why did you choose a Monorepo structure instead of Polyrepo?"
> **Answer:**  
> 1. **Single Source of Truth**: Backend API routes and frontend client interfaces evolve together in atomic commits, eliminating cross-repo version drift.
> 2. **Unified Developer Experience**: Developers can start both services locally with a single script and run unified pre-commit security scans (Ruff, Biome, Gitleaks) across both codebases simultaneously.

### Q19: "What happens if two users upload files with the exact same filename at the exact same time?"
> **Answer:**  
> "To prevent race conditions or file overwrites on disk, incoming files are prefixed with a unique UUID v4 and high-precision epoch timestamp (e.g., `uploads/a1b2c3d4_1719827361_invoice.pdf`). The original filename is preserved strictly in the audit metadata table."

### Q20: "How do you test this system for reliability and performance?"
> **Answer:**  
> 1. **Unit Testing**: Pytest suites covering document extraction parsing routines.
> 2. **Static Security Analysis**: `Bandit` scanning for Python vulnerabilities and `Semgrep` checking API endpoints.
> 3. **Load Verification**: Benchmark testing endpoints under concurrent load to measure thread-pool latency and memory consumption.

---

## 💡 5. Quick Reference Cheat Sheet

| Question Concept | Keyword Answer to Remember |
| :--- | :--- |
| **Backend Framework** | FastAPI (Async ASGI, Pydantic, OpenAPI) |
| **Frontend Framework** | React + TypeScript + Vite (Type Safety, Instant HMR) |
| **Text & Audio AI Engine** | Google Gemini 2.0 Flash (Multimodal, Low Latency, Large Context Window) |
| **Computer Vision Engine** | YOLOv8 (Single-pass CNN real-time face detection) |
| **Local Persistence** | SQLite (Zero-config ACID embedded storage) |
| **Encryption Standard** | AES-256 Fernet Stream Encryption |
| **File Cleanup Daemon** | AsyncIO TTL Cleaner Loop (GDPR Zero Retention) |
| **Tabular Data Scaling** | Pandas Column Sampling + Vectorized Local Masking |
| **Compliance Support** | GDPR, HIPAA, SOC 2 Type II |
