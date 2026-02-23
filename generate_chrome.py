#!/usr/bin/env python3
"""Generate window chrome image using FLUX.1-dev via HuggingFace Inference API."""

import os
from pathlib import Path

from huggingface_hub import InferenceClient
from PIL import Image, ImageChops


PROMPT = """Orthographic front view of a 9-slice UI frame template: a single rectangular window chrome divided into a 3x3 grid (top-left, top, top-right / left, center, right / bottom-left, bottom, bottom-right). The center cell is a large solid BRIGHT MAGENTA #FF00FF rectangle (terminal viewport placeholder). The 8 surrounding border cells form the chrome and are clearly separated by thick black dividers. Each chrome border cell uses ONLY these colors: orange, brown, black, white, green. Use low-resolution pixelated patterns: animal prints (zebra/leopard/tiger), snake-skin patterns, leaf patterns, lo-fi tie-dye in earth tones. White background outside the outer window. CRITICAL: DO NOT use any pink or magenta colors in the 8 border cells - pink is ONLY for the center cell. No text, no icons, no window controls, no logos. Flat, crisp edges, no shadows, no gradients. The 3x3 grid lines must be explicit and evenly spaced like a 9-patch sprite sheet. The center cell must be pure #FF00FF magenta; border cells must contain NO pink whatsoever."""


def trim_white(im):
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -10)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def main():
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable not set")
        return 1
    
    output_dir = Path("assets")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "window_chrome.png"
    
    print("Generating window chrome image via HuggingFace API...")
    print(f"Prompt: {PROMPT[:100]}...")
    
    client = InferenceClient(token=hf_token)
    
    try:
        image = client.text_to_image(
            prompt=PROMPT,
            model="black-forest-labs/FLUX.1-dev",
            width=768,
            height=512
        )
        
        if isinstance(image, Image.Image):
            print(f"Generated image size: {image.size}")
            
            trimmed = trim_white(image)
            print(f"Trimmed image size: {trimmed.size}")
            
            trimmed.save(output_path)
            print(f"Chrome image saved to: {output_path}")
            return 0
        else:
            print(f"Unexpected result type: {type(image)}")
            return 1
            
    except Exception as e:
        print(f"Error generating image: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
