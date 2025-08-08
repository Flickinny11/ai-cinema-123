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

# Install essential audio dependencies
RUN python3.10 -m pip install --no-cache-dir \
    pydub==0.25.1 \
    moviepy==1.0.3 \
    torchaudio==2.0.2

# Install facial processing dependencies
RUN python3.10 -m pip install --no-cache-dir \
    mediapipe==0.10.9 \
    gfpgan==1.3.8 \
    basicsr==1.4.2 \
    realesrgan==0.3.0 \
    facexlib==0.3.0

# Install video processing dependencies
RUN python3.10 -m pip install --no-cache-dir \
    insightface==0.7.3 \
    onnxruntime==1.16.3

# Install additional dependencies that work
RUN python3.10 -m pip install --no-cache-dir \
    scipy==1.13.0 \
    imageio-ffmpeg==0.4.9 \
    audioread==3.0.1

# Install NLP dependencies for natural language processing
RUN python3.10 -m pip install --no-cache-dir \
    spacy==3.7.2 \
    spacy-transformers==1.3.4

# Download spaCy English model
RUN python3.10 -m spacy download en_core_web_sm

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
COPY natural_language_processor.py /app/
COPY cinema_pipeline.py /app/
COPY runpod_handler_production.py /app/runpod_handler.py
# Create models directory and files using Python
RUN mkdir -p /app/models

# Create models __init__.py
RUN echo '# Models package for Cinema AI Pipeline' > /app/models/__init__.py

# Create simplified model stubs using echo commands
RUN echo '#!/usr/bin/env python3' > /app/models/wav2lip.py && \
    echo 'import os' >> /app/models/wav2lip.py && \
    echo 'import logging' >> /app/models/wav2lip.py && \
    echo '' >> /app/models/wav2lip.py && \
    echo 'logger = logging.getLogger(__name__)' >> /app/models/wav2lip.py && \
    echo '' >> /app/models/wav2lip.py && \
    echo 'class Wav2LipModel:' >> /app/models/wav2lip.py && \
    echo '    def __init__(self, checkpoint_path: str, device: str = "cuda"):' >> /app/models/wav2lip.py && \
    echo '        self.device = device' >> /app/models/wav2lip.py && \
    echo '        self.checkpoint_path = checkpoint_path' >> /app/models/wav2lip.py && \
    echo '        logger.info("Wav2Lip model stub initialized")' >> /app/models/wav2lip.py && \
    echo '' >> /app/models/wav2lip.py && \
    echo '    def generate(self, video_path: str, audio_path: str, output_path: str) -> str:' >> /app/models/wav2lip.py && \
    echo '        logger.info(f"Wav2Lip processing: {video_path} + {audio_path}")' >> /app/models/wav2lip.py && \
    echo '        try:' >> /app/models/wav2lip.py && \
    echo '            import moviepy.editor as mpe' >> /app/models/wav2lip.py && \
    echo '            video = mpe.VideoFileClip(video_path)' >> /app/models/wav2lip.py && \
    echo '            audio = mpe.AudioFileClip(audio_path)' >> /app/models/wav2lip.py && \
    echo '            if audio.duration > video.duration:' >> /app/models/wav2lip.py && \
    echo '                audio = audio.subclip(0, video.duration)' >> /app/models/wav2lip.py && \
    echo '            final = video.set_audio(audio)' >> /app/models/wav2lip.py && \
    echo '            final.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)' >> /app/models/wav2lip.py && \
    echo '            final.close()' >> /app/models/wav2lip.py && \
    echo '            video.close()' >> /app/models/wav2lip.py && \
    echo '            audio.close()' >> /app/models/wav2lip.py && \
    echo '            return output_path' >> /app/models/wav2lip.py && \
    echo '        except Exception as e:' >> /app/models/wav2lip.py && \
    echo '            logger.error(f"Wav2Lip fallback failed: {e}")' >> /app/models/wav2lip.py && \
    echo '            import shutil' >> /app/models/wav2lip.py && \
    echo '            shutil.copy2(video_path, output_path)' >> /app/models/wav2lip.py && \
    echo '            return output_path' >> /app/models/wav2lip.py

RUN echo '#!/usr/bin/env python3' > /app/models/face_expression.py && \
    echo 'import os' >> /app/models/face_expression.py && \
    echo 'import cv2' >> /app/models/face_expression.py && \
    echo 'import numpy as np' >> /app/models/face_expression.py && \
    echo 'import logging' >> /app/models/face_expression.py && \
    echo '' >> /app/models/face_expression.py && \
    echo 'logger = logging.getLogger(__name__)' >> /app/models/face_expression.py && \
    echo '' >> /app/models/face_expression.py && \
    echo 'class FacialExpressionModel:' >> /app/models/face_expression.py && \
    echo '    def __init__(self, model_path: str, device: str = "cuda"):' >> /app/models/face_expression.py && \
    echo '        self.device = device' >> /app/models/face_expression.py && \
    echo '        self.model_path = model_path' >> /app/models/face_expression.py && \
    echo '        logger.info("Facial expression model stub initialized")' >> /app/models/face_expression.py && \
    echo '' >> /app/models/face_expression.py && \
    echo '    def enhance_video(self, video_path: str, output_path: str) -> str:' >> /app/models/face_expression.py && \
    echo '        logger.info(f"Enhancing facial expressions: {video_path}")' >> /app/models/face_expression.py && \
    echo '        try:' >> /app/models/face_expression.py && \
    echo '            import shutil' >> /app/models/face_expression.py && \
    echo '            shutil.copy2(video_path, output_path)' >> /app/models/face_expression.py && \
    echo '            return output_path' >> /app/models/face_expression.py && \
    echo '        except Exception as e:' >> /app/models/face_expression.py && \
    echo '            logger.error(f"Face enhancement failed: {e}")' >> /app/models/face_expression.py && \
    echo '            return video_path' >> /app/models/face_expression.py

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

ENTRYPOINT ["python3.10", "-u", "runpod_handler.py"]