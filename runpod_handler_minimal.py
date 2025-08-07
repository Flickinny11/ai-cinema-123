#!/usr/bin/env python3
"""
RunPod Serverless Handler - Minimal Working Version
Guaranteed to build and run
"""

import runpod
import logging
import json
import traceback
import os
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline = None

def initialize_pipeline():
    """Initialize pipeline with minimal dependencies"""
    global pipeline
    
    logger.info("🎬 Cinema AI Minimal Pipeline")
    logger.info("="*50)
    
    try:
        # Check PyTorch
        import torch
        logger.info(f"✅ PyTorch: {torch.__version__}")
        logger.info(f"✅ CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"✅ GPU: {gpu_name}")
            logger.info(f"✅ VRAM: {vram:.1f}GB")
        
        # Create minimal pipeline
        pipeline = MinimalPipeline()
        logger.info("✅ Minimal pipeline initialized")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline initialization failed: {e}")
        return False

class MinimalPipeline:
    """Minimal working pipeline"""
    
    def __init__(self):
        self.mode = "minimal"
        self.models = {}
        
        # Set up directories
        os.makedirs("/runpod-volume/cache", exist_ok=True)
        os.makedirs("/app/output", exist_ok=True)
    
    def health_check(self):
        """Return health status"""
        try:
            import torch
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "pipeline_mode": self.mode,
                "gpu_available": torch.cuda.is_available(),
                "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
                "vram_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 0,
                "volume_mounted": os.path.exists("/runpod-volume"),
                "models_loaded": list(self.models.keys()),
                "message": "Minimal pipeline running - models need to be downloaded"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def download_model(self, model_name):
        """Download a model"""
        logger.info(f"📥 Download request for {model_name}")
        
        # Model configurations
        models = {
            "ltx": {
                "repo_id": "Lightricks/LTX-Video",
                "cache_dir": "/runpod-volume/ltx"
            },
            "hunyuan": {
                "repo_id": "tencent/HunyuanVideo",
                "cache_dir": "/runpod-volume/hunyuan"
            }
        }
        
        if model_name not in models:
            return {"error": f"Unknown model: {model_name}"}
        
        try:
            config = models[model_name]
            cache_dir = Path(config["cache_dir"])
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if already downloaded
            marker_file = cache_dir / f".{model_name}_downloaded"
            if marker_file.exists():
                logger.info(f"✅ {model_name} already downloaded")
                return {"status": "already_downloaded", "model": model_name}
            
            # Download using huggingface_hub
            from huggingface_hub import snapshot_download
            
            logger.info(f"🔄 Downloading {config['repo_id']}...")
            
            snapshot_download(
                repo_id=config["repo_id"],
                cache_dir=config["cache_dir"],
                resume_download=True,
                local_dir_use_symlinks=False,
                ignore_patterns=["*.md", "*.py", "*.git*"]
            )
            
            # Create marker file
            marker_file.touch()
            
            logger.info(f"✅ {model_name} downloaded successfully")
            return {"status": "success", "model": model_name}
            
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return {"error": f"Download failed: {str(e)}"}
    
    def generate_video(self, scene_data):
        """Generate video (placeholder)"""
        logger.info("🎬 Video generation request received")
        
        # Check if models are available
        ltx_marker = Path("/runpod-volume/ltx/.ltx_downloaded")
        hunyuan_marker = Path("/runpod-volume/hunyuan/.hunyuan_downloaded")
        
        if not ltx_marker.exists() and not hunyuan_marker.exists():
            return {
                "error": "No video models available",
                "suggestion": "Download models first using download_model request"
            }
        
        # Simulate video generation
        time.sleep(2)
        
        return {
            "status": "success",
            "scene_id": scene_data.get("id", "unknown"),
            "message": "Video generation placeholder - models need full integration",
            "processing_time": 2.0,
            "available_models": [
                "ltx" if ltx_marker.exists() else None,
                "hunyuan" if hunyuan_marker.exists() else None
            ]
        }

def process_job(job_input):
    """Process job synchronously"""
    request_type = job_input.get("type", "health_check")
    
    logger.info(f"📋 Processing: {request_type}")
    
    try:
        if request_type == "health_check":
            return pipeline.health_check() if pipeline else {"status": "error", "error": "Pipeline not initialized"}
        
        elif request_type == "download_model":
            model_name = job_input.get("model", "ltx")
            return pipeline.download_model(model_name) if pipeline else {"error": "Pipeline not initialized"}
        
        elif request_type == "single_scene":
            scene_data = job_input.get("scene", {})
            return pipeline.generate_video(scene_data) if pipeline else {"error": "Pipeline not initialized"}
        
        elif request_type == "list_models":
            return {
                "status": "success",
                "available_models": ["ltx", "hunyuan"],
                "downloaded_models": [
                    "ltx" if Path("/runpod-volume/ltx/.ltx_downloaded").exists() else None,
                    "hunyuan" if Path("/runpod-volume/hunyuan/.hunyuan_downloaded").exists() else None
                ]
            }
        
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    except Exception as e:
        logger.error(f"Job processing error: {e}")
        return {"status": "error", "error": str(e)}

def handler(event):
    """RunPod serverless handler - MINIMAL VERSION"""
    try:
        input_data = event["input"]
        job_id = event.get("id", "unknown")
        
        logger.info(f"🎯 Job {job_id}: {input_data.get('type', 'unknown')}")
        
        # Initialize pipeline if needed
        if pipeline is None:
            initialize_pipeline()
        
        # Process job
        result = process_job(input_data)
        
        logger.info(f"✅ Job {job_id} completed")
        return result
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"status": "error", "error": str(e)}

# Initialize on startup
try:
    os.environ.setdefault("HF_HOME", "/runpod-volume/cache")
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")
    initialize_pipeline()
except Exception as e:
    logger.error(f"Startup failed: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting RunPod Cinema AI Worker - Minimal")
    logger.info(f"Pipeline initialized: {pipeline is not None}")
    
    # Start the serverless worker
    runpod.serverless.start({"handler": handler})