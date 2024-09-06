# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies and PostgreSQL client, development files, gcc, and git
RUN apt-get update && apt-get install -y \
    postgresql-client \
    postgresql-server-dev-all \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Install Python dependencies
RUN poetry config virtualenvs.create false && poetry install --only main  --no-root --no-interaction --no-ansi


# Make port 8000 available to the world outside this container
EXPOSE 8000

CMD ["bash", "-c", "poetry run python scripts/test_deploy/initialise_db.py"]