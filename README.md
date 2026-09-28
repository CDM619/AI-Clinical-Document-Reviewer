# AI Clinical Document Reviewer

An educational AI-assisted web application that extracts information from clinical text and documents, then organizes it into a structured review report. It supports digital PDFs, scanned PDFs, and image-based documents.

> **Safety notice:** This is an educational prototype, not a medical device. It does not provide validated diagnoses or treatment recommendations and must not replace review by a qualified clinician. Use synthetic or appropriately de-identified data.

## Live Application

- **Frontend:** https://ai-clinical-document-reviewer-xi.vercel.app/
- **Backend API:** https://ai-clinical-document-reviewer-pb0o.onrender.com
- **API documentation:** https://ai-clinical-document-reviewer-pb0o.onrender.com/docs
- **Health check:** https://ai-clinical-document-reviewer-pb0o.onrender.com/health

The frontend is hosted on Vercel and the FastAPI backend on Render. The backend uses the Groq API for hosted language-model inference.

## Features

- Submit clinical text through the web interface.
- Upload PDF, PNG, JPG, JPEG, and WEBP documents (maximum 10 MB).
- Extract selectable PDF text using PyMuPDF.
- Use Tesseract OCR for scanned PDF pages and images.
- Generate structured reports using a hosted model through Groq.
- Validate report structure with Pydantic.
- Save and retrieve report history using SQLite.
- Highlight missing or uncertain information and require clinician review.
- Validate file extensions, content types, and upload size.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend API | Python, FastAPI |
| Validation | Pydantic |
| Hosted inference | Groq API; model configured by `GROQ_MODEL` |
| PDF extraction | PyMuPDF |
| OCR | Tesseract OCR, pytesseract |
| Image processing | Pillow |
| Report storage | SQLite |
| Deployment | Vercel (frontend), Render (backend Docker service) |

The deployed service is configured with `GROQ_MODEL=openai/gpt-oss-120b`. If `GROQ_MODEL` is unset, the code defaults to `llama-3.3-70b-versatile`.

## Repository Structure

```text
ai-clinical-document-reviewer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/documents.py
│   │   ├── schemas/clinical_report.py
│   │   └── services/
│   │       ├── ai_analyzer.py
│   │       ├── document_processor.py
│   │       └── report_storage.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env                 # create locally; never commit secrets
├── frontend/
│   ├── src/App.jsx
│   ├── src/App.css
│   └── package.json
├── ARCHITECTURE.md
├── AI_ML_DESIGN.md
├── TECHNICAL_DECISIONS.md
├── TESTING.md
└── README.md
```

## Run Locally

### Prerequisites

- Python 3.10 or later
- Node.js and npm
- Tesseract OCR installed
- A Groq API key for model inference

### 1. Configure the backend

From the repository root, open PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` with your own key:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Never commit `.env` or expose API keys in source code, screenshots, logs, or documentation. In production, configure secrets in the hosting provider's environment settings.

Install Tesseract OCR using a trusted distribution. On Windows, the document processor checks `C:\Program Files\Tesseract-OCR\tesseract.exe`. You can set `TESSERACT_CMD` to an alternate executable path. On Linux, Tesseract must be installed and available on the system path.

Start the backend from `backend/`:

```powershell
python -m uvicorn app.main:app --reload
```

Local API URLs:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

### 2. Configure the frontend

Open a second terminal at the repository root:

```powershell
cd frontend
npm install
```

Optionally create `frontend/.env.local`:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Then start Vite:

```powershell
npm run dev
```

Open the local URL printed by Vite, normally http://localhost:5173/.

Vite environment variables are read at build time. In Vercel, set `VITE_API_URL` to the deployed backend URL and redeploy if needed.

## Application Workflow

1. The user submits clinical text or uploads a supported file.
2. The React frontend sends the request to FastAPI.
3. The backend validates the request and file type, content type, and size.
4. The document processor extracts PDF text or uses OCR for scanned pages and images.
5. The AI analyzer sends extracted text and instructions to the configured Groq model.
6. The response is parsed and validated with Pydantic.
7. The report is stored in SQLite.
8. The frontend displays the report and allows history retrieval.

See [ARCHITECTURE.md](ARCHITECTURE.md), [AI_ML_DESIGN.md](AI_ML_DESIGN.md), and [TECHNICAL_DECISIONS.md](TECHNICAL_DECISIONS.md).

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status message |
| GET | `/health` | Backend health check |
| POST | `/analyze/text` | Analyze clinical text |
| POST | `/analyze/file` | Extract and analyze an uploaded document |
| GET | `/reports` | Retrieve report history |
| GET | `/reports/{report_id}` | Retrieve an individual report |

The Swagger interface is available at `/docs` on the API host.

## Report Structure

Reports can contain a summary, patient information, symptoms, recorded diagnoses or labels, medications, vital signs, allergies, observations, concerns, missing information, inconsistencies, a clinician-review flag, and review notes.

The model instructions tell it to use source-supported information, distinguish missing information from confirmed absence, avoid inventing clinical facts, and require clinician review. These instructions reduce risk but do not guarantee correctness.

## Validation and Error Handling

| HTTP Status | Meaning |
|---|---|
| 400 | Empty or invalid input |
| 413 | Upload exceeds the 10 MB limit |
| 415 | Unsupported file type or mismatched content type |
| 422 | Document extraction or input validation failure |
| 500 | Internal processing or storage failure |
| 502 | AI analysis failure |

Exact responses depend on the validation path.

## Storage and Deployment Limitations

Reports are stored in `backend/clinical_reports.db`. Local SQLite persistence depends on retaining the database file. **The deployed free Render service may use ephemeral local storage, so report history is not guaranteed to survive service replacement or redeployment.** Reliable long-term storage would require a persistent disk or managed database.

A free Render instance may also spin down after inactivity, making the first request slower. The public demo does not implement authentication or role-based access control. Do not upload real patient data to the public demo.

## Testing

Manual testing has been performed for clinical text analysis, synthetic PDF upload and analysis, and report history through the deployed frontend. See [TESTING.md](TESTING.md). These are manual functional checks, not an automated test suite or clinical accuracy evaluation.

## Limitations and Future Work

- Model output may omit, misinterpret, or incorrectly organize source information.
- OCR accuracy depends on scan quality and layout.
- Pydantic validation checks structure, not medical correctness.
- Synthetic dataset labels are not validated clinical diagnoses.
- Automated tests and quantitative extraction evaluation should be added.
- Persistent storage, authentication, audit logging, and stronger privacy controls would be needed for a more robust deployment.

## Safety Disclaimer

This is an educational prototype for document review assistance. It is not intended for autonomous diagnosis, treatment selection, emergency use, or replacement of professional medical judgment. All generated reports must be checked against the source document by a qualified clinician.
