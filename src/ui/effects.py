"""Fullscreen startup effects like Copilot CLI."""

import random
import time
from imgui_bundle import imgui


class StartupEffects:
    EFFECT_TYPES = ["glitch", "fade", "typewriter"]
    
    def __init__(self):
        self.start_time = time.time()
        self.duration = 2.5
        self.current_effect = random.choice(self.EFFECT_TYPES)
        self._target_text = "BRUTALTERM"
        self._char_idx = 0
        self._last_char_time = 0.0

    def render(self) -> bool:
        elapsed = time.time() - self.start_time
        
        if elapsed >= self.duration:
            return True
        
        viewport = imgui.get_main_viewport()
        size = viewport.size
        
        imgui.set_next_window_pos((0, 0))
        imgui.set_next_window_size((size.x, size.y))
        
        window_flags = (
            imgui.WindowFlags_.no_title_bar |
            imgui.WindowFlags_.no_collapse |
            imgui.WindowFlags_.no_resize |
            imgui.WindowFlags_.no_move |
            imgui.WindowFlags_.no_inputs
        )
        
        imgui.push_style_color(imgui.Col_.window_bg, imgui.ImVec4(0.0, 0.0, 0.0, 1.0))
        imgui.begin("##startup", None, window_flags)
        
        if self.current_effect == "glitch":
            self._render_glitch(elapsed, size)
        elif self.current_effect == "fade":
            self._render_fade(elapsed, size)
        elif self.current_effect == "typewriter":
            self._render_typewriter(elapsed, size)
        
        imgui.end()
        imgui.pop_style_color()
        
        return False

    def _render_glitch(self, elapsed: float, size) -> None:
        progress = min(1.0, elapsed / self.duration)
        
        cx = size.x / 2
        cy = size.y / 2
        
        imgui.set_cursor_pos((cx - 80, cy - 20))
        
        if progress < 0.8:
            offset = random.randint(-3, 3) if random.random() > 0.7 else 0
            imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(1.0, 0.2, 0.3, 1.0))
            imgui.text("BRUTALTERM")
            imgui.pop_style_color()
        else:
            imgui.text("BRUTALTERM")
        
        if progress > 0.5:
            alpha = (progress - 0.5) * 2
            imgui.set_cursor_pos((cx - 100, cy + 15))
            imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.7, 0.7, 0.7, alpha))
            imgui.text("A TERMINAL FOR THE ABSURD")
            imgui.pop_style_color()

    def _render_fade(self, elapsed: float, size) -> None:
        progress = min(1.0, elapsed / self.duration)
        
        cx = size.x / 2
        cy = size.y / 2
        
        alpha = min(1.0, progress * 2)
        
        imgui.set_cursor_pos((cx - 80, cy - 10))
        imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(1.0, 1.0, 1.0, alpha))
        imgui.text("BRUTALTERM")
        imgui.pop_style_color()
        
        if progress > 0.6:
            sub_alpha = (progress - 0.6) / 0.4
            imgui.set_cursor_pos((cx - 100, cy + 15))
            imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.7, 0.7, 0.7, sub_alpha))
            imgui.text("A TERMINAL FOR THE ABSURD")
            imgui.pop_style_color()

    def _render_typewriter(self, elapsed: float, size) -> None:
        progress = min(1.0, elapsed / self.duration)
        
        cx = size.x / 2
        cy = size.y / 2
        
        chars_to_show = int(len(self._target_text) * min(1.0, progress * 1.5))
        text = self._target_text[:chars_to_show]
        
        imgui.set_cursor_pos((cx - 80, cy - 10))
        imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.0, 1.0, 0.5, 1.0))
        imgui.text(text)
        
        if chars_to_show < len(self._target_text):
            if int(elapsed * 4) % 2 == 0:
                imgui.same_line()
                imgui.text("_")
        
        imgui.pop_style_color()
        
        if progress > 0.7:
            sub_alpha = (progress - 0.7) / 0.3
            imgui.set_cursor_pos((cx - 100, cy + 15))
            imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(0.7, 0.7, 0.7, sub_alpha))
            imgui.text("A TERMINAL FOR THE ABSURD")
            imgui.pop_style_color()
