FROM python:3.9-slim

# Install Java & wget
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk wget tar && \
    apt-get clean

WORKDIR /app

# Install Python Deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Monaco Editor (Critical for offline UI)
RUN mkdir -p static && \
    wget https://registry.npmjs.org/monaco-editor/-/monaco-editor-0.34.0.tgz && \
    tar -xzf monaco-editor-0.34.0.tgz && \
    mv package/min/vs static/vs && \
    rm -rf package monaco-editor-0.34.0.tgz

# Copy App
COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]