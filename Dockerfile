FROM python:3.12.10-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 espeak-ng ffmpeg && rm -rf /var/lib/apt/lists/*
COPY backend/requirements*.txt /tmp/
ARG LOCAL_AI=false
RUN if [ "$LOCAL_AI" = true ]; then pip install --no-cache-dir -r /tmp/requirements-local.txt; else pip install --no-cache-dir -r /tmp/requirements.txt; fi
COPY backend/app /app/backend/app
COPY frontend /app/frontend
RUN useradd -u 10001 -m voiceops && mkdir /data /models && chown voiceops /data /models
USER voiceops
WORKDIR /app/backend
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","1","--ws-max-size","65536","--no-access-log"]
