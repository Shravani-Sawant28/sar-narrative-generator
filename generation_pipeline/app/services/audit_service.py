from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import SAR

def get_latest_sar_version(case_id: str):
    db: Session = SessionLocal()

    try:
        return (
            db.query(SAR)
            .filter(SAR.case_id == case_id)
            .order_by(SAR.version.desc())
            .first()
        )
    finally:
        db.close()


def save_sar_version(case_id: str, narrative: str, explanation: str):
    db: Session = SessionLocal()

    try:
        latest = (
            db.query(SAR)
            .filter(SAR.case_id == case_id)
            .order_by(SAR.version.desc())
            .first()
        )

        new_version = 1 if not latest else latest.version + 1

        sar_entry = SAR(
            case_id=case_id,
            version=new_version,
            sar_narrative=narrative,
            explanation=explanation
        )

        db.add(sar_entry)
        db.commit()
        db.refresh(sar_entry)

        return new_version

    finally:
        db.close()
