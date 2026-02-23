"""Core application class for BrutalTerm."""

import os
import sys
import platform
import threading
import time
from typing import Optional, List, Callable

from imgui_bundle import imgui, immapp, hello_imgui
from imgui_bundle import immvision
from PIL import Image
import numpy as np
import cv2

from src.terminal.pty_manager import PtyManager
from src.terminal.terminal_tab import TerminalTab
from src.ui.chrome import ChromeRenderer
from src.ui.theme import ThemeManager
from src.ui.effects import StartupEffects
from src.huggingface.image_fetcher import ImageFetcher
from src.huggingface.message_fetcher import MessageFetcher
from src.utils.scheduler import BackgroundScheduler


class BrutalTermApp:
    def __init__(self):
        self.window_width = 1200
        self.window_height = 800
        
        self.terminal_tabs: List[TerminalTab] = []
        self.active_tab_idx: int = 0
        
        self.pty_manager = PtyManager()
        self.theme_manager = ThemeManager()
        self.chrome_renderer: Optional[ChromeRenderer] = None
        self.startup_effects: Optional[StartupEffects] = None
        
        self.image_fetcher: Optional[ImageFetcher] = None
        self.message_fetcher: Optional[MessageFetcher] = None
        self.scheduler: Optional[BackgroundScheduler] = None
        
        self.show_startup_effect = True
        self.running = False
        self._hf_enabled = False
        self._chrome_texture_id = None
        self._chrome_image_size = None
        self._chrome_image_array = None
        self._chrome_center_rect = None
        
        self._validate_hf_token()

    def _validate_hf_token(self) -> None:
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            print("WARNING: HF_TOKEN environment variable not set.")
            print("HuggingFace features disabled. Set HF_TOKEN to enable.")
            self._hf_enabled = False
        else:
            print(f"HF_TOKEN found (length: {len(hf_token)})")
            self._hf_enabled = True

    def _init_components(self) -> None:
        self.theme_manager.apply_random_theme()
        
        self.chrome_renderer = ChromeRenderer(self.theme_manager)
        self.startup_effects = StartupEffects()
        
        self._load_chrome_background()
        
        if self._hf_enabled:
            self.image_fetcher = ImageFetcher()
            self.message_fetcher = MessageFetcher()
            
            self.scheduler = BackgroundScheduler()
            self.scheduler.schedule("image_fetch", 3600, self._fetch_image)
            self.scheduler.schedule("message_fetch", 1800, self._fetch_message)
            self.scheduler.start()
        
        self._create_initial_tab()

    def _load_chrome_background(self) -> None:
        immvision.use_rgb_color_order()
        
        chrome_path = os.path.join(os.path.dirname(__file__), "..", "assets", "window_chrome.png")
        chrome_path = os.path.abspath(chrome_path)
        
        if os.path.exists(chrome_path):
            try:
                img = Image.open(chrome_path).convert("RGB")
                arr = np.array(img)
                
                # Chroma key out pink/magenta using HSV
                arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                hsv = cv2.cvtColor(arr_bgr, cv2.COLOR_BGR2HSV)
                
                # Pink/magenta hue range in HSV (140-170 in OpenCV's 0-180 range)
                lower_pink = np.array([130, 50, 100])
                upper_pink = np.array([180, 255, 255])
                
                pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
                arr[pink_mask > 0] = [0, 0, 0]
                
                self._chrome_image_array = arr
                self._chrome_image_size = img.size
                self._detect_chrome_center(img)
                print(f"Loaded chrome background: {chrome_path} ({self._chrome_image_size})")
                if self._chrome_center_rect:
                    print(f"Detected center region: {self._chrome_center_rect}")
            except Exception as e:
                print(f"Failed to load chrome background: {e}")
        else:
            print(f"Chrome background not found: {chrome_path}")

    def _detect_chrome_center(self, img: Image.Image) -> None:
        arr = np.array(img)
        h, w = arr.shape[:2]
        
        arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(arr_bgr, cv2.COLOR_BGR2HSV)
        
        lower_magenta = np.array([140, 100, 100])
        upper_magenta = np.array([170, 255, 255])
        
        mask = cv2.inRange(hsv, lower_magenta, upper_magenta)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        img_area = h * w
        best_rect = None
        best_area = 0
        
        for cnt in contours:
            x, y, rw, rh = cv2.boundingRect(cnt)
            area = rw * rh
            if area > best_area and area > img_area * 0.05:
                best_area = area
                best_rect = (x, y, rw, rh)
        
        if best_rect:
            x, y, rw, rh = best_rect
            padding = 5
            x = max(0, x - padding)
            y = max(0, y - padding)
            rw = min(w - x, rw + 2 * padding)
            rh = min(h - y, rh + 2 * padding)
            
            self._chrome_center_rect = (x / w, y / h, rw / w, rh / h)
        else:
            self._chrome_center_rect = (0.1, 0.1, 0.8, 0.8)

    def _create_initial_tab(self) -> None:
        tab = TerminalTab(self.pty_manager, self.theme_manager)
        self.terminal_tabs.append(tab)
        self.active_tab_idx = 0

    def _create_new_tab(self) -> None:
        tab = TerminalTab(self.pty_manager, self.theme_manager)
        self.terminal_tabs.append(tab)
        self.active_tab_idx = len(self.terminal_tabs) - 1

    def _close_tab(self, idx: int) -> None:
        if len(self.terminal_tabs) <= 1:
            return
        if 0 <= idx < len(self.terminal_tabs):
            self.terminal_tabs[idx].close()
            self.terminal_tabs.pop(idx)
            if self.active_tab_idx >= len(self.terminal_tabs):
                self.active_tab_idx = len(self.terminal_tabs) - 1

    def _fetch_image(self) -> None:
        if self.image_fetcher:
            try:
                self.image_fetcher.fetch_async()
            except Exception as e:
                print(f"Image fetch error: {e}")

    def _fetch_message(self) -> None:
        if self.message_fetcher:
            try:
                self.message_fetcher.fetch_async()
            except Exception as e:
                print(f"Message fetch error: {e}")

    def _render_tab_bar(self) -> None:
        for i, tab in enumerate(self.terminal_tabs):
            label = f" {tab.title} ##{i}"
            if i == self.active_tab_idx:
                imgui.push_style_color(imgui.Col_.button, self.theme_manager.accent_color)
            
            if imgui.button(label):
                self.active_tab_idx = i
            
            if i == self.active_tab_idx:
                imgui.pop_style_color()
            
            imgui.same_line()
        
        if imgui.button(" + "):
            self._create_new_tab()
        
        imgui.same_line()
        imgui.text(f"  [{self.theme_manager.get_theme_name()}]")

    def _render_main_area(self) -> None:
        self._render_tab_bar()
        imgui.separator()
        self._render_terminal_area()

    def _render_terminal_area(self) -> None:
        if self.terminal_tabs and 0 <= self.active_tab_idx < len(self.terminal_tabs):
            self.terminal_tabs[self.active_tab_idx].render()

    def _render_chrome(self) -> None:
        if self.chrome_renderer:
            message = None
            image = None
            if self.message_fetcher:
                message = self.message_fetcher.current_message
            if self.image_fetcher:
                image = self.image_fetcher.current_image
            
            self.chrome_renderer.render(message, image)

    def _render_chrome_background(self) -> None:
        if self._chrome_image_array is None:
            return
        
        viewport = imgui.get_main_viewport()
        size = viewport.size
        
        img_size = self._chrome_image_size or (738, 507)
        scale_x = size.x / img_size[0]
        scale_y = size.y / img_size[1]
        scale = max(scale_x, scale_y)
        
        scaled_w = int(img_size[0] * scale)
        scaled_h = int(img_size[1] * scale)
        offset_x = int((size.x - scaled_w) / 2)
        offset_y = int((size.y - scaled_h) / 2)
        
        imgui.set_cursor_pos((offset_x, offset_y))
        
        params = immvision.ImageParams()
        params.image_display_size = scaled_w, scaled_h
        params.show_options_button = False
        params.zoom_key = ""
        
        immvision.image("##chrome_bg", self._chrome_image_array, params)

    def _get_center_screen_rect(self) -> tuple | None:
        if self._chrome_center_rect is None or self._chrome_image_size is None:
            return None
        
        viewport = imgui.get_main_viewport()
        size = viewport.size
        
        img_size = self._chrome_image_size
        scale_x = size.x / img_size[0]
        scale_y = size.y / img_size[1]
        scale = max(scale_x, scale_y)
        
        scaled_w = img_size[0] * scale
        scaled_h = img_size[1] * scale
        offset_x = (size.x - scaled_w) / 2
        offset_y = (size.y - scaled_h) / 2
        
        rx, ry, rw, rh = self._chrome_center_rect
        
        screen_x = offset_x + rx * scaled_w
        screen_y = offset_y + ry * scaled_h
        screen_w = rw * scaled_w
        screen_h = rh * scaled_h
        
        return (int(screen_x), int(screen_y), int(screen_w), int(screen_h))

    def _render_startup_effect(self) -> None:
        if self.show_startup_effect and self.startup_effects:
            done = self.startup_effects.render()
            if done or imgui.is_key_pressed(imgui.Key.escape):
                self.show_startup_effect = False

    def _gui_function(self) -> None:
        if self.show_startup_effect:
            self._render_startup_effect()
        else:
            self._render_chrome_background()
            
            center_rect = self._get_center_screen_rect()
            
            if center_rect:
                cx, cy, cw, ch = center_rect
                imgui.set_cursor_pos((cx, cy))
                imgui.push_style_var(imgui.StyleVar_.window_padding, (4, 4))
                imgui.begin_child("##terminal_container", (cw, ch), False, 
                                  imgui.WindowFlags_.no_scroll_with_mouse)
                self._render_terminal_area()
                imgui.end_child()
                imgui.pop_style_var()
            else:
                self._render_tab_bar()
                imgui.separator()
                
                available = imgui.get_content_region_avail()
                chrome_height = 30.0
                terminal_height = available.y - chrome_height
                if terminal_height < 100:
                    terminal_height = 100
                
                imgui.begin_child("##terminal_container", (0, terminal_height), False, 0)
                self._render_terminal_area()
                imgui.end_child()
            
            self._render_chrome()
        
        for tab in self.terminal_tabs:
            tab.update()

    def _setup_docking_layout(self, runner_params) -> None:
        pass

    def _post_init(self) -> None:
        self._init_components()

    def _cleanup(self) -> None:
        if self.scheduler:
            self.scheduler.stop()
        
        for tab in self.terminal_tabs:
            tab.close()
        
        self.pty_manager.cleanup()

    def run(self) -> None:
        runner_params = immapp.RunnerParams()
        
        runner_params.callbacks.post_init = self._post_init
        runner_params.callbacks.show_gui = self._gui_function
        runner_params.callbacks.before_exit = self._cleanup
        
        runner_params.app_window_params.window_title = "BrutalTerm"
        runner_params.app_window_params.window_geometry.size = (self.window_width, self.window_height)
        runner_params.app_window_params.restore_previous_geometry = False
        
        runner_params.imgui_window_params.default_imgui_window_type = \
            hello_imgui.DefaultImGuiWindowType.provide_full_screen_window
        runner_params.imgui_window_params.show_menu_bar = False
        runner_params.imgui_window_params.show_status_bar = False
        
        runner_params.fps_idling.enable_idling = False
        
        self._setup_docking_layout(runner_params)
        
        immapp.run(runner_params)
