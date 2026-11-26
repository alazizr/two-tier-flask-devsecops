FROM python:3.11-slim

ENV PYTHONDONTWRITEBYCODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# add security patch debian os (libzstdl, dll) after that remove apt cache
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/list/*

# buat non-root system user sesuai standar CIS Docker benchmarark
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# copy requierment terlebih dahulu untuk memanfaatkan Docker layer caching
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y setuptools

# copy source code aplikasi dengan kepimilikan langsung
COPY --chown=appuser:appgroup app/ .

USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
