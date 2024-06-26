FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# `build-essential` required to build some wheels on newer Python versions, `openssh-client` required to clone some dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install "bootstrap" dependencies (wheel and poetry)
RUN python -m pip install -U pip wheel && pip install poetry

# Copy source files
COPY . ./

# Install production dependencies with poetry
RUN poetry install 

# build database
RUN python scripts/test_deploy/initialize_db.py

# run tests
CMD ["poetry", "run", "tox"]