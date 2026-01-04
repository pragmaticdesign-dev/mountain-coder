FROM python:3.12-slim-bookworm

# Install Java & wget
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk wget tar && \
    apt-get clean

RUN java -Xshare:dump

WORKDIR /app

# Install Python Deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Assets (Monaco + Marked)
# Logic: Create dirs -> Download Monaco -> Extract & Move -> Cleanup -> Download Marked
RUN mkdir -p static/lib && \
    # 1. Monaco Editor
    wget -q https://registry.npmjs.org/monaco-editor/-/monaco-editor-0.34.0.tgz && \
    tar -xzf monaco-editor-0.34.0.tgz && \
    mv package/min/vs static/ && \
    rm -rf package monaco-editor-0.34.0.tgz && \
    # 2. Marked.js
    wget -q -O static/lib/marked.min.js https://cdn.jsdelivr.net/npm/marked/marked.min.js

# Copy App Code (Overlays your local app files onto the /app directory)
COPY ./app /app

# ✅ NEW: Copy the import script so Docker can see it
COPY import_script.py .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]