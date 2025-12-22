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
# Models (WAN-safe install)
############################
echo "=== Models ==="
cd /workspace/ComfyUI/models

ARIA_HDR=()
if [ -n "${HF_TOKEN:-}" ]; then
  ARIA_HDR=(--header="Authorization: Bearer ${HF_TOKEN}")
fi

TMP_DL="/workspace/model_tmp"
rm -rf "$TMP_DL"
mkdir -p "$TMP_DL"

while read -r folder url; do
  [[ -z "$folder" || "$folder" =~ ^# ]] && continue
  echo "Downloading $url"
  aria2c -x16 -s16 "${ARIA_HDR[@]}" -d "$TMP_DL" "$url"
done < "$MODELS_FILE"

echo "=== Normalizing model layout (authoritative) ==="

mkdir -p diffusion_models loras text_encoders vae

# Diffusion models
find "$TMP_DL" -type f -name "wan2.2_*14B*.safetensors" \
  -exec mv -f {} diffusion_models/ \;

# LoRAs
find "$TMP_DL" -type f -name "*lora*.safetensors" \
  -exec mv -f {} loras/ \;

# Text encoders
find "$TMP_DL" -type f -name "umt5*.safetensors" \
  -exec mv -f {} text_encoders/ \;

# VAEs
find "$TMP_DL" -type f -name "*vae*.safetensors" \
  -exec mv -f {} vae/ \;

rm -rf "$TMP_DL"

echo "Models installed:"
echo "  diffusion_models: $(ls diffusion_models | wc -l)"
echo "  loras:            $(ls loras | wc -l)"
echo "  text_encoders:    $(ls text_encoders | wc -l)"
echo "  vae:              $(ls vae | wc -l)"

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
