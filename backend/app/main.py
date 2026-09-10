import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from .database import Base, engine, SessionLocal
from .routers import auth, orders, master, dashboard, modules
from .services.seed import seed

app = FastAPI(title="BOS SYAMS API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(master.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(modules.router, prefix="/api")

@app.on_event("startup")
def startup():
    for _ in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                seed(db)
            finally:
                db.close()
            return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("Database unavailable")

@app.get("/api/health")
def health():
    return {"status":"ok"}
