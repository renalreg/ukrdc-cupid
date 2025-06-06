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

# install psycopg2 dependencies
RUN apt-get update && \
    apt-get install -y postgresql-server-dev-all gcc python3-dev musl-dev nano curl procps && \
    rm -rf /var/lib/apt/lists/*    

WORKDIR /app

RUN python -m pip install -U pip wheel && pip install poetry
RUN pip install "psycopg[c]"

# Copy source files
COPY . ./

# Rebuild Lock
#RUN poetry lock

# Install dependencies with poetry
# Install core dependencies plus required groups
# - store: database access
# - api: web API functionality 
# - dev: development tools
RUN poetry install --with store,api,utils

#CMD ["python", "scripts/test_deploy/initialise_db.py"]
#CMD ["poetry", "run", "uvicorn", "ukrdc_xml_converter.api:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "scripts/start_api_docker.py"]