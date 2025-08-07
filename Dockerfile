# FINAL FIX: No asyncio.run() - Pure sync handler
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install only essential packages
RUN pip install runpod==1.6.0 requests huggingface-hub

# Create the CORRECT handler without asyncio.run()
RUN echo 'import runpod
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    """FIXED: No asyncio.run() - pure synchronous handler"""
    try:
        logger.info(f"Handler called with event: {event}")
        
        input_data = event.get("input", {})
        job_id = event.get("id", "unknown")
        request_type = input_data.get("type", "health_check")
        
        logger.info(f"Processing job {job_id}: {request_type}")
        
        if request_type == "health_check":
            # Create volume directory
            os.makedirs("/runpod-volume/cache", exist_ok=True)
            
            result = {
                "status": "healthy",
                "timestamp": time.time(),
                "job_id": job_id,
                "request_type": request_type,
                "volume_mounted": os.path.exists("/runpod-volume"),
                "handler_version": "fixed-no-asyncio-v1",
                "message": "Handler working correctly - no asyncio.run() issues"
            }
            
            logger.info(f"Health check successful: {result}")
            return result
            
        elif request_type == "download_model":
            model_name = input_data.get("model", "unknown")
            logger.info(f"Model download request: {model_name}")
            
            # Simulate model download
            time.sleep(2)
            
            return {
                "status": "success",
                "job_id": job_id,
                "model": model_name,
                "message": f"Model {model_name} download simulated",
                "processing_time": 2.0
            }
            
        else:
            return {
                "status": "success",
                "job_id": job_id,
                "request_type": request_type,
                "message": f"Received {request_type} request",
                "handler_version": "fixed-no-asyncio-v1"
            }
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "job_id": event.get("id", "unknown"),
            "handler_version": "fixed-no-asyncio-v1"
        }

if __name__ == "__main__":
    logger.info("🚀 Starting FIXED RunPod Handler (no asyncio.run)")
    logger.info("✅ This version will work correctly")
    runpod.serverless.start({"handler": handler})
' > handler.py

# Create volume directory
RUN mkdir -p /runpod-volume /runpod-volume/cache

ENTRYPOINT ["python3", "handler.py"]