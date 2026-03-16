from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewOut

router = APIRouter(
    prefix="/applications/{app_id}/interviews",
    tags=["interviews"],
)


def get_owned_application(app_id: int, current_user: User, db: Session) -> Application:
    application = (
        db.query(Application)
        .filter(Application.id == app_id, Application.user_id == current_user.id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return application


@router.post("/", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
def create_interview(
    app_id: int,
    payload: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Interview:
    application = get_owned_application(app_id, current_user, db)

    interview = Interview(application_id=app_id, **payload.model_dump())
    db.add(interview)

    if application.status == ApplicationStatus.Applied:
        application.status = ApplicationStatus.Interview
        db.add(application)

    db.commit()
    db.refresh(interview)
    return interview


@router.get("/", response_model=list[InterviewOut])
def list_interviews(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Interview]:
    get_owned_application(app_id, current_user, db)
    return db.query(Interview).filter(Interview.application_id == app_id).all()
