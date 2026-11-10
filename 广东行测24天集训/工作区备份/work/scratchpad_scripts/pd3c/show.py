import pool, sys, os, json
def tag_of(pid):
    return pid if os.path.exists(f'/home/user/work/index/{pid}.json') else pid + '_xc'
def show(key):
    pid, q = key.rsplit('-', 1); q = int(q)
    tag = tag_of(pid)
    x = pool.qtext(tag, q)
    a = pool.answers(tag).get(str(q)) or {}
    r = pool.QI.get((pid, q), {})
    print(f"=== {key} [{tag}] taken={pool.taken(key)} ans={a.get('ans')} rate={a.get('rate')} yicuo={a.get('yicuo')} qi_ans={r.get('answer')} imgs={len(x.get('images') or []) if x else None} page={x['segs'][0][0]+1 if x else None}")
    print(x['text'] if x else 'NOT FOUND')
if __name__ == '__main__':
    for k in sys.argv[1:]: show(k)
