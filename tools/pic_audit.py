#!/usr/bin/env python3
"""(v634) 헷갈리는 그림 찾기 — 유치원·G1-2 (level 1) 그림 단어 중
① 같은 그림을 다른 단어도 쓰는 것  ② 직접 그린 그림(assets/words, WIMG)이 없는 것만 뽑아 표로.
쓰기: python3 tools/pic_audit.py [out.md]"""
import re, sys, collections, os
s = open(os.path.join(os.path.dirname(__file__), "..", "index.html"), encoding="utf-8").read()
W = re.findall(r'\{en:"([^"]+)",ko:"([^"]*)",level:(\d),emoji:"([^"]+)"', s)
wimg = set(re.findall(r'"\d+\|([a-z ]+)":\["', s.split("const WIMG = {",1)[1].split("};",1)[0]))
by = collections.defaultdict(list)
for en, ko, lv, em in W: by[em].append((en, ko, int(lv)))
rows = []
for em, L in by.items():
    l1 = [x for x in L if x[2] <= 1]
    if not l1 or len(L) < 2: continue
    for en, ko, lv in l1:
        if en in wimg: continue
        others = [f"{o[0]}({o[1]})" for o in L if o[0] != en]
        rows.append((len(others), em, en, ko, ", ".join(others[:6])))
rows.sort(key=lambda r: (-r[0], r[2]))
out = ["# 헷갈리는 그림 — 유치원·G1-2 단어 (같은 그림을 다른 단어도 씀)", "",
       f"직접 그린 그림이 이미 있는 단어({len(wimg)}개)는 뺐어요. 위에서부터 그리면 효과가 커요.", "",
       "| 그림 | 단어 | 뜻 | 같은 그림을 쓰는 다른 단어 |", "|---|---|---|---|"]
out += [f"| {em} | **{en}** | {ko} | {oth} |" for n, em, en, ko, oth in rows]
txt = "\n".join(out) + "\n"
if len(sys.argv) > 1: open(sys.argv[1], "w", encoding="utf-8").write(txt)
print(f"{len(rows)} words", file=sys.stderr); print(txt[:1500])
