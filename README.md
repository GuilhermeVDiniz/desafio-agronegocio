# 🌱 Desafio Agronegócio — Plataforma de Dados

Este é um projeto completo para o setor de **agronegócio**, dividido em dois módulos principais:

- **API Backend (FastAPI):** coleta, processamento e disponibilização de dados agrícolas
- **Dashboard Web (Frontend):** interface interativa para consulta e visualização dos dados

A solução foi criada com foco em facilitar a análise de informações do setor agrícola, permitindo que gestores, pesquisadores e produtores possam **explorar indicadores, filtrar dados e tomar decisões baseadas em evidências.**

---

## ⚙️ Tecnologias Utilizadas

### 🖥️ Backend (API)
- [FastAPI](https://fastapi.tiangolo.com/) — Framework Python para construção da API
- [Uvicorn](https://www.uvicorn.org/) — Servidor ASGI para executar a API
- [Pandas](https://pandas.pydata.org/) — Tratamento e análise dos dados
- [SidraPy](https://pypi.org/project/sidrapy/) — Coleta de dados da API SIDRA/IBGE
- [Docker](https://www.docker.com/) e **Docker Compose** — Containerização e orquestração
- [Pandas](https://pandas.pydata.org/docs/) — Manipulação e análise de dados de forma eficiente
  
### 🌐 Frontend (Dashboard Web)
- [JavaScript](https://developer.mozilla.org/docs/Web/JavaScript) — Lógica da interface e consumo da API
- [Chart.js](https://www.chartjs.org/) — Gráficos interativos para visualização dos dados
- [mapsvg](https://mapsvg.com/) — Biblioteca para mapas interativos
- [Axios](https://axios-http.com/) — Cliente HTTP para requisições à API
- [Vue.js](https://vuejs.org/) — Framework JavaScript para construção da interface

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

## Url base da API: 
http://localhost:8000/api/
## Acessar a documentação da API:
http://localhost:8000/docs
## Acessar a documentação da API (redoc):
http://localhost:8000/redoc