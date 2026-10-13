#!/usr/bin/env python3
"""HY ENG 단어 검사기 — 챗지피티가 만든 노션 표(마크다운)를 게임에 넣기 전에 검사한다.

쓰는 법:  python3 tools/wordcheck.py 표.md [--html index.html] [--json 결과.json] [--report 보고서.md]
표 형식 (claude/hy-eng-chatgpt-word-prompt.md 2단계):
  ## 출처 (예: 보카 Basic 16 / 리스닝 Starter 2권 5과)
  | 영어 | 대표 뜻 | 다른 뜻 | 품사 | 예문 1 | 해석 1 | 예문 2 | 해석 2 |

검사 등급
  ❌ 꼭 고칠 것  — 칸 빠짐, ❓ 남음, 철자 사전에 없음, 예문에 그 단어가 없음, 해석 없음
  ⚠️ 확인할 것  — 뜻 너무 김, 품사와 뜻 꼴이 안 맞음, 예문 길이, 고유명사·사람 이름, 조심할 낱말,
                  예문 철자, 예문에 게임에 없는 단어가 많음, 챗지피티가 붙인 뜻(*)
  ℹ️ 참고      — 이미 게임에 있는 단어(뜻 비교), 같은 대표 뜻을 가진 단어, 제안 레벨
철자 사전: /usr/share/hunspell/en_US.dic (+ .aff 접사 규칙으로 변화형까지 펼침) + 게임 단어
뜻이 맞는지·예문이 자연스러운지는 스크립트가 못 본다 → Claude가 표를 직접 읽고 한 번 더 본다.
"""
import re, sys, json, os, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
DIC = "/usr/share/hunspell/en_US"

# ── 불규칙 동사 (원형 과거 과거분사) — 예문에 단어가 들어 있는지 볼 때 쓴다
IRR = """be was were been|have had had|do did done|go went gone|come came come|get got gotten got|make made made|take took taken|see saw seen|know knew known|give gave given|find found found|think thought thought|tell told told|become became become|leave left left|feel felt felt|bring brought brought|begin began begun|keep kept kept|hold held held|write wrote written|stand stood stood|hear heard heard|let let let|mean meant meant|set set set|meet met met|run ran run|pay paid paid|sit sat sat|speak spoke spoken|lie lay lain|lead led led|read read read|grow grew grown|lose lost lost|fall fell fallen|send sent sent|build built built|understand understood understood|draw drew drawn|break broke broken|spend spent spent|cut cut cut|rise rose risen|drive drove driven|buy bought bought|wear wore worn|choose chose chosen|seek sought sought|throw threw thrown|catch caught caught|deal dealt dealt|win won won|forget forgot forgotten|lay laid laid|sell sold sold|fight fought fought|bite bit bitten|hide hid hidden|eat ate eaten|drink drank drunk|sing sang sung|swim swam swum|ring rang rung|fly flew flown|blow blew blown|teach taught taught|sleep slept slept|feed fed fed|hurt hurt hurt|put put put|shut shut shut|hit hit hit|cost cost cost|beat beat beaten|shake shook shaken|steal stole stolen|wake woke woken|freeze froze frozen|forgive forgave forgiven|ride rode ridden|shine shone shone|shoot shot shot|sink sank sunk|spin spun spun|stick stuck stuck|sting stung stung|strike struck struck|swing swung swung|tear tore torn|bend bent bent|bleed bled bled|dig dug dug|hang hung hung|light lit lit|slide slid slid|spill spilled spilt|split split split|spread spread spread|sweep swept swept|weep wept wept|wind wound wound|bear bore born|lend lent lent|bet bet bet|quit quit quit|upset upset upset|overcome overcame overcome|withdraw withdrew withdrawn|undergo underwent undergone|seek sought sought|flee fled fled|kneel knelt knelt|leap leapt leapt|dream dreamt dreamt|burn burnt burnt|learn learnt learnt|smell smelt smelt|spell spelt spelt|prove proved proven|show showed shown|sew sewed sewn|saw sawed sawn|mistake mistook mistaken|grind ground ground|creep crept crept|weave wove woven|tread trod trodden|stink stank stunk|spit spat spat|forbid forbade forbidden|arise arose arisen|awake awoke awoken|bind bound bound|breed bred bred|cling clung clung|lean leant leant"""
IRREG = {}
for part in IRR.split("|"):
    ws = part.split(); IRREG.setdefault(ws[0], set()).update(ws[1:])

FUNC = set("""a an the and or but so if then than because when while after before until since though although as of to in on at by for with from up down out off over under into onto about around through across along near between behind beside without within upon
i you he she it we they me him her us them my your his its our their mine yours hers ours theirs this that these those there here who what where when why how which whose whom
is am are was were be been being do does did done have has had having will would can could shall should may might must not no yes don't doesn't didn't can't won't isn't aren't wasn't weren't i'm you're he's she's it's we're they're i've let's that's there's what's
very too also just only still even really much many more most some any all every each both other another one two three four five six seven eight nine ten first last next
oh hi hello please thank thanks okay ok wow""".split())

NAMES_OK = set("Minsu Jiho Yuna Tom Amy I Mom Dad Mr Mrs Ms Korea Korean Seoul Busan Jeju English Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March April May June July August September October November December Christmas Earth".split())
CAREFUL = set("kill killed kills die died dies dead death blood bloody gun guns shoot bomb war kiss kissed sexy beer wine drunk cigarette cigarettes smoke smoking stupid idiot hate ugly fat dumb hell damn god".split())
POS_OK = {"명사","동사","형용사","부사","전치사","접속사","대명사","감탄사","표현","수사","한정사"}

def load_dict():
    """hunspell .dic + .aff → 변화형까지 펼친 소문자 낱말 집합"""
    sfx, pfx = {}, {}
    try:
        for line in open(DIC+".aff", encoding="utf-8"):
            p = line.split()
            if len(p) >= 5 and p[0] in ("SFX","PFX"):
                strip = "" if p[2]=="0" else p[2]; add = "" if p[3]=="0" else p[3].split("/")[0]
                cond = p[4]; rx = re.compile((cond+"$") if p[0]=="SFX" else ("^"+cond)) if cond!="." else None
                (sfx if p[0]=="SFX" else pfx).setdefault(p[1], []).append((strip, add, rx))
    except FileNotFoundError: pass
    out = set()
    try:
        for i, line in enumerate(open(DIC+".dic", encoding="utf-8")):
            if i == 0: continue
            w, _, fl = line.strip().partition("/"); lw = w.lower(); out.add(lw)
            made = [lw]
            for f in fl:
                for strip, add, rx in sfx.get(f, []):
                    if (rx is None or rx.search(lw)) and lw.endswith(strip): made.append(lw[:len(lw)-len(strip)]+add)
            out.update(made)
            for f in fl:                                   # 앞붙이 × 뒷붙이 (dis+appoint+ed)
                for strip, add, rx in pfx.get(f, []):
                    for m in made: out.add(add+m)
    except FileNotFoundError: pass
    return out

def load_bank(html):
    """index.html 의 WORD_BANK → {en: {ko, level}}"""
    t = open(html, encoding="utf-8").read()
    a = t.index("const WORD_BANK = ["); b = t.index("\n];", a)
    bank = {}
    for m in re.finditer(r'\{en:"([^"]+)",ko:"([^"]*)",level:(\d)', t[a:b]):
        bank.setdefault(m.group(1), {"ko": m.group(2), "level": int(m.group(3))})
    return bank

def forms(word):
    """단어 하나의 변화형 (규칙 + 불규칙)"""
    w = word.lower(); s = {w, w+"s", w+"es", w+"ed", w+"d", w+"ing", w+"er", w+"est", w+"ly"}
    if w.endswith("e"): s |= {w[:-1]+"ing", w[:-1]+"ed", w[:-1]+"er", w[:-1]+"est"}
    if w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou": s |= {w[:-1]+"ies", w[:-1]+"ied", w[:-1]+"ier", w[:-1]+"iest", w[:-1]+"ily"}
    if re.search(r"[^aeiou][aeiou][bdgmnprt]$", w): s |= {w+w[-1]+"ing", w+w[-1]+"ed", w+w[-1]+"er", w+w[-1]+"est"}
    if w.endswith("f"): s.add(w[:-1]+"ves")
    if w.endswith("fe"): s.add(w[:-2]+"ves")
    s |= IRREG.get(w, set())
    return s

def has_word(sent, en):
    toks = [x.lower() for x in re.findall(r"[A-Za-z']+", sent)]
    parts = en.lower().replace("~", " ").split()
    parts = [p for p in parts if p not in ("sb", "sth", "somebody", "something", "one's")]
    if not parts: return True
    if len(parts) == 1: return any(t in forms(parts[0]) or t.rstrip("'s") in forms(parts[0]) for t in toks)
    # 표현: 첫 낱말은 변화형 허용, 나머지는 순서대로 나오기만 하면 된다
    for i, t in enumerate(toks):
        if t in forms(parts[0]):
            j = i + 1; ok = True
            for p in parts[1:]:
                while j < len(toks) and toks[j] not in forms(p): j += 1
                if j >= len(toks): ok = False; break
                j += 1
            if ok: return True
    return False

HANGUL = re.compile(r"[가-힣]")
def jong(ch):
    c = ord(ch) - 0xAC00
    return (c % 28) if 0 <= c < 11172 else -1

def parse_md(text):
    """## 출처 + 마크다운 표 → 행 목록"""
    rows, src = [], "출처 없음"
    for ln, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("#"): src = s.lstrip("#").strip() or "출처 없음"; continue
        if not s.startswith("|"): continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c or "--") for c in cells): continue
        if cells and cells[0] in ("영어", "English"): continue
        rows.append({"src": src, "line": ln, "cells": cells})
    return rows

def level_of(src):
    s = src.lower()
    if re.search(r"pre[\s-]*starter|프리", s): return 1
    if "starter" in s or "스타터" in s: return 1
    if "basic" in s or "베이직" in s: return 2
    if re.search(r"junior|주니어|high|하이|중등", s): return 3
    return 0

def check(rows, bank, dic):
    known = set(dic) | {k.lower() for k in bank}
    bank_forms = set(FUNC)
    for k in bank: bank_forms |= forms(k) if " " not in k else set(k.lower().split())
    seen, out = {}, []
    ko_index = {}
    for k, v in bank.items(): ko_index.setdefault(v["ko"], []).append(k)
    for r in rows:
        c = r["cells"] + [""] * 8
        en_raw, ko, ko2, pos, e1, k1, e2, k2 = [x.strip() for x in c[:8]]
        dup_mark = "(중복)" in en_raw
        en = re.sub(r"\s*\(중복\)\s*", "", en_raw).strip()
        lv_src = level_of(r["src"])
        item = {"src": r["src"], "line": r["line"], "en": en, "ko": ko.lstrip("*").strip(), "ko2": ko2, "pos": pos,
                "ex": [[e1, k1]] + ([[e2, k2]] if e2 else []), "err": [], "warn": [], "info": [], "level": lv_src or None}
        E, W, I = item["err"], item["warn"], item["info"]
        if len(r["cells"]) != 8: E.append(f"칸이 {len(r['cells'])}개예요 (8개여야 해요)")
        for name, v in (("영어", en), ("대표 뜻", ko), ("품사", pos), ("예문 1", e1), ("해석 1", k1)):
            if not v: E.append(f"{name} 칸이 비었어요")
        if any("❓" in x for x in c[:8]): E.append("❓ 가 남아 있어요 (사진에서 못 읽은 글자)")
        if not en: out.append(item); continue
        # 철자
        for p in re.findall(r"[A-Za-z']+", en):
            if p.lower() not in known and p.lower().strip("'") not in known: E.append(f"철자 사전에 없어요: {p}")
        if re.search(r"[^A-Za-z' \-~.]", en): W.append("영어 칸에 영어가 아닌 글자가 있어요")
        # 뜻
        if ko.startswith("*"): W.append("챗지피티가 붙인 뜻이에요 (* — 교재에 뜻이 없음): " + ko)
        kk = ko.lstrip("*").strip()
        if kk and not HANGUL.search(kk): E.append("대표 뜻이 한글이 아니에요")
        if len(kk.replace(" ", "")) > 10: W.append(f"대표 뜻이 길어요 ({len(kk.replace(' ', ''))}자) — 문 간판에 안 들어갈 수 있어요")
        if "," in kk or "/" in kk: W.append("대표 뜻에 뜻이 여러 개예요 — 첫 뜻만 대표 뜻으로, 나머지는 다른 뜻 칸으로")
        last = kk.rstrip(" .")[-1:] if kk and "❓" not in kk else ""
        pset = set(re.split(r"[·,/ ]+", pos)) - {""}
        if pset - POS_OK: W.append(f"품사 이름을 확인해 주세요: {pos}")
        p0 = pos.split("·")[0] if pos else ""
        if p0 == "동사" and last and last != "다": W.append(f"동사인데 뜻이 '~다'로 안 끝나요: {kk}")
        if p0 == "형용사" and (last == "다" or (last and jong(last) != 4 and last not in "의")): W.append(f"형용사인데 뜻이 '~한/~은' 꼴이 아니에요: {kk}")
        if p0 == "명사" and last == "다" and not kk.endswith("바다"): W.append(f"명사인데 뜻이 '~다'로 끝나요: {kk}")
        # 예문
        lo, hi = ((4, 8) if lv_src <= 1 else (6, 12))
        for n, (es, ks) in enumerate(item["ex"], 1):
            if not es: continue
            toks = re.findall(r"[A-Za-z']+", es)
            if not has_word(es, en): E.append(f"예문 {n}에 '{en}'이(가) 없어요: {es}")
            if not ks: E.append(f"예문 {n}의 해석이 없어요")
            elif not HANGUL.search(ks): E.append(f"예문 {n}의 해석이 한글이 아니에요")
            if len(toks) > hi + 1: W.append(f"예문 {n}이 길어요 ({len(toks)}단어, 이 단계는 {hi}단어까지): {es}")
            if len(toks) < 2: W.append(f"예문 {n}이 너무 짧아요 ({len(toks)}단어): {es}")
            if not re.search(r"[.!?]['\"]?$", es): W.append(f"예문 {n} 끝에 . ! ? 가 없어요")
            if es[:1].islower(): W.append(f"예문 {n}이 소문자로 시작해요")
            starts = {m.start() for m in re.finditer(r"(?:^|[.!?:;\"“”]\s*)\s*\"?([A-Za-z])", es)} | {0}
            caps = [m.group(0) for m in re.finditer(r"[A-Za-z']+", es)
                    if m.group(0)[:1].isupper() and m.start() not in starts and not any(abs(m.start()-x) <= 3 for x in starts)
                    and m.group(0) not in NAMES_OK and m.group(0).rstrip("s") not in NAMES_OK and not m.group(0).startswith("I'") and not m.group(0).isupper()]
            if caps: W.append(f"예문 {n}의 고유명사·사람 이름 확인: {', '.join(sorted(set(caps)))}")
            bad = sorted({t for t in toks if t.lower() in CAREFUL})
            if bad: W.append(f"예문 {n}에 조심할 낱말: {', '.join(bad)}")
            miss = sorted({t for t in toks if t.lower() not in known and t.lower().rstrip("'s") not in known and t not in NAMES_OK})
            if miss: W.append(f"예문 {n} 철자 확인: {', '.join(miss)}")
            target = forms(en.split()[0]) if en else set()
            hard = sorted({t.lower() for t in toks if t.lower() not in bank_forms and t.lower() not in target and t not in NAMES_OK and len(t) > 2}
                          - {p.lower() for p in en.split()})
            limit = 2 if lv_src <= 1 else 4
            if len(hard) > limit: W.append(f"예문 {n}에 게임에 없는 단어가 많아요 ({len(hard)}개): {', '.join(hard)}")
        if ko2 and e2 == "": I.append("다른 뜻이 있는데 예문 2가 없어요")
        # 이미 있음
        b = bank.get(en) or bank.get(en.lower())
        if b:
            I.append(f"이미 게임에 있어요 (★{b['level'] or '표현'} · {b['ko']})" + ("" if b["ko"] == kk else f" → 새 뜻 '{kk}'와 달라요, 다른 뜻으로 넣을지 확인"))
            item["exists"] = True
        if en.lower() in seen: W.append(f"이 표 안에서 또 나왔어요 (앞: {seen[en.lower()]})")
        seen.setdefault(en.lower(), r["src"])
        if dup_mark and not b: I.append("(중복) 표시가 있지만 게임에는 없어요")
        same = [x for x in ko_index.get(kk, []) if x != en]
        if same and not b: I.append(f"대표 뜻이 같은 게임 단어: {', '.join(same[:4])} (문제 보기에서 서로 빠져요)")
        if not lv_src: I.append("출처에서 단계를 못 찾았어요 — 레벨은 직접 정해야 해요")
        if " " in en or pos == "표현": item["level"] = 0 if pos == "표현" else item["level"]
        out.append(item)
    return out

def report(items):
    n = len(items); ne = sum(1 for x in items if x["err"]); nw = sum(1 for x in items if x["warn"] and not x["err"])
    new = sum(1 for x in items if not x.get("exists"))
    L = [f"# 단어 검사 보고서", "", f"- 단어 {n}개 (새 단어 {new}개 · 이미 게임에 있음 {n-new}개)",
         f"- ❌ 꼭 고칠 것: {ne}개 · ⚠️ 확인할 것: {nw}개 · ✅ 문제 없음: {n-ne-nw}개", ""]
    for title, key in (("❌ 꼭 고칠 것", "err"), ("⚠️ 확인할 것", "warn"), ("ℹ️ 참고", "info")):
        rows = [x for x in items if x[key]]
        if not rows: continue
        L += [f"## {title}", ""]
        for x in rows:
            L.append(f"- **{x['en'] or '(빈칸)'}** · {x['ko']} — {x['src']} ({x['line']}째 줄)")
            L += [f"  - {m}" for m in x[key]]
        L.append("")
    return "\n".join(L)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md"); ap.add_argument("--html", default=os.path.join(HERE, "..", "index.html"))
    ap.add_argument("--json"); ap.add_argument("--report")
    a = ap.parse_args()
    items = check(parse_md(open(a.md, encoding="utf-8").read()), load_bank(a.html), load_dict())
    rep = report(items)
    if a.report: open(a.report, "w", encoding="utf-8").write(rep)
    else: print(rep)
    if a.json: json.dump(items, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(1 if any(x["err"] for x in items) else 0)
