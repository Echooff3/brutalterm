"""VT100/ANSI escape sequence parser using pyte."""

import pyte
from typing import Optional


class VT100Parser:
    def __init__(self, cols: int = 80, rows: int = 24):
        self.cols = cols
        self.rows = rows
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream(self.screen)

    def feed(self, data: bytes) -> None:
        try:
            text = data.decode("utf-8", errors="replace")
            self.stream.feed(text)
        except Exception:
            pass

    def resize(self, cols: int, rows: int) -> None:
        self.cols = cols
        self.rows = rows
        self.screen.resize(rows, cols)

    def get_display(self) -> str:
        return self.screen.display

    def get_buffer(self) -> list:
        return self.screen.buffer

    def get_cursor_position(self) -> tuple:
        return self.screen.cursor.x, self.screen.cursor.y

    def clear(self) -> None:
        self.screen.erase_in_display(2)
        self.screen.cursor_position()
