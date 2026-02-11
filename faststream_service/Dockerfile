FROM python:3.13-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /faststream_app
ENV PYTHONPATH=/faststream_app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY faststream_app ./faststream_app
CMD ["python", "-m", "faststream_app.main"]
