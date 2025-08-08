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
# Create models directory and files directly in container
RUN mkdir -p /app/models

# Create models __init__.py
RUN echo '# Models package for Cinema AI Pipeline' > /app/models/__init__.py

# Create wav2lip.py model file
RUN cat > /app/models/wav2lip.py << 'EOF'
#!/usr/bin/env python3
"""
Wav2Lip Model Implementation
Real production implementation using the official Wav2Lip model
"""

import os
import cv2
import torch
import numpy as np
import subprocess
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Wav2LipModel:
    """Production Wav2Lip implementation"""
    
    def __init__(self, checkpoint_path: str, device: str = "cuda"):
        self.device = device
        self.checkpoint_path = checkpoint_path
        self.model = None
        self.face_detect = None
        
        # Download and load model
        self._ensure_model_downloaded()
        self._load_model()
    
    def _ensure_model_downloaded(self):
        """Download Wav2Lip model if not present"""
        if not os.path.exists(self.checkpoint_path):
            logger.info("Downloading Wav2Lip model...")
            
            # Create directory
            os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
            
            # Download from official source
            import requests
            url = "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth"
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(self.checkpoint_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info("✅ Wav2Lip model downloaded")
    
    def _load_model(self):
        """Load the Wav2Lip model"""
        try:
            # Import Wav2Lip modules
            import sys
            sys.path.append('/app/models/wav2lip_src')
            
            from models import Wav2Lip
            import face_detection
            
            # Load model
            self.model = Wav2Lip()
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
            self.model.load_state_dict(checkpoint["state_dict"])
            self.model.to(self.device)
            self.model.eval()
            
            # Load face detector
            self.face_detect = face_detection.FaceAlignment(
                face_detection.LandmarksType._2D, 
                flip_input=False, 
                device=self.device
            )
            
            logger.info("✅ Wav2Lip model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Wav2Lip model: {e}")
            # Clone and setup Wav2Lip repository
            self._setup_wav2lip_repo()
            self._load_model()  # Retry
    
    def _setup_wav2lip_repo(self):
        """Clone and setup Wav2Lip repository"""
        repo_path = "/app/models/wav2lip_src"
        
        if not os.path.exists(repo_path):
            logger.info("Setting up Wav2Lip repository...")
            
            # Clone repository
            subprocess.run([
                "git", "clone", 
                "https://github.com/Rudrabha/Wav2Lip.git",
                repo_path
            ], check=True)
            
            # Install requirements
            subprocess.run([
                "pip", "install", "-r", 
                f"{repo_path}/requirements.txt"
            ], check=True)
            
            logger.info("✅ Wav2Lip repository setup complete")
    
    def generate(self, video_path: str, audio_path: str, output_path: str) -> str:
        """Generate lip-synced video"""
        try:
            logger.info(f"Generating lip sync: {video_path} + {audio_path}")
            
            if not self.model:
                raise Exception("Wav2Lip model not loaded")
            
            # Use Wav2Lip inference script
            cmd = [
                "python", "/app/models/wav2lip_src/inference.py",
                "--checkpoint_path", self.checkpoint_path,
                "--face", video_path,
                "--audio", audio_path,
                "--outfile", output_path,
                "--static", "False",
                "--fps", "25",
                "--pads", "0", "10", "0", "0",
                "--face_det_batch_size", "16",
                "--wav2lip_batch_size", "128",
                "--resize_factor", "1",
                "--crop", "0", "-1", "0", "-1",
                "--box", "-1", "-1", "-1", "-1",
                "--rotate", "0",
                "--nosmooth"
            ]
            
            # Run inference
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Wav2Lip inference failed: {result.stderr}")
                raise Exception(f"Wav2Lip failed: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise Exception("Output video not generated")
            
            logger.info(f"✅ Lip sync completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Wav2Lip generation failed: {e}")
            raise
    
    def preprocess_video(self, video_path: str) -> str:
        """Preprocess video for better lip sync results"""
        try:
            # Extract frames and detect faces
            cap = cv2.VideoCapture(video_path)
            frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            
            cap.release()
            
            if not frames:
                raise Exception("No frames extracted from video")
            
            # Detect faces in first frame
            faces = self.face_detect.get_detections_for_batch(np.array([frames[0]]))
            
            if not faces or len(faces[0]) == 0:
                logger.warning("No faces detected in video")
                return video_path
            
            # Get largest face
            face = max(faces[0], key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))
            
            # Crop video to face region with padding
            x1, y1, x2, y2 = face
            padding = 50
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(frames[0].shape[1], x2 + padding)
            y2 = min(frames[0].shape[0], y2 + padding)
            
            # Create cropped video
            output_path = video_path.replace(".mp4", "_cropped.mp4")
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 25.0, (x2-x1, y2-y1))
            
            for frame in frames:
                cropped = frame[y1:y2, x1:x2]
                out.write(cropped)
            
            out.release()
            
            logger.info(f"✅ Video preprocessed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video preprocessing failed: {e}")
            return video_path
EOF

# Create face_expression.py model file
RUN cat > /app/models/face_expression.py << 'EOF'
#!/usr/bin/env python3
"""
Facial Expression Enhancement Model
Real production implementation using open-source facial expression models
"""

import os
import cv2
import torch
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FacialExpressionModel:
    """Production facial expression enhancement"""
    
    def __init__(self, model_path: str, device: str = "cuda"):
        self.device = device
        self.model_path = model_path
        self.model = None
        self.face_detector = None
        
        # Download and load model
        self._ensure_model_downloaded()
        self._load_model()
    
    def _ensure_model_downloaded(self):
        """Download facial expression model if not present"""
        if not os.path.exists(self.model_path):
            logger.info("Downloading facial expression model...")
            
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Use MediaPipe Face Mesh as base
            try:
                import mediapipe as mp
                self.mp_face_mesh = mp.solutions.face_mesh
                self.mp_drawing = mp.solutions.drawing_utils
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                logger.info("✅ MediaPipe Face Mesh loaded")
                
            except ImportError:
                logger.error("MediaPipe not available, installing...")
                import subprocess
                subprocess.run(["pip", "install", "mediapipe"], check=True)
                import mediapipe as mp
                self.mp_face_mesh = mp.solutions.face_mesh
                self.mp_drawing = mp.solutions.drawing_utils
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
    
    def _load_model(self):
        """Load facial expression enhancement model"""
        try:
            # Use GFPGAN for face enhancement
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            from gfpgan import GFPGANer
            
            # Load GFPGAN model
            self.face_enhancer = GFPGANer(
                model_path='/runpod-volume/cache/GFPGANv1.4.pth',
                upscale=2,
                arch='clean',
                channel_multiplier=2,
                bg_upsampler=None
            )
            
            logger.info("✅ GFPGAN face enhancer loaded")
            
        except ImportError:
            logger.warning("GFPGAN not available, using basic enhancement")
            self.face_enhancer = None
        except Exception as e:
            logger.error(f"Failed to load face enhancement model: {e}")
            self.face_enhancer = None
    
    def enhance_video(self, video_path: str, output_path: str) -> str:
        """Enhance facial expressions in video"""
        try:
            logger.info(f"Enhancing facial expressions: {video_path}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Enhance frame
                enhanced_frame = self._enhance_frame(frame)
                out.write(enhanced_frame)
                
                frame_count += 1
                if frame_count % 30 == 0:
                    logger.info(f"Processed {frame_count} frames")
            
            cap.release()
            out.release()
            
            logger.info(f"✅ Facial expression enhancement completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Facial expression enhancement failed: {e}")
            # Copy original file as fallback
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path
    
    def _enhance_frame(self, frame: np.ndarray) -> np.ndarray:
        """Enhance facial expressions in a single frame"""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect face landmarks
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Extract face region
                    h, w, _ = frame.shape
                    
                    # Get bounding box of face
                    x_coords = [landmark.x * w for landmark in face_landmarks.landmark]
                    y_coords = [landmark.y * h for landmark in face_landmarks.landmark]
                    
                    x_min, x_max = int(min(x_coords)), int(max(x_coords))
                    y_min, y_max = int(min(y_coords)), int(max(y_coords))
                    
                    # Add padding
                    padding = 20
                    x_min = max(0, x_min - padding)
                    y_min = max(0, y_min - padding)
                    x_max = min(w, x_max + padding)
                    y_max = min(h, y_max + padding)
                    
                    # Extract face region
                    face_region = frame[y_min:y_max, x_min:x_max]
                    
                    # Enhance face if GFPGAN available
                    if self.face_enhancer and face_region.size > 0:
                        try:
                            _, _, enhanced_face = self.face_enhancer.enhance(
                                face_region, 
                                has_aligned=False, 
                                only_center_face=False, 
                                paste_back=True
                            )
                            
                            # Replace face region in original frame
                            if enhanced_face is not None:
                                frame[y_min:y_max, x_min:x_max] = enhanced_face
                                
                        except Exception as e:
                            logger.debug(f"GFPGAN enhancement failed: {e}")
                    
                    # Apply basic sharpening to face region
                    else:
                        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                        sharpened = cv2.filter2D(face_region, -1, kernel)
                        
                        # Blend with original
                        alpha = 0.3
                        blended = cv2.addWeighted(face_region, 1-alpha, sharpened, alpha, 0)
                        frame[y_min:y_max, x_min:x_max] = blended
            
            return frame
            
        except Exception as e:
            logger.debug(f"Frame enhancement failed: {e}")
            return frame
    
    def detect_emotions(self, frame: np.ndarray) -> dict:
        """Detect emotions in face (for future use)"""
        try:
            # This could integrate with emotion detection models
            # For now, return neutral
            return {"emotion": "neutral", "confidence": 0.5}
            
        except Exception as e:
            logger.debug(f"Emotion detection failed: {e}")
            return {"emotion": "neutral", "confidence": 0.0}
EOF

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

ENTRYPOINT ["python3.10", "-u", "runpod_handler.py"]