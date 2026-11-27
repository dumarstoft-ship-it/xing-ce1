export const meta = {
  name: 'review-daily-plan',
  description: '从排程正确性、遗忘规律、回归三个角度审查“每日计划”改动，并逐条验证发现',
  phases: [
    { title: '找问题', detail: '三位审查人各看一个角度，可以自己跑浏览器模拟' },
    { title: '验证', detail: '每条发现由另一人尝试推翻' },
  ],
}

const REPO = '/home/user/xing-ce1'
const DIR = `${REPO}/广东行测18套模拟/备考资料/马哲辨析`
const PAGE = `${DIR}/site/index.html`
const SP = '/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad'

const CONTEXT = `背景：这是一个给广东省考考生用的做题网页（单个 HTML 文件，题库是同目录的 JSON），考试在2026-12-06。题库有625道题，其中一部分会被标成“核心”（字段 t=1）和“备选”（t=2），并带做题顺序 o（越小越先学）；其余是“扩展”。刚加了“今日计划”：用户每天做固定题数（默认50），到期的先复习，再按顺序学新题，目标是在考前把核心学完并对抗遗忘。

要审的代码：
- 网页：${PAGE} 。新加的函数是 planParts、planGroup、resumePlan、planCounts、mixChips、dailySelect、planPanel、planWhy，以及 viewToday、viewPractice（“精选”筛选）、pickGroup 的打分、DEFAULT_SETTINGS、blankProg 的改动。相关的旧代码：record（作答记录与间隔）、INTERVALS、todayGroup、todayPanel、renderRun、reveal、runSummary、connectCloud、importProg、exportProg、start。
- 构建脚本：${DIR}/build_data.py 里“精选”一段（读 精选/精选.json，给题目写 o 和 t，写 meta.plan）；单文件导出 ${DIR}/build_single.py 。
- 这次改动的差异：在 ${REPO} 里运行 git show 0a7d2f3 --stat 看不到的话，用 git log --oneline -3 找到“每日计划的逻辑”那次提交，再 git show <提交> -- 广东行测18套模拟/备考资料/马哲辨析/site/index.html 。

设计意图（planParts 上方的注释也写了）：一天的题按这个顺序填满，做不完的自动顺延——①上次答错、今天到期；②只答对过一次、今天到期（第一次间隔复习）；③没做过的核心题（按 o 顺序，同一知识点一天只上一道新题）；④答对两次以上、今天到期；⑤没做过的备选题；⑥还有空位就补最久没见的。考前两天（距考试1天、2天）在①②之后插入“考前回顾”：错过的、只见过一次的、自评讲不清的，最久没见的在前。间隔：答错次日再出；答对后依次隔2天、4天、7天。出题顺序就是上面的类别顺序（复习在前），类别内打乱。计划外的题（扩展）只在上次答错时才进计划。没有精选数据时（没有任何 t=1 的题），页面要和改动前完全一样。

怎么在本机跑：
- 浏览器用 Playwright（require('playwright') 直接可用，chromium.launch() 不用参数）。页面要通过路由拦截来打开，照 ${SP}/plan_sim.js 的写法（它把 index.html 包上 <meta charset> 再返回，JSON 文件按路径返回）。
- 已有一个带随机精选数据的测试站点：${SP}/testsite_plan （160道核心、40道备选，随机抽的，只为测逻辑）。不要改它；要做实验就把它整个复制到 ${SP}/review_<你的角度>/ 下再改。
- ${SP}/plan_sim.js <站点目录> <起始日> <首次正确率> <复习正确率> [每天只做前N题]：从起始日到12月5日每天把今日计划做完，输出每天各类别的题数和结束时的统计。它用注入的假 Date 控制“今天”。
- ${SP}/plan_shot.js <站点目录> <输出目录> <日期>：截今日页的图。
- 不要改仓库里的任何文件，不要 git 提交。只报告问题。`

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
          where: { type: 'string', description: '文件名和函数名（或行号）' },
          scenario: { type: 'string', description: '具体怎么触发：什么状态、做了什么、出现什么错误结果' },
          evidence: { type: 'string', description: '你怎么确认的：读到的代码、跑的命令和输出' },
          fix: { type: 'string', description: '建议怎么改，尽量具体到代码' },
        },
        required: ['title', 'severity', 'where', 'scenario', 'evidence', 'fix'],
      },
    },
    checked: { type: 'string', description: '你检查过、确认没问题的方面，200字以内' },
  },
  required: ['findings', 'checked'],
}

const VERDICT = {
  type: 'object',
  properties: {
    real: { type: 'boolean', description: '这个问题是否真实存在' },
    worth_fixing: { type: 'boolean', description: '考前这9天内值不值得改' },
    reason: { type: 'string', description: '你的验证过程和结论，200字以内' },
    better_fix: { type: 'string', description: '如果你有更稳妥的改法就写，没有留空' },
  },
  required: ['real', 'worth_fixing', 'reason', 'better_fix'],
}

const LENSES = [
  { key: '排程', prompt: `你的角度：排程是否正确。逐行读 planParts、planGroup、resumePlan、planPanel 和 record，对照设计意图找偏差和边界错误。至少检查这些情况，每个都用实际运行或代码推演确认：
1. 用户某天只做了一部分就停（plan_sim.js 的第6个参数），第二天计划怎么接；没做的新题、没做的复习会不会丢。
2. 当天开始后改“每天题数”；当天做完后点“再加N题”；同一天在别处（分科加练、自选练习）做过计划里的题。
3. 跨过零点后页面没刷新（S.prog.plan.day 是昨天）时继续做；从云端同步回来的旧记录没有 plan 字段、没有 settings.daily；老记录里某些题缺字段。
4. 考前两天（finalDays）的“考前回顾”条件和排序；考试当天及之后打开页面。
5. “同一知识点一天只上一道新题”会不会让某些题永远轮不到；多知识点的题。
6. 计划外的题上次答错后进计划的规则；暂停（hold）和待审（review）的题。
7. extra 类别会不会把今天刚做过的题又排进来；用 spread(shuffle()) 会不会改变截取的集合。
8. planCounts、mixChips、planPanel 显示的数字和实际计划是否一致（例如预览时的题数与点“开始”后的题数）。` },
  { key: '遗忘', prompt: `你的角度：对抗遗忘的效果。考试在12月6日，用户从11月27日或28日开始，每天50题。请评估现在的规则是否让“考试那天还记得”的题最多，并找出可以改进的地方。要求用模拟说话：
1. 用 plan_sim.js 跑几组（起始日11-27和11-28；首次正确率0.6、0.75、0.85；每天做满和只做35题），看核心学完的日期、每题见面次数的分布、只见过一次的题数、12月3日以后还见过一次的题占比、答错过的题考前是否都再见过。
2. 审视类别顺序：新核心题排在“答对两次以上到期”的复习之前是否合理；考前两天是否还该上新题；最后一天（12月5日）学的新题没有复习机会，是否应该把新题的截止日提前；“考前回顾”是否应该覆盖所有核心题而不只是错过的。
3. 审视间隔：答对后隔2天、4天、7天，在9天的窗口里是否合适；有没有某一天复习量超过每天题数、把新题挤没了的情况，是否需要平滑。
4. 如果你认为某个改法更好，把测试站点复制一份，改它的 index.html 里的 planParts，再跑同样的模拟，给出改前改后的数字对比。只报告有数字支持的改进，不要泛泛而谈。` },
  { key: '回归', prompt: `你的角度：有没有弄坏原有功能，以及界面是否正常。
1. 没有精选数据时（把测试站点复制一份，去掉 questions.json 里所有题的 t 和 o、meta.json 里的 plan），今日页、练习页、做题、错题重练、卡片、待审、附录、记录页是否和改动前一样；可以跑 ${SP}/mz_test4.js <站点目录> <输出目录>（它是旧的整页测试）看看有没有报错。
2. 有精选数据时：今日页各面板、“精选依据”折叠、“分科加练”折叠里的两个面板和入口是否都能用；做题页是否显示“核心”“备选”标签；自选练习的“精选”筛选是否生效；记录页有没有报错。
3. 做题中途刷新页面、热更新恢复（window.claude.hot 的 snapshot/restore，tkey 为 "plan"）、退出后“继续”、做完后的小结页。
4. 导出、导入记录后计划是否正常；本机记录键 mzbx-progress-v1 的老数据（只有 today、today2）加载后是否正常。
5. 手机宽度（390px）下有没有横向溢出；深色模式下新加的元素颜色是否正常（页面用 CSS 变量和 prefers-color-scheme）；键盘操作和标签（label for）是否对应。
6. build_data.py 的精选一段：精选.json 不存在、题号重复或不存在、core 越界时的行为；build_single.py 导出的单文件里是否带上了 meta.plan 和题目的 t、o。` },
]

phase('找问题')
const found = await parallel(LENSES.map(l => () =>
  agent(`你是代码审查人。${CONTEXT}\n\n${l.prompt}\n\n只报告你确认存在的问题：每条都要有可复现的场景和证据。没有问题的方面写进 checked。最多报告8条，按严重程度排序。`,
    { label: `审查：${l.key}`, phase: '找问题', schema: FINDINGS, agentType: 'general-purpose' })
    .then(r => (r ? r.findings.map(f => ({ ...f, lens: l.key })) : []))))
const all = found.filter(Boolean).flat()
const rank = { '严重': 0, '中等': 1, '轻微': 2 }
all.sort((a, b) => rank[a.severity] - rank[b.severity])
const toVerify = all.slice(0, 12)
if (all.length > toVerify.length) log(`共 ${all.length} 条发现，只验证最重的 ${toVerify.length} 条；其余 ${all.length - toVerify.length} 条原样带回`)
else log(`共 ${all.length} 条发现，全部验证`)

phase('验证')
const verified = await parallel(toVerify.map((f, i) => () =>
  agent(`你是复核人，要独立判断下面这条代码审查发现是否属实。先假设它可能是错的，自己去读代码、跑测试来证实或推翻。\n\n${CONTEXT}\n\n待验证的发现（来自“${f.lens}”角度的审查人）：\n- 问题：${f.title}\n- 位置：${f.where}\n- 触发场景：${f.scenario}\n- 对方的证据：${f.evidence}\n- 对方建议的改法：${f.fix}\n\n请判断：这个问题是否真实存在（real）；在考前这9天、用户每天做50题的实际使用里值不值得改（worth_fixing，罕见到几乎碰不到、或改动风险大于收益的写 false）；如果建议的改法有漏洞或有更稳妥的改法，写在 better_fix 。做实验请把测试站点复制到 ${SP}/verify_${i}/ 下再改，不要动别人的目录和仓库文件。`,
    { label: `验证：${f.title.slice(0, 18)}`, phase: '验证', schema: VERDICT, agentType: 'general-purpose' })
    .then(v => ({ ...f, verdict: v }))))

return {
  confirmed: verified.filter(Boolean).filter(f => f.verdict && f.verdict.real),
  rejected: verified.filter(Boolean).filter(f => f.verdict && !f.verdict.real).map(f => ({ title: f.title, reason: f.verdict.reason })),
  unverified: all.slice(toVerify.length).concat(verified.filter(Boolean).filter(f => !f.verdict)),
}
