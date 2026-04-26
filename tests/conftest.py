"""Shared pytest configuration.

Sets the SDL drivers to dummy *before* anything imports ``pygame`` /
``pygamejr`` so the test process never tries to open a real display
or audio device on a headless CI VM.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
