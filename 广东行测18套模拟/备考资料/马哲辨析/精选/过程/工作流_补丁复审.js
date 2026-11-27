export const meta = {
  name: 'review-plan-patch',
  description: '独立审查“每日计划”修订补丁：云端同步与合并会不会丢记录；作答记录、排程、题组续做有没有新问题',
  phases: [
    { title: '找问题', detail: '两位审查人各看一块，自己跑浏览器复现' },
  ],
}

const REPO = '/home/user/xing-ce1'
const DIR = `${REPO}/广东行测18套模拟/备考资料/马哲辨析`
const SP = '/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad'
const DTS = '/tmp/claude-0/bundled-skills/2.1.332/61392e910097c7c8fb7dce6111c5c23c/artifact-capabilities/0.2.99/db.d.ts'

const CONTEXT = `背景：这是一个给广东省考考生用的做题网页（单个 HTML 文件，题库是同目录的 JSON），考试在2026-12-06，用户每天做50题。做题记录存在浏览器本机（localStorage）和云端（页面运行环境提供的 db，一份文档 progress/main，只有所有者可读写）。题库625道题里，200道被标成“核心”（t=1）或“备选”（t=2），带顺序 o；“今日计划”每天按规则排50题。

上一轮审查发现了一批问题，现在有一份修订补丁，还没有发布。你的任务是在发布前独立审查这份补丁：先假设它有错，找出会丢记录、排错题、卡住或报错的地方。

文件：
- 改动前的网页：${DIR}/site/index.html
- 改动后的网页：${SP}/v7/index.html （用 diff 看两者的差别；改动由 ${SP}/patch_v7.py 生成，脚本里每段有注释）
- 测试站点（都用改动后的网页）：${SP}/v7 （160道核心、40道备选是随机抽的）、${SP}/realdraft （真实名单的草稿）、${SP}/v7_noplan （没有精选数据，页面应退回“马哲一组、政常一组”的旧样子）
- 已有的测试脚本，可以当作写法的参考：${SP}/v7_cloud_test.js <站点目录>（7种云端同步情形，用假的 db）、${SP}/v7_plan_test.js <站点目录>（当天重做、别处做过的题、跨零点、考前两天、折叠面板）、${SP}/plan_sim.js <站点目录> <起始日> <首次正确率> <复习正确率>（从起始日到12月5日每天做完计划）。它们现在都通过。
- db 的接口说明（权威）：${DTS} 。要点：set 是整份替换、后写覆盖；onSnapshot 可能先给一份上次留下的副本（metadata.fromCache 为 true），云端确认过的记录随后才到；自己写入后会先收到 hasPendingWrites 为 true 的快照；云端连不上时可能长时间没有任何回调。

补丁做了什么（设计意图）：
1. 云端同步：收到云端确认过的第一份记录之前不写云端（S.synced）；这期间“今日计划”和“今日一组”的“开始”不可点，最多等10秒，超时后先存本机（S.cloud 变成 slow），连上后再合并。收到快照时不再整份替换，而是合并（mergeProg）：同一道题留最近练过的那份（同一天取作答次数多的；都一样但内容不同时跟较新的整份记录走），每天的作答数取多的，设置和当天的题组（today、today2、plan）跟 updated 较新的一份走；本机有云端没有的内容时，合并后推回云端。
2. 作答记录（record）：每天只有当天第一次作答能升盒、改到期日、记“隔天又答对”；答错随时回到第0盒、明天到期；当天再答对不改盒子和到期日。计划的第①类按“第0盒且到期”取。
3. 排程（planParts）：平日顺序是 ①第0盒到期的 ②保底的核心新题（每天题数的四成）③核心里第1盒到期的 ④其余核心新题 ⑤核心里第2盒以上到期的 ⑥备选里到期的 ⑦备选新题 ⑧最久没见的。考前两天和考试当天另有顺序，考试当天不上新题。新题保持 o 的顺序，不打乱；同一知识点一天只上一道新题，核心凑不满时放宽。
4. 题组续做（settle）：当天定好的题组（今日计划、分科的今日一组）里还没轮到、但今天已在别处做过的题算作已做；题库里已经没有的题去掉。
5. 其他：改设置后原地重画（route(true)、rerender），折叠面板记住展开状态；页面开着过了零点会换成新一天；面板的预估文字改了；小结页说明当天重做不算过关。

怎么在本机跑：浏览器用 Playwright（require('playwright') 直接可用，chromium.launch() 不用参数）。页面要通过路由拦截打开，照已有测试脚本的写法。做实验请把站点整个复制到 ${SP}/rev2_<你的代号>/ 下，脚本也放那里；不要改 ${SP}/v7、realdraft、v7_noplan 和仓库里的任何文件，不要 git 提交。只报告问题。`

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string', description: '一句话说清问题' },
          severity: { type: 'string', enum: ['严重', '中等', '轻微'] },
          where: { type: 'string', description: '函数名（或行号）' },
          scenario: { type: 'string', description: '具体怎么触发：什么状态、做了什么、出现什么错误结果' },
          evidence: { type: 'string', description: '你怎么确认的：跑的脚本路径和关键输出' },
          fix: { type: 'string', description: '建议怎么改，具体到代码' },
        },
        required: ['title', 'severity', 'where', 'scenario', 'evidence', 'fix'],
      },
    },
    checked: { type: 'string', description: '你检查过、确认没问题的方面，300字以内' },
  },
  required: ['findings', 'checked'],
}

const LENSES = [
  { key: '同步', code: 'sync', prompt: `你的范围：云端同步与合并（touch、scheduleCloud、pushCloud、mergeProg、syncing、cloudSettled、connectCloud），以及它和导入导出（importProg、exportProg）、清除记录（confirmReset）、题组（plan、today、today2）的配合。重点找“记录会丢、会被旧记录盖掉、会反复写云端停不下来”的路径。至少检查：
1. 两台设备交替或同时使用：A 做题时 B 打开、B 做题后 A 不刷新继续做（A 会实时收到 B 的写入）、两边都离线各做一段再先后连上、一边清除全部记录后另一边打开（清除应当生效还是被另一边的记录“复活”？按现在的合并规则会怎样，这是不是用户想要的）。
2. 快照的各种到达顺序：只有缓存副本、迟迟没有确认过的记录；先缓存后确认；确认过的记录是“文档不存在”；带 hasPendingWrites 的快照；error 回调；10秒超时后才连上；db 为 null（离线单文件版）。
3. mergeProg 的每条分支：同一天同次数但内容不同（例如只改了“能讲清”自评 e）；设置只在一边改过；两边各自生成了当天的 plan（ids 不同）时跟哪边、另一边做过的题怎么办；合并后 updated 的取值会不会让下一次比较出错；合并会不会造成“写云端 → 收快照 → 又写”的循环（数一数 set 的次数）。
4. 写入时序：pushCloud 的 S.saving、S.again，unavailable 重试；页面关闭前900毫秒内的作答有没有机会丢（本机已存，下次打开能否补推）。
5. 文档大小：做满625题、plan 带50个题号时 progress/main 有多大（上限256 KiB）。
用假的 db 做实验时，要让它尽量贴近接口说明（可以让多台“设备”共用同一份远端文档，并把一边的写入推给另一边的监听）。` },
  { key: '排程', code: 'plan', prompt: `你的范围：作答记录（record）、排程（planParts、planGroup、settle、resumePlan、resumeToday、planPanel、mixChips、dailySelect）、重画（route、rerender、dayRolled）和它们对旧功能的影响。重点找“题排错了、该出的不出、不该出的出了、点了没反应、数字对不上、没有精选数据时和以前不一样”的地方。至少检查：
1. record 的新规则在所有入口下是否一致：今日计划、分科今日一组、按模块练、自选练习、错题重练（startRedo，会把判断题换成改正后的说法）、本组错题再做一遍、计划加练（再加20题）。错题页、卡片状态、记录页的统计在“当天重做答对”之后各显示什么，有没有自相矛盾。老记录（没有 b 或 due 字段的题、b 很大的题）会怎样。
2. planParts：各类之和是否总等于清单长度；同一道题会不会进两类；考前两天、考试当天、考试之后；每天题数改成20或80；核心全学完之后；只有备选没学时；计划外的题答错后进①的规则；“再加20题”连续点几次；今天在别处先学了新题再开始计划。
3. settle：计划做到一半去别处做了计划里后面的题（答对、答错各试）；做完计划后又去分科一组；题组里的题全部在别处做完；题库少了一道题；它在 planPanel 渲染时会写记录（touch），会不会造成反复重画或反复写云端。
4. 用 plan_sim.js 在 ${SP}/realdraft 上跑几组（起始日11-28、11-29；首次正确率0.6、0.75、0.9；每天只做前30题的情况自己改脚本试），看核心学完的日期、考前是否把答错过的题都再过了一遍、有没有哪天清单不满50或出现重复题。
5. 没有精选数据的站点（v7_noplan）：今日页、做题、小结、错题重练是否和改动前的网页一致（record 的规则变化是有意的，其余不应变）；${SP}/mz_test4.js <站点目录> <输出目录> 是旧的整页测试，可以跑。
6. 界面：390px 宽下今日计划面板在三种状态（未开始、进行中、做完）是否正常、有没有横向溢出；“每天题数”在三种状态下改动后的表现；深色模式。` },
]

phase('找问题')
const found = await parallel(LENSES.map(l => () =>
  agent(`你是代码审查人（代号 ${l.code}）。${CONTEXT}\n\n${l.prompt}\n\n只报告你确认存在的问题：每条都要有可复现的场景和证据。没有问题的方面写进 checked。最多报告6条，按严重程度排序。`,
    { label: `复审：${l.key}`, phase: '找问题', schema: FINDINGS, agentType: 'general-purpose' })
    .then(r => (r ? { lens: l.key, findings: r.findings, checked: r.checked } : null))))
return { reviews: found.filter(Boolean) }
