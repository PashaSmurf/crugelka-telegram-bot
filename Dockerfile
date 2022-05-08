FROM python:3.7-slim

# args
ARG TELEGRAM_API_TOKEN
ARG MYSQL_HOST
ARG MYSQL_LOGIN
ARG MYSQL_PASSWORD
ARG MYSQL_DATABASE

# envs
ENV TELEGRAM_API_TOKEN=${TELEGRAM_API_TOKEN}
ENV MYSQL_HOST=${MYSQL_HOST}
ENV MYSQL_LOGIN=${MYSQL_LOGIN}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD}
ENV MYSQL_DATABASE=${MYSQL_DATABASE}
WORKDIR /usr/src/app
RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install && \
    apt-get clean
COPY telegram_bot ./telegram_bot
EXPOSE 8080
ENTRYPOINT python3.7 -m telegram_bot.app
