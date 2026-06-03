FROM python:3.12-slim-bookworm
#FROM pypy:latest

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/app/.venv/bin:$PATH"

# `build-essential` required to build some wheels on newer Python versions, `openssh-client` required to clone some dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

# install psycopg2 dependencies
RUN apt-get update && \
    apt-get install -y postgresql-server-dev-all gcc python3-dev musl-dev nano curl procps && \
    rm -rf /var/lib/apt/lists/*    

WORKDIR /app

ENV PYTHONPATH=/app/src

RUN python -m pip install -U pip wheel \
    && pip install "poetry==1.8.5"

RUN pip install "psycopg[c]"


COPY pyproject.toml poetry.lock ./

RUN poetry install --with store,api,utils --no-root --no-ansi

COPY . ./

RUN poetry install --with store,api,utils --no-ansi

# Install production dependencies with poetry
#RUN poetry install --only main --no-interaction

CMD ["python", "scripts/start_api_docker.py"]