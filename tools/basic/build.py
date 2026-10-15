"""3단계 1~15과(노션 DAY 01~15) → 게임 자료.
python3 tools/basic/build.py  (저장소 맨 위에서, 몇 번 돌려도 같은 결과)
만드는 것:
  data/bex.json            교재 예문 {en:{x:[[예문,해석]×2], m:다른 뜻, p:품사, a:추가 품사}}
  data/dex2.json           새 단어 도감 설명 (이미 있는 단어는 건드리지 않음)
  tools/talk/g56.txt       '# 3단계 1~15과' 아래 대화 (다시 만들 때 그 아래를 통째로 바꿈) → talk/build.py
  tools/talk/words.json    g56 에 1~15과
  tools/basic/out/*.js     index.html 에 넣을 조각 (COURSE · WORD_BANK · G56KO · DEX_ADD)
화면에는 교재 이름을 쓰지 않는다."""
import json, os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(R, 'tools', 'basic')
low = lambda s: s.lower()

W, T = [], []
for d in range(1, 16):
    for ln in open(os.path.join(B, 'day%02d.txt' % d), encoding='utf8'):
        p = ln.rstrip('\n').split('|')
        if p[0] == 'W':
            assert len(p) == 10, ln
            W.append(dict(day=d, en=low(p[1]), raw=p[1], ko=p[2], other=p[3], pos=p[4], add=p[5],
                          ex=[[p[6], p[7]], [p[8], p[9]]]))
        elif p[0] == 'T':
            assert len(p) == 5, ln
            T.append(dict(en=low(p[1]), a=p[2], b=p[3], ko=p[4]))
byW = {w['en']: w for w in W}
assert len(byW) == 450, len(byW)

html = open(os.path.join(R, 'index.html'), encoding='utf8').read()
wb = {}
for m in re.finditer(r'\{en:"([^"]+)",ko:"([^"]*)"[^}]*?level:(\d)', html):
    wb.setdefault(m.group(1), m.group(2))

ND = {}
for ln in open(os.path.join(B, 'newdex.txt'), encoding='utf8'):
    if ln.startswith('#') or not ln.strip(): continue
    p = ln.rstrip('\n').split('|'); assert len(p) == 13, (len(p), ln)
    ND[p[0]] = p
EX3 = {}
for ln in open(os.path.join(B, 'ex3.txt'), encoding='utf8'):
    if ln.startswith('#') or not ln.strip(): continue
    p = ln.rstrip('\n').split('|'); assert len(p) == 3, ln; EX3[p[0]] = [p[1], p[2]]
new = [w for w in W if w['en'] not in wb]
miss = [w['en'] for w in new if w['en'] not in ND]
assert not miss, ('newdex.txt 에 없음', miss)

# 대화: @1/@2 → 예문
def tl(t):
    a = t['a']
    if a in ('@1', '@2'): a = byW[t['en']]['ex'][int(a[1]) - 1][0]
    return a
talk_lines = []
for t in T:
    a = tl(t)
    assert '|' not in a + t['b'] + t['ko']
    talk_lines.append('|'.join([t['en'], a, t['b'], t['ko']]))

# bex
bex = {w['en']: {k: v for k, v in dict(x=w['ex'], m=w['other'] if w['other'] != '—' else '', p=w['pos'],
                                       a=w['add'] if w['add'] != '—' else '').items() if v} for w in W}
json.dump(bex, open(os.path.join(R, 'data', 'bex.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))

# dex2 — 새 단어
dexf = os.path.join(R, 'data', 'dex2.json'); dex = json.load(open(dexf, encoding='utf8'))
have = set()
for f in ('dex1', 'dex2', 'dex3'): have |= set(json.load(open(os.path.join(R, 'data', f + '.json'), encoding='utf8')))
def has_word(s, en):
    return re.search(r'(^|[^A-Za-z])' + re.escape(en) + r'(?![A-Za-z])', s, re.I)
added = 0
for w in new:
    en = w['en']
    if en in have and en not in ND: continue
    p = ND[en]
    exs = ([EX3[en]] if en in EX3 else []) + [x for x in w['ex']]   # 쉬운 예문을 맨 앞에
    for t in T:   # 세 번째 예문 — 대화에서 단어가 든 줄
        if t['en'] != en or len(exs) >= 3: continue
        a = tl(t); ka, _, kb = t['ko'].partition(' / ')
        for s, k in ((a, ka), (t['b'], kb)):
            if len(exs) < 3 and has_word(s, en) and s not in [x[0] for x in exs] and k: exs.append([s, k.strip()])
    rel = {k: v for k, v in zip('osfg', p[7:11]) if v}
    desc = p[3]
    pos = w['pos'] + ('·' + w['add'].split(':')[0].strip() if w['add'] not in ('—', '') and ':' in w['add'] and w['add'].split(':')[0].strip() not in w['pos'] and w['add'].split(':')[0].strip() != '표현' else '')
    dex[en] = [desc, pos, p[12], exs, p[4], p[5], p[6], rel, p[11], '']
    added += 1
json.dump(dex, open(dexf, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))

# talk
gf = os.path.join(R, 'tools', 'talk', 'g56.txt'); src = open(gf, encoding='utf8').read()
MK = '# 3단계 1~15과 (노션 DAY 01~15)'
src = src.split('\n' + MK)[0].rstrip('\n') + '\n' + MK + '\n' + '\n'.join(talk_lines) + '\n'
open(gf, 'w', encoding='utf8').write(src)
wf = os.path.join(R, 'tools', 'talk', 'words.json'); wj = json.load(open(wf, encoding='utf8'))
wj['g56'] = [[str(d), [w['en'] + '=' + w['ko'] for w in W if w['day'] == d]] for d in range(1, 16)] + [x for x in wj['g56'] if int(x[0]) > 15]
json.dump(wj, open(wf, 'w', encoding='utf8'), ensure_ascii=False)
subprocess.run([sys.executable, 'build.py'], cwd=os.path.join(R, 'tools', 'talk'), check=True)

# index.html 조각
os.makedirs(os.path.join(B, 'out'), exist_ok=True)
js = lambda s: s.replace('\\', '\\\\').replace('"', '\\"')
course = '\n'.join('    %d:"%s",' % (d, '|'.join(w['en'] for w in W if w['day'] == d)) for d in range(1, 16))
open(os.path.join(B, 'out', 'course.js'), 'w', encoding='utf8').write(course + '\n')
items = []
for w in new:
    e = ND[w['en']][1]
    items.append('{en:"%s",ko:"%s",level:2%s}' % (js(w['en']), js(w['ko']), (',emoji:"%s"' % e) if e else ''))
open(os.path.join(B, 'out', 'wb.js'), 'w', encoding='utf8').write('WORD_BANK.push(' + ', '.join(items) + ');\n')
def norm(s): return set(x.strip() for x in re.split(r'[,·/;]', re.sub(r'\(.*?\)', '', s)) if x.strip())
ko = {w['en']: w['ko'] for w in W if w['en'] in wb and not (norm(wb[w['en']]) & norm(w['ko']))}
open(os.path.join(B, 'out', 'g56ko.js'), 'w', encoding='utf8').write('const G56KO = ' + json.dumps(ko, ensure_ascii=False, separators=(',', ':')) + ';\n')
alb = {}
for w in new: alb.setdefault(ND[w['en']][2], []).append(w['en'].replace(' ', '_'))
open(os.path.join(B, 'out', 'album.js'), 'w', encoding='utf8').write(
    '\n'.join('if(DEX_ADD.%s!=null) DEX_ADD.%s += " %s"; else DEX_ADD.%s="%s";' % (a, a, ' '.join(v), a, ' '.join(v)) for a, v in alb.items()) + '\n')
print('words', len(W), 'new', len(new), 'dex added', added, 'talk', len(talk_lines), 'ko override', len(ko))
