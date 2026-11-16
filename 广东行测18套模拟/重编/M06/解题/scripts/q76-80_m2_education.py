# -*- coding: utf-8 -*-
"""第76—80题（资料第2组，广东“十四五”教育）核算脚本。数据从输入 data.json 的文字材料中按原文摘取并核对。"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', '..', '输入', 'data.json'), encoding='utf-8'))
m2 = [m for m in d['materials'] if m['id'].endswith('-m2')][0]
text = ''.join(b['text'] for b in m2['blocks'] if b['type'] == 'text')


def has(s):
    return s in text


# ---------- 第76、77题：原文定位 ----------
print('[76] 选项关键词是否在材料中出现：')
for k in ['职业教育规模位居全国前列', '港澳', '内地', '深化', '优化调整高校', '专业布点', '坚持财政优先保障教育', '开放协同']:
    print(f'  {k}: {has(k)}')
print('[77] 原文：')
for pat in [r'实现21个地市[^。；]*', r'保障全国近五分之一[^。；]*', r'60%以上[^。；]*', r'地方教育经费总投入[^。；]*']:
    m = re.search(pat, text)
    print('  ', m.group(0) if m else None)
print('  “随迁子女”出现处：', [text[max(0, i.start() - 25): i.end() + 10] for i in re.finditer('随迁子女', text)])
print('  “首位/第一”出现处：', [text[max(0, i.start() - 20): i.end()] for i in re.finditer('首位|第一', text)])

# ---------- 数值 ----------
teachers, teachers_inc = 168.04, 15.85
students, students_inc = 2766.19, 165.56
schools, schools_inc = 36868, 28
grad, ug = 23.55, 275.46
g_grad, g_ug = 52.2, 14.8
fund, g_fund = 6747.4, 25.3
pub_fund, g_pub = 3986.4, 12.7
for v in [teachers, teachers_inc, students, students_inc, grad, ug, fund, pub_fund]:
    assert str(v) in text or ('%g' % v) in text, v

# ---------- 第78题 ----------
print('\n[78] 专任教师增长率')
opts = {'A': 7.8, 'B': 8.6, 'C': 9.4, 'D': 10.4}
r = teachers_inc / (teachers - teachers_inc) * 100
print(f'正确：15.85/(168.04-15.85)=15.85/{teachers - teachers_inc:.2f}={r:.4f}%')
print(f'  错误：15.85/168.04={teachers_inc / teachers * 100:.4f}%')
print(f'  （对照）在校生增速={students_inc / (students - students_inc) * 100:.3f}%，学校增速={schools_inc / (schools - schools_inc) * 100:.4f}%')

# ---------- 第79题 ----------
print('\n[79] 专科及以上在校生占比')
share = (grad + ug) / students * 100
print(f'正确：(23.55+275.46)/2766.19={grad + ug:.2f}/2766.19={share:.4f}%  → 10%—15%')
print(f'  只算本专科：275.46/2766.19={ug / students * 100:.4f}%  → 5%—10%（离10%只差{10 - ug / students * 100:.3f}个百分点）')
print(f'  只算硕博士：23.55/2766.19={grad / students * 100:.4f}%  → 不到5%')
print(f'  10%临界：2766.19×10%={students * 0.1:.3f}；15%临界：{students * 0.15:.3f}')

# ---------- 第80题 ----------
print('\n[80] 逐项')
new_univ = 166 - 154
print(f'A：新增普通高校=166-154={new_univ}所，新增职教本科5所，5/{new_univ}={5 / new_univ:.4f}（<1/2，正确）；'
      f'若误用“新增10所本科院校”作比较对象，5/10=0.5，恰为一半')
print('B：材料为“入选第二轮……高校数比首轮新增3所”，首轮为8-3=5所，说成首轮8所，错误')
inc_fund = fund * g_fund / (100 + g_fund)
print(f'C：增长量=6747.4×25.3%/(1+25.3%)={inc_fund:.2f}亿元 <1500，错误；'
      f'误用6747.4×25.3%={fund * g_fund / 100:.2f}>1500 会误判正确')
print(f'D：教育经费3986.4亿元超过支出的1/5 → 支出<3986.4×5={pub_fund * 5:.1f}亿元<2万亿，错误')

# ---------- 自洽检查 ----------
print('\n[自洽检查]')
print(f'十三五末：学校={schools - schools_inc}，在校生={students - students_inc:.2f}万，专任教师={teachers - teachers_inc:.2f}万')
print(f'十三五末：硕博士={grad / (1 + g_grad / 100):.3f}万（增加{grad - grad / (1 + g_grad / 100):.3f}万），'
      f'本专科={ug / (1 + g_ug / 100):.3f}万（增加{ug - ug / (1 + g_ug / 100):.3f}万）')
print(f'  硕博+本专科增量={grad - grad / (1 + g_grad / 100) + ug - ug / (1 + g_ug / 100):.2f}万 ≤ 在校生总增量165.56万：'
      f'{grad - grad / (1 + g_grad / 100) + ug - ug / (1 + g_ug / 100) <= students_inc}')
print(f'2020年：地方教育经费总投入={fund / (1 + g_fund / 100):.2f}亿元，一般公共预算教育经费={pub_fund / (1 + g_pub / 100):.2f}亿元，'
      f'占比2020={pub_fund / (1 + g_pub / 100) / (fund / (1 + g_fund / 100)) * 100:.2f}% → 2024={pub_fund / fund * 100:.2f}%')
print('普通高校154→166（+12），新增本科10所（含职教本科5所）：本科新增≤高校新增，自洽（部分为专科升格）')
