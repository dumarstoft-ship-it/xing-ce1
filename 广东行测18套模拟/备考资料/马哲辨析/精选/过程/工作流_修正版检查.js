export const meta = {
  name: 'verify-v7c',
  description: '政常辨析日课第7版修正的独立检查：逐处审读、使用走查、同步收敛三路，各自设法找出问题',
  phases: [{ title: '检查', detail: '三位检查人各查一路，互不通气' }],
}

const SP = '/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad'

const COMMON = `
你是一位独立检查人，任务是给一个网页的修正版找毛病。请用中文、平实的话写结论。

## 背景
“政常辨析日课”是一个做题网页（一个 index.html 加四个 json 数据文件），用户一个人用，手机和电脑轮着用，每天做“今日计划”50题，考试在 2026-12-06。
做题记录存两处：这台设备的 localStorage（键 mzbx-progress-v1），和云端的一份文档（window.claude.use("db") 得到 db，db.doc("progress/main") 得到 ref）。
云端接口的行为（照接口说明）：ref.get() 读一次；ref.set(整份) 整份替换、后写的盖掉先写的、没有事务；ref.onSnapshot(cb, err) 监听。
快照有 exists、data()、metadata.fromCache（真=只是本机缓存的副本）、metadata.hasPendingWrites（真=自己还没被云端确认的写入）。
云端返回的文档，键是按字母排过序的。断网时 get() 可能给 fromCache 的副本或抛 code 为 "unavailable" 的错；set() 断网时可能一直挂着，连上后才完成。
写不进去时错误的 code 可能是 quota_exceeded、not_granted 等。文档上限 256 KiB（整份记录约 77 KiB）。

## 版本
- ${SP}/v7b/ ：第7版（之前发布的）。上一轮两位检查人在它上面查出10条问题，原文在 ${SP}/final_check_results.json。
- ${SP}/v7c/ ：第7版修正（现在要你查的；主持人正在把它发布出去）。两个目录的数据文件完全一样，只有 index.html 不同。
- ${SP}/patch_v7c.py ：从 v7b 到 v7c 的全部改动（32处替换，每处有中文标签，old/new 原文都在里面）。
- ${SP}/v7c_notes.md ：改了什么、哪些地方和上一轮检查人的建议不一样（A–H，这些是主持人自己定的，最值得查）、已知并接受的限制、已经跑过哪些测试。**先读这份。**
- ${SP}/v7c_noplan/ ：同一份 index.html 配没有精选标记的数据（页面退回“马哲一组、政常一组”的老样子），用来确认老样子没被改坏。

## 现成的工具（都可以读；要用就先复制到你自己的目录再跑，不要在原目录里运行，也不要改原目录里的任何文件）
- ${SP}/v7b_conv/ ：sim.js（在 Node 里原样运行页面脚本，多台设备共用一份假云端，虚拟时钟；\`SITE=<相对 v7b_conv 的站点目录> node sim.js scen <情形…>\` 或 \`node sim.js fuzz <起始种子> <轮数> <每轮步数> [keepLater=1 focus=1 noreset=1 midnight=1 old=1 ndev=3 …]\`），driver.js（它驱动页面用的函数），lib.js 加 pw_stale_run.js、pw_settle_fight.js（真浏览器、多设备假云端），sum.py（汇总 fuzz 输出）。oldsite/ 是更老的第6版页面。
- ${SP}/v7b_walk/ ：lib.js（Playwright：假时钟、可选假云端、像用户一样点着做题、版面检查），s1–s8 是上一轮的走查脚本。
- ${SP}/v7c_tests/ ：lib.js（同上，默认站点指向 v7c，可加预置脚本），t_wake.js（主持人给 A–D 写的测试）。
- ${SP}/rev2_sync/ 、${SP}/rev2_plan/ ：第一轮两位审查人的复现脚本。
- ${SP}/rc/ ：主持人对最终文件重跑全部测试的输出（还在跑，_status_*.txt 是各项的退出码）。这些只说明“已有的测试过了”，你的任务是找它们没测到的。
- Playwright 和 Chromium 已装好：require('playwright')，chromium.launch() 不带参数。站点用路由拦截 http://mz.local/** 提供（lib.js 里有现成写法）。Node 里跑页面脚本时请设 TZ=Asia/Shanghai。

## 规矩
- 只在你自己的目录 ${SP}/v7c_chk_<你的代号>/ 里新建和修改文件（代号见下）。不要改 v7c/、v7b/ 和上面那些工具目录；不要动 /home/user/xing-ce1 仓库里的任何文件；不要访问外网。
- 这台机器只有4个核，别的检查人和主持人的测试也在跑：同时运行的进程不要超过2个，单个命令不要超过8分钟（长的拆开跑）。
- 每条问题都要有能重放的证据：脚本路径和输出路径，输出里能看到问题。只凭读代码怀疑、没有跑出来的，写进 checked 里说明“怀疑但没复现”，不要当成问题报。
- v7c_notes.md 里列的“已知、接受的限制”不用再报，除非实际比那里写的更严重。
- 如果你建议改法，请在你自己目录里的副本上改好并用同一个脚本验证过，再写进 fix。
- 严重程度：严重=会丢做题记录、页面不能用、云端被写个不停；中等=计划排错、按钮点不了或点了没反应、显示的数字或文字与实际不符而且会误导；轻微=其他。
- 大约用40分钟。时间不够时，优先把最可能出问题的地方查透，并在 checked 里写清楚哪些查了、哪些没查。
`

const ROLES = {
  read: {
    label: '逐处审读',
    task: `
## 你的代号：read。你这一路：逐处审读改动
1. 对着 patch_v7c.py 的32处替换，逐处读 v7c/index.html 里改后的代码和它周围的函数（mergeProg、pushCloud、connectCloud、cloudSettled、resync、back、beat、dayRolled、ownGroup、saveRun、syncRun、reveal、nextQ、resumePlan、resumeToday、coreShort、planPanel、todayPanel、runSummary、confirmReset、start 和热更新快照）。
2. 每一处都问：会不会抛错（变量没定义、暂时性死区、对空值取属性、toISOString 遇到无效时间）；条件写反或漏了情形没有；几个异步函数（pushCloud、resync、监听回调、定时器）交错时状态会不会乱（S.synced、S.cloud、waking、wakeSeq、S.saving、S.again、lastWrote、wroteSame、cloudTimer、retryTimer）；定时器会不会越积越多或永远不停；文字有没有错字、和实际行为对不对得上。
3. 特别要查的环境：
   - 离线单文件版：仓库里的 /home/user/xing-ce1/广东行测18套模拟/备考资料/马哲辨析/build_single.py 会把站点打成一个 html（题库放进 id 为 mz-data 的脚本块，没有 window.claude，S.cloud 是 "local"）。请读这个脚本（只读），在你自己的目录里照它的做法用 v7c 打一份单文件，用浏览器打开做几题、切后台再回来、过零点，确认新加的心跳、睡醒核对在这里不出错、不显示奇怪的提示。
   - 没有云端权限的访客（use("db") 给了 db 但 set() 抛 not_granted；或 onSnapshot 直接走错误回调）。
   - 热更新：页面重新发布时，旧页面用 window.claude.hot.snapshot 交出 { run: {…} }，新页面 start(hot) 接手。旧版（v7b）交出的 run 没有 day 字段。
   - get() 一直不返回（既不成功也不失败）、set() 一直挂着时，页面还能不能做题、按钮会不会一直灰着、以后还会不会再同步。
   - 设备时钟往回拨、时区改变。
4. 怀疑的地方写个小测试跑出来（Node 的 vm 里跑页面脚本，或 Playwright）。
`,
  },
  walk: {
    label: '使用走查',
    task: `
## 你的代号：walk。你这一路：像用户一样用（390×844 的手机尺寸为主）
上一轮的走查脚本（v7b_walk/s1–s8）主持人已经在 v7c 上重跑过（输出在 rc/walk_*.txt），你不用重复，请走它们没走到的路，重点是这次新加的东西在真实使用里顺不顺：
1. 睡醒：手机做到一半锁屏几小时再拿起来（同一天、隔一天；有网、没网、网很慢）；停在今日页、题目页（刚选了选项还没看解析、看着解析）、小结页、练习页、错题页、卡片页（搜索框里打了字）、记录页（“清除全部记录”点了一下正等第二下、导入框里粘了文字）。每种情况：页面有没有莫名其妙跳走、打的字和展开的面板还在不在、按钮灰多久、提示的话对不对、之后做的题记上了没有。连着锁屏、解锁好几次呢？
2. 两台设备轮着用一整天、两天：手机上午做一部分，电脑接着做，手机晚上“再加20题”；其中一台忘了退出就合上。每次换手后看今日面板的数字（已做几题、核心已学、今天已答）和实际对不对得上，有没有重复出已经做过的题。
3. 零点：做着题跨零点（连着做、中间停两分多钟、中间切出去再回来）；今日页开着跨零点。看用户会不会糊涂。
4. 考前两天、考试当天、考后一天：面板、题目页、小结页每句话读一遍，有没有和当天情形对不上的（“明天”“新题”“再加”）。
5. “再加20题（新题N道）”按钮上的数和实际那一组对不对；缺了两天课之后“还差X道”的估算和照做之后的实际差多少；提示里说的办法（调高一档、再加20题）照做以后数字怎么变。
6. v7c_noplan（没有精选标记的老样子）走一遍基本流程，确认没被改坏、没有多出来的字。
7. 每一步顺手用 lib.js 的版面检查看有没有横向溢出、null/undefined/NaN 字样、控件伸出屏幕；深色模式下看一眼今日页和题目页。
和 v7b 对比着看：有没有哪件事在 v7b 上是好的、到 v7c 反而坏了。
`,
  },
  sync: {
    label: '同步收敛',
    task: `
## 你的代号：sync。你这一路：多台设备的记录会不会乱、会不会丢、会不会写个不停
主持人已经在 v7c 上重跑了上一轮的 sim.js（定向9种情形，随机交错若干批，种子见 v7c_notes.md 和 rc/sim_*.txt）。请查它们没覆盖的，重点是 v7c_notes.md 里 A–D、H 这几处主持人自己定的做法：
1. 睡醒后重新核对云端（resync、back、beat、waking）。sim.js 的环境里页面有心跳定时器、会收到 visibilitychange 和 focus；请加定向情形：睡醒时 get() 失败很多次、get() 很久才回来（超过10秒）、回来的是 fromCache 副本、睡醒核对和写云端（pushCloud）同时在跑、睡醒核对进行中又来一次睡醒、云端在核对期间被另一台设备改了。看有没有：按钮永远灰着（syncing() 一直为真）；本机做的题最后没到云端；同一处来回写。
2. 同一份内容最多写3次（lastWrote、wroteSame）。找：需要第4次才能收敛、于是某台设备的记录一直没到云端的情形（三台设备、网络慢、set 失败但其实已落到云端等）；以及3次都拦不住的来回写（两台设备每次写的内容都略有不同，比如只有 updated 在变）。
3. 清除全部记录：较旧一方只作废清除当天及之前的记录。找：清除之后记录又活过来；清除后别的设备上后来做的题被清掉（超出“已知限制”说的范围）；两台设备对“清除当天”是哪天看法不同（时区、零点前后）时会不会来回写。
4. 题组（today、today2、plan）和做题页（ownGroup、saveRun、syncRun）：两台设备同一天各自排了计划、其中一台停在做题页；时钟差几分钟；一台时区不同。看当天的计划会不会被换成别的名单、已做的位置会不会倒退、两边会不会顶来顶去。
5. 新旧混用：把 v7b（上一版，不是 oldsite 那个更老的）也当成一种设备放进 sim（在你自己的目录里复制一份 sim，把 v7b 加成一种站点），v7b 和 v7c 各一台、各两台，带清除和不带清除。看 v7c 设备上做的题会不会丢、会不会写个不停。用户可能有一台设备上的旧页面一直没刷新。
6. 随机交错请用没用过的种子（30000 以上），每批 100–200 轮；注意 sim 的检查项里“answers-after-reset-wiped(stale-device)”和“later-reset-overridden”属于已知限制。其它类型（device-differs-from-cloud、answer-missing-in-cloud、answer-lost-everywhere（只有新版设备时）、writes-never-stop、wrong-answer-overridden、today-group-replaced-by-foreign-list、pre-reset-record-survived、localStorage-differs）出现了就要追到原因。
发现问题后，尽量再用真浏览器（v7b_conv/lib.js 或 v7c_tests/lib.js）复现一次。
`,
  },
}

const SCHEMA = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string', description: '一句话说清问题' },
          severity: { type: 'string', enum: ['严重', '中等', '轻微'] },
          where: { type: 'string', description: '哪个函数、哪段文字' },
          scenario: { type: 'string', description: '用户怎么用会碰到、后果是什么' },
          evidence: { type: 'string', description: '脚本路径、怎么运行、输出路径、输出里的关键几行' },
          fix: { type: 'string', description: '建议的改法；写明是否已在副本上验证' },
          worse_than_v7b: { type: 'boolean', description: '这个问题在 v7b 上没有、是 v7c 新带来的吗' },
        },
        required: ['title', 'severity', 'where', 'scenario', 'evidence', 'fix', 'worse_than_v7b'],
      },
    },
    checked: { type: 'string', description: '查了哪些情形、各跑了多少、哪些怀疑但没复现、哪些没来得及查' },
    ok_to_keep: { type: 'boolean', description: 'v7c 现在这样能继续给用户用吗（发现的问题都不要紧、或者比 v7b 好就算能）' },
  },
  required: ['findings', 'checked', 'ok_to_keep'],
}

phase('检查')
const order = (args && args.roles) || ['read', 'walk', 'sync']
const results = await parallel(order.map((k) => () =>
  agent(COMMON + ROLES[k].task, { label: ROLES[k].label, phase: '检查', schema: SCHEMA })))
return { results: order.map((k, i) => ({ role: k, label: ROLES[k].label, result: results[i] })) }
