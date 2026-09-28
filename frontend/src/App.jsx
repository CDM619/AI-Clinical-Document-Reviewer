
import { useEffect, useState } from "react";
import "./App.css";

// Use the deployed API URL when configured.
// Fall back to the local backend during development.
const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [activeTab, setActiveTab] = useState("analyze");
  const [inputMode, setInputMode] = useState("text");
  const [clinicalText, setClinicalText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [report, setReport] = useState(null);
  const [reportId, setReportId] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function getErrorMessage(response) {
    try {
      const data = await response.json();
      return data.detail || "The request failed.";
    } catch {
      return "The server returned an unreadable response.";
    }
  }

  async function loadHistory() {
    setHistoryLoading(true);

    try {
      const response = await fetch(`${API_URL}/reports`);

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const data = await response.json();
      setHistory(data.reports || []);
    } catch (err) {
      setError(
        err.message ||
          "Unable to load report history. Check that the backend is running."
      );
    } finally {
      setHistoryLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function handleTextAnalysis(event) {
    event.preventDefault();

    setError("");
    setMessage("");
    setReport(null);
    setReportId(null);

    const cleanedText = clinicalText.trim();

    if (!cleanedText) {
      setError(
        "Please enter clinical text before clicking Analyze. Empty submissions are not allowed."
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/analyze/text`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: cleanedText,
        }),
      });

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const data = await response.json();

      if (!data.report) {
        throw new Error("The server did not return a clinical report.");
      }

      setReport(data.report);
      setReportId(data.report_id);

      setMessage(
        `Analysis completed. Report #${data.report_id} was saved.`
      );

      await loadHistory();
    } catch (err) {
      setError(err.message || "Unable to analyze the text.");
    } finally {
      setLoading(false);
    }
  }

  async function handleFileAnalysis(event) {
    event.preventDefault();

    setError("");
    setMessage("");
    setReport(null);
    setReportId(null);

    if (!selectedFile) {
      setError("Please select a PDF or image before uploading.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_URL}/analyze/file`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const data = await response.json();

      if (!data.report) {
        throw new Error("The server did not return a clinical report.");
      }

      setReport(data.report);
      setReportId(data.report_id);

      setMessage(
        `Analysis completed for ${data.filename}. Report #${data.report_id} was saved.`
      );

      setSelectedFile(null);
      event.target.reset();

      await loadHistory();
    } catch (err) {
      setError(err.message || "Unable to analyze the document.");
    } finally {
      setLoading(false);
    }
  }

  async function openSavedReport(id) {
    setLoading(true);
    setError("");
    setMessage("");
    setReport(null);
    setReportId(null);

    try {
      const response = await fetch(`${API_URL}/reports/${id}`);

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const data = await response.json();

      if (!data.report) {
        throw new Error("The saved report could not be retrieved.");
      }

      setReport(data.report);
      setReportId(data.id);
      setMessage(`Viewing saved report #${data.id}.`);
      setActiveTab("analyze");
      setInputMode("text");
    } catch (err) {
      setError(err.message || "Unable to retrieve the saved report.");
    } finally {
      setLoading(false);
    }
  }

  function renderList(items) {
    if (!items || items.length === 0) {
      return (
        <p className="empty-value">
          Not documented in the supplied text.
        </p>
      );
    }

    return (
      <ul>
        {items.map((item, index) => (
          <li key={`${index}-${item}`}>{item}</li>
        ))}
      </ul>
    );
  }

  function renderReport() {
    if (!report) {
      return null;
    }

    return (
      <section className="report-panel">
        <div className="report-heading">
          <div>
            <span className="eyebrow">ANALYSIS RESULT</span>
            <h2>Clinical review report</h2>
            {reportId && (
              <p className="muted">Report ID: #{reportId}</p>
            )}
          </div>

          <span className="status-pill">Processed</span>
        </div>

        <div className="summary-card">
          <h3>Summary</h3>
          <p>{report.summary || "No summary was generated."}</p>
        </div>

        <div className="report-grid">
          <article className="report-card">
            <h3>Patient information</h3>
            <p>
              <strong>Patient ID:</strong>{" "}
              {report.patient_info?.patient_id || "Not documented"}
            </p>
            <p>
              <strong>Age:</strong>{" "}
              {report.patient_info?.age || "Not documented"}
            </p>
            <p>
              <strong>Sex:</strong>{" "}
              {report.patient_info?.sex || "Not documented"}
            </p>
          </article>

          <article className="report-card">
            <h3>Symptoms</h3>
            {renderList(report.symptoms)}
          </article>

          <article className="report-card">
            <h3>Diagnoses / recorded labels</h3>
            {renderList(report.diagnoses)}
          </article>

          <article className="report-card">
            <h3>Medications</h3>
            {renderList(report.medications)}
          </article>

          <article className="report-card">
            <h3>Vitals</h3>
            {renderList(report.vitals)}
          </article>

          <article className="report-card">
            <h3>Allergies</h3>
            {renderList(report.allergies)}
          </article>

          <article className="report-card">
            <h3>Observations</h3>
            {renderList(report.observations)}
          </article>

          <article className="report-card">
            <h3>Concerns</h3>
            {renderList(report.concerns)}
          </article>

          <article className="report-card">
            <h3>Missing information</h3>
            {renderList(report.missing_information)}
          </article>

          <article className="report-card">
            <h3>Inconsistencies</h3>
            {renderList(report.inconsistencies)}
          </article>

          <article className="report-card">
            <h3>Review notes</h3>
            {renderList(report.review_notes)}
          </article>
        </div>

        <div className="review-warning">
          <strong>Clinician review required</strong>

          <p>
            {report.requires_clinician_review
              ? "This AI-generated report requires review by a qualified clinician."
              : "Review the report carefully before relying on its contents."}
          </p>

          <p>
            This tool supports document review. It does not establish
            diagnoses or replace professional medical judgment.
          </p>
        </div>

        <div className="report-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              setReport(null);
              setReportId(null);
              setMessage("");
              setError("");
            }}
          >
            Close report
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              setActiveTab("history");
              loadHistory();
            }}
          >
            View report history
          </button>
        </div>
      </section>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">+</div>
          <div>
            <h1>ClinReview</h1>
            <p>Document intelligence</p>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <button
          className={`nav-button ${
            activeTab === "analyze" ? "active" : ""
          }`}
          onClick={() => setActiveTab("analyze")}
          type="button"
        >
          <span>▤</span> Document analysis
        </button>

        <button
          className={`nav-button ${
            activeTab === "history" ? "active" : ""
          }`}
          onClick={() => {
            setActiveTab("history");
            loadHistory();
          }}
          type="button"
        >
          <span>◷</span> Report history
        </button>

        <div className="sidebar-footer">
          <span className="online-dot" />
          <span>Backend API integration</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">
              Workspace /{" "}
              {activeTab === "analyze" ? "Analysis" : "History"}
            </p>

            <h2>
              {activeTab === "analyze"
                ? "Clinical document reviewer"
                : "Report history"}
            </h2>
          </div>

          <span className="environment-badge">
            {import.meta.env.VITE_API_URL ? "PRODUCTION" : "DEVELOPMENT"}
          </span>
        </header>

        {error && (
          <div className="alert alert-error" role="alert">
            <span>{error}</span>
            <button
              onClick={() => setError("")}
              aria-label="Dismiss error"
              type="button"
            >
              ×
            </button>
          </div>
        )}

        {message && (
          <div className="alert alert-success" role="status">
            <span>{message}</span>
            <button
              onClick={() => setMessage("")}
              aria-label="Dismiss message"
              type="button"
            >
              ×
            </button>
          </div>
        )}

        {activeTab === "analyze" && (
          <>
            <section className="welcome-section">
              <span className="eyebrow">
                AI-ASSISTED DOCUMENT REVIEW
              </span>

              <h2>
                Turn clinical documents into structured insights.
              </h2>

              <p>
                Submit clinical text or upload a document to extract
                and organize information for clinician review.
              </p>
            </section>

            <section className="input-panel">
              <div className="section-heading">
                <div>
                  <h3>Provide a clinical document</h3>
                  <p>
                    Use synthetic or appropriately authorized data only.
                  </p>
                </div>
              </div>

              <div className="input-tabs">
                <button
                  className={`input-tab ${
                    inputMode === "text" ? "active" : ""
                  }`}
                  onClick={() => {
                    setInputMode("text");
                    setError("");
                  }}
                  type="button"
                >
                  Paste text
                </button>

                <button
                  className={`input-tab ${
                    inputMode === "file" ? "active" : ""
                  }`}
                  onClick={() => {
                    setInputMode("file");
                    setError("");
                  }}
                  type="button"
                >
                  Upload document
                </button>
              </div>

              {inputMode === "text" && (
                <form onSubmit={handleTextAnalysis}>
                  <label htmlFor="clinical-text">
                    Clinical text
                  </label>

                  <textarea
                    id="clinical-text"
                    value={clinicalText}
                    onChange={(event) =>
                      setClinicalText(event.target.value)
                    }
                    placeholder="Paste a synthetic clinical note, observations, medication list, or other clinical text here..."
                    rows={7}
                    disabled={loading}
                  />

                  <div className="form-footer">
                    <span>
                      {clinicalText.length} characters
                    </span>

                    <button
                      className="primary-button"
                      type="submit"
                      disabled={loading}
                    >
                      {loading
                        ? "Analyzing..."
                        : "Analyze clinical text →"}
                    </button>
                  </div>
                </form>
              )}

              {inputMode === "file" && (
                <form
                  onSubmit={handleFileAnalysis}
                  className="upload-form"
                >
                  <label
                    className="drop-zone"
                    htmlFor="clinical-file"
                  >
                    <span className="upload-icon">↑</span>

                    <strong>
                      {selectedFile
                        ? selectedFile.name
                        : "Choose a document to analyze"}
                    </strong>

                    <span>
                      PDF, PNG, JPG or WEBP · Maximum 10 MB
                    </span>

                    <input
                      id="clinical-file"
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/png,image/jpeg,image/webp"
                      disabled={loading}
                      onChange={(event) =>
                        setSelectedFile(
                          event.target.files?.[0] || null
                        )
                      }
                    />
                  </label>

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={loading || !selectedFile}
                  >
                    {loading
                      ? "Processing document..."
                      : "Upload and analyze →"}
                  </button>
                </form>
              )}

              {loading && (
                <div className="loading-panel">
                  <span className="spinner" />
                  <span>
                    Processing the document and generating a
                    structured report. This may take a little while.
                  </span>
                </div>
              )}
            </section>

            {renderReport()}
          </>
        )}

        {activeTab === "history" && (
          <section className="input-panel history-panel">
            <div className="section-heading">
              <div>
                <h3>Previously generated reports</h3>
                <p>
                  Reports saved by the backend service.
                </p>
              </div>

              <button
                className="secondary-button"
                onClick={loadHistory}
                disabled={historyLoading}
                type="button"
              >
                {historyLoading ? "Refreshing..." : "Refresh"}
              </button>
            </div>

            {historyLoading && history.length === 0 ? (
              <div className="loading-panel">
                <span className="spinner" />
                <span>Loading saved reports...</span>
              </div>
            ) : history.length === 0 ? (
              <div className="empty-history">
                <span className="upload-icon">◷</span>
                <h3>No saved reports yet</h3>
                <p>
                  Analyze a document to create your first report.
                </p>

                <button
                  className="primary-button"
                  onClick={() => setActiveTab("analyze")}
                  type="button"
                >
                  Analyze a document
                </button>
              </div>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <article
                    className="history-item"
                    key={item.id}
                  >
                    <div className="history-file-icon">▤</div>

                    <div className="history-details">
                      <strong>
                        {item.filename ||
                          `Clinical text report #${item.id}`}
                      </strong>

                      <span>
                        ID #{item.id} · {item.input_type} ·{" "}
                        {item.character_count} characters
                      </span>

                      <span>
                        {item.created_at
                          ? new Date(
                              item.created_at
                            ).toLocaleString()
                          : "Date unavailable"}
                      </span>
                    </div>

                    <button
                      className="secondary-button"
                      onClick={() => openSavedReport(item.id)}
                      disabled={loading}
                      type="button"
                    >
                      {loading ? "Loading..." : "View report"}
                    </button>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

        <footer className="page-footer">
          <span>
            ClinReview · AI Clinical Document Reviewer
          </span>

          <span>
            For document review support only · Clinician oversight required
          </span>
        </footer>
      </main>
    </div>
  );
}

export default App;
