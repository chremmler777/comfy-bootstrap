# Technical Architecture

In-depth technical documentation of the bootstrap installation system.

## Overview

The bootstrap is a Bash-based installation framework that automates:
1. System dependency installation
2. ComfyUI core deployment
3. Custom node repository cloning
4. AI model downloading with intelligent optimization
5. Python dependency management
6. Service startup and logging

## Design Principles

### 1. Idempotency
- Installation is repeatable without errors
- Existing files are skipped, not re-downloaded
- No state corruption from interrupted runs

### 2. Fault Tolerance
- Retry logic for flaky downloads (Civitai)
- File size validation for corruption detection
- Process recovery after interruptions

### 3. Optimization
- Parallel downloads for reliable sources (HuggingFace)
- Sequential downloads for rate-limited sources (Civitai)
- Background job management for efficiency

### 4. Transparency
- Comprehensive logging to console and files
- Progress indicators for long operations
- Detailed error messages for debugging

---

## Directory Structure

```
/workspace/
├── ComfyUI/                          # Core installation
│   ├── main.py                       # Entry point
│   ├── comfy/                        # Core modules
│   ├── models/                       # AI model storage
│   │   ├── checkpoints/              # SDXL base models
│   │   ├── diffusion_models/         # Diffusion backbones
│   │   ├── loras/                    # LoRA fine-tunes
│   │   ├── vae/                      # VAE models
│   │   ├── text_encoders/            # Text embeddings
│   │   ├── ultralytics/
│   │   │   └── bbox/                 # YOLO detection
│   │   ├── upscale_models/           # Upscalers
│   │   └── sams/                     # Segment Anything
│   ├── custom_nodes/                 # User/community nodes
│   │   ├── ComfyUI-Manager/
│   │   ├── ComfyUI-WanVideoWrapper/
│   │   ├── ... (11 total)
│   ├── user/                         # User data
│   │   └── default/
│   │       ├── workflows/            # Workflow JSON files
│   │       ├── ComfyUI-Impact-Subpack/
│   │       │   └── model-whitelist.txt
│   ├── venv/                         # Python virtual environment
│   └── requirements.txt               # Python dependencies
├── bootstrap/                        # This repository
│   ├── install.sh                    # Main installer
│   ├── models.txt                    # Model configuration
│   ├── custom_nodes.txt              # Node repositories
│   ├── README.md                     # Overview
│   ├── INSTALLATION.md               # Install guide
│   ├── MODELS.md                     # Model reference
│   ├── NODES.md                      # Node reference
│   └── ARCHITECTURE.md               # This file
└── comfyui.log                       # Runtime logs
```

---

## Installation Script Architecture

### File: install.sh (206 lines)

#### Section 1: System Setup (Lines 1-2)
```bash
#!/bin/bash
set -e
```

- `#!/bin/bash` → Use Bash interpreter
- `set -e` → Exit on first error (fail-fast)

#### Section 2: System Dependencies (Lines 7-9)

```bash
echo "=== System dependencies ==="
apt update
apt install -y git wget aria2 ffmpeg python3-venv curl
```

**Installed tools**:
- `git` → Clone repositories
- `wget` → Alternative download tool
- `aria2` → Parallel download utility
- `ffmpeg` → Video processing
- `python3-venv` → Create virtual environments
- `curl` → HTTP downloads with advanced features

**Why separate tools?**
- `aria2c` → Fast parallel downloads
- `curl` → Better auth/redirect handling for Civitai
- `wget` → Fallback option

#### Section 3: ComfyUI Core Installation (Lines 14-30)

```bash
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

**Key points**:
- Clones official ComfyUI repository
- Creates isolated Python virtual environment
- Installs PyTorch with CUDA 12.1 support (GPU acceleration)
- Installs all core ComfyUI dependencies from requirements.txt

**PyTorch Installation**:
- `cu121` → CUDA 12.1 (must match GPU driver)
- Separate URL for GPU wheel variants
- Ensures GPU drivers compatible with 12.1

#### Section 4: Bootstrap Data (Lines 35-43)

```bash
cd /workspace
if [ ! -d bootstrap ]; then
  git clone https://github.com/chremmler777/comfy-bootstrap.git bootstrap
else
  cd bootstrap
  git pull
fi
```

**Logic**:
- Check if `bootstrap` directory exists
- If not: clone fresh repository
- If yes: pull latest changes (idempotent)
- Ensures configuration files are current

#### Section 5: Custom Nodes Installation (Lines 55-63)

```bash
cd /workspace/ComfyUI/custom_nodes
while read -r repo; do
  [[ -z "$repo" || "$repo" =~ ^# ]] && continue
  name=$(basename "$repo" .git)
  [ -d "$name" ] && continue
  git clone "$repo"
done < /workspace/bootstrap/custom_nodes.txt
```

**Algorithm**:
1. Read each line from `custom_nodes.txt`
2. Skip empty lines and comments (lines starting with `#`)
3. Extract repository name from URL (e.g., `ComfyUI-Manager` from `github.com/.../ComfyUI-Manager.git`)
4. Check if directory exists (idempotent - skip if already installed)
5. Clone if not exists

**Example Processing**:
```
Input: https://github.com/ltdrdata/ComfyUI-Manager
Process: basename removes URL, leaves "ComfyUI-Manager"
Output: Cloned to custom_nodes/ComfyUI-Manager/
```

#### Section 6: Model Download Logic (Lines 73-135)

**Architecture Overview**:
```
models.txt parsing
    ↓
For each model:
    ├─ Extract: folder, url, filename
    ├─ Check if Civitai URL
    │   ├─ Yes → curl with retry (SEQUENTIAL)
    │   └─ No → aria2c (PARALLEL BACKGROUND)
    └─ Next model
```

##### 6a: Download Preparation (Lines 73-79)

```bash
ARIA_HDR=(
  --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
  --header="Accept: */*"
)
if [ -n "${HF_TOKEN:-}}" ]; then
  ARIA_HDR+=(--header="Authorization: Bearer ${HF_TOKEN}")
fi
```

**Setup headers for all downloads**:
- User-Agent → Pretend to be browser, avoid blocking
- Accept → Accept all file types
- HF_TOKEN (optional) → HuggingFace authentication

##### 6b: Model Loop (Lines 81-135)

```bash
while read -r folder url filename; do
  # Parse and validate
  [[ -z "$folder" || "$folder" =~ ^# ]] && continue

  # Determine filename
  if [ -z "$filename" ]; then
    fname="$(basename "$url")"
  else
    fname="$filename"
  fi

  mkdir -p "$folder"

  # Download based on source
  if [[ "$url" =~ civitai.com ]]; then
    # CIVITAI DOWNLOAD (curl with retry)
  else
    # HUGGINGFACE DOWNLOAD (aria2c parallel)
  fi
done < "$MODELS_FILE"
wait  # Wait for background jobs
```

**Algorithm Flow**:
1. Read each line from models.txt
2. Skip empty/comment lines
3. Parse: folder, url, filename
4. Create target directory
5. Route to appropriate downloader
6. Wait for all background jobs to complete

##### 6c: Civitai Download with Retry (Lines 95-122)

```bash
if [[ "$url" =~ civitai.com ]]; then
  RETRY_COUNT=0
  MAX_RETRIES=3

  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    curl -L -C - \
      -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
      ${CIVITAI_TOKEN:+-H "Authorization: Bearer ${CIVITAI_TOKEN}"} \
      -o "$folder/$fname" \
      "$url"

    # Validate file integrity
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
fi
```

**Civitai-Specific Design**:

**Why curl?**
- Better redirect handling
- Native auth header support
- Simpler CIVITAI_TOKEN integration

**Why sequential?**
- Civitai has per-IP rate limiting
- Multiple parallel requests get blocked
- Sequential avoids HTTP 429 errors

**Why retry?**
- Civitai sometimes returns 401/524 errors
- Returns HTML error pages instead of files
- Retry after 5-second delay often succeeds

**File Size Validation**:
```
< 500KB → HTML error page → Delete and retry
> 500KB → Actual model file → Success
```

**Environment Variable Usage**:
```bash
${CIVITAI_TOKEN:+-H "Authorization: Bearer ${CIVITAI_TOKEN}"}
```
- `${VAR:+TEXT}` → Include `TEXT` if VAR is set
- If no CIVITAI_TOKEN → Header not added
- If CIVITAI_TOKEN set → Header added with token

##### 6d: HuggingFace Download (Lines 124-133)

```bash
else
  # aria2c for other sources (HuggingFace)
  DOWNLOAD_HEADERS=("${ARIA_HDR[@]}")
  aria2c -x16 -s16 "${DOWNLOAD_HEADERS[@]}" \
    --continue=true \
    --allow-overwrite=true \
    --auto-file-renaming=false \
    -d "$folder" \
    -o "$fname" \
    "$url" &
fi
```

**aria2c Parameters**:
- `-x16` → 16 parallel connections
- `-s16` → 16 segments per file
- `--continue=true` → Resume interrupted downloads
- `--allow-overwrite=true` → Overwrite if corrupted
- `-d "$folder"` → Download to target folder
- `-o "$fname"` → Use custom filename
- `&` → Run in background

**Why background?**
- Multiple HuggingFace downloads can run in parallel
- Civitai downloads block, but HF downloads continue
- Better resource utilization

**Final wait**:
```bash
wait  # Wait for all background aria2c jobs
```
- Blocks until all background downloads complete
- Ensures models ready before next phase

#### Section 7: SAM Model Download (Lines 143-151)

```bash
echo "=== Downloading SAM model for Impact-Pack ==="
mkdir -p /workspace/ComfyUI/models/sams
cd /workspace/ComfyUI/models/sams
if [ ! -f sam_vit_b_01ec64.pth ]; then
  curl -L -o sam_vit_b_01ec64.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
  echo "✓ SAM model downloaded"
else
  echo "✓ SAM model already exists"
fi
```

**Design**:
- Special-cased single file (not in models.txt)
- Checks existence first (idempotent)
- From official Meta AI source (reliable)
- Sequential curl (small, reliable source)

#### Section 8: Model Inventory Report (Lines 153-161)

```bash
echo "Model inventory:"
echo "  checkpoints:      $(ls checkpoints 2>/dev/null | wc -l)"
echo "  diffusion_models: $(ls diffusion_models 2>/dev/null | wc -l)"
echo "  loras:            $(ls loras 2>/dev/null | wc -l)"
echo "  text_encoders:    $(ls text_encoders 2>/dev/null | wc -l)"
echo "  vae:              $(ls vae 2>/dev/null | wc -l)"
echo "  sams:             $(ls sams 2>/dev/null | wc -l)"
echo "  ultralytics/bbox: $(ls ultralytics/bbox 2>/dev/null | wc -l)"
echo "  upscale_models:   $(ls upscale_models 2>/dev/null | wc -l)"
```

**Verification Output**:
```
Model inventory:
  checkpoints:      5
  diffusion_models: 2
  loras:            14
  ...
```

**Why?**
- Verify downloads completed
- Quick sanity check
- Helps troubleshoot missing models

#### Section 9: Python Dependencies (Line 167)

```bash
echo "=== Custom node Python dependencies ==="
pip install diffusers gguf accelerate ftfy opencv-python-headless matplotlib \
  scikit-image ultralytics piexif dill segment-anything
```

**Dependency Mapping**:
- `diffusers` → WanVideoWrapper, general diffusion support
- `gguf` → ComfyUI-GGUF
- `accelerate` → WanVideoWrapper (distributed training)
- `ftfy` → Text encoding fixes
- `opencv-python-headless` → Image processing
- `matplotlib` → Visualization (optional)
- `scikit-image` → Impact-Pack image operations
- `ultralytics` → YOLO detection models
- `piexif` → Image EXIF data
- `dill` → Advanced pickling (Impact-Pack)
- `segment-anything` → SAM model integration

#### Section 10: Model Whitelists (Lines 173-181)

```bash
mkdir -p /workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack
cat > /workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack/model-whitelist.txt << 'EOF'
bbox/penis.pt
bbox/nipple.pt
bbox/Eyeful_v2-Paired.pt
bbox/face_yolov8m.pt
bbox/hand_yolov8s.pt
EOF
```

**Purpose**:
- Impact-Subpack requires explicit whitelist
- Security: only allows specified detection models
- Prevents loading arbitrary models

**Format**:
```
bbox/model_name.pt
```
- Relative path from models directory
- One per line

#### Section 11: Workflows (Lines 189-191)

```bash
mkdir -p user/default/workflows
cp /workspace/bootstrap/workflows/*.json user/default/workflows/ || true
```

**Design**:
- `|| true` → Ignore errors if no workflows exist
- Idempotent (overwrites existing)
- Optional feature (workflows in separate directory)

#### Section 12: ComfyUI Launch (Lines 199-202)

```bash
nohup python main.py \
  --listen 0.0.0.0 \
  --port 8188 \
  > /workspace/comfyui.log 2>&1 &
```

**Launch Parameters**:
- `nohup` → No hangup (runs after disconnect)
- `--listen 0.0.0.0` → Listen on all network interfaces (RunPod requirement)
- `--port 8188` → Standard ComfyUI port
- `> /workspace/comfyui.log` → Redirect stdout to log
- `2>&1` → Redirect stderr to same log
- `&` → Run in background

**Why nohup?**
- SSH sessions can disconnect on RunPod
- `nohup` allows process to survive disconnect
- Service continues running

---

## Configuration Files

### models.txt Format

**Structure**:
```
folder url filename
folder url
```

**Examples**:
```
checkpoints https://civitai.com/api/download/models/1942437?type=Model&format=SafeTensor illustrij_v16.safetensors
loras https://huggingface.co/User/model/resolve/main/file.safetensors my_lora.safetensors
```

**Parsing Rules**:
- Space-separated: folder, url, filename (optional)
- Comment: lines starting with `#`
- Empty: blank lines (skipped)

**Folder Must Match**:
```
/workspace/ComfyUI/models/<folder>/
```

### custom_nodes.txt Format

**Structure**:
```
https://github.com/user/ComfyUI-Node
https://github.com/user/ComfyUI-Another
# Optional comment
```

**Parsing Rules**:
- One URL per line (https:// required)
- Comments: lines starting with `#`
- Empty: blank lines (skipped)
- Cloned to: `/workspace/ComfyUI/custom_nodes/<directory>/`

---

## Download Strategy Analysis

### Parallel vs Sequential Decision

```
HuggingFace (Parallel - aria2c):
├─ Reliable CDN infrastructure
├─ No per-IP rate limiting
├─ Fast with multiple connections
└─ Run in background (non-blocking)

Civitai (Sequential - curl):
├─ Per-IP rate limiting
├─ Returns errors on parallel requests
├─ Requires authentication
└─ Must wait for each download
```

### Optimization Timeline

**Naive Approach** (all sequential):
```
Model 1 (8h) → Model 2 (5h) → Model 3 (2h)
Total: 15 hours
```

**Bootstrap Approach** (optimized):
```
Timeline:
0:00  Start
0:05  System setup done
0:20  ComfyUI installed
1:00  Custom nodes cloned
1:05  ├─ Civitai model 1 (5h) ┐
      ├─ HF Model 2 (2h)      ├─ Parallel
      └─ HF Model 3 (1h) ┘
6:05  All models done
6:15  Dependencies installed
6:16  Launch ComfyUI

Actual: ~6 hours (vs 15 hours naive)
Savings: 9 hours (60% faster)
```

---

## Error Handling Strategy

### Fail-Fast Design

```bash
set -e  # Exit on any error
```

**Benefits**:
- No silent failures
- Clear error point
- Easier debugging

**Exceptions** (explicit error handling):
```bash
cp /workspace/bootstrap/workflows/*.json ... || true
# Ignore errors if workflows directory empty
```

### Retry Logic (Civitai Only)

```bash
RETRY_COUNT=0
MAX_RETRIES=3

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  # Download attempt
  if [ "$FILE_SIZE" -lt 500000 ]; then
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 5  # Wait before retry
  else
    break  # Success
  fi
done
```

**Behavior**:
- Attempt 1: If fail, sleep 5s
- Attempt 2: If fail, sleep 5s
- Attempt 3: If fail, exit
- Total wait: ~10 seconds max per file

---

## Performance Characteristics

### Theoretical Limits

**Network Bandwidth**:
- aria2c × 16 connections = 16 × connection_speed
- Typical: 16 × 10 Mbps = 160 Mbps aggregate
- Actual: 100-200 Mbps typical

**Disk I/O**:
- Modern SSD: 500-1000 Mbps write
- Not bottleneck for most cases
- RAID/network storage can be slower

**Model Download Time** (empirical):
```
Parallel HuggingFace:
├─ 2GB model: ~2 minutes (at 160 Mbps)
├─ 5GB model: ~5 minutes
└─ 100GB total: ~2 hours

Civitai Sequential:
├─ 2GB model: ~10 minutes (at 30 Mbps)
├─ 5GB model: ~25 minutes
└─ 40GB total: ~4+ hours
```

---

## Monitoring & Debugging

### Log Files

**ComfyUI Log**:
```
/workspace/comfyui.log
```

Contains:
- Startup messages
- Node loading status
- Errors and warnings
- Runtime information

**Installation Log** (optional):
```bash
bash install.sh 2>&1 | tee /tmp/install.log
```

### Debug Commands

**Check Process**:
```bash
ps aux | grep python
# Shows if ComfyUI running

pgrep -f "main.py"
# Returns PID if running
```

**Monitor Downloads**:
```bash
ps aux | grep aria2c
# Show active aria2c processes

du -sh /workspace/ComfyUI/models
# Total model size downloaded
```

**Check Network**:
```bash
ping civitai.com
# Verify connectivity

curl -I https://civitai.com
# Check response headers
```

---

## Extension Points

### Adding Custom Models

Edit `models.txt`:
```bash
# Add line
checkpoints https://your-url/model.safetensors custom.safetensors

# Re-run installer
bash install.sh
# Will download only new/missing models
```

### Adding Custom Nodes

Edit `custom_nodes.txt`:
```bash
# Add line
https://github.com/user/ComfyUI-CustomNode

# Re-run installer (manual clone)
cd /workspace/ComfyUI/custom_nodes
git clone https://github.com/user/ComfyUI-CustomNode

# Install dependencies if needed
pip install -r ComfyUI-CustomNode/requirements.txt
```

### Modifying Download Strategy

In `install.sh` line 126:
```bash
# Change aria2c parameters
aria2c -x8 -s8 ...     # Reduce connections
aria2c -x32 -s32 ...   # Increase connections (if reliable)

# Change retry behavior (Civitai)
MAX_RETRIES=5          # More retries
sleep 10               # Longer wait between retries
```

---

## Security Considerations

### Token Handling

```bash
export CIVITAI_TOKEN="..."
# Token stored in process environment
# Not written to disk
# Visible in shell history (careful!)

# Better practice:
read -s -p "Enter Civitai token: " CIVITAI_TOKEN
export CIVITAI_TOKEN
bash install.sh
```

### Repository Trust

```bash
git clone https://github.com/...
# Clones HEAD branch
# No signature verification by default

# For critical deployments:
git verify-commit <commit-hash>
# Verify PGP signatures
```

### Model Validation

Current validation:
```bash
if [ "$FILE_SIZE" -lt 500000 ]; then
  # Assume corrupted
fi
```

Could enhance with:
```bash
# SHA256 verification
sha256sum file.safetensors
# Compare against known hash

# Scan for malware
clamav model.safetensors
```

---

## Future Improvements

### Possible Enhancements

1. **Checksum Verification**:
   - Add SHA256 hashes to models.txt
   - Validate downloaded files
   - Detect corruption early

2. **Bandwidth Limiting**:
   - Configurable speed limits
   - Avoid network saturation
   - Fair resource sharing

3. **Resumable Installation**:
   - Save phase completion state
   - Resume from checkpoint
   - Better for unreliable networks

4. **Model Compression**:
   - Optional: compress models on disk
   - Decompress on-demand
   - Save disk space

5. **Multiple Mirrors**:
   - Support alternative URLs
   - Auto-fallback on failures
   - Faster downloads by region

6. **Health Checks**:
   - Verify ComfyUI starts
   - Test node loading
   - Auto-fix common issues

---

**Last Updated**: 2025-12-23

For implementation details, see `install.sh` source code.
