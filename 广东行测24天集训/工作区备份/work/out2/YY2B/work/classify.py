import json, re, sys, collections
IDX='/home/user/work/index'
def prompt_of(t):
    # last line(s) before options
    m = re.search(r'\n\s*A\s*[\.、．]', t)
    body = t[:m.start()] if m else t
    lines=[l.strip() for l in body.split('\n') if l.strip()]
    # prompt: last line that looks like a question
    for l in reversed(lines[-3:]):
        if re.search(r'(是|为|的是|最恰当|最准确|项是|:|：|\(\s*\)|（\s*）)$', l) or re.search(r'(这段|文段|上述|以上|作者|下列|填入|排列|文中|根据|最适合|最能|接下来|下文)', l):
            return l, body
    return (lines[-1] if lines else ''), body
def classify(t):
    p, body = prompt_of(t)
    pp = p
    if re.search(r'重新排列|语序正确|排序|顺序正确|排列顺序', t): return 'PX', pp
    if re.search(r'依次填入', pp) or re.search(r'填入(画|划)?横线(部分|处)?(的词|的成语|最恰当的(一项|一组|词))', pp): return 'XC', pp
    if re.search(r'填入|横线', pp): return 'TK', pp
    if re.search(r'标题', pp): return 'BT', pp
    if re.search(r'接下来|下文|后文|随后|紧接', pp): return 'XW', pp
    if re.search(r'相符|不符|理解(正确|准确|错误|不准确|不正确|有误)|推出|符合|说法(正确|错误|准确)|没有(提及|涉及)|提到|属于|不属于|可以得出|不能得出|可知|成立', pp): return 'XJ', pp
    if re.search(r'意在|旨在|主要(说明|讲述|介绍|论述|强调|表达|谈论|讲|阐述|论证|揭示|探讨|分析|谈|想|反映|体现|观点)|主旨|概括|核心|观点|重在|想要|想说明|作者|主要内容|中心|告诉我们|启示|强调', pp): return 'ZZ', pp
    if re.search(r'指的是|意思是|理解为|所指|含义|是指|意指|指代', pp): return 'CJ', pp
    if re.search(r'态度', pp): return 'TD', pp
    return '??', pp
if __name__=='__main__':
    tags=sys.argv[1:]
    for tag in tags:
        ix=json.load(open(f'{IDX}/{tag}.json'))
        c=collections.Counter()
        for q in ix:
            if q['kind']!='q' or q.get('section')!='言语': continue
            k,p=classify(q['text'])
            c[k]+=1
            print(tag, q['qno'], k, '|', p[:60])
        print('##', tag, dict(c))
