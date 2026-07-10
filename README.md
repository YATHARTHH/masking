# PII Detection and Masking System (Full-Stack Monorepo)

An AI-powered, full-stack application designed to automatically detect and mask Personally Identifiable Information (PII) across multiple file formats. The project features a fast and interactive **React + TypeScript + Vite** frontend and a robust **FastAPI** backend leveraging **Google's Gemini 2.0 Flash** model, OCR tools, and face-detection networks (YOLOv8) to redact sensitive data securely.

---

## 📂 Repository Structure

This is a monorepo containing both the frontend user interface and the backend processing engine:

```
pii-masking/
├── LICENSE                          # Project license (MIT)
├── README.md                        # Root developer & system documentation (this file)
│
├── pii-masking-backend-main/        # Python FastAPI Backend
│   ├── src/                         # Backend source code
│   │   └── utils/                   # PII extraction and redacting utilities
│   │       ├── audio_utils.py       # Audio transcription and beep-overlaying
│   │       ├── video_utils.py       # Frame-by-frame parallel video processing
│   │       ├── image_utils.py       # OCR and visual masking (boxes/blur)
│   │       ├── pdf_utils.py         # Multi-page PDF layout conversion
│   │       ├── csv_utils.py         # Tabular data PII identification
│   │       ├── docx_utils.py        # Word document XML text parsing
│   │       └── text_utils.py        # Raw text replacement routines
│   ├── main.py / app.py             # FastAPI entrypoints
│   ├── pyproject.toml / ruff.toml   # Linter and package manager configs
│   ├── yolov8n.pt                   # Pre-trained YOLOv8 weights (face detection)
│   └── requirements.txt             # Python packages manifest
│
└── pii-masking-frontend-master/     # React TypeScript Frontend
    ├── src/
    │   ├── components/              # UI widgets (Navbar, Footer, TempMain)
    │   ├── pages/                   # Views & app routing
    │   │   └── main/Page.tsx        # Dashboard and masking settings workbench
    │   ├── context/                 # State management
    │   └── config.ts                # Endpoint host and base URL definitions
    ├── package.json                 # Node.js manifest
    └── vite.config.ts               # Vite configuration (with Tailwind Integration)
```

---

## ✨ Features

- **Multi-Format Processing**: Full pipeline support for:
  - **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`
  - **Documents**: `.pdf`, `.docx`, `.txt`
  - **Tabular Data**: `.csv`, `.xlsx`
  - **Audio**: `.wav`, `.mp3`, `.m4a`
  - **Video**: `.mp4`, `.avi`
- **AI-Powered Semantic Detection**: Uses **Gemini 2.0 Flash** for state-of-the-art context-aware PII detection (such as names, addresses, credit cards, dates of birth, SSNs, and custom categories).
- **Computer Vision & OCR**: Combining **EasyOCR** or **PaddleOCR** with fuzzy text similarity algorithms to precisely map PII string coordinates inside images and PDFs.
- **Biometric Protection**: Face detection powered by **YOLOv8** to blur faces in pictures and video frames automatically.
- **Privacy Obfuscation Modes**:
  - **Visuals**: Soft Blur, Rectangular opaque overlays, or Solid paint masking.
  - **Documents**: Name-replacement placeholder (e.g., `[Full Name]`), generic replacements (`[MASKED]`), size-preserving overlays, or custom character mapping (e.g., `XXXX`).
  - **Audio**: Automatic word timestamp alignment with beep tone replacement.
  - **Video**: Frame-by-frame parallel rendering and recombination using threading.

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.8+** (for the backend)
- **Node.js 18+** & **npm** (for the frontend)
- A **Google Gemini API Key** (obtainable from [Google AI Studio](https://aistudio.google.com/app/apikey))

---

### 2. Backend Setup & Run

Navigate to the backend directory:
```bash
cd pii-masking-backend-main
```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables:
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Open `.env` and set your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

#### Run the server:
- **Production-like / Default Mode**:
  ```bash
  uvicorn app:app
  ```
- **Development Auto-Reload Mode**:
  ```bash
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- **Verify Backend**:
  Open `http://localhost:8000/docs` in your browser to explore the Swagger interactive API documentation.

---

### 3. Frontend Setup & Run

Navigate to the frontend directory:
```bash
cd ../pii-masking-frontend-master
```

#### Install packages:
```bash
npm install
```

#### Configure Environment Variables:
Create a `.env` file:
```bash
cp .env.example .env
```
Ensure the API endpoint matches the running backend address:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_HOST=localhost:8000
```

#### Run the development server:
```bash
npm run dev
```
Open the printed URL (typically `http://localhost:5173`) in your browser.

---

## 🛠 Supported Formats Reference

| Format Family | Extensions | Processing Method | Masking Output Options |
|:---|:---|:---|:---|
| **Images** | `.png`, `.jpg`, `.jpeg`, `.gif` | OCR text extraction + Gemini + Fuzzy matching + YOLOv8 face detection | Soft Blurring, Rectangular paint boxes |
| **PDF Documents** | `.pdf` | Page-to-image rasterization → visual OCR + text masking pipeline | Soft Blurring, Rectangular paint boxes |
| **Word Docs / Text** | `.docx`, `.txt` | XML/Plain text extraction → Gemini exact string location | Named replacement, General replacement, X-masking |
| **Spreadsheets** | `.csv`, `.xlsx` | Cell-by-cell tabular scanning | Masked fields preserving shapes and headers |
| **Audio** | `.wav`, `.mp3`, `.m4a` | Gemini audio transcription with timestamps | Beep tone overlays |
| **Video** | `.mp4`, `.avi` | Thread-pool frame extraction → YOLOv8 + OCR frame masking → Re-encoding | Soft Blurring, Rectangular paint boxes |

---

## 🔒 Security & Optimization Guidelines

1. **API Keys Security**: Never commit `.env` or configurations containing raw keys. Use secrets management or system environment variables in staging/production.
2. **CORS Configuration**: By default, the FastAPI server accepts requests from all origins (`"*"`). Update the middleware configuration in `main.py` to allow only your frontend origin in production:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       ...
   )
   ```
3. **Execution Optimization**:
   - For high-volume file processing (e.g., long videos), increase or configure `max_workers` in `video_utils.py` depending on target server CPU/GPU resources.
   - Adjust `similarity_threshold` in `image_utils.py` if the OCR fuzzy matching is missing slight variations or mismatching non-sensitive terms.

---

## 🔄 Git Hooks & Developer Quality checks

Both directories are pre-packaged with linting, scanning, and code-cleanliness pre-commit checks:
- **Pre-commit actions**: Gitleaks (secrets scanner), Ruff (Python style guide check), Biome, and Semgrep.

### Initialize development hooks:
Run the following script **once** to register the pre-commit environment:
- **Windows (PowerShell)**:
  ```powershell
  .\tasks\mise-install.cmd
  ```
- **macOS / Linux**:
  ```bash
  bash tasks/mise-install.sh
  ```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///LICENSE) file at the root for details.
