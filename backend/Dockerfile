FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and GL libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install extra dependencies
RUN pip install --no-cache-dir \
    scikit-learn \
    pandas \
    numpy \
    scikit-fuzzy \
    ultralytics \
    opencv-python \
    pillow \
    paho-mqtt \
    shapely \
    python-multipart

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
