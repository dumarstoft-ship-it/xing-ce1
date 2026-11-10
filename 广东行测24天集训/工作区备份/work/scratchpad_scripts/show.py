import json,sys
src=json.load(open('/home/user/work/review/source_by_key.json'))
idx=json.load(open('/home/user/work/review/gpt_index.json'))
book=json.load(open('/home/user/work/gpt/gpt_book_parsed.json'))
for qid in sys.argv[1:]:
    k='D01-'+qid
    e=idx[k]; s=src[e['source_key']]
    b=book.get(k,{})
    print('='*100)
    print(k,e)
    print('--GPT stem:',b.get('stem'))
    print('--GPT opts:',b.get('options'))
    print('--SRC stem:',s['stem'])
    print('--SRC opts:',s['options'],' SRC ans:',s['source_answer'])
    print('--SRC analysis:',s['source_analysis'])
    print('--flags:',s.get('extraction_flags'),' crop:',s.get('crop'),s.get('analysis_crop'))
