
# AI Clinical Document Reviewer

An AI-assisted application that extracts information from clinical documents and produces structured clinical review reports. The application supports clinical text input, digital PDFs, scanned PDFs, and image-based documents.

## Features

- **Clinical text analysis:** Submit clinical notes directly through the web interface.
- **Document upload:** Upload PDF, PNG, JPG, JPEG, and WEBP files.
- **Text extraction:** Extract selectable text from PDFs and use OCR for scanned pages and images.
- **AI-powered analysis:** Use a locally running Mistral model through Ollama to generate structured reports.
- **Structured reports:** Organize information into patient details, symptoms, diagnoses, medications, vital signs, allergies, observations, concerns, missing information, inconsistencies, and review notes.
- **Report history:** Save and retrieve previously generated reports.
- **Persistent storage:** Store report data in SQLite.
- **Input validation:** Reject unsupported files, oversized uploads, empty files, and documents that cannot be processed.
- **Clinician review warnings:** Remind users that AI-generated output must be verified by a qualified clinician.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| Data validation | Pydantic |
| Language model | Mistral through Ollama |
| PDF processing | PyMuPDF |
| Image OCR | Tesseract OCR, pytesseract |
| Image processing | Pillow |
| Database | SQLite |
| API communication | REST API, JSON |

## Project Structure

```text
ai-clinical-document-reviewer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   └── documents.py
│   │   ├── schemas/
│   │   │   └── clinical_report.py
│   │   └── services/
│   │       ├── ai_analyzer.py
│   │       ├── document_processor.py
│   │       └── report_storage.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── ...
└── README.md
```

## Prerequisites

Install the following before running the application:

- Python 3.10 or later
- Node.js and npm
- Ollama
- Tesseract OCR

Download Ollama from https://ollama.com/.

Install Tesseract OCR using a trusted distribution for your operating system.

## Installation and Setup

### 1. Open the project directory

Open PowerShell in the project root directory, where the `backend` and `frontend` folders are located.

### 2. Set up the backend

```powershell
cd backend

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

If PowerShell prevents virtual environment activation, run:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Set up Ollama

Ensure Ollama is installed and running. Download the Mistral model:

```powershell
ollama pull mistral
```

Verify that the model is available:

```powershell
ollama list
```

### 4. Configure Tesseract OCR

The document processor is currently configured for this Windows installation path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Tesseract is installed elsewhere, update the `tesseract_cmd` setting in `backend/app/services/document_processor.py`.

### 5. Start the backend

From the `backend` directory, activate the virtual environment if necessary, then run:

```powershell
python -m uvicorn app.main:app --reload
```

The API should be available at:

- API base URL: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Keep this terminal running.

### 6. Set up the frontend

Open a second PowerShell terminal. Navigate to the project root if necessary, then run:

```powershell
cd frontend

npm install

npm run dev
```

Open the local URL printed by Vite, normally:

http://localhost:5173/

## Application Workflow

1. The user enters clinical text or uploads a supported document.
2. The frontend sends the input to the FastAPI backend.
3. The backend validates the request and extracts document text.
4. Scanned pages and images are processed using OCR when necessary.
5. The extracted text is sent to the locally running Mistral model through Ollama.
6. The model generates a structured report that is validated against the Pydantic schema.
7. The report is stored in SQLite.
8. The frontend displays the report and allows users to view report history.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check that the API is running |
| GET | `/health` | Check backend health |
| POST | `/analyze/text` | Analyze submitted clinical text |
| POST | `/analyze/file` | Extract and analyze an uploaded document |
| GET | `/reports` | Retrieve report history |
| GET | `/reports/{report_id}` | Retrieve an individual report |

The interactive Swagger interface at `/docs` can be used to inspect endpoints and test requests.

## Report Sections

Each generated report can contain:

- Summary
- Patient information
- Symptoms
- Diagnoses or recorded labels
- Medications
- Vital signs
- Allergies
- Observations
- Concerns
- Missing information
- Inconsistencies
- Clinician review requirement
- Review notes

Information that is not documented should not automatically be interpreted as a confirmed negative finding. Missing or uncertain information should be identified for review.

## Validation and Error Handling

The backend validates uploaded documents and provides appropriate error responses for common problems.

| HTTP Status | Meaning |
|---|---|
| 400 | Invalid or empty file |
| 413 | File exceeds the configured upload limit |
| 415 | Unsupported file type |
| 422 | Document extraction or input validation failure |
| 500 | Internal server or storage failure |
| 502 | AI analysis failure |

The maximum upload size is configured as 10 MB.

## Data Storage

Generated reports are stored in the SQLite database at:

`backend/clinical_reports.db`

The database is initialized by the backend at startup. Report history is retrieved through the API.

The database may contain sensitive clinical information if real documents are uploaded. Use synthetic data for demonstrations and testing. Do not expose the database or API publicly without appropriate security and privacy controls.

## Testing

The application has been manually tested with the following scenarios:

- Clinical text containing patient details, symptoms, and vital signs.
- Clinical text containing missing or uncertain information.
- Contradictory patient information.
- Synthetic clinical dataset PDFs containing multiple patient records.
- File uploads with unsupported extensions.
- Documents that fail text extraction.
- Report retrieval and persistence through SQLite.

These are manual test scenarios. Automated test coverage should be added separately.

## Limitations

- AI-generated information can be incomplete or incorrect.
- OCR may misread low-quality scans, handwriting, or poorly formatted documents.
- Extracted information should be verified against the original document.
- Synthetic dataset labels are not equivalent to validated clinical diagnoses.
- The system is intended for document review assistance, not autonomous diagnosis or treatment.
- The current OCR configuration uses a Windows-specific Tesseract path.
- Local model inference requires Ollama and sufficient local computing resources.

## Safety Disclaimer

This project is an educational prototype for clinical document review assistance. It is not a medical device and must not be used as a substitute for professional medical judgment, diagnosis, or treatment.

All generated reports require review by a qualified clinician. Use fictional or appropriately de-identified data during development and demonstrations.

## Future Improvements

- Automated backend and frontend tests.
- Improved handling of complex tables and handwritten documents.
- Configurable model and OCR settings.
- Authentication and role-based access control.
- Audit logging and stronger data protection.
- Deployment with persistent database storage and a hosted inference service.
- More robust evaluation of extraction accuracy and AI output quality.