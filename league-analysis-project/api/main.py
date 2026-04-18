from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import io
import pandas as pd
from typing import List

app = FastAPI(title="League Analysis API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./league.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from . import models, schemas
models.Base.metadata.create_all(bind=engine)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# --- Members API ---
@app.get("/api/members", response_model=List[schemas.Member])
def get_members(db: Session = Depends(get_db)):
    return db.query(models.Member).all()

@app.post("/api/members", response_model=schemas.Member)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    db_member = db.query(models.Member).filter(models.Member.game_id == member.game_id).first()
    if db_member:
        for key, value in member.model_dump().items():
            setattr(db_member, key, value)
    else:
        db_member = models.Member(**member.model_dump())
        db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.post("/api/members/import")
async def import_members(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        # Expected CSV might have headers starting at line 2, so we need to handle that
        # Try reading normally first
        lines = content.decode("utf-8").splitlines()
        # Find the header row (contains "玩家名字")
        header_idx = 0
        for i, line in enumerate(lines):
            if "玩家名字" in line:
                header_idx = i
                break
                
        # Join lines from header onwards
        valid_csv = "\n".join(lines[header_idx:])
        df = pd.read_csv(io.StringIO(valid_csv))
        
        # map to DB fields based on new CSV format
        imported_count = 0
        for _, row in df.iterrows():
            game_id = str(row.get("玩家名字", ""))
            if not game_id or game_id == "nan" or game_id == "nil":
                continue
                
            db_member = db.query(models.Member).filter(models.Member.game_id == game_id).first()
            if db_member:
                db_member.job = str(row.get("职业", db_member.job))
                # New CSV might not have sub_job, remark, attendance explicitly named as before
                # We'll just update what we have
            else:
                db_member = models.Member(
                    job=str(row.get("职业", "未知")),
                    game_id=game_id,
                    sub_job=None,
                    remark=None,
                    attendance=1 # Default to 1 on import
                )
                db.add(db_member)
            imported_count += 1
            
        db.commit()
        return {"status": "success", "imported": imported_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/members/delete-batch")
def delete_members(game_ids: List[str], db: Session = Depends(get_db)):
    db.query(models.Member).filter(models.Member.game_id.in_(game_ids)).delete(synchronize_session=False)
    db.commit()
    return {"status": "success"}

# --- Team Configs API ---
@app.get("/api/teams", response_model=List[schemas.TeamConfig])
def get_teams(db: Session = Depends(get_db)):
    return db.query(models.TeamConfig).order_by(models.TeamConfig.created_at.desc()).all()

@app.post("/api/teams", response_model=schemas.TeamConfig)
def create_team(team: schemas.TeamConfigCreate, db: Session = Depends(get_db)):
    db_team = models.TeamConfig(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

# --- Analysis API ---
@app.post("/api/analysis/upload")
async def upload_analysis_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        # Very simple initial parse, store raw stats
        stats_dict = df.to_dict(orient="records")
        
        match_data = models.MatchData(
            match_name=file.filename,
            raw_stats=stats_dict
        )
        db.add(match_data)
        db.commit()
        db.refresh(match_data)
        
        return {"status": "success", "match_id": match_data.id, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analysis/team-data")
def get_team_analysis_data(team_id: int, match_id: int, db: Session = Depends(get_db)):
    team = db.query(models.TeamConfig).filter(models.TeamConfig.id == team_id).first()
    match = db.query(models.MatchData).filter(models.MatchData.id == match_id).first()
    
    if not team or not match:
        raise HTTPException(status_code=404, detail="Team or Match not found")
        
    # We will process team layout and match raw stats here
    # For now, just return a dummy combined structure
    return {
        "team_name": team.name,
        "match_name": match.match_name,
        "layout": team.layout_data,
        "stats": match.raw_stats
    }
