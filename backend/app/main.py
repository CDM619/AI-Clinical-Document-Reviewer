
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.documents import router as documents_router
from app.services.report_storage import initialize_database

app = FastAPI(
    title="AI Clinical Document Reviewer",
    description="API for processing clinical documents and generating structured reviews.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.on_event("startup")
def startup_event():
    initialize_database()


@app.get("/")
def home():
    return {"message": "AI Clinical Document Reviewer API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(documents_router)