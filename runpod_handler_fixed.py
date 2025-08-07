#!/usr/bin/env python3
"""
RunPod Serverless Handler - FIXED VERSION
Handles missing dependencies gracefully
"""

import runpod
import asyncio
import logging
import json
import traceback
import os
import time
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline = None
pipeline_mode = "minimal"  # minimal, basic, full

def check_dependencies():
    """Check what dependencies are available"""
    available = {
        "torch": False,
        "transformers": False,
        "diffusers": False,
        "cinema_pipeline": False,
        "script_processor": False,
        "human_sounds": False,
        "audiocraft": False,
        "tts": False
    }
    
    try:
        import torch
        available["torch"] = True
        logger.info(f"✅ PyTorch: {torch.__version__}")
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning("⚠️  No CUDA available")
    except ImportError:
        logger.error("❌ PyTorch not available")
    
    try:
        import transformers
        available["transformers"] = True
        logger.info(f"✅ Transformers: {transformers.__version__}")
    except ImportError:
        logger.warning("⚠️  Transformers not available")
    
    try:
        import diffusers
        available["diffusers"] = True
        logger.info(f"✅ Diffusers: {diffusers.__version__}")
    except ImportError:
        logger.warning("⚠️  Diffusers not available")
    
    try:
        from cinema_pipeline import CinemaPipeline
        available["cinema_pipeline"] = True
        logger.info("✅ Cinema Pipeline available")
    except ImportError as e:
        logger.warning(f"⚠️  Cinema Pipeline not available: {e}")
    
    try:
        from script_processor import DeepSeekScriptProcessor
        available["script_processor"] = True
        logger.info("✅ Script Processor available")
    except ImportError:
        logger.warning("⚠️  Script Processor not available")
    
    try:
        from human_sounds import HumanSoundsGenerator
        available["human_sounds"] = True
        logger.info("✅ Human Sounds available")
    except ImportError:
        logger.warning("⚠️  Human Sounds not available")
    
    try:
        from audiocraft.models import MusicGen
        available["audiocraft"] = True
        logger.info("✅ AudioCraft available")
    except ImportError:
        logger.warning("⚠️  AudioCraft not available")
    
    try:
        from TTS.api import TTS
        available["tts"] = True
        logger.info("✅ TTS available")
    except ImportError:
        logger.warning("⚠️  TTS not available")
    
    return available

def initialize_pipeline():
    """Initialize pipeline with graceful fallback"""
    global pipeline, pipeline_mode
    
    logger.info("="*60)
    logger.info("🎬 Cinema AI Production Pipeline v2.1 - FIXED")
    logger.info("="*60)
    
    # Check dependencies
    deps = check_dependencies()
    
    # Determine pipeline mode
    if deps["cinema_pipeline"] and deps["torch"] and deps["transformers"]:
        try:
            from cinema_pipeline import CinemaPipeline
            pipeline = CinemaPipeline()
            pipeline_mode = "full"
            logger.info("✅ Full pipeline initialized!")
        except Exception as e:
            logger.error(f"❌ Full pipeline failed: {e}")
            pipeline_mode = "basic"
    
    if pipeline_mode != "full" and deps["torch"] and deps["transformers"]:
        try:
            # Initialize basic pipeline
            pipeline = BasicPipeline()
            pipeline_mode = "basic"
            logger.info("✅ Basic pipeline initialized!")
        except Exception as e:
            logger.error(f"❌ Basic pipeline failed: {e}")
            pipeline_mode = "minimal"
    
    if pipeline_mode == "minimal":
        pipeline = MinimalPipeline()
        logger.info("✅ Minimal pipeline initialized!")
    
    logger.info(f"🎯 Running in {pipeline_mode} mode")
    logger.info("="*60)

class MinimalPipeline:
    """Minimal pipeline that always works"""
    
    def __init__(self):
        self.mode = "minimal"
        self.models = {}
    
    async def process_script(self, script: str, options: Dict) -> Dict:
        return {
            "error": "Script processing not available in minimal mode",
            "suggestion": "Check Docker dependencies and rebuild"
        }
    
    async def process_complete_scene(self, scene) -> Dict:
        return {
            "error": "Video generation not available in minimal mode",
            "suggestion": "Check Docker dependencies and rebuild"
        }
    
    async def develop_concept(self, concept: str, options: Dict) -> Dict:
        return {
            "error": "Concept development not available in minimal mode",
            "suggestion": "Check Docker dependencies and rebuild"
        }

class BasicPipeline:
    """Basic pipeline with core functionality"""
    
    def __init__(self):
        self.mode = "basic"
        self.models = {}
        
        # Try to initialize basic models
        try:
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Device: {self.device}")
        except:
            self.device = "cpu"
    
    async def process_script(self, script: str, options: Dict) -> Dict:
        # Basic script processing without DeepSeek
        scenes = self._parse_script_basic(script)
        return {
            "status": "success",
            "scenes": scenes,
            "mode": "basic",
            "note": "Using basic script parsing - DeepSeek not available"
        }
    
    def _parse_script_basic(self, script: str) -> List[Dict]:
        """Basic script parsing without AI"""
        scenes = []
        blocks = script.split("\n\n")
        
        for i, block in enumerate(blocks):
            if not block.strip():
                continue
                
            lines = block.strip().split("\n")
            description = lines[0] if lines else "Scene description"
            
            scene = {
                "id": f"scene_{i+1:03d}",
                "description": description,
                "duration": 10,
                "resolution": "720p",
                "fps": 30,
                "dialogue": [],
                "camera_movements": ["static shot"],
                "music_mood": "cinematic"
            }
            
            # Extract dialogue
            for line in lines[1:]:
                if ":" in line:
                    character, text = line.split(":", 1)
                    scene["dialogue"].append({
                        "character": character.strip(),
                        "text": text.strip()
                    })
            
            scenes.append(scene)
        
        return scenes
    
    async def process_complete_scene(self, scene) -> Dict:
        # Simulate video generation
        await asyncio.sleep(2)  # Simulate processing time
        
        return {
            "status": "success",
            "scene_id": getattr(scene, 'id', 'unknown'),
            "video_url": None,
            "audio_url": None,
            "processing_time": 2.0,
            "mode": "basic",
            "note": "Video generation not available - returning placeholder"
        }
    
    async def develop_concept(self, concept: str, options: Dict) -> Dict:
        # Basic concept development
        return {
            "status": "success",
            "concept": concept,
            "script_text": f"A story about: {concept}",
            "scenes": [],
            "mode": "basic",
            "note": "Basic concept processing - AI not available"
        }

async def process_job(job_input: Dict) -> Dict:
    """Main job processing function"""
    request_type = job_input.get("type", "script_to_video")
    
    logger.info(f"📋 Processing job type: {request_type} in {pipeline_mode} mode")
    
    try:
        if request_type == "health_check":
            # Comprehensive health check
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "pipeline_mode": pipeline_mode,
                "system": {
                    "gpu_available": False,
                    "device_count": 0,
                    "memory_allocated": 0,
                    "memory_cached": 0
                },
                "pipeline": {
                    "initialized": pipeline is not None,
                    "mode": pipeline.mode if pipeline else "not_initialized",
                    "models_loaded": list(pipeline.models.keys()) if pipeline else []
                },
                "capabilities": {
                    "video_generation": pipeline_mode == "full",
                    "music_generation": pipeline_mode == "full",
                    "sound_effects": pipeline_mode == "full",
                    "voice_cloning": pipeline_mode == "full",
                    "script_processing": pipeline_mode in ["full", "basic"],
                    "basic_responses": True
                }
            }
            
            # Add GPU info if available
            try:
                import torch
                if torch.cuda.is_available():
                    health_status["system"] = {
                        "gpu_available": True,
                        "device_count": torch.cuda.device_count(),
                        "memory_allocated": torch.cuda.memory_allocated() / 1024**3,
                        "memory_cached": torch.cuda.memory_cached() / 1024**3
                    }
                    health_status["gpu"] = {
                        "name": torch.cuda.get_device_name(0),
                        "vram_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
                        "vram_used_gb": torch.cuda.memory_allocated() / 1024**3
                    }
            except:
                pass
            
            return health_status
        
        elif request_type == "script_to_video":
            script = job_input.get("script", "")
            if not script:
                return {"error": "No script provided"}
            
            options = job_input.get("options", {})
            return await pipeline.process_script(script, options)
        
        elif request_type == "single_scene":
            scene_data = job_input.get("scene", {})
            
            # Create a simple scene object
            class SimpleScene:
                def __init__(self, data):
                    self.id = data.get("id", f"scene_{int(time.time())}")
                    self.description = data.get("description", "")
                    self.duration = data.get("duration", 5)
                    self.resolution = data.get("resolution", "720p")
                    self.fps = data.get("fps", 30)
            
            scene = SimpleScene(scene_data)
            return await pipeline.process_complete_scene(scene)
        
        elif request_type == "concept_to_script":
            concept = job_input.get("concept", "")
            if not concept:
                return {"error": "No concept provided"}
            
            options = job_input.get("options", {})
            return await pipeline.develop_concept(concept, options)
        
        elif request_type == "list_models":
            return {
                "status": "success",
                "pipeline_mode": pipeline_mode,
                "models": {
                    "video": ["HunyuanVideo-13B", "LTX-Video-13B"] if pipeline_mode == "full" else [],
                    "audio": ["MusicGen-Large", "AudioGen-Medium"] if pipeline_mode == "full" else [],
                    "tts": ["XTTS-v2"] if pipeline_mode == "full" else [],
                    "script": ["DeepSeek-v3"] if pipeline_mode == "full" else ["Basic Parser"],
                    "active": list(pipeline.models.keys()) if pipeline else []
                }
            }
        
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    except Exception as e:
        logger.error(f"Job processing error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "pipeline_mode": pipeline_mode,
            "traceback": traceback.format_exc()
        }

def handler(event):
    """RunPod serverless handler function"""
    try:
        input_data = event["input"]
        job_id = event.get("id", "unknown")
        
        logger.info(f"🎯 Job {job_id} started (mode: {pipeline_mode})")
        logger.info(f"Type: {input_data.get('type', 'unknown')}")
        
        # Process job
        result = asyncio.run(process_job(input_data))
        
        logger.info(f"✅ Job {job_id} completed")
        return result
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "pipeline_mode": pipeline_mode,
            "traceback": traceback.format_exc()
        }

# Initialize pipeline when module loads
try:
    initialize_pipeline()
except Exception as e:
    logger.error(f"Pipeline initialization failed: {e}")
    pipeline = MinimalPipeline()
    pipeline_mode = "minimal"

if __name__ == "__main__":
    logger.info("🚀 Starting RunPod Cinema AI Worker - FIXED VERSION")
    logger.info(f"Pipeline Mode: {pipeline_mode}")
    
    # Start the serverless worker
    runpod.serverless.start({"handler": handler})