#!/usr/bin/env python3
"""
Robust package installer for Cinema AI Pipeline
Handles problematic dependencies gracefully
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_package(package, description=""):
    """Install a package with error handling"""
    try:
        logger.info(f"Installing {package} {description}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--no-cache-dir", package
        ], capture_output=True, text=True, check=True)
        logger.info(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"❌ Failed to install {package}: {e.stderr}")
        return False

def install_with_alternatives(packages, description=""):
    """Try to install packages, trying alternatives if main fails"""
    for package in packages:
        if install_package(package, description):
            return True
    logger.error(f"❌ All alternatives failed for {description}")
    return False

def main():
    """Main installation process"""
    logger.info("🚀 Starting robust package installation")
    
    # Core packages (must succeed)
    core_packages = [
        "transformers==4.44.0",
        "diffusers==0.30.0", 
        "accelerate==0.33.0",
        "safetensors==0.4.4",
        "sentencepiece==0.2.0",
        "protobuf==4.25.3",
        "einops==0.8.0",
        "einops-exts==0.0.4",
        "soundfile==0.12.1",
        "librosa==0.10.2",
        "opencv-python==4.10.0.84",
        "imageio==2.34.0",
        "imageio-ffmpeg==0.4.9",
        "pydub==0.25.1",
        "audioread==3.0.1",
        "huggingface-hub==0.24.0",
        "hf-transfer==0.1.6",
        "fastapi==0.111.0",
        "uvicorn==0.30.0",
        "runpod==1.6.0",
        "pydantic==2.8.0",
        "httpx==0.27.0",
        "openai==1.40.0",
        "tiktoken==0.7.0",
        "psutil==6.0.0",
        "tqdm==4.66.4",
        "python-dotenv==1.0.1",
        "rich==13.7.1"
    ]
    
    logger.info("📦 Installing core packages...")
    failed_core = []
    for package in core_packages:
        if not install_package(package, "(core)"):
            failed_core.append(package)
    
    if failed_core:
        logger.error(f"❌ Core packages failed: {failed_core}")
        return False
    
    # Additional packages (can fail)
    additional_packages = [
        ("moviepy==1.0.3", "video processing"),
        ("ffmpeg-python==0.2.0", "ffmpeg wrapper"),
        ("datasets==2.20.0", "HF datasets"),
        ("anthropic==0.31.0", "Anthropic API"),
        ("langchain==0.2.0", "LangChain"),
        ("GPUtil==1.4.0", "GPU monitoring"),
        ("typer==0.12.3", "CLI framework"),
        ("timm==1.0.7", "vision models"),
        ("omegaconf==2.3.0", "config management"),
        ("pytorch-lightning==2.3.0", "PyTorch Lightning"),
        ("rotary-embedding-torch==0.5.3", "rotary embeddings"),
        ("num2words==0.5.13", "number to words"),
        ("inflect==7.2.0", "word inflection")
    ]
    
    logger.info("📦 Installing additional packages...")
    for package, desc in additional_packages:
        install_package(package, f"({desc})")
    
    # Problematic packages with alternatives
    problematic_packages = [
        (["decord==0.6.0"], "video decoding"),
        (["av==12.3.0"], "PyAV video processing"),
        (["scikit-video==1.1.11"], "video processing"),
        (["vidgear==0.3.3"], "video gear"),
        (["pyaudio==0.2.14"], "audio I/O"),
        (["audiocraft==1.3.0"], "Meta AudioCraft"),
        (["TTS==0.22.0"], "text-to-speech"),
        (["gruut==2.4.0"], "phoneme processing"),
        (["phonemizer==3.2.1"], "phonemization"),
        (["bitsandbytes==0.43.0"], "quantization"),
        (["optimum==1.20.0"], "model optimization"),
        (["onnxruntime-gpu==1.18.0"], "ONNX runtime")
    ]
    
    logger.info("📦 Installing problematic packages with fallbacks...")
    for packages, desc in problematic_packages:
        install_with_alternatives(packages, desc)
    
    # Development tools (optional)
    dev_packages = [
        "pytest==8.3.0",
        "pytest-asyncio==0.23.0", 
        "black==24.4.0",
        "isort==5.13.0",
        "flake8==7.1.0"
    ]
    
    logger.info("📦 Installing development tools...")
    for package in dev_packages:
        install_package(package, "(dev)")
    
    logger.info("✅ Package installation completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)