from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    company_id: int
    role: str = Field(min_length=1)
    status: ApplicationStatus = ApplicationStatus.Applied
    date_applied: date | None = None
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    role: str | None = None
    status: ApplicationStatus | None = None
    date_applied: date | None = None
    notes: str | None = None


class ApplicationOut(BaseModel):
    id: int
    user_id: int
    company_id: int
    role: str
    status: ApplicationStatus
    date_applied: date
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedApplicationsResponse(BaseModel):
    items: list[ApplicationOut]
    page: int
    limit: int
    total: int
