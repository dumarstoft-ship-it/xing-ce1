#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search the bundled question records; no dependencies or network required."""
import argparse,json
from pathlib import Path

def searchable(r):
 parts=[r['stem'],*[o['text'] for o in r['options']],*[f['transcription'] for f in r['figures']]]
 if r['material']:
  parts.extend(b.get('text',b.get('transcription','')) for b in r['material']['content'])
 return '\n'.join(parts)

def main():
 p=argparse.ArgumentParser(description='检索广东行测2022—2026年整卷题库')
 p.add_argument('--year',type=int);p.add_argument('--paper');p.add_argument('--number',type=int)
 p.add_argument('--section');p.add_argument('--keyword',default='')
 p.add_argument('--answer-status',choices=['known','disputed','missing'])
 p.add_argument('--jsonl',action='store_true');p.add_argument('--limit',type=int,default=0,help='0表示全部')
 args=p.parse_args();n=0
 with (Path(__file__).parent/'all.jsonl').open(encoding='utf-8') as f:
  for line in f:
   r=json.loads(line)
   if args.year is not None and r['year']!=args.year:continue
   if args.paper and r['paper_id']!=args.paper:continue
   if args.number is not None and r['question_number']!=args.number:continue
   if args.section and r['section']!=args.section:continue
   if args.answer_status and r['answer']['status']!=args.answer_status:continue
   if args.keyword.casefold() not in searchable(r).casefold():continue
   if args.jsonl:print(line.rstrip('\n'))
   else:
    images=r['figures']+([b for b in r['material']['content'] if b['type']=='image'] if r['material'] else [])
    print(r['id']+' | '+r['section']+' | '+r['answer']['status']+' | '+r['stem'].replace('\n',' ')[:160])
    if images:print('  图片：'+' '.join(dict.fromkeys(i['path'] for i in images)))
   n+=1
   if args.limit and n>=args.limit:break
if __name__=='__main__':main()
