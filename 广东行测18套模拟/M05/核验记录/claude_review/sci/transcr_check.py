# Read-only: transcription records for the embedded images of M05 Q66-70 sources.
import json
R = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/转写核验记录.json'
recs = json.load(open(R))
want = {'s32_p17_i00','s32_p17_i01','s32_p17_i02','s32_p17_i03','s32_p17_i04',
        's27_p18_i01','s27_p18_i02','s27_p18_i03','s27_p18_i04','s27_p18_i05',
        's21_p18_i09','s21_p18_i10','s21_p18_i11','s23_p19_i11'}
found = set()
for r in recs:
    aid = r.get('asset_id')
    if aid in want:
        found.add(aid)
        print(json.dumps(r, ensure_ascii=False))
print('not found in 转写核验记录:', sorted(want - found))
# also look at 阅读顺序校正记录 / 重绘核对记录 for these seasons/questions
for fn in ['阅读顺序校正记录.json', '重绘核对记录.json', '校验报告.json']:
    p = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/' + fn
    s = open(p).read()
    hits = [k for k in ['s32-q66','s27-q67','s21-q68','s31-q70','s23-q70','s32_p17','s27_p18','s21_p18','s23_p19','s31_p18'] if k in s]
    print(fn, 'mentions:', hits)
