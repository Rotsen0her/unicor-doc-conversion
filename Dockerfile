FROM python:3.11-slim

# torch/docling en CPU no necesitan compilar nada si dynamo/inductor están
# apagados — ver docs/17-08-2026/SPIKE-CONVERSION-ENGINE.md en backend_web_bot:
# en Windows esto rompe por falta de MSVC; en esta imagen Linux es defensivo,
# evita depender de que la imagen base tenga gcc/g++ instalados.
ENV TORCHDYNAMO_DISABLE=1 \
    TORCH_COMPILE_DISABLE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# opencv-python (dependencia transitiva de docling_ibm_models, usada para
# reconstruir tablas) está compilado contra libs gráficas de X11 aunque
# corra headless — sin esto falla en runtime con
# "ImportError: libxcb.so.1: cannot open shared object file" al procesar
# el primer PDF, no al instalar (pip install no lo detecta).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8100

HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=40s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
