import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Exemplo de configuração
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
