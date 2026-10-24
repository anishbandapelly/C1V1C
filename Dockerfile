# C1V1C - Tulabhara AI: Streamlit workspace + engine (offline-first; AWS via the runtime's role/env).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    C1V1C_ROOT=/app PYTHONPATH=/app/src C1V1C_RUNS_DIR=/app/runs C1V1C_OFFLINE_MODE=true AWS_REGION=ap-south-2
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src ./src
COPY app.py ./
COPY ui ./ui
COPY static ./static
COPY .streamlit ./.streamlit
COPY config ./config
# The curated baseline is produced by `python -m c1v1c.pipeline` and is not in Git (licence review pending).
COPY data/curated/bengaluru_pilot_v1 ./data/curated/bengaluru_pilot_v1

RUN useradd --create-home --uid 10001 c1v1c && mkdir -p /app/runs && chown -R c1v1c /app/runs
USER c1v1c
EXPOSE 8501 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health',timeout=4).read()==b'ok' else 1)"
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
