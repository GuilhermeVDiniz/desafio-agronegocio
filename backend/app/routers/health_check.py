from fastapi import APIRouter

router = APIRouter()


@router.get("/health_check", tags=["Status"])
async def health_check():
    return {"status": "ok"}
