FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .

COPY . .

RUN pip install .

# RUN cd library_management
EXPOSE 8000
ENTRYPOINT ["sh", "./docker-entrypoint"]