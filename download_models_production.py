#!/usr/bin/env python3
"""
Production Model Downloader for RunPod Volume
Downloads all required models to persistent storage
"""

import os
import sys
import logging
import time
import boto3
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Volume configuration
VOLUME_ID = "wv11ilzha0"
S3_ENDPOINT = "https://s3api-us-ks-2.runpod.io"
S3_REGION = "us-ks-2"

# Model configurations with sizes
MODELS = {
    "ltx": {
        "repo_id": "Lightricks/LTX-Video",
        "cache_dir": "/runpod-volume/ltx",
        "size_gb": 35,
        "priority": 1,
        "essential": True
    },
    "hunyuan": {
        "repo_id": "tencent/HunyuanVideo", 
        "cache_dir": "/runpod-volume/hunyuan",
        "size_gb": 50,
        "priority": 2,
        "essential": True
    },
    "musicgen": {
        "repo_id": "facebook/musicgen-large",
        "cache_dir": "/runpod-volume/musicgen",
        "size_gb": 7,
        "priority": 3,
        "essential": False
    },
    "audiogen": {
        "repo_id": "facebook/audiogen-medium",
        "cache_dir": "/runpod-volume/audiogen", 
        "size_gb": 5,
        "priority": 4,
        "essential": False
    },
    "xtts": {
        "repo_id": "coqui/XTTS-v2",
        "cache_dir": "/runpod-volume/xtts",
        "size_gb": 2,
        "priority": 5,
        "essential": False
    }
}

class ModelDownloader:
    """Production model downloader with volume integration"""
    
    def __init__(self):
        self.downloaded_models = []
        self.failed_models = []
        self.total_size_gb = 0
        
        # Setup environment
        os.environ["HF_HOME"] = "/runpod-volume/cache"
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
        
    def check_volume_space(self):
        """Check available space on volume"""
        try:
            # Check disk space
            statvfs = os.statvfs("/runpod-volume")
            free_bytes = statvfs.f_frsize * statvfs.f_bavail
            free_gb = free_bytes / (1024**3)
            
            logger.info(f"📊 Available volume space: {free_gb:.1f}GB")
            
            # Calculate required space
            required_gb = sum(model["size_gb"] for model in MODELS.values())
            logger.info(f"📊 Required space: {required_gb}GB")
            
            if free_gb < required_gb:
                logger.warning(f"⚠️ Limited space - may need to download selectively")
                return False
            else:
                logger.info("✅ Sufficient space available")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to check volume space: {e}")
            return False
    
    def download_model(self, model_name: str, config: dict) -> bool:
        """Download a single model"""
        logger.info(f"📥 Downloading {model_name} ({config['size_gb']}GB)...")
        logger.info(f"   Repository: {config['repo_id']}")
        logger.info(f"   Cache dir: {config['cache_dir']}")
        
        try:
            # Create cache directory
            cache_dir = Path(config["cache_dir"])
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if already downloaded
            marker_file = cache_dir / f".{model_name}_downloaded"
            if marker_file.exists():
                logger.info(f"✅ {model_name} already downloaded")
                self.downloaded_models.append(model_name)
                return True
            
            # Download model
            start_time = time.time()
            
            snapshot_download(
                repo_id=config["repo_id"],
                cache_dir=config["cache_dir"],
                resume_download=True,
                local_dir_use_symlinks=False,
                ignore_patterns=["*.md", "*.py", "*.git*", "*.gitignore", "README*"]
            )
            
            download_time = time.time() - start_time
            
            # Create marker file
            marker_file.touch()
            
            # Log success
            logger.info(f"✅ {model_name} downloaded successfully!")
            logger.info(f"   Download time: {download_time:.1f}s")
            logger.info(f"   Size: ~{config['size_gb']}GB")
            
            self.downloaded_models.append(model_name)
            self.total_size_gb += config["size_gb"]
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {e}")
            self.failed_models.append(model_name)
            return False
    
    def download_essential_models(self):
        """Download only essential models"""
        logger.info("🎯 Downloading essential models only...")
        
        essential_models = {k: v for k, v in MODELS.items() if v["essential"]}
        
        for model_name in sorted(essential_models.keys(), key=lambda x: essential_models[x]["priority"]):
            config = essential_models[model_name]
            success = self.download_model(model_name, config)
            
            if not success and config["essential"]:
                logger.error(f"❌ Essential model {model_name} failed - this will impact functionality")
    
    def download_all_models(self):
        """Download all models in priority order"""
        logger.info("📥 Downloading all models...")
        
        # Sort by priority
        sorted_models = sorted(MODELS.items(), key=lambda x: x[1]["priority"])
        
        for model_name, config in sorted_models:
            success = self.download_model(model_name, config)
            
            # If essential model fails, continue but warn
            if not success and config["essential"]:
                logger.error(f"❌ Essential model {model_name} failed - continuing anyway")
    
    def verify_downloads(self):
        """Verify all downloaded models"""
        logger.info("🔍 Verifying model downloads...")
        
        verified = []
        missing = []
        
        for model_name, config in MODELS.items():
            cache_dir = Path(config["cache_dir"])
            marker_file = cache_dir / f".{model_name}_downloaded"
            
            if marker_file.exists() and cache_dir.exists():
                # Check if directory has content
                if any(cache_dir.iterdir()):
                    verified.append(model_name)
                    logger.info(f"✅ {model_name}: Verified")
                else:
                    missing.append(model_name)
                    logger.warning(f"❌ {model_name}: Directory empty")
            else:
                missing.append(model_name)
                logger.warning(f"❌ {model_name}: Not found")
        
        return verified, missing
    
    def create_model_manifest(self):
        """Create a manifest of downloaded models"""
        manifest = {
            "timestamp": time.time(),
            "downloaded_models": self.downloaded_models,
            "failed_models": self.failed_models,
            "total_size_gb": self.total_size_gb,
            "volume_id": VOLUME_ID
        }
        
        manifest_path = Path("/runpod-volume/model_manifest.json")
        
        try:
            import json
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"📋 Model manifest created: {manifest_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create manifest: {e}")
    
    def print_summary(self):
        """Print download summary"""
        logger.info("="*60)
        logger.info("📊 DOWNLOAD SUMMARY")
        logger.info("="*60)
        
        if self.downloaded_models:
            logger.info(f"✅ Successfully downloaded ({len(self.downloaded_models)}):")
            for model in self.downloaded_models:
                size = MODELS[model]["size_gb"]
                logger.info(f"   • {model}: ~{size}GB")
        
        if self.failed_models:
            logger.info(f"❌ Failed downloads ({len(self.failed_models)}):")
            for model in self.failed_models:
                essential = "ESSENTIAL" if MODELS[model]["essential"] else "optional"
                logger.info(f"   • {model}: {essential}")
        
        logger.info(f"📊 Total downloaded: ~{self.total_size_gb}GB")
        logger.info(f"🗂️ Volume ID: {VOLUME_ID}")
        logger.info("="*60)

def main():
    """Main download process"""
    logger.info("🚀 Cinema AI Production Model Downloader")
    logger.info("="*60)
    logger.info(f"Volume ID: {VOLUME_ID}")
    logger.info(f"S3 Endpoint: {S3_ENDPOINT}")
    logger.info("="*60)
    
    downloader = ModelDownloader()
    
    # Check volume space
    has_space = downloader.check_volume_space()
    
    # Download models
    if has_space:
        logger.info("🎯 Downloading all models...")
        downloader.download_all_models()
    else:
        logger.info("⚠️ Limited space - downloading essential models only...")
        downloader.download_essential_models()
    
    # Verify downloads
    verified, missing = downloader.verify_downloads()
    
    # Create manifest
    downloader.create_model_manifest()
    
    # Print summary
    downloader.print_summary()
    
    # Check if essential models are available
    essential_verified = [m for m in verified if MODELS[m]["essential"]]
    essential_missing = [m for m in missing if MODELS[m]["essential"]]
    
    if essential_missing:
        logger.error("❌ Essential models missing - endpoint may not function properly")
        logger.error(f"Missing: {essential_missing}")
        return False
    else:
        logger.info("✅ All essential models downloaded successfully!")
        logger.info("🎬 Cinema AI endpoint is ready for video generation!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)