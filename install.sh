#!/bin/bash
set -e

# Ignore terminal hangup - script continues if terminal closes
trap '' HUP

############################
# Setup logging to file and terminal
############################
mkdir -p /workspace/logs
LOG_FILE="/workspace/logs/install_$(date +%Y%m%d_%H%M%S).log"
exec &> >(tee -a "$LOG_FILE")
echo "=== Installation Log ==="
echo "Log file: $LOG_FILE"
echo "Start time: $(date)"
echo "Script will continue if terminal closes. Check log: tail -f $LOG_FILE"
echo ""

############################
# SSH setup (dockerArgs bypasses RunPod init, so we start sshd manually)
############################
mkdir -p /root/.ssh /run/sshd
chmod 700 /root/.ssh
SSH_KEY="${PUBLIC_KEY:-ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDouP0kUKnL2oL9QOwYCdXeaN8gBfnvtWFtgRIXV+mq+ christoph.demmler@gmail.com}"
echo "$SSH_KEY" > /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
which sshd || apt-get install -y -q openssh-server
ssh-keygen -A  # generate missing host keys (required before sshd will start)
/usr/sbin/sshd
echo "SSH ready (sshd running)."

############################
# Check for existing installation (Network Volume)
############################
MARKER_FILE="/workspace/.comfy_installed"
SKIP_DOWNLOADS=0

if [ -f "$MARKER_FILE" ]; then
  echo "╔════════════════════════════════════════════════╗"
  echo "║   Existing installation detected!              ║"
  echo "╚════════════════════════════════════════════════╝"
  echo ""
  echo "Models already downloaded (Network Volume)"
  echo "Last installed: $(cat "$MARKER_FILE")"
  echo ""
  echo "Options:"
  echo "  1) Quick start - skip downloads, just launch ComfyUI"
  echo "  2) Full reinstall - download everything fresh"
  echo ""
  read -p "Enter choice [default: 1]: " INSTALL_CHOICE || true
  INSTALL_CHOICE=${INSTALL_CHOICE:-1}

  if [ "$INSTALL_CHOICE" = "1" ]; then
    SKIP_DOWNLOADS=1
    echo "✓ Skipping downloads, using existing models"
  else
    echo "✓ Full reinstall selected"
  fi
  echo ""
fi

############################
# Bootstrap repo (clone first for model selection)
############################
echo "=== Pull bootstrap data ==="
cd /workspace

if [ ! -d bootstrap ]; then
  git clone https://github.com/chremmler777/comfy-bootstrap.git bootstrap
else
  cd bootstrap
  git pull
  cd /workspace
fi

############################
# Model Selection Menu (skip if using existing installation)
############################
if [ $SKIP_DOWNLOADS -eq 0 ]; then
  echo ""
  echo "╔════════════════════════════════════════════════╗"
  echo "║         Model Selection Menu                   ║"
  echo "╚════════════════════════════════════════════════╝"
  echo ""
  echo "Which model packages would you like to download?"
  echo "  1) WAN 14B fp8 SafeTensor + LoRAs (civitai.red)"
  echo ""
  echo "Select options separated by spaces (e.g., '1')"
  echo "Press Enter for all options [default: 1]"
  echo ""
  read -p "Enter your choices: " MODEL_CHOICES || true
  MODEL_CHOICES=${MODEL_CHOICES:-1}
else
  MODEL_CHOICES="1"
fi

# Create temp models file based on selection
MODELS_FILE="/tmp/models_selected.txt"
cp /workspace/bootstrap/models.txt "$MODELS_FILE"

# Track what's being downloaded
DOWNLOAD_LIST=""
INCLUDE_WAN_IV=0

# Parse selections
for choice in $MODEL_CHOICES; do
  case "$choice" in
    1)
      INCLUDE_WAN_IV=1
      DOWNLOAD_LIST="$DOWNLOAD_LIST WAN-14B-fp8"
      ;;
  esac
done

# Filter models based on selections
if [ $INCLUDE_WAN_IV -eq 0 ]; then
  sed -i '/diffusion_models\/wan/d' "$MODELS_FILE"
  sed -i '/loras\/wan/d' "$MODELS_FILE"
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
if [ $SKIP_DOWNLOADS -eq 0 ]; then
echo "=== System dependencies ==="
apt update
apt install -y git wget aria2 ffmpeg curl software-properties-common

# Install Python 3.10 with venv support (ComfyUI requires Python 3.10+)
# Always ensure python3.10-venv is available
echo "Ensuring Python 3.10 with venv support..."
if ! python3.10 -m venv --help &> /dev/null; then
  add-apt-repository -y ppa:deadsnakes/ppa
  apt update
fi
apt install -y python3.10 python3.10-venv python3.10-dev 2>/dev/null || true
fi

############################
# ComfyUI core
############################
echo "=== ComfyUI ==="
cd /workspace

if [ ! -d ComfyUI ]; then
  git clone https://github.com/comfyanonymous/ComfyUI.git
fi

cd ComfyUI

if [ $SKIP_DOWNLOADS -eq 0 ]; then
  # Use Python 3.10 for venv — inherit system packages (torch already in base image)
  python3.10 -m venv --system-site-packages venv
  source venv/bin/activate
  pip install --upgrade pip

  # Upgrade torch — base image has 2.2.0 but comfy_kitchen requires 2.4+
  pip install --force-reinstall --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

  # Remove strict version pins that cause issues
  sed -i 's/==.*//' requirements.txt

  pip install -r requirements.txt

  # Apply fix for extra_config.py YAML parsing
  cp /workspace/bootstrap/extra_config.py /workspace/ComfyUI/utils/extra_config.py
else
  source venv/bin/activate 2>/dev/null || true
fi

############################
# Skip URL validation - aria2c will handle errors
############################
echo "=== Preparing model downloads ==="

############################
# Custom nodes
############################
if [ $SKIP_DOWNLOADS -eq 0 ]; then
echo "=== Custom nodes ==="
cd /workspace/ComfyUI/custom_nodes

while read -r repo; do
  [[ -z "$repo" || "$repo" =~ ^# ]] && continue
  name=$(basename "$repo" .git)
  [ -d "$name" ] && continue
  git clone "$repo"
done < /workspace/bootstrap/custom_nodes.txt
fi

############################
# Models (WAN-authoritative)
############################
echo "=== Models ==="

mkdir -p /workspace/ComfyUI/models
cd /workspace/ComfyUI/models

if [ $SKIP_DOWNLOADS -eq 0 ]; then
  ARIA_HDR=(
    --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    --header="Accept: */*"
  )
  if [ -n "${HF_TOKEN:-}" ]; then
    ARIA_HDR+=(--header="Authorization: Bearer ${HF_TOKEN}")
  fi

  # Create tracking directory for live status
  TRACK_DIR="/tmp/model_downloads"
  rm -rf "$TRACK_DIR"
  mkdir -p "$TRACK_DIR"

  # Count total files
  TOTAL_FILES=$(grep -cv '^[[:space:]]*\(#\|$\)' "$MODELS_FILE")

  # Start all downloads in background
  while read -r folder url filename; do
    [[ -z "$folder" || "$folder" =~ ^# ]] && continue

    # Use custom filename if provided, otherwise extract from URL
    if [ -z "$filename" ]; then
      fname="$(basename "$url")"
    else
      fname="$filename"
    fi

    # Create tracking marker file with model name inside
    TRACK_ID="${folder//\//_}__${fname//\//_}"
    echo "$fname" > "$TRACK_DIR/$TRACK_ID"

    mkdir -p "$folder"

    # Use curl for Civitai downloads to handle redirects with auth headers (run in background)
    if [[ "$url" =~ civitai ]]; then
      (
        curl -s -L -C - \
          --speed-limit 10000 --speed-time 60 \
          --retry 5 --retry-delay 10 \
          -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
          ${CIVITAI_TOKEN:+-H "Authorization: Bearer ${CIVITAI_TOKEN}"} \
          -o "$folder/$fname" \
          "$url" 2>/dev/null
        rm -f "$TRACK_DIR/$TRACK_ID"
      ) &
    else
      # Use aria2c for other sources (faster with parallel connections, run in background)
      (
        DOWNLOAD_HEADERS=("${ARIA_HDR[@]}")
        aria2c -q -x16 -s16 "${DOWNLOAD_HEADERS[@]}" \
          --continue=true \
          --allow-overwrite=true \
          --auto-file-renaming=false \
          -d "$folder" \
          -o "$fname" \
          "$url" >/dev/null 2>&1
        rm -f "$TRACK_DIR/$TRACK_ID"
      ) &
    fi

  done < "$MODELS_FILE"

  # Show live download status with speed
  echo "Downloading $TOTAL_FILES models..."
  echo ""

  # Initialize for speed calculation
  LAST_BYTES=$(du -sb /workspace/ComfyUI/models 2>/dev/null | cut -f1 || echo 0)
  LAST_TIME=$(date +%s)
  SPEED_MBPS="--"

  while true; do
    # Count remaining downloads
    REMAINING=$(find "$TRACK_DIR" -type f 2>/dev/null | wc -l)
    COMPLETED=$((TOTAL_FILES - REMAINING))

    # Get current models being downloaded (suppress errors from race condition)
    CURRENT_MODELS=""
    for f in "$TRACK_DIR"/*; do
      [ -f "$f" ] && CURRENT_MODELS+="$(cat "$f" 2>/dev/null || true) "
    done

    # Calculate download speed (total bytes in models folder)
    CURRENT_BYTES=$(du -sb /workspace/ComfyUI/models 2>/dev/null | cut -f1 || echo 0)
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - LAST_TIME))

    if [ $TIME_DIFF -gt 0 ] && [ "$CURRENT_BYTES" -gt "$LAST_BYTES" ]; then
      BYTES_DIFF=$((CURRENT_BYTES - LAST_BYTES))
      SPEED_BPS=$((BYTES_DIFF / TIME_DIFF))
      SPEED_MBPS=$(awk "BEGIN {printf \"%.1f\", $SPEED_BPS / 1048576}")
      LAST_BYTES=$CURRENT_BYTES
      LAST_TIME=$CURRENT_TIME
    fi

    # Show status
    echo "[$COMPLETED/$TOTAL_FILES] ${SPEED_MBPS} MB/s | ${CURRENT_MODELS:0:60}"

    if [ $REMAINING -eq 0 ]; then
      break
    fi

    sleep 3
  done

  # Kill any remaining aria2c or curl processes
  pkill -f "aria2c|curl" 2>/dev/null || true
  sleep 1

  # Clean up tracking directory
  rm -rf "$TRACK_DIR"

  echo ""
  echo "✓ All models downloaded"
else
  echo "✓ Using existing models from Network Volume"
fi

############################
# SAM model for Impact-Pack
############################
if [ $SKIP_DOWNLOADS -eq 0 ]; then
echo "=== Downloading SAM model for Impact-Pack ==="
mkdir -p /workspace/ComfyUI/models/sams
cd /workspace/ComfyUI/models/sams
if [ ! -f sam_vit_b_01ec64.pth ]; then
  curl -s -L -o sam_vit_b_01ec64.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
  echo "✓ SAM model downloaded"
else
  echo "✓ SAM model already exists"
fi

MODELS_DIR="/workspace/ComfyUI/models"
echo "Model inventory:"
echo "  diffusion_models: $(find $MODELS_DIR/diffusion_models -type f 2>/dev/null | wc -l)"
echo "  loras:            $(find $MODELS_DIR/loras -type f 2>/dev/null | wc -l)"
echo "  text_encoders:    $(find $MODELS_DIR/text_encoders -type f 2>/dev/null | wc -l)"
echo "  vae:              $(find $MODELS_DIR/vae -type f 2>/dev/null | wc -l)"
echo "  sams:             $(find $MODELS_DIR/sams -type f 2>/dev/null | wc -l)"
echo "  ultralytics/bbox: $(find $MODELS_DIR/ultralytics/bbox -type f 2>/dev/null | wc -l)"
echo "  upscale_models:   $(find $MODELS_DIR/upscale_models -type f 2>/dev/null | wc -l)"

############################
# Python deps for custom nodes
############################
echo "=== Custom node Python dependencies ==="
pip install --quiet diffusers gguf accelerate ftfy opencv-python-headless matplotlib scikit-image ultralytics piexif dill segment-anything 2>&1 | grep -E "^(ERROR|Successfully)" || true

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

fi # end SKIP_DOWNLOADS -eq 0

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

############################
# Keeperweb (comfyui2)
############################
echo "=== Keeperweb ==="
pip install --quiet flask anthropic

mkdir -p /workspace/comfyui2/keeper_web/static
mkdir -p /workspace/comfyui2/data

cp /workspace/bootstrap/keeperweb/app.py          /workspace/comfyui2/keeper_web/app.py
cp /workspace/bootstrap/keeperweb/wan_workflow.py  /workspace/comfyui2/keeper_web/wan_workflow.py
cp /workspace/bootstrap/keeperweb/planner.py       /workspace/comfyui2/keeper_web/planner.py
cp /workspace/bootstrap/keeperweb/static/index.html   /workspace/comfyui2/keeper_web/static/index.html
cp /workspace/bootstrap/keeperweb/static/videos.html  /workspace/comfyui2/keeper_web/static/videos.html
cp /workspace/bootstrap/keeperweb/static/animate.html /workspace/comfyui2/keeper_web/static/animate.html 2>/dev/null || true

nohup python /workspace/comfyui2/keeper_web/app.py \
  > /workspace/keeperweb.log 2>&1 &

echo "Keeperweb started on port 8189"
echo "Log: /workspace/keeperweb.log"

############################
# Create installation marker (for Network Volume)
############################
echo "$(date '+%Y-%m-%d %H:%M:%S') - Models: $MODEL_CHOICES" > "$MARKER_FILE"

echo ""
echo "════════════════════════════════════════════════════"
echo "Installation completed!"
echo "════════════════════════════════════════════════════"
echo ""
echo "📋 Installation log saved to:"
echo "   $LOG_FILE"
echo ""
echo "🔍 To troubleshoot later, view the full installation log:"
echo "   cat $LOG_FILE"
echo ""
echo "📊 ComfyUI runtime logs:"
echo "   /workspace/comfyui.log"
echo ""
echo "✅ Ready to use!"
echo ""
echo "🎬 ComfyUI:   port 8188"
echo "📺 Keeperweb: port 8189  (browse + download videos)"
echo "════════════════════════════════════════════════════"

# Keep container alive so RunPod doesn't restart it
sleep infinity
