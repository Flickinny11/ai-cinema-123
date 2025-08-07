#!/usr/bin/env python3
"""
RunPod Serverless Handler - Production Ready
August 2025 Edition
"""

import runpod  # Required for RunPod serverless
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

# Global pipeline instance - initialized once when worker starts
pipeline = None

def initialize_pipeline():
    """Initialize pipeline on worker startup"""
    global pipeline
    
    logger.info("="*60)
    logger.info("🎬 Cinema AI Production Pipeline v2.0")
    logger.info("="*60)
    
    try:
        # Import here to handle missing dependencies gracefully
        import torch
        from cinema_pipeline import CinemaPipeline, Scene, cleanup
        
        logger.info(f"PyTorch: {torch.__version__}")
        logger.info(f"CUDA Available: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"VRAM: {vram:.1f}GB")

            # Log model capabilities based on VRAM
            if vram >= 80:
                logger.info("✅ Full Cinema Mode: All models enabled")
                logger.info("  • HunyuanVideo (13B) - Cinema quality")
                logger.info("  • LTX-Video (13B) - Real-time generation")
                logger.info("  • MusicGen-Large - Orchestral music")
                logger.info("  • AudioGen-Medium - Sound effects")
                logger.info("  • XTTS-v2 - Voice cloning")
            elif vram >= 40:
                logger.info("⚡ Balanced Mode: Optimized models")
                logger.info("  • LTX-Video (13B) - Fast generation")
                logger.info("  • MusicGen-Medium - Music generation")
                logger.info("  • XTTS-v2 - Voice cloning")
            else:
                logger.info("🚀 Fast Mode: Consumer GPU optimized")
                logger.info("  • LTX-Video (Quantized) - Quick generation")
                logger.info("  • Basic audio models")
        else:
            logger.warning("No GPU detected - running in CPU mode (very slow)")

        logger.info("="*60)
        logger.info("Initializing pipeline...")

        pipeline = CinemaPipeline()

        logger.info("✅ Pipeline ready for production!")
        logger.info("="*60)
        
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.error("Running in minimal mode - some features disabled")
        pipeline = None
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        logger.error(traceback.format_exc())
        pipeline = None
        
# Initialize pipeline when module loads (RunPod best practice)
try:
    # Set environment variables for optimal performance
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:512")
    os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")
    os.environ.setdefault("HF_HOME", "/models/cache")
    os.environ.setdefault("DIFFUSERS_CACHE", "/models/diffusers")
    os.environ.setdefault("AUDIOCRAFT_CACHE_DIR", "/models/audiocraft")
    
    # Enable HF Transfer for faster downloads
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")
    
    initialize_pipeline()
except Exception as e:
    logger.error(f"Pipeline initialization failed: {e}")
    pipeline = None

async def process_script(job_input: Dict) -> Dict:
    """Process a full script into multiple scenes"""
    if not pipeline:
        return {"error": "Pipeline not initialized - check dependencies"}
        
    script = job_input.get("script", "")
    if not script:
        return {"error": "No script provided"}

    options = job_input.get("options", {})

    try:
        # Use DeepSeek to process script
        processed = await pipeline.process_script(script, options)
        scenes = processed['scenes']

        logger.info(f"📽️ Processing {len(scenes)} scenes from script")

        results = []
        total_start = time.time()

        for i, scene in enumerate(scenes):
            logger.info(f"Scene {i+1}/{len(scenes)}: {scene.id}")
            scene_start = time.time()

            try:
                result = await pipeline.process_complete_scene(scene)
                result["scene_number"] = i + 1
                result["scene_time"] = time.time() - scene_start
                results.append(result)

                # Log progress
                logger.info(f"  ✅ Scene {i+1} completed in {result['scene_time']:.1f}s")

            except Exception as e:
                logger.error(f"  ❌ Scene {i+1} failed: {e}")
                results.append({
                    "scene_id": scene.id,
                    "scene_number": i + 1,
                    "error": str(e)
                })

        total_time = time.time() - total_start

        return {
            "status": "success",
            "scenes": results,
            "total_scenes": len(scenes),
            "total_processing_time": total_time,
            "average_scene_time": total_time / len(scenes) if scenes else 0,
            "metadata": processed.get('metadata', {})
        }
    except Exception as e:
        logger.error(f"Script processing failed: {e}")
        return {"error": f"Script processing failed: {str(e)}"}

async def process_single_scene(job_input: Dict) -> Dict:
    """Process a single scene"""
    if not pipeline:
        return {"error": "Pipeline not initialized - check dependencies"}
        
    scene_data = job_input.get("scene", {})

    try:
        # Import Scene class here to handle missing dependencies
        from cinema_pipeline import Scene
        
        # Create Scene object from input
        scene = Scene(
            id=scene_data.get("id", f"scene_{int(time.time())}"),
            description=scene_data.get("description", ""),
            duration=scene_data.get("duration", 5),
            resolution=scene_data.get("resolution", "720p"),
            fps=scene_data.get("fps", 30),
            characters=scene_data.get("characters", []),
            dialogue=scene_data.get("dialogue", []),
            environment=scene_data.get("environment", ""),
            camera_movements=scene_data.get("camera_movements", []),
            sound_effects=scene_data.get("sound_effects", []),
            music_mood=scene_data.get("music_mood", ""),
            emotion_expressions=scene_data.get("emotion_expressions", []),
            voice_clone_samples=scene_data.get("voice_clone_samples", [])
        )

        logger.info(f"🎬 Processing single scene: {scene.id}")

        result = await pipeline.process_complete_scene(scene)

        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Single scene processing failed: {e}")
        return {"error": f"Single scene processing failed: {str(e)}"}

def parse_script_to_scenes(script: str, options: Dict) -> List:
    """Parse script text into Scene objects"""
    try:
        from cinema_pipeline import Scene
    except ImportError:
        return []
        
    scenes = []

    # Advanced parsing options
    scene_duration = options.get("scene_duration", 10)
    resolution = options.get("resolution", "720p")
    fps = options.get("fps", 30)
    style = options.get("style", "cinematic")

    # Simple parsing - split by double newlines or scene markers
    blocks = script.split("\n\n")

    for i, block in enumerate(blocks):
        if not block.strip():
            continue

        # Parse scene elements
        lines = block.strip().split("\n")
        description = lines[0]

        # Extract dialogue if present
        dialogue = []
        for line in lines[1:]:
            if ":" in line:  # Simple dialogue detection
                character, text = line.split(":", 1)
                dialogue.append({
                    "character": character.strip(),
                    "text": text.strip()
                })

        # Detect camera movements from description
        camera_movements = []
        if "pan" in description.lower():
            camera_movements.append("pan")
        if "zoom" in description.lower():
            camera_movements.append("zoom")
        if "tracking" in description.lower():
            camera_movements.append("tracking shot")

        # Detect mood from description
        music_mood = "cinematic"
        if "action" in description.lower():
            music_mood = "epic action"
        elif "romantic" in description.lower():
            music_mood = "romantic"
        elif "suspense" in description.lower():
            music_mood = "suspenseful"

        scene = Scene(
            id=f"scene_{i+1:03d}",
            description=description,
            duration=scene_duration,
            resolution=resolution,
            fps=fps,
            dialogue=dialogue,
            camera_movements=camera_movements or ["static shot"],
            music_mood=music_mood,
            environment=style
        )

        scenes.append(scene)

    return scenes

async def process_job(job_input: Dict) -> Dict:
    """Main job processing function"""
    request_type = job_input.get("type", "script_to_video")

    logger.info(f"📋 Processing job type: {request_type}")

    try:
        if request_type == "script_to_video":
            return await process_script(job_input)

        elif request_type == "concept_to_script":
            return await process_concept(job_input)

        elif request_type == "single_scene":
            return await process_single_scene(job_input)

        elif request_type == "batch_scenes":
            return await process_batch_scenes(job_input)

        elif request_type == "health_check":
            # Comprehensive health check
            try:
                import torch
                
                health_status = {
                    "status": "healthy",
                    "timestamp": time.time(),
                    "system": {
                        "gpu_available": torch.cuda.is_available() if 'torch' in locals() else False,
                        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                        "memory_allocated": torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0,
                        "memory_cached": torch.cuda.memory_cached() / 1024**3 if torch.cuda.is_available() else 0
                    },
                    "pipeline": {
                        "initialized": pipeline is not None,
                        "mode": pipeline.mode if pipeline else "not_initialized",
                        "models_loaded": list(pipeline.models.keys()) if pipeline else [],
                        "script_processor_available": pipeline and hasattr(pipeline, 'script_processor') and pipeline.script_processor is not None,
                        "human_sounds_available": pipeline and hasattr(pipeline, 'human_sounds') and pipeline.human_sounds is not None
                    }
                }
                
                if torch.cuda.is_available():
                    health_status["gpu"] = {
                        "name": torch.cuda.get_device_name(0),
                        "vram_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
                        "vram_used_gb": torch.cuda.memory_allocated() / 1024**3,
                        "vram_free_gb": (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / 1024**3
                    }
                
                if pipeline:
                    health_status["capabilities"] = {
                        "video_generation": "hunyuan" in pipeline.models or "ltx" in pipeline.models,
                        "music_generation": "musicgen" in pipeline.models,
                        "sound_effects": "audiogen" in pipeline.models,
                        "voice_cloning": "tts" in pipeline.models,
                        "script_processing": hasattr(pipeline, 'script_processor') and pipeline.script_processor is not None,
                        "human_sounds": hasattr(pipeline, 'human_sounds') and pipeline.human_sounds is not None,
                        "max_duration": 60 if pipeline.mode == "cinema" else 30 if pipeline.mode == "balanced" else 15,
                        "max_resolution": "4k" if pipeline.mode == "cinema" else "1080p" if pipeline.mode == "balanced" else "720p"
                    }
                
                return health_status
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "timestamp": time.time(),
                    "error": str(e),
                    "pipeline_initialized": pipeline is not None
                }

        elif request_type == "list_models":
            return {
                "status": "success",
                "models": {
                    "video": ["HunyuanVideo-13B", "LTX-Video-13B"],
                    "audio": ["MusicGen-Large", "AudioGen-Medium"],
                    "tts": ["XTTS-v2"],
                    "script": ["DeepSeek-v3"],
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
            "traceback": traceback.format_exc()
        }

async def process_concept(job_input: Dict) -> Dict:
    """Process a concept into a full script and videos"""
    if not pipeline:
        return {"error": "Pipeline not initialized - check dependencies"}
        
    concept = job_input.get("concept", "")
    if not concept:
        return {"error": "No concept provided"}

    options = job_input.get("options", {})

    logger.info(f"🎬 Developing concept: {concept[:100]}...")

    try:
        # Develop concept into script
        result = await pipeline.develop_concept(concept, options)

        # Process scenes into videos if requested
        if options.get("generate_videos", True) and "processed_scenes" in result:
            scenes = result["processed_scenes"]

            logger.info(f"📽️ Generating {len(scenes)} videos from concept")

            video_results = []
            for scene in scenes:
                try:
                    scene_result = await pipeline.process_complete_scene(scene)
                    video_results.append(scene_result)
                except Exception as e:
                    logger.error(f"Failed to generate video for scene: {e}")
                    video_results.append({"error": str(e)})

            result["videos"] = video_results

        return {
            "status": "success",
            "concept": concept,
            "script": result.get("script_text", ""),
            "scenes": result.get("processed_scenes", []),
            "videos": result.get("videos", []),
            "metadata": result.get("metadata", {})
        }
    except Exception as e:
        logger.error(f"Concept processing failed: {e}")
        return {"error": f"Concept processing failed: {str(e)}"}

async def process_batch_scenes(job_input: Dict) -> Dict:
    """Process multiple scenes in batch"""
    if not pipeline:
        return {"error": "Pipeline not initialized - check dependencies"}
        
    scenes_data = job_input.get("scenes", [])
    if not scenes_data:
        return {"error": "No scenes provided"}

    logger.info(f"📽️ Processing batch of {len(scenes_data)} scenes")

    try:
        # Import Scene class here to handle missing dependencies
        from cinema_pipeline import Scene
        
        results = []
        for scene_data in scenes_data:
            # Create Scene object
            scene = Scene(
                id=scene_data.get("id", f"batch_{int(time.time())}"),
                description=scene_data.get("description", ""),
                duration=scene_data.get("duration", 10),
                resolution=scene_data.get("resolution", "720p"),
                fps=scene_data.get("fps", 30),
                characters=scene_data.get("characters", []),
                dialogue=scene_data.get("dialogue", []),
                environment=scene_data.get("environment", ""),
                camera_movements=scene_data.get("camera_movements", []),
                sound_effects=scene_data.get("sound_effects", []),
                music_mood=scene_data.get("music_mood", ""),
                emotion_expressions=scene_data.get("emotion_expressions", []),
                voice_clone_samples=scene_data.get("voice_clone_samples", [])
            )

            # Add human sounds if specified
            if "human_sounds" in scene_data:
                scene.human_sounds = scene_data["human_sounds"]

            try:
                result = await pipeline.process_complete_scene(scene)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process scene {scene.id}: {e}")
                results.append({"scene_id": scene.id, "error": str(e)})

        return {
            "status": "success",
            "videos": results,
            "total_scenes": len(scenes_data)
        }
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return {"error": f"Batch processing failed: {str(e)}"}

def handler(event):
    """RunPod serverless handler function"""
    try:
        # Extract input data from the request (RunPod serverless pattern)
        input_data = event["input"]
        job_id = event.get("id", "unknown")

        logger.info(f"🎯 Job {job_id} started")
        logger.info(f"Type: {input_data.get('type', 'unknown')}")

        # Check if pipeline is initialized
        if not pipeline and input_data.get('type') != 'health_check':
            return {
                "status": "error",
                "error": "Pipeline not initialized - check dependencies and Docker environment"
            }

        # Process job (replace this with your own code)
        result = asyncio.run(process_job(input_data))

        # Cleanup resources after processing
        try:
            from cinema_pipeline import cleanup
            cleanup()
        except ImportError:
            # Cleanup function not available
            pass

        logger.info(f"✅ Job {job_id} completed successfully")

        # Return the result (RunPod serverless pattern)
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
    logger.info("🚀 Starting RunPod Cinema AI Worker")
    logger.info("Version: 2.0 - August 2025 Edition")
    logger.info("Models: HunyuanVideo, LTX-Video, MusicGen, AudioGen, XTTS-v2")
    
    # Log configuration
    logger.info(f"Pipeline initialized: {pipeline is not None}")
    if pipeline:
        logger.info(f"Pipeline mode: {pipeline.mode}")
    
    # Start the serverless worker (Required for RunPod)
    runpod.serverless.start({"handler": handler})  # Required
