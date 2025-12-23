# Installation Guide

Complete step-by-step guide for deploying ComfyUI with bootstrap on RunPod.

## Pre-Installation

### Requirements

- **RunPod Instance**: L40S GPU (45GB VRAM) or better
- **Storage**: 500GB+ SSD (256GB minimum)
- **Internet**: Fast connection (2+ Mbps for 2-4 hour download)
- **Civitai Account** (optional but recommended for model access)

### Civitai Setup (Optional but Recommended)

1. Create Civitai account: https://civitai.com/user/account
2. Generate API token: https://civitai.com/user/account
3. Copy token (you'll need it during installation)

**Note**: Without token, some Civitai models will fail to download.

---

## Installation Steps

### Step 1: Start RunPod Instance

1. Go to RunPod console
2. Select a template (e.g., PyTorch)
3. Choose L40S GPU (or better)
4. Select storage (500GB recommended)
5. Start instance and wait for SSH access

### Step 2: Connect to Pod

```bash
# Copy SSH command from RunPod dashboard
ssh root@your-runpod-url.com -p 12345
```

### Step 3: Clone Bootstrap Repository

```bash
cd /workspace
git clone https://github.com/chremmler777/comfy-bootstrap.git bootstrap
```

### Step 4: (Optional) Set Civitai Token

If you have a Civitai token:

```bash
export CIVITAI_TOKEN="your_token_here"
```

**Note**: Token can be shared during installation. Store securely after.

### Step 5: Run Installation Script

```bash
bash /workspace/bootstrap/install.sh
```

**Expected Runtime**: 2-5 hours depending on connection speed

**Output**: Watch for:
```
=== System dependencies ===
=== ComfyUI ===
=== Pull bootstrap data ===
=== Custom nodes ===
=== Models ===
=== Model inventory ===
=== Custom node Python dependencies ===
=== Launch ComfyUI ===
```

### Step 6: Wait for Completion

Monitor installation:

```bash
# In separate terminal
tail -f /workspace/comfyui.log
```

Expected completion message:
```
ComfyUI started.
Log file: /workspace/comfyui.log
```

### Step 7: Access ComfyUI

1. Get your RunPod URL (e.g., `https://xxxxx-8188.proxy.runpod.io`)
2. Open in browser
3. Should show ComfyUI interface
4. Check "Extra options" menu → "Refresh UI" if nodes not showing

---

## Installation Phases

### Phase 1: System Setup (5-10 minutes)

```
apt update
apt install -y git wget aria2 ffmpeg python3-venv curl
```

Installs system dependencies for downloading and video processing.

### Phase 2: ComfyUI Core (10-15 minutes)

```
git clone https://github.com/comfyanonymous/ComfyUI.git
python3 -m venv venv
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

Installs PyTorch with CUDA 12.1 and ComfyUI core.

**Expected Output**:
```
Successfully installed torch-...
Successfully installed torchvision-...
Successfully installed torchaudio-...
Successfully installed -r requirements.txt
```

### Phase 3: Bootstrap Data (2-5 minutes)

```
git clone https://github.com/chremmler777/comfy-bootstrap.git bootstrap
```

Clones model list and node configuration.

### Phase 4: Custom Nodes (5-10 minutes)

Clones 11 custom node repositories from GitHub:
```
ComfyUI-Manager
ComfyUI-WanVideoWrapper
ComfyUI-GGUF
ComfyUI-Impact-Pack
rgthree-comfy
ComfyUI-Custom-Scripts
ComfyUI-KJNodes
ComfyUI_UltimateSDUpscale
ComfyUI_essentials
ComfyUI-Detail-Daemon
ComfyUI-Impact-Subpack
```

**Expected Output**:
```
Cloning into 'ComfyUI-Manager'...
Cloning into 'ComfyUI-WanVideoWrapper'...
... (11 total)
```

### Phase 5: Model Downloads (1-4 hours)

Downloads 45+ AI models:
- Parallel downloads from HuggingFace (aria2c)
- Sequential downloads from Civitai (curl) with retry logic
- File size validation for corruption detection

**Progress Indicators**:
```
Downloading wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors → diffusion_models
Downloading illustrij_v16.safetensors → checkpoints (using curl with Civitai auth)
... (45+ downloads)
```

**Key Model Downloads**:
- Diffusion models: ~14GB
- Checkpoints: ~30GB
- LoRAs: ~20GB
- Other models: ~10GB

### Phase 6: Python Dependencies (5-10 minutes)

Installs Python packages for custom nodes:

```
pip install diffusers gguf accelerate ftfy opencv-python-headless matplotlib \
  scikit-image ultralytics piexif dill segment-anything
```

Required by:
- WanVideoWrapper → accelerate
- Impact-Pack → ultralytics, piexif, dill, segment-anything
- Various nodes → diffusers, scikit-image, opencv

### Phase 7: Model Whitelists (< 1 minute)

Creates configuration for Impact-Subpack:

```
/workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack/model-whitelist.txt
```

Lists allowed detection models:
```
bbox/penis.pt
bbox/nipple.pt
bbox/Eyeful_v2-Paired.pt
bbox/face_yolov8m.pt
bbox/hand_yolov8s.pt
```

### Phase 8: Workflow Deployment (< 1 minute)

Copies workflow files from bootstrap:

```bash
mkdir -p user/default/workflows
cp /workspace/bootstrap/workflows/*.json user/default/workflows/
```

(Only if workflows exist in bootstrap repo)

### Phase 9: Launch ComfyUI (< 1 minute)

Starts ComfyUI server:

```bash
nohup python main.py \
  --listen 0.0.0.0 \
  --port 8188 \
  > /workspace/comfyui.log 2>&1 &
```

**Output**:
```
ComfyUI started.
Log file: /workspace/comfyui.log
```

---

## Monitoring Installation

### Watch Overall Progress

```bash
tail -f /workspace/comfyui.log
```

### Check Model Downloads

```bash
# Terminal 1: Watch file sizes growing
watch 'du -sh /workspace/ComfyUI/models'

# Terminal 2: Watch individual models
ls -lh /workspace/ComfyUI/models/checkpoints/
```

### Monitor System Resources

```bash
# Watch GPU/CPU/Memory usage
watch nvidia-smi

# Watch disk usage
watch 'df -h /workspace'
```

### Check Aria2c Download Status

```bash
# If downloads seem stuck
ps aux | grep aria2c

# If hanging, can kill and re-run (will resume)
pkill aria2c
bash /workspace/bootstrap/install.sh
```

---

## Troubleshooting Installation

### Issue: "Permission Denied" on Script

**Symptoms**:
```
bash: /workspace/bootstrap/install.sh: Permission denied
```

**Fix**:
```bash
chmod +x /workspace/bootstrap/install.sh
bash /workspace/bootstrap/install.sh
```

---

### Issue: "Git Clone Failed" During Custom Nodes

**Symptoms**:
```
fatal: repository not found
```

**Causes**:
- Git not installed (unlikely)
- Network connectivity issue
- GitHub API rate limit

**Fixes**:
```bash
# Check git
which git

# Check network
ping github.com

# Re-run installer (skips existing nodes)
bash /workspace/bootstrap/install.sh
```

---

### Issue: "Civitai Download Failed" (83KB file)

**Symptoms**:
```
Downloaded file too small (83000 bytes) - likely corrupted. Retrying...
```

**Causes**:
- Missing or invalid CIVITAI_TOKEN
- Civitai link expired
- Rate limiting

**Fixes**:

1. **Verify token**:
   ```bash
   echo $CIVITAI_TOKEN
   # Should show: xxx...xxx (not empty)
   ```

2. **Test Civitai directly**:
   ```bash
   curl -L -H "Authorization: Bearer ${CIVITAI_TOKEN}" \
     "https://civitai.com/api/download/models/1942437..." \
     -o test.safetensors

   ls -lh test.safetensors  # Should be >100MB
   ```

3. **Re-export token if needed**:
   ```bash
   export CIVITAI_TOKEN="your_new_token"
   bash /workspace/bootstrap/install.sh
   ```

4. **Wait between retries**:
   - Script waits 5 seconds between retries
   - Civitai may rate-limit after multiple attempts
   - Can pause and resume later

---

### Issue: "ModuleNotFoundError" During Installation

**Symptoms**:
```
ModuleNotFoundError: No module named 'X'
```

**Causes**:
- pip install failed silently
- Custom node has undocumented dependency
- Virtual environment not activated

**Fixes**:

1. **Activate venv**:
   ```bash
   source /workspace/ComfyUI/venv/bin/activate
   ```

2. **Install missing module**:
   ```bash
   pip install module_name
   ```

3. **Check installation**:
   ```bash
   python -c "import module_name"
   ```

4. **Add to install.sh** (for future pods):
   Edit line 167, add module to pip install command.

---

### Issue: "Out of Memory" During Downloads

**Symptoms**:
```
Killed
```

**Causes**:
- Parallel aria2c downloads using too much RAM
- Other processes consuming memory

**Fixes**:

1. **Reduce parallel connections** in install.sh line 126:
   ```bash
   # Change from:
   aria2c -x16 -s16 ...
   # To:
   aria2c -x8 -s8 ...
   ```

2. **Kill background jobs**:
   ```bash
   pkill aria2c
   pkill wget
   ```

3. **Check memory usage**:
   ```bash
   free -h
   ps aux --sort=-%mem | head -10
   ```

4. **Resume installation**:
   ```bash
   bash /workspace/bootstrap/install.sh
   # Will skip existing files, continue downloads
   ```

---

### Issue: "ComfyUI Port 8188 Already in Use"

**Symptoms**:
```
Address already in use
```

**Causes**:
- ComfyUI already running
- Previous instance didn't shutdown cleanly

**Fixes**:

1. **Kill existing process**:
   ```bash
   pkill python
   ```

2. **Start on different port**:
   ```bash
   cd /workspace/ComfyUI
   python main.py --listen 0.0.0.0 --port 8189
   ```

3. **Check what's using port 8188**:
   ```bash
   lsof -i :8188
   kill -9 <PID>
   ```

---

### Issue: "Models Not Appearing in Dropdown"

**Symptoms**:
- Model loader shows empty list
- No checkpoints/LoRAs available

**Causes**:
- Models didn't download successfully
- Downloaded to wrong folder
- ComfyUI cache not refreshed

**Fixes**:

1. **Check if files exist**:
   ```bash
   ls -l /workspace/ComfyUI/models/checkpoints/
   ls -l /workspace/ComfyUI/models/loras/
   ```

2. **Check file integrity**:
   ```bash
   du -h /workspace/ComfyUI/models/checkpoints/*.safetensors
   # Should be >100MB, not <1MB
   ```

3. **Refresh UI**:
   - ComfyUI Menu → Extra options → "Refresh models"

4. **Restart ComfyUI**:
   ```bash
   pkill python
   cd /workspace/ComfyUI
   python main.py --listen 0.0.0.0 --port 8188 &
   ```

5. **Check logs for errors**:
   ```bash
   grep -i "error\|fail" /workspace/comfyui.log | tail -20
   ```

---

### Issue: "Custom Node Not Loading"

**Symptoms**:
- Node doesn't appear in UI
- Red error in node selector
- Import error in logs

**Fixes**:

1. **Verify node cloned**:
   ```bash
   ls /workspace/ComfyUI/custom_nodes/ | grep -i nodename
   ```

2. **Check node dependencies**:
   ```bash
   source /workspace/ComfyUI/venv/bin/activate
   cd /workspace/ComfyUI/custom_nodes/NodeRepository
   python -m pip install -r requirements.txt 2>/dev/null || true
   ```

3. **Check logs for import errors**:
   ```bash
   tail -50 /workspace/comfyui.log | grep -i error
   ```

4. **Restart with full error output**:
   ```bash
   pkill python
   cd /workspace/ComfyUI
   source venv/bin/activate
   python main.py --listen 0.0.0.0 --port 8188 2>&1 | tee /tmp/debug.log
   # Let it run for 30 seconds, Ctrl+C
   grep -i error /tmp/debug.log
   ```

---

## Post-Installation Verification

### Checklist

- [ ] ComfyUI accessible at `your-pod-url:8188`
- [ ] No red errors in node selector
- [ ] Models appearing in dropdowns
- [ ] Can load a checkpoint
- [ ] Can load a LoRA
- [ ] FaceDetailer node available
- [ ] WAN sampler available
- [ ] Can create basic workflow

### Quick Test Workflow

1. **Load Checkpoint**:
   - Add "Load Checkpoint" node
   - Select any SDXL checkpoint
   - Should load without error

2. **Add Sampler**:
   - Add "KSampler" or "KSampler Refined"
   - Set steps to 4 (quick test)
   - Set CFG to 7

3. **Add Output**:
   - Add "VAE Decode"
   - Connect to sampler
   - Add "Save Image" node

4. **Generate**:
   - Click "Queue" button
   - Should complete in <30 seconds
   - Should see generated image

---

## Performance Optimization

### After Installation

1. **Monitor Resource Usage**:
   ```bash
   watch nvidia-smi
   # Watch VRAM usage during generation
   ```

2. **Adjust Model Precision**:
   - Use FP8 quantized models (default)
   - Save ~20% VRAM vs FP16

3. **Disable Unused Nodes**:
   - ComfyUI-Manager → Disable unused custom nodes
   - Frees memory for actual generation

4. **Optimize Settings**:
   - Batch size: 1 (balance speed/quality)
   - Tile size for upscaling: 512px
   - Use attention splitting if VRAM low

---

## Backup & Restore

### Backup Installation

```bash
# Compress entire ComfyUI installation
tar -czf comfyui-backup.tar.gz /workspace/ComfyUI/

# Upload to storage (Dropbox, S3, etc)
```

### Restore from Backup

```bash
# Decompress
tar -xzf comfyui-backup.tar.gz -C /

# Restart ComfyUI
pkill python
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 &
```

---

## Deployment Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Instance Start | 1-2 min | RunPod container boot |
| Clone Bootstrap | <1 min | Fast |
| System Dependencies | 2-5 min | apt install |
| ComfyUI Core | 10-15 min | PyTorch download large |
| Custom Nodes | 5-10 min | GitHub cloning |
| Model Downloads | 1-4 hours | Depends on connection |
| Dependencies Install | 5-10 min | pip install |
| ComfyUI Launch | <1 min | Service startup |
| **Total** | **2-5 hours** | Mostly model downloading |

---

## Success Indicators

✅ ComfyUI accessible at pod URL
✅ No red errors in "Search nodes" menu
✅ 5+ SDXL checkpoints in dropdown
✅ 10+ LoRAs in dropdown
✅ FaceDetailer node available
✅ Test generation completes <60 seconds
✅ Generated image visible in UI

---

## Next Steps After Installation

1. **Upload Custom Workflows**: `user/default/workflows/`
2. **Add Custom Models**: Edit `models.txt` and re-run installer
3. **Configure Settings**: ComfyUI Extra options menu
4. **Test Performance**: Run actual workflow
5. **Optimize**: Adjust tile sizes, batch sizes as needed

---

**Last Updated**: 2025-12-23

For advanced troubleshooting, check `/workspace/comfyui.log` and `/tmp/install.log`
