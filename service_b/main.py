from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from middleware.tenants import TenantMiddleware, get_db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


app = FastAPI()
app.add_middleware(TenantMiddleware)

# Pydantic models
class TaskBase(BaseModel):
    title: str
    content: str

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True

# SQLAlchemy models

Base = declarative_base()

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)

# CRUD operations
def get_post(db: Session, post_id: int):
    return db.query(TaskModel).filter(TaskModel.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(TaskModel).offset(skip).limit(limit).all()

def create_post(db: Session, post: TaskCreate):
    Base.metadata.create_all(bind=db.get_bind())
    db_post = TaskModel(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# API endpoints
@app.post("/tasks/", response_model=Task)
def create_post_endpoint(post: TaskCreate, db: Session = Depends(get_db)):
    return create_post(db, post)

@app.get("/tasks/", response_model=List[Task])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = get_posts(db, skip=skip, limit=limit)
    return posts

@app.get("/tasks/{post_id}", response_model=Task)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_post