from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.transitions import validate_status_transition
from app.models.application import Application, ApplicationStatus
from app.models.company import Company
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
    PaginatedApplicationsResponse,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=PaginatedApplicationsResponse)
def list_applications(
    status: ApplicationStatus | None = None,
    company_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedApplicationsResponse:
    query = db.query(Application).where(Application.user_id == current_user.id)

    if status is not None:
        query = query.where(Application.status == status)
    if company_id is not None:
        query = query.where(Application.company_id == company_id)
    if date_from is not None:
        query = query.where(Application.date_applied >= date_from)
    if date_to is not None:
        query = query.where(Application.date_applied <= date_to)

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    return PaginatedApplicationsResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.post("/", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    company = (
        db.query(Company)
        .filter(Company.id == payload.company_id, Company.user_id == current_user.id)
        .first()
    )
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    application = Application(
        user_id=current_user.id,
        company_id=payload.company_id,
        role=payload.role,
        status=payload.status,
        date_applied=payload.date_applied or date.today(),
        notes=payload.notes,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    application = (
        db.query(Application)
        .filter(Application.id == app_id, Application.user_id == current_user.id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return application


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    application = (
        db.query(Application)
        .filter(Application.id == app_id, Application.user_id == current_user.id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] is not None:
        validate_status_transition(application.status, update_data["status"])

    for key, value in update_data.items():
        setattr(application, key, value)

    db.commit()
    db.refresh(application)
    return application


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    application = (
        db.query(Application)
        .filter(Application.id == app_id, Application.user_id == current_user.id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    db.delete(application)
    db.commit()
    return None
