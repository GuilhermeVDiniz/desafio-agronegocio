# 🌱 Desafio Agronegócio — Plataforma de Dados

Este é um projeto para o setor de **agronegócio**, dividido em dois módulos principais:

- **API Backend (FastAPI):** coleta, processamento e disponibilização de dados agrícolas
- **Dashboard Web (Frontend):** interface interativa para consulta e visualização dos dados

A solução foi criada com foco em facilitar a análise de informações do setor agrícola.

---

## ⚙️ Tecnologias Utilizadas

### 🖥️ Backend (API)

- [FastAPI](https://fastapi.tiangolo.com/) — Framework Python para construção da API
- [Uvicorn](https://www.uvicorn.org/) — Servidor ASGI para executar a API
- [Pandas](https://pandas.pydata.org/) — Tratamento e análise dos dados
- [SidraPy](https://pypi.org/project/sidrapy/) — Coleta de dados da API SIDRA/IBGE
- [Docker](https://www.docker.com/) e **Docker Compose** — Containerização e orquestração
### 🌐 Frontend (Dashboard Web)

- [JavaScript](https://developer.mozilla.org/docs/Web/JavaScript) — Lógica da interface e consumo da API
- [Chart.js](https://www.chartjs.org/) — Gráficos interativos para visualização dos dados
- [leafletjs](https://leafletjs.com/) — Biblioteca para mapas interativos

---

## 🛠️ Configuração do Ambiente de Desenvolvimento

### 1. Clonar o Repositório

```bash
  git https://github.com/GuilhermeVDiniz/Desafio.git
  cd desafio-agronegocio
```

---

# 🛠️ Configuração do Ambiente

### Pré-requisitos

- **Python 3.10**
- **pip**
- **Docker e Docker Compose**
- **Git**
- **virtualenv**

## Ativar o ambiente virtual

```bash
  python3 -m venv venv
  source venv/bin/activate
```

## Instale as dependências

```bash
  pip install -r requirements.txt
```

## Executar o servidor localmente

```bash
  uvicorn app.main:app --reload
```

## Rodar o projeto com docker

```bash
  docker compose up --build
```

## Backend: Url base da API:
http://localhost:8000/api/

## Acessar a documentação da API:
http://localhost:8000/docs

## Acessar a documentação da API (redoc):
http://localhost:8000/redoc

# Frontend (Dashboard Web):
http://localhost:3000


# Referências e Fontes de Dados

## Links de Dados Utilizados

SIDRA / IBGE (Sistema IBGE de Recuperação Automática):
https://sidra.ibge.gov.br/

API oficial do IBGE usada para consultar dados estatísticos do agronegócio.

Documentação da API SIDRA (via SidraPy):
https://pypi.org/project/sidrapy/

Biblioteca Python utilizada para consumir os dados da API SIDRA.
 
## Links de Tecnologias de Apoio

FastAPI — Framework da API:
https://fastapi.tiangolo.com/

Uvicorn — Servidor ASGI:
https://www.uvicorn.org/

Pandas — Análise e Tratamento de Dados:
https://pandas.pydata.org/docs/

Chart.js — Gráficos no Frontend:
https://www.chartjs.org/docs/latest/

leafletjs — Mapas Interativos:
https://leafletjs.com/reference.html/

Docker Compose — Orquestração de containers:
https://docs.docker.com/compose/


