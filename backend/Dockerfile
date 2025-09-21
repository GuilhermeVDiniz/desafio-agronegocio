FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y g++ python3-dev \
    && pip wheel --wheel-dir=/wheels -r requirements.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt -f /wheels

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
