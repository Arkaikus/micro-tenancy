import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
assert DATABASE_URL, "DATABASE_URL is required"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class TenantCreate(BaseModel):
    name: str
    email: str

Base.metadata.create_all(bind=engine)

@app.get("/healthcheck")
def healthcheck():
    try:
        db = SessionLocal()
        # Perform a simple query to check database connectivity
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/tenants/", response_model=TenantCreate)
def create_tenant(tenant: TenantCreate):
    db = SessionLocal()
    db_tenant = Tenant(name=tenant.name, email=tenant.email)
    db.add(db_tenant)
    try:
        db.commit()
        db.refresh(db_tenant)
        
        # Create a new schema for the tenant
        db.execute(text(f"CREATE SCHEMA {tenant.name}"))
        db.commit()
        
        db.refresh(db_tenant)  # Ensure the instance is attached to the session
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating tenant: {str(e)}")
    finally:
        db.close()
    return db_tenant

@app.get("/tenants/{tenant_id}", response_model=TenantCreate)
def read_tenant(tenant_id: int):
    db = SessionLocal()
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    db.close()
    if db_tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return db_tenant

@app.put("/tenants/{tenant_id}", response_model=TenantCreate)
def update_tenant(tenant_id: int, tenant: TenantCreate):
    db = SessionLocal()
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if db_tenant is None:
        db.close()
        raise HTTPException(status_code=404, detail="Tenant not found")
    db_tenant.name = tenant.name
    db_tenant.email = tenant.email
    db.commit()
    db.refresh(db_tenant)
    db.close()
    return db_tenant

@app.delete("/tenants/{tenant_id}")
def delete_tenant(tenant_id: int):
    db = SessionLocal()
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if db_tenant is None:
        db.close()
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Drop the schema for the tenant
    schema_name = f"tenant_{db_tenant.id}"
    db.execute(text(f"DROP SCHEMA {schema_name} CASCADE"))
    db.commit()
    
    db.delete(db_tenant)
    db.commit()
    db.close()
    return {"detail": "Tenant deleted"}

