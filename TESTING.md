
# Testing Report — AI Clinical Document Reviewer

## 1. Objective

The purpose of testing is to verify that the AI Clinical Document Reviewer accepts supported input, extracts clinical text, generates structured reports, stores report history, and handles invalid inputs appropriately.

Testing is performed using synthetic clinical data to avoid unnecessary exposure of real patient information.

## 2. Testing Approach

The application has been manually tested through the React frontend and its FastAPI backend.

Testing covers:
- Clinical text analysis.
- PDF and image document processing.
- OCR for scanned documents.
- Structured report generation.
- Input validation and error handling.
- Report history and database persistence.

## 3. Functional Test Cases

| Test ID | Test Scenario | Expected Result | Reported Outcome |
|---|---|---|---|
| TC-01 | Submit valid clinical text | Generate a structured clinical report | Passed |
| TC-02 | Include patient information and vital signs | Extract and display documented details | Passed |
| TC-03 | Submit text with missing information | Identify missing or uncertain information where appropriate | Passed |
| TC-04 | Submit contradictory patient information | Flag inconsistencies when detected | Passed |
| TC-05 | Upload a supported PDF | Extract text and generate a report | Passed |
| TC-06 | Upload a synthetic clinical dataset PDF | Process the dataset and display relevant observations | Passed |
| TC-07 | Upload an unsupported TXT file | Reject the upload with an unsupported-media response | Passed |
| TC-08 | Upload a document that cannot be processed | Return an extraction error | Passed |
| TC-09 | Retrieve report history | Display previously stored reports | Passed |
| TC-10 | Restart the backend and retrieve saved reports | Preserve reports stored in SQLite | Passed |

The outcomes above reflect the manual testing results reported during development. They are not the output of an automated test suite.

## 4. Input Validation and Error Handling

The backend validates incoming requests and uploaded files.

| Condition | Expected HTTP Status |
|---|---|
| Unsupported file type | 415 Unsupported Media Type |
| Empty or invalid file | 400 Bad Request, where applicable |
| File exceeding the configured limit | 413 Payload Too Large |
| Document extraction failure | 422 Unprocessable Entity |
| AI analysis failure | 502 Bad Gateway |
| Internal processing or storage failure | 500 Internal Server Error |

Exact responses depend on the validation path and error-handling implementation.

## 5. Clinical Information Validation

The application organizes extracted information into a structured report containing fields such as:

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
- Review notes

The system should not invent undocumented patient details or treat missing information as a confirmed negative finding.

Generated reports must be compared against the original document. Structured output validation alone does not establish clinical accuracy.

## 6. Database Persistence

SQLite is used to store generated reports.

Manual verification includes:
- Generating a report.
- Retrieving the report through the application.
- Checking the report history.
- Restarting the backend.
- Confirming that previously saved reports remain retrievable.

Persistence depends on retaining the database file and its contents.

## 7. Known Testing Limitations

- Testing is manual rather than automated.
- No quantitative clinical extraction accuracy benchmark has been established.
- OCR performance may vary with image quality, page layout, and text clarity.
- AI output may contain omissions or inaccuracies.
- The application has not been validated for clinical deployment.
- Passing functional tests does not establish medical correctness or patient safety.

## 8. Future Testing Improvements

The following tests should be added as the project develops:

- Automated backend API tests using pytest and FastAPI's test client.
- Frontend component and interaction tests.
- Tests for oversized files, malformed PDFs, and password-protected PDFs.
- Tests for database failures and unavailable Ollama services.
- Tests for empty AI responses and malformed model output.
- Regression tests for patient identifiers and contradictory information.
- Measured OCR accuracy using documents with known text.
- Security testing for file uploads, data access, and deployment configuration.

## 9. Conclusion

Manual testing has been used to verify the main application workflow, including clinical text analysis, supported document uploads, synthetic dataset processing, error handling, and report persistence.

The application is an educational prototype. Further automated testing, accuracy evaluation, privacy safeguards, and security validation are required before considering any real-world clinical use.