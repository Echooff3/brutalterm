"""Image fetcher for HuggingFace FLUX.1-dev absurd graphics."""

import os
import threading
import time
from typing import Optional
from pathlib import Path

from huggingface_hub import InferenceClient
from PIL import Image


class ImageFetcher:
    PROMPTS = [
        "brutalist architecture concrete geometric abstract art",
        "glitch art corrupted data visualization chaos",
        "soviet propaganda poster surreal computer terminal",
        "cyberpunk brutalist interface design neon concrete",
        "abstract brutalist typography heavy bold letters",
        "dystopian terminal interface monochrome chaos",
        "retro computer CRT glitch static noise art",
        "industrial machinery pipes valves steam punk",
        "deconstructivist architecture shattered fragments",
        "brutalist monument concrete sky ominous clouds",
    ]

    def __init__(self):
        self.client = InferenceClient(
            model="black-forest-labs/FLUX.1-dev",
            token=os.environ.get("HF_TOKEN")
        )
        self.current_image: Optional[str] = None
        self._cache_dir = Path.home() / ".brutal" / "images"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._fetch_lock = threading.Lock()
        self._fetching = False

    def fetch_async(self) -> None:
        if self._fetching:
            return
        
        thread = threading.Thread(target=self._fetch_sync, daemon=True)
        thread.start()

    def _fetch_sync(self) -> None:
        with self._fetch_lock:
            if self._fetching:
                return
            self._fetching = True
        
        try:
            import random
            prompt = random.choice(self.PROMPTS)
            prompt += ", absurd, chaotic, brutal, raw, unpolished"
            
            print(f"Fetching image with prompt: {prompt[:50]}...")
            
            image = self.client.text_to_image(
                prompt,
                width=512,
                height=512
            )
            
            if isinstance(image, Image.Image):
                timestamp = int(time.time())
                filename = f"chrome_{timestamp}.png"
                filepath = self._cache_dir / filename
                image.save(filepath)
                self.current_image = str(filepath)
                print(f"Image saved: {filepath}")
                
                self._cleanup_old_images()
        
        except Exception as e:
            print(f"Image fetch failed: {e}")
        
        finally:
            self._fetching = False

    def _cleanup_old_images(self, keep: int = 10) -> None:
        try:
            images = sorted(
                self._cache_dir.glob("chrome_*.png"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for old_image in images[keep:]:
                old_image.unlink()
        except Exception:
            pass

    def get_random_cached_image(self) -> Optional[str]:
        try:
            images = list(self._cache_dir.glob("chrome_*.png"))
            if images:
                import random
                return str(random.choice(images))
        except Exception:
            pass
        return None
