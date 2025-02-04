import os
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
assert DATABASE_URL, "DATABASE_URL is required"

# Dependency to get the database session
def get_db(request: Request):
    schema = request.state.schema
    # Set the schema in the database
    engine = create_engine(f"{DATABASE_URL}?options=-csearch_path={schema}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host")
        if not host:
            raise HTTPException(status_code=400, detail="Host header is missing")
        
        match = re.match(r"^(?P<subdomain>[^.]+)\.", host)
        if not match:
            raise HTTPException(status_code=404, detail="Subdomain is missing")
        
        subdomain = match.group("subdomain")
        request.state.schema = subdomain
        response = await call_next(request)
        return response
