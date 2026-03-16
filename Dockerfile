FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./

# Provide a minimal package so pip can resolve local project metadata
# before the full source tree is copied in a later layer.
RUN mkdir -p app && touch app/__init__.py

RUN pip install --no-cache-dir ".[dev]"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
