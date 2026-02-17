from sqlalchemy import Column, Integer, String, Text
from app.database.connection import Base


class SAR(Base):
    __tablename__ = "sar_versions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, index=True)
    version = Column(Integer)
    sar_narrative = Column(Text)
    explanation = Column(Text)
