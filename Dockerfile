# Better handler with error handling
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install runpod==1.6.0 requests

RUN echo 'import runpod
import logging
import time
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    try:
        logger.info(f"Handler called with: {event}")
        
        input_data = event.get("input", {})
        request_type = input_data.get("type", "health_check")
        
        logger.info(f"Processing: {request_type}")
        
        result = {
            "status": "healthy",
            "timestamp": time.time(),
            "request_type": request_type,
            "message": "Better handler with logging",
            "version": "better-v1"
        }
        
        logger.info(f"Returning: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    logger.info("Starting better handler...")
    runpod.serverless.start({"handler": handler})
' > handler.py

ENTRYPOINT ["python3", "handler.py"]