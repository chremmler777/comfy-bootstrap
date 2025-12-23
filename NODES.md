# Custom Nodes Documentation

Complete reference for all 11 custom node repositories installed by the bootstrap.

## Overview

The bootstrap automatically installs 11 community-maintained custom node repositories that extend ComfyUI with additional functionality for image generation, enhancement, and manipulation.

## Custom Node Repositories

### 1. ComfyUI-Manager

**Repository**: https://github.com/ltdrdata/ComfyUI-Manager
**Purpose**: Node and model management interface

#### Key Features
- **Node Browser**: Browse, search, and install nodes from community
- **Model Manager**: Download and organize models directly from UI
- **Dependency Management**: Automatically resolves node dependencies
- **Node Search**: Full-text search across all available nodes
- **Update Checking**: Notifies when custom nodes have updates

#### Key Nodes
- Manager (main UI)
- Model Installer
- Node Browser

#### Installation
Automatically installed during bootstrap. Accessible via Manager menu in ComfyUI UI.

#### Use Cases
- Installing additional custom nodes at runtime
- Downloading models without command-line
- Managing node versions and dependencies
- Discovering new nodes and models

---

### 2. ComfyUI-WanVideoWrapper

**Repository**: https://github.com/kijai/ComfyUI-WanVideoWrapper
**Purpose**: Image-to-video generation wrapper

#### Key Features
- **WAN 2.2 Integration**: Wrapper for WAN image-to-video models
- **Batch Processing**: Process multiple images to video
- **Quality Control**: Adjustable noise levels and sampling steps
- **Fast Inference**: Optimized for 4-step fast inference

#### Key Nodes
- WAN Video Sampler
- Load WAN Models
- Video Output

#### Dependencies
- `accelerate` (for distributed inference)
- `diffusers` (for sampling)
- WAN diffusion models (wan2.2_i2v_*.safetensors)
- WAN VAE (wan_2.1_vae.safetensors)
- Text encoder (umt5_xxl_fp8_e4m3fn_scaled.safetensors)

#### Configuration
Add to custom_nodes.txt:
```
https://github.com/kijai/ComfyUI-WanVideoWrapper
```

#### Use Cases
- Converting images to short videos
- Smooth animation generation
- Video interpolation
- Motion synthesis

#### Example Workflow
1. Load image
2. Load WAN video sampler
3. Set noise level (high=more variation, low=consistency)
4. Run sampling (4-50 steps)
5. Encode output to video format

---

### 3. ComfyUI-GGUF

**Repository**: https://github.com/city96/ComfyUI-GGUF
**Purpose**: GGUF quantized model support

#### Key Features
- **GGUF Format**: Support for highly compressed models
- **CPU Inference**: Run models on CPU with low memory
- **Quantization**: Load FP8, INT8, INT4 quantized models
- **Flexibility**: Mix quantized and full-precision models

#### Key Nodes
- Load GGUF Model
- GGUF Sampler
- Quantize Model

#### Model Formats Supported
- `.gguf` - GGML quantized format
- `.ggml` - Original GGML format
- Quantization levels: FP32, FP16, FP8, INT8, INT4

#### Use Cases
- Running on low-memory systems
- CPU-only inference
- Model compression
- Cost optimization (less VRAM needed)

#### Configuration
Models in GGUF format go in:
```
checkpoints/         # For checkpoint GGUF
loras/              # For LoRA GGUF
```

---

### 4. ComfyUI-Impact-Pack

**Repository**: https://github.com/ltdrdata/ComfyUI-Impact-Pack
**Purpose**: Advanced face detection and segmentation

#### Key Features
- **FaceDetailer**: Automatic face enhancement/refinement
- **SAM Integration**: Segment Anything for precise masks
- **YOLO Detection**: Object detection for faces, hands, etc.
- **Iterative Refinement**: Multi-pass enhancement
- **ADetailer**: Works like Automatic1111's ADetailer

#### Key Nodes
- FaceDetailer
- SAMLoader
- UltralyticsDetectorProvider
- FaceSegmentation
- MaskToSegment
- IterativeLatentUpscale

#### Dependencies
- Detection models (face_yolov8m.pt, hand_yolov8s.pt)
- SAM model (sam_vit_b_01ec64.pth)
- `ultralytics` (YOLO)
- `piexif` (image metadata)
- `dill` (serialization)
- `segment-anything` (SAM)

#### Model Whitelist
Required models must be whitelisted:
```
# /workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack/model-whitelist.txt
bbox/face_yolov8m.pt
bbox/hand_yolov8s.pt
bbox/penis.pt
bbox/nipple.pt
bbox/Eyeful_v2-Paired.pt
```

#### Typical Workflow
```
Image → Ultralytics Detector (finds faces)
       → SAMLoader (creates masks)
       → FaceDetailer (enhances faces)
       → Output refined image
```

#### Use Cases
- Automatic face enhancement
- Face detail refinement
- Instance segmentation
- Multi-pass upscaling with face focus
- Precise mask generation

#### Performance Notes
- **FaceDetailer**: ~1-5 seconds per face
- **SAMLoader**: ~0.1-0.2 seconds per mask
- **Ultralytics**: ~0.5 seconds per image

---

### 5. rgthree-comfy

**Repository**: https://github.com/rgthree/rgthree-comfy
**Purpose**: Power tools and workflow utilities

#### Key Features
- **Seed Control**: Advanced seed management and locking
- **Power Tools**: Batch processing and looping
- **Groups**: Organize nodes into collapsible groups
- **Prompt Tools**: Advanced prompt manipulation
- **Fast Groups Bypasser**: Quick disable/enable node groups

#### Key Nodes
- Seed (with lock option)
- Power Prompt - Simple
- Power Prompt - Advanced
- Fast Groups Bypasser
- Fast Mutes
- Primitive (extended)

#### Features by Category

**Seed Management**:
- Lock/unlock seeds for consistency
- Increment/decrement by batch
- Copy seed between nodes
- Seed history

**Prompt Processing**:
- Multi-line prompt editing
- Wildcard expansion
- Prompt weighting
- Syntax highlighting

**Workflow Organization**:
- Collapsible groups for complex workflows
- Node linking and routing
- Fast bypass/mute toggles
- Layout management

#### Use Cases
- Batch generation with controlled variation
- Workflow organization
- Prompt experimentation
- Reproducible generations

#### Example: Seed Locking
```
Fixed Seed (123) → Deterministic output
Changed Seed (456) → Variation with locked faces/details
```

---

### 6. ComfyUI-Custom-Scripts

**Repository**: https://github.com/pythongosssss/ComfyUI-Custom-Scripts
**Purpose**: Utility scripts and automation

#### Key Nodes
- PlaySound (audio feedback on completion)
- ExecPython (run Python code in workflows)
- JavaScript Eval (run JS)
- Checkpoint Merger (combine checkpoints)
- Model Merge (blend LoRAs)
- WebhookEventListener (external triggers)

#### Dependencies
- Python 3.8+
- Standard library modules

#### Key Utilities

**Audio Feedback**:
```
PlaySound (plays beep on generation complete)
```

**Code Execution**:
```
ExecPython (run arbitrary Python in workflow context)
JavaScript Eval (run JS for browser-based operations)
```

**Model Operations**:
```
Checkpoint Merger (blend multiple checkpoints)
LoRA Merger (combine multiple LoRAs)
```

**Event Handling**:
```
WebhookEventListener (trigger workflows from external events)
```

#### Use Cases
- Workflow completion notifications
- Model blending experiments
- Automated processing pipelines
- Integration with external systems

---

### 7. ComfyUI-KJNodes

**Repository**: https://github.com/kijai/ComfyUI-KJNodes
**Purpose**: Advanced composition and layout nodes

#### Key Nodes
- LayerChain (layer-based editing)
- PathchSageAttentionKJ (attention manipulation)
- ColorMatch (match image colors)
- ImageSelector (batch selection)
- ImageCombine (merge images)
- TransitionMask (smooth transitions)

#### Key Features
- **Layer Operations**: Stack and blend images
- **Attention Control**: Modify attention maps
- **Color Matching**: Synchronize colors between images
- **Image Composition**: Advanced blending and cropping
- **Batch Operations**: Process image batches

#### Use Cases
- Layer-based image editing
- Advanced color grading
- Image composition
- Batch processing workflows
- Attention visualization

---

### 8. ComfyUI-UltimateSDUpscale

**Repository**: https://github.com/ssitu/ComfyUI_UltimateSDUpscale
**Purpose**: Advanced image upscaling with refinement

#### Key Nodes
- Ultimate SD Upscale
- Tile Settings
- Upscale Model Selector
- Latent Upscale (refined)

#### Key Features
- **Tile-based Upscaling**: Process large images in tiles
- **Overlap Handling**: Blend tiles for seamless results
- **Multiple Upscalers**: Support for various upscale models
- **Refinement Pass**: Optional detail enhancement
- **Progress Tracking**: Real-time progress display

#### Dependencies
- Upscale models (4x_foolhardy_Remacri.pth, etc.)
- Checkpoint model
- VAE

#### Workflow Example
```
512×512 image → Ultimate SD Upscale (2x tile)
            → 1024×1024 upscaled result
            → Optional refinement pass
```

#### Use Cases
- Upscaling 512px to 2048px+
- Tile-based processing of huge images
- Seamless tiling
- Detail enhancement during upscaling

#### Performance
- **2× upscale**: ~30-60 seconds per image
- **4× upscale**: ~2-5 minutes per image
- Tile size: adjustable (256-768px recommended)

---

### 9. ComfyUI_essentials

**Repository**: https://github.com/cubiq/ComfyUI_essentials
**Purpose**: Essential utility and convenience nodes

#### Key Nodes
- SDXLEmptyLatentSizePicker+
- Image utilities (crop, pad, resize)
- Latent utilities
- Prompt utilities
- Mask operations

#### Key Features
- **Size Picker**: Easy SDXL resolution selection
- **Image Tools**: Batch operations on images
- **Mask Tools**: Mask creation and manipulation
- **Prompt Tools**: Token counting, syntax checking
- **Latent Tools**: Latent space manipulation

#### Node Categories

**Size Selection**:
```
SDXLEmptyLatentSizePicker+ (predefined SDXL resolutions)
```

**Image Operations**:
```
Image Crop
Image Pad
Image Resize
Image Batch
```

**Mask Operations**:
```
Mask From Alpha
Alpha From Mask
Mask Invert
Mask Blend
```

#### Use Cases
- SDXL workflow setup
- Image preprocessing
- Mask manipulation
- Batch operations
- Resolution management

---

### 10. ComfyUI-Detail-Daemon

**Repository**: https://github.com/Jonseed/ComfyUI-Detail-Daemon
**Purpose**: Advanced sampling and detail enhancement

#### Key Nodes
- DetailDaemonSamplerNode
- LyingSigmaSampler
- DetailEnhancer
- AdvancedSigmaSchedule

#### Key Features
- **Custom Samplers**: Alternative sampling algorithms
- **Sigma Control**: Fine-grained noise schedule control
- **Detail Enhancement**: Iterative refinement
- **Advanced Scheduling**: Custom noise schedules
- **Multi-step Control**: Frame-by-frame refinement

#### Sampling Algorithms
- LyingSigmaSampler (specialized sigma handling)
- DetailDaemonSamplerNode (multi-stage refinement)
- Custom schedule generators

#### Use Cases
- Fine detail generation
- Custom noise schedules
- Multi-stage sampling
- Advanced quality control
- Sampling algorithm experimentation

#### Performance
- Minimal overhead compared to standard samplers
- More control = more iterations potentially needed

---

### 11. ComfyUI-Impact-Subpack

**Repository**: https://github.com/ltdrdata/ComfyUI-Impact-Subpack
**Purpose**: Extended Impact Pack functionality

#### Key Nodes
- Additional detectors
- Extended FaceDetailer variants
- Sepia/colorization tools
- Marker nodes
- Stream helpers

#### Key Features
- **Extended Detectors**: More detection models
- **Variant Samplers**: Alternative sampling methods
- **Colorization Tools**: Color-based filters
- **Streaming Support**: Real-time processing
- **Helper Nodes**: Utility functions

#### Dependencies
- ComfyUI-Impact-Pack (parent)
- Model whitelist (required)

#### Model Requirements
```
Model Whitelist Location:
/workspace/ComfyUI/user/default/ComfyUI-Impact-Subpack/model-whitelist.txt

Required entries:
bbox/penis.pt
bbox/nipple.pt
bbox/Eyeful_v2-Paired.pt
bbox/face_yolov8m.pt
bbox/hand_yolov8s.pt
```

#### Use Cases
- Custom detection workflows
- Extended face detailing
- Color processing
- Real-time generation

---

## Custom Nodes Node Mapping

Quick reference for finding specific nodes:

| Node Name | Repository |
|-----------|-----------|
| Manager | ComfyUI-Manager |
| PlaySound | ComfyUI-Custom-Scripts |
| WAN Video Sampler | ComfyUI-WanVideoWrapper |
| Load GGUF Model | ComfyUI-GGUF |
| FaceDetailer | ComfyUI-Impact-Pack |
| SAMLoader | ComfyUI-Impact-Pack |
| UltralyticsDetectorProvider | ComfyUI-Impact-Pack |
| Seed | rgthree-comfy |
| Fast Groups Bypasser | rgthree-comfy |
| Power Prompt - Simple | rgthree-comfy |
| LayerChain | ComfyUI-KJNodes |
| Ultimate SD Upscale | ComfyUI-UltimateSDUpscale |
| SDXLEmptyLatentSizePicker+ | ComfyUI_essentials |
| DetailDaemonSamplerNode | ComfyUI-Detail-Daemon |
| LyingSigmaSampler | ComfyUI-Detail-Daemon |

---

## Node Installation Issues

### Issue: Node Missing or Import Failed

**Symptoms**: Red error in node selector, import error in logs

**Diagnostics**:
```bash
# Check if repository cloned
ls /workspace/ComfyUI/custom_nodes/ | grep <node_name>

# Check Python dependencies
source /workspace/ComfyUI/venv/bin/activate
python -c "import <module>"

# Check logs
tail -100 /workspace/comfyui.log | grep -i error
```

**Common Fixes**:

1. **Missing Python dependency**:
   ```bash
   source /workspace/ComfyUI/venv/bin/activate
   pip install <missing_module>
   ```

2. **Repository not cloned**:
   ```bash
   cd /workspace/ComfyUI/custom_nodes
   git clone https://github.com/user/repo
   ```

3. **Restart ComfyUI**:
   ```bash
   pkill python
   cd /workspace/ComfyUI
   python main.py --listen 0.0.0.0 --port 8188 &
   ```

---

## Adding Custom Nodes

### Step 1: Find the Repository

Search GitHub for "ComfyUI" + node name or function

### Step 2: Get the Clone URL

Repository page → Code button → HTTPS URL

### Step 3: Add to custom_nodes.txt

```
https://github.com/user/ComfyUI-CustomNode
```

### Step 4: Clone Manually (if urgent)

```bash
cd /workspace/ComfyUI/custom_nodes
git clone https://github.com/user/ComfyUI-CustomNode
```

### Step 5: Install Dependencies (if needed)

```bash
source /workspace/ComfyUI/venv/bin/activate
pip install <required_package>
```

### Step 6: Restart ComfyUI

```bash
pkill python
cd /workspace/ComfyUI
nohup python main.py --listen 0.0.0.0 --port 8188 > /workspace/comfyui.log 2>&1 &
```

---

## Node Dependencies Summary

| Repository | Key Dependencies |
|-----------|-----------------|
| ComfyUI-Manager | None (core) |
| ComfyUI-WanVideoWrapper | accelerate, diffusers |
| ComfyUI-GGUF | (included) |
| ComfyUI-Impact-Pack | ultralytics, piexif, dill, segment-anything |
| rgthree-comfy | (core features) |
| ComfyUI-Custom-Scripts | (optional: aiohttp for webhooks) |
| ComfyUI-KJNodes | PIL, numpy |
| ComfyUI-UltimateSDUpscale | (core math) |
| ComfyUI_essentials | (core) |
| ComfyUI-Detail-Daemon | numpy |
| ComfyUI-Impact-Subpack | (requires Impact-Pack) |

All core dependencies installed in install.sh line 167

---

## Performance Tips

1. **Disable unused nodes**: Unload in Manager if not needed
2. **Load models on demand**: Don't keep all checkpoints in memory
3. **Batch process**: Use batch nodes instead of loops
4. **Monitor VRAM**: `nvidia-smi` while generating
5. **Use FP8 models**: Faster and lower memory than FP16
6. **Tile upscaling**: Don't upscale huge images at once

---

## Troubleshooting Workflow

1. **Node red error** → Check imports/dependencies
2. **Missing node** → Reinstall from Manager or manual clone
3. **Slow performance** → Check VRAM, reduce batch size
4. **Model not loading** → Verify file path and format
5. **Mask/image format mismatch** → Use Image Convert nodes

---

**Last Updated**: 2025-12-23

For detailed node documentation, visit individual repository GitHub pages.
