# Testing Report — AI Clinical Document Reviewer

## 1. Objective

Testing checks the main workflow: clinical text submission, document extraction, structured report generation, and report history. Testing uses synthetic data and is not a clinical validation study.

## 2. Testing Approach

Testing has been performed manually through the deployed React frontend and FastAPI backend. No automated test suite or quantitative clinical accuracy benchmark is claimed.

## 3. Manual Functional Test Results

| Test ID | Scenario | Expected Result | Reported Outcome |
|---|---|---|---|
| TC-01 | Submit synthetic clinical text | Generate a structured report | Passed in deployed application |
| TC-02 | Inspect patient details and observations | Show source-supported details | Checked during text-analysis testing |
| TC-03 | Upload a supported synthetic PDF | Extract text and generate a report | Passed in deployed application |
| TC-04 | View report history after generating reports | Show saved report entries | Report history tested by user |
| TC-05 | Open an individual report from history | Display saved report details | Report history tested by user |
| TC-06 | Refresh the frontend | Application remains accessible and can request data again | Verify during final check |
| TC-07 | Upload an unsupported file type | Reject the upload | Validation implemented; retest before claiming deployment verification |
| TC-08 | Upload an empty or malformed document | Return an appropriate error | Error handling implemented; retest before claiming deployment verification |
| TC-09 | Upload a file larger than 10 MB | Reject the upload | 10 MB limit implemented; retest before claiming deployment verification |
| TC-10 | Test scanned PDF/image OCR | Extract readable text where possible | OCR path implemented; quality depends on the document |

## 4. Input Validation and Error Handling

The backend checks supported file extensions and content types, rejects empty uploads, enforces a 10 MB limit, and handles extraction, AI, and storage failures.

| Status | Meaning |
|---|---|
| 400 | Empty or invalid input |
| 413 | File exceeds the configured limit |
| 415 | Unsupported file type or content type mismatch |
| 422 | Document extraction or input validation failure |
| 500 | Internal processing or storage failure |
| 502 | AI analysis failure |

Exact responses depend on the path and error condition.

## 5. Data and Clinical Safety Checks

The expected report structure includes a summary, patient information, symptoms, recorded diagnoses, medications, vital signs, allergies, observations, concerns, missing information, inconsistencies, clinician-review flag, and review notes.

Generated information should be checked against the source document. Missing information should not be treated as a confirmed negative finding. Pydantic validation checks structure but not medical correctness.

## 6. Report History and Persistence

The application stores report content and metadata in SQLite. Local persistence depends on retaining the database file. The deployed free Render service may use ephemeral local storage, so long-term persistence across service replacement or redeployment is not guaranteed. Production durability would require persistent storage.

## 7. Limitations

- Testing is manual, not automated.
- No quantitative clinical extraction accuracy benchmark has been established.
- OCR performance varies by scan quality and layout.
- Model output may omit or misinterpret information.
- The application has not been validated for clinical deployment.
- Passing functional tests does not establish clinical correctness or patient safety.

## 8. Recommended Future Tests

- Automated backend tests using pytest and FastAPI's test client.
- Frontend component and interaction tests.
- Oversized, malformed, and password-protected PDF tests.
- Tests for unavailable Groq service, malformed model output, and database failures.
- Regression tests for missing fields and contradictory information.
- OCR accuracy evaluation against documents with known text.
- Security tests for upload handling, access control, and deployment configuration.

## 9. Conclusion

Manual testing confirmed deployed clinical text analysis, synthetic PDF upload and analysis, and report history in the demonstrated workflow. Additional automated tests, accuracy evaluation, persistent storage, privacy safeguards, and security validation are needed before any real-world clinical use.
