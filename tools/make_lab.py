# 🧪 단어 연구소 (v640) 재료 만들기 — data/xtra.json 의 낱말 가족(fam)에서 "뿌리 + 붙는 말 = 새 단어" 를 찾아 data/lab.json 으로
# 사람이 만든 뜻(fam 의 한국어)만 씀 · 철자 규칙(e 빠짐 · y→i · 자음 겹침)이 맞는 것만
import json, os, re
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
X = json.load(open(os.path.join(D, "xtra.json")))["w"]
B = json.load(open(os.path.join(D, "bex.json")))
AF = {  # 붙는 말: [뜻, 무엇이 되나]
 "-ly": ["~하게", "꾸미는 말"], "-er": ["~하는 사람·것", "명사"], "-or": ["~하는 사람·것", "명사"], "-ist": ["~하는 사람", "명사"],
 "-y": ["~이 많은 · ~한", "형용사"], "-ion": ["~하는 것", "명사"], "-ation": ["~하는 것", "명사"], "-al": ["~의 · ~한", "형용사"],
 "-able": ["~할 수 있는", "형용사"], "-ible": ["~할 수 있는", "형용사"], "-ness": ["~함", "명사"], "-ity": ["~함", "명사"], "-ment": ["~하는 것", "명사"],
 "-ful": ["~이 가득한", "형용사"], "-less": ["~이 없는", "형용사"], "-ive": ["~하는 성질의", "형용사"], "-ize": ["~하게 만들다", "동사"], "-en": ["~하게 하다", "동사"],
 "-ous": ["~이 많은 · ~한", "형용사"], "-ic": ["~의 · ~적인", "형용사"], "-ance": ["~하는 것", "명사"], "-ence": ["~하는 것", "명사"], "-ship": ["관계 · 자격", "명사"],
 "-ish": ["~같은 · 조금 ~한", "형용사"], "un-": ["아닌 · 반대", "앞에 붙음"], "re-": ["다시", "앞에 붙음"], "dis-": ["반대 · 아닌", "앞에 붙음"],
 "im-": ["아닌", "앞에 붙음"], "in-": ["아닌", "앞에 붙음"], "mis-": ["잘못", "앞에 붙음"], "over-": ["너무 · 위", "앞에 붙음"], "under-": ["아래 · 덜", "앞에 붙음"],
}
SUF = sorted([a[1:] for a in AF if a[0] == "-"], key=lambda s: -len(s))
PRE = [a[:-1] for a in AF if a[-1] == "-"]
V = "aeiou"
def forms(b, s):
    o = {b + s: "+"}
    if b.endswith("e") and s[0] in V and s != "ly": o[b[:-1] + s] = "e"
    if s == "ly" and b.endswith("le"): o[b[:-1] + "y"] = "l"          # gentle → gently · possible → possibly
    if s == "y" and b.endswith("e") and not b.endswith("le"): o[b[:-1] + "y"] = "e"   # ice → icy
    if b.endswith("y") and len(b) > 2 and b[-2] not in V and s[0] != "i": o[b[:-1] + "i" + s] = "y"
    if len(b) >= 3 and b[-1] not in V + "wxy" and b[-2] in V and b[-3] not in V and s[0] in V + "y": o[b + b[-1] + s] = "d"
    return o
ko = {}
for en, v in B.items():
    try: ko[en.lower()] = v["P"][0][1].split(",")[0].strip()
    except Exception: pass
pairs = []
for k, v in X.items():
    for f in v.get("fam") or []:
        a, b = k.lower(), str(f[0]).lower(); ko.setdefault(b, f[1].split(",")[0].strip())
        pairs.append((a, b))
for k, v in X.items():   # 열쇠 단어의 뜻 (다른 가족에서)
    pass
BAN = {"assembly", "later", "lower", "chicken", "mitten", "arabic", "resource", "impolitic", "spaceship", "multiply", "difficulty", "easy", "uneasy", "signal", "basic", "flyer", "prayer"}   # 뜻이 이어지지 않는 것
R, seen = [], set(BAN)
for a, b in pairs:
    for x, y in ((a, b), (b, a)):
        if y in seen or not re.fullmatch(r"[a-z]{3,}", x) or not re.fullmatch(r"[a-z]+", y) or x not in ko or y not in ko: continue
        hit = None
        for s in SUF:
            fm = forms(x, s)
            if y in fm: hit = ("-" + s, fm[y]); break
        if not hit:
            for p in PRE:
                if y == p + x: hit = (p + "-", "+"); break
        if hit and ko[x] != ko[y]:
            seen.add(y); R.append([x, ko[x], hit[0], y, ko[y], hit[1]])
R.sort(key=lambda r: (r[2], r[3]))
used = {r[2] for r in R}
out = {"a": {k: v for k, v in AF.items() if k in used}, "r": R}
json.dump(out, open(os.path.join(D, "lab.json"), "w"), ensure_ascii=False, separators=(",", ":"))
from collections import Counter
print(len(R), Counter(r[2] for r in R).most_common(), Counter(r[5] for r in R))
