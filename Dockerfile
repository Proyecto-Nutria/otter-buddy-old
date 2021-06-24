FROM python:3.8-slim

LABEL MAINTAINER="Proyecto Nutria <contact@proyectonutria.com>"

WORKDIR /otter-buddy

COPY ./pyproject.toml ./pyproject.toml

RUN python3.8 -m pip install poetry
RUN python3.8 -m poetry install --no-dev

COPY . .

CMD [ "poetry", "run", "python", "-m", "otter_buddy"]