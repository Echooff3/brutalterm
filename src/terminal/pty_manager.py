"""Cross-platform PTY manager for terminal emulation."""

import os
import sys
import platform
import subprocess
import threading
import select
from typing import Optional, Callable

if platform.system() == "Windows":
    from winpty import PtyProcess
else:
    import pty
    import fcntl
    import termios
    import struct


class PtyManager:
    def __init__(self):
        self.processes: dict = {}
        self._lock = threading.Lock()

    def spawn(self, cols: int = 80, rows: int = 24, 
              on_output: Optional[Callable[[bytes], None]] = None) -> int:
        system = platform.system()
        
        if system == "Windows":
            return self._spawn_windows(cols, rows, on_output)
        else:
            return self._spawn_unix(cols, rows, on_output)

    def _spawn_windows(self, cols: int, rows: int,
                       on_output: Optional[Callable[[bytes], None]]) -> int:
        shell = "pwsh"
        try:
            subprocess.run(["pwsh", "-Command", "exit"], capture_output=True)
        except FileNotFoundError:
            shell = "cmd"
        
        process = PtyProcess.spawn(
            shell,
            dimensions=(rows, cols),
            env=os.environ.copy()
        )
        
        pty_id = id(process)
        self.processes[pty_id] = {
            "process": process,
            "on_output": on_output,
            "alive": True
        }
        
        thread = threading.Thread(
            target=self._read_windows,
            args=(pty_id,),
            daemon=True
        )
        thread.start()
        
        return pty_id

    def _spawn_unix(self, cols: int, rows: int,
                    on_output: Optional[Callable[[bytes], None]]) -> int:
        shell = "/bin/bash"
        if not os.path.exists(shell):
            shell = "/bin/sh"
        
        master_fd, slave_fd = pty.openpty()
        
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
        
        pid = os.fork()
        
        if pid == 0:
            os.close(master_fd)
            os.setsid()
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(slave_fd)
            
            os.execpe(shell, [shell], os.environ.copy())
        else:
            os.close(slave_fd)
            
            pty_id = master_fd
            self.processes[pty_id] = {
                "master_fd": master_fd,
                "pid": pid,
                "on_output": on_output,
                "alive": True
            }
            
            thread = threading.Thread(
                target=self._read_unix,
                args=(pty_id,),
                daemon=True
            )
            thread.start()
            
            return pty_id

    def _read_windows(self, pty_id: int) -> None:
        proc_info = self.processes.get(pty_id)
        if not proc_info:
            return
        
        process = proc_info["process"]
        on_output = proc_info["on_output"]
        
        while proc_info.get("alive", False) and process.isalive():
            try:
                data = process.read(4096)
                if data and on_output:
                    on_output(data.encode("utf-8"))
            except Exception:
                break
        
        proc_info["alive"] = False

    def _read_unix(self, pty_id: int) -> None:
        proc_info = self.processes.get(pty_id)
        if not proc_info:
            return
        
        master_fd = proc_info["master_fd"]
        on_output = proc_info["on_output"]
        
        while proc_info.get("alive", False):
            try:
                r, _, _ = select.select([master_fd], [], [], 0.1)
                if r:
                    data = os.read(master_fd, 4096)
                    if data and on_output:
                        on_output(data)
            except Exception:
                break
        
        proc_info["alive"] = False

    def write(self, pty_id: int, data: bytes) -> None:
        with self._lock:
            proc_info = self.processes.get(pty_id)
            if not proc_info or not proc_info.get("alive"):
                return
            
            system = platform.system()
            
            if system == "Windows":
                process = proc_info["process"]
                try:
                    process.write(data.decode("utf-8", errors="replace"))
                except Exception:
                    pass
            else:
                master_fd = proc_info["master_fd"]
                try:
                    os.write(master_fd, data)
                except Exception:
                    pass

    def resize(self, pty_id: int, cols: int, rows: int) -> None:
        with self._lock:
            proc_info = self.processes.get(pty_id)
            if not proc_info:
                return
            
            system = platform.system()
            
            if system == "Windows":
                process = proc_info["process"]
                try:
                    process.setwinsize(rows, cols)
                except Exception:
                    pass
            else:
                master_fd = proc_info["master_fd"]
                try:
                    winsize = struct.pack("HHHH", rows, cols, 0, 0)
                    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
                except Exception:
                    pass

    def close(self, pty_id: int) -> None:
        with self._lock:
            proc_info = self.processes.get(pty_id)
            if not proc_info:
                return
            
            proc_info["alive"] = False
            
            system = platform.system()
            
            if system == "Windows":
                process = proc_info["process"]
                try:
                    process.terminate()
                except Exception:
                    pass
            else:
                pid = proc_info["pid"]
                try:
                    os.kill(pid, 9)
                except Exception:
                    pass
            
            del self.processes[pty_id]

    def cleanup(self) -> None:
        for pty_id in list(self.processes.keys()):
            self.close(pty_id)
