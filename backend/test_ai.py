
from app.services.ai_analyzer import analyze_clinical_text

sample_text = """
Synthetic clinical record for software testing.
Patient ID: SYN-TEST-001
Age: 45
BMI: 26.5
Systolic blood pressure: 120 mmHg
Diastolic blood pressure: 80 mmHg
Glucose: 110 mg/dL
HbA1c: 5.4 percent
Allergies: Not documented.
Medications: Not documented.
This is fictional data, not a real patient record.
"""

report = analyze_clinical_text(sample_text)

print(report.model_dump_json(indent=2))