# Use PostgreSQL 17 base image
FROM postgres:17 AS postgres_base

# Copy schema and dump files into the container
#COPY .dump /docker-entrypoint-initdb.d/.dump
COPY .dump .dump

# Copy initialization scripts
COPY init_db.sh /docker-entrypoint-initdb.d/init_db.sh
RUN chmod +x /docker-entrypoint-initdb.d/init_db.sh