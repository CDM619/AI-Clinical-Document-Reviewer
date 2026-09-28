# Technical Decisions — AI Clinical Document Reviewer

## 1. React and Vite for the Frontend

**Decision:** Use React for the interactive UI and Vite for development and builds.

**Reasoning:** The application needs text input, file upload, loading/error states, structured report display, and report history.

**Trade-off:** The client-side frontend depends on the backend API being reachable.

## 2. FastAPI for the Backend

**Decision:** Use FastAPI for JSON and file-upload endpoints.

**Reasoning:** FastAPI supports typed request validation, multipart uploads, route definitions, and interactive OpenAPI/Swagger documentation.

**Trade-off:** Production use would require further hardening, monitoring, and authentication if sensitive or multi-user workflows were introduced.

## 3. Groq Hosted Inference

**Decision:** Use the Groq API through the Python Groq client. Configure the model with `GROQ_MODEL` and the credential with `GROQ_API_KEY`.

**Reasoning:** Hosted inference avoids downloading and running a large language model on the deployment instance.

**Trade-offs:**
- The backend requires network access and a valid API key.
- Inference can fail due to provider availability, rate limits, or configuration.
- Submitted text is sent to the inference provider; sensitive clinical data should not be sent without appropriate authorization and privacy review.
- API success does not guarantee correct model output.

The deployed configuration uses `openai/gpt-oss-120b`. The code defaults to `llama-3.3-70b-versatile` if `GROQ_MODEL` is not set.

## 4. PyMuPDF with Tesseract OCR

**Decision:** Extract selectable PDF text with PyMuPDF and use Tesseract OCR for scanned pages and images.

**Reasoning:** Direct extraction is preferable when a PDF already contains selectable text, while OCR provides a fallback for scans.

**Trade-off:** OCR can misread text, numbers, units, and complex layouts. Extracted text should be checked against the source.

## 5. Pydantic for Report Structure

**Decision:** Define the report contract with Pydantic models.

**Reasoning:** A consistent schema makes reports easier to render, store, retrieve, and validate across API boundaries.

**Trade-off:** Structural validation cannot guarantee factual or clinical correctness.

## 6. SQLite for Prototype Storage

**Decision:** Use SQLite to store report JSON and metadata.

**Reasoning:** SQLite is simple to set up, requires no separate database server, and supports local development and demonstrations.

**Trade-offs:**
- Persistence depends on retaining the database file.
- The deployed free Render filesystem may be ephemeral across service replacement or redeployment.
- Local SQLite storage is not a substitute for durable production storage.
- Reports may contain sensitive information and require access controls.

For a more durable deployment, use a persistent disk or managed database and implement authentication, access control, retention rules, and monitoring.

## 7. Environment Variables for Configuration

**Decision:** Keep credentials and deployment-specific settings in environment variables.

Relevant variables:
- `GROQ_API_KEY`: required API credential.
- `GROQ_MODEL`: model identifier.
- `TESSERACT_CMD`: optional Tesseract executable path.
- `VITE_API_URL`: frontend API base URL at build time.

Never commit secret values to GitHub. If a key is exposed, revoke it and replace it.

## 8. Docker for Backend Deployment

**Decision:** Package the backend in Docker and install Tesseract in the container.

**Reasoning:** Docker makes Python and system OCR dependencies more consistent on the hosting platform.

**Trade-off:** The image includes system packages and still depends on correct environment variables and hosting configuration.

## 9. Vercel and Render Deployment

**Decision:** Host the React frontend on Vercel and the FastAPI backend on Render.

**Reasoning:** This separates frontend and backend deployment and provides public demonstration URLs.

**Trade-offs:**
- CORS must allow the frontend origin.
- Free Render instances may spin down after inactivity, slowing the first request.
- Local database files may not be durable on an ephemeral filesystem.
- A public demo without authentication should only be used with synthetic data.

## 10. Safety-Oriented Output Instructions

**Decision:** Prompt the model to avoid inventing information, distinguish missing data from confirmed absence, avoid treatment recommendations, and require clinician review.

**Reasoning:** These constraints help communicate uncertainty and limit unsupported claims.

**Trade-off:** Prompt instructions do not eliminate hallucinations or ensure safe clinical interpretation. Reports remain unvalidated drafts and must be checked against the source.

## 11. Known Gaps

The current implementation is a prototype. Future improvements include automated tests, quantitative extraction evaluation, durable storage, authentication, authorization, audit logging, privacy review, and operational monitoring before any higher-stakes use.
