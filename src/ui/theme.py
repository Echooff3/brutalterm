"""Theme manager for brutalist styling with random mutations."""

import random
from typing import Optional

from imgui_bundle import imgui

from src.utils.font_loader import FontLoader


class ThemeManager:
    BRUTALIST_THEMES = [
        {
            "name": "Concrete",
            "bg": (0.12, 0.12, 0.12, 1.0),
            "fg": (0.9, 0.9, 0.9, 1.0),
            "accent": (0.8, 0.2, 0.1, 1.0),
            "border": (0.3, 0.3, 0.3, 1.0),
        },
        {
            "name": "Industrial",
            "bg": (0.08, 0.08, 0.1, 1.0),
            "fg": (0.95, 0.85, 0.7, 1.0),
            "accent": (0.9, 0.5, 0.1, 1.0),
            "border": (0.4, 0.35, 0.25, 1.0),
        },
        {
            "name": "Neon Brutalism",
            "bg": (0.02, 0.02, 0.05, 1.0),
            "fg": (0.1, 1.0, 0.8, 1.0),
            "accent": (1.0, 0.1, 0.5, 1.0),
            "border": (0.2, 0.8, 0.6, 1.0),
        },
        {
            "name": "Paper",
            "bg": (0.95, 0.95, 0.9, 1.0),
            "fg": (0.1, 0.1, 0.1, 1.0),
            "accent": (0.1, 0.1, 0.8, 1.0),
            "border": (0.2, 0.2, 0.2, 1.0),
        },
        {
            "name": "Soviet",
            "bg": (0.15, 0.08, 0.08, 1.0),
            "fg": (0.9, 0.85, 0.7, 1.0),
            "accent": (0.9, 0.2, 0.2, 1.0),
            "border": (0.4, 0.2, 0.15, 1.0),
        },
        {
            "name": "Brutalist Blue",
            "bg": (0.05, 0.1, 0.2, 1.0),
            "fg": (0.8, 0.9, 1.0, 1.0),
            "accent": (0.3, 0.6, 1.0, 1.0),
            "border": (0.2, 0.3, 0.5, 1.0),
        },
    ]

    FONT_SIZES = [12, 14, 16, 18, 20]

    def __init__(self):
        self.current_theme_idx = 0
        self.font_size = 14
        self._theme_data = self.BRUTALIST_THEMES[0]
        
        self.bg_color = self._theme_data["bg"]
        self.text_color = self._theme_data["fg"]
        self.accent_color = self._theme_data["accent"]
        self.border_color = self._theme_data["border"]
        
        self.font_loader = FontLoader()
        self.current_font: Optional[imgui.ImFont] = None

    def apply_random_theme(self) -> None:
        self.current_theme_idx = random.randint(0, len(self.BRUTALIST_THEMES) - 1)
        self._apply_theme()
        self.randomize_font_size()

    def load_random_font(self) -> None:
        if self.font_loader.has_fonts():
            self.current_font = self.font_loader.load_random_font(self.font_size)

    def _apply_theme(self) -> None:
        self._theme_data = self.BRUTALIST_THEMES[self.current_theme_idx]
        self.bg_color = self._theme_data["bg"]
        self.text_color = self._theme_data["fg"]
        self.accent_color = self._theme_data["accent"]
        self.border_color = self._theme_data["border"]
        
        style = imgui.get_style()
        style.window_rounding = 0.0
        style.frame_rounding = 0.0
        style.scrollbar_rounding = 0.0
        style.grab_rounding = 0.0
        style.window_border_size = 2.0
        style.frame_border_size = 1.0
        
        def vec4(t):
            return imgui.ImVec4(t[0], t[1], t[2], t[3])
        
        style.set_color_(imgui.Col_.text, vec4(self.text_color))
        style.set_color_(imgui.Col_.text_disabled, vec4((0.5, 0.5, 0.5, 1.0)))
        style.set_color_(imgui.Col_.window_bg, vec4(self.bg_color))
        style.set_color_(imgui.Col_.child_bg, vec4(self.bg_color))
        style.set_color_(imgui.Col_.popup_bg, vec4(self.bg_color))
        style.set_color_(imgui.Col_.border, vec4(self.border_color))
        style.set_color_(imgui.Col_.border_shadow, vec4((0.0, 0.0, 0.0, 0.0)))
        style.set_color_(imgui.Col_.frame_bg, vec4((
            self.bg_color[0] * 1.2,
            self.bg_color[1] * 1.2,
            self.bg_color[2] * 1.2,
            1.0
        )))
        style.set_color_(imgui.Col_.frame_bg_hovered, vec4((
            self.bg_color[0] * 1.4,
            self.bg_color[1] * 1.4,
            self.bg_color[2] * 1.4,
            1.0
        )))
        style.set_color_(imgui.Col_.frame_bg_active, vec4(self.accent_color))
        style.set_color_(imgui.Col_.title_bg, vec4(self.border_color))
        style.set_color_(imgui.Col_.title_bg_active, vec4(self.accent_color))
        style.set_color_(imgui.Col_.title_bg_collapsed, vec4(self.bg_color))
        style.set_color_(imgui.Col_.button, vec4(self.border_color))
        style.set_color_(imgui.Col_.button_hovered, vec4(self.accent_color))
        style.set_color_(imgui.Col_.button_active, vec4((
            self.accent_color[0] * 0.8,
            self.accent_color[1] * 0.8,
            self.accent_color[2] * 0.8,
            1.0
        )))
        style.set_color_(imgui.Col_.scrollbar_bg, vec4(self.bg_color))
        style.set_color_(imgui.Col_.scrollbar_grab, vec4(self.border_color))
        style.set_color_(imgui.Col_.scrollbar_grab_hovered, vec4(self.accent_color))
        style.set_color_(imgui.Col_.scrollbar_grab_active, vec4(self.accent_color))
        style.set_color_(imgui.Col_.tab, vec4(self.border_color))
        style.set_color_(imgui.Col_.tab_hovered, vec4(self.accent_color))
        style.set_color_(imgui.Col_.tab_selected, vec4(self.accent_color))

    def randomize_font_size(self) -> None:
        self.font_size = random.choice(self.FONT_SIZES)

    def cycle_theme(self) -> None:
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.BRUTALIST_THEMES)
        self._apply_theme()

    def get_theme_name(self) -> str:
        return self._theme_data["name"]

    def mutate_randomly(self) -> None:
        if random.random() < 0.3:
            self.apply_random_theme()

    def get_fonts_dir(self):
        return self.font_loader.get_fonts_dir()
