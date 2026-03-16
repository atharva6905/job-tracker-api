from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.interview import InterviewOutcome, RoundType


class InterviewCreate(BaseModel):
    round_type: RoundType
    scheduled_at: datetime | None = None
    outcome: InterviewOutcome = InterviewOutcome.Pending
    notes: str | None = None


class InterviewOut(BaseModel):
    id: int
    application_id: int
    round_type: RoundType
    scheduled_at: datetime | None
    outcome: InterviewOutcome | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
