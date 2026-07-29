# PII Shield Enterprise - AI-Powered PII Detection & Masking System

An enterprise-ready, full-stack monorepo application designed to automatically detect and mask Personally Identifiable Information (PII) across multiple file formats (Images, PDFs, Office Documents, Tabular Data, Audio, and Video).

Featuring a modern **React + TypeScript + Vite** frontend and a high-performance **FastAPI** backend leveraging **Google's Gemini 2.0 Flash**, OCR engines (EasyOCR/PaddleOCR), computer vision (YOLOv8 face detection), and local **SQLite audit logging, AES-256 storage encryption, background TTL file shredding, air-gapped regex fallback, and compliance report generation**.

---

## 📂 Repository Structure

```
pii-masking/
├── LICENSE                          # Project license (MIT)
├── README.md                        # Root developer & system documentation (this file)
│
├── pii-masking-backend-main/        # Python FastAPI Enterprise Backend
│   ├── src/
│   │   ├── api/v1/                  # [NEW] Enterprise V1 REST API endpoints
│   │   │   └── router.py            # Analytics, Audit, Batch, Preview, API Key endpoints
│   │   ├── core/                    # [NEW] Core configuration & security modules
│   │   │   ├── config.py            # Enterprise Settings & Feature Flags
│   │   │   └── security.py          # SHA-256 Hashing, AES-256 Encryption, API Keys
│   │   ├── db/                      # [NEW] Local SQLite Database Layer
│   │   │   └── database.py          # SQLite connection manager & query helpers
│   │   ├── middleware/              # [NEW] Middleware layers
│   │   │   ├── audit_middleware.py  # Latency & security headers middleware
│   │   │   └── auth_middleware.py   # API Key authentication dependency
│   │   ├── services/                # [NEW] Enterprise services
│   │   │   ├── compliance_reporter.py # HTML/PDF GDPR & HIPAA compliance report generator
│   │   │   ├── fallback_engine.py   # Air-gapped local regex detection fallback
│   │   │   └── ttl_cleaner.py       # Async background file shredding daemon
│   │   └── utils/                   # Core PII detection and redacting utilities
│   │       ├── audio_utils.py       # Audio transcription and beep-overlaying
│   │       ├── video_utils.py       # Parallel multi-threaded video frame masking
│   │       ├── image_utils.py       # OCR and visual masking (boxes/blur)
│   │       ├── pdf_utils.py         # Multi-page PDF rasterization & masking
│   │       ├── csv_utils.py         # Tabular data PII identification
│   │       ├── docx_utils.py        # Word document XML text parsing
│   │       ├── ppt_utils.py         # PowerPoint shape text parsing
│   │       └── text_utils.py        # Raw text replacement routines
│   ├── main.py                      # FastAPI app entrypoint
│   ├── pii_enterprise.db            # Local SQLite Database (auto-created)
│   └── pyproject.toml / ruff.toml   # Package configs & linters
│
└── pii-masking-frontend-master/     # React TypeScript Frontend
    ├── src/
    │   ├── components/              # UI widgets (Navbar, Footer, TempMain)
    │   ├── pages/                   # Views & App Routing
    │   │   ├── main/Page.tsx        # Interactive Masking Workbench
    │   │   ├── analytics/           # [NEW] Real-time Compliance Analytics Dashboard
    │   │   ├── audit/               # [NEW] Searchable Verification Audit Ledger
    │   │   ├── batch/               # [NEW] Drag & Drop Multi-file Batch Processing
    │   │   └── preview/             # [NEW] Human-In-The-Loop (HITL) Review Queue
    │   ├── config.ts                # Endpoint host and base URL definitions
    │   └── Routes.tsx               # Application routing table
    ├── package.json                 # Node.js manifest
    └── vite.config.ts               # Vite build configuration
```

---

## ✨ System Features

### Core Masking Engine
- **Multi-Format Pipeline**: Support for Images (`.png`, `.jpg`, `.gif`), PDFs (`.pdf`), Word (`.docx`), PowerPoint (`.pptx`), Spreadsheets (`.csv`, `.xlsx`), Audio (`.wav`, `.mp3`), and Video (`.mp4`, `.avi`).
- **AI Semantic Context (Gemini 2.0 Flash)**: Identifies complex PII like names, addresses, credit cards, SSNs, dates of birth, and custom enterprise entities.
- **Biometric Protection (YOLOv8)**: Blurs faces automatically in photos and video frames.
- **Custom Redaction Modes**: Soft Blur, Solid Paint BBoxes, Named Replacement (`[Full Name]`), General Replacement (`[MASKED]`), X-Character Mapping (`XXXX`), and Beep Audio Overlays.

### 🛡️ Enterprise Local Additions
- **Immutable SQLite Audit Ledger**: Automatically logs `job_id`, timestamp, filename, SHA-256 hash, PII categories redacted, masking mode, and execution latency.
- **AES-256 Storage at Rest**: Encrypts temporary file data stored on local disk.
- **Automatic TTL File Shredder**: Background daemon auto-shreds raw uploads and output files older than `FILE_TTL_SECONDS` (default: 1 hour).
- **Air-Gapped Local Fallback**: Regex-based offline detection engine (Email, Phone, SSN, Credit Card, IP Address, DOB) when Gemini API is offline.
- **Compliance Export**: One-click generation of downloadable GDPR / HIPAA / SOC2 verification certificates.
- **Batch Processing Workspace**: Multi-file parallel processing queue with summary outputs.
- **Human-in-the-Loop (HITL) Inspector**: Pre-redaction entity verification queue for compliance officers.

---

## ⚡ Quick Start

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+ & npm**
- **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/app/apikey))

---

### 2. Backend Setup & Run

Navigate to the backend directory:
```bash
cd pii-masking-backend-main
```

#### Run with Virtual Environment:
```bash
# Windows
.venv\Scripts\python.exe -m uvicorn src.main.app --reload --host 0.0.0.0 --port 8000

# macOS / Linux
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
- **Interactive API Documentation**: Open `http://localhost:8000/docs` in your browser.

---

### 3. Frontend Setup & Run

Navigate to the frontend directory:
```bash
cd ../pii-masking-frontend-master
```

#### Run development server:
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -Command "npm run dev"

# macOS / Linux
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🌐 Enterprise V1 API Endpoints Reference

| Endpoint | Method | Description |
|:---|:---|:---|
| `/upload/` | `POST` | Legacy single-file masking endpoint with automatic audit logging |
| `/api/v1/analytics/stats` | `GET` | Retrieve real-time dashboard analytics & PII distribution metrics |
| `/api/v1/audit/logs` | `GET` | Fetch paginated audit ledger records |
| `/api/v1/audit/export` | `GET` | Export downloadable HTML compliance proof report |
| `/api/v1/batch` | `POST` | Process multiple files simultaneously |
| `/api/v1/preview` | `POST` | HITL pre-redaction entity inspection |
| `/api/v1/keys` | `POST` | Generate new API authentication keys |
| `/healthcheck` | `GET` | System health diagnostic endpoint |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///LICENSE) file at the root for details.
