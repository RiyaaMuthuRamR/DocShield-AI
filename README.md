# DocShield AI

**AI-assisted fake identity and document screening prototype**

DocShield AI combines document-image upload, OCR field extraction, a heuristic Error Level Analysis (ELA) signal, basic QR payload decoding, cross-document field consistency checks, a risk summary, and PDF report generation.

> **Important:** This is a prototype, not an official document-authentication service. OCR can be wrong; ELA is not a calibrated probability and cannot prove forgery; a decoded QR payload is not proof of a valid signature; and missing image metadata does not prove fraud. All results require human review. Do not upload real personal identity documents to a public repository or use this score as the sole basis for a decision.

## Project structure

```text
DocShield-AI/
├── ai_models/             # ELA evidence, OCR/MRZ and QR utilities
├── backend/
│   ├── app.py             # FastAPI application
│   ├── routes/             # API endpoints
│   ├── services/           # OCR, ELA, identity, risk, PDF and storage logic
│   ├── uploads/            # Runtime uploads and heatmaps (git-ignored)
│   └── reports/            # Generated PDFs (git-ignored)
├── datasets/               # Sample images; verify they are synthetic before publishing
├── docs/
├── frontend/               # React + Vite interface
├── tests/
├── requirements.txt
└── .gitignore
```

## Requirements

- Python 3.10–3.12 recommended for the current EasyOCR/PyTorch dependency stack.
- Node.js 20+ and npm.
- Internet access on the first EasyOCR run may be needed to download its model weights.
- The separate advanced MRZ utility under `ai_models/ocr/ocr_engine.py` uses Tesseract. Install the Tesseract executable and add it to `PATH` (or set `TESSERACT_CMD`) if you want to call that utility directly. The main `/api/analyze` endpoint uses EasyOCR and does not require Tesseract.

## Run the backend (Windows PowerShell)

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` to test the API and `http://127.0.0.1:8000/health` to check server status.

If PowerShell blocks activation, run the commands using the venv interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

## Run the frontend

Open a second terminal at the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). The frontend calls `http://127.0.0.1:8000/api` by default. To use another backend URL, create `frontend/.env.local` with:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/upload` | Validate and save an image |
| POST | `/api/analyze` | Combined OCR, ELA, QR, metadata and risk screening |
| POST | `/api/ocr` | OCR and basic field parsing |
| POST | `/api/forgery` | ELA heatmap and heuristic indicator |
| POST | `/api/identity-check` | Compare fields from two documents |
| POST | `/api/risk-score` | Calculate a screening score from supplied signals |
| POST | `/api/report` | Generate a PDF report |
| GET | `/api/report/download/{report_id}` | Download a generated report |
| POST | `/api/face-verify` | Explicitly returns 501 until a real face-verification model is integrated |

## What is implemented vs. not implemented

- **Implemented in this MVP:** image validation/upload, EasyOCR-based text extraction and basic field parsing, ELA visualization/indicator, basic QR payload decoding, field-consistency comparison, heuristic risk score, PDF report download, React interface.
- **Not implemented as production verification:** official registry checks, cryptographic QR/signature validation, calibrated forgery probability, live face matching/liveness, blacklist/expiry checks, database-backed audit trail, authentication/authorization. The face route intentionally returns `501 Not Implemented` instead of pretending to verify a face.
- The advanced MRZ parser/OCR files are retained under `ai_models/`, but they are not yet part of the main `/api/analyze` request pipeline.

## Testing

```powershell
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests exercise API health, identity consistency, risk scoring, image screening fallback and report generation. Full OCR success must also be tested locally after installing EasyOCR and its model weights.
