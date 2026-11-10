"""Merge editor outputs into final first-batch package.
Usage: python3 merge.py <config.json>
config: {"day_order": {...}, "parts": [{"agent": "ZL-A", "final_day": "D02", "module_code": "ZL", "group_order": [...]} ...]}
Writes /home/user/work/build/pkg/ ..."""
import json, os, sys, shutil, re, collections
OUT = '/home/user/work/out'; PKG = '/home/user/work/build/pkg'
def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
def main(cfg):
    os.makedirs(PKG + '/assets', exist_ok=True)
    final, idmap, problems = [], {}, []
    seq = collections.Counter()
    for part in cfg['parts']:
        a = part['agent']; recs = load_jsonl(f'{OUT}/{a}/questions.jsonl')
        keep = [r for r in recs if r.get('day') in part.get('days', [r.get('day')]) and not r.get('exclude')]
        # order by group order then order
        go = part.get('group_order')
        if go: keep.sort(key=lambda r: (go.index(r['group']) if r['group'] in go else 999, r.get('order') or 0))
        for r in keep:
            day = part['day_map'].get(r['day'], r['day'])
            key = (day, part['module_code'])
            seq[key] += 1
            fid = f"{day}-{part['module_code']}-{seq[key]:03d}"
            r2 = dict(r); r2['local_id'] = r['id']; r2['id'] = fid; r2['day'] = day; r2['editor'] = a
            # copy assets
            new_assets = []
            for p in r.get('assets') or []:
                src = p if os.path.isabs(p) else os.path.join(OUT, a, p)
                if not os.path.exists(src):
                    alt = os.path.join(OUT, p)
                    src = alt if os.path.exists(alt) else src
                if not os.path.exists(src): problems.append(f'{fid}: missing asset {p}'); new_assets.append(p); continue
                dst_rel = f"assets/{a}/{os.path.basename(src)}"
                os.makedirs(os.path.dirname(f'{PKG}/{dst_rel}'), exist_ok=True)
                shutil.copy2(src, f'{PKG}/{dst_rel}'); new_assets.append(dst_rel)
            r2['assets'] = new_assets
            idmap[(a, r['id'])] = fid
            final.append(r2)
    return final, idmap, problems
if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1]))
    final, idmap, problems = main(cfg)
    with open(f'{PKG}/questions.jsonl', 'w') as fo:
        for r in final: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(len(final), 'records;', len(problems), 'problems'); print('\n'.join(problems[:30]))
