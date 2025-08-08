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

# Create simplified model stubs that will work in RunPod environment
RUN python3.10 -c "
import os

# Create wav2lip.py stub
wav2lip_content = '''#!/usr/bin/env python3
import os
import logging

logger = logging.getLogger(__name__)

class Wav2LipModel:
    def __init__(self, checkpoint_path: str, device: str = \"cuda\"):
        self.device = device
        self.checkpoint_path = checkpoint_path
        logger.info(\"Wav2Lip model stub initialized\")
    
    def generate(self, video_path: str, audio_path: str, output_path: str) -> str:
        logger.info(f\"Wav2Lip processing: {video_path} + {audio_path}\")
        # Basic audio-video combination using moviepy
        try:
            import moviepy.editor as mpe
            video = mpe.VideoFileClip(video_path)
            audio = mpe.AudioFileClip(audio_path)
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            final = video.set_audio(audio)
            final.write_videofile(output_path, codec=\"libx264\", audio_codec=\"aac\", verbose=False, logger=None)
            final.close()
            video.close()
            audio.close()
            return output_path
        except Exception as e:
            logger.error(f\"Wav2Lip fallback failed: {e}\")
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path
'''

with open('/app/models/wav2lip.py', 'w') as f:
    f.write(wav2lip_content)

# Create face_expression.py stub
face_expr_content = '''#!/usr/bin/env python3
import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FacialExpressionModel:
    def __init__(self, model_path: str, device: str = \"cuda\"):
        self.device = device
        self.model_path = model_path
        logger.info(\"Facial expression model stub initialized\")
    
    def enhance_video(self, video_path: str, output_path: str) -> str:
        logger.info(f\"Enhancing facial expressions: {video_path}\")
        try:
            # Basic video processing with OpenCV
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*\"mp4v\")
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply basic sharpening
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                sharpened = cv2.filter2D(frame, -1, kernel)
                enhanced = cv2.addWeighted(frame, 0.7, sharpened, 0.3, 0)
                out.write(enhanced)
            
            cap.release()
            out.release()
            return output_path
            
        except Exception as e:
            logger.error(f\"Face enhancement failed: {e}\")
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path
'''

with open('/app/models/face_expression.py', 'w') as f:
    f.write(face_expr_content)

print('Model files created successfully')
"

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

ENTRYPOINT ["python3.10", "-u", "runpod_handler.py"]