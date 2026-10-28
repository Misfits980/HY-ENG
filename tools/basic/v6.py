"""노션 보카 v6 (챗지피티 최종 프롬프트) → 검사 · 게임 자료.

  python3 tools/basic/v6.py check  DAY01.md [DAY02.md …] [--level L3]
  python3 tools/basic/v6.py apply  DAY01.md [DAY02.md …] [--level L3] [--day N] [--no-course]
        (DAY 번호는 파일 이름 DAYnn 에서. listen/JLnn.md = 🎧 중등 리스닝 Stage nn (L4 규칙, 과 jl, 새 단어 src jl). L1=G1-2 1단계 · L2=G3-4 2단계 · L3=G5-6 3단계 · L4=중등 voca — 과 목록·교재 뜻·새 단어는 tools/words/auto.json → sync.py)

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
POS = {"명사","동사","형용사","부사","전치사","접속사","대명사","조동사","감탄사","표현","동사 과거형","접두사"}   # (v388 semi)  (v322) 동사 과거형 = found '찾았다 (find)' 처럼 다른 동사의 지난 꼴
TALK_SENSE = {}   # (v322) v6/talk_sense.txt — 프롬프트 규칙(대화 2 = 품사 2 뜻)을 안 지킨 대화의 실제 뜻 품사
_tsf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v6", "talk_sense.txt")
if os.path.exists(_tsf):
    for _l in open(_tsf, encoding="utf8"):
        _l = _l.strip()
        if _l and not _l.startswith("#"): _w, _a, _p = _l.split("|"); TALK_SENSE[(_w.strip().lower(), _a.strip())] = _p.strip()
SAME_POS_OK ={"work","post","back","party","keep","view"}   # (v322) 같은 품사인데 뜻이 정말 다른 단어 (일/작품, 우편/게시물, 등/뒤 …) — 같은 품사 두 줄 ⚠️ 에서 뺌
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
PAST_AUX = re.compile(r"\b(was|were|did|didn't|had|wasn't|weren't|hadn't)\b", re.I)   # (v286) wasn't·weren't 도 과거

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
    """같은 종류 표가 여러 개(1~15번 · 16~20번)면 이어 붙인다"""
    T1 = T2 = None
    for t in tables(text):
        if not t: continue
        t = [[re.sub(r"^\*\*(.*)\*\*$", r"\1", c.strip()).strip() for c in r] for r in t]   # **굵게** 벗기기
        h = [x.replace(" ", "") for x in t[0]]
        if "품사1" in h: T1 = t if T1 is None else T1 + t[1:]
        elif "상황" in h: T2 = t if T2 is None else T2 + t[1:]
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
    IRR = {"cannot":"can","can't":"can","won't":"will","don't":"do","doesn't":"do","isn't":"be","aren't":"be","is":"be","are":"be","am":"be","was":"be","were":"be",
           "has":"have","had":"have","does":"do","did":"do","went":"go","goes":"go","made":"make","took":"take","came":"come","saw":"see","ate":"eat","got":"get","gave":"give",
           "ran":"run","sat":"sit","told":"tell","said":"say","felt":"feel","left":"leave","bought":"buy","brought":"bring","thought":"think","found":"find","children":"child","feet":"foot","teeth":"tooth","men":"man","women":"woman","mice":"mouse"}
    if t in IRR: c.add(IRR[t])
    for suf, rep in (("ies","y"),("ied","y"),("es",""),("s",""),("ed",""),("ed","e"),("d",""),("ing",""),("ing","e"),("er",""),("est",""),("ly",""),("'s","")):
        if t.endswith(suf) and len(t) > len(suf)+1: c.add(t[:-len(suf)] + rep)
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
            dv = [x for x in items if re.search(r"다$", x) and not re.search(r"바다$", x)]   # (v285) 바다·큰 바다는 명사
            if p == "동사" and len(dv) < len(items): bad.append(tag + f"{mk} '{m}' — 동사인데 '~다'가 아닌 뜻이 섞임 (품사 섞임?)")
            if p == "명사" and dv: bad.append(tag + f"{mk} '{m}' — 명사인데 '~다' 뜻이 섞임 (품사 섞임?)")
            if any(len(x) > 10 for x in items): warn.append(tag + f"{mk} 뜻이 김")
        if d["품사 2"] != "—" and "—" in (d["뜻 2"], d["설명 2"]): bad.append(tag + "품사 2가 있는데 뜻 2·설명 2가 —")
        if d["품사 2"] == "—" and (d["뜻 2"] != "—" or d["설명 2"] != "—"): bad.append(tag + "품사 2가 —인데 뜻 2·설명 2가 있음")
        for k in ("설명 1","설명 2"):
            if d[k] != "—" and len(d[k]) > 32: warn.append(tag + f"{k} {len(d[k])}자 (25자 안쪽)")
        ir = infl_re(en)
        # (v314) 불규칙 모양(stole·kept·rose …)은 '변하는 모양' 칸에 적힌 꼴도 목표 단어로 친다
        fm = {x.lower() for x in re.findall(r"[A-Za-z][A-Za-z'-]*", d["변하는 모양"]) if " " not in en}
        fre = re.compile(r"(?<![A-Za-z'-])(" + "|".join(re.escape(x) for x in sorted(fm, key=len, reverse=True)) + r")(?![A-Za-z'-])", re.I) if fm else None
        for k in ("예문 1","예문 2"):
            s = d[k]
            if not ir.search(s) and not (fre and fre.search(s)):
                if re.search(r"(?<![A-Za-z'-])" + re.escape(en) + r"'s\b", s, re.I): warn.append(tag + f"{k}: 목표 단어가 ~'s 꼴 (빈칸 문제에서 빠질 수 있음): {s}")   # (v443) puppet's
                else: bad.append(tag + f"{k}에 목표 단어가 없음: {s}")
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
            gs = d["변하는 모양"].split(" / "); g = next((x for x in gs if x.startswith("동사 ")), gs[0]); g = re.sub(r"^(명사|동사|형용사)\s+", "", g)   # (v443) '명사 … / 동사 …' 순서여도 동사 칸
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
    mean1 = {d["영어"]: d["뜻 1"] for d in rows}
    # 대화
    talk = []
    if not T2: bad.append("[표 2] 게임 대화 표(상황 칸이 있는 표)를 못 찾음")
    else:
        if [x.replace(" ","") for x in T2[0]] != [x.replace(" ","") for x in H2]: bad.append("표 2 칸 이름·순서가 다름: " + " / ".join(T2[0]))
        cnt = {}; oth = []
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
            # (v283) 📍 상황은 문제와 함께 보이므로 정답의 한국어 뜻이 들어가면 답을 알려 주는 셈
            for m in re.split(r"[,·]", mean1.get(en, "")):
                m = re.sub(r"\(.*?\)|~", "", m).strip(); m = re.sub(r"(하다|다|의|한|운|은|는|적인)$", "", m).strip()
                if len(m) >= 2 and m in d["상황"]: warn.append(tag + f"상황에 정답 뜻 '{m}'이 보임 (답을 알려 줌): {d['상황']}")
            others = [o for o in words_set if o != en and len(o) > 2 and wre(o).search(d["A"] + " " + d["B"])]
            if others: oth.append(en)   # (v281) 게임이 대화 줄에 나온 단어를 보기에서 빼므로 경고 대신 숫자만
            if re.match(r"^(yes|no|ok|okay)[,.!]?\s*(i do|that's nice|i think so)?[.!]?$", d["B"].strip(), re.I): bad.append(tag + f"단서 없는 대답: {d['B']}")
        for en in words_set:
            if cnt.get(en, 0) != 2: bad.append(f"{en}: 대화 {cnt.get(en,0)}개 (2개)")
    # 비율 (L3·L4)
    ex = [(d["영어"], d[k]) for d in rows for k in ("예문 1","예문 2")]
    past = [s for _, s in ex if PAST_SIG.search(s) or PAST_AUX.search(s) or re.search(r"\b\w{3,}ed\b", s)]
    prep = [s for _, s in ex if PREP_RE.search(s)]
    tpast = {}
    for d in talk:
        if re.search(r"\b(did|didn't|was|were|wasn't|weren't|yesterday|ago|last)\b", d["A"] + " " + d["B"], re.I) or re.search(r"\b\w{3,}ed\b", d["A"] + " " + d["B"]): tpast[d["영어"]] = 1
    info = {"단어": len(rows), "대화": len(talk), "과거 예문": f"{len(past)}/{len(ex)} ({round(100*len(past)/max(1,len(ex)))}%)",
            "시간 말 있는 과거 예문": sum(1 for s in past if PAST_SIG.search(s)), "전치사구 예문": f"{len(prep)}/{len(ex)} ({round(100*len(prep)/max(1,len(ex)))}%)",
            "과거 대화가 있는 단어": f"{len(tpast)}/{len(rows)}"}
    if talk and oth: info["다른 목표 단어가 든 대화 (보기에서 자동으로 뺌)"] = len(oth)
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
                if len(tl) < 2 or any(tl in re.split(r"[- ]", w) for w in tw): continue
                if tl in FUNC or tl in tw or any(b in K or b in tw for b in base_forms(t)) or t in NAMES or t in CAPOK or t.split("'")[0] in NAMES: continue
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

RAW = {"L1": "kinder", "L2": "basic", "L3": "elem", "L4": "mv1"}      # 원본 과 이름 (COURSE)
SETK = {"L1": "basic", "L2": "elem", "L3": "g56", "L4": "mv1"}       # 게임 반 (교재 뜻 COURSE_KO)
LVL = {"L1": 1, "L2": 1, "L3": 2, "L4": 3}                            # 게임 단어 레벨 (★)
# (v322) 점검: 앨범 짐작이 자주 틀림 (일몰·칼날→time, 젓가락·찬장→food, 땅콩·올리브→mind2, 예약→body) →
#        ① 뜻(ko)으로 먼저 짐작하고 설명은 그다음 ② 음식·시간을 먼저 ③ '해·날·달·번·약' 같은 한 글자 낱말은 빼고 낱말을 더 넣음
ALB_KW = [("food", "음식|과일|채소|먹을|마시는|음료|빵|요리$|맛$|간식|과자|열매|콩$|땅콩|호두|올리브|코코넛|카카오|고기|치즈|소스|국수|쌀"),
          ("time", "시간|시각|요일|날짜|달력|아침|저녁|오전|오후|계절|세기|숫자|번째|순서|[가-힣]색$|^색"),
          ("animal", "동물|곤충|새끼|물고기|짐승|뱀|벌레|날개|꼬리|새$"),
          ("body", "몸|병$|질병|아프|건강|약품|알약|치료|증상|뼈|피부|상처|눈썹|눈알|안구|손목|발목|머리$|하품|질식|복용|바이러스|백신|청력|혈액|격리|검역"),
          ("home", "물건|가구|옷|도구|가방|상자|그릇|용기|의자|침대|매트리스|젓가락|숟가락|찬장|수납|냉동|냉장|세제|끈|장화|부츠|신발|모자|재킷|컴퓨터|기기|밸브|구슬|소포|굴뚝|히터|난방"),
          ("people", "사람|직업|가족|선수|요정|인어|어부|상인|주의자|[가-힣]자$|꾼$"), ("school", "학교|공부|수업|과목|책$|시험|고사|학기|글$|[가-힣]학$|평가|비평|설명|묘사"),
          ("play", "운동|놀이|경기|악기|공연|게임|노래|그림"),
          ("nature", "자연|날씨|하늘|바다|산$|강$|식물|꽃|나무|돌$|흙|번개|햇빛|햇살|서리|일몰|해 질|수성|행성|별$|눈$|비$"),
          ("place", "장소|곳$|건물|가게|탈것|자동차|자전거|유람선|트랙터|교통|배$|비행기|길$|도시|인도|보도|운하|수로|주택|거주|마을|캠프장|야영지|지붕|탑$|진료소|하수"),
          ("society", "나라|사회|돈|회사|뉴스|법$|정부|문화|대륙|예약|약속|무기|요금|협회|허가|허락|회의|모임|노동|출판|비자|입국")]
# (v322) 두 뜻이 같은 뜻인지 — 게임 index.html 의 koSame() 과 같은 규칙 (뜻 조각의 꼬리 '하다·한·의…'를 떼고 같거나 2글자 이상이 서로 들어 있으면)
KO_SUF = re.compile(r"(스러운|적인|하다|하는|되다|해요|한|된|다|의|은|는|운|색|이|로)$")
def ko_parts(k): return [y for y in (re.sub(r"[\s~·.…]", "", re.sub(r"\([^)]*\)", "", x)) for x in re.split(r"[,;/]", k or "")) if y]
def ko_stem(p):
    s = KO_SUF.sub("", p); return s if len(s) >= 2 else p
def ko_same(a, b):
    A = [ko_stem(x) for x in ko_parts(a)]; B = [ko_stem(x) for x in ko_parts(b)]
    return any(x == y or (len(x) >= 2 and len(y) >= 2 and (x in y or y in x)) for x in A for y in B)
ALB_CONCRETE ={"food", "animal", "body", "home", "nature", "place"}   # 설명 글로는 이것만 짐작 ('사람'·'시간'은 설명에 너무 자주 나옴)
def guess_album(pos, ko, expl, level):
    if pos == "동사": return ("act2" if level <= 2 else "act3"), False
    if pos in ("형용사", "부사"): return ("feel1" if level <= 1 else "feel2"), False
    parts = [re.sub(r"\(.*?\)", "", x).strip() for x in re.split(r"[,，]", ko) if x.strip()]
    for a, kw in ALB_KW:               # 뜻 조각으로 먼저
        if any(re.search(kw, p) for p in parts): return a, True
    for a, kw in ALB_KW:               # 없으면 설명으로 (구체적인 앨범만)
        if a in ALB_CONCRETE and re.search(kw, expl): return a, True
    return ("mind1" if level <= 1 else "mind2"), True

def to_auto(results, levels, days):
    """auto.json 에 과 단어 순서 · 교재 뜻 · 새 단어(+앨범)를 넣고 sync.py"""
    AF = os.path.join(R, "tools", "words", "auto.json"); A = json.load(open(AF, encoding="utf8"))
    h = open(os.path.join(R, "index.html"), encoding="utf8").read()
    base = h.split("/* AUTO-WORDS-BEGIN")[0] + h.split("/* AUTO-WORDS-END */")[-1]
    wb = {}
    for m in re.finditer(r'\{en:"([^"]+)",ko:"([^"]*)"', base): wb.setdefault(m.group(1), m.group(2))
    for en, w in A.get("words", {}).items(): wb.setdefault(en, w["ko"])
    wb0 = dict(wb)
    norm =lambda s: set(x.strip() for x in re.split(r"[,·/;]", re.sub(r"\(.*?\)", "", s)) if x.strip())
    A.setdefault("course", {}); A.setdefault("ko", {}); A.setdefault("words", {}); A.setdefault("album", [])
    have = {en for _, en in A["album"]}; added, guessed = [], []
    for res, lv, day in zip(results, levels, days):
        if day is None: print("⚠️ DAY 번호를 몰라 과 목록에 넣지 않음 (파일 이름 DAYnn 또는 --day)"); continue
        jl = lv == "JL"; lv = "L4" if jl else lv          # (v314) 🎧 중등 리스닝 = L4 규칙 · 자기 과(jl) · src jl
        raw, setk = ("jl", "jl") if jl else (RAW[lv], SETK[lv])
        if lv == "L4" and not jl and int(day) <= 35: raw = setk = "mv0"   # (v443) 중등 voca 1 = Junior DAY 1~35 · voca 2(mv1) = DAY 36~70
        ws = [d["영어"].lower() for d in res["rows"]]
        A["course"].setdefault(raw, {})[str(day)] = ws
        ko = {}
        for d in res["rows"]:
            en = d["영어"].lower(); m1 = d["뜻 1"]
            # (v394) 중등(L4·리스닝): 단어장 뜻에 없는 뜻 조각이 md 뜻 1 에 있어도 교재 뜻으로 (nut 견과 → '견과, 너트' — 예문이 가르치는 뜻이 화면에 보이게)
            #        초등 반은 단어장의 쉬운 뜻을 그대로 (사발·조 같은 어려운 말이 늘지 않게)
            if en in wb and (not (norm(wb[en]) & norm(m1)) or (lv == "L4" and any(not ko_same(p, wb[en]) for p in ko_parts(m1)))): ko[en] = m1
            if en not in wb:
                A["words"][en] = {"ko": m1, "level": LVL[lv], "emoji": ""}
                if lv == "L4": A["words"][en]["src"] = "jl" if jl else "mv1"
                wb[en] = m1; added.append(en)
                if en not in have:
                    alb, g = guess_album(d["품사 1"], m1, d["설명 1"], LVL[lv]); A["album"].append([alb, en]); have.add(en)
                    if g: guessed.append(f"{en}→{alb}")
        if ko: A["ko"].setdefault(setk, {})[str(day)] = ko
        else: A["ko"].get(setk, {}).pop(str(day), None)
    # (v322) 단어장 뜻이나 다른 반 교재 뜻(COURSE_KO)이 새 품사별 뜻(P)에 하나도 없으면 알림 — 게임은 그 Stage 에서 v6 예문·대화를 안 씀
    #        (mean: 단어장 '의미하다' ↔ 리스닝 '못된'만 → 다른 뜻 예문으로 문제가 나왔다). 원본 md 에 그 뜻 품사 줄을 넣을 것.
    bex = json.load(open(os.path.join(R, "data", "bex.json"), encoding="utf8")); lost = []
    for res in results:
        for d in res["rows"]:
            en = d["영어"].lower(); P = (bex.get(en) or {}).get("P") or []
            olds = [("단어장", wb0.get(en))] + [(f"{s} {dy}", m.get(en)) for s, D in A["ko"].items() for dy, m in D.items()]
            for where, k in olds:
                if k and P and not any(ko_same(k, p[1]) for p in P) and (en, k) not in [(x[0], x[2]) for x in lost]: lost.append((en, where, k, " / ".join(p[1] for p in P)))
    for en, where, k, ps in lost: print(f"⚠️ 기존 뜻 사라짐: {en} — {where} '{k}' 이(가) 새 뜻에 없음 ({ps})")
    json.dump(A, open(AF, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    import subprocess; subprocess.run([sys.executable, os.path.join(R, "tools", "words", "sync.py")], check=True)
    if added: print("새 게임 단어 %d개: %s" % (len(added), ", ".join(added)))
    if guessed: print("앨범을 뜻으로 짐작한 단어 (확인):", ", ".join(guessed))

def apply(results):
    bexf = os.path.join(R, "data", "bex.json"); bex = json.load(open(bexf, encoding="utf8"))
    dex = {b: json.load(open(os.path.join(R, "data", f"dex{b}.json"), encoding="utf8")) for b in (1, 2, 3)}
    html_ = open(os.path.join(R, "index.html"), encoding="utf8").read()
    lvl = {}
    for m in re.finditer(r'\{en:"([^"]+)",ko:"[^"]*"[^}]*?level:(\d)', html_): lvl.setdefault(m.group(1), int(m.group(2)))
    talk_lines, newwords, done = [], [], {}
    talk_rows = []   # (v322) [줄 칸들, 단어, 그 대화의 뜻 (품사, 뜻)] — 끝에 합친 P 에서 몇 번째 뜻인지 찾는다
    for res in results:
        rowP = {}
        for d in res["rows"]:
            en = d["영어"]; key = en.lower()
            P = [[d["품사 1"], d["뜻 1"], d["설명 1"]]] + ([[d["품사 2"], d["뜻 2"], d["설명 2"]]] if d["품사 2"] != "—" else [])
            rowP[key] = [p[:2] for p in P]
            x = [[d["예문 1"], d["해석 1"], 1], [d["예문 2"], d["해석 2"], int(d["예문 2 뜻"]) if d["예문 2 뜻"] in ("1","2") else 1]]
            if key in done:   # (v281) 같은 단어가 다른 DAY 에 또 나옴 (back: 등 → 뒤) — 뜻·예문을 합친다 (뒤 DAY 가 앞 DAY 를 덮지 않게)
                P0, x0 = done[key]; idx = {}
                for i, sp in enumerate(P, 1):
                    parts = lambda m: [t.strip() for t in m.split(",") if t.strip()]
                    j = next((k for k, q in enumerate(P0, 1) if q[0] == sp[0] and set(parts(q[1])) & set(parts(sp[1]))), None)
                    if j is None: P0.append(sp); j = len(P0)
                    else: P0[j-1] = [P0[j-1][0], ", ".join(dict.fromkeys(parts(P0[j-1][1]) + parts(sp[1]))), P0[j-1][2]]
                    idx[i] = j
                x = x0 + [[e[0], e[1], idx.get(e[2], 1)] for e in x if e[0] not in [y[0] for y in x0]]
                order = sorted(range(len(P0)), key=lambda i: ([q[0] for q in P0].index(P0[i][0]), i))   # 같은 품사끼리 붙여서 (명사 등 · 명사 뒤 · 부사)
                new = {o + 1: n + 1 for n, o in enumerate(order)}
                P = [P0[o] for o in order]; x = [[e[0], e[1], new.get(e[2], 1)] for e in x]
            done[key] = (P, x)
            g = {k: v for k, v in res["gloss"].items() if any(re.search(r"\b" + re.escape(k) + r"\w*\b", e[0], re.I) for e in x)}
            b = bex.get(key, {}); b.update({"x": x, "P": P, "p": "·".join(dict.fromkeys(p[0] for p in P)), "v": 6})
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
            D[0] = P[0][2]; D[1] = "·".join(dict.fromkeys(p[0] for p in P))
            if d["변하는 모양"] != "—": D[2] = d["변하는 모양"]
            old = [e for e in (D[3] or []) if e and e[0] not in (x[0][0], x[1][0])]
            old.sort(key=lambda e: len(e) > 2)   # (v322) 뜻 번호가 없는 예전 사전 예문(We cycle to school.)을 먼저 남김 — 바뀐 v6 예문 찌꺼기 말고
            # (v394) 예전 사전 예문은 더 남기지 않음 — 뜻 번호가 없고 짧아서 ("I see a ___.", 톱 saw 수업에 "I ___ a rainbow.") 다른 보기도 정답이 됐다 (단어 QA)
            D[3] = [[e[0], e[1], e[2]] for e in x[:4]]
            if d["자주 쓰는 말"] != "—": D[6] = d["자주 쓰는 말"]
            rel = dict(D[7] or {})
            if d["비슷한 말"] != "—": rel["s"] = d["비슷한 말"]
            if d["반대말"] != "—": rel["o"] = d["반대말"]
            D[7] = rel
            if d["헷갈리는 말"] != "—": D[8] = "헷갈리지 마요: " + d["헷갈리는 말"]
            elif str(D[8]).startswith("다른 뜻"): D[8] = ""          # 품사별 뜻(D[10])으로 보여 주므로
            D[10] = P
            dex[book][key] = D
        nth = {}
        for t in res["talk"]:
            for k in ("A","B","A 해석","B 해석","상황"): assert "|" not in t[k]
            key = t["영어"].lower(); nth[key] = nth.get(key, 0) + 1; rp = rowP.get(key) or [["", ""]]
            # (v322) 대화의 뜻 — 프롬프트 규칙: 대화 1 = 품사 1 의 뜻, 품사 2 가 있으면 대화 2 = 품사 2 의 뜻 (게임이 Stage 뜻과 맞는 대화만 쓰게)
            #        규칙을 안 지킨 대화는 v6/talk_sense.txt 에 (단어|A 앞부분|품사)
            sp = rp[1] if nth[key] == 2 and len(rp) > 1 else rp[0]
            fix = next((p for (w, a), p in TALK_SENSE.items() if w == key and t["A"].startswith(a)), None)
            if fix:
                m = [q for q in rp if q[0] == fix]
                if m: sp = m[0]
                else: print(f"⚠️ talk_sense.txt: {key} '{fix}' 품사가 그 DAY 줄에 없음")
            talk_rows.append(([key, t["A"], t["B"], t["A 해석"] + " / " + t["B 해석"], t["상황"]], key, sp))
    parts = lambda m: [s.strip() for s in m.split(",") if s.strip()]
    for cells, key, sp in talk_rows:
        P = done[key][0]
        j = next((k for k, q in enumerate(P, 1) if q[0] == sp[0] and set(parts(q[1])) & set(parts(sp[1]))), 1)
        talk_lines.append("|".join(cells + [str(j)]))
    # (v322) 같은 품사 뜻이 두 줄로 갈림 (뜻 이름이 조금 달라 합쳐지지 않음: '(몸을) 떨다' / '떨다') → 원본 md 뜻을 맞출 것
    for key, (P, _) in done.items():
        ps = [p[0] for p in P]
        if len(ps) != len(set(ps)) and key not in SAME_POS_OK: print(f"⚠️ 같은 품사 뜻 두 줄: {key} — " + " / ".join(p[0] + " " + p[1] for p in P))
    json.dump(bex, open(bexf, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
    for bb in (1, 2, 3): json.dump(dex[bb], open(os.path.join(R, "data", f"dex{bb}.json"), "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
    tf = os.path.join(R, "tools", "talk", "v6.txt")
    old = [l.rstrip("\n") for l in open(tf, encoding="utf8")] if os.path.exists(tf) else ["# 노션 v6 대화 — word|A|B|A해석 / B해석|상황 (tools/basic/v6.py apply)"]
    have = {l.split("|")[0] for l in talk_lines}
    keep = [l for l in old if l.startswith("#") or l.split("|")[0] not in have]
    open(tf, "w", encoding="utf8").write("\n".join(keep + talk_lines) + "\n")
    import subprocess; subprocess.run([sys.executable, "build.py"], cwd=os.path.join(R, "tools", "talk"), check=True)
    print(f"\n적용: 단어 {sum(len(r['rows']) for r in results)} · 대화 {len(talk_lines)}")

def main():
    a = sys.argv[1:]
    if not a or a[0] not in ("check", "apply"): print(__doc__); sys.exit(1)
    # (v285) --level 이 여러 번 나오면 그 뒤 파일들에 그 레벨을 쓴다 (단계가 다른 파일을 한 번에 적용 → 겹치는 단어의 뜻·예문·대화를 합침).
    #        --level 이 한 번이면 예전처럼 모든 파일에 적용.
    nlv = a.count("--level"); level = "L3"; flv = []
    if nlv == 1: level = a[a.index("--level") + 1]
    cur = level
    for i, x in enumerate(a[1:], 1):
        if x == "--level" and nlv > 1: cur = a[i + 1]
        elif x.endswith((".md", ".txt", ".html")): flv.append((x, cur))
    files = [f for f, _ in flv]
    K = known_words(); res = []
    for f, lv in flv:
        r = check(f, lv, K); report(f, r); res.append(r)
    nbad = sum(len(r["bad"]) for r in res)
    print(f"\n합계: ❌ {nbad} · ⚠️ {sum(len(r['warn']) for r in res)}")
    if a[0] == "apply":
        if nbad: print("❌ 가 있어 적용하지 않음"); sys.exit(2)
        apply(res)
        days = []
        for f in files:
            m = re.search(r"(?:DAY|JL)\s*0*(\d+)", os.path.basename(f), re.I)
            days.append(int(a[a.index("--day") + 1]) if "--day" in a else (int(m.group(1)) if m else None))
        kinds = ["JL" if re.match(r"JL\d+", os.path.basename(f), re.I) else lv for f, lv in flv]   # (v314) listen/JLnn.md = 중등 리스닝 Stage nn
        if "--no-course" not in a: to_auto(res, kinds, days)

if __name__ == "__main__":
    main()
