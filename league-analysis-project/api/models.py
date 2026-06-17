from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from .main import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    job = Column(String, index=True)
    game_id = Column(String, unique=True, index=True)
    sub_job = Column(String, nullable=True)
    remark = Column(String, nullable=True)
    attendance = Column(Integer, default=0)

class TeamConfig(Base):
    __tablename__ = "team_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    layout_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MatchData(Base):
    __tablename__ = "match_data"

    id = Column(Integer, primary_key=True, index=True)
    match_name = Column(String, index=True)
    raw_stats = Column(JSON)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
