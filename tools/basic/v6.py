"""노션 보카 v6 (챗지피티 최종 프롬프트) → 검사 · 게임 자료.

  python3 tools/basic/v6.py check  DAY01.md [DAY02.md …] [--level L3]
  python3 tools/basic/v6.py apply  DAY01.md [DAY02.md …] [--level L3] [--day-from-name]

DAYnn.md = 노션 DAY 페이지를 그대로 옮긴 글. 안에 [표 1] 학습 표(17칸), [표 2] 게임 대화 표(6칸), 자기 점검 줄이 있다.
표는 마크다운(| … |)이든 노션 <table>이든 읽는다.

check : ❌ 꼭 고칠 것 / ⚠️ 확인할 것 / 수치(과거·전치사 비율 …) 를 보여 준다. 자료는 바꾸지 않는다.
apply : check 에서 ❌ 가 없으면
  · data/bex.json      — 단어마다 x(예문 2, 3번째 칸 = 뜻 번호), P(품사·뜻·설명 줄), f(변하는 모양), c(자주 쓰는 말), g(어려운 말 뜻)
  · data/dex<권>.json   — D[0] 설명 1 · D[1] 품사 · D[2] 모양 · D[3] 예문(앞에) · D[6] 자주 쓰는 말 · D[7] o/s · D[8] 헷갈리는 말 · D[10] 품사별 뜻
  · tools/talk/v6.txt  — word|A|B|A해석 / B해석|상황  (talk/build.py 가 이 파일을 먼저 읽어 단어마다 앞에 둔다)
  을 고친다. 게임 코드는 바꾸지 않는다 (COURSE·WORD_BANK 에 없는 새 단어는 목록만 알려 줌).
"""
import json, os, re, sys, html
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H1 = ["영어","품사 1","뜻 1","설명 1","품사 2","뜻 2","설명 2","예문 1","해석 1","예문 2","해석 2","예문 2 뜻","변하는 모양","자주 쓰는 말","비슷한 말","반대말","헷갈리는 말"]
H2 = ["영어","상황","A","B","A 해석","B 해석"]
POS = {"명사","동사","형용사","부사","전치사","접속사","대명사","조동사","감탄사","표현"}
NAMES = {"Minsu","Jiho","Yuna","Tom","Amy","Mina"}
LEN_EX = {"L1":(4,8),"L2":(5,10),"L3":(7,14),"L4":(8,16)}
LEN_TALK = {"L1":(3,7),"L2":(5,10),"L3":(5,10),"L4":(7,14)}      # 대화는 한 단계 쉽게
CAPOK = set("I Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March April May June July August September October November December "
            "Korea Korean English Seoul Busan America American Africa African Asia China Chinese Japan Japanese Europe India Australia German Germany France French Easter Christmas Halloween "
            "Mr Mrs Ms Dr OK TV Dad Mom Grandma Grandpa Mother Father".split())
FUNC = set("""a an the and or but so because if when while although though since until after before as than then that this these those it its it's i me my mine you your yours he him his she her hers we us our ours they them their theirs
is am are was were be been being do does did done doing have has had having will would can could shall should may might must not no yes don't doesn't didn't isn't aren't wasn't weren't can't won't
to of in on at by for with from into onto about over under up down out off through during without within between among around near behind above below across along toward towards
what who whom whose which where why how there here very too also just only still even again ever never always often usually sometimes all some any many much more most few little each every other another
one two three four five six seven eight nine ten first second third last next many lot lots s t""".split())
PREP_RE = re.compile(r"\b(at|on|in|for|during|since|until|before|after|from|to|into|through|between|among|by)\s+(the|a|an|my|our|his|her|their|your|this|that|\d|one|two|three|four|five|six|seven|eight|nine|ten|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december|spring|summer|fall|autumn|winter|noon|night|school|home|class|lunch|breakfast|dinner|work)\b", re.I)
PAST_SIG = re.compile(r"\b(yesterday|last (night|week|month|year|summer|winter|weekend|monday|tuesday|wednesday|thursday|friday|saturday|sunday|time)|\w+ (days?|weeks?|months?|years?) ago)\b", re.I)
PAST_AUX = re.compile(r"\b(was|were|did|didn't|had)\b", re.I)

def cells_md(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")): return None
    return [c.strip() for c in s[1:-1].split("|")]

def tables(text):
    """마크다운 · 노션 <table> 둘 다 → [[행…]…]"""
    out = []
    if "<table" in text:
        for t in re.findall(r"<table.*?</table>", text, re.S):
            rows = []
            for tr in re.findall(r"<tr.*?</tr>", t, re.S):
                cs = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
                rows.append(cs)
            out.append(rows)
    cur = []
    for ln in text.splitlines():
        c = cells_md(ln)
        if c is None:
            if cur: out.append(cur); cur = []
            continue
        if all(re.fullmatch(r":?-{2,}:?", x or "--") for x in c): continue
        cur.append(c)
    if cur: out.append(cur)
    return out

def pick(text):
    T1 = T2 = None
    for t in tables(text):
        if not t: continue
        h = [x.replace(" ", "") for x in t[0]]
        if "품사1" in h and T1 is None: T1 = t
        elif "상황" in h and T2 is None: T2 = t
    hard = ""
    m = re.search(r"어려운 말\s*[:：]\s*(.+)", text)
    if m: hard = m.group(1).strip()
    return T1, T2, hard

def words(s): return re.findall(r"[A-Za-z']+", s)
def wre(en): return re.compile(r"(?<![A-Za-z'-])" + re.escape(en) + r"(?![A-Za-z'-])", re.I)
def infl_re(en):
    b = re.escape(en)
    if " " in en: return wre(en)
    stem = re.escape(en[:-1]) if len(en) > 3 and en[-1] in "ey" else b
    return re.compile(r"(?<![A-Za-z'-])(" + b + r"|" + stem + r"[a-z]{0,4}|" + b + r"[a-z]{0,4})(?![A-Za-z'-])", re.I)

def gloss(s):
    """'laboratory (실험실), analyze (분석하다)' → {laboratory: 실험실}"""
    g = {}
    for m in re.finditer(r"([A-Za-z][A-Za-z' -]*?)\s*\(([^)]+)\)", s or ""):
        g[m.group(1).strip().lower()] = m.group(2).strip()
    return g

def known_words():
    h = open(os.path.join(R, "index.html"), encoding="utf8").read()
    K = set(m.group(1).lower() for m in re.finditer(r'\{en:"([^"]+)"', h))
    return K

def base_forms(tok):
    t = tok.lower().strip("'")
    c = {t}
    for suf, rep in (("ies","y"),("ied","y"),("es",""),("s",""),("ed",""),("ed","e"),("d",""),("ing",""),("ing","e"),("er",""),("est",""),("ly",""),("'s","")):
        if t.endswith(suf) and len(t) > len(suf)+2: c.add(t[:-len(suf)] + rep)
    if re.search(r"([bdgmnprt])\1(ed|ing)$", t): c.add(re.sub(r"([bdgmnprt])\1(ed|ing)$", r"\1", t))
    return c

def check(path, level, K):
    text = open(path, encoding="utf8").read()
    T1, T2, hard = pick(text)
    bad, warn, info = [], [], {}
    if not T1: return {"bad":["[표 1] 학습 표(품사 1 칸이 있는 표)를 못 찾음"], "warn":[], "info":{}, "rows":[], "talk":[], "gloss":{}}
    hd = T1[0]
    if [x.replace(" ","") for x in hd] != [x.replace(" ","") for x in H1]: bad.append("표 1 칸 이름·순서가 다름: " + " / ".join(hd))
    rows = []
    for i, r in enumerate(T1[1:], 1):
        if len(r) != 17: bad.append(f"표 1 {i}줄 칸 수 {len(r)} (17이어야 함): {r[:1]}"); continue
        d = dict(zip(H1, r)); rows.append(d)
        en = d["영어"]; tag = f"{en}: "
        for k, v in d.items():
            if v == "": bad.append(tag + f"'{k}' 칸이 비었음 (—로)")
        if d["품사 1"] not in POS: bad.append(tag + f"품사 1 '{d['품사 1']}'")
        if d["품사 2"] not in POS | {"—"}: bad.append(tag + f"품사 2 '{d['품사 2']}'")
        if d["품사 2"] == d["품사 1"]: bad.append(tag + "품사 2가 품사 1과 같음")
        for pk, mk in (("품사 1","뜻 1"),("품사 2","뜻 2")):
            p, m = d[pk], d[mk]
            if p == "—" or m == "—": continue
            items = [x.strip() for x in re.split(r"[,，]", m) if x.strip()]
            if len(items) > 2: warn.append(tag + f"{mk} 뜻이 {len(items)}개 (2개까지)")
            dv = [x for x in items if re.search(r"다$", x)]
            if p == "동사" and len(dv) < len(items): bad.append(tag + f"{mk} '{m}' — 동사인데 '~다'가 아닌 뜻이 섞임 (품사 섞임?)")
            if p == "명사" and dv: bad.append(tag + f"{mk} '{m}' — 명사인데 '~다' 뜻이 섞임 (품사 섞임?)")
            if any(len(x) > 10 for x in items): warn.append(tag + f"{mk} 뜻이 김")
        if d["품사 2"] != "—" and "—" in (d["뜻 2"], d["설명 2"]): bad.append(tag + "품사 2가 있는데 뜻 2·설명 2가 —")
        if d["품사 2"] == "—" and (d["뜻 2"] != "—" or d["설명 2"] != "—"): bad.append(tag + "품사 2가 —인데 뜻 2·설명 2가 있음")
        for k in ("설명 1","설명 2"):
            if d[k] != "—" and len(d[k]) > 32: warn.append(tag + f"{k} {len(d[k])}자 (25자 안쪽)")
        ir = infl_re(en)
        for k in ("예문 1","예문 2"):
            s = d[k]
            if not ir.search(s): bad.append(tag + f"{k}에 목표 단어가 없음: {s}")
            n = len(words(s)); lo, hi = LEN_EX.get(level, (4, 16))
            if n < lo or n > hi: warn.append(tag + f"{k} {n}단어 ({level} {lo}~{hi})")
        if d["예문 2 뜻"] not in ("1","2"): bad.append(tag + f"예문 2 뜻 '{d['예문 2 뜻']}' (1·2)")
        if d["품사 2"] != "—" and d["예문 2 뜻"] != "2": warn.append(tag + "품사 2가 있는데 예문 2 뜻이 1")
        if d["품사 1"] == "동사" and d["예문 2 뜻"] != "2" and level in ("L3","L4") and wre(en).search(d["예문 2"]) and not re.search(r"\b(will|didn't|did|to)\s+" + re.escape(en) + r"\b", d["예문 2"], re.I):
            warn.append(tag + "동사인데 예문 2가 원형 그대로 (과거형으로?)")
        if d["품사 1"] == "동사" and not wre(en).search(d["예문 1"]) and not re.search(r"\b" + re.escape(en) + r"(s|es)\b", d["예문 1"], re.I) and " " not in en:
            warn.append(tag + "예문 1이 원형이 아님 (기본 빈칸 문제를 못 만듦)")
        if "→" in d["변하는 모양"]: bad.append(tag + "변하는 모양에 화살표")
        if d["품사 1"] == "동사" and d["변하는 모양"] != "—":
            g = d["변하는 모양"].split(" / ")[0]; g = re.sub(r"^(명사|동사|형용사)\s+", "", g)
            if len([x for x in g.split("·") if x.strip()]) != 4: bad.append(tag + f"동사 모양이 4개가 아님: {d['변하는 모양']}")
        if d["자주 쓰는 말"] != "—":
            cs = [c for c in d["자주 쓰는 말"].split(" · ") if c.strip()]
            if len(cs) != 2: warn.append(tag + f"자주 쓰는 말 {len(cs)}개")
            for c in cs:
                if not infl_re(en).search(c): warn.append(tag + f"자주 쓰는 말에 목표 단어 없음: {c}")
                if "(" not in c: warn.append(tag + f"자주 쓰는 말에 한국어 뜻 없음: {c}")
        for k in ("예문 1","예문 2"):
            for nm in re.findall(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]+)\b", d[k]):
                if nm not in NAMES and nm not in CAPOK and nm.lower() != en.lower(): warn.append(tag + f"{k} 대문자 낱말 '{nm}' (허용 이름·고유명사?)")
        for k in ("해석 1","해석 2"):
            if re.search(r"[A-Za-z]{3,}", d[k]) and not re.search(r"[가-힣]", d[k]): bad.append(tag + f"{k}이 한국어가 아님")
    words_set = [d["영어"] for d in rows]
    # 대화
    talk = []
    if not T2: bad.append("[표 2] 게임 대화 표(상황 칸이 있는 표)를 못 찾음")
    else:
        if [x.replace(" ","") for x in T2[0]] != [x.replace(" ","") for x in H2]: bad.append("표 2 칸 이름·순서가 다름: " + " / ".join(T2[0]))
        cnt = {}
        for i, r in enumerate(T2[1:], 1):
            if len(r) != 6: bad.append(f"표 2 {i}줄 칸 수 {len(r)} (6이어야 함)"); continue
            d = dict(zip(H2, r)); talk.append(d); en = d["영어"]; tag = f"{en} 대화: "
            cnt[en] = cnt.get(en, 0) + 1
            if en not in words_set: bad.append(tag + "표 1에 없는 단어")
            n = len(wre(en).findall(d["A"] + " \n " + d["B"]))
            if n != 1: bad.append(tag + f"목표 단어(원형)가 {n}번: A '{d['A']}' / B '{d['B']}'")
            if n == 0 and infl_re(en).search(d["A"] + " " + d["B"]): bad.append(tag + "목표 단어가 변한 꼴로 들어감")
            lo, hi = LEN_TALK.get(level, (3, 14))
            for k in ("A","B"):
                nn = len(words(d[k]))
                if nn < lo or nn > hi: warn.append(tag + f"{k} {nn}단어 ({level} 대화 {lo}~{hi})")
            sl = len(d["상황"].replace(" ", ""))
            if sl < 5 or sl > 16: warn.append(tag + f"상황 {sl}자 (6~15자): {d['상황']}")
            if wre(en).search(d["상황"]): bad.append(tag + "상황에 정답 영어 단어가 있음")
            others = [o for o in words_set if o != en and len(o) > 2 and wre(o).search(d["A"] + " " + d["B"])]
            if others: warn.append(tag + f"같은 DAY 다른 목표 단어: {', '.join(others)} (빈칸에 들어가도 말이 되면 고치기)")
            if re.match(r"^(yes|no|ok|okay)[,.!]?\s*(i do|that's nice|i think so)?[.!]?$", d["B"].strip(), re.I): bad.append(tag + f"단서 없는 대답: {d['B']}")
        for en in words_set:
            if cnt.get(en, 0) != 2: bad.append(f"{en}: 대화 {cnt.get(en,0)}개 (2개)")
    # 비율 (L3·L4)
    ex = [(d["영어"], d[k]) for d in rows for k in ("예문 1","예문 2")]
    past = [s for _, s in ex if PAST_SIG.search(s) or PAST_AUX.search(s) or re.search(r"\b\w{3,}ed\b", s)]
    prep = [s for _, s in ex if PREP_RE.search(s)]
    tpast = {}
    for d in talk:
        if re.search(r"\b(did|didn't|was|were|yesterday|ago|last)\b", d["A"] + " " + d["B"], re.I) or re.search(r"\b\w{3,}ed\b", d["A"] + " " + d["B"]): tpast[d["영어"]] = 1
    info = {"단어": len(rows), "대화": len(talk), "과거 예문": f"{len(past)}/{len(ex)} ({round(100*len(past)/max(1,len(ex)))}%)",
            "시간 말 있는 과거 예문": sum(1 for s in past if PAST_SIG.search(s)), "전치사구 예문": f"{len(prep)}/{len(ex)} ({round(100*len(prep)/max(1,len(ex)))}%)",
            "과거 대화가 있는 단어": f"{len(tpast)}/{len(rows)}"}
    if level in ("L3","L4"):
        if len(past) < 0.4*len(ex): warn.append(f"과거 예문 {info['과거 예문']} — 40% 이상")
        if len(prep) < 0.5*len(ex): warn.append(f"전치사구 예문 {info['전치사구 예문']} — 절반 이상")
        miss = [en for en in words_set if en not in tpast]
        if miss: warn.append(f"과거 대화가 없는 단어 {len(miss)}개: {', '.join(miss[:8])}")
    # 어려운 말 (모르는 낱말)
    G = gloss(hard); unk = {}
    tw = set(w.lower() for w in words_set)
    for d in rows:
        for k in ("예문 1","예문 2"):
            for t in words(d[k]):
                tl = t.lower()
                if tl in FUNC or tl in tw or any(b in K or b in tw for b in base_forms(t)) or t in NAMES or t in CAPOK: continue
                unk.setdefault(tl, []).append(d["영어"])
    if level == "L4":
        nog = [u for u in unk if u not in G and not any(b in G for b in base_forms(u))]
        if nog: warn.append(f"게임 단어장에 없는 낱말인데 '어려운 말'에 없음: {', '.join(sorted(nog)[:20])}")
    elif unk:
        warn.append(f"게임 단어장에 없는 낱말 (학년보다 어려울 수 있음): {', '.join(sorted(unk)[:20])}")
    info["단어장에 없는 낱말"] = len(unk)
    return {"bad": bad, "warn": warn, "info": info, "rows": rows, "talk": talk, "gloss": G}

def report(path, res):
    print(f"\n== {os.path.basename(path)}")
    print("  " + " · ".join(f"{k} {v}" for k, v in res["info"].items()))
    for b in res["bad"]: print("  ❌", b)
    for w in res["warn"]: print("  ⚠️", w)
    if not res["bad"] and not res["warn"]: print("  ✅ 문제 없음")

def apply(results):
    bexf = os.path.join(R, "data", "bex.json"); bex = json.load(open(bexf, encoding="utf8"))
    dex = {b: json.load(open(os.path.join(R, "data", f"dex{b}.json"), encoding="utf8")) for b in (1, 2, 3)}
    html_ = open(os.path.join(R, "index.html"), encoding="utf8").read()
    lvl = {}
    for m in re.finditer(r'\{en:"([^"]+)",ko:"[^"]*"[^}]*?level:(\d)', html_): lvl.setdefault(m.group(1), int(m.group(2)))
    talk_lines, newwords = [], []
    for res in results:
        for d in res["rows"]:
            en = d["영어"]; key = en.lower()
            P = [[d["품사 1"], d["뜻 1"], d["설명 1"]]] + ([[d["품사 2"], d["뜻 2"], d["설명 2"]]] if d["품사 2"] != "—" else [])
            x = [[d["예문 1"], d["해석 1"], 1], [d["예문 2"], d["해석 2"], int(d["예문 2 뜻"]) if d["예문 2 뜻"] in ("1","2") else 1]]
            g = {k: v for k, v in res["gloss"].items() if any(re.search(r"\b" + re.escape(k) + r"\w*\b", e[0], re.I) for e in x)}
            b = bex.get(key, {}); b.update({"x": x, "P": P, "p": "·".join(p[0] for p in P), "v": 6})
            b.pop("m", None); b.pop("a", None)
            if d["변하는 모양"] != "—": b["f"] = d["변하는 모양"]
            if d["자주 쓰는 말"] != "—": b["c"] = d["자주 쓰는 말"]
            if g: b["g"] = g
            bex[key] = b
            book = lvl.get(key)
            if book is None: newwords.append(key); book = 2
            book = min(3, max(1, book))
            D = None
            for bb in (1, 2, 3):
                if key in dex[bb]: D = dex[bb][key]; book = bb; break
            if D is None: D = ["", "", "", [], "", "", "", {}, "", ""]
            while len(D) < 11: D.append("" if len(D) != 10 else [])
            D[0] = d["설명 1"]; D[1] = "·".join(p[0] for p in P)
            if d["변하는 모양"] != "—": D[2] = d["변하는 모양"]
            old = [e for e in (D[3] or []) if e and e[0] not in (x[0][0], x[1][0])]
            D[3] = [[e[0], e[1], e[2]] for e in x] + old[:1]
            if d["자주 쓰는 말"] != "—": D[6] = d["자주 쓰는 말"]
            rel = dict(D[7] or {})
            if d["비슷한 말"] != "—": rel["s"] = d["비슷한 말"]
            if d["반대말"] != "—": rel["o"] = d["반대말"]
            D[7] = rel
            if d["헷갈리는 말"] != "—": D[8] = "헷갈리지 마요: " + d["헷갈리는 말"]
            elif str(D[8]).startswith("다른 뜻"): D[8] = ""          # 품사별 뜻(D[10])으로 보여 주므로
            D[10] = P
            dex[book][key] = D
        for t in res["talk"]:
            for k in ("A","B","A 해석","B 해석","상황"): assert "|" not in t[k]
            talk_lines.append("|".join([t["영어"].lower(), t["A"], t["B"], t["A 해석"] + " / " + t["B 해석"], t["상황"]]))
    json.dump(bex, open(bexf, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
    for bb in (1, 2, 3): json.dump(dex[bb], open(os.path.join(R, "data", f"dex{bb}.json"), "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
    tf = os.path.join(R, "tools", "talk", "v6.txt")
    old = [l.rstrip("\n") for l in open(tf, encoding="utf8")] if os.path.exists(tf) else ["# 노션 v6 대화 — word|A|B|A해석 / B해석|상황 (tools/basic/v6.py apply)"]
    have = {l.split("|")[0] for l in talk_lines}
    keep = [l for l in old if l.startswith("#") or l.split("|")[0] not in have]
    open(tf, "w", encoding="utf8").write("\n".join(keep + talk_lines) + "\n")
    import subprocess; subprocess.run([sys.executable, "build.py"], cwd=os.path.join(R, "tools", "talk"), check=True)
    print(f"\n적용: 단어 {sum(len(r['rows']) for r in results)} · 대화 {len(talk_lines)}")
    if newwords: print("게임 단어장(WORD_BANK)에 없는 단어 — 손으로 넣어야 함:", ", ".join(sorted(set(newwords))))

def main():
    a = sys.argv[1:]
    if not a or a[0] not in ("check", "apply"): print(__doc__); sys.exit(1)
    level = "L3"
    if "--level" in a: level = a[a.index("--level") + 1]
    files = [x for x in a[1:] if x.endswith((".md", ".txt", ".html"))]
    K = known_words(); res = []
    for f in files:
        r = check(f, level, K); report(f, r); res.append(r)
    nbad = sum(len(r["bad"]) for r in res)
    print(f"\n합계: ❌ {nbad} · ⚠️ {sum(len(r['warn']) for r in res)}")
    if a[0] == "apply":
        if nbad: print("❌ 가 있어 적용하지 않음"); sys.exit(2)
        apply(res)

if __name__ == "__main__":
    main()
