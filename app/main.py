from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.pregnancy.routes.health import router as health_router
from app.pregnancy.routes.clicks import router as clicks_router
from app.pregnancy.routes.tools import router as tools_router

from app.pregnancy import models  # noqa: F401

app = FastAPI(
    title="Lume Health Backend",
    description="Backend services for Lume Health tools, calculators, and comparison workflows.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict:
    return {
        "ok": True,
        "service": "Lume Health Backend",
        "message": "API is running",
    }


app.include_router(health_router, tags=["Health"])
app.include_router(clicks_router, tags=["Clicks"])
app.include_router(tools_router, tags=["Tools"])