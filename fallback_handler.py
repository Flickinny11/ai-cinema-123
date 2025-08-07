#!/usr/bin/env python3
"""
Fallback RunPod Handler
Works even if some dependencies are missing
"""

import runpod
import json
import logging
import time
import traceback
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
pipeline_available = False
pipeline = None

def initialize_pipeline():
    """Try to initialize the full pipeline, fallback to minimal mode"""
    global pipeline_available, pipeline
    
    logger.info("🎬 Cinema AI Pipeline - Initializing...")
    
    try:
        # Try to import the full pipeline
        from cinema_pipeline import CinemaPipeline
        pipeline = CinemaPipeline()
        pipeline_available = True
        logger.info("✅ Full pipeline initialized successfully")
        return True
    except ImportError as e:
        logger.warning(f"Full pipeline not available: {e}")
        logger.info("🔄 Falling back to minimal mode")
        pipeline_available = False
        return False
    except Exception as e:
        logger.error(f"Pipeline initialization failed: {e}")
        logger.info("🔄 Falling back to minimal mode")
        pipeline_available = False
        return False

def handler(event):
    """Main handler with fallback support"""
    try:
        input_data = event.get("input", {})
        job_id = event.get("id", "unknown")
        request_type = input_data.get("type", "test")

        logger.info(f"🎯 Job {job_id} - Type: {request_type}")

        # Health check
        if request_type == "health_check":
            return {
                "status": "healthy" if pipeline_available else "limited",
                "timestamp": time.time(),
                "pipeline_available": pipeline_available,
                "mode": "full" if pipeline_available else "fallback",
                "message": "Cinema AI Pipeline ready" if pipeline_available else "Running in fallback mode",
                "capabilities": {
                    "video_generation": pipeline_available,
                    "script_processing": pipeline_available,
                    "voice_cloning": pipeline_available,
                    "basic_response": True
                }
            }

        # If full pipeline is available, use it
        if pipeline_available and pipeline:
            try:
                # Import the full handler logic
                from runpod_handler import process_job
                import asyncio
                return asyncio.run(process_job(input_data))
            except Exception as e:
                logger.error(f"Full pipeline failed: {e}")
                # Fall through to minimal response

        # Minimal fallback responses
        if request_type == "script_to_video":
            return {
                "status": "error",
                "error": "Full pipeline not available. Video generation requires all dependencies.",
                "fallback_mode": True,
                "suggestion": "Check Docker build logs and ensure all packages installed correctly."
            }

        elif request_type == "single_scene":
            return {
                "status": "error", 
                "error": "Full pipeline not available. Scene generation requires all dependencies.",
                "fallback_mode": True,
                "suggestion": "Check Docker build logs and ensure all packages installed correctly."
            }

        else:
            # Basic test response
            return {
                "status": "success",
                "message": "Fallback handler working",
                "job_id": job_id,
                "input_received": input_data,
                "timestamp": time.time(),
                "fallback_mode": True,
                "note": "Full pipeline not available - running in minimal mode"
            }

    except Exception as e:
        logger.error(f"Handler error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time(),
            "fallback_mode": True,
            "traceback": traceback.format_exc()
        }

# Initialize on startup
try:
    initialize_pipeline()
except Exception as e:
    logger.error(f"Startup initialization failed: {e}")
    pipeline_available = False

if __name__ == "__main__":
    logger.info("🚀 Starting Cinema AI Handler (with fallback support)")
    logger.info(f"Pipeline available: {pipeline_available}")
    runpod.serverless.start({"handler": handler})