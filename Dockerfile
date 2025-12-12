FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_PROJECT_ENVIRONMENT="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml ./

RUN uv lock

#RUN pip install torch==2.9.1 --index-url https://download.pytorch.org/whl/cpu --no-deps   старая скачать пипом
#ENV UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu через uv скачака 
RUN pip install torch==2.9.1 sentence-transformers --extra-index-url https://download.pytorch.org/whl/cpu

RUN uv sync --frozen


ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]