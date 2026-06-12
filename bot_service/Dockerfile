FROM python:3.12-slim

WORKDIR /service

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv pip install --system -r pyproject.toml

COPY app ./app

EXPOSE 8001
# Команда переопределяется в docker-compose (api / bot / worker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
