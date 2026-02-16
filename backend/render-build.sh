#!/bin/sh
# render.com build script

# Install CPU-only PyTorch first to avoid downloading the ~2.4GB CUDA version.
# The CPU-only wheels are ~200MB and work fine for inference on Render.
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies (torch requirement is already satisfied)
pip install -r requirements.txt
