from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import production, health_check, cultures

app = FastAPI(title="API - Agronegócio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# status
app.include_router(health_check.router, prefix="/api", tags=["Status"])

# data
app.include_router(production.router, prefix="/api/data", tags=["Dados Produção Agrícola"])

# opcoes
app.include_router(cultures.router, prefix="/api/opcoes/cultures", tags=["Opções"])
