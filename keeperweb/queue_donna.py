#!/usr/bin/env python3
"""Queue Donna prompts to ComfyUI - Donna Paulsen (Suits) look-alike, redhead power woman."""

import json
import random
import copy
import requests
import sys
import time

COMFY_URL = "http://127.0.0.1:8188"

# Donna's base workflow - sophisticated redhead, slim elegant, corporate power
# Key: Lower breast sag for perkier look, RealSkin for realism
BASE_WORKFLOW = {
    "3": {
        "inputs": {
            "seed": 0,
            "steps": 27,
            "cfg": 8.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["17", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["19", 0]
        },
        "class_type": "KSampler",
        "_meta": {"title": "KSampler"}
    },
    "6": {
        "inputs": {
            "text": "",
            "clip": ["17", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "CLIP Text Encode (Prompt)"}
    },
    "7": {
        "inputs": {
            "text": "",
            "clip": ["17", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "CLIP Text Encode (Prompt)"}
    },
    "8": {
        "inputs": {
            "samples": ["22", 0],
            "vae": ["14", 2]
        },
        "class_type": "VAEDecode",
        "_meta": {"title": "VAE Decode"}
    },
    "9": {
        "inputs": {
            "filename_prefix": "comfy/donna/donna",
            "images": ["8", 0]
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save Image"}
    },
    "14": {
        "inputs": {
            "ckpt_name": "cyberrealisticPony_v160.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {"title": "Load Checkpoint"}
    },
    "17": {
        "inputs": {
            "PowerLoraLoaderHeaderWidget": {"type": "PowerLoraLoaderHeaderWidget"},
            "lora_1": {"on": True, "lora": "Pony/RealSkin_xxXL_v1.safetensors", "strength": 1},
            "lora_2": {"on": True, "lora": "Pony/Breast Sag Slider_alpha1.0_rank4_noxattn_last.safetensors", "strength": 0.8},
            "lora_3": {"on": False, "lora": "Pony/Lifted_fake_breasts_v2-test.safetensors", "strength": 1.58},
            "lora_4": {"on": True, "lora": "Pony/Penis Size_alpha1.0_rank4_noxattn_last.safetensors", "strength": -0.2},
            "lora_5": {"on": False, "lora": "Pony/Breast Size Slider - Illustrious - V2_alpha1.0_rank4_noxattn_last.safetensors", "strength": 0.758},
            "lora_6": {"on": False, "lora": "Pony/Taker_POV_Concept.safetensors", "strength": 1},
            "lora_7": {"on": False, "lora": "Pony/zy_Detailed_Backgrounds_v1.safetensors", "strength": -0.333},
            "lora_8": {"on": False, "lora": "Pony/Pony Realism Slider.safetensors", "strength": 2.0},
            "lora_9": {"on": False, "lora": "Pony/RealSkin_xxXL_v1.safetensors", "strength": 1},
            "lora_10": {"on": True, "lora": "Pony/Testicle size Slider V2_alpha1.0_rank4_noxattn_last.safetensors", "strength": 0.78},
            "lora_11": {"on": False, "lora": "sdxl/Myla/heavy engorged breasts XLTa.safetensors", "strength": 0.55},
            "lora_12": {"on": False, "lora": "sdxl/Myla/style_myia_xl09.safetensors", "strength": 1},
            "lora_13": {"on": False, "lora": "sdxl/Cock/bulgelust.safetensors", "strength": 0.708},
            "lora_14": {"on": False, "lora": "sdxl/Cock/Huge erect.safetensors", "strength": 0.45},
            "lora_15": {"on": True, "lora": "sdxl/Cock/HugeFlaccid.safetensors", "strength": 0.9},
            "lora_16": {"on": False, "lora": "Pony/Swim_Teacher.safetensors", "strength": 1.583},
            "lora_17": {"on": False, "lora": "Pony/CrotchlessSwimsuitV1PONY.safetensors", "strength": 1.0},
            "lora_18": {"on": False, "lora": "Pony/Futa_on_Futa_POV_Pony.safetensors", "strength": 1},
            "lora_19": {"on": True, "lora": "Pony/amateur_style_v1_pony.safetensors", "strength": 1.5},
            "\u2795 Add Lora": "",
            "model": ["14", 0],
            "clip": ["14", 1]
        },
        "class_type": "Power Lora Loader (rgthree)",
        "_meta": {"title": "Power Lora Loader (rgthree)"}
    },
    "19": {
        "inputs": {
            "width": 904,
            "height": 1400,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage",
        "_meta": {"title": "Empty Latent Image"}
    },
    "23": {
        "inputs": {
            "images": ["8", 0]
        },
        "class_type": "PreviewImage",
        "_meta": {"title": "Preview Image"}
    },
    "21": {
        "inputs": {
            "upscale_method": "bicubic",
            "scale_by": 1.5,
            "samples": ["3", 0]
        },
        "class_type": "LatentUpscaleBy",
        "_meta": {"title": "Upscale Latent By"}
    },
    "22": {
        "inputs": {
            "seed": 0,
            "steps": 20,
            "cfg": 4.0,
            "sampler_name": "dpmpp_2m_sde",
            "scheduler": "karras",
            "denoise": 0.56,
            "model": ["14", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["21", 0]
        },
        "class_type": "KSampler",
        "_meta": {"title": "KSampler"}
    }
}

# Donna cock modes - same as Luna baseline
COCK_MODES = {
    "flaccid": {
        "lora_4": {"on": True, "strength": -0.2},       # Penis Size slider
        "lora_10": {"on": True, "strength": 0.78},       # Testicle size
        "lora_13": {"on": False},                         # bulgelust OFF
        "lora_14": {"on": False},                         # Huge erect OFF
        "lora_15": {"on": True, "strength": 0.9},        # HugeFlaccid ON
    },
    "erect": {
        "lora_4": {"on": True, "strength": -0.3},       # Penis Size slider
        "lora_10": {"on": True, "strength": 0.5},        # Testicle size
        "lora_13": {"on": False},                         # bulgelust OFF
        "lora_14": {"on": True, "strength": 0.45},      # Huge erect ON
        "lora_15": {"on": False},                         # HugeFlaccid OFF
    },
    "bulge": {
        "lora_4": {"on": False},
        "lora_10": {"on": False},
        "lora_13": {"on": True, "strength": 0.708},     # bulgelust ON
        "lora_14": {"on": False},
        "lora_15": {"on": False},
    },
    "none": {
        "lora_4": {"on": False},
        "lora_10": {"on": False},
        "lora_13": {"on": False},
        "lora_14": {"on": False},
        "lora_15": {"on": False},
    },
}


def _add_enhanced_nodes(workflow, upscale=True):
    """Add FaceDetailer + HandDetailer + PenisDetailer (+ optional UltimateSDUpscale) after VAEDecode.

    Pipeline: decoded image -> FaceDetailer -> HandDetailer -> PenisDetailer -> [UltimateSDUpscale 2x]
    Also injects Detail Slider LoRA for extra texture/background detail.

    Args:
        upscale: If True, add UltimateSDUpscale 2x at the end (slow, huge files).
                 If False, skip upscale - just detailer passes + detail LoRA (faster).
    """

    # --- Detectors ---
    workflow["100"] = {
        "inputs": {"model_name": "bbox/face_yolov8m.pt"},
        "class_type": "UltralyticsDetectorProvider",
        "_meta": {"title": "Face Detector"}
    }
    workflow["110"] = {
        "inputs": {"model_name": "bbox/hand_yolov8s.pt"},
        "class_type": "UltralyticsDetectorProvider",
        "_meta": {"title": "Hand Detector"}
    }
    workflow["120"] = {
        "inputs": {"model_name": "segm/CockAndBallYolo8x.pt"},
        "class_type": "UltralyticsDetectorProvider",
        "_meta": {"title": "CockAndBall Detector"}
    }

    # --- Pass 1: FaceDetailer ---
    workflow["101"] = {
        "inputs": {
            "image": ["8", 0],
            "model": ["17", 0],
            "clip": ["17", 1],
            "vae": ["14", 2],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "guide_size": 1024,
            "guide_size_for": True,
            "max_size": 2048,
            "seed": random.randint(1, 2**53),
            "steps": 20,
            "cfg": 5.0,
            "sampler_name": "dpmpp_2m",
            "scheduler": "simple",
            "denoise": 0.4,
            "feather": 5,
            "noise_mask": True,
            "force_inpaint": False,
            "bbox_threshold": 0.5,
            "bbox_dilation": 15,
            "bbox_crop_factor": 3.0,
            "sam_detection_hint": "center-1",
            "sam_dilation": 0,
            "sam_threshold": 0.93,
            "sam_bbox_expansion": 0,
            "sam_mask_hint_threshold": 0.7,
            "sam_mask_hint_use_negative": "False",
            "drop_size": 10,
            "bbox_detector": ["100", 0],
            "wildcard": "",
            "cycle": 1,
        },
        "class_type": "FaceDetailer",
        "_meta": {"title": "FaceDetailer"}
    }

    # --- Pass 2: HandDetailer (same node type, different detector) ---
    workflow["111"] = {
        "inputs": {
            "image": ["101", 0],       # chain from face-detailed image
            "model": ["17", 0],
            "clip": ["17", 1],
            "vae": ["14", 2],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "guide_size": 512,
            "guide_size_for": True,
            "max_size": 1024,
            "seed": random.randint(1, 2**53),
            "steps": 12,
            "cfg": 5.0,
            "sampler_name": "dpmpp_2m",
            "scheduler": "simple",
            "denoise": 0.35,
            "feather": 5,
            "noise_mask": True,
            "force_inpaint": False,
            "bbox_threshold": 0.4,
            "bbox_dilation": 20,
            "bbox_crop_factor": 3.0,
            "sam_detection_hint": "center-1",
            "sam_dilation": 0,
            "sam_threshold": 0.93,
            "sam_bbox_expansion": 0,
            "sam_mask_hint_threshold": 0.7,
            "sam_mask_hint_use_negative": "False",
            "drop_size": 10,
            "bbox_detector": ["110", 0],
            "wildcard": "",
            "cycle": 1,
        },
        "class_type": "FaceDetailer",
        "_meta": {"title": "HandDetailer"}
    }

    # --- Pass 3: CockAndBallDetailer (segmentation model) ---
    workflow["121"] = {
        "inputs": {
            "image": ["111", 0],       # chain from hand-detailed image
            "model": ["17", 0],
            "clip": ["17", 1],
            "vae": ["14", 2],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "guide_size": 768,
            "guide_size_for": True,
            "max_size": 1536,
            "seed": random.randint(1, 2**53),
            "steps": 16,
            "cfg": 5.0,
            "sampler_name": "dpmpp_2m",
            "scheduler": "simple",
            "denoise": 0.3,
            "feather": 5,
            "noise_mask": True,
            "force_inpaint": False,
            "bbox_threshold": 0.35,
            "bbox_dilation": 25,
            "bbox_crop_factor": 3.0,
            "sam_detection_hint": "center-1",
            "sam_dilation": 0,
            "sam_threshold": 0.93,
            "sam_bbox_expansion": 0,
            "sam_mask_hint_threshold": 0.7,
            "sam_mask_hint_use_negative": "False",
            "drop_size": 10,
            "bbox_detector": ["120", 0],
            "wildcard": "",
            "cycle": 1,
        },
        "class_type": "FaceDetailer",
        "_meta": {"title": "PenisDetailer"}
    }

    # --- Inject Detail Slider LoRA for extra texture/bg detail ---
    lora_inputs = workflow["17"]["inputs"]
    next_slot = 20
    while f"lora_{next_slot}" in lora_inputs:
        next_slot += 1
    lora_inputs[f"lora_{next_slot}"] = {
        "on": True,
        "lora": "Pony/Detail_Slider_v1.4.safetensors",
        "strength": 2.5,
    }

    # Final output node depends on whether we upscale
    last_node = "121"  # penis-detailed image

    if upscale:
        # --- Upscale model loader (4x-UltraSharp) ---
        workflow["102"] = {
            "inputs": {"model_name": "4x-UltraSharp.pth"},
            "class_type": "UpscaleModelLoader",
            "_meta": {"title": "Load Upscale Model"}
        }

        # --- UltimateSDUpscale 2x (from penis-detailed image) ---
        workflow["103"] = {
            "inputs": {
                "image": ["121", 0],
                "model": ["17", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "vae": ["14", 2],
                "upscale_by": 2,
                "seed": random.randint(1, 2**53),
                "steps": 4,
                "cfg": 1,
                "sampler_name": "deis",
                "scheduler": "simple",
                "denoise": 0.15,
                "mode_type": "Chess",
                "tile_width": 512,
                "tile_height": 512,
                "mask_blur": 8,
                "tile_padding": 32,
                "seam_fix_mode": "None",
                "seam_fix_denoise": 1,
                "seam_fix_width": 64,
                "seam_fix_mask_blur": 8,
                "seam_fix_padding": 16,
                "force_uniform_tiles": True,
                "tiled_decode": False,
                "batch_size": 1,
                "upscale_model": ["102", 0],
            },
            "class_type": "UltimateSDUpscale",
            "_meta": {"title": "UltimateSDUpscale"}
        }
        last_node = "103"

    # Save/preview from the last node in the chain
    workflow["9"]["inputs"]["images"] = [last_node, 0]
    workflow["23"]["inputs"]["images"] = [last_node, 0]

    return workflow


def build_workflow(positive_prompt, negative_prompt, cock_mode="flaccid", seed=None, seed2=None, fast=False, quality=False, enhanced=False):
    """Build a workflow with the given prompts and cock mode.

    Modes:
        fast: 1-pass only (no upscale)
        quality: 50 steps, higher res, no upscale
        enhanced: normal 2-pass + FaceDetailer + UltimateSDUpscale 2x
        (default): normal 2-pass
    """
    workflow = copy.deepcopy(BASE_WORKFLOW)

    workflow["6"]["inputs"]["text"] = positive_prompt
    workflow["7"]["inputs"]["text"] = negative_prompt

    workflow["3"]["inputs"]["seed"] = seed or random.randint(1, 2**53)
    workflow["22"]["inputs"]["seed"] = seed2 or random.randint(1, 2**53)

    mode = COCK_MODES.get(cock_mode, COCK_MODES["flaccid"])
    for lora_key, settings in mode.items():
        lora = workflow["17"]["inputs"][lora_key]
        lora["on"] = settings["on"]
        if "strength" in settings:
            lora["strength"] = settings["strength"]

    if quality:
        workflow["3"]["inputs"]["steps"] = 50
        workflow["3"]["inputs"]["sampler_name"] = "dpmpp_2m_sde"
        workflow["3"]["inputs"]["scheduler"] = "karras"
        workflow["19"]["inputs"]["width"] = 1024
        workflow["19"]["inputs"]["height"] = 1584
        workflow["8"]["inputs"]["samples"] = ["3", 0]
        del workflow["21"]
        del workflow["22"]
    elif fast:
        workflow["8"]["inputs"]["samples"] = ["3", 0]
        del workflow["21"]
        del workflow["22"]

    if enhanced:
        _add_enhanced_nodes(workflow)

    return workflow


def queue_prompt(workflow):
    payload = {"prompt": workflow}
    resp = requests.post(f"{COMFY_URL}/prompt", json=payload)
    resp.raise_for_status()
    return resp.json().get("prompt_id")


def get_history(prompt_id):
    resp = requests.get(f"{COMFY_URL}/history/{prompt_id}")
    resp.raise_for_status()
    return resp.json()


def wait_for_result(prompt_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        history = get_history(prompt_id)
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            for node_id, output in outputs.items():
                if "images" in output:
                    return output["images"]
            return outputs
        time.sleep(2)
    return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: queue_donna.py <cock_mode> <positive_prompt> [negative_prompt]")
        sys.exit(1)

    cock_mode = sys.argv[1]
    pos = sys.argv[2]
    neg = sys.argv[3] if len(sys.argv) > 3 else "bad quality"

    workflow = build_workflow(pos, neg, cock_mode)
    prompt_id = queue_prompt(workflow)
    print(f"Queued prompt: {prompt_id}")
    print(f"Cock mode: {cock_mode}")
    print(f"Waiting for result...")

    result = wait_for_result(prompt_id)
    if result:
        print(f"Done! Output: {result}")
    else:
        print("Timed out waiting for result")
