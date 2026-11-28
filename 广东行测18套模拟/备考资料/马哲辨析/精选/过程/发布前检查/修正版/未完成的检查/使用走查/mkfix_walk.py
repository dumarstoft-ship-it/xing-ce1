# walk 检查人的改法（在副本 site_fix/index.html 上）：睡醒时正在做题页/小结页没核对的，离开做题页时补核对一次
import sys
p = sys.argv[1]; s = open(p, encoding="utf8").read()
def sub(tag, old, new):
    global s
    assert s.count(old) == 1, (tag, s.count(old))
    s = s.replace(old, new)
sub("W1-变量", 'let waking = 0;      // 页面睡了一阵再回来、正在向云端核对的那几秒（见 resync）',
    'let waking = 0;      // 页面睡了一阵再回来、正在向云端核对的那几秒（见 resync）\nlet wakeDue = false; // 睡醒时正在做题（或停在小结页），当时没核对：离开做题页时补上')
sub("W1-resync", '  if (!S.ref || S.cloud === "local" || !S.synced || S.run || waking) return;\n  const my = ++wakeSeq; let open = true;',
    '  if (!S.ref || S.cloud === "local" || !S.synced || waking) return;\n  if (S.run) { wakeDue = true; return; }      // 做题中不打断，记下来\n  wakeDue = false;\n  const my = ++wakeSeq; let open = true;')
sub("W1-exitRun", 'function exitRun() { S.run = null; route(); }', 'function exitRun() { S.run = null; if (wakeDue) resync(); route(); }')
sub("W1-hashchange", 'window.addEventListener("hashchange", () => { if (S.run) S.run = null; route(); });',
    'window.addEventListener("hashchange", () => { if (S.run) { S.run = null; if (wakeDue) resync(); } route(); });')
sub("W1-dayRolled", '  if (S.run && S.run.day && S.run.day !== today) S.run = null;', '  if (S.run && S.run.day && S.run.day !== today) { S.run = null; if (wakeDue) resync(); }')
open(p, "w", encoding="utf8").write(s)
print("ok")
