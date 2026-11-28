export const meta = {
  name: 'verify-plan-patch-v7b',
  description: '发布前的最后检查：对修订后的同步代码做随机交错的收敛性测试，并按真实使用过程走查今日计划',
  phases: [
    { title: '检查', detail: '两位检查人各管一块，自己写脚本复现' },
  ],
}

const DIR = '/home/user/xing-ce1/广东行测18套模拟/备考资料/马哲辨析'
const SP = '/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad'
const DTS = '/tmp/claude-0/bundled-skills/2.1.332/61392e910097c7c8fb7dce6111c5c23c/artifact-capabilities/0.2.99/db.d.ts'

const CONTEXT = `背景：给广东省考考生用的做题网页（单个 HTML 文件加同目录的题库 JSON），考试在2026-12-06，用户每天做50题。做题记录存在浏览器本机（localStorage）和云端（页面运行环境提供的 db，一份文档 progress/main）。题库625道题里200道标成“核心”（t=1）或“备选”（t=2），“今日计划”每天按规则排50题。

这个网页马上要发布新版。上一轮审查在同步上找出过一批问题（云端返回的键按字母排序导致页面误判“不一样”而反复写、清除全部记录被别的设备并回来、落后的设备整份覆盖云端、做题当中另一台设备推进了计划、断网重试成串等），现在都改了。你的任务是在发布前对改完的版本再挑一遍毛病：先假设它还有错。

文件：
- 要发布的版本：${SP}/v7b/index.html （题库数据是定稿的，同目录）。它由 ${SP}/patch_v7b.py 从仓库里的旧版 ${DIR}/site/index.html 生成，脚本里每段改动有注释。
- 上一版（改之前的补丁）：${SP}/v7/index.html 。没有精选数据的站点：${SP}/v7b_noplan 。
- 上一轮审查人留下的复现脚本和假 db：${SP}/rev2_sync/ （lib.js 是工具，t1—t11 各一个情形，out7b/ 是它们在新版上的输出，都已符合预期）；${SP}/rev2_plan/ （harness.js、t4_settle、t8_monkey 随机操作、t9_cross 等）。主持人的测试：${SP}/v7_cloud_test.js、${SP}/v7_plan_test.js、${SP}/plan_sim.js 。这些在新版上全部通过，可以当写法参考，不必重跑。
- db 的接口说明（权威）：${DTS} 。要点：set 整份替换、后写覆盖，没有事务；get 读一次；onSnapshot 可能先给上次留下的副本（fromCache 为 true），确认过的记录随后才到；自己写入后先收到 hasPendingWrites 为 true 的快照；云端返回的文档，键是按字母排过序的（真实文档如此）；连不上时可能长时间没有回调，调用会以 unavailable 拒绝。

新版在同步上的做法（设计意图）：
1. 收到云端确认过的第一份记录之前不写云端；这期间“开始”“继续”和题数选择不可用，最多等10秒，超时先走本机，连上后合并。
2. 合并（mergeProg）是对称、确定的：先比“清除时间”（epoch），晚的一方整份胜出；否则同一道题留最近练过的那份（同一天取作答次数多的）；同一天同次数但内容不同的，一边答错一边答对以答错为准，其余冲突跟较新的整份记录（updated 一样时按内容的字典序定先后），只有一边有的字段保留；每天作答数取多的；当天的题组（today、today2、plan）只有一边是今天的就留今天的，否则跟较新的；设置跟“设置改动时间”（st）较晚的一方，都没有 st 时跟较新的整份记录。比较内容一律不看键的先后（canon、sameRec）。
3. 写云端（pushCloud）：先 get 读云端现在的记录并进来，内容一样就不写；失败时只留一条重试、间隔逐次加长；页面转到后台或关闭前把没推的马上推出去。
4. 更新时间（stamp）：保证比本机记录里现有的 updated 大，别的设备时钟偏快也不会让这边的改动被当成旧的。
5. 做题当中并进了别处的记录（syncRun）：接下来的题今天已在别处做过的算作已做；题组位置跟着眼前这一组走。
6. 清除全部记录：写入清除时间并马上推到云端。

纪律：做实验请把站点复制到 ${SP}/v7b_<你的代号>/ 下，脚本也放那里；不要改 ${SP}/v7b、v7、rev2_sync、rev2_plan 和仓库里的任何文件，不要 git 提交。浏览器用 Playwright（require('playwright') 直接可用）。只报告你确认存在、能复现的问题；没有就照实说没有。工具调用控制在40次以内，先查最可能出事的地方。`

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
          where: { type: 'string', description: '函数名' },
          scenario: { type: 'string', description: '怎么触发、出现什么错误结果' },
          evidence: { type: 'string', description: '脚本路径和关键输出' },
          fix: { type: 'string', description: '建议怎么改，具体到代码' },
        },
        required: ['title', 'severity', 'where', 'scenario', 'evidence', 'fix'],
      },
    },
    checked: { type: 'string', description: '检查过、确认没问题的方面，400字以内' },
    safe_to_publish: { type: 'boolean', description: '你是否认为这一版可以发布（没有会丢记录或反复写云端的问题）' },
  },
  required: ['findings', 'checked', 'safe_to_publish'],
}

const LENSES = [
  { key: '同步收敛', code: 'conv', prompt: `你的范围：合并和写云端在多台设备下会不会不收敛、丢记录或反复写。请写一个随机交错的测试（可以直接在 Node 里把页面脚本里的 mergeProg、pushCloud、touch、stamp、record 等函数连同它们依赖的小工具取出来跑，也可以用 Playwright 开两三个页面共用一份假云端——哪种快用哪种）：
- 假云端要照接口说明：返回的文档键按字母排序；set 整份替换；可以让写入延迟、乱序到达、偶尔拒绝为 unavailable；一台设备的写入会推给其他在线设备的监听；设备可以离线一段再回来；时钟可以有偏差（几秒到几分钟）。
- 随机操作：答题（对或错）、同一天重做、改设置、改“能讲清”自评、开始或继续今日计划、清除全部记录、离线、上线、刷新。种子固定，可重放。
- 每轮结束让所有设备上线并静置，检查：（1）各设备本机记录和云端文档内容一致（不看键序）；（2）静置期间写云端的次数有界并最终为0；（3）没有任何一台设备做过的题在最终记录里消失（清除之后做的除外，清除之前的应当都没了）；（4）答错的题没有被“答对”的旧记录盖掉当天的次日复习。
- 另外专门看：还开着旧版页面的设备（旧版逻辑：云端较新就整份替换本机，本机较新就整份 set，不合并、不读 st 和 epoch）和新版设备混用时，新版会不会被拖进反复写，记录会不会丢到两边都没有。旧版页面是 ${DIR}/site/index.html 。
跑不出问题也要给出你跑了多少轮、多少步、哪些种子。` },
  { key: '使用走查', code: 'walk', prompt: `你的范围：站在用户的位置把今日计划从11月28日用到12月6日，找“看起来不对、点了没反应、数字前后矛盾、说明文字和实际不符”的地方。用 Playwright 在 390×844 的手机尺寸下操作 ${SP}/v7b（用假时钟换日，写法见 ${SP}/v7_plan_test.js）。至少走这几条路：
1. 正常用户：每天做完50题，错的点“错题再做一遍”；看每天今日面板的数字和那句“核心还有N道没学……”的说明是否和实际一致（特别是“照现在的量……还差X道”的估算，和真实结果差多少）；考前两天、考试当天、考后的面板。
2. 偷懒用户：有两天只做20题，有一天没做，有一天做完又点了两次“再加20题”。
3. 爱逛的用户：计划做到一半去“练习”里自选核心题做一组、去“分科加练”做马哲一组和错题重练、看卡片、改每天题数、再回计划；页面开着过夜。
4. 两台设备轮着用（共用一份假云端，写法见 ${SP}/rev2_plan/t9_cross.js，假 db 要有 get）：白天手机做一半，晚上电脑接着做；第二天反过来。
每条路都记下：每天计划的构成、面板文字、有没有报错、有没有横向溢出、有没有出现 null、undefined、NaN。再截几张图自己看一眼版面（未开始、进行中、做完、考前两天），图存到你的目录下。` },
]

phase('检查')
const found = await parallel(LENSES.map(l => () =>
  agent(`你是发布前的检查人（代号 ${l.code}）。${CONTEXT}\n\n${l.prompt}\n\n最多报告5条，按严重程度排序。`,
    { label: `发布前检查：${l.key}`, phase: '检查', schema: FINDINGS, agentType: 'general-purpose' })
    .then(r => (r ? { lens: l.key, ...r } : null))))
return { reviews: found.filter(Boolean) }
