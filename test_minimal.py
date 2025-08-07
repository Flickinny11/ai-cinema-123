#!/usr/bin/env python3
"""
Minimal RunPod Handler for Initial Testing
This ensures RunPod can detect and sync the repository
"""

import runpod
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    """Minimal handler for RunPod detection testing"""
    try:
        input_data = event.get("input", {})
        job_id = event.get("id", "unknown")
        request_type = input_data.get("type", "test")

        logger.info(f"🎯 Job {job_id} - Type: {request_type}")

        if request_type == "health_check":
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "message": "Cinema AI Pipeline - Minimal Test Mode",
                "version": "1.0.0",
                "capabilities": ["basic_test", "health_check"]
            }
        
        return {
            "status": "success",
            "message": "Minimal handler working correctly",
            "job_id": job_id,
            "input_received": input_data,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

if __name__ == "__main__":
    logger.info("🚀 Starting Minimal Cinema AI Handler")
    runpod.serverless.start({"handler": handler})