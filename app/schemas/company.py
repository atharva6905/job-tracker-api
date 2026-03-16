from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1)
    location: str | None = None
    link: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    link: str | None = None


class CompanyOut(BaseModel):
    id: int
    user_id: int
    name: str
    location: str | None
    link: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
