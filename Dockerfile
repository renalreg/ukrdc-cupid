FROM python:3.11-bookworm-slim

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
    apt-get install -y postgresql-server-dev-all gcc python3-dev musl-dev && \
    rm -rf /var/lib/apt/lists/*    

WORKDIR /app

# Install "bootstrap" dependencies (wheel and poetry)
RUN python -m pip install -U pip wheel && pip install poetry

# Copy source files
COPY . ./

# Rebuild Lock
RUN poetry lock

# Install production dependencies with poetry
#RUN poetry install --only main --no-interaction

#RUN source /app/.venv/bin/activate
#RUN
RUN python -m pip install .

CMD ["python", "scripts/test_deploy/initialise_db.py"]
#CMD ["poetry", "run", "uvicorn", "ukrdc_xml_converter.api:app", "--host", "0.0.0.0", "--port", "8000"]