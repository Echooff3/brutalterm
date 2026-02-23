#!/usr/bin/env python3
"""BrutalTerm - A brutalist terminal emulator with absurd AI-generated chrome."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import BrutalTermApp


def main():
    app = BrutalTermApp()
    app.run()


if __name__ == "__main__":
    main()
