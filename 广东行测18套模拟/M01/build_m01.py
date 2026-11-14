#!/usr/bin/env python3
"""Build M01 after a guarded one-time merge of the five reviewed science slots."""
from pathlib import Path
import subprocess
import sys
import build_m01_core as core
from complete_science import prepare, finish

if __name__ == '__main__':
    here=Path(__file__).resolve().parent
    subprocess.run([sys.executable,str(here/'核验记录/check_science.py')],check=True)
    before=prepare()
    core.main()
    finish(before,core)
