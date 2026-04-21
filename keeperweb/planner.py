"""Uses Claude API to plan WAN I2V workflow parameters from an image + user prompt."""
import base64
import json
import os
from pathlib import Path

import anthropic

AVAILABLE_LORAS = [
    "Anal_Sex",
    "Breast_Physics",
    "Bouncing_Boobs",
    "PenisLora",
    "Braless",
    "BottomTS",
    "K3NK_4llinOne",
    "WalkToward",
]

SYSTEM_PROMPT = """You are an expert at crafting prompts for WAN 2.2 Image-to-Video generation.

Given an image and a user's description of what they want to happen, you will plan the optimal workflow parameters.

WAN I2V prompt rules (follow strictly):
- The IMAGE defines appearance — do NOT describe how the subject looks, only how they MOVE
- Use strong action verbs with pace adverbs: "breathes deeply", "sways gently", "trembles subtly"
- Keep prompts 80-120 words — specific motion descriptions, not appearance
- Be explicit about camera: "static shot", "slow push-in", "slight handheld drift" — or omit camera entirely
- Subtle movements preserve identity: micro-expressions, breathing, understated body language
- Avoid dramatic full-body motion — it causes morphing and identity drift
- Include environmental/secondary motion: hair swaying, fabric rippling, muscles tensing
- Negative prompt is critical: always include morphing, warping, flickering, face deformation prevention

Resolution guide:
- 640x640: square, default, good for portraits and general use
- 832x480: landscape widescreen
- 480x832: portrait/vertical
- 960x544: wide cinematic

Available content LoRAs (use only when clearly relevant to the scene/request):
- Breast_Physics: breast physics/jiggle motion — use for any female with visible breasts
- Bouncing_Boobs: stronger bouncing motion — pair with Breast_Physics for active scenes; trigger: "her breasts are bouncing"
- Braless: braless appearance with physics — use when clothing suggests no bra
- PenisLora: male anatomy — use when penis is visible or relevant
- Anal_Sex: anal sex motion — only for explicit anal scenes
- K3NK_4llinOne: general intimate/sex motion — for sex scenes without a more specific LoRA
- BottomTS: butt/bottom motion — use when ass is featured
- WalkToward: POV walking approach — trigger: "From a first-person perspective, they walk forward toward the camera, and reach out hands to hug it."

Return ONLY valid JSON with this exact structure:
{
  "positive_prompt": "...",
  "negative_prompt": "...",
  "width": 640,
  "height": 640,
  "length": 81,
  "fps": 24,
  "mode": "fast",
  "content_loras": [["LoraName", 0.8]]
}

length guide: 49 frames = ~2s, 81 frames = ~3.4s, 121 frames = ~5s, 161 frames = ~6.7s (use 81 as default)
mode: "fast" for LightX2V 6-step (default), "q8" for 8-step quality, "q20" for 20-step quality
content_loras: list of [name, strength] pairs, empty array if none needed
negative_prompt: default to standard WAN negative unless user specifies otherwise"""


def plan_workflow(image_path: str | Path, user_prompt: str) -> dict:
    """
    Analyze image + user prompt and return workflow parameters dict.
    """
    image_path = Path(image_path)

    # encode image
    suffix = image_path.suffix.lower()
    media_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    media_type = media_map.get(suffix, "image/jpeg")
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_data},
                    },
                    {
                        "type": "text",
                        "text": f"User wants: {user_prompt}\n\nPlan the WAN I2V workflow for this image and request. Return only the JSON.",
                    },
                ],
            }
        ],
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    params = json.loads(text.strip())
    # normalise: ensure both fast_mode and mode are present
    if "mode" not in params:
        params["mode"] = "fast" if params.get("fast_mode", True) else "q20"
    if "fast_mode" not in params:
        params["fast_mode"] = params["mode"] == "fast"
    return params
