# Production Cinema AI Pipeline - Optimized for RunPod
# Reduced layer sizes to avoid registry upload issues
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0" \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
    TORCH_BACKENDS_CUDNN_BENCHMARK=1 \
    HF_HOME=/models/cache \
    DIFFUSERS_CACHE=/models/diffusers \
    AUDIOCRAFT_CACHE_DIR=/models/audiocraft

# Set PATH and LD_LIBRARY_PATH
ENV PATH=/usr/local/cuda/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

# Install system dependencies in smaller chunks
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3.10-distutils python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    git git-lfs wget curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    build-essential cmake ninja-build pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libsndfile1 libsndfile1-dev libportaudio2 portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    sox libsox-dev libsox-fmt-all \
    libffi-dev libssl-dev libjpeg-dev libpng-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libtiff5-dev libfreetype6-dev liblcms2-dev libwebp-dev \
    libharfbuzz-dev libfribidi-dev libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    espeak espeak-data libespeak-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3.10 -m pip install --upgrade pip setuptools wheel

WORKDIR /app

# Install PyTorch first (largest dependency)
RUN python3.10 -m pip install --no-cache-dir \
    torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Install core ML packages
RUN python3.10 -m pip install --no-cache-dir \
    transformers==4.44.0 diffusers==0.30.0 accelerate==0.33.0

# Install essential packages
RUN python3.10 -m pip install --no-cache-dir \
    safetensors==0.4.4 sentencepiece==0.2.0 protobuf==4.25.3 \
    einops==0.8.0 einops-exts==0.0.4

# Install audio/video processing
RUN python3.10 -m pip install --no-cache-dir \
    soundfile==0.12.1 librosa==0.10.2 audioread==3.0.1 pydub==0.25.1

# Install computer vision
RUN python3.10 -m pip install --no-cache-dir \
    opencv-python==4.10.0.84 imageio==2.34.0 imageio-ffmpeg==0.4.9

# Install Hugging Face ecosystem
RUN python3.10 -m pip install --no-cache-dir \
    huggingface-hub==0.24.0 hf-transfer==0.1.6

# Install API and server components
RUN python3.10 -m pip install --no-cache-dir \
    fastapi==0.111.0 uvicorn==0.30.0 runpod==1.6.0 \
    pydantic==2.8.0 httpx==0.27.0

# Install LLM and script processing
RUN python3.10 -m pip install --no-cache-dir \
    openai==1.40.0 tiktoken==0.7.0

# Install utilities
RUN python3.10 -m pip install --no-cache-dir \
    psutil==6.0.0 tqdm==4.66.4 python-dotenv==1.0.1 rich==13.7.1

# Install missing critical dependencies
RUN python3.10 -m pip install --no-cache-dir \
    omegaconf==2.3.0 hydra-core==1.3.2 PyYAML==6.0.1

# Install AWS SDK for volume access
RUN python3.10 -m pip install --no-cache-dir \
    boto3==1.34.0 botocore==1.34.0

# Install optional packages with error handling
RUN python3.10 -m pip install --no-cache-dir moviepy==1.0.3 || echo "MoviePy failed"
RUN python3.10 -m pip install --no-cache-dir ffmpeg-python==0.2.0 || echo "FFmpeg-python failed"
RUN python3.10 -m pip install --no-cache-dir datasets==2.20.0 || echo "Datasets failed"
RUN python3.10 -m pip install --no-cache-dir anthropic==0.31.0 || echo "Anthropic failed"
RUN python3.10 -m pip install --no-cache-dir langchain==0.2.0 || echo "LangChain failed"

# Install problematic packages individually
RUN python3.10 -m pip install --no-cache-dir decord==0.6.0 || echo "Decord failed"
RUN python3.10 -m pip install --no-cache-dir av==12.3.0 || echo "PyAV failed"
RUN python3.10 -m pip install --no-cache-dir pyaudio==0.2.14 || echo "PyAudio failed"

# Enable HF Transfer for faster downloads
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# Create directories
RUN mkdir -p /models /models/cache /models/audiocraft /models/hunyuan /models/ltx \
    /models/musicgen /models/xtts /models/foley /app/output /app/temp

# Copy Python files in dependency order
COPY model_configs.yaml /app/
COPY script_processor.py /app/
COPY human_sounds.py /app/
COPY cinema_pipeline.py /app/
COPY download_models.py /app/
COPY runpod_handler_production.py /app/runpod_handler.py

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Pre-download essential models during build (if space allows)
RUN python3.10 -c "
import os
os.environ['HF_HOME'] = '/models/cache'
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'
from pathlib import Path
Path('/models').mkdir(exist_ok=True)
Path('/models/cache').mkdir(exist_ok=True)
print('Model directories created')
" || echo "Model setup failed"

WORKDIR /app

ENTRYPOINT ["python3.10", "-u", "runpod_handler.py"]
