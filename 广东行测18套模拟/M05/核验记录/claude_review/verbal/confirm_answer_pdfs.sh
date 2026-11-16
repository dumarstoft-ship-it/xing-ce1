#!/bin/bash
# 只读：在原解析PDF中核对第21题（江苏2023A类第23题）与第24题（浙江2025A类第42题）的源参考答案
X=/home/user/dumarstoft-ship-it/xingce
echo "== 2023江苏A类解析 第12—13页：原第23题（M05第21题）"
pdftotext -f 12 -l 13 -layout "$X/2023年江苏公务员考试《行测》真题（A类）解析.pdf" - | grep -n -A1 "23\. 法律或司法裁判\|【答案】" | sed -n '1,12p'
echo "== 2025浙江A类解析 第18—19页：原第42题（M05第24题）"
pdftotext -f 18 -l 19 -layout "$X/2025年浙江省公务员录用考试《行测》题（A类）（网友回忆版）解析.pdf" - | grep -n "解耦表征\|正确答案" | sed -n '1,12p'
