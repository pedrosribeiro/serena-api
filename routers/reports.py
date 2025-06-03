from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.report import Report
from models.user import User
from routers.prescriptions import get_current_user
from schemas.report import ReportCreate, ReportRead
from utils.jwt import decode_access_token

router = APIRouter()


@router.post("/", response_model=ReportRead, dependencies=[Depends(get_current_user)])
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_report = Report(user_id=current_user.id, **report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get(
    "/", response_model=List[ReportRead], dependencies=[Depends(get_current_user)]
)
def list_reports(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    return db.query(Report).filter(Report.user_id == current_user.id).all()


@router.get(
    "/{report_id}", response_model=ReportRead, dependencies=[Depends(get_current_user)]
)
def get_report(
    report_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete(
    "/{report_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
def delete_report(
    report_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return


@router.put(
    "/{report_id}", response_model=ReportRead, dependencies=[Depends(get_current_user)]
)
def update_report(
    report_id: int,
    report: ReportCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.user_id == current_user.id)
        .first()
    )
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    db_report.content = report.content
    db_report.created_at = report.created_at
    db.commit()
    db.refresh(db_report)
    return db_report


@router.post("/", response_model=ReportRead, dependencies=[Depends(get_current_user)])
def create_report(report: ReportCreate, db: Session = Depends(get_session)):
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get(
    "/", response_model=List[ReportRead], dependencies=[Depends(get_current_user)]
)
def list_reports(db: Session = Depends(get_session)):
    return db.query(Report).all()


@router.get(
    "/{report_id}", response_model=ReportRead, dependencies=[Depends(get_current_user)]
)
def get_report(report_id: str, db: Session = Depends(get_session)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put(
    "/{report_id}", response_model=ReportRead, dependencies=[Depends(get_current_user)]
)
def update_report(
    report_id: str, report: ReportCreate, db: Session = Depends(get_session)
):
    db_report = db.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    for key, value in report.dict().items():
        setattr(db_report, key, value)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.delete(
    "/{report_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
def delete_report(report_id: str, db: Session = Depends(get_session)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return
