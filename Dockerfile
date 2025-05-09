FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    dnsutils \
    iputils-ping \
    ffmpeg \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip config set global.timeout 100

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]