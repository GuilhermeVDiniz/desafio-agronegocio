from fastapi import FastAPI
from app.routers import production, cities, cultures, analytics

app = FastAPI(title="API - Agronegócio")

app.include_router(production.router, prefix="/api/productions", tags=["Produção Agrícola"])
app.include_router(cities.router, prefix="/api/cities", tags=["Municípios"])
app.include_router(cultures.router, prefix="/api/cultures", tags=["Culturas"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Indicadores"])

