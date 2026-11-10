import json, sys
a, b = int(sys.argv[1]), int(sys.argv[2])
rows = [json.loads(l) for l in open('/home/user/work/out4/ZL4A/questions.jsonl')]
for r in rows[a - 1:b]:
    v = 'V←' + r['variant_of'] if r['variant_of'] else r['claim_key']
    print(f"【{r['id']}】{v} | {r['group']} #{r['order']} | {r['material_or_article']} | {r['intensity']}/{r['difficulty']}/{r['precision_need']} | ans={r['checked_answer']} src={r['source_answer']} | flags={r['flags']} | assets={r['assets']}")
    print('  题:', r['stem'])
    print('  选:', ' | '.join(f"{k}.{x}" for k, x in r['options'].items()))
    print('  解:', r['brief_solution'])
    print('  值:', r['selection_value'])
    print('  标:', r['topic'], r['skill_tags'])
    if '--n' in sys.argv: print('  注:', r['notes'])
