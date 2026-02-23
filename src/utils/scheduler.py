"""Background task scheduler for periodic operations."""

import threading
import time
from typing import Callable, Dict


class BackgroundScheduler:
    def __init__(self):
        self._tasks: Dict[str, dict] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def schedule(self, name: str, interval_seconds: float, 
                 callback: Callable[[], None]) -> None:
        with self._lock:
            self._tasks[name] = {
                "interval": interval_seconds,
                "callback": callback,
                "last_run": 0.0,
            }

    def start(self) -> None:
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run_loop(self) -> None:
        while self._running:
            current_time = time.time()
            
            with self._lock:
                for name, task in self._tasks.items():
                    if current_time - task["last_run"] >= task["interval"]:
                        try:
                            task["callback"]()
                        except Exception as e:
                            print(f"Task '{name}' error: {e}")
                        task["last_run"] = current_time
            
            time.sleep(1.0)
