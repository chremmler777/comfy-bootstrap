"""Uses Claude API to plan WAN I2V workflow parameters from an image + user prompt."""
import base64
import json
import os
from pathlib import Path

import anthropic

AVAILABLE_LORAS = [
    "Anal_Sex",
    "Breast_Physics",
    "PenisLora",
    "Braless",
    "BottomTS",
    "K3NK_4llinOne",
]

SYSTEM_PROMPT = """You are an expert at crafting prompts for WAN 2.2 Image-to-Video generation.

Given an image and a user's description of what they want to happen, you will plan the optimal workflow parameters.

WAN I2V prompt tips:
- Describe motion explicitly and cinematically: "camera slowly pushes in", "hair blows in the wind"
- Describe subject actions clearly: "she turns her head left", "raises hand slowly"
- Include environment motion: "leaves rustle", "fabric ripples"
- Avoid static descriptions — WAN needs motion cues to generate good video
- Keep it cinematic and detailed, 2-4 sentences

Resolution guide:
- 640x640: square, default, good for portraits and general use
- 832x480: landscape widescreen
- 480x832: portrait/vertical
- 960x544: wide cinematic

Available content LoRAs (use only when clearly relevant to the scene/request):
- Breast_Physics: adds breast physics/jiggle motion
- Braless: specific braless appearance with physics
- PenisLora: male anatomy
- Anal_Sex: anal sex motion
- K3NK_4llinOne: general intimate/sex motion
- BottomTS: bottom/butt motion

Return ONLY valid JSON with this exact structure:
{
  "positive_prompt": "...",
  "negative_prompt": "...",
  "width": 640,
  "height": 640,
  "length": 81,
  "fps": 24,
  "fast_mode": true,
  "content_loras": [["LoraName", 0.8]]
}

length guide: 49 frames = ~2s, 81 frames = ~3.4s, 121 frames = ~5s (use 81 as default)
fast_mode: true for 4-step (faster, good quality), false for 20-step (slower, higher quality)
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
    # strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
