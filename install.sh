#!/bin/bash
set -e

ODELS_FILE="/workspace/bootstrap/models.txt"

if [ -z "${HF_TOKEN:-}" ]; then
  echo "HF_TOKEN not set → validating anonymously"
  HDR=()
else
  HDR=(-H "Authorization: Bearer ${HF_TOKEN}")
fi

echo "=== Validating model URLs ==="

while read -r folder url; do
  [[ -z "$folder" || "$folder" =~ ^# ]] && continue

  echo "Checking: $url"

  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -L --head "${HDR[@]}" "$url")

  if [[ "$code" != "200" ]]; then
    echo "ERROR: $url returned HTTP $code"
    exit 1
  fi
done < "$MODELS_FILE"

echo "All model URLs validated successfully."

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
while read -r repo; do
  name=$(basename "$repo" .git)
  [ -d "$name" ] && continue
  git clone "$repo"
done < /workspace/bootstrap/custom_nodes.txt

echo "=== Models ==="
cd /workspace/ComfyUI/models

HDR=()
if [ -n "${HF_TOKEN:-}" ]; then
  HDR=(--header="Authorization: Bearer ${HF_TOKEN}")
fi

while read -r folder url; do
  [[ -z "$folder" || "$folder" =~ ^# ]] && continue
  mkdir -p "$folder"
  aria2c -x16 -s16 "${HDR[@]}" -d "$folder" "$url"
done < /workspace/bootstrap/models.txt

echo "=== Workflows ==="
cd /workspace/ComfyUI
mkdir -p user/default/workflows
cp /workspace/bootstrap/workflows/*.json user/default/workflows/

echo "=== Launch ComfyUI ==="
python main.py --listen 0.0.0.0 --port 8188
