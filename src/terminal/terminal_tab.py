"""Terminal tab widget for rendering a single terminal instance."""

import platform
from typing import Optional

from imgui_bundle import imgui

from src.terminal.pty_manager import PtyManager
from src.terminal.vt100_parser import VT100Parser
from src.ui.theme import ThemeManager


class TerminalTab:
    def __init__(self, pty_manager: PtyManager, theme_manager: ThemeManager):
        self.pty_manager = pty_manager
        self.theme_manager = theme_manager
        self.title = "Terminal"
        
        self.cols = 80
        self.rows = 24
        
        self.parser = VT100Parser(self.cols, self.rows)
        self.pty_id: Optional[int] = None
        
        self._input_buffer = ""
        self._scroll_to_bottom = True
        
        self._spawn_terminal()

    def _spawn_terminal(self) -> None:
        system = platform.system()
        self.title = "Bash" if system != "Windows" else "PowerShell"
        
        self.pty_id = self.pty_manager.spawn(
            cols=self.cols,
            rows=self.rows,
            on_output=self._on_output
        )

    def _on_output(self, data: bytes) -> None:
        self.parser.feed(data)
        self._scroll_to_bottom = True

    def _send_input(self, text: str) -> None:
        if self.pty_id is not None:
            self.pty_manager.write(self.pty_id, text.encode("utf-8"))

    def update(self) -> None:
        pass

    def render(self) -> None:
        imgui.push_style_color(imgui.Col_.text, self.theme_manager.text_color)
        imgui.push_style_color(imgui.Col_.frame_bg, self.theme_manager.bg_color)
        
        available = imgui.get_content_region_avail()
        input_height = imgui.get_frame_height_with_spacing() + 5
        
        terminal_height = available.y - input_height
        if terminal_height < 50:
            terminal_height = 50
        
        imgui.begin_child("##terminal_content", (0, terminal_height), True,
                          imgui.WindowFlags_.no_scroll_with_mouse)
        
        display = self.parser.get_display()
        for line in display:
            imgui.text_unformatted(line)
        
        if self._scroll_to_bottom:
            imgui.set_scroll_here_y(1.0)
            self._scroll_to_bottom = False
        
        imgui.end_child()
        
        imgui.pop_style_color()
        imgui.pop_style_color()
        
        imgui.push_item_width(-1)
        if imgui.input_text("##input", self._input_buffer, 
                           imgui.InputTextFlags_.enter_returns_true):
            if self._input_buffer:
                self._send_input(self._input_buffer + "\n")
                self._input_buffer = ""
        imgui.pop_item_width()
        
        if imgui.is_item_focused():
            io = imgui.get_io()
            for c in io.input_queue_characters:
                self._send_input(chr(c))

    def close(self) -> None:
        if self.pty_id is not None:
            self.pty_manager.close(self.pty_id)
            self.pty_id = None
