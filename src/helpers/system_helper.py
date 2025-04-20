"""
Helper functions for all related to system operations.
"""

import os
import platform
import subprocess


def open_image(image_path: str) -> None:
    """Open an image using the default image viewer of the operating system."""
    system_platform = platform.system()
    try:
        if system_platform == 'Darwin':  # macOS
            subprocess.run(['open', image_path])
        elif system_platform == 'Windows':  # Windows
            os.startfile(image_path)
        else:  # Linux and others
            subprocess.run(['xdg-open', image_path])
    except Exception as e:
        print(f"Failed to open image: {e}")