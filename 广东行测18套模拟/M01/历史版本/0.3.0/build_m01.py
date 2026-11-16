#!/usr/bin/env python3
"""Rebuild the complete M01 without rerunning the historical science migration."""
from pathlib import Path
import subprocess
import sys
import build_m01_core as core

if __name__ == '__main__':
    here=Path(__file__).resolve().parent
    subprocess.run([sys.executable,str(here/'核验记录/check_science.py')],check=True)
    core.main()
