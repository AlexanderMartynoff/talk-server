FROM python:3.11-slim

EXPOSE 9090

COPY ./talk ./talk
COPY ./README.md .
COPY ./pyproject.toml .
COPY ./poetry.lock .

RUN pip install poetry && poetry install

CMD ["poetry", "run", "talk-server"]
