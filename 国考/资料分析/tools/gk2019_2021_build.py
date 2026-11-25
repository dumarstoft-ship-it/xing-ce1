"""国考地市级卷2019—2021年资料分析题库的生成程序：GK2019-DS、GK2020-DS、GK2021-DS。

    python3 国考/资料分析/tools/gk2019_2021_build.py [GK2019-DS ...]   # 不写卷名则三卷都生成

只写本程序负责的文件：国考/资料分析/GK20{19,20,21}-DS.jsonl、.md、assets/<卷>/（PNG与manifest.json）。
题池 广东行测18套模拟/重编/题池/GK2019-2021.json 由 check_GK2019-2021.py --write-pool 生成（评定在那里）。
2015、2023年两卷由 gk2015_2023_build.py 生成：它导入本模块，往下面各张登记表里加两卷的登记，再调用 build()。

- 文字取自题本PDF文字层（按字符拼接；PDF里没有空格字符），材料按首行缩进分段，设问里的①②③④另起一行；
- 表格、统计图：页面按288 DPI渲染，从PDF图片对象的外框出发，把框内的页面文字涂白后收紧到有墨迹处，
  四周留1.5pt（6像素）白边，白边不碰页面文字和相邻图片；2019年第114、124题的选项字母在图片里，
  按连通域只取折线；
- 答案：答案PDF文字层解析一遍；人工看答案页拼图（每题题号行与“正确答案”行）再读一遍写在 ANS_VISUAL，
  两遍一致才写入；再由 check_GK2019-2021.py 用转写数据逐题核算。
依赖：pdfplumber、Pillow、numpy、scipy；poppler-utils（pdftoppm、pdftotext）。
"""
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

import numpy as np
import pdfplumber
from PIL import Image
from scipy import ndimage

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / '国考/资料分析'
WORK = Path(tempfile.mkdtemp(prefix='gk2019_2021_'))      # 页面渲染缓存
COMMIT = 'c8c05b25417644d53471de20148eeae93562c68e'       # 整理时的仓库提交（源PDF在此提交与工作区一致）
DPI = 288
S = DPI / 72.0
PAD = 6
INK = 240

QPDF = {
    'GK2019-DS': '国考/真题/2019年国家公务员考试行测真题（地市级）.pdf',
    'GK2020-DS': '国考/真题/2020年国家公务员考试《行测》真题（地市级）.pdf',
    'GK2021-DS': '国考/真题/2021年国家公务员考试《行测》真题（市地级）.pdf',
}

# (图号, 页, 图片对象名, 取第几块折线(None=整张), 说明)
FIGS = {
    'GK2019-DS': [
        ('p12-i01', 12, 'IM67', None),
        ('p12-i02', 12, 'IM68', None),
        ('p13-i01', 13, 'IM71', 0),     # 第114题A
        ('p13-i02', 13, 'IM71', 1),     # 第114题B
        ('p13-i03', 13, 'IM72', 0),     # 第114题C
        ('p13-i04', 13, 'IM72', 1),     # 第114题D
        ('p13-i05', 13, 'IM73', None),
        ('p13-i06', 13, 'IM74', None),
        ('p14-i01', 14, 'IM77', None),
        ('p14-i02', 14, 'IM78', 0),     # 第124题A
        ('p14-i03', 14, 'IM78', 1),     # 第124题B
        ('p14-i04', 14, 'IM79', 0),     # 第124题C
        ('p14-i05', 14, 'IM79', 1),     # 第124题D
    ],
    'GK2020-DS': [
        ('p13-i01', 13, 'IM70', None),
        ('p13-i02', 13, 'IM71', None),
        ('p14-i01', 14, 'IM74', None),
        ('p14-i02', 14, 'IM75', None),
        ('p14-i03', 14, 'IM76', None),
        ('p15-i01', 15, 'IM79', None),  # 第124题题图
    ],
    'GK2021-DS': [
        ('p15-i01', 15, 'IM76', None),
        ('p15-i02', 15, 'IM77', None),  # 第114题A
        ('p15-i03', 15, 'IM78', None),  # B
        ('p15-i04', 15, 'IM79', None),  # C
        ('p15-i05', 15, 'IM80', None),  # D
        ('p15-i06', 15, 'IM81', None),
        ('p16-i01', 16, 'IM84', None),
        ('p17-i01', 17, 'KSPX1', None),
        ('p17-i02', 17, 'IM88', None),
    ],
}


def render(pdf: Path, page: int, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    png = out / f'page-{page:02d}.png'
    if not png.exists():
        subprocess.run(['pdftoppm', '-r', str(DPI), '-png', '-singlefile', '-f', str(page), '-l', str(page),
                        str(pdf), str(png.with_suffix(''))], check=True)
    return png


def crop_all(paper: str, outdir: Path, work: Path):
    pdf = REPO / QPDF[paper]
    work.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    with pdfplumber.open(str(pdf)) as doc:
        for fid, page, name, part in FIGS[paper]:
            pg = doc.pages[page - 1]
            ims = {im['name']: im for im in pg.images}
            im = ims[name]
            full = Image.open(render(pdf, page, work)).convert('RGB')
            W, H = full.size
            gray = np.asarray(full.convert('L')).copy()
            # 页面文字涂白（只用于找墨迹，不改输出像素）
            chars = [(c['x0'], c['top'], c['x1'], c['bottom']) for c in pg.chars]
            for x0, t0, x1, b0 in chars:
                gray[max(0, math.floor(t0 * S) - 1):math.ceil(b0 * S) + 1,
                     max(0, math.floor(x0 * S) - 1):math.ceil(x1 * S) + 1] = 255
            bx = [max(0, math.floor(im['x0'] * S)), max(0, math.floor(im['top'] * S)),
                  min(W, math.ceil(im['x1'] * S)), min(H, math.ceil(im['bottom'] * S))]
            sub = gray[bx[1]:bx[3], bx[0]:bx[2]]
            ink = sub < INK
            if part is not None:
                # 图片内含选项字母：按连通域取较大的折线（按从左到右第part条）
                lab, n = ndimage.label(sub < 200, structure=np.ones((3, 3)))
                objs = ndimage.find_objects(lab)
                lines = []
                for i, sl in enumerate(objs):
                    size = int((lab[sl] == i + 1).sum())
                    if size >= 400 and (sl[1].stop - sl[1].start) > 80:
                        lines.append((sl[1].start, i + 1, sl))
                lines.sort()
                assert len(lines) == 2, (paper, fid, len(lines))
                _, k, sl = lines[part]
                ink = np.zeros_like(ink)
                # 折线及其抗锯齿灰边：在折线外接框内取所有墨迹，但排除别的连通域
                y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
                region = sub[y0:y1, x0:x1] < INK
                other = (lab[y0:y1, x0:x1] != 0) & (lab[y0:y1, x0:x1] != k)
                region &= ~other
                ink[y0:y1, x0:x1] = region
            ys, xs = np.where(ink)
            tight = [bx[0] + xs.min(), bx[1] + ys.min(), bx[0] + xs.max() + 1, bx[1] + ys.max() + 1]
            box = [tight[0] - PAD, tight[1] - PAD, tight[2] + PAD, tight[3] + PAD]
            box = [max(box[0], 0), max(box[1], 0), min(box[2], W), min(box[3], H)]
            # 白边不碰文字、不进相邻图片对象
            obstacles = [(x0 * S, t0 * S, x1 * S, b0 * S) for x0, t0, x1, b0 in chars]
            for other_im in pg.images:
                if other_im['name'] == name:
                    continue
                o = (other_im['x0'] * S, other_im['top'] * S, other_im['x1'] * S, other_im['bottom'] * S)
                # 只管有墨迹的相邻图片（空白水印图不算）
                oa = np.asarray(full.convert('L'))[int(o[1]):int(o[3]), int(o[0]):int(o[2])]
                if oa.size and (oa < INK).any():
                    obstacles.append(o)
            if part is not None:
                # 同一图片对象里的另一条折线和字母也不能进白边
                lab_boxes = []
                for i, sl in enumerate(objs):
                    if i + 1 == k:
                        continue
                    lab_boxes.append((bx[0] + sl[1].start, bx[1] + sl[0].start, bx[0] + sl[1].stop, bx[1] + sl[0].stop))
                obstacles += lab_boxes
            for cx0, cy0, cx1, cy1 in obstacles:
                if cx1 <= box[0] or cx0 >= box[2] or cy1 <= box[1] or cy0 >= box[3]:
                    continue
                if cy1 <= tight[1]:
                    box[1] = max(box[1], math.ceil(cy1))
                elif cy0 >= tight[3]:
                    box[3] = min(box[3], math.floor(cy0))
                elif cx1 <= tight[0]:
                    box[0] = max(box[0], math.ceil(cx1))
                elif cx0 >= tight[2]:
                    box[2] = min(box[2], math.floor(cx0))
                else:
                    raise SystemExit(f'{paper} {fid}: 墨迹框与文字/图片相交 {cx0, cy0, cx1, cy1}')
            box = [int(v) for v in box]
            out = full.crop(box)
            iid = f'{paper}-{fid}'
            path = outdir / f'{iid}.png'
            out.save(path, optimize=True)
            raw = path.read_bytes()
            manifest.append({
                'id': iid,
                'path': f'assets/{paper}/{iid}.png',
                'paper_id': paper,
                'source_page': page,
                'source_bbox_points': [round(v / S, 2) for v in box],
                'method': 'pdf_render_crop',
                'width': out.size[0],
                'height': out.size[1],
                'sha256': hashlib.sha256(raw).hexdigest(),
            })
            print(iid, box, out.size)
    return manifest



APDF = {
    'GK2019-DS': '国考/答案解析/2019年国家公务员考试行测真题（地市级）答案及解析...pdf',
    'GK2020-DS': '国考/答案解析/2020年国家公务员考试《行测》真题（地市级）答案及解析...pdf',
    'GK2021-DS': '国考/答案解析/2021年国家公务员考试《行测》真题（市地级）参考答案及解析...pdf',
}
APAGES = {'GK2019-DS': (29, 35), 'GK2020-DS': (22, 28), 'GK2021-DS': (29, 35)}
YEAR = {'GK2019-DS': 2019, 'GK2020-DS': 2020, 'GK2021-DS': 2021}
TITLE = {'GK2019-DS': '2019年国考行测（地市级）资料分析',
         'GK2020-DS': '2020年国考行测（地市级）资料分析',
         'GK2021-DS': '2021年国考行测（市地级）资料分析'}
QPAGES = {'GK2019-DS': [12, 13, 14, 15], 'GK2020-DS': [13, 14, 15], 'GK2021-DS': [14, 15, 16, 17, 18]}
# 资料分析部分从这一行之后开始（第一组材料的组号/材料标记行）
START = {'GK2019-DS': (12, 409.0), 'GK2020-DS': (13, 210.0), 'GK2021-DS': (15, 28.0)}

# 第二遍：看答案页拼图（每题“正确答案”一行连同题号）逐题读出的字母
ANS_VISUAL = {
    'GK2019-DS': 'BCCDB' 'BDAAC' 'BCDBA' 'CBCAD',
    'GK2020-DS': 'DAADB' 'BCCDA' 'DABCC' 'ADCBB',
    'GK2021-DS': 'BCABD' 'AACBD' 'ACBAD' 'DACCB',
}

# ---------------------------------------------------------------- 材料结构
# ('text', 页, top下限, top上限)：区间内的正文行，首行缩进处分段；
#   跨页的一段写作 ('text', [(页, top下限, top上限), ...])，各区间的行依次相接
# ('caption', 页, top)：图下一行图名（正文文字）
# ('img', 图号)
MATERIALS = {
    'GK2019-DS': [
        ('M1', range(111, 116), [12], [('img', 'p12-i01'), ('img', 'p12-i02')]),
        ('M2', range(116, 121), [13], [('text', 13, 248, 273), ('img', 'p13-i05'), ('img', 'p13-i06')]),
        ('M3', range(121, 126), [14], [('img', 'p14-i01')]),
        ('M4', range(126, 131), [14], [('text', 14, 618, 793)]),
    ],
    'GK2020-DS': [
        ('M1', range(111, 116), [13], [('img', 'p13-i01'), ('caption', 13, 378.4), ('img', 'p13-i02'), ('caption', 13, 559.1)]),
        ('M2', range(116, 121), [14], [('img', 'p14-i01'), ('img', 'p14-i02')]),
        ('M3', range(121, 126), [14], [('img', 'p14-i03')]),
        ('M4', range(126, 131), [15], [('text', 15, 217, 419)]),
    ],
    'GK2021-DS': [
        ('M1', range(111, 116), [15], [('img', 'p15-i01')]),
        ('M2', range(116, 121), [15, 16], [('text', 15, 540, 551), ('img', 'p15-i06'), ('text', 16, 28, 39),
                                           ('img', 'p16-i01'), ('text', 16, 429, 441)]),
        ('M3', range(121, 126), [16, 17], [('text', 16, 714, 742), ('img', 'p17-i01'), ('img', 'p17-i02'),
                                           ('text', 17, 559, 585)]),
        ('M4', range(126, 131), [18], [('text', 18, 77, 273)]),
    ],
}

# 选项为图：题号 → [A、B、C、D 的图号]；题图（role=question）：题号 → 图号
OPTION_FIGS = {
    'GK2019-DS': {114: ['p13-i01', 'p13-i02', 'p13-i03', 'p13-i04'],
                  124: ['p14-i02', 'p14-i03', 'p14-i04', 'p14-i05']},
    'GK2020-DS': {},
    'GK2021-DS': {114: ['p15-i02', 'p15-i03', 'p15-i04', 'p15-i05']},
}
QUESTION_FIGS = {'GK2019-DS': {}, 'GK2020-DS': {124: 'p15-i01'}, 'GK2021-DS': {}}


def table(header, rows):
    s = '| ' + ' | '.join(header) + ' |\n| ' + ' | '.join('---' for _ in header) + ' |\n'
    return s + '\n'.join('| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows)


M19 = ['2017年3月', '2017年4月', '2017年5月', '2017年6月', '2017年7月', '2017年8月', '2017年9月',
       '2017年10月', '2017年11月', '2017年12月', '2018年1月', '2018年2月']

# 图号 → (alt, transcription)
FIG_TEXT = {
    'GK2019-DS': {
        'p12-i01': ('材料1图1：2017年3月～2018年2月全国进口药品数量及同比增速（柱形图与折线图）',
                    '图1　2017年3月～2018年2月全国进口药品数量及同比增速\n\n' + table(
                        ['月份', '数量（万吨）', '同比增速（%）'],
                        zip(M19, ['1.3', '1.1', '1.2', '1.1', '1.1', '1.2', '1.1', '1.0', '1.4', '1.3', '1.3', '0.8'],
                            ['14.6', '19.8', '32.8', '5.6', '1.0', '13.3', '8.2', '7.0', '21.5', '-3.0', '26.0', '-17.0']))
                    + '\n\n柱为数量（左轴，万吨，0—5），折线为同比增速（右轴，%，-75—50）；图名在图片内、印在图下方。'),
        'p12-i02': ('材料1图2：2017年3月～2018年2月全国进口药品金额及同比增速（柱形图与折线图）',
                    '图2　2017年3月～2018年2月全国进口药品金额及同比增速\n\n' + table(
                        ['月份', '金额（亿美元）', '同比增速（%）'],
                        zip(M19, ['24.9', '18.8', '27.8', '26.5', '19.6', '23.8', '21.9', '18.4', '24.0', '27.8', '22.2', '15.6'],
                            ['24.2', '12.2', '54.5', '32.1', '-4.6', '29.5', '3.5', '10.5', '11.9', '24.1', '16.3', '1.7']))
                    + '\n\n柱为金额（左轴，亿美元，0—100），折线为同比增速（右轴，%，-60—60）；图名在图片内、印在图下方。'),
        'p13-i01': ('第114题选项A：两段折线，先陡降、再缓降，末点最低', ''),
        'p13-i02': ('第114题选项B：两段折线，先缓降至低点、再陡升，末点最高', ''),
        'p13-i03': ('第114题选项C：两段折线，先缓升至高点、再陡降，末点最低', ''),
        'p13-i04': ('第114题选项D：两段折线，先陡升至高点、再缓降，末点低于中间点、高于起点', ''),
        'p13-i05': ('材料2图1：2011～2017年全国二手车交易量及同比增速（柱形图与折线图）',
                    '图1　2011～2017年全国二手车交易量及同比增速\n\n' + table(
                        ['年份', '交易量（万辆）', '同比增速（%）'],
                        zip(['2011年', '2012年', '2013年', '2014年', '2015年', '2016年', '2017年'],
                            ['682', '794', '847', '920', '942', '1039', '1240'],
                            ['12.4', '16.4', '6.7', '8.6', '2.4', '10.3', '19.3']))
                    + '\n\n柱为交易量（左轴，万辆，0—2000），折线为同比增速（右轴，%，-20—20）；图名在图片内、印在图下方。'),
        'p13-i06': ('材料2图2：2013～2017年全国二手车平均交易价格（柱形图）',
                    '图2　2013～2017年全国二手车平均交易价格\n\n' + table(
                        ['年份', '平均交易价格（万元/辆）'],
                        zip(['2013年', '2014年', '2015年', '2016年', '2017年'], ['5.6', '6.1', '5.9', '5.8', '6.5']))
                    + '\n\n纵轴单位为万元/辆（5.0—7.0，纵轴不从0起）；图名在图片内、印在图下方。'),
        'p14-i01': ('材料3表：2017年1月～2018年4月全国钓鱼网站处理情况',
                    '2017年1月～2018年4月全国钓鱼网站处理情况\n\n' + table(
                        ['时间', '处理数量（个）：CN域名', '处理数量（个）：非CN域名', '处理数量占比（%）：支付交易类', '处理数量占比（%）：金融证券类'],
                        [['2017年1月', 42, 1870, '64.9', '34.4'], ['2017年2月', 91, 860, '52.6', '45.8'],
                         ['2017年3月', 76, 2019, '80.5', '18.9'], ['2017年4月', 32, 761, '49.4', '50.3'],
                         ['2017年5月', 43, 785, '60.4', '39.6'], ['2017年6月', 19, 810, '66.0', '33.3'],
                         ['2017年7月', 33, 1445, '53.0', '46.8'], ['2017年8月', 58, 4675, '87.3', '12.4'],
                         ['2017年9月', 52, 2572, '83.2', '15.9'], ['2017年10月', 87, 2246, '78.2', '21.2'],
                         ['2017年11月', 40, 2626, '83.6', '13.5'], ['2017年12月', 302, 2693, '79.8', '19.1'],
                         ['2018年1月', 204, 2598, '79.3', '20.2'], ['2018年2月', 58, 641, '46.6', '51.9'],
                         ['2018年3月', 254, 3230, '77.4', '22.3'], ['2018年4月', 229, 1749, '73.2', '25.8']])
                    + '\n\n原表表头为两层：“处理数量（个）”下分“CN域名”“非CN域名”，“处理数量占比（%）”下分“支付交易类”“金融证券类”。'),
        'p14-i02': ('第124题选项A：两段折线，先缓降、再陡升，末点最高', ''),
        'p14-i03': ('第124题选项B：两段折线，先陡降至低点、再上升，末点低于起点', ''),
        'p14-i04': ('第124题选项C：两段折线，先陡升至高点、再缓降，末点高于起点', ''),
        'p14-i05': ('第124题选项D：两段折线，先缓升、再较陡下降，末点最低', ''),
    },
    'GK2020-DS': {
        'p13-i01': ('材料1图1：2010-2018年我国海洋主题公园年末数量及全年游客规模（柱形图与折线图）',
                    '图1　2010-2018年我国海洋主题公园年末数量及全年游客规模\n\n' + table(
                        ['年份', '数量（家）', '游客规模（万人次）'],
                        zip(['2010年', '2011年', '2012年', '2013年', '2014年', '2015年', '2016年', '2017年', '2018年'],
                            ['34', '38', '40', '41', '48', '51', '59', '63', '72'],
                            ['3100', '3650', '3950', '4355', '5288', '5804', '6277', '6845', '8109']))
                    + '\n\n图名为图下的一行正文（见材料文字），不在图片内；柱为数量（左轴，家，0—120），折线为游客规模（右轴，万人次，0—10000）。'),
        'p13-i02': ('材料1图2：2010-2018年我国海洋主题公园收入构成（堆积柱形图）',
                    '图2　2010-2018年我国海洋主题公园收入构成\n\n' + table(
                        ['年份', '门票收入（亿元）', '非门票收入（亿元）'],
                        zip(['2010年', '2011年', '2012年', '2013年', '2014年', '2015年', '2016年', '2017年', '2018年'],
                            ['22.30', '25.20', '26.68', '27.64', '32.89', '35.86', '38.02', '42.09', '50.6'],
                            ['8.2', '9.46', '10.32', '10.86', '13.05', '14.58', '15.61', '17.45', '21.18']))
                    + '\n\n图名为图下的一行正文（见材料文字），不在图片内；堆积柱：下段（白色）为门票收入，上段（灰色）为非门票收入；纵轴单位亿元（0—80）。'
                      '部分数字标签被柱边线压住一部分（如32.89、35.86、38.02的首位），按柱高核对无误。'),
        'p14-i01': ('材料2表：2013~2018年中国集成电路进出口状况',
                    '2013~2018年中国集成电路进出口状况\n\n' + table(
                        ['年份', '进口：数量（亿块）', '进口：金额（亿美元）', '出口：数量（亿块）', '出口：金额（亿美元）'],
                        [['2013年', '2663.1', '2313.4', '1426.7', '877.0'], ['2014年', '2856.5', '2176.2', '1535.2', '608.6'],
                         ['2015年', '3140.0', '2300.0', '1827.7', '693.2'], ['2016年', '3425.5', '2270.7', '1810.1', '613.8'],
                         ['2017年', '3770.1', '2601.4', '2043.5', '668.8'], ['2018年', '4175.7', '3120.6', '2171.0', '846.4']])
                    + '\n\n原表表头为两层：“进口”“出口”下各分“数量（亿块）”“金额（亿美元）”。'),
        'p14-i02': ('材料2图：2013~2018年中国集成电路产业销售额及增速（柱形图与折线图）',
                    '2013~2018年中国集成电路产业销售额及增速\n\n' + table(
                        ['年份', '销售额（亿元人民币）', '增速（%）'],
                        zip(['2013年', '2014年', '2015年', '2016年', '2017年', '2018年'],
                            ['2508.5', '3015.4', '3609.8', '4335.5', '5411.3', '6532.0'],
                            ['16.2', '20.2', '19.7', '20.1', '24.8', '20.7']))
                    + '\n\n柱为销售额（左轴，亿元人民币，0—10000），折线为增速（右轴，%，0—30）；图名在图片内、印在图下方。'),
        'p14-i03': ('材料3表：2013~2018年中国在线旅游收入状况',
                    '2013~2018年中国在线旅游收入状况\n\n' + table(
                        ['年份', '旅游业总收入（万亿元）', '在线旅游收入（亿元）：交通预订', '在线旅游收入（亿元）：住宿预订', '在线旅游收入（亿元）：度假旅游预订'],
                        [['2013年', '2.95', '1519.67', '412.10', '244.20'], ['2014年', '3.38', '2271.57', '547.45', '347.58'],
                         ['2015年', '4.13', '3325.15', '862.57', '549.97'], ['2016年', '4.69', '5385.42', '1251.42', '757.40'],
                         ['2017年', '5.40', '6389.65', '1586.19', '947.47'], ['2018年', '5.97', '6820.95', '1881.49', '1051.81']])
                    + '\n\n原表表头为两层：“在线旅游收入（亿元）”下分“交通预订”“住宿预订”“度假旅游预订”；旅游业总收入单位为万亿元。'),
        'p15-i01': ('第124题题图：5个点的折线示意图（无坐标轴、无数值），首点低，第2点陡升到高位，第3点略高于第2点，'
                    '第4点略降，末点陡降到与首点相近的低位', ''),
    },
    'GK2021-DS': {
        'p15-i01': ('材料1表：2013～2019年我国LED产业不同领域产值规模（单位：亿元）',
                    '2013～2019年我国LED产业不同领域产值规模（单位：亿元）\n\n' + table(
                        ['年份', '2013', '2014', '2015', '2016', '2017', '2018', '2019'],
                        [['总产值', 2576, 3507, 4245, 5216, 6538, 7374, 7548],
                         ['其中：封装', 403, 517, 615, 748, 963, 1054, 959],
                         ['外延芯片', 105, 138, 151, 182, 232, 240, 201],
                         ['应用市场', 2068, 2852, 3479, 4286, 5343, 6080, 6388],
                         ['其中：汽车照明', 27, 30, 45, 60, 75, 90, 97],
                         ['通用照明', 696, 1145, 1551, 2040, 2551, 2679, 2707],
                         ['景观照明', 435, 475, 478, 579, 799, 1007, 1108],
                         ['显示屏', 240, 307, 425, 549, 727, 947, 1089],
                         ['背光应用', 340, 435, 475, 519, 513, 505, 503],
                         ['信号及指示', 87, 89, 90, 90, 91, 92, 84],
                         ['其他', 243, 371, 415, 449, 587, 760, 800]])
                    + '\n\n原表缩进排：“封装”“外延芯片”“应用市场”为总产值的分项（首项前印“其中：”）；'
                      '“汽车照明”至“其他”七项为应用市场的分项（首项前印“其中：”）。“单位：亿元”印在表右上方。'),
        'p15-i02': ('第114题选项A：4个点的折线，一路上升且越升越陡', ''),
        'p15-i03': ('第114题选项B：4个点的折线，前三点缓升（第3点最高），末点陡降到最低', ''),
        'p15-i04': ('第114题选项C：4个点的折线，前三点陡升（第3点最高），末点略降', ''),
        'p15-i05': ('第114题选项D：4个点的折线，第2点略升，第3点陡降，末点再略降', ''),
        'p15-i06': ('材料2图：2013—2019年全国地铁运营线路长度（柱形图）',
                    '2013—2019年全国地铁运营线路长度\n\n' + table(
                        ['年份', '地铁运营线路长度（公里）'],
                        zip(['2013年', '2014年', '2015年', '2016年', '2017年', '2018年', '2019年'],
                            ['2073', '2361', '2658', '3169', '3884', '4354', '5181']))
                    + '\n\n纵轴单位为公里（0—6000）；图名在图片内、印在图下方。'),
        'p16-i01': ('材料2表：2019年我国部分城市地铁运营状况',
                    '2019年我国部分城市地铁运营状况\n\n' + table(
                        ['城市', '运营线路长度（公里）', '运营线路条数（条）', '配属地铁列车（列）', '客运量（亿人次）'],
                        [['上海', '669.5', 15, 898, '38.7'], ['北京', '637.6', 20, 1001, '39.4'],
                         ['广州', '489.4', 13, 510, '32.9'], ['武汉', '338.4', 9, 435, '12.4'],
                         ['深圳', '304.4', 8, 384, '17.8'], ['成都', '302.2', 7, 410, '14.0'],
                         ['重庆', '230.0', 7, 223, '6.1'], ['天津', '178.6', 5, 178, '4.7'],
                         ['南京', '176.8', 5, 203, '10.4'], ['苏州', '165.9', 4, 173, '3.6'],
                         ['西安', '158.0', 5, 203, '9.5'], ['郑州', '151.7', 4, 151, '4.1'],
                         ['杭州', '130.9', 4, 174, '6.3']])
                    + '\n\n表下的“注：除客运量为全年数值外，其余指标为年末时点值。”是正文文字，见材料。'),
        'p17-i01': ('材料3图1：2014—2019年各年末全国残疾人康复机构数量（柱形图）',
                    '图1　2014—2019年各年末全国残疾人康复机构数量\n\n' + table(
                        ['年份', '残疾人康复机构数量（个）'],
                        zip(['2014年', '2015年', '2016年', '2017年', '2018年', '2019年'],
                            ['6914', '7111', '7858', '8334', '9036', '9775']))
                    + '\n\n纵轴单位为个（0—10000）；图名在图片内、印在图下方。'),
        'p17-i02': ('材料3图2：2019年末提供不同类型服务的残疾人康复机构数量（条形图）',
                    '图2　2019年末提供不同类型服务的残疾人康复机构数量\n\n' + table(
                        ['服务类型', '机构数量（个）'],
                        [['辅助器具服务', 1970], ['视力残疾康复服务', 1430], ['听力言语残疾康复服务', 1669],
                         ['精神残疾康复服务', 2022], ['孤独症儿童康复服务', 2238], ['智力残疾康复服务', 3529],
                         ['肢体残疾康复服务', 4312]])
                    + '\n\n横向条形图，自上而下按上表顺序；横轴单位为个（0—5000）；图名在图片内、印在图下方。'),
    },
}

# 材料说明（每题 notes 都带）、题目说明
MAT_NOTES = {
    'GK2019-DS': {
        'M1': ['原卷本组组号印作“（一）”（四组依次为“（一）”至“（四）”，与M1—M4对应），组号未收入材料。',
               '材料1没有文字，只有两张统计图（图名“图1”“图2”在图片内、印在各图下方），已逐项转写。'],
        'M2': ['原卷本组组号印作“（二）”，组号未收入材料。'],
        'M3': ['原卷本组组号印作“（三）”，组号未收入材料。'],
        'M4': ['原卷本组组号印作“（四）”，组号未收入材料。'],
    },
    'GK2020-DS': {
        'M1': ['原卷资料分析四组材料的组号依次印作“（二）”“（三）”“（四）”“（五）”（与判断推理第106—110题的材料组号“（一）”连排），本库按次序记为M1—M4。',
               '两张统计图的图名“图1……”“图2……”是图下的一行正文（不在图片内），已作为文字放在各图之后。'],
        'M2': ['原卷本组组号印作“（三）”（资料分析各组组号从“（二）”起，见M1说明）。'],
        'M3': ['原卷本组组号印作“（四）”（资料分析各组组号从“（二）”起，见M1说明）。'],
        'M4': ['原卷本组组号印作“（五）”（资料分析各组组号从“（二）”起，见M1说明）。'],
    },
    'GK2021-DS': {
        'M1': ['原卷本组组号印作“(材料1)”（半角括号；四组依次为“(材料1)”至“(材料4)”，与M1—M4对应），组号未收入材料。'],
        'M2': ['原卷本组组号印作“(材料2)”，组号未收入材料。'],
        'M3': ['原卷本组组号印作“(材料3)”，组号未收入材料。'],
        'M4': ['原卷本组组号印作“(材料4)”，组号未收入材料。'],
    },
}
# md 开头写明原卷资料组号怎么印
MD_INTRO = {
    'GK2019-DS': ['原卷资料分析四组材料的组号印作“（一）”至“（四）”，与本库 M1—M4 依次对应。'],
    'GK2020-DS': ['原卷资料分析四组材料的组号印作“（二）”至“（五）”（与判断推理第106—110题的“（一）”连排），本库按次序记为 M1—M4。'],
    'GK2021-DS': ['原卷资料分析四组材料的组号印作“(材料1)”至“(材料4)”，与本库 M1—M4 依次对应。'],
}
Q_NOTES = {
    'GK2019-DS': {
        114: ['四个选项为折线示意图（无坐标轴、无数值）；原卷A、B两项印在一张图片里，C、D两项印在另一张图片里，选项字母“A.”“B.”“C.”“D.”也在图片内，已按选项分别裁出折线（不含字母）。'],
        124: ['四个选项为折线示意图（无坐标轴、无数值）；原卷A、B两项印在一张图片里，C、D两项印在另一张图片里，选项字母“A.”“B.”“C.”“D.”也在图片内，已按选项分别裁出折线（不含字母）。'],
    },
    'GK2020-DS': {
        116: ['四个选项把集成电路进出口贸易额占进出口贸易总额的比重写作“超过10个百分点”“在5～10个百分点之间”等，照录。'],
        124: ['题图为一条5个点的折线示意图（无坐标轴、无数值），选项为文字。'],
    },
    'GK2021-DS': {
        114: ['四个选项各为一张折线示意图（无坐标轴、无数值），选项字母“A、”“B、”“C、”“D、”为正文文字、印在各图左下方，裁图不含字母。'],
    },
}


# ---------------------------------------------------------------- 读文字层
def load_lines(paper):
    pdf = REPO / QPDF[paper]
    lines = []
    with pdfplumber.open(str(pdf)) as doc:
        for p in QPAGES[paper]:
            for ln in doc.pages[p - 1].extract_text_lines(return_chars=True, strip=False):
                t = ''.join(c['text'] for c in ln['chars'])
                lines.append({'page': p, 'x0': ln['x0'], 'top': ln['top'], 'text': t,
                              'size': max(c['size'] for c in ln['chars'])})
    sp, st = START[paper]
    lines = [l for l in lines if (l['page'], l['top']) >= (sp, st - 0.5)]
    return lines


RE_SKIP = re.compile(r'^(-\d+-|（[一二三四五六]）|\(材料\d\)|第五部分资料分析)$')
# 组号行连同“根据以下资料，回答116-120题。”（2015年卷），不收入材料
RE_GROUP_HEAD = re.compile(r'^(?:（[一二三四五六]）)?根据以下资料，回答\d+[—\-～~－]\d+题。$')


def paragraphs(lines):
    paras = []
    for l in lines:
        if not paras or l['x0'] > 55:
            paras.append(l['text'])
        else:
            paras[-1] += l['text']
    return paras


def split_options(t):
    """“A、2B、19C、8D、96” → {A:2, B:19, ...}；从行首的选项字母起，按字母顺序依次找“字母+、/．”。"""
    out, pos, labels = {}, 0, []
    m0 = re.match(r'^([A-D])[、．]', t)
    if not m0:
        return out, None, labels
    for L in 'ABCD'['ABCD'.index(m0.group(1)):]:
        m = re.compile(L + '[、．]').search(t, pos)
        if m:
            labels.append((L, m.start(), m.end()))
            pos = m.end()
    for i, (L, s, e) in enumerate(labels):
        end = labels[i + 1][1] if i + 1 < len(labels) else len(t)
        out[L] = t[e:end]
    return out, (labels[0][0] if labels else None), labels


def parse(paper):
    lines = load_lines(paper)
    used = set()
    mats = {}
    for mid, qn, pages, content in MATERIALS[paper]:
        blocks = []
        for c in content:
            if c[0] == 'img':
                blocks.append(('img', c[1]))
            elif c[0] == 'caption':
                hit = [i for i, l in enumerate(lines) if l['page'] == c[1] and abs(l['top'] - c[2]) < 0.6]
                assert len(hit) == 1, (paper, c)
                used.add(hit[0])
                t = re.sub(r'^(图\d)', r'\1　', lines[hit[0]]['text'])
                blocks.append(('text', t))
            else:
                ranges = c[1] if isinstance(c[1], list) else [c[1:]]
                idx = [i for p, lo, hi in ranges for i, l in enumerate(lines) if l['page'] == p and lo <= l['top'] <= hi]
                assert idx and all(any(lines[i]['page'] == p and lo <= lines[i]['top'] <= hi for i in idx)
                                   for p, lo, hi in ranges), (paper, c)
                used |= set(idx)
                blocks.append(('text', '\n'.join(paragraphs([lines[i] for i in idx]))))
        mats[mid] = {'qnums': list(qn), 'pages': pages, 'blocks': blocks}
    qs = {}
    cur = None
    for i, l in enumerate(lines):
        if i in used:
            continue
        t = l['text']
        if (RE_SKIP.match(t) or RE_GROUP_HEAD.match(t) or l['size'] < 9.5 or t.startswith('五、资料分析')
                or t == '析、比较、计算和判断处理。'):
            continue
        m = re.match(r'^(1[1-3]\d)(?:、(.*))?$', t)      # 2023年卷题号单独一行
        if m:
            cur = int(m.group(1))
            qs[cur] = {'stem': m.group(2) or '', 'options': {}, 'pages': {l['page']}, 'opt_mode': False}
            continue
        assert cur, (paper, t)
        q = qs[cur]
        q['pages'].add(l['page'])
        opts, first, labels = split_options(t)
        if first and labels[0][1] == 0 and (first == 'A' or q['opt_mode']):
            q['opt_mode'] = True
            q['options'].update(opts)
            q['last_opt'] = labels[-1][0]
        elif q['opt_mode']:
            q['options'][q['last_opt']] += t          # 选项折行：接到上一个选项后
        elif re.match(r'^[①②③④⑤⑥]', t):
            q['stem'] += '\n' + t
        else:
            q['stem'] += t
    assert sorted(qs) == list(range(111, 131)), (paper, sorted(qs))
    for n, q in qs.items():
        if n in OPTION_FIGS[paper] and not q['options']:
            q['options'] = {L: '' for L in 'ABCD'}      # 选项字母在图片里，正文没有选项行
        assert sorted(q['options']) == list('ABCD'), (paper, n, q['options'])
        q['stem'] = re.sub(r'[（(]\s*[）)]', '（）', q['stem'])
    return mats, qs


# ---------------------------------------------------------------- 答案
def answers_text_layer(paper):
    pdf = REPO / APDF[paper]
    lo, hi = APAGES[paper]
    res, cur = {}, None
    for p in range(lo, hi + 1):
        out = subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), str(pdf), '-'],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            s = line.strip().replace(' ', '')
            m = re.match(r'^(\d{3})(?:[、.．]|$)', s)      # “111、……”或题号单独一行
            if m and 111 <= int(m.group(1)) <= 130:
                cur = int(m.group(1))
                res.setdefault(cur, [])
            for a in re.finditer(r'正确答案(?:为|：|:)([A-D])', s):
                if cur:
                    res[cur].append((a.group(1), p))
    out = {}
    for n in range(111, 131):
        vals = res.get(n) or []
        letters = {a for a, _ in vals}
        assert len(letters) == 1, (paper, n, vals)
        out[n] = (vals[0][0], sorted({p for _, p in vals}))
    return out


# ---------------------------------------------------------------- 输出
def rel_link(path):
    """从 国考/资料分析/ 指向仓库文件的相对链接。"""
    return '../' + urllib.parse.quote(path.split('国考/', 1)[1])


def build(paper):
    mats, qs = parse(paper)
    ans = answers_text_layer(paper)
    vis = ANS_VISUAL[paper]
    for i, n in enumerate(range(111, 131)):
        assert ans[n][0] == vis[i], (paper, n, ans[n], vis[i])
    adir = OUT / 'assets' / paper
    if adir.exists():
        shutil.rmtree(adir)
    manifest = crop_all(paper, adir, WORK / paper)
    man = {m['id']: m for m in manifest}

    def figure(fid, role, label=None):
        iid = f'{paper}-{fid}'
        alt, tr = FIG_TEXT[paper][fid]
        man[iid]['transcription'] = tr
        return {'type': 'image', 'image_id': iid, 'path': man[iid]['path'], 'role': role,
                'option_label': label, 'method': 'pdf_render_crop', 'alt': alt, 'transcription': tr}

    recs = []
    mat_objs = {}
    for mid, m in mats.items():
        content = []
        for kind, v in m['blocks']:
            if kind == 'text':
                content.append({'type': 'text', 'text': v})
            else:
                content.append(figure(v, 'material'))
        mat_objs[mid] = {'id': f'{paper}-{mid}', 'question_numbers': m['qnums'], 'source_pages': m['pages'],
                         'content': content}
    for mid, m in mats.items():
        for n in m['qnums']:
            q = qs[n]
            figs, options = [], []
            ofig = OPTION_FIGS[paper].get(n)
            if n in QUESTION_FIGS[paper]:
                figs.append(figure(QUESTION_FIGS[paper][n], 'question'))
            for k, L in enumerate('ABCD'):
                if ofig:
                    assert q['options'][L] == '', (paper, n, q['options'])
                    f = figure(ofig[k], 'option', L)
                    figs.append(f)
                    options.append({'label': L, 'text': '', 'image_refs': [{'image_id': f['image_id'], 'label_in_image': None}]})
                else:
                    assert q['options'][L], (paper, n, L)
                    options.append({'label': L, 'text': q['options'][L], 'image_refs': []})
            a, apages = ans[n]
            pages = sorted(q['pages'] | ({man[f['image_id']]['source_page'] for f in figs}))
            recs.append({
                'id': f'{paper}-Q{n:03d}', 'year': YEAR[paper], 'province': '全国', 'exam': '国家公务员录用考试',
                'subject': '行政职业能力测验', 'paper_id': paper, 'paper_variant': '地市级', 'source_edition': '仓库原卷',
                'question_number': n, 'section': '资料分析', 'question_type': 'single_choice', 'stem': q['stem'],
                'options': options, 'figures': figs, 'material': mat_objs[mid],
                'answer': {'status': 'known', 'values': [[a]], 'source_pages': apages, 'note': ''},
                'source': {'question_pdf': QPDF[paper], 'question_pages': pages, 'answer_pdf': APDF[paper],
                           'repository_commit': COMMIT},
                'notes': list(MAT_NOTES[paper].get(mid, [])) + list(Q_NOTES[paper].get(n, [])),
            })
    with open(OUT / f'{paper}.jsonl', 'w', encoding='utf-8') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    for m in manifest:
        m.setdefault('transcription', '')
    (adir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    write_md(paper, recs, mats)
    return recs


def write_md(paper, recs, mats):
    qpdf, apdf = QPDF[paper], APDF[paper]
    qp = sorted({p for r in recs for p in r['source']['question_pages'] + r['material']['source_pages']})
    ap = sorted({p for r in recs for p in r['answer']['source_pages']})
    s = [f'# {TITLE[paper]}', '',
         f'共 20 题（第 111—130 题，原题号保留），4 组材料。内容：材料、题干、选项、答案（不收解析）；'
         '共用材料置于所属题组前，JSONL 每条记录完整内嵌材料。表格、统计图为题本按 288 DPI 渲染后的裁图，图中文字和数字另有转写。', '',
         f'[结构化数据]({paper}.jsonl) · [图片清单](assets/{paper}/manifest.json)', '',
         f'原题来源：[{qpdf.split("/")[-1]}]({rel_link(qpdf)})（第 {qp[0]}—{qp[-1]} 页）。'
         f'答案来源：[{apdf.split("/")[-1]}]({rel_link(apdf)})（第 {ap[0]}—{ap[-1]} 页，只取答案）。', '']
    for t in MD_INTRO.get(paper, []):
        s += [t, '']
    s += ['## 资料分析', '']
    by_mat = {}
    for r in recs:
        by_mat.setdefault(r['material']['id'], []).append(r)
    for mid, rs in by_mat.items():
        m = rs[0]['material']
        qn = m['question_numbers']
        s += [f'<a id="{mid}"></a>', '', f'### 共用材料：第 {qn[0]}—{qn[-1]} 题', '']
        for b in m['content']:
            if b['type'] == 'text':
                s += [b['text'], '']
            else:
                s += [f'![{b["alt"]}]({b["path"]})', '']
                if b['transcription']:
                    s += [b['transcription'], '']
        mn = MAT_NOTES[paper].get(mid.split('-')[-1], [])
        if mn:
            s += ['> 材料说明：' + ''.join(mn), '']
        for r in rs:
            n = r['question_number']
            pages = '、'.join(str(p) for p in r['source']['question_pages'])
            s += [f'<a id="{r["id"]}"></a>', '', f'### 第 {n} 题', '', f'`{r["id"]}` · 单选 · 原卷第 {pages} 页', '',
                  f'[共用材料](#{mid})', '', r['stem'].replace('\n', '  \n'), '']
            for f in r['figures']:
                s += [f'![{f["alt"]}]({f["path"]})', '']
            for o in r['options']:
                if o['text']:
                    s += [f'**{o["label"]}.** {o["text"]}', '']
                else:
                    s += [f'**{o["label"]}.** 见上方选项图 {o["label"]}。', '']
            s += [f'**答案：{"".join(r["answer"]["values"][0])}**', '']
            qn_notes = Q_NOTES[paper].get(n, [])
            if qn_notes:
                s += ['> 转写说明：' + ''.join(qn_notes), '']
    (OUT / f'{paper}.md').write_text('\n'.join(s).rstrip() + '\n', encoding='utf-8')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        for p in (sys.argv[1:] or ['GK2019-DS', 'GK2020-DS', 'GK2021-DS']):
            recs = build(p)
            print(p, len(recs))
    finally:
        shutil.rmtree(WORK, ignore_errors=True)
