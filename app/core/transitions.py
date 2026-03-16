from fastapi import HTTPException, status

from app.models.application import ApplicationStatus

ALLOWED_TRANSITIONS: dict[ApplicationStatus, set[ApplicationStatus]] = {
    ApplicationStatus.Applied: {
        ApplicationStatus.Interview,
        ApplicationStatus.Rejected,
    },
    ApplicationStatus.Interview: {
        ApplicationStatus.Offer,
        ApplicationStatus.Rejected,
    },
    ApplicationStatus.Offer: set(),
    ApplicationStatus.Rejected: set(),
}


def validate_status_transition(
    current: ApplicationStatus,
    new: ApplicationStatus,
) -> None:
    if current == new:
        return

    if new not in ALLOWED_TRANSITIONS[current]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {current.value} to {new.value}",
        )
