"""把只存在于本机 /home/user/work 的工作状态备份进仓库，供换人、换会话后恢复。
用法：python3 /home/user/work/tools/backup_workspace.py
恢复办法见备份目录里的 RESTORE.md。"""
import os, shutil, sys
W = '/home/user/work'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad'
B = '/home/user/xing-ce1/广东行测24天集训/工作区备份/work'
IMG = ('.png', '.jpg', '.jpeg', '.gif')
def copy_tree(src, dst, skip_dirs=(), skip_ext=(), only_ext=None, fresh=True):
    if fresh and os.path.isdir(dst): shutil.rmtree(dst)
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in skip_dirs and d != '__pycache__' and d != 'node_modules']
        for f in files:
            lf = f.lower()
            if lf.endswith('.bak') or lf.endswith('.pyc'): continue
            if skip_ext and lf.endswith(skip_ext): continue
            if only_ext and not lf.endswith(only_ext): continue
            rel = os.path.relpath(os.path.join(root, f), src)
            out = os.path.join(dst, rel); os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(os.path.join(root, f), out); n += 1
    return n
os.makedirs(B + '/out', exist_ok=True)
shutil.copy2(f'{W}/SPEC.md', B)
print('tools', copy_tree(f'{W}/tools', f'{B}/tools'))
print('index', copy_tree(f'{W}/index', f'{B}/index'))
print('answers', copy_tree(f'{W}/answers', f'{B}/answers'))
shutil.copy2(f'{W}/qindex.jsonl', B)
for f in ('claims.jsonl', 'claims_notsame.jsonl'): shutil.copy2(f'{W}/out/{f}', f'{B}/out/')
print('zl_materials', copy_tree(f'{W}/out/zl_materials', f'{B}/out/zl_materials'))
# 第1—3轮各编者的非图片文件（图片已在各批成品里）
for d in ('out', 'out2', 'out3'):
    n = 0
    for e in sorted(os.listdir(f'{W}/{d}')):
        p = f'{W}/{d}/{e}'
        if not os.path.isdir(p) or e == 'zl_materials': continue
        n += copy_tree(p, f'{B}/{d}/{e}', skip_dirs=('assets',), skip_ext=IMG)
    print(d, n)
# 第4轮现场：全部保留（含图片）
print('out4', copy_tree(f'{W}/out4', f'{B}/out4'))
# 合并配置等小文件（成品目录不收，成品在仓库各批目录里）
os.makedirs(f'{B}/build', exist_ok=True)
for f in os.listdir(f'{W}/build'):
    if os.path.isfile(f'{W}/build/{f}'): shutil.copy2(f'{W}/build/{f}', f'{B}/build/')
os.makedirs(f'{B}/books', exist_ok=True)
for f in os.listdir(f'{W}/books'):
    if os.path.isfile(f'{W}/books/{f}') and f.endswith(('.py', '.js')): shutil.copy2(f'{W}/books/{f}', f'{B}/books/')
# 各编者放在临时目录里的脚本
print('scratchpad scripts', copy_tree(SP, f'{B}/scratchpad_scripts', only_ext=('.py', '.js')))
tot = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(B) for f in fs)
print('total MB %.1f' % (tot / 1e6))
