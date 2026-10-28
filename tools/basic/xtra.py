"""(v442) 노션 보카 v2.1 추가분 → data/xtra.json
   tools/basic/v6/junior/x/DAYnn.md ([표 3] 추가 단어 표 · [짧은 글 1] · [짧은 글 2], 노션에서 그대로 옮김)
   + tools/basic/v6/junior/DAYnn.md ([표 1] 변하는 모양 — 모양 바꿔 쓰기 보기)

   python3 tools/basic/xtra.py check   — ❌ 꼭 고칠 것 · ⚠️ 확인할 것 (자료는 안 바꿈)
   python3 tools/basic/xtra.py apply   — ❌ 줄은 빼고 data/xtra.json 을 씀

   xtra.json = {"w": {영어: {"d":DAY, "fam":[[영어,한국어]…], "idm":[숙어,한국어], "pre":숙어 빈칸 앞, "post":뒤,
                            "hint":영어 힌트, "fs":[바뀐 모양 예문, 해석], "form":바뀐 모양, "fpre","fpost", "fopt":[보기 4]}},
                "st": {DAY: [ {"t":[제목,한국어], "ws":[쓴 단어], "s":[[문장,해석]…], "ox":[[문장,해석,참?,근거]…],
                               "tc":[제목 3, 정답 0번], "sm":[요약 3, 정답 0번], "q":[질문,한국어], "ex":[예시 답,해석]} … ]}}
"""
import json, os, re, sys, glob
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XD = os.path.join(R, "tools/basic/v6/junior/x"); MD = os.path.join(R, "tools/basic/v6/junior")
OUT = os.path.join(R, "data/xtra.json")

def rows(text, head):
    """'## head' 아래 첫 표 → [dict]"""
    i = text.find("## " + head)
    if i < 0: return None
    L = [l.strip() for l in text[i:].split("\n")[1:]]
    T = []
    for l in L:
        if l.startswith("## "): break
        if not l.startswith("|"):
            if T: break
            continue
        c = [x.strip() for x in l.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", x) for x in c): continue
        T.append(c)
    if not T: return None
    H = T[0]; return [dict(zip(H, r)) for r in T[1:]]

def dash(x): x = (x or "").strip(); return "" if x in ("—", "-", "–", "") else x
PAIR = re.compile(r"^\s*(.+?)\s*\(([^()]*)\)\s*$")
def pairs(cell):
    out = []
    for it in re.split(r"\s+·\s+", dash(cell)):
        m = PAIR.match(it)
        if m: out.append([m.group(1).strip(), m.group(2).strip()])
    return out

def forms_of(cell):
    """[표 1] 변하는 모양 칸 → 모양들 (품사 이름 빼고)"""
    s = dash(cell); out = []
    for part in re.split(r"\s*/\s*", s):
        part = re.sub(r"^(명사|동사|형용사|부사)\s+", "", part.strip())
        for f in re.split(r"\s*·\s*", part):
            f = f.strip()
            if f and f != "—" and re.fullmatch(r"[A-Za-z][A-Za-z' -]*", f): out.append(f)
    return out

def wre(w): return re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", re.I)

def t1(day):
    """v6/junior/DAYnn.md 의 [표 1] ('품사 1'·'변하는 모양' 칸이 있는 표) → {영어: 줄}"""
    p = os.path.join(MD, "DAY%02d.md" % day)
    if not os.path.exists(p): return {}
    out, H = {}, None
    for l in open(p, encoding="utf8").read().split("\n"):
        if not l.startswith("|"): H = None if out else H; continue
        c = [x.strip() for x in l.strip("|").split("|")]
        if "품사 1" in c and "변하는 모양" in c: H = c; continue
        if H and len(c) == len(H) and not all(re.fullmatch(r":?-{2,}:?", x) for x in c): d = dict(zip(H, c)); out[d["영어"]] = d
    return out

def build():
    bad, warn, W, ST = [], [], {}, {}
    for p in sorted(glob.glob(os.path.join(XD, "DAY*.md"))):
        day = int(re.search(r"DAY(\d+)", p).group(1)); text = open(p, encoding="utf8").read(); T1 = t1(day)
        tag = "DAY%02d" % day
        X = rows(text, "[표 3] 추가 단어 표")
        if X is None: warn.append(f"{tag}: [표 3] 없음")
        for r in X or []:
            en = r.get("영어", "").strip()
            if not en: continue
            o = {"d": day}; w1 = T1.get(en)
            if not w1: warn.append(f"{tag} {en}: [표 1]에 없는 단어 (표 1 은 v6/junior/{tag}.md)")
            fam = [f for f in pairs(r.get("가족 단어")) if f[0].lower() != en.lower()]
            if dash(r.get("가족 단어")) and not fam: bad.append(f"{tag} {en}: 가족 단어 형식(영어 (한국어)) 아님 — {r.get('가족 단어')}")
            for f in fam:
                if not re.fullmatch(r"[A-Za-z][A-Za-z'-]*", f[0]): warn.append(f"{tag} {en}: 가족 단어가 한 낱말이 아님 — {f[0]} (짝 문제에서 뺌)")
            fam = [f for f in fam if re.fullmatch(r"[A-Za-z][A-Za-z'-]*", f[0])]
            if fam: o["fam"] = fam
            idm = pairs(r.get("숙어"))
            if dash(r.get("숙어")):
                if not idm: bad.append(f"{tag} {en}: 숙어 형식 아님 — {r.get('숙어')}")
                else:
                    ph, ko = idm[0]; m = wre(en).search(ph)
                    if not m: warn.append(f"{tag} {en}: 숙어에 목표 단어가 원형으로 없음 — {ph} (빈칸 문제에서 뺌)"); o["idm"] = [ph, ko]
                    else: o["idm"] = [ph, ko]; o["pre"] = ph[:m.start()]; o["post"] = ph[m.end():]
            h = dash(r.get("영어 힌트"))
            if h:
                if wre(en).search(h): bad.append(f"{tag} {en}: 영어 힌트에 목표 단어가 있음 — {h}")
                elif any(wre(f[0]).search(h) for f in fam): warn.append(f"{tag} {en}: 영어 힌트에 가족 단어 — {h}"); o["hint"] = h
                else: o["hint"] = h
            fs, fk = dash(r.get("바뀐 모양 예문")), dash(r.get("바뀐 모양 해석"))
            if fs:
                F = forms_of((w1 or {}).get("변하는 모양", ""))
                hit = None
                for f in sorted(set(F), key=len, reverse=True):
                    if f.lower() == en.lower(): continue
                    m = wre(f).search(fs)
                    if m: hit = (f, m); break
                if not fk: bad.append(f"{tag} {en}: 바뀐 모양 해석 없음")
                elif not hit:
                    if wre(en).search(fs): warn.append(f"{tag} {en}: 바뀐 모양 예문에 원형만 있음 — {fs}")
                    else: warn.append(f"{tag} {en}: 바뀐 모양 예문에서 변하는 모양({', '.join(F) or '—'})을 못 찾음 — {fs}")
                else:
                    f, m = hit; got = fs[m.start():m.end()]
                    opts = [got] + [x for x in dict.fromkeys([en] + F) if x.lower() != got.lower()]
                    # 보기 = 바뀐 모양 + 원형 + [표 1] 의 다른 모양 (가짜 철자는 만들지 않음 — 명사는 단수/복수 둘만일 수 있음)
                    o.update({"fs": [fs, fk], "form": got, "fpre": fs[:m.start()], "fpost": fs[m.end():], "fopt": opts[:4]})
            W[en] = o
        # 짧은 글
        for k in (1, 2, 3):
            S = rows(text, "[짧은 글 %d]" % k)
            if S is None: continue
            it = {r.get("항목", "").strip(): r for r in S}
            st = {"s": []}
            t = it.get("제목")
            if not t: bad.append(f"{tag} 짧은 글 {k}: 제목 없음"); continue
            st["t"] = [t["영어"], dash(t.get("한국어"))]
            st["ws"] = [x.strip() for x in re.split(r"\s*,\s*", dash((it.get("쓴 단어") or {}).get("영어", ""))) if x.strip()]
            n = 1
            while ("문장 %d" % n) in it: r = it["문장 %d" % n]; st["s"].append([r["영어"], dash(r.get("한국어"))]); n += 1
            if len(st["s"]) < 3: bad.append(f"{tag} 짧은 글 {k}: 문장이 {len(st['s'])}개"); continue
            if len(st["s"]) != 6: warn.append(f"{tag} 짧은 글 {k}: 중등 6문장인데 {len(st['s'])}문장")
            nw = sum(len(x[0].split()) for x in st["s"])
            if not 60 <= nw <= 100: warn.append(f"{tag} 짧은 글 {k}: {nw}단어 (70~90)")
            for w in st["ws"]:
                if w not in T1 and w not in W: warn.append(f"{tag} 짧은 글 {k}: 쓴 단어 {w} 가 이 DAY 단어가 아님")
            st["ox"] = []
            for j in (1, 2, 3):
                r = it.get("OX %d" % j)
                if not r: continue
                m = re.match(r"^\s*([OX○×])\s*[·.]?\s*(\d+)?", r.get("답", ""))
                if not m: bad.append(f"{tag} 짧은 글 {k} OX {j}: 답 형식 — {r.get('답')}"); continue
                st["ox"].append([r["영어"], dash(r.get("한국어")), m.group(1) in "O○", int(m.group(2) or 0)])
            for key, nm in (("tc", "제목 고르기"), ("sm", "요약 고르기")):
                r = it.get(nm)
                if not r: continue
                L = [x.strip() for x in re.split(r"\s+/\s+", r["영어"]) if x.strip()]
                a = int(re.sub(r"\D", "", r.get("답", "1")) or 1) - 1
                if len(L) != 3 or not 0 <= a < 3: bad.append(f"{tag} 짧은 글 {k} {nm}: 보기 3개·답 번호 — {r['영어'][:60]} | {r.get('답')}"); continue
                st[key] = [L[a]] + [x for i, x in enumerate(L) if i != a]   # 정답이 맨 앞 (게임이 섞음)
            q = it.get("생각 질문"); e = it.get("예시 답")
            if q: st["q"] = [q["영어"], dash(q.get("한국어"))]
            if e: st["ex"] = [e["영어"], dash(e.get("한국어"))]
            if not st["ox"]: warn.append(f"{tag} 짧은 글 {k}: OX 없음")
            ST.setdefault(str(day), []).append(st)
    return W, ST, bad, warn

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    W, ST, bad, warn = build()
    print(f"단어 {len(W)} · 가족 {sum(1 for o in W.values() if 'fam' in o)} · 숙어 {sum(1 for o in W.values() if 'pre' in o)} · 영어 힌트 {sum(1 for o in W.values() if 'hint' in o)} · 모양 바꿔 쓰기 {sum(1 for o in W.values() if 'form' in o)} · 짧은 글 {sum(len(v) for v in ST.values())}편 ({len(ST)} DAY)")
    for b in bad: print("❌", b)
    for w in warn[:80]: print("⚠️", w)
    if len(warn) > 80: print(f"⚠️ … {len(warn)-80}개 더")
    if cmd == "apply":
        json.dump({"w": W, "st": ST}, open(OUT, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
        print("→", OUT, os.path.getsize(OUT), "bytes")
