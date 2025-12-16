#!/usr/bin/env python3
import sys
print("Starting test...", file=sys.stderr)
print("Python version:", sys.version)
print("Test output working!")

try:
    import PyInstaller
    print(f"PyInstaller found: {PyInstaller.__version__}")
except ImportError as e:
    print(f"PyInstaller NOT found: {e}")

print("Test complete!")
