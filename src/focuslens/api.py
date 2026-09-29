from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import Settings
from .model import FocusModel
from .schemas import AnalysisResult, ModelCard, SignalInput, Summary
from .service import AnalysisService
from .store import ObservationStore


@lru_cache(maxsize=1)
def get_service() -> AnalysisService:
    settings = Settings.from_environment()
    return AnalysisService(
        model=FocusModel(settings.model_path),
        store=ObservationStore(settings.database_path),
    )


settings = Settings.from_environment()
static_directory = files("focuslens").joinpath("static")

app = FastAPI(
    title="FocusLens AI",
    version=__version__,
    description=(
        "Privacy-first portfolio API for explainable engagement-signal analysis. "
        "The API accepts numeric features only and never accepts raw images."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")


@app.exception_handler(Exception)
async def unexpected_error(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred", "request_data_retained": False},
    )


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(static_directory.joinpath("index.html"))


@app.get("/api/health", tags=["system"])
def health() -> dict[str, str | bool]:
    service = get_service()
    return {
        "status": "ok",
        "model_loaded": bool(service.model.version),
        "privacy_mode": "numeric-signals-only",
    }


@app.post("/api/v1/analyze", response_model=AnalysisResult, tags=["analysis"])
def analyze(signal: SignalInput) -> AnalysisResult:
    return get_service().analyze(signal)


@app.get("/api/v1/summary", response_model=Summary, tags=["analysis"])
def summary() -> Summary:
    return get_service().summary()


@app.get("/api/v1/model-card", response_model=ModelCard, tags=["governance"])
def model_card() -> ModelCard:
    return get_service().model_card()
