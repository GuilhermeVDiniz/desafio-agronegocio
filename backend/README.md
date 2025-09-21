# Backend - Agronegócio API

API FastAPI para análise de dados agrícolas do SIDRA-IBGE.

## Requisitos

- Python 3.8+
- Docker

## Instalação

### Ambiente Virtual
```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # venv\Scripts\activate   # Windows
    pip install -r requirements.txt
```

### Execução Local
```bash
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
# Build da imagem
  docker build -t backend-agronegocio .
  
# Executar container
  docker run -p 8000:8000 backend-agronegocio
```

## Endpoints

- **API Base**: `http://localhost:8000/api/`
- **Documentação**: `http://localhost:8000/docs`

## Principais Rotas

```
GET  /api/data/                    # Buscar dados de produção
GET  /api/opcoes/cultures/         # Listar culturas disponíveis
GET  /api/health_check             # Status da API
```

## Filtros Disponíveis

- `ano`: Ano da consulta (2021-2024)
- `cultura`: Código da cultura (ex: 2713 para Soja)

## Exemplo de Uso

```bash
  curl "http://localhost:8000/api/data/?ano=2024&cultura=2713"
```