# Usar una imagen base de Ubuntu
FROM ubuntu:20.04

# Establecer variables de entorno para evitar preguntas interactivas durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias y Python 3.10
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    build-essential \
    git \
    curl \
    wget \
    libxml2-dev \
    libxslt1-dev \
    libfontconfig \
    tree && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependencias
WORKDIR /app

# Crear un entorno virtual de Python
RUN python3.10 -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# pdftotext requires fontconfig runtime
RUN apt-get update && apt-get install -y libfontconfig && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/venv/bin:$PATH"

# The JSON schema is lazily generated at first usage, but we do it explicitly here for two reasons:
# - the schema will be already there when the container runs, saving the generation overhead when a container starts
# - derived images don't need to write the schema and can run with lower user privileges
RUN python3 -c "from haystack.utils.docker import cache_schema; cache_schema()"

# Haystack Preprocessor uses NLTK punkt model to divide text into a list of sentences.
# We cache these models for seamless user experience.
RUN python3 -c "from haystack.utils.docker import cache_nltk_model; cache_nltk_model()"

ENV SERVICE_NAME="haystackd"

# Haystack pipelines are run by the "haystackd" user.
# This helps keep the process and log management organized.
RUN addgroup --gid 1001 $SERVICE_NAME && \
    adduser --gid 1001 --uid 1001 --shell /bin/false --disabled-password $SERVICE_NAME && \
    mkdir -p /var/log/$SERVICE_NAME && \
    chown $SERVICE_NAME:$SERVICE_NAME /var/log/$SERVICE_NAME

# Create a folder for the /file-upload API endpoint with write permissions for the service user only
RUN mkdir -p /opt/file-upload && chown $SERVICE_NAME:$SERVICE_NAME /opt/file-upload && chmod 700 /opt/file-upload

# Tell rest_api which folder to use for uploads
ENV FILE_UPLOAD_PATH="/opt/file-upload"

ENV TIKA_LOG_PATH="/var/log/$SERVICE_NAME/"

# Instalar pdftotext al final para aprovechar la caché de capas anteriores
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

# The uvicorn server runs on port 8000, and it needs to be accessible from outside the container.
EXPOSE 8000

USER $SERVICE_NAME
CMD ["uvicorn", "rest_api.application:app",  "--host", "0.0.0.0"]
