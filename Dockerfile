FROM python:3.12-slim-bookworm
#FROM pypy:3.10-7.3.17-bookworm
#FROM pypy:latest

ENV PYTHONUNBUFFERED=1 \
    #POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# `build-essential` required to build some wheels on newer Python versions, `openssh-client` required to clone some dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

# install psycopg2 dependencies and a few useful tools
RUN apt-get update && \
    apt-get install -y postgresql-server-dev-all gcc python3-dev musl-dev nano curl procps && \
    rm -rf /var/lib/apt/lists/*    

WORKDIR /app

RUN python -m pip install -U pip wheel && pip install poetry
RUN pip install "psycopg[c]"

# Copy source files
COPY . ./

# Rebuild Lock
RUN poetry lock

# Install production dependencies with poetry
#RUN poetry install --only main --no-interaction


RUN poetry install --with dev 

CMD ["python", "scripts/start_api_docker.py"]