# Etapa 1: build das dependências
ARG PYTHON_VERSION=3.10-slim
FROM python:${PYTHON_VERSION} as builder
LABEL maintainer="Guilherme Diniz"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia o requirements e gera os wheels
COPY requirements.txt .
RUN apt-get update && apt-get install -y g++ python3-dev \
    && ln -sf python3 /usr/bin/python \
    && pip3 install --upgrade pip setuptools wheel \
    && pip wheel -r requirements.txt -w /wheels

# Etapa 2: imagem final
FROM python:${PYTHON_VERSION}
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia os wheels e o requirements.txt
COPY --from=builder /wheels /wheels
COPY requirements.txt .

# Instala usando os wheels já baixados
RUN pip install -U pip \
    && pip install -r requirements.txt -f /wheels \
    && rm -rf /root/.cache/pip/*

# Copia o código da aplicação (pasta app/)
COPY ./app ./app

# Comando para rodar a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
