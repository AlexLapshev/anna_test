FROM postgres:latest

RUN apt-get update

ENV POSTGRES_DB anna_test_db
ENV POSTGRES_USER anna_test_user
ENV POSTGRES_PASSWORD 123456

COPY initdb.sql /docker-entrypoint-initdb.d/init.sql

VOLUME /var/lib/postgresql/data

EXPOSE 5432