# Production Cinema AI Pipeline - Fixed Build
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
    HF_HOME=/runpod-volume/cache \
    HF_HUB_ENABLE_HF_TRANSFER=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3-pip \
    git wget curl ffmpeg \
    build-essential cmake \
    libsndfile1 libportaudio2 \
    espeak espeak-data libespeak-dev \
    sox libsox-dev libsox-fmt-all \
    rustc cargo \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip
RUN python3.10 -m pip install --upgrade pip

WORKDIR /app

# Install PyTorch first (compatible version)
RUN python3.10 -m pip install --no-cache-dir \
    torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu121

# Install core dependencies directly
RUN python3.10 -m pip install --no-cache-dir \
    transformers==4.44.0 \
    diffusers==0.30.0 \
    accelerate==0.33.0 \
    safetensors==0.4.4 \
    huggingface-hub==0.24.0 \
    hf-transfer==0.1.6 \
    einops==0.8.0

RUN python3.10 -m pip install --no-cache-dir \
    numpy==1.24.3 \
    opencv-python==4.10.0.84 \
    soundfile==0.12.1 \
    librosa==0.10.2 \
    imageio==2.34.0

RUN python3.10 -m pip install --no-cache-dir \
    runpod==1.6.0 \
    fastapi==0.111.0 \
    pydantic==2.8.0 \
    requests==2.32.0

RUN python3.10 -m pip install --no-cache-dir \
    omegaconf==2.3.0 \
    PyYAML==6.0.1 \
    python-dotenv==1.0.1 \
    openai==1.40.0

# Install essential audio dependencies (minimal working set)
RUN python3.10 -m pip install --no-cache-dir \
    pydub==0.25.1 \
    moviepy==1.0.3 \
    torchaudio==2.0.2

# Skip TTS and AudioCraft for now - focus on video generation first
# These can be added in a future version once we have a working base

# Install additional dependencies that work
RUN python3.10 -m pip install --no-cache-dir \
    scipy==1.13.0 \
    imageio-ffmpeg==0.4.9 \
    audioread==3.0.1

# Install additional ML dependencies
RUN python3.10 -m pip install --no-cache-dir \
    sentencepiece==0.2.0 \
    protobuf==4.25.3

# Create necessary directories
RUN mkdir -p /runpod-volume /runpod-volume/cache /app/output

# Copy application files
COPY model_configs.yaml /app/
COPY script_processor.py /app/
COPY human_sounds.py /app/
COPY cinema_pipeline.py /app/
COPY runpod_handler_production.py /app/runpod_handler.py

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

ENTRYPOINT ["python3.10", "-u", "runpod_handler.py"]