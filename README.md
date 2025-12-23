# ComfyUI Bootstrap - Automated Installation & Model Setup

Complete automated bootstrap installer for ComfyUI on RunPod with pre-configured models, custom nodes, and all dependencies.

## Overview

This project provides a one-command installation script that sets up a fully functional ComfyUI instance with:
- **11 custom node repositories** pre-installed
- **45+ AI models** pre-configured for download (checkpoints, LoRAs, VAEs, diffusion models, detection models, upscalers)
- **All Python dependencies** pre-installed
- **Automatic Civitai authentication** with retry logic for reliable downloads
- **Optimized parallel downloads** (HuggingFace parallel, Civitai sequential to avoid rate limits)
- **Automatic service startup** on boot

## Quick Start

### RunPod Deployment

1. **Clone to RunPod workspace**:
   ```bash
   cd /workspace
   git clone https://github.com/chremmler777/comfy-bootstrap.git bootstrap
   ```

2. **Run the bootstrap installer**:
   ```bash
   bash /workspace/bootstrap/install.sh
   ```

3. **(Optional) Set Civitai token for authentication**:
   ```bash
   export CIVITAI_TOKEN="your_token_here"
   bash /workspace/bootstrap/install.sh
   ```

4. **Access ComfyUI**:
   - URL: `http://your-runpod-url:8188`
   - Log file: `/workspace/comfyui.log`

## Installation Details

### What Gets Installed

#### System Dependencies
- git, wget, aria2, ffmpeg, python3-venv, curl

#### Core ComfyUI
- ComfyUI cloned from official repository
- PyTorch with CUDA 12.1 support
- All core requirements from requirements.txt

#### Custom Node Repositories (11 total)
1. **ComfyUI-Manager** - Node and model management UI
2. **ComfyUI-WanVideoWrapper** - WAN 2.2 video generation wrapper
3. **ComfyUI-GGUF** - GGUF quantized model support
4. **ComfyUI-Impact-Pack** - Advanced face detection, SAM integration
5. **rgthree-comfy** - Seed control, power tools, groups
6. **ComfyUI-Custom-Scripts** - Utility scripts and playback
7. **ComfyUI-KJNodes** - Custom KJ nodes
8. **ComfyUI-UltimateSDUpscale** - Advanced upscaling
9. **ComfyUI_essentials** - Essential utility nodes
10. **ComfyUI-Detail-Daemon** - Detail enhancement sampler
11. **ComfyUI-Impact-Subpack** - Additional Impact tools

#### Python Dependencies
```
diffusers gguf accelerate ftfy opencv-python-headless matplotlib
scikit-image ultralytics piexif dill segment-anything
```

#### AI Models (45+ models)

**Diffusion Models**:
- WAN 2.2 image-to-video models (14B parameters, FP8 quantized)

**Checkpoints** (5 SDXL models):
- illustrij_v16.safetensors (Illustrious style)
- divingIllustriousReal_v50VAE.safetensors (Realistic)
- lustifySDXLNSFW_endgame.safetensors (NSFW-optimized)
- xxxRay_v11.safetensors (Illustration)
- novaAsianXL_illustriousV50.safetensors (Asian features)

**LoRAs** (13 total):
- WAN 2.2 light inference LoRAs (2)
- Custom workflow LoRAs:
  - spo_sdxl_10ep_4k-data_lora_webui.safetensors
  - qqq-grabbing_from_behind-v2-000006.safetensors
  - Penis_Size_alpha1.0_rank4_noxattn_last.safetensors
  - testicles_slider_IXLR1_alpha16.0_rank32_full_last.safetensors
  - Realistic_Saggy_Testicles.safetensors
  - PenisQuiron_illus.safetensors
  - scarlet-nikke-richy-v1_pdxl.safetensors
  - longnippls-vp2-000012.safetensors
  - MS_Breasts_Style_V1_IL.safetensors
  - Breast_Size_Slider_Illustrious_V2.safetensors
  - cinematic_photography_detailed_illu_xl.safetensors
  - ILXL_Realism_Slider_V.1.safetensors
  - zy_illustrious_Realism_Enhancer_v1.safetensors
  - zy_AmateurStyle_v2.safetensors

**VAE Models** (2):
- wan_2.1_vae.safetensors (WAN 2.1 VAE)
- sdxl_vae.safetensors (SDXL VAE)

**Text Encoders** (1):
- umt5_xxl_fp8_e4m3fn_scaled.safetensors (UMT5 XXL)

**Detection Models** (5 YOLO):
- penis.pt (custom detection)
- nipple.pt (custom detection)
- Eyeful_v2-Paired.pt (custom detection)
- face_yolov8m.pt (face detection)
- hand_yolov8s.pt (hand detection)

**Upscalers** (1):
- 4x_foolhardy_Remacri.pth (4x upscaling)

**SAM Models** (1):
- sam_vit_b_01ec64.pth (Segment Anything)

**Total Download Size**: ~180-250GB (depends on model variants)

## Configuration

### Civitai Authentication

Some models are hosted on Civitai and require authentication:

1. **Get your Civitai token**: https://civitai.com/user/account
2. **Set environment variable**:
   ```bash
   export CIVITAI_TOKEN="your_token_here"
   bash /workspace/bootstrap/install.sh
   ```

Without a token, Civitai downloads may fail or return corrupted files.

### Adding Custom Models

Edit `models.txt` to add custom models:

```
# Format: folder url filename
loras https://example.com/model.safetensors custom_name.safetensors
checkpoints https://civitai.com/api/download/models/12345?type=Model&format=SafeTensor checkpoint.safetensors
```

**Supported Folders**:
- `checkpoints/` - SDXL checkpoint models
- `diffusion_models/` - Diffusion backbone models
- `loras/` - LoRA fine-tuning models
- `vae/` - VAE models
- `text_encoders/` - Text embedding models
- `ultralytics/bbox/` - YOLO detection models
- `upscale_models/` - Upscaler models

### Adding Custom Nodes

Edit `custom_nodes.txt` to add custom node repositories:

```
https://github.com/username/ComfyUI-CustomNode
```

One repository URL per line. Comments and blank lines are ignored.

## Download Strategy

The installer uses an optimized download strategy:

### HuggingFace Downloads (aria2c - Parallel)
- **16 parallel connections** for speed
- **Continues incomplete downloads**
- **Runs in background** while Civitai downloads proceed

### Civitai Downloads (curl - Sequential)
- **Sequential downloads** to avoid rate limiting
- **Automatic authentication** via CIVITAI_TOKEN header
- **Retry logic**: Up to 3 attempts with file size validation
- **Corruption detection**: Files < 500KB are considered corrupted HTML pages

### File Size Validation
```bash
if [ "$FILE_SIZE" -lt 500000 ]; then
  # File is likely an HTML error page, retry
fi
```

## Troubleshooting

### Issue: Civitai Downloads Failing

**Symptoms**: 83KB files instead of GB-sized models

**Solutions**:
1. Set CIVITAI_TOKEN environment variable
2. Check Civitai API links are still valid
3. Ensure User-Agent header is sent (included in script)
4. Wait 5 minutes between retries (built into script)

### Issue: Missing Python Module

**Symptoms**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
source /workspace/ComfyUI/venv/bin/activate
pip install module_name
```

Then update `install.sh` line 167 to include the new dependency.

### Issue: Node Import Failures

**Symptoms**: Nodes show red in UI, log shows import errors

**Solutions**:
1. Ensure all custom_nodes.txt repositories cloned correctly
2. Check Python dependencies (see above)
3. Verify model files exist in correct folders
4. Restart ComfyUI:
   ```bash
   pkill python
   cd /workspace/ComfyUI
   nohup python main.py --listen 0.0.0.0 --port 8188 > /workspace/comfyui.log 2>&1 &
   ```

### Issue: Out of Memory

**Symptoms**: Kernel panic or OOM errors

**Solutions**:
- Use fp8 quantized models (default)
- Disable unused custom nodes
- Use smaller checkpoint variants
- Monitor with `nvidia-smi` while generating

### Issue: ComfyUI Port Already in Use

**Symptoms**: `Address already in use` on port 8188

**Solutions**:
```bash
# Kill existing process
pkill python

# Or use different port
python main.py --listen 0.0.0.0 --port 8189
```

## File Structure

```
/workspace/
├── ComfyUI/                          # Main ComfyUI installation
│   ├── models/
│   │   ├── checkpoints/              # SDXL checkpoints
│   │   ├── diffusion_models/         # Diffusion backbones
│   │   ├── loras/                    # LoRA models
│   │   ├── vae/                      # VAE models
│   │   ├── text_encoders/            # Text encoders
│   │   ├── ultralytics/
│   │   │   └── bbox/                 # YOLO detection models
│   │   ├── upscale_models/           # Upscalers
│   │   └── sams/                     # Segment Anything models
│   ├── custom_nodes/                 # 11 installed node repositories
│   ├── user/
│   │   └── default/
│   │       ├── workflows/            # Workflow JSON files
│   │       └── ComfyUI-Impact-Subpack/
│   │           └── model-whitelist.txt
│   ├── venv/                         # Python virtual environment
│   └── main.py
├── bootstrap/                        # This repository
│   ├── install.sh                    # Main installer script
│   ├── models.txt                    # Model configuration
│   ├── custom_nodes.txt              # Custom node repositories
│   ├── workflows/                    # Workflow files (if present)
│   └── README.md
└── comfyui.log                       # ComfyUI server log
```

## Installation Time Estimates

- **System setup**: 2-5 minutes
- **ComfyUI & dependencies**: 10-15 minutes
- **Custom nodes clone**: 5-10 minutes
- **Model downloads**: 1-4 hours (depending on connection speed)

**Total**: 2-5 hours for complete installation

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `CIVITAI_TOKEN` | Civitai API authentication | `export CIVITAI_TOKEN="token_here"` |
| `HF_TOKEN` | HuggingFace token (optional) | `export HF_TOKEN="hf_token"` |

## Key Features

✅ **Fully Automated** - Single command installation
✅ **Fault Tolerant** - Retry logic for failed downloads
✅ **Optimized Downloads** - Parallel + sequential strategy
✅ **Dependency Complete** - All Python modules pre-installed
✅ **Model Integrity** - File size validation & corruption detection
✅ **Auto-Launch** - ComfyUI starts automatically
✅ **Logging** - Comprehensive logs at `/workspace/comfyui.log`
✅ **Extensible** - Easy to add models and nodes

## Testing on Fresh Pods

To validate a new RunPod pod:

1. SSH into pod
2. Run: `bash /workspace/bootstrap/install.sh 2>&1 | tee /tmp/install.log`
3. Wait for completion
4. Check logs: `tail -f /workspace/comfyui.log`
5. Access UI: `http://pod-url:8188`
6. Upload test workflow and verify nodes load

## Contributing

To update the bootstrap configuration:

1. Edit `models.txt`, `custom_nodes.txt`, or `install.sh`
2. Test on fresh RunPod pod
3. Commit changes: `git add . && git commit -m "description"`
4. Push: `git push`

## Support

For issues or improvements:
1. Check troubleshooting section above
2. Review `/workspace/comfyui.log` for errors
3. Check `/tmp/install.log` for installation errors
4. Open GitHub issue with error logs

## License

This bootstrap configuration is provided as-is for use with ComfyUI.

---

**Last Updated**: 2025-12-23
**Repository**: https://github.com/chremmler777/comfy-bootstrap
