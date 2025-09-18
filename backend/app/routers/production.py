from fastapi import APIRouter
from app.services.data_service import fetch_and_process_production_data

router = APIRouter()

@router.get("/{id_production}")
async def get_productions(id_production: str):
    data = fetch_and_process_production_data(id_production)
    return data
