"""Font loader for Nerd Fonts with extended glyph support."""

import random
import urllib.request
import zipfile
import io
import os
from pathlib import Path
from typing import Optional, List

from imgui_bundle import imgui


class FontLoader:
    POPULAR_NERD_FONTS = {
        "JetBrainsMono": "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/JetBrainsMono.zip",
        "FiraCode": "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/FiraCode.zip",
        "Hack": "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/Hack.zip",
        "Meslo": "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/Meslo.zip",
        "CascadiaCode": "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/CascadiaCode.zip",
    }

    def __init__(self):
        self._fonts_dir = Path.home() / ".brutal" / "fonts"
        self._fonts_dir.mkdir(parents=True, exist_ok=True)
        
        self._loaded_fonts: dict = {}
        self._available_fonts: List[Path] = []
        self._current_font: Optional[imgui.ImFont] = None
        self._font_size = 16.0
        
        self._scan_fonts()

    def _scan_fonts(self) -> None:
        self._available_fonts = []
        try:
            for ext in ("*.ttf", "*.otf"):
                self._available_fonts.extend(self._fonts_dir.glob(ext))
            
            self._available_fonts = list(set(self._available_fonts))
            self._available_fonts.sort(key=lambda p: p.name.lower())
        except Exception:
            pass
        
        if self._available_fonts:
            print(f"Found {len(self._available_fonts)} fonts in {self._fonts_dir}")
            for f in self._available_fonts[:5]:
                print(f"  - {f.name}")
            if len(self._available_fonts) > 5:
                print(f"  ... and {len(self._available_fonts) - 5} more")

    def download_nerd_font(self, font_name: str = "JetBrainsMono") -> bool:
        if font_name not in self.POPULAR_NERD_FONTS:
            print(f"Unknown font: {font_name}. Available: {list(self.POPULAR_NERD_FONTS.keys())}")
            return False
        
        url = self.POPULAR_NERD_FONTS[font_name]
        print(f"Downloading {font_name} Nerd Font...")
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'BrutalTerm/1.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                zip_data = response.read()
            
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                for name in zf.namelist():
                    if name.endswith('.ttf') and 'NerdFont' in name:
                        if 'Mono' in name or 'Regular' in name:
                            target_path = self._fonts_dir / os.path.basename(name)
                            if not target_path.exists():
                                with zf.open(name) as src, open(target_path, 'wb') as dst:
                                    dst.write(src.read())
                                print(f"  Extracted: {target_path.name}")
            
            self._scan_fonts()
            return True
        except Exception as e:
            print(f"Failed to download font: {e}")
            return False

    def ensure_default_font(self) -> bool:
        if self.has_fonts():
            return True
        
        print("No fonts found. Downloading JetBrainsMono Nerd Font...")
        return self.download_nerd_font("JetBrainsMono")

    def load_random_font(self, size: float = 16.0) -> Optional[imgui.ImFont]:
        if not self._available_fonts:
            return None
        
        font_path = random.choice(self._available_fonts)
        return self.load_font(font_path, size)

    def load_font(self, font_path: Path, size: float = 16.0) -> Optional[imgui.ImFont]:
        try:
            io = imgui.get_io()
            
            font_config = imgui.ImFontConfig()
            font_config.merge_mode = False
            font_config.pixel_snap_h = True
            
            font = io.fonts.add_font_from_file_ttf(
                str(font_path),
                size,
                font_config
            )
            
            if font:
                self._current_font = font
                self._font_size = size
                self._loaded_fonts[str(font_path)] = font
                print(f"Loaded Nerd Font: {font_path.name} @ {size}px")
                return font
        except Exception as e:
            print(f"Failed to load font {font_path}: {e}")
        
        return None

    def load_all_fonts(self, size: float = 16.0) -> dict:
        loaded = {}
        for font_path in self._available_fonts:
            font = self.load_font(font_path, size)
            if font:
                loaded[font_path.name] = font
        return loaded

    def set_current_font(self, font: Optional[imgui.ImFont]) -> None:
        if font:
            imgui.push_font(font, 0.0)

    def unset_font(self) -> None:
        imgui.pop_font()

    def get_current_font(self) -> Optional[imgui.ImFont]:
        return self._current_font

    def get_font_size(self) -> float:
        return self._font_size

    def set_font_size(self, size: float) -> None:
        self._font_size = size

    def get_available_fonts(self) -> List[str]:
        return [f.name for f in self._available_fonts]

    def has_fonts(self) -> bool:
        return len(self._available_fonts) > 0

    def reload_fonts(self) -> None:
        self._scan_fonts()

    def get_fonts_dir(self) -> Path:
        return self._fonts_dir

    def get_font_by_name(self, name: str) -> Optional[Path]:
        for font_path in self._available_fonts:
            if name.lower() in font_path.name.lower():
                return font_path
        return None

    def load_font_by_name(self, name: str, size: float = 16.0) -> Optional[imgui.ImFont]:
        font_path = self.get_font_by_name(name)
        if font_path:
            return self.load_font(font_path, size)
        return None

    def list_downloadable_fonts(self) -> List[str]:
        return list(self.POPULAR_NERD_FONTS.keys())
