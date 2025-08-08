# AI Cinema Production Pipeline

[![Deploy on RunPod](https://img.shields.io/badge/Deploy%20on-RunPod-6366f1)](https://runpod.io/console/deploy?template=cinema-ai-pipeline&ref=github)
[![Docker Build](https://img.shields.io/badge/Docker-Build%20Ready-2496ED)](https://github.com/Flickinny11/ai-cinema-123)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Production-ready AI video generation pipeline for RunPod serverless deployment.

## Features

- **Video Generation**: HunyuanVideo (13B) & LTX-Video (13B)
- **Audio Synthesis**: MusicGen-Large & AudioGen-Medium  
- **Voice Cloning**: XTTS-v2 with 6-second samples
- **Script Processing**: DeepSeek v3 integration
- **Human Sounds**: Realistic non-verbal audio effects
- **GPU Optimization**: Automatic VRAM-based model selection

## Quick Start

```bash
# Build image
docker build -t ai-cinema .

# Run locally
docker run --gpus all -p 8000:8000 ai-cinema

# Test health check
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"input": {"type": "health_check"}}'
```

## Deploy to RunPod

### Option 1: One-Click Deploy (Recommended)
[![Deploy on RunPod](https://img.shields.io/badge/Deploy%20on-RunPod-6366f1)](https://runpod.io/console/deploy?template=cinema-ai-pipeline&ref=github)

### Option 2: Manual Deploy
1. Go to [RunPod Console](https://runpod.io/console/serverless)
2. Click "New Template" 
3. Select "From GitHub"
4. Enter repository: `Flickinny11/ai-cinema-123`
5. Select latest release tag
6. Configure GPU: A100 40GB+ recommended
7. Set volume size: 50GB minimum
8. Deploy endpoint

### Option 3: Docker Registry
```bash
docker tag ai-cinema-working your-registry/ai-cinema:v1.0
docker push your-registry/ai-cinema:v1.0
```

## API Endpoints

- `health_check` - System status and GPU info
- `script_to_video` - Convert script to video scenes
- `single_scene` - Generate single video scene
- `concept_to_script` - Develop concept into full script

## GPU Requirements

- **Cinema Mode**: H100/A100 80GB (all models)
- **Balanced Mode**: A100 40GB (optimized models)  
- **Fast Mode**: RTX 4090/3090 24GB+ (quantized models)

Models download automatically on first startup.