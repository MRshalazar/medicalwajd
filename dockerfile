FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gcc \
        rustc \
        cargo \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN python - <<'PY'
from pathlib import Path
req_file = Path('requirements.txt')
filtered = [
    line for line in req_file.read_text(encoding='utf-8').splitlines()
    if 'pywin32' not in line.lower() and 'pywin32-ctypes' not in line.lower()
]
Path('/tmp/requirements-docker.txt').write_text('\n'.join(filtered) + '\n', encoding='utf-8')
PY
RUN pip install --upgrade pip && pip install -r /tmp/requirements-docker.txt

COPY . .

RUN cd /app/zkp_engine && cargo build --release \
    && cp /app/zkp_engine/target/release/zkp_engine /usr/local/bin/zkp_engine \
    && chmod +x /usr/local/bin/zkp_engine

RUN mkdir -p /app/knowledge_mcp/chroma_db /app/RAG/chroma_db

EXPOSE 8002 8003 8004 8005 8007 8010 11434

CMD ["bash", "-lc", "python -m uvicorn --help >/dev/null 2>&1 || true; echo 'Base image ready. Override command in docker-compose.yml.'"]
