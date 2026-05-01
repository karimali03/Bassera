# ---------------------------------------------------------------------------
# Baseera Hybrid Forecasting System — Docker Image
#
# Designed for Hugging Face Docker Spaces.
# The app listens on port 7860 as required by HF infrastructure.
# ---------------------------------------------------------------------------

FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr (important for container logs)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# --- Install dependencies first (Docker layer caching) ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Copy project files ---
COPY . .

# --- Expose the Hugging Face required port ---
EXPOSE 7860

# --- Run the FastAPI server ---
# Hugging Face Spaces requires the app to bind to 0.0.0.0:7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
