from fastapi import FastAPI

from app.api.routes.applications import router as applications_router
from app.api.routes.auth import router as auth_router
from app.api.routes.companies import router as companies_router
from app.api.routes.interviews import router as interviews_router
from app.core.config import settings  # noqa: F401

app = FastAPI(
    title="Job Application Tracker API",
    version="0.1.0",
    description="API for managing job applications, companies, interviews, and auth.",
)


@app.get("/health", status_code=200)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


# Routers are included here.
app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(applications_router)
app.include_router(interviews_router)
