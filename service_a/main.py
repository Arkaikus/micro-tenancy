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
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int

    class Config:
        orm_mode = True

# SQLAlchemy models

Base = declarative_base()

class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)

# CRUD operations
def get_post(db: Session, post_id: int):
    return db.query(PostModel).filter(PostModel.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(PostModel).offset(skip).limit(limit).all()

def create_post(db: Session, post: PostCreate):
    Base.metadata.create_all(bind=db.get_bind())
    db_post = PostModel(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# API endpoints
@app.post("/posts/", response_model=Post)
def create_post_endpoint(post: PostCreate, db: Session = Depends(get_db)):
    return create_post(db, post)

@app.get("/posts/", response_model=List[Post])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = get_posts(db, skip=skip, limit=limit)
    return posts

@app.get("/posts/{post_id}", response_model=Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post