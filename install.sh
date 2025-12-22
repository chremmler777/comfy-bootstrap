#!/bin/bash
set -e

echo "=== System dependencies ==="
apt update
apt install -y git wget aria2 ffmpeg python3-venv

echo "=== ComfyUI ==="
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu121

pip install -r requirements.txt

echo "=== Pull bootstrap data ==="
cd /workspace
git clone https://github.com/chremmler777/comfy-bootstrap.git bootstrap

echo "=== Custom nodes ==="
cd /workspace/ComfyUI/custom_nodes
while read repo; do
  git clone "$repo"
done < /workspace/bootstrap/custom_nodes.txt

echo "=== Models ==="
cd /workspace/ComfyUI/models
while read folder url; do
  mkdir -p "$folder"
  aria2c -x16 -s16 -d "$folder" "$url"
done < /workspace/bootstrap/models.txt

echo "=== Workflows ==="
cd /workspace/ComfyUI
mkdir -p user/default/workflows
cp /workspace/bootstrap/workflows/*.json user/default/workflows/

echo "=== Launch ComfyUI ==="
python main.py --listen 0.0.0.0 --port 8188
