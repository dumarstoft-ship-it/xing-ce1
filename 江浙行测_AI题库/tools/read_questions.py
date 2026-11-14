"""Example: python3 tools/read_questions.py --province 江苏 --year 2024 --section 数量关系"""
from pathlib import Path
import json,argparse
parser=argparse.ArgumentParser()
parser.add_argument('--province',choices=['江苏','浙江'])
parser.add_argument('--year',type=int)
parser.add_argument('--section',choices=['数量关系','言语理解与表达','判断推理'])
parser.add_argument('--with-answers',action='store_true',help='Explicitly join the separately stored answers.')
parser.add_argument('--complete-only',action='store_true',help='Skip source-missing or source-omitted questions.')
args=parser.parse_args();root=Path(__file__).resolve().parents[1]
answers={}
if args.with_answers:
 answers={a['question_id']:a for a in map(json.loads,(root/'answers.jsonl').read_text().splitlines())}
for q in map(json.loads,(root/'questions.jsonl').read_text().splitlines()):
 if any(getattr(args,k) is not None and q[k]!=getattr(args,k) for k in ['province','year','section']):continue
 if args.complete_only and {'source_missing','source_omission'}&set(q['quality_flags']):continue
 if args.with_answers:q['answer_record']=answers[q['question_id']]
 print(json.dumps(q,ensure_ascii=False))
