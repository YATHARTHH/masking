# PII Shield Enterprise - Master Interview Q&A Guide

This is the ultimate, end-to-end technical reference and interview guide for the **PII Shield Enterprise System**. It covers all **45 deep-dive questions**, system design decisions, technology stack justifications, file-processing pipelines, security architectures, ML/DL model deep dives, local/cloud deployment options, and scenario-based interview responses.

---

## 📑 Table of Contents
1. [Pillar 1: Project Overview & Business Value (Q1 - Q4)](#pillar-1-project-overview--business-value)
2. [Pillar 2: Technology Stack Justifications (Q5 - Q11)](#pillar-2-technology-stack-justifications)
3. [Pillar 3: Per-Format Processing Pipelines (Q12 - Q24)](#pillar-3-per-format-processing-pipelines)
4. [Pillar 4: Enterprise Security & Governance (Q25 - Q30)](#pillar-4-enterprise-security--governance)
5. [Pillar 5: System Design & Production Scaling (Q31 - Q38)](#pillar-5-system-design--production-scaling)
6. [Pillar 6: Developer Quality & Operations (Q40 - Q42)](#pillar-6-developer-quality--operations)
7. [Pillar 7: Quick-Reference Cheat Sheet & Interview Numbers (Q43 - Q45)](#pillar-7-quick-reference-cheat-sheet--interview-numbers)

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

### Q18: "Why render PDF pages as 300 DPI images instead of parsing raw text elements from PDF text layers?"
> **Answer:**  
> "Extracting raw PDF text streams fails on scanned PDFs, flattened forms, receipts, or PDFs with corrupted font glyph maps. Rasterizing PDF pages into 300 DPI images (`fitz.Matrix(300/72, 300/72)`) creates a unified visual canvas that handles digital PDFs, scanned documents, and image-based PDFs identically with high OCR accuracy."

### Q19: "Why use native `python-docx` for Word (.docx) files instead of converting to PDF and applying visual OCR?"
> **Answer:**  
> "Converting `.docx` to PDF and applying OCR is slow, resource-heavy, and distorts document formatting and fonts. `python-docx` allows us to manipulate the underlying XML DOM directly, performing instant, non-destructive text node replacement while preserving paragraphs, tables, and document styling."

### Q20: "How do you handle multi-lingual PII (e.g. Hindi, Spanish, Arabic) across OCR and LLM engines?"
> **Answer:**  
> "EasyOCR is instantiated with multi-lingual language models (`reader = easyocr.Reader(['en', 'hi'])`), and Gemini 2.0 Flash is natively trained on multi-lingual prompt comprehension. Gemini identifies the exact unicode characters in any script, and EasyOCR recognizes multi-script word boundaries on the image canvas."

### Q21: "How does audio timestamp matching prevent spoken word edge fragments from peeking out around beeps?"
> **Answer:**  
> "Gemini returns exact `start_time` and `end_time` timestamps. In `audio_utils.py`, we convert timestamps to milliseconds and apply a **100ms safety padding buffer** on both ends (`start_ms - 100`, `end_ms + 100`) before slicing the `pydub` audio waveform, guaranteeing that word edges are fully muted."

### Q22: "Why combine downsampling (10% scale) with Gaussian blur instead of applying Gaussian blur alone?"
> **Answer:**  
> "Standard Gaussian blurs can sometimes be mathematically reversed using deconvolution algorithms if the blur kernel radius is known. Downsampling the Region of Interest (ROI) to 10% resolution physically destroys 90% of high-frequency pixel data. Resizing it back up and applying Gaussian smoothing creates an un-recoverable pixelated blur."

### Q23: How do you scale CSV / Excel spreadsheet masking for 100,000+ rows?
> **Answer:**  
> Passing 100,000 rows to Gemini would exceed LLM token limits and cost thousands of dollars.  
> We use a **Schema Sampling Technique**:
> 1. Pandas loads the dataframe and extracts column headers + a random 15-row sample.
> 2. Gemini inspects only the 15-row sample to identify column-level PII mapping (e.g. Column B = Email).
> 3. Pandas applies vectorized local regex transformations across all 100,000 rows in milliseconds with zero LLM API cost.

### Q24: What text redaction modes are supported for documents?
> **Answer:**  
> 1. **General Replacement**: Replaces sensitive words with `[MASKED]`.
> 2. **Named Replacement**: Replaces words with category labels like `[Full Name]` or `[Credit Card]`.
> 3. **X-Character Mapping**: Replaces each character with `X` (e.g., "John" $\rightarrow$ "XXXX") to preserve line length.

---

## 🔒 Pillar 4: Enterprise Security & Governance

### Q25: How does the Air-Gapped Offline Fallback Engine work?
> **Answer:**  
> Located in `src/services/fallback_engine.py`. If Gemini API fails or if `OFFLINE_MODE=true` is set, requests route to a local Python regex scanner containing compiled patterns for Email, Phone Numbers, SSNs, Credit Cards, IP Addresses, and Dates of Birth, allowing complete air-gapped operation.

### Q26: How does the Automatic File Shredder (TTL Cleaner) enforce zero-retention?
> **Answer:**  
> Located in `src/services/ttl_cleaner.py`. On server startup, an async background task (`asyncio.create_task`) is spawned. Every 60 seconds, it checks file modification times in `uploads/` and `processed/` folders, permanently deleting any file older than `FILE_TTL_SECONDS` (default: 3600s / 1 hour).

### Q27: How does the Audit Ledger & Compliance Exporter work?
> **Answer:**  
> Every request automatically logs `job_id`, `timestamp`, `filename`, `file_hash_sha256`, `pii_categories`, `masking_type`, and `processing_time_ms` into SQLite.  
> The endpoint `GET /api/v1/audit/export` reads this ledger and uses `compliance_reporter.py` to generate downloadable HTML/PDF audit verification certificates for GDPR/HIPAA compliance officers.

### Q28: How is API Key Authentication handled?
> **Answer:**  
> API keys are passed in the `X-API-Key` request header. `auth_middleware.py` hashes the incoming key using SHA-256 and queries the `api_keys` SQLite table to verify active status and role permissions before allowing request execution.

### Q29: How do middleware layers enhance security and tracing?
> **Answer:**  
> `AuditMiddleware` intercepts all HTTP traffic to compute processing latency and inject enterprise security headers (`X-Enterprise-Processing-Time-MS`, `X-Enterprise-Security-Level: AES-256-Local`) into HTTP responses.

### Q30: How do you prevent file collisions when multiple users upload files with the same name?
> **Answer:**  
> Incoming files are renamed on disk with a UUID v4 prefix and epoch timestamp (e.g., `uploads/a1b2c3d4_1719827361_invoice.pdf`). The original filename is stored safely in metadata.

---

## 🚀 Pillar 5: System Design & Production Scaling

### Q31: "What happens if a user uploads a 500-page PDF?"
> **Answer:**  
> Processing 500 pages synchronously risks HTTP timeouts. We handle large files asynchronously:
> 1. Document is split into page batches using `pypdf`.
> 2. Request is submitted to `/api/v1/jobs`, returning a `202 Accepted` response with a `job_id` immediately.
> 3. Frontend polls `/api/v1/jobs/{job_id}` for progress updates.
> 4. Temporary page images are garbage-collected after each batch to keep memory utilization under 512MB.

### Q32: "How would you scale this system to 1,000,000 files/day in production?"
> **Answer:**  
> 1. **Stateless Kubernetes Cluster**: Deploy FastAPI backend as stateless Docker pods on Kubernetes with Horizontal Pod Autoscaling (HPA).
> 2. **Distributed Task Queue**: Replace local job queue with **Celery + Redis / RabbitMQ** workers dedicated to heavy GPU video/OCR processing.
> 3. **Cloud Storage**: Move local disk uploads to **AWS S3 / Google Cloud Storage** with S3 Lifecycle policies for automatic object expiration.
> 4. **Database & Caching**: Move SQLite to **AWS Aurora PostgreSQL** with read-replicas for audit queries, and use Redis for file hash deduplication caching.

### Q33: "Walk me through the Local / On-Premise Deployment Stack for this system."
> **Answer:**  
> "When deployed locally — on a developer workstation, on-premise server, or an air-gapped edge device — the system uses the following stack:
>
> #### 🏠 Local / On-Premise / Edge Deployment Stack
>
> | Service | Technology | Why We Use It |
> | :--- | :--- | :--- |
> | **Web Application Server** | FastAPI + Uvicorn | Uvicorn is a lightning-fast ASGI server. FastAPI is async-native so it handles concurrent file uploads without blocking. |
> | **Frontend SPA Server** | Vite + Node.js | Vite gives instant HMR during dev. In production, `npm run build` compiles static assets served by any HTTP server. |
> | **LLM / AI Engine** | Google Gemini 2.0 Flash API | Contextual semantic understanding of PII across text, images, audio — something pure regex cannot do. |
> | **Face Detection Model** | YOLOv8 Nano (`yolov8n.pt`) | Runs fully locally, single-pass CNN, no cloud dependency, very fast even on CPU. |
> | **OCR Engine** | EasyOCR (PyTorch) | Produces spatial pixel bounding boxes for every word, enabling coordinate-level image redaction. |
> | **Database** | SQLite3 (`pii_enterprise.db`) | Zero-configuration, file-based, ACID-compliant, no external server needed. |
> | **Encryption** | Fernet AES-256 (`cryptography` library) | Ensures any file saved to disk is encrypted at rest. Keys are auto-generated and stored in `.env`. |
> | **Background TTL Shredder** | Python `asyncio` loop | Continuously watches upload folders and shreds files older than 1 hour, enforcing GDPR zero-retention. |
> | **Offline Fallback Engine** | Local compiled regex patterns | If Gemini API is unreachable (no internet), this catches standard PII patterns (Email, SSN, Phone, Credit Card, etc.) |
> | **Document Tools** | PyMuPDF, python-docx, python-pptx, pydub, OpenCV | Each handles one file format family: PDF rendering, Word XML, PPT XML, audio waveforms, and image/video frames. |

### Q34: "Walk me through the full AWS Cloud Production Deployment Stack."
> **Answer:**  
> "On AWS, we break the system into clearly separated managed services, each solving a specific production concern:
>
> #### ☁️ AWS Production Cloud Stack
>
> **1. Compute — AWS EKS (Elastic Kubernetes Service)**
> - **What**: The FastAPI backend runs as Docker containers on Kubernetes pods.
> - **Why EKS**: Kubernetes auto-scales pods horizontally (HPA) when upload queue depth exceeds thresholds. EKS manages the Kubernetes control plane automatically, removing maintenance overhead.
> - **GPU Workers**: Heavy tasks (video processing, OCR, YOLOv8 inference) run on dedicated `g4dn.xlarge` GPU worker nodes (NVIDIA T4 GPUs), giving CUDA acceleration.
>
> **2. Frontend — AWS S3 + CloudFront CDN**
> - **What**: The compiled React app (`npm run build` output) is uploaded as static HTML/JS/CSS assets to an S3 bucket configured as a static website.
> - **Why S3 + CloudFront**: CloudFront caches the static assets at 450+ edge locations globally, so users load the UI in under 50ms regardless of location. S3 provides 99.999999999% (11-nines) durability for static assets.
>
> **3. API Gateway & Traffic Control — AWS ALB + WAF**
> - **What**: AWS Application Load Balancer (ALB) sits in front of the Kubernetes cluster, terminating TLS 1.3, routing `/api/v1/` traffic to backend pods, and distributing load.
> - **Why ALB + WAF**: AWS WAF blocks DDoS traffic, SQL injection, and rate-limit abusive API callers before they hit your FastAPI app. Much cheaper than absorbing and handling bad traffic inside the app.
>
> **4. Task Queue — Celery + Amazon SQS / Redis (ElastiCache)**
> - **What**: Heavy async processing jobs (multi-page PDFs, long videos) are offloaded from the FastAPI request thread into Celery worker queues backed by Amazon SQS or ElastiCache Redis.
> - **Why Celery + SQS**: Decouples file upload acceptance from actual processing. A 500-page PDF returns `202 Accepted` in 200ms; the heavy rendering happens asynchronously. SQS is fully managed and handles burst spikes automatically.
>
> **5. Object Storage — AWS S3 with Lifecycle Rules**
> - **What**: Replaces local `uploads/` and `processed/` disk directories. All raw uploaded files and redacted output files go into S3 buckets.
> - **Why S3 Lifecycle Rules**: S3 Lifecycle Expiration Policy automatically deletes objects older than 1 hour, enforcing GDPR zero-retention at the cloud infrastructure level — far more reliable than a Python background loop.
>
> **6. Database — AWS Aurora PostgreSQL (Multi-AZ)**
> - **What**: Replaces SQLite with a fully managed, distributed PostgreSQL cluster. Stores audit logs, job queue state, and API keys.
> - **Why Aurora**: Aurora PostgreSQL supports up to 15 read replicas, handles millions of audit log writes per day, and provides automatic failover (Multi-AZ) with 99.99% SLA uptime — impossible with SQLite.
>
> **7. Caching — AWS ElastiCache (Redis)**
> - **What**: Caches API key lookups (to avoid hitting the DB on every request), file SHA-256 hash deduplication checks, and job state polling results.
> - **Why Redis**: Sub-millisecond in-memory lookups. API key validation on every request would destroy DB performance at scale without a cache.
>
> **8. Secrets & Config — AWS Secrets Manager + Parameter Store**
> - **What**: Stores the Gemini API key, DB credentials, Fernet encryption key, and feature flags.
> - **Why Secrets Manager**: Never commit secrets to `.env` files in production. Secrets Manager rotates keys automatically and integrates natively with EKS service accounts via IAM Roles for Service Accounts (IRSA).
>
> **9. Observability — CloudWatch + Prometheus + Grafana**
> - **What**: CloudWatch collects container logs and AWS infra metrics. Prometheus scrapes FastAPI app metrics (request count, latency histograms). Grafana dashboards visualize processing throughput, GPU utilization, and error rates.
> - **Why Prometheus + Grafana**: CloudWatch is great for AWS infra metrics, but Prometheus lets you define custom business-level metrics (e.g. PII_categories_detected_per_minute), which CloudWatch alone cannot do.

---

### Q35: "Walk me through the full GCP Cloud Production Deployment Stack — and how it differs from AWS."
> **Answer:**  
> "GCP is a strong alternative, especially if you are already using Gemini API (Google Cloud AI APIs integrate natively). Here is the equivalent GCP stack:
>
> #### ☁️ GCP Production Cloud Stack
>
> **1. Compute — GCP GKE (Google Kubernetes Engine)**
> - **What**: Same concept as EKS, but GCP GKE has Autopilot Mode which auto-manages node provisioning — you only pay per pod CPU/memory, not for idle nodes.
> - **Why GKE over EKS**: GKE Autopilot is cheaper and simpler for teams that don't want to manage node pools. GKE also has native Gemini AI integration and lower network egress costs when calling Vertex AI / Gemini API from within GCP.
>
> **2. Frontend — GCS Static Hosting + Cloud CDN**
> - **What**: React app static assets uploaded to a Google Cloud Storage (GCS) bucket with static website serving enabled, fronted by Cloud CDN.
> - **Why GCS + Cloud CDN**: Same principle as S3 + CloudFront. Cloud CDN caches static content at Google's global edge PoPs (Points of Presence). Slightly simpler IAM setup than S3 for teams already on GCP.
>
> **3. API Gateway & Traffic — Cloud Load Balancing + Cloud Armor**
> - **What**: GCP Cloud Load Balancing handles TLS termination and distributes API traffic across GKE pods. Cloud Armor is GCP's equivalent of AWS WAF — blocking DDoS and bot traffic.
> - **Why Cloud Armor**: Integrates directly with GCP Load Balancer without extra configuration overhead. Also supports ML-based adaptive DDoS protection (Adaptive Protection feature).
>
> **4. Task Queue — Celery + Google Cloud Pub/Sub or Memorystore Redis**
> - **What**: Cloud Pub/Sub is GCP's fully managed message broker (equivalent of AWS SQS). Memorystore is managed Redis.
> - **Why Pub/Sub**: Better suited for very high-volume fan-out messaging and event-driven architectures. Pub/Sub guarantees at-least-once delivery and handles millions of messages per second without provisioning.
>
> **5. Object Storage — Google Cloud Storage (GCS) with Object Lifecycle Rules**
> - **What**: GCS replaces local disk storage. Lifecycle policies auto-delete objects after TTL (e.g., 1 hour).
> - **Why GCS**: If using Vertex AI / Gemini API on GCP, data transfer between GCS and Gemini API is free within the same region — no egress charges. With AWS S3 + Gemini API calls, you pay for outbound data transfer.
>
> **6. Database — Cloud SQL for PostgreSQL or Cloud Spanner**
> - **What**: Cloud SQL is GCP's managed PostgreSQL (equivalent to Aurora). Cloud Spanner is used for globally distributed, horizontally scalable relational workloads.
> - **Why Cloud SQL vs Spanner**: For audit logs at moderate scale (< 1B rows), Cloud SQL is sufficient and cheaper. Cloud Spanner is for massive multi-region globally consistent workloads.
>
> **7. Secrets — GCP Secret Manager**
> - **What**: Stores Gemini API key, DB credentials, encryption keys — accessed by GKE pods via Workload Identity.
> - **Why GCP over AWS Secrets Manager**: GCP Secret Manager has a slightly simpler IAM binding model via Workload Identity, and is better integrated with Vertex AI service accounts natively.
>
> **8. Observability — Cloud Monitoring + Cloud Logging + Managed Prometheus**
> - **What**: Cloud Monitoring (formerly Stackdriver) collects infra metrics. Cloud Logging stores structured JSON logs. GKE natively integrates with Google Cloud Managed Service for Prometheus.
> - **Why**: One-click integration — no agents to install on GKE nodes. Cloud Logging is automatically fed from container stdout, so your FastAPI JSON logs appear instantly without configuration.
>
> #### 🔑 AWS vs GCP: Key Decision Factors
> | Factor | Choose AWS | Choose GCP |
> | :--- | :--- | :--- |
> | **LLM/AI Integration** | Use Bedrock (Claude, Titan) | ✅ Use Gemini API natively — lower latency & cost |
> | **Kubernetes Management** | EKS (more control) | ✅ GKE Autopilot (simpler, cheaper for small teams) |
> | **Message Queue** | SQS (simpler) | Pub/Sub (better for high fan-out event streams) |
> | **Storage Egress Cost** | S3 (higher egress fees) | ✅ GCS (free egress within GCP for AI calls) |
> | **Market Share** | ✅ Largest ecosystem, more 3rd-party tooling | Growing fast, strong AI-native ecosystem |
> | **Database** | Aurora PostgreSQL | Cloud SQL / Cloud Spanner |

---

### Q36: "What ML and DL (Machine Learning / Deep Learning) models are used in this system, and how does each one work?"
> **Answer:**  
> "The system uses three distinct AI/ML/DL models, each serving a completely different purpose:
>
> #### 🧠 Model 1: Google Gemini 2.0 Flash — Large Language Model (LLM / Foundation Model)
> - **Type**: Transformer-based Large Language Model (LLM) + Multimodal Vision-Language Model (VLM).
> - **Architecture**: Built on Google DeepMind's Gemini architecture — a decoder-only transformer with a 1M+ token context window and multimodal embeddings for text, image, audio, and video frames.
> - **What It Does Here**: Receives file content (text, base64 image, or audio bytes) and performs **semantic contextual PII detection**. It understands context — for example, it can tell that the number `345-678-9012` is a phone number in one sentence and a serial number in another sentence. Pure regex cannot do this.
> - **Why Flash (not Pro)**: Gemini 2.0 Flash is optimized for **speed and cost** — it processes 5x more requests per second at ~10x lower cost than Gemini Pro, while retaining 90%+ of accuracy for structured extraction tasks like PII tagging.
> - **Training**: Trained by Google on multi-lingual, multimodal web-scale datasets using Reinforcement Learning from Human Feedback (RLHF). We do NOT fine-tune it — we use prompt engineering with structured JSON output format instructions.
> - **Key Limitation**: Cannot return pixel-level bounding box coordinates for image text (only semantic understanding). This is why we pair it with EasyOCR for spatial localization.
>
> #### 👁️ Model 2: YOLOv8 Nano — Real-Time Object Detection CNN (Computer Vision / Deep Learning)
> - **Type**: Convolutional Neural Network (CNN) — Single-Stage Object Detector.
> - **Architecture**: YOLOv8 Nano (`yolov8n.pt`) is the smallest variant of the You Only Look Once v8 architecture by Ultralytics. It processes the full image in a **single forward pass** through convolutional layers, outputting bounding boxes `(x, y, w, h)` + class confidence scores in one shot.
> - **What It Does Here**: Detects human faces in images and video frames. For every detected face bounding box with confidence $\ge 0.5$, we apply a heavy $(99, 99)$ Gaussian blur or solid paint-box to permanently obscure biometric identity.
> - **Why YOLOv8 over alternatives**:
>   - **vs OpenCV Haar Cascades**: YOLOv8 is 10x more accurate, handles partial occlusion, rotated faces, and motion blur.
>   - **vs MediaPipe Face Mesh**: MediaPipe requires landmarks; YOLO provides bounding boxes directly — simpler for blurring.
>   - **vs AWS Rekognition**: Keeps all biometric processing fully local, no biometric data ever leaves the machine (critical for HIPAA compliance).
> - **Training**: Trained on COCO dataset (Common Objects in Context) with 80 object classes. The model uses **anchor-free detection heads** and **C2f (Cross Stage Partial with Feature hierarchy fusion)** blocks.
> - **Runtime**: Runs on CPU via PyTorch. CUDA GPU is supported if `torch` is installed with CUDA — dramatically speeds up video processing.
>
> #### 🔤 Model 3: EasyOCR — OCR Neural Network (CRNN — Optical Character Recognition)
> - **Type**: Deep Learning OCR — Convolutional Recurrent Neural Network (CRNN) with CTC (Connectionist Temporal Classification) decoder.
> - **Architecture**:
>   - **Stage 1 — Text Region Detection**: A CRAFT (Character Region Awareness For Text detection) model locates text regions on the image canvas and outputs word bounding boxes `(x_min, y_min, x_max, y_max)`.
>   - **Stage 2 — Text Recognition**: A CRNN reads each detected text region and converts pixels into character sequences. ResNet CNN extracts visual features, a BiLSTM (Bidirectional LSTM) handles sequential character context, and a CTC decoder maps the sequence to output text.
> - **What It Does Here**: Given an image, EasyOCR returns a list of `(bounding_box, text_string, confidence_score)` tuples for every word on the canvas. We use the bounding boxes to pinpoint exactly where in the image a PII word physically appears so we can blur that specific pixel region.
> - **Why EasyOCR over alternatives**:
>   - **vs Tesseract OCR**: EasyOCR is 15-20% more accurate on curved, low-contrast, or stylized text. Tesseract is legacy C++ software not GPU-acceleratable.
>   - **vs PaddleOCR**: Roughly equivalent accuracy. EasyOCR has simpler Python API; PaddleOCR is slightly faster. We support both.
>   - **vs Google Cloud Vision OCR (API)**: Cloud Vision is more accurate but costs ~$1.50 per 1,000 images. EasyOCR is free, local, and processes 200ms/image on CPU.
> - **Multi-Language**: EasyOCR supports 80+ languages via different model weights (`easyocr.Reader(['en', 'hi', 'ar'])`).
>
> #### 🔗 How All 3 Models Work Together (Example: Image with ID Card)
> ```
> Step 1 → Gemini 2.0 Flash reads the image and returns:
>            ["John Smith", "123-45-6789", "john@email.com"]
>
> Step 2 → EasyOCR scans the image and returns bounding boxes:
>            [(box1, "John"), (box2, "Smith"), (box3, "123-45-6789"), ...]
>
> Step 3 → Levenshtein fuzzy match pairs Gemini strings with EasyOCR boxes:
>            "John Smith" → box1 + box2 (similarity ratio 1.0)
>            "123-45-6789" → box3 (similarity ratio 0.97 — minor OCR typo tolerated)
>
> Step 4 → YOLOv8 separately detects face bounding boxes → Gaussian blur applied.
>
> Step 5 → All matched text boxes are heavy-blurred at pixel level → Output image saved.
> ```

### Q39: How do you handle Gemini API Rate Limits (HTTP 429)?
> **Answer:**  
> We wrap GenAI API calls in an exponential backoff retry function (`generate_content_with_retry`). If an HTTP 429 or `resource_exhausted` error occurs, the helper sleeps for `initial_backoff * 2^attempt` seconds up to 5 retries before failing.

### Q37: How do you handle False Positives and False Negatives?
> **Answer:**  
> 1. **Levenshtein Ratio Thresholding**: String similarity must meet or exceed 85% (`ratio >= 0.85`), with strict 100% exact matching enforced for short words ($\le 3$ chars).
> 2. **Human-in-the-Loop Queue (`/preview`)**: Pre-inspection workbench allows operators to visually review detected entities before triggering destructive masking.

### Q38: Why choose a Monorepo architecture over Polyrepo?
> **Answer:**  
> 1. **Atomic Commits**: Frontend and backend API changes are committed together, eliminating breaking contract mismatches.
> 2. **Unified Quality Tooling**: Shared pre-commit hooks (Ruff, Biome, Gitleaks, Semgrep) run across both frontend and backend in a single developer workflow.

---

## 🛠️ Pillar 6: Developer Quality & Operations

### Q40: What static analysis and security scanning tools are integrated?
> **Answer:**  
> - **Gitleaks**: Scans git commits for leaked API keys or secrets.
> - **Ruff**: High-speed Python linter enforcing PEP 8.
> - **Bandit**: Static security analyzer detecting insecure Python code patterns (e.g. `eval`, hardcoded passwords).
> - **Semgrep**: Static analysis checking FastAPI route security.

### Q41: How do you verify build correctness before deployment?
> **Answer:**  
> 1. **Backend**: Python syntax and import validation using `python -m py_compile`.
> 2. **Frontend**: TypeScript type-checking using `tsc --noEmit` and Vite build bundling (`npm run build`).

### Q42: What logging standard is used for troubleshooting?
> **Answer:**  
> We use structured JSON logging with custom trace IDs, capturing timestamps, route names, HTTP status codes, execution latency, and error tracebacks.

---

## 💡 Pillar 7: Quick-Reference Cheat Sheet & Interview Numbers

### Q43: Core Technology Matrix
| Domain | Technology Selected | Key Function |
| :--- | :--- | :--- |
| **Backend API** | FastAPI + Python 3.11 | Async ASGI Web Gateway |
| **Frontend UI** | React 19 + TypeScript + Vite | Enterprise Dashboard SPA |
| **AI LLM Engine** | Google Gemini 2.0 Flash | Multimodal Contextual PII Detection |
| **Computer Vision** | YOLOv8 Nano | Real-Time Biometric Face Blurring |
| **OCR Engine** | EasyOCR / PaddleOCR | Spatial Word Bounding Box Extraction |
| **Database** | SQLite3 (`pii_enterprise.db`) | Local Audit Ledger & Job Tracking |
| **Encryption** | Fernet AES-256 | Storage at Rest Security |

### Q44: Top 10 One-Word Memory Anchors for Interviews
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

### Q45: Key Metrics to Quote in Interviews
- **300 DPI**: High-resolution PyMuPDF page rendering matrix ($300 / 72 = 4.166\times$).
- **85% Similarity Ratio**: Minimum Levenshtein fuzzy match threshold for OCR word alignment.
- **10% + 2px**: Dynamic border padding added around OCR bounding boxes to prevent edge leakage.
- **100 ms**: Safety padding buffer added on both ends of audio beep timestamps.
- **3600 Seconds**: Default TTL age threshold before background file shredding.
- **200 ms**: Average single-image processing latency.
