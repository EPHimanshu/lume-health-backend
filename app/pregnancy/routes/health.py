from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "Lume Health Backend",
        "status": "healthy",
    }