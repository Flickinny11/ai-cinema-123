# Production Cinema AI Pipeline - H100/A100 80GB Optimized
# Updated August 2025 with latest models
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

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3-pip \
    git \
    git-lfs \
    wget \
    curl \
    ffmpeg \
    build-essential \
    libsndfile1 \
    libsndfile1-dev \
    libportaudio2 \
    portaudio19-dev \
    sox \
    libsox-dev \
    libsox-fmt-all \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3.10 -m pip install --upgrade pip setuptools wheel

WORKDIR /app

# Install PyTorch 2.3.0 with CUDA 12.1
RUN python3.10 -m pip install --no-cache-dir \
    torch==2.3.0 \
    torchvision==0.18.0 \
    torchaudio==2.3.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Install core ML packages
RUN python3.10 -m pip install --no-cache-dir \
    transformers==4.44.0 \
    diffusers==0.30.0 \
    accelerate==0.33.0 \
    safetensors==0.4.4 \
    sentencepiece==0.2.0 \
    protobuf==4.25.3

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Install Python packages in optimized order
RUN python3.10 -m pip install --no-cache-dir -r requirements.txt

# Enable HF Transfer for faster downloads
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# Create directories
RUN mkdir -p /models /models/cache /models/audiocraft /models/hunyuan /models/ltx \
    /models/musicgen /models/xtts /models/foley /app/output /app/temp

# Copy Python files
COPY cinema_pipeline.py /app/
COPY runpod_handler.py /app/
COPY download_models.py /app/
COPY model_configs.yaml /app/
COPY script_processor.py /app/
COPY human_sounds.py /app/

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

WORKDIR /app

# Download base models during build (optional - comment out for faster builds)
# RUN python3.10 download_models.py --base-only

ENTRYPOINT ["python3.10", "-u", "runpod_handler.py"]
