#!/usr/bin/env python3
"""Queue Sarah prompts to ComfyUI - blonde beach futa character."""

import json
import random
import copy
import requests
import sys
import time

COMFY_URL = "http://127.0.0.1:8188"

# Same base workflow as Rosa but with different LoRA defaults for Sarah
# Key differences: Breast Sag OFF (small perky tits), no breast enhancement
BASE_WORKFLOW = {
    "3": {
        "inputs": {
            "seed": 0,
            "steps": 27,
            "cfg": 5.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["51", 0],
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
            "filename_prefix": "comfy/round2/sarah/sarah",
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
            "lora_2": {"on": False, "lora": "Pony/Breast Sag Slider_alpha1.0_rank4_noxattn_last.safetensors", "strength": 1.5},
            "lora_3": {"on": False, "lora": "Pony/Lifted_fake_breasts_v2-test.safetensors", "strength": 1.58},
            "lora_4": {"on": False, "lora": "Pony/Penis Size_alpha1.0_rank4_noxattn_last.safetensors", "strength": 0.377},
            "lora_5": {"on": False, "lora": "Pony/Breast Size Slider - Illustrious - V2_alpha1.0_rank4_noxattn_last.safetensors", "strength": 1.8},
            "lora_6": {"on": False, "lora": "Pony/Taker_POV_Concept.safetensors", "strength": 1},
            "lora_7": {"on": False, "lora": "Pony/zy_Detailed_Backgrounds_v1.safetensors", "strength": -0.333},
            "lora_8": {"on": False, "lora": "Pony/Pony Realism Slider.safetensors", "strength": 2.0},
            "lora_9": {"on": False, "lora": "Pony/RealSkin_xxXL_v1.safetensors", "strength": 1},
            "lora_10": {"on": False, "lora": "Pony/Testicle size Slider V2_alpha1.0_rank4_noxattn_last.safetensors", "strength": 0.78},
            "lora_11": {"on": False, "lora": "sdxl/Myla/heavy engorged breasts XLTa.safetensors", "strength": 1},
            "lora_12": {"on": False, "lora": "sdxl/Myla/style_myia_xl09.safetensors", "strength": 1},
            "lora_13": {"on": False, "lora": "sdxl/Cock/bulgelust.safetensors", "strength": 0.708},
            "lora_14": {"on": True, "lora": "sdxl/Cock/Huge erect.safetensors", "strength": 0.667},
            "lora_15": {"on": False, "lora": "sdxl/Cock/HugeFlaccid.safetensors", "strength": 1.0},
            "lora_16": {"on": False, "lora": "Pony/Swim_Teacher.safetensors", "strength": 0.625},
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
            "model": ["51", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["21", 0]
        },
        "class_type": "KSampler",
        "_meta": {"title": "KSampler"}
    },
    # PAG (Perturbed Attention Guidance) — rolled in as default 2026-04-11.
    # Validated on Valentina erect, Megan flaccid, Jade erect. CFG 5 partners with PAG.
    # Fallback to CFG 8 (no-PAG): call build_workflow(..., use_pag=False)
    "51": {
        "inputs": {
            "model": ["17", 0],
            "scale": 3.0,
            "adaptive_scale": 0.0,
            "unet_block": "middle",
            "unet_block_id": 0,
            "sigma_start": -1.0,
            "sigma_end": -1.0,
            "rescale": 0.0,
            "rescale_mode": "full"
        },
        "class_type": "PerturbedAttention",
        "_meta": {"title": "Perturbed Attention"}
    }
}

# Sarah cock modes - same as Rosa but no breast sag
# Breast Sag LoRA (lora_2) stays OFF for Sarah (small perky breasts)
COCK_MODES = {
    "erect": {
        "lora_4": {"on": True, "strength": -0.5},     # Penis Size slider - BIGGER for long cock
        "lora_10": {"on": True, "strength": 0.3},     # Testicle size - SMALL for Sarah
        "lora_13": {"on": False},                      # bulgelust OFF
        "lora_14": {"on": True, "strength": 0.667},   # Huge erect ON - same as Rosa keeper
        "lora_15": {"on": False},                      # HugeFlaccid OFF
    },
    "flaccid": {
        "lora_4": {"on": True, "strength": -0.2},     # Penis Size slider - dialed back 15%
        "lora_10": {"on": True, "strength": 0.7},     # Testicle size - dialed back from 1.2
        "lora_13": {"on": False},                      # bulgelust OFF
        "lora_14": {"on": False},                      # Huge erect OFF
        "lora_15": {"on": True, "strength": 0.85},    # HugeFlaccid ON - 15% shorter
    },
    "bulge": {
        "lora_4": {"on": False},
        "lora_10": {"on": False},
        "lora_13": {"on": True, "strength": 0.708},   # bulgelust ON
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


def build_workflow(positive_prompt, negative_prompt, cock_mode="erect", seed=None, seed2=None, fast=False, quality=False, use_pag=True):
    """Build a workflow with the given prompts and cock mode.

    Modes:
      - fast=True: skip upscaler, 27 steps @ 904x1400 (~1min) - for drafts
      - quality=True: no upscaler, 40 steps @ 1024x1584 (~1.5min) - for final keepers (bulge safe)
      - default: 2-pass with upscaler, 27+20 steps (~2.5min) - for erect/flaccid keepers
      - use_pag=False: fallback to CFG 8 without Perturbed Attention (pre-2026-04-11 default)
    """
    workflow = copy.deepcopy(BASE_WORKFLOW)

    if not use_pag:
        # Revert to pre-PAG wiring: CFG 8, model direct from Power Lora, no node 51
        workflow["3"]["inputs"]["cfg"] = 8.0
        workflow["3"]["inputs"]["model"] = ["17", 0]
        workflow["22"]["inputs"]["model"] = ["17", 0]
        del workflow["51"]

    # Set prompts
    workflow["6"]["inputs"]["text"] = positive_prompt
    workflow["7"]["inputs"]["text"] = negative_prompt

    # Set seeds
    workflow["3"]["inputs"]["seed"] = seed or random.randint(1, 2**53)
    workflow["22"]["inputs"]["seed"] = seed2 or random.randint(1, 2**53)

    # Apply cock mode LoRA settings
    mode = COCK_MODES.get(cock_mode, COCK_MODES["erect"])
    for lora_key, settings in mode.items():
        lora = workflow["17"]["inputs"][lora_key]
        lora["on"] = settings["on"]
        if "strength" in settings:
            lora["strength"] = settings["strength"]

    # Quality mode: single pass, bigger res, dpmpp_2m_sde/karras - no upscaler smudging
    if quality:
        workflow["3"]["inputs"]["steps"] = 50
        workflow["3"]["inputs"]["sampler_name"] = "dpmpp_2m_sde"
        workflow["3"]["inputs"]["scheduler"] = "karras"
        workflow["19"]["inputs"]["width"] = 1024
        workflow["19"]["inputs"]["height"] = 1584
        workflow["8"]["inputs"]["samples"] = ["3", 0]
        del workflow["21"]
        del workflow["22"]
    # Fast mode: skip upscaler, decode directly from 1st pass
    elif fast:
        workflow["8"]["inputs"]["samples"] = ["3", 0]  # VAEDecode from 1st KSampler
        # Remove upscale nodes (not needed)
        del workflow["21"]
        del workflow["22"]

    return workflow


def queue_prompt(workflow):
    """Queue a prompt to ComfyUI and return the prompt ID."""
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
        print("Usage: queue_sarah.py <cock_mode> <positive_prompt> [negative_prompt]")
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
