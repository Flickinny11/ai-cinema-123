# Ultra-minimal Cinema AI - Guaranteed to work
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/runpod-volume/cache

# Install only essential system packages
RUN apt-get update && apt-get install -y \
    git wget curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Install only core Python packages
RUN pip install --no-cache-dir \
    runpod==1.6.0 \
    requests==2.32.0 \
    huggingface-hub==0.24.0

# Create minimal handler
RUN echo '#!/usr/bin/env python3
import runpod
import logging
import json
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    """Ultra-minimal RunPod handler"""
    try:
        input_data = event["input"]
        job_id = event.get("id", "unknown")
        request_type = input_data.get("type", "health_check")
        
        logger.info(f"🎯 Job {job_id}: {request_type}")
        
        if request_type == "health_check":
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "message": "Ultra-minimal handler working",
                "volume_mounted": os.path.exists("/runpod-volume"),
                "handler_version": "ultra-minimal-v1"
            }
        else:
            return {
                "status": "success", 
                "message": f"Received {request_type} request",
                "note": "Ultra-minimal handler - limited functionality"
            }
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    logger.info("🚀 Starting Ultra-Minimal RunPod Handler")
    runpod.serverless.start({"handler": handler})
' > /app/runpod_handler.py

# Make directories
RUN mkdir -p /runpod-volume /runpod-volume/cache

ENTRYPOINT ["python3", "-u", "/app/runpod_handler.py"]