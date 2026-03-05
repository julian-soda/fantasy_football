FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy shared CLI modules needed by the backend
COPY ff_luck.py yahoo_api.py espn_fetch.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
