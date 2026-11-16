#!/usr/bin/env python3
"""Import exactly the already-delivered M05 draft; no new question editing."""
from __future__ import annotations
import base64, hashlib, json, lzma, os, re, shutil, subprocess, sys
from pathlib import Path

BASE = '8b37121d4f486e364b8f76826cf8de651021f4b2'
PAYLOAD_HASH = 'e8826d281e0016c01c127315d96109faf68ede5f7611112854a3369f21c010ae'
DRIVE = 'https://drive.google.com/drive/folders/1z62g1fZa6MFwPYAXnl9pNeosI8ot7-Qt'
ROOT = Path.cwd().resolve()
PARTS = Path(__file__).resolve().parent
PROJECT = ROOT/'广东行测18套模拟'
TARGET = PROJECT/'M05'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jl(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def safe(path):
    p=Path(path)
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in path, path
    return p


def ids(value):
    if isinstance(value, dict):
        out={value['source_id']} if isinstance(value.get('source_id'),str) else set()
        for v in value.values(): out.update(ids(v))
        return out
    if isinstance(value,list):
        out=set()
        for v in value:
            if isinstance(v,str):out.add(v)
            else:out.update(ids(v))
        return out
    return set()


def main():
    assert (ROOT/'.git').exists(), 'Not a repository checkout'
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert head==BASE, ('Main changed; do not publish without renewed preflight',head)
    assert not TARGET.exists(), 'M05 already exists; refuse overwrite'
    parts=sorted(PARTS.glob('part_*.b64'))
    assert [p.name for p in parts]==[f'part_{i:02d}.b64' for i in range(1,10)]
    packed=base64.b64decode(''.join(p.read_text().strip() for p in parts),validate=True)
    assert hashlib.sha256(packed).hexdigest()==PAYLOAD_HASH, 'Transport checksum mismatch'
    obj=json.loads(lzma.decompress(packed))
    assert obj['format']=='m05-exact-inputs-v1' and obj['source_main']==BASE
    assert len(obj['files'])==22 and len(obj['expected_all_M05_sha256'])==35
    for rel,h in {**obj['source_sha256'],**obj['asset_sha256']}.items():
        p=ROOT/safe(rel)
        assert p.is_file() and digest(p)==h, ('Source/image changed',rel)
    ledger=PROJECT/'用题登记.jsonl'; ledger_before=ledger.read_bytes(); old=jl(ledger)
    assert len(old)==360 and {r['paper_id'] for r in old}=={'M01','M02','M03','M04'}
    chosen={q['source_id'] for q in json.loads(obj['files']['originals.json'])}
    for group in json.loads(obj['files']['choices.json']).values():chosen.update(group)
    assert len(chosen)==90 and not chosen.intersection(r['source_id'] for r in old)
    protected={}; retired=set()
    for name in ['M01','M02','M03','M04']:
        d=PROJECT/name;assert d.is_dir()
        for p in d.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                protected[str(p.relative_to(ROOT))]=digest(p)
                if p.suffix=='.json' and ('撤题' in p.name or 'excluded' in p.name):
                    retired.update(ids(json.loads(p.read_text(encoding='utf-8'))))
    assert not chosen.intersection(retired), 'Overlap with previously retired questions'
    entry_paths=[ROOT/'README.md',PROJECT/'README.md']
    entry_original={str(p):p.read_bytes() for p in entry_paths}
    try:
        TARGET.mkdir()
        for rel,content in obj['files'].items():
            p=TARGET/safe(rel);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(content,encoding='utf-8')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        for name in ['prepare_m05.py','build_m05.py','核验记录/check_math_logic.py','核验记录/check_graphics.py','核验记录/verify_m05.py','build_reader.py']:
            subprocess.run([sys.executable,str(TARGET/name)],check=True,cwd=ROOT,env=env)
        for rel,h in obj['expected_all_M05_sha256'].items():
            p=TARGET/safe(rel)
            assert p.is_file() and digest(p)==h, ('Rebuilt file differs from delivered draft',rel)
        after=jl(ledger)
        assert len(after)==450 and [r for r in after if r['paper_id']!='M05']==old
        assert len([r for r in after if r['paper_id']=='M05'])==90
        assert protected=={p:digest(ROOT/p) for p in protected}, 'Prior paper changed'
        assert all(digest(ROOT/p)==h for p,h in {**obj['source_sha256'],**obj['asset_sha256']}.items())
        # Only delivery-status prose changes after exact 35-file reconstruction.
        readme=TARGET/'README.md';s=readme.read_text(encoding='utf-8')
        a=s.index('本轮生成物保存在本对话资料包；')
        b=s.index('\n\n阅览HTML',a)
        s=s[:a]+'本稿由已交付资料包校验重建后入库，目录为`广东行测18套模拟/M05/`。题本、答案解析、题源与核验记录不作内容修改。另有[Google Drive备份]('+DRIVE+')，包含原始完整资料包及单独阅览文件。发布状态以本次远端提交为准；仍为0.1.0待Claude独立审核稿，不是最终打印稿。'+s[b:]
        readme.write_text(s,encoding='utf-8')
        (TARGET/'发布说明.md').write_text('# M05发布说明\n\n目标为`dumarstoft-ship-it/xing-ce1`的`main`分支。源快照：`'+BASE+'`。\n\n本次仅发布已经交付的0.1.0完整待审稿。传输包校验、源库与12张原图指纹、前四套及撤题排重均通过；六个构建/核验脚本运行后，35个文件与原交付稿逐一SHA-256一致。之后只更新本说明、README及项目入口中的交付位置，不修改题目、答案、解析或审核结论。\n\n前四套目录及原题库不覆盖，用题登记从360条追加为450条。暂存分块和上传工作流不进入main。\n\n[Google Drive完整备份]('+DRIVE+')。云盘资料包保留原始交付快照，其中“未上传”的文字是发布前历史说明；当前发布状态看本目录及远端提交。\n\n当前仍需Claude独立审核；没有最终打印PDF。\n',encoding='utf-8')
        project_readme=PROJECT/'README.md';s=project_readme.read_text(encoding='utf-8')
        row='| M05—M18 | 尚未开始选编 | 根据既有各卷反馈继续 |'
        assert row in s,'Project index changed'
        s=s.replace(row,'| M05 | [0.1.0完整待审稿](M05/README.md)，90题及编辑核验已齐 | [Claude独立审核](M05/交接_Claude.md)，审核后打印 |\n| M06—M18 | 尚未开始选编 | 根据既有各卷反馈继续 |')
        s=s.replace('M01—M04各已登记90题','M01—M05各已登记90题')
        s=s.replace('# 广东行测18套模拟｜协作入口\n','# 广东行测18套模拟｜协作入口\n\n**最新发布（2026-11-16）：[M05 0.1.0](M05/README.md)完整待审稿已入库，90题、90分钟，待Claude独立审核。** [题本](M05/题本_待审.md)｜[答案解析](M05/答案与解析_待审.md)｜[审核交接](M05/交接_Claude.md)\n\n以下各卷既有状态记录保留；不将编辑核验当作外部审核通过。\n',1)
        project_readme.write_text(s,encoding='utf-8')
        root_readme=ROOT/'README.md';s=root_readme.read_text(encoding='utf-8')
        root_readme.write_text('## 最新发布：M05第五套完整待审稿\n\n[第五套入口](广东行测18套模拟/M05/README.md)｜[Claude审核交接](广东行测18套模拟/M05/交接_Claude.md)。90题、90分钟，编辑核验完成，独立审核与正式打印尚未完成。\n\n以下历史进度保留。\n\n'+s,encoding='utf-8')
        record={'status':'PASS','scope':'publication_integrity_not_new_content_review','payload_sha256':PAYLOAD_HASH,'main_parent':BASE,'exact_rebuilt_files':35,'status_only_updates':['README.md','发布说明.md'],'original_package_file_sha256':obj['expected_all_M05_sha256'],'published_file_sha256':{p:digest(TARGET/p) for p in obj['expected_all_M05_sha256']},'ledger_total':450,'M05_ledger_rows':90,'prior_papers_unchanged':True,'source_images_unchanged':True,'external_review':'not_started','drive_backup':DRIVE}
        (TARGET/'核验记录/上传完整性核验.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':'PASS','exact_rebuilt_files':35,'questions':90,'ledger':450,'main_parent':BASE,'external_review':'not_started'},ensure_ascii=False))
    except BaseException:
        ledger.write_bytes(ledger_before)
        for p,content in entry_original.items():Path(p).write_bytes(content)
        if TARGET.exists():shutil.rmtree(TARGET)
        raise

if __name__=='__main__':
    main()
