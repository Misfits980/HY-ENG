#!/usr/bin/env python3
# (v651) 문법 문제 검사기 — data/gram.json (g34 · g56 · mid)
#   python3 tools/check_gram.py            → 전체 검사 (❌ 오류가 있으면 종료 코드 1)
#   python3 tools/check_gram.py mid        → 중등만
#   python3 tools/check_gram.py mid --sheet out.md   → 선생님이 훑어볼 「정답 문장 목록」도 만듦
# ❌ 오류 = 게임이 깨지거나 답이 틀리게 채점됨 (꼭 고침)   ⚠️ 살펴보기 = 답이 둘일 수 있거나 어색할 수 있음 (사람이 봄)
import json, os, re, sys, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = json.load(open(os.path.join(ROOT, "data", "gram.json"), encoding="utf-8"))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
SHEET = sys.argv[sys.argv.index("--sheet") + 1] if "--sheet" in sys.argv else None
BOOKS = [b for b in ("g34", "g56", "mid") if b in D and (not args or b in args)]

# 단계마다 필요한 문제 수 (index.html Gram.TIER / TIERM 과 같게)
NEED = {"g34": {"pick": 4, "ox": 2, "order": 3, "fix": 2, "hard": 3}, "g56": {"pick": 4, "ox": 2, "order": 3, "fix": 2, "hard": 3},
        "mid": {"pick": 4, "ox": 2, "order": 3, "fix": 2, "hard": 3, "write": 4}}

# 게임 단어장 (철자 틀린 단어 잡기)
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
BANK = set(w.lower() for w in re.findall(r'\{en:"([^"]+)"', html))
BANK |= set(x for w in list(BANK) for x in w.split(" "))
EXTRA = set("""a an the i you he she it we they me him her us them my your his its our their mine yours this that these those am is are was were be been
 do does did don't doesn't didn't isn't aren't wasn't weren't can't cannot won't not no yes and or but so because if when than then there here to of in on at by for with from
 about into under over after before up down out off near very too much many more most some any every all one two three four five six seven eight nine ten thirteen
 can could may might must should will would shall have has had let's let ms mr mrs kim tom mina jinsu jisu canada busan seoul jeju korea english saturday sunday saturdays
 yuna amy jiho minsu jiho's grandma grandma's kimchi sushi ramen christmas herself himself myself yourself themselves ourselves itself fluently gracefully laps
 seen forgot written spoken became known eaten broken grown taken gone given done been driven chosen stolen fallen flown thrown drawn worn hidden ridden forgotten begun sung swum drunk woken
 tv ok o'clock who what where which whose why how a.m p.m didn mall weekdays vegetarian classmate hallway onions baths twins amn't""".split())
IRR = {"went": "go", "ate": "eat", "saw": "see", "bought": "buy", "wrote": "write", "gave": "give", "met": "meet", "made": "make", "got": "get", "took": "take", "broke": "break", "came": "come",
       "knew": "know", "heard": "hear", "had": "have", "did": "do", "ran": "run", "swam": "swim", "said": "say", "told": "tell", "found": "find", "left": "leave", "slept": "sleep", "read": "read",
       "has": "have", "does": "do", "goes": "go", "is": "be", "are": "be", "am": "be", "was": "be", "were": "be", "children": "child", "people": "person", "men": "man", "women": "woman", "feet": "foot", "teeth": "tooth"}
def lemma(w):
    w = w.lower()
    if w in IRR: return IRR[w]
    for suf, rep in (("ies", "y"), ("ied", "y"), ("es", ""), ("ed", ""), ("ing", ""), ("s", ""), ("d", ""), ("er", ""), ("est", ""), ("ly", "")):
        if w.endswith(suf) and len(w) > len(suf) + 1:
            b = w[:-len(suf)] + rep
            for c in (b, b + "e", b[:-1] if len(b) > 2 and b[-1] == b[-2] else b):
                if c in BANK or c in EXTRA: return c
    return w
def known(w):
    w = w.lower().strip("'")
    for suf in ("n't", "'d", "'ll", "'re", "'ve", "'m", "'s"):
        if w.endswith(suf) and len(w) > len(suf): w = w[:-len(suf)]; break
    if len(w) <= 2 and w in ("b", "th", "st", "nd", "rd", "p", "m", "ca", "wo"): return True
    return (not w) or w.isdigit() or w in BANK or w in EXTRA or lemma(w) in BANK or lemma(w) in EXTRA or (w.endswith("'s") and known(w[:-2]))
def words(s): return re.findall(r"[A-Za-z][A-Za-z']*", s or "")

TIME = re.compile(r"\b(yesterday|ago|last|now|right now|every|always|usually|often|sometimes|never|tomorrow|next|today|tonight|this morning|at the moment|look|listen|these days|on (mon|tues|wednes|thurs|fri|satur|sun)days?|in \d{4}|when i was|soon|already|yet|just|since|for \w+ (years|days|hours))\b", re.I)
AUX_BEFORE = re.compile(r"\b(do|does|did|don't|doesn't|didn't|can|can't|could|will|won't|must|should|may|might|to|is|are|am|was|were|isn't|aren't|wasn't|weren't|let's)\s+(not\s+)?(\w+\s+)?___", re.I)
BE = {"am", "is", "are", "was", "were"}

err, warn = [], []
def E(g, q, m): err.append(f"{g['id']} 「{g['t']}」 {m}  ← {q if isinstance(q, str) else (q.get('s') or ' '.join(q.get('w', [])))}")
def Wn(g, q, m): warn.append(f"{g['id']} 「{g['t']}」 {m}  ← {q if isinstance(q, str) else (q.get('s') or ' '.join(q.get('w', [])))}")

def right(q):   # 게임 GramUI.right 과 같은 규칙 — 채점 뒤 보여 주고 읽어 주는 「정답 문장」
    k = q["k"]
    if k == "pick": return re.sub(r"\s+([.,!?])", r"\1", re.sub(r" ?___ ?", " ", q["s"], count=1)).strip() if q["a"] == "-" else q["s"].replace("___", q["a"], 1)
    if k == "ox": return q["s"] if q["ok"] else q.get("fix", "")
    if k == "order": return " ".join(q["w"])
    if k == "fix":
        st = lambda t: re.sub(r"[.,!?]", "", t)
        return " ".join(x for x in ((t.replace(q["bad"], q["a"]) if q["a"] else "") if st(t) == q["bad"] else t for t in q["s"].split(" ")) if x)
    if k == "write":
        s = re.sub(r"\s*\([^)]*\)\s*$", "", q["s"]); a = q["a"]
        return s.replace("___", a[0].upper() + a[1:] if s.startswith("___") else a, 1)
    return ""

def check_q(g, q, bk, where):
    k = q.get("k")
    if k not in ("pick", "ox", "order", "fix", "write"): return E(g, q, f"모르는 문제 종류 {k}")
    if not (q.get("ko") or "").strip(): E(g, q, "한국어 뜻(ko) 없음")
    txt = " ".join(q["w"]) if k == "order" else q.get("s", "")
    if re.search(r"[‘’“”]", json.dumps(q, ensure_ascii=False)): E(g, q, "굽은 따옴표(’ “) — 곧은 따옴표로 (자판으로 못 침)")
    if "  " in txt.replace("?  B:", "?B:") or txt != txt.strip(): Wn(g, q, "빈칸이 두 개 붙었거나 앞뒤에 빈칸")
    if k in ("pick", "write"):
        if q["s"].count("___") != 1: return E(g, q, "빈칸(___)은 꼭 하나")
    if k == "pick":
        o = q.get("o") or []
        if len(o) < 2: E(g, q, "보기가 2개보다 적음")
        if q.get("a") not in o: E(g, q, f"정답 {q.get('a')!r} 이 보기에 없음")
        if len(set(x.lower() for x in o)) != len(o): E(g, q, "같은 보기가 두 번")
        if bk == "mid" and not q.get("w"): Wn(g, q, "왜 그런지 한 줄(w) 없음")
        # 답이 둘일 수 있는지: 같은 동사의 때(시제)만 다른 보기인데 문장에 때를 알려 주는 말이 없음
        lem = set(lemma(x.split(" ")[-1]) for x in o if x != "-")
        if len(o) >= 2 and len(lem) == 1 and all(" " not in x for x in o) and not (lem & {"child", "person", "man", "woman", "foot", "tooth"}):
            forms = set(x.lower() for x in o); past = any(x in IRR and IRR[x] != "be" and x not in ("has", "does", "goes") or x.endswith("ed") for x in forms) or bool(forms & {"was", "were"})
            pres = any(not (x.endswith("ed") or (x in IRR and x not in ("has", "does", "goes", "is", "are", "am"))) for x in forms)
            fake = any(re.search(r"(eed|oed|yed|ked|ted|ned|med)$", x) and lemma(x) != x and x[:-2] in IRR.values() for x in forms)   # goed · buyed 같은 일부러 틀린 모양
            if past and pres and not fake and not any(x.endswith("ing") for x in forms) and "would" not in q["s"].lower() and not re.search(r"\b(have|has|had|and|or|than|be|been)\s+___", q["s"]) and not TIME.search(q["s"]) and not AUX_BEFORE.search(q["s"]) and not re.search(r"\b(and|but|so)\b.*\b\w+ed\b|\b\w+ed\b.*\b(and|but|so)\b", q["s"]):
                Wn(g, q, f"때를 알려 주는 말이 없음 — 보기 {o} 둘 다 될 수 있는지 확인")
        if len(o) >= 2 and set(x.lower() for x in o) <= {"can", "may", "must", "should", "will", "have to", "has to", "could", "might"}:
            Wn(g, q, f"조동사끼리 고르기 {o} — 문맥으로 하나만 되는지 확인")
        for x in o:
            if x != q.get("a") and x != "-" and x.lower() == str(q.get("a")).lower(): E(g, q, "대소문자만 다른 보기")
    elif k == "ox":
        if q["ok"] and q.get("fix"): E(g, q, "맞는 문장인데 고친 문장(fix)이 있음")
        if not q["ok"]:
            if not q.get("fix"): E(g, q, "틀린 문장인데 고친 문장(fix)이 없음")
            elif q["fix"].strip() == q["s"].strip(): E(g, q, "고친 문장이 원래 문장과 같음")
            elif abs(len(words(q["fix"])) - len(words(q["s"]))) > 2: Wn(g, q, "고친 문장이 많이 다름 — 틀린 곳이 하나인지 확인")
        if not re.search(r"[.!?]$", q["s"]): Wn(g, q, "문장 끝에 마침표·물음표 없음")
    elif k == "order":
        w = q.get("w") or []
        if len(w) < 3: E(g, q, "순서 맞추기 단어가 3개보다 적음")
        if len(w) > 9: Wn(g, q, f"순서 맞추기 단어 {len(w)}개 — 휴대폰에서 길 수 있음")
        if any(" " in t or not t for t in w): E(g, q, "단어 조각에 빈칸")
        if not re.search(r"[.!?]$", w[-1] if w else ""): Wn(g, q, "마지막 조각에 마침표·물음표 없음")
        if w and not w[0][0].isupper(): Wn(g, q, "첫 조각이 대문자가 아님 — 순서가 둘일 수 있음")
    elif k == "fix":
        toks = [re.sub(r"[.,!?]", "", t) for t in q["s"].split(" ")]
        if toks.count(q.get("bad")) != 1: E(g, q, f"틀린 단어 {q.get('bad')!r} 가 문장에 꼭 한 번 있어야 함 (지금 {toks.count(q.get('bad'))}번)")
        if q.get("a") == q.get("bad"): E(g, q, "고친 말이 틀린 말과 같음")
        if "a" not in q: E(g, q, "고친 말(a) 없음 (빼는 것이면 빈 글자)")
    elif k == "write":
        a = q.get("a", "")
        if not re.fullmatch(r"[a-z]+(?:'[a-z]+)?(?: [a-z]+(?:'[a-z]+)?)*", a): E(g, q, f"직접 쓰기 정답 {a!r} — 소문자·빈칸·' 만 (자판에 있는 글자)")
        for x in q.get("alt") or []:
            if not re.fullmatch(r"[a-z' ]+", x): E(g, q, f"다른 정답 {x!r} 글자")
            if x == a: E(g, q, "다른 정답(alt)이 정답과 같음")
        if not re.search(r"\([^)]+\)\s*$", q["s"]): E(g, q, "직접 쓰기에는 문장 끝 괄호 힌트 (go) 가 있어야 함 — 없으면 답이 여러 개")
        if len(a) > 16: Wn(g, q, f"쓸 글자가 {len(a)}자 — 휴대폰 자판으로 길 수 있음")
        if "n't" in a and not any("not" in x for x in q.get("alt") or []): Wn(g, q, "줄임말 정답인데 풀어 쓴 것(does not)이 alt 에 없음")
        if not q.get("w"): Wn(g, q, "왜 그런지 한 줄(w) 없음")
    # 철자: 정답 문장의 단어가 게임 단어장·기본 단어에 있는지 (일부러 틀린 문장은 고친 쪽으로)
    r = right(q)
    for i, w in enumerate(words(r)):
        if i and w[0].isupper(): continue   # 문장 가운데 대문자 = 이름·달·요일
        if not known(w): Wn(g, q, f"단어장에 없는 단어 「{w}」 — 철자 또는 수준 확인")
    if r and r[0].islower(): Wn(g, q, f"정답 문장이 소문자로 시작: {r}")
    if k != "order" and r and not re.search(r"[.!?]$", r.replace(".", ".").strip()): Wn(g, q, f"정답 문장 끝 부호 없음: {r}")
    return r

sheet = []
for bk in BOOKS:
    L = D[bk]; ids = [g["id"] for g in L]
    for i in set(x for x in ids if ids.count(x) > 1): err.append(f"{bk}: 같은 id 가 두 번 {i}")
    for g in L:
        if not re.fullmatch(bk + r"-\d+", g.get("id", "")): err.append(f"{bk}: id 모양 {g.get('id')}")
        for f in ("t", "emo", "sub", "cards", "qs"):
            if not g.get(f): err.append(f"{g.get('id')}: {f} 없음")
        rules = [c for c in g.get("cards", []) if c.get("k") == "rule"]
        if not rules: err.append(f"{g['id']}: 설명 카드 없음")
        for ci, c in enumerate(rules):
            if not c.get("h") or not c.get("p"): E(g, c.get("h") or "?", f"카드 {ci+1}: 제목·설명 없음")
            if not c.get("ex"): E(g, c.get("h", "?"), f"카드 {ci+1}: 예문 없음")
            for e in c.get("ex", []):
                if len(e) != 4: E(g, str(e), f"카드 {ci+1}: 예문은 [그림, 앞, 뒤, 뜻] 4칸"); continue
                if e[2].count("{") != e[2].count("}"): E(g, e[2], f"카드 {ci+1}: 강조 괄호 {{}} 짝")
                for i, w in enumerate(words(re.sub(r"[{}]", "", e[2]))):
                    if i and w[0].isupper(): continue
                    if not known(w): Wn(g, e[2], f"카드 {ci+1}: 단어장에 없는 단어 「{w}」")
            cq = c.get("q")
            if not cq: E(g, c.get("h", "?"), f"카드 {ci+1}: 확인 문제 없음")
            elif isinstance(cq, dict): check_q(g, cq, bk, "card")
        cnt = collections.Counter(); seen = {}; rows = []
        for q in g.get("qs", []):
            r = check_q(g, q, bk, "qs")
            key = "hard" if (q.get("k") == "pick" and q.get("hd")) else q.get("k"); cnt[key] += 1
            sig = (q.get("k"), q.get("s") or " ".join(q.get("w", [])))
            if sig in seen: E(g, q, "같은 문제가 두 번")
            seen[sig] = 1
            if r:
                if q.get("sid") is None and r in [x[1] for x in rows if x[4].get("sid") is None] and q.get("k") != "ox": Wn(g, q, "정답 문장이 다른 문제와 같음 (답을 미리 알려 줌)")   # sid 가 있으면 게임이 한 판에 한 번만 냄
                rows.append((q.get("k"), r, q.get("ko", ""), q.get("w", ""), q))
        for k, n in NEED[bk].items():
            if cnt[k] < n: (Wn if k in ("write", "hard", "fix", "order") and bk == "mid" else E)(g, "", f"{k} 문제가 {cnt[k]}개 — 별 단계에 {n}개 필요 (모자라면 고르기로 채워짐)")
        sheet.append((bk, g, rows, cnt))

print(f"검사: {', '.join(BOOKS)} · 단원 {sum(len(D[b]) for b in BOOKS)}개 · 문제 {sum(len(g['qs']) for b in BOOKS for g in D[b])}개")
for m in err: print("❌", m)
for m in warn: print("⚠️ ", m)
print(f"결과: ❌ 오류 {len(err)} · ⚠️ 살펴보기 {len(warn)}")

if SHEET:
    KN = {"pick": "고르기", "ox": "⭕❌", "order": "순서", "fix": "고치기", "write": "직접 쓰기"}
    out = ["# 문법 문제 훑어보기 — 정답 문장 목록", "", "게임이 채점 뒤 보여 주는 「정답 문장」이에요. 어색하거나 답이 둘인 문장이 있으면 번호만 알려 주세요.", ""]
    for bk, g, rows, cnt in sheet:
        out += [f"## {g['id']} · {g['t']}  ({g['sub']})", "", "설명 카드: " + " / ".join(c["h"] for c in g["cards"] if c.get("k") == "rule"), "", "| # | 종류 | 문제 | 정답 문장 | 뜻 | 왜 |", "|---|---|---|---|---|---|"]
        for i, (k, r, ko, w, q) in enumerate(rows, 1):
            src = " / ".join(q["w"]) if k == "order" else q["s"] + ("  [" + " · ".join(q["o"]) + "]" if k == "pick" else "  (❌ 틀린 문장)" if k == "ox" and not q["ok"] else "  (⭕ 맞는 문장)" if k == "ox" else "")
            out.append(f"| {i} | {KN[k]}{' ★' if q.get('hd') else ''} | {src} | **{r}** | {ko} | {w} |")
        out.append("")
    open(SHEET, "w", encoding="utf-8").write("\n".join(out)); print("훑어보기 목록 →", SHEET)
sys.exit(1 if err else 0)
