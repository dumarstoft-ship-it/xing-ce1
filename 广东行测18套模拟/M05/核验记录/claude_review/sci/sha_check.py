# Read-only: compare sha256 of figure files with 图片清单.json and M05 图形核验.json.
import hashlib, json
ROOT = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/'
inv = {o['id']: o for o in json.load(open(ROOT + '图片清单.json'))}
g = json.load(open('/home/user/xing-ce1/广东行测18套模拟/M05/核验记录/图形核验.json'))['source_asset_sha256']
for a in ['s32_p17_i01', 's27_p18_i01', 's23_p19_i11']:
    h = hashlib.sha256(open(ROOT + 'assets/' + a + '.png', 'rb').read()).hexdigest()
    print(a, 'file==inventory:', h == inv[a]['sha256'], '| file==M05图形核验:', h == g.get('assets/' + a + '.png'),
          '| visual_check:', inv[a].get('visual_check'))
