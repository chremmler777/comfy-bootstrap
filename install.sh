#!/bin/bash
set -e

############################
# Model Selection Menu (at startup - before any downloads)
############################
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║         Model Selection Menu                   ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "Which model packages would you like to download?"
echo "  1) WAN 2.2 Text-to-Video (remix models + T2V LoRAs)"
echo "  2) WAN 2.2 Image-to-Video (TV models + IV LoRAs)"
echo "  3) SDXL Workflow (illustrij, lustify, nova, xxxray)"
echo ""
echo "Select multiple options separated by spaces (e.g., '1 3' for WAN T2V + SDXL)"
echo "Press Enter for all options [default: 1 2 3]"
echo ""
read -p "Enter your choices: " MODEL_CHOICES
MODEL_CHOICES=${MODEL_CHOICES:-1 2 3}

# Create temp models file based on selection
MODELS_FILE="/tmp/models_selected.txt"
cp /workspace/bootstrap/models.txt "$MODELS_FILE"

# Track what's being downloaded
DOWNLOAD_LIST=""
INCLUDE_WAN_REMIX=0
INCLUDE_WAN_TV=0
INCLUDE_SDXL=0

# Parse selections
for choice in $MODEL_CHOICES; do
  case "$choice" in
    1)
      INCLUDE_WAN_REMIX=1
      DOWNLOAD_LIST="$DOWNLOAD_LIST WAN-T2V"
      ;;
    2)
      INCLUDE_WAN_TV=1
      DOWNLOAD_LIST="$DOWNLOAD_LIST WAN-IV"
      ;;
    3)
      INCLUDE_SDXL=1
      DOWNLOAD_LIST="$DOWNLOAD_LIST SDXL"
      ;;
  esac
done

# Filter models based on selections
if [ $INCLUDE_WAN_REMIX -eq 0 ]; then
  # Remove remix models and T2V LoRAs
  sed -i '/remix/d' "$MODELS_FILE"
  sed -i '/loras\/wantv/d' "$MODELS_FILE"
fi

if [ $INCLUDE_WAN_TV -eq 0 ]; then
  # Remove TV models and IV LoRAs
  sed -i '/WAN22_TV/d' "$MODELS_FILE"
  sed -i '/loras\/waniv/d' "$MODELS_FILE"
fi

# Remove WAN general LoRAs only if NO WAN options selected
if [ $INCLUDE_WAN_REMIX -eq 0 ] && [ $INCLUDE_WAN_TV -eq 0 ]; then
  sed -i '/loras\/wan\//d' "$MODELS_FILE"
fi

if [ $INCLUDE_SDXL -eq 0 ]; then
  # Remove SDXL checkpoint models and LoRAs
  sed -i '/illustrij_v19\|lustifySDXLNSFW_endgame\|novaAsianXL\|divingIllustriousReal_v50VAE/d' "$MODELS_FILE"
  sed -i '/loras\/sd\//d' "$MODELS_FILE"
fi

# Show selections
if [ -z "$DOWNLOAD_LIST" ]; then
  echo "⚠️  No models selected. Defaulting to all options."
  MODELS_FILE="/workspace/bootstrap/models.txt"
else
  echo "✓ Downloading:$DOWNLOAD_LIST"
fi
echo ""

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

# Apply fix for extra_config.py YAML parsing
cp /workspace/bootstrap/extra_config.py /workspace/ComfyUI/utils/extra_config.py

############################
# Skip URL validation - aria2c will handle errors
############################
echo "=== Preparing model downloads ==="

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

ARIA_HDR=(
  --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
  --header="Accept: */*"
)
if [ -n "${HF_TOKEN:-}" ]; then
  ARIA_HDR+=(--header="Authorization: Bearer ${HF_TOKEN}")
fi

while read -r folder url filename; do
  [[ -z "$folder" || "$folder" =~ ^# ]] && continue

  # Use custom filename if provided, otherwise extract from URL
  if [ -z "$filename" ]; then
    fname="$(basename "$url")"
  else
    fname="$filename"
  fi

  echo "Downloading $fname → $folder"
  mkdir -p "$folder"

  # Use curl for Civitai downloads to handle redirects with auth headers (sequential - avoids rate limiting)
  if [[ "$url" =~ civitai.com ]]; then
    echo "Downloading $fname → $folder (using curl with Civitai auth - parallel)"

    # Retry logic for Civitai downloads (run in background for parallel processing)
    (
      RETRY_COUNT=0
      MAX_RETRIES=3

      while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        curl -s -L -C - \
          -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
          ${CIVITAI_TOKEN:+-H "Authorization: Bearer ${CIVITAI_TOKEN}"} \
          -o "$folder/$fname" \
          "$url"

        # Check if file is corrupted (< 500KB is likely HTML error page)
        if [ -f "$folder/$fname" ]; then
          FILE_SIZE=$(stat -f%z "$folder/$fname" 2>/dev/null || stat -c%s "$folder/$fname" 2>/dev/null)
          if [ "$FILE_SIZE" -lt 500000 ]; then
            echo "⚠️  Downloaded file too small ($FILE_SIZE bytes) - likely corrupted. Retrying..."
            rm "$folder/$fname"
            RETRY_COUNT=$((RETRY_COUNT + 1))
            sleep 5
          else
            echo "✓ Download successful ($FILE_SIZE bytes)"
            break
          fi
        fi
      done
    ) &
  else
    # Use aria2c for other sources (faster with parallel connections, run in background)
    DOWNLOAD_HEADERS=("${ARIA_HDR[@]}")
    aria2c -x16 -s16 "${DOWNLOAD_HEADERS[@]}" \
      --continue=true \
      --allow-overwrite=true \
      --auto-file-renaming=false \
      --quiet=true \
      -d "$folder" \
      -o "$fname" \
      "$url" &
  fi

done < "$MODELS_FILE"

# Wait for all background downloads to complete
wait

############################
# SAM model for Impact-Pack
############################
echo "=== Downloading SAM model for Impact-Pack ==="
mkdir -p /workspace/ComfyUI/models/sams
cd /workspace/ComfyUI/models/sams
if [ ! -f sam_vit_b_01ec64.pth ]; then
  curl -s -L -o sam_vit_b_01ec64.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
  echo "✓ SAM model downloaded"
else
  echo "✓ SAM model already exists"
fi

echo "Model inventory:"
echo "  checkpoints:      $(ls checkpoints 2>/dev/null | wc -l)"
echo "  diffusion_models: $(ls diffusion_models 2>/dev/null | wc -l)"
echo "  loras:            $(ls loras 2>/dev/null | wc -l)"
echo "  text_encoders:    $(ls text_encoders 2>/dev/null | wc -l)"
echo "  vae:              $(ls vae 2>/dev/null | wc -l)"
echo "  sams:             $(ls sams 2>/dev/null | wc -l)"
echo "  ultralytics/bbox: $(ls ultralytics/bbox 2>/dev/null | wc -l)"
echo "  upscale_models:   $(ls upscale_models 2>/dev/null | wc -l)"

############################
# Python deps for custom nodes
############################
echo "=== Custom node Python dependencies ==="
pip install diffusers gguf accelerate ftfy opencv-python-headless matplotlib scikit-image ultralytics piexif dill segment-anything

############################
# Model Whitelists
############################
echo "=== Creating model whitelists ==="
mkdir -p /workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack

cat > /workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack/model-whitelist.txt << 'EOF'
bbox/penis.pt
bbox/nipple.pt
bbox/Eyeful_v2-Paired.pt
bbox/face_yolov8m.pt
bbox/hand_yolov8s.pt
EOF

echo "Whitelist created at: /workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack/model-whitelist.txt"

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
