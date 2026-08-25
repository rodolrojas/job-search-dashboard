FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	FLASK_APP=app.py

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env .env

EXPOSE 5000

# Load environment variables from .env at runtime.
CMD ["sh", "-c", "set -a && . ./.env && set +a && exec flask run --host=0.0.0.0 --port=5000"]
