from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

class MemberBase(BaseModel):
    job: str
    game_id: str
    sub_job: Optional[str] = None
    remark: Optional[str] = None
    attendance: int = 0

class MemberCreate(MemberBase):
    pass

class Member(MemberBase):
    id: int
    class Config:
        from_attributes = True

class TeamConfigBase(BaseModel):
    name: str
    layout_data: Any

class TeamConfigCreate(TeamConfigBase):
    pass

class TeamConfig(TeamConfigBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class MatchDataBase(BaseModel):
    match_name: str
    raw_stats: Any

class MatchDataCreate(MatchDataBase):
    pass

class MatchData(MatchDataBase):
    id: int
    uploaded_at: datetime
    class Config:
        from_attributes = True
