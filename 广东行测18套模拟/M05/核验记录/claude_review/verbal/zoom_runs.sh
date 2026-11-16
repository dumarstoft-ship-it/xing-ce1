#!/bin/bash
# 记录用 zoom.py 生成的高倍局部截图（原卷 → crops/）
cd "$(dirname "$0")"
python3 -I zoom.py zj2025 6 28 610 300 660 q19_zoom_line1-2_left.png 400
python3 -I zoom.py zj2025 6 380 610 552 660 q19_zoom_line1-2_right.png 400
python3 -I zoom.py js2022 7 50 728 330 786 q20_options_ABC_zoom400.png 400
python3 -I zoom.py js2022 8 50 30 330 56 q20_option_D_zoom400.png 400
python3 -I zoom.py zj2025 10 28 428 330 450 q28_zoom_blank400.png 400
