# Read-only: list image-inventory entries for the source assets of M05 Q66-70.
import json, os
INV = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/图片清单.json'
ROOT = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/'
inv = {o['id']: o for o in json.load(open(INV))}
want = ['s32_p17_i00','s32_p17_i01','s32_p17_i02','s32_p17_i03','s32_p17_i04',
        's27_p18_i01','s27_p18_i02','s27_p18_i03','s27_p18_i04','s27_p18_i05',
        's21_p18_i09','s21_p18_i10','s21_p18_i11','s23_p19_i11']
for a in want:
    o = inv.get(a)
    if o is None:
        p = ROOT + 'assets/' + a + '.png'
        print(f'{a}: NOT in 图片清单.json; file exists={os.path.exists(p)}')
        continue
    print(a, 'Q', o.get('season'), o.get('section'), o.get('question_number'), 'page', o.get('pdf_page'),
          'bbox', o.get('bbox_pt'), 'px', o.get('width_px'), o.get('height_px'))
# also: any inventory entries for the same season/page/question
print('---- entries tied to these questions ----')
for o in inv.values():
    key = (o.get('season'), o.get('question_number'))
    if key in [(32, 66), (27, 67), (21, 68), (31, 70), (23, 70)]:
        print(o['id'], key, o.get('bbox_pt'), o.get('width_px'), o.get('height_px'))
