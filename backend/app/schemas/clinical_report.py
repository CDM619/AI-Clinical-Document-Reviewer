from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    patient_id: str | None = None
    age: str | None = None
    sex: str | None = None


class ClinicalReport(BaseModel):
    summary: str = Field(
        description="A concise summary of the provided clinical document."
    )

    patient_info: PatientInfo = Field(
        description="Patient details explicitly present in the document."
    )

    symptoms: list[str] = Field(default_factory=list)
    diagnoses: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    vitals: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    inconsistencies: list[str] = Field(default_factory=list)

    requires_clinician_review: bool = True

    review_notes: list[str] = Field(
        default_factory=list,
        description="Limitations, uncertainty, and review notes."
    )