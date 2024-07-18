# Stage 1: Base
FROM python:3.10-slim-buster as base

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git libpq-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install -U pip wheel && pip install poetry

COPY . ./

# Stage 2: Test
FROM base as test

RUN poetry install

CMD ["poetry", "run", "python", "scripts/test_deploy/initialize_db.py && poetry run tox"]

# Stage 3: Production
FROM base as prod

RUN poetry install --no-dev

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]