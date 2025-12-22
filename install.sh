#!/bin/bash
set -e

############################
# System dependencies
############################
echo "=== System dependencies ==="
apt update
apt install -y git wget aria2 ffmpeg python3-venv curl

############################
# ComfyUI core
############################
echo "=== ComfyUI ==="
cd /workspace

if [ ! -d ComfyUI ]; then
  git clone https://github.com/comfyanonymous/ComfyUI.git
fi

cd ComfyUI

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu121

pip install -r requirements.txt

############################
# Bootstrap repo
############################
echo "=== Pull bootstrap data ==="
cd /workspace

if [ ! -d bootstrap ]; then
  git clone https://github.com/chremmler777/comfy-bootstrap.git bootstrap
else
  cd bootstrap
  git pull
fi

MODELS_FILE="/workspace/bootstrap/models.txt"

############################
# Validate model URLs
############################
echo "=== Validating model URLs ==="

if [ -z "${HF_TOKEN:-}" ]; then
  echo "HF_TOKEN not set → validating anonymously"
  CURL_HDR=()
else
  CURL_HDR=(-H "Authorization: Bearer ${HF_TOKEN}")
fi

while read -r folder url; do
  [[ -z "$folder" || "$folder" =~ ^# ]] && continue
  echo "Checking: $url"
  code=$(curl -s -o /dev/null -w "%{http_code}" -L --head "${CURL_HDR[@]}" "$url")
  if [[ "$code" != "200" ]]; then
    echo "ERROR: $url returned HTTP $code"
    exit 1
  fi
done < "$MODELS_FILE"

echo "All model URLs validated successfully."

############################
# Custom nodes
############################
echo "=== Custom nodes ==="
cd /workspace/ComfyUI/custom_nodes

while read -r repo; do
  [[ -z "$repo" || "$repo" =~ ^# ]] && continue
  name=$(basename "$repo" .git)
  [ -d "$name" ] && continue
  git clone "$repo"
done < /workspace/bootstrap/custom_nodes.txt

############################
# Models (WAN-authoritative)
############################
echo "=== Models ==="

mkdir -p /workspace/ComfyUI/models
cd /workspace/ComfyUI/models

ARIA_HDR=()
if [ -n "${HF_TOKEN:-}" ]; then
  ARIA_HDR=(--header="Authorization: Bearer ${HF_TOKEN}")
fi

while read -r folder url; do
  [[ -z "$folder" || "$folder" =~ ^# ]] && continue

  fname="$(basename "$url")"

  echo "Downloading $fname → $folder"
  mkdir -p "$folder"

  aria2c -x16 -s16 "${ARIA_HDR[@]}" \
    --continue=true \
    --allow-overwrite=true \
    --auto-file-renaming=false \
    -d "$folder" \
    -o "$fname" \
    "$url"

done < "$MODELS_FILE"

echo "Model inventory:"
echo "  diffusion_models: $(ls diffusion_models 2>/dev/null | wc -l)"
echo "  loras:            $(ls loras 2>/dev/null | wc -l)"
echo "  text_encoders:    $(ls text_encoders 2>/dev/null | wc -l)"
echo "  vae:              $(ls vae 2>/dev/null | wc -l)"

############################
# Python deps for custom nodes
############################
echo "=== Custom node Python dependencies ==="
pip install diffusers gguf

############################
# Workflows
############################
echo "=== Workflows ==="
cd /workspace/ComfyUI
mkdir -p user/default/workflows
cp /workspace/bootstrap/workflows/*.json user/default/workflows/ || true

############################
# Launch (background-safe)
############################
echo "=== Launch ComfyUI ==="
cd /workspace/ComfyUI

nohup python main.py \
  --listen 0.0.0.0 \
  --port 8188 \
  > /workspace/comfyui.log 2>&1 &

echo "ComfyUI started."
echo "Log file: /workspace/comfyui.log"
