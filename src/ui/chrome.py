"""Brutalist window chrome renderer with absurd graphics."""

from typing import Optional
from imgui_bundle import imgui

from src.ui.theme import ThemeManager


class ChromeRenderer:
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager

    def render(self, message: Optional[str] = None, image_path: Optional[str] = None) -> None:
        self._render_status_bar(message)

    def _render_status_bar(self, message: Optional[str]) -> None:
        imgui.separator()
        
        cols = 2
        if message:
            cols = 3
        imgui.columns(cols, "##status", False)
        
        if message:
            display_msg = message[:60] + "..." if len(message) > 60 else message
            imgui.text(display_msg)
            imgui.next_column()
        
        imgui.next_column()
        
        imgui.text(f"[{self.theme_manager.get_theme_name()}]")
        
        imgui.columns(1)
