"""Streaming output utilities for CLI"""
from __future__ import annotations

import sys
import time
from typing import Iterator


def stream_text(text: str, delay: float = 0.01) -> None:
    """Print text with a conversational streaming effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write('\n')
    sys.stdout.flush()


def stream_lines(lines: list[str] | Iterator[str], delay: float = 0.01) -> None:
    """Print multiple lines with streaming effect"""
    for line in lines:
        stream_text(line, delay)


def stream_print(text: str, delay: float = 0.01, newline: bool = True) -> None:
    """Print text with streaming effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        sys.stdout.write('\n')
    sys.stdout.flush()


def print_instant(text: str = "") -> None:
    """Print text instantly without streaming (for structural elements)"""
    print(text)
