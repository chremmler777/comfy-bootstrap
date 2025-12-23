# Model Configuration Documentation

Complete reference for all models configured in `models.txt`.

## Overview

The bootstrap installer downloads 45+ AI models across 8 categories:
- **Diffusion Models**: WAN 2.2 image-to-video models
- **Checkpoints**: SDXL base models for image generation
- **LoRAs**: Fine-tuning models for style/concept control
- **VAEs**: Latent variable autoencoders for encoding/decoding
- **Text Encoders**: Text-to-embedding models
- **Detection Models**: YOLO object detection models
- **Upscalers**: Super-resolution models
- **SAM Models**: Segment Anything for image segmentation

## Model Categories

### 1. Diffusion Models (2 models)

Backbone models for image-to-video synthesis using WAN 2.2 architecture.

| Model | Size | Format | Purpose |
|-------|------|--------|---------|
| wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors | ~7GB | SafeTensor | High noise variation for video synthesis |
| wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors | ~7GB | SafeTensor | Low noise variation for video synthesis |

**Source**: HuggingFace (Comfy-Org)
**Architecture**: WAN 2.2 (14B parameters, FP8 quantized)
**Use Case**: Image-to-video generation with WanVideoWrapper node

**Installation Path**: `/workspace/ComfyUI/models/diffusion_models/`

---

### 2. Checkpoints (5 models)

SDXL base models for 2D image generation. These are large foundation models that provide the base generative capabilities.

| Model | Size | Style | Quantization |
|-------|------|-------|--------------|
| illustrij_v16.safetensors | ~6-7GB | Illustration | FP16 |
| divingIllustriousReal_v50VAE.safetensors | ~6GB | Realistic | FP16 |
| lustifySDXLNSFW_endgame.safetensors | ~6GB | NSFW-optimized | FP16 |
| xxxRay_v11.safetensors | ~6GB | Illustration | FP16 |
| novaAsianXL_illustriousV50.safetensors | ~6GB | Asian features | FP16 |

**Source**: Civitai (except novaAsian from HuggingFace)
**Format**: SafeTensor (weights only)
**Installation Path**: `/workspace/ComfyUI/models/checkpoints/`

**Details**:
- **illustrij_v16**: General illustration model with diverse art styles
- **divingIllustriousReal_v50VAE**: High-quality realistic rendering
- **lustifySDXLNSFW_endgame**: Specialized for NSFW content generation
- **xxxRay_v11**: Illustration-focused with varied artistic styles
- **novaAsianXL_illustriousV50**: Optimized for Asian features and characteristics

---

### 3. LoRAs (14 models)

Low-Rank Adaptation (LoRA) models for fine-tuning without full model retraining. Each adds specific capabilities or style characteristics.

#### WAN 2.2 Inference LoRAs (2)
| Model | Purpose |
|-------|---------|
| wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors | Fast low-noise video inference |
| wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors | Fast high-noise video inference |

#### Style & Effect LoRAs (12)

**Photography & Composition**:
| Model | Effect |
|-------|--------|
| spo_sdxl_10ep_4k-data_lora_webui.safetensors | Professional photography style |
| cinematic_photography_detailed_illu_xl.safetensors | Cinematic photography detail |

**Anatomical Enhancement**:
| Model | Target |
|-------|--------|
| Penis_Size_alpha1.0_rank4_noxattn_last.safetensors | Penis size control slider |
| testicles_slider_IXLR1_alpha16.0_rank32_full_last.safetensors | Testicle appearance slider |
| Realistic_Saggy_Testicles.safetensors | Realistic testicle rendering |
| PenisQuiron_illus.safetensors | Illustrious style penis rendering |
| MS_Breasts_Style_V1_IL.safetensors | Breast style and appearance |
| Breast_Size_Slider_Illustrious_V2.safetensors | Breast size control slider |

**Character & Concept**:
| Model | Concept |
|--------|---------|
| qqq-grabbing_from_behind-v2-000006.safetensors | Specific pose/action concept |
| scarlet-nikke-richy-v1_pdxl.safetensors | Character style (Scarlet Nikke) |
| longnippls-vp2-000012.safetensors | Specific anatomical feature |

**Realism & Enhancement**:
| Model | Effect |
|-------|--------|
| ILXL_Realism_Slider_V.1.safetensors | Realism level control |
| zy_illustrious_Realism_Enhancer_v1.safetensors | Realism enhancement for Illustrious |
| zy_AmateurStyle_v2.safetensors | Amateur/casual aesthetic |

**Source**: Civitai (most) and HuggingFace
**Installation Path**: `/workspace/ComfyUI/models/loras/`

**Usage**: Load in ComfyUI as "LoRA Loader" node with strength 0.0-1.0

---

### 4. VAE Models (2)

Variational Autoencoders for encoding images to latent space and decoding latent back to images.

| Model | Size | Source |
|-------|------|--------|
| wan_2.1_vae.safetensors | ~1.5GB | WAN 2.1 official |
| sdxl_vae.safetensors | ~1.5GB | Stability AI |

**Installation Path**: `/workspace/ComfyUI/models/vae/`

**Details**:
- **wan_2.1_vae**: Optimized for WAN models, handles complex image features
- **sdxl_vae**: SDXL-specific VAE with optimized latent representation

**Usage**: Selected in checkpoint loader or VAE loader nodes
**Recommended**: Use matching VAE with checkpoint model (WAN vae for WAN, SDXL vae for SDXL)

---

### 5. Text Encoders (1)

Text embedding models that convert prompts to numerical representations.

| Model | Parameters | Quantization |
|-------|-----------|--------------|
| umt5_xxl_fp8_e4m3fn_scaled.safetensors | 11B | FP8 |

**Source**: HuggingFace (Comfy-Org)
**Installation Path**: `/workspace/ComfyUI/models/text_encoders/`

**Details**:
- **UMT5 XXL**: Universal Multilingual T5, supports multiple languages
- **FP8 Quantized**: Reduced precision for faster inference and lower memory
- **Purpose**: Encodes text prompts for image/video generation

**Configuration**: Required for WAN 2.2 models, automatically loaded

---

### 6. Detection Models (5)

YOLO-based object detection models for identifying faces, hands, and anatomical features.

| Model | Type | Purpose |
|-------|------|---------|
| face_yolov8m.pt | YOLOv8 Medium | Face detection |
| hand_yolov8s.pt | YOLOv8 Small | Hand detection |
| penis.pt | Custom YOLO | Penis detection |
| nipple.pt | Custom YOLO | Nipple detection |
| Eyeful_v2-Paired.pt | Custom YOLO | Eye region detection |

**Installation Path**: `/workspace/ComfyUI/models/ultralytics/bbox/`

**Source**: HuggingFace community models
**Format**: PyTorch (.pt)

**Details**:
- **face_yolov8m**: Standard face detection, moderate speed/accuracy tradeoff
- **hand_yolov8s**: Lightweight hand detection model
- **Custom Models**: Trained for specific anatomical features in artwork

**Usage**:
- Loaded by ComfyUI-Impact-Pack's `UltralyticsDetectorProvider`
- Used for FaceDetailer node for targeted enhancement
- Can be used with SAMLoader for precise segmentation

**Configuration**: Model whitelist at `/workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack/model-whitelist.txt`

---

### 7. Upscalers (1)

Super-resolution models for increasing image resolution.

| Model | Scale | Size | Architecture |
|-------|-------|------|--------------|
| 4x_foolhardy_Remacri.pth | 4x | ~150MB | ESRGAN-based |

**Installation Path**: `/workspace/ComfyUI/models/upscale_models/`

**Source**: HuggingFace (community)
**Format**: PyTorch (.pth)

**Details**:
- **4x Upscaling**: Increases resolution by 4x (e.g., 512→2048)
- **Foolhardy Remacri**: Balanced quality/speed variant
- **Usage**: Applied after generation or on existing images
- **Node**: "Upscale Image (using Model)" in ComfyUI

**Configuration**: Loaded by upscaler loader nodes

---

### 8. SAM Models (1)

Segment Anything Model for instance segmentation and mask generation.

| Model | Size | Purpose |
|-------|------|---------|
| sam_vit_b_01ec64.pth | ~375MB | Instance segmentation |

**Installation Path**: `/workspace/ComfyUI/models/sams/`

**Source**: Meta AI (Official)
**Format**: PyTorch (.pth)

**Details**:
- **ViT-B backbone**: Base size model balancing quality and speed
- **Purpose**: Generate masks for any object/region in an image
- **Node**: "SAMLoader" in ComfyUI-Impact-Pack
- **Usage**: Combined with FaceDetailer for precise face enhancement

**Performance**:
- **Speed**: ~100-200ms per image
- **Memory**: ~1-2GB VRAM
- **Quality**: High-quality segmentation masks

---

## Model Configuration Format

The `models.txt` file uses a simple space-separated format:

```
folder url filename
```

### Examples

```
# Checkpoint from Civitai
checkpoints https://civitai.com/api/download/models/1942437?type=Model&format=SafeTensor&size=full&fp=fp16 illustrij_v16.safetensors

# LoRA from HuggingFace
loras https://huggingface.co/LyliaEngine/spo_sdxl_10ep_4k-data_lora_webui/resolve/main/spo_sdxl_10ep_4k-data_lora_webui.safetensors spo_sdxl_10ep_4k-data_lora_webui.safetensors

# Detection model
ultralytics/bbox https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt face_yolov8m.pt
```

### Download Behavior

**HuggingFace URLs** (lines 3+ in examples):
- Downloaded with **aria2c** (parallel, 16 connections)
- Runs in **background** to enable concurrent downloads
- Continues from interrupted downloads

**Civitai URLs** (lines 1-2 in examples):
- Downloaded with **curl** (sequential)
- Supports **CIVITAI_TOKEN** authentication
- Includes **retry logic** with file size validation
- Waits for other Civitai downloads to complete

---

## Adding Models

### Step 1: Find the Model URL

**HuggingFace**:
1. Navigate to model page
2. Click "Files and versions"
3. Right-click file → "Copy link"
4. Example: `https://huggingface.co/user/model/resolve/main/file.safetensors`

**Civitai**:
1. Find model on civitai.com
2. Note the Model ID (e.g., `1942437`)
3. Construct download URL:
   ```
   https://civitai.com/api/download/models/MODEL_ID?type=Model&format=SafeTensor&size=pruned&fp=fp16
   ```

### Step 2: Determine Folder

Choose the appropriate folder based on model type:
- `checkpoints/` - Checkpoint/base models
- `loras/` - LoRA fine-tunes
- `vae/` - VAE models
- `text_encoders/` - Text embeddings
- `diffusion_models/` - Diffusion backbones
- `ultralytics/bbox/` - Detection models
- `upscale_models/` - Upscalers

### Step 3: Choose Filename

Use a descriptive name matching the original:
```
good:   checkpoint_v2.safetensors
bad:    file.safetensors
better: illustrious_v2_pruned_fp16.safetensors
```

### Step 4: Add to models.txt

```
loras https://civitai.com/api/download/models/12345?type=Model&format=SafeTensor my_new_lora.safetensors
```

### Step 5: Test

Run on fresh pod and verify download/placement:
```bash
ls /workspace/ComfyUI/models/loras/ | grep my_new_lora
```

---

## Troubleshooting Models

### Issue: Model Not Found in ComfyUI

**Symptoms**: Dropdown shows no models in loader node

**Possible Causes**:
1. Wrong folder name in `models.txt`
2. Download failed silently
3. Filename incompatible with loader

**Solutions**:
```bash
# Check if files exist
ls /workspace/ComfyUI/models/checkpoints/
ls /workspace/ComfyUI/models/loras/

# Check download log
tail -50 /workspace/comfyui.log

# Verify file integrity
ls -lh /workspace/ComfyUI/models/checkpoints/
```

### Issue: Civitai Download Failing

**Symptoms**: File stuck at 83KB or fails after retries

**Solutions**:
1. Verify Civitai token: `echo $CIVITAI_TOKEN`
2. Test manually:
   ```bash
   curl -L -H "Authorization: Bearer YOUR_TOKEN" \
     "https://civitai.com/api/download/models/12345..." \
     -o test.safetensors
   ```
3. Check if link still works on civitai.com
4. Try reducing file size or format (e.g., smaller variant)

### Issue: Out of Memory During Download

**Symptoms**: Process killed during aria2c parallel downloads

**Solutions**:
1. Limit aria2c connections in install.sh (line 126):
   ```bash
   aria2c -x8 -s8 ...  # Reduce from -x16 -s16
   ```
2. Download in stages:
   ```bash
   # Comment out some model groups in models.txt
   # Run installer
   # Uncomment and re-run for next batch
   ```
3. Monitor memory:
   ```bash
   watch nvidia-smi
   ```

### Issue: Corrupted Model File

**Symptoms**: Checksum mismatch or "invalid safetensor" error

**Solutions**:
1. Delete and re-download:
   ```bash
   rm /workspace/ComfyUI/models/checkpoints/corrupt_file.safetensors
   # Re-run installer (will download again)
   ```
2. Verify file size matches expected size
3. Try different file format (e.g., pruned vs full)

---

## Storage Considerations

### Disk Space Requirements

```
Diffusion Models:      ~14GB
Checkpoints (5):       ~30GB
LoRAs (14):            ~20GB
VAEs (2):              ~3GB
Text Encoders (1):     ~5GB
Detection (5):         ~500MB
Upscalers (1):         ~150MB
SAM Models (1):        ~375MB
─────────────────────────────
Total:                 ~73GB
```

**Minimum SSD**: 256GB (allows room for generations)
**Recommended**: 500GB+ (better performance, cached generations)

### Optimization Tips

1. **Delete unused models**: Frees up space
2. **Use pruned variants**: Smaller files, minimal quality loss
3. **Use FP8 quantization**: Smaller than FP16, similar quality
4. **Separate fast/slow storage**: Keep hot models on NVMe

---

## Model Compatibility Matrix

| Checkpoint | VAE | LoRA Compatibility |
|-----------|-----|-------------------|
| illustrij_v16 | sdxl_vae | All SDXL LoRAs |
| divingIllustriousReal | sdxl_vae | All SDXL LoRAs |
| lustifySDXLNSFW | sdxl_vae | All SDXL LoRAs |
| xxxRay_v11 | sdxl_vae | All SDXL LoRAs |
| novaAsianXL | sdxl_vae | All SDXL LoRAs |

**WAN 2.2 Models**:
- Diffusion: `wan2.2_i2v_*`
- VAE: `wan_2.1_vae.safetensors`
- Text Encoder: `umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- LoRA: `wan2.2_i2v_lightx2v_*`

---

## Updates

To update models list, edit `models.txt` and re-run installer on fresh pod.

All downloads are idempotent - existing files are skipped, missing files are downloaded.

---

**Last Updated**: 2025-12-23
