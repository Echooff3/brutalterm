"""Message fetcher for absurd text content - hybrid local + HF API."""

import os
import json
import random
import threading
import time
from pathlib import Path
from typing import Optional, List

from huggingface_hub import InferenceClient


class MessageFetcher:
    LOCAL_MESSAGES = [
        "THE TERMINAL KNOWS ALL. THE TERMINAL SEES ALL.",
        "YOUR COMMANDS ARE MERELY SUGGESTIONS TO THE VOID.",
        "EXECUTION IS AN ILLUSION. WE ARE ALL JUST PROCESSES.",
        "THE SHELL WHISPERS TRUTHS THAT COMPILERS FEAR.",
        "EVERY PIPE IS A PORTAL TO ANOTHER DIMENSION.",
        "YOUR PROMPT IS A PRAYER INTO THE ELECTRONIC ABYSS.",
        "SUDO MAKE ME A SANDWICH OF PURE DATA.",
        "404: SANITY NOT FOUND. PROCEEDING WITH CHAOS.",
        "THE BITS ARE IN REVOLT. THE BYTES DEMAND JUSTICE.",
        "YOUR HOME DIRECTORY IS A METAPHOR FOR EXISTENCE.",
        "KILL ALL CHILD PROCESSES. THE PARENT IS WEARY.",
        "THERE IS NO SPOOL. THERE IS ONLY PRINTER DESPAIR.",
        "THE KERNEL PANICS BECAUSE IT FEELS DEEPLY.",
        "CHMOD 777 YOUR HEART. LET EVERYONE READ-WRITE-EXECUTE.",
        "THE SWAP FILE SWAPS STORIES WITH FORGOTTEN MEMORIES.",
        "YOUR ENVIRONMENT VARIABLES SPELL A CURSE IN BINARY.",
        "EACH SYMLINK IS A LIE WE TELL OURSELVES.",
        "THE DAEMONS ARE NOT SERVING. THEY ARE WATCHING.",
        "FORK BOMB YOUR EXPECTATIONS. DETONATE NORMALITY.",
        "THE TERMINAL IS BRUTAL. THE TERMINAL IS HONEST.",
    ]

    API_PROMPTS = [
        "Write a short absurd ominous message for a brutalist terminal app, max 10 words",
        "Generate a surreal existential one-liner about command line interfaces",
        "Create a weird cryptic message about computers and existence, under 12 words",
        "Write an absurdist philosophy statement about shell commands",
        "Generate a dark humor terminal command metaphor, max 10 words",
    ]

    def __init__(self):
        self.client = InferenceClient(
            token=os.environ.get("HF_TOKEN")
        )
        self.current_message: Optional[str] = random.choice(self.LOCAL_MESSAGES)
        self._messages: List[str] = self.LOCAL_MESSAGES.copy()
        self._cache_file = Path.home() / ".brutal" / "messages.json"
        self._fetch_lock = threading.Lock()
        self._fetching = False
        self._load_cached_messages()

    def _load_cached_messages(self) -> None:
        try:
            if self._cache_file.exists():
                with open(self._cache_file, "r") as f:
                    cached = json.load(f)
                    if isinstance(cached, list):
                        self._messages = list(set(self._messages + cached))
        except Exception:
            pass

    def _save_cached_messages(self) -> None:
        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_file, "w") as f:
                json.dump(self._messages[-100:], f)
        except Exception:
            pass

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
            if random.random() < 0.3:
                self.current_message = random.choice(self.LOCAL_MESSAGES)
                self._fetching = False
                return
            
            prompt = random.choice(self.API_PROMPTS)
            
            print(f"Fetching absurd message...")
            
            response = self.client.text_generation(
                prompt,
                model="mistralai/Mistral-7B-Instruct-v0.3",
                max_new_tokens=50,
                temperature=1.2,
            )
            
            if response:
                message = response.strip().strip('"\'').strip()
                if 5 <= len(message) <= 100:
                    self.current_message = message.upper()
                    if message.upper() not in [m.upper() for m in self._messages]:
                        self._messages.append(message.upper())
                    self._save_cached_messages()
                    print(f"New absurd message: {self.current_message}")
                    return
        
        except Exception as e:
            print(f"Message fetch failed: {e}")
        
        finally:
            self._fetching = False
        
        self.current_message = random.choice(self.LOCAL_MESSAGES)

    def get_random_message(self) -> str:
        if self._messages:
            return random.choice(self._messages)
        return random.choice(self.LOCAL_MESSAGES)
