"""(v288) g56b.txt 검사 — 고학년(G5-6) 단어에 새로 쓴 대화 (상황 칸 있음)
   줄 형식: word|A|B|A 해석 / B 해석|상황      usage: python3 tools/talk/checkb.py [파일 …]
   규칙: 단어마다 정확히 2줄 · 목표 단어는 A+B 합쳐 정확히 1번(원형 그대로) · A·B 각각 5~10 낱말 ·
         상황은 공백 빼고 6~15자, 영어 정답·한국어 뜻이 들어가면 안 됨 · 해석은 'A / B'"""
import re, sys, os, json
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(H))
files = sys.argv[1:] or [os.path.join(H, "g56b.txt")]
html = open(os.path.join(R, "index.html"), encoding="utf8").read()
KO = {}
for m in re.finditer(r'\{en:"([^"]+)",ko:"([^"]*)"', html): KO.setdefault(m.group(1), m.group(2))
words = lambda s: re.findall(r"[A-Za-z']+", s)
bad, warn, cnt = [], [], {}
for f in files:
    for i, ln in enumerate(open(f, encoding="utf8"), 1):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.startswith("#"): continue
        p = ln.split("|"); tag = f"{os.path.basename(f)}:{i} "
        if len(p) != 5: bad.append(tag + f"칸 {len(p)}개 (5개): {ln[:80]}"); continue
        en, a, b, ko, sit = [x.strip() for x in p]
        cnt[en] = cnt.get(en, 0) + 1
        rx = re.compile(r"(?<![A-Za-z\-'])" + re.escape(en) + r"(?![A-Za-z\-])", re.I)
        n = len(rx.findall(a)) + len(rx.findall(b))
        if n != 1: bad.append(tag + f"{en}: 목표 단어 {n}번 — A '{a}' / B '{b}'")
        for k, s in (("A", a), ("B", b)):
            nw = len(words(s))
            if nw < 5 or nw > 10: warn.append(tag + f"{en}: {k} {nw}낱말 (5~10): {s}")
        if " / " not in ko: bad.append(tag + f"{en}: 해석에 ' / ' 없음")
        sl = len(sit.replace(" ", ""))
        if sl < 5 or sl > 16: warn.append(tag + f"{en}: 상황 {sl}자: {sit}")
        if re.search(r"[A-Za-z]", sit): bad.append(tag + f"{en}: 상황에 영어: {sit}")
        for m in re.split(r"[,·/]", KO.get(en, "")):
            m = re.sub(r"\(.*?\)|~", "", m).strip(); m = re.sub(r"(하다|다|의|한|운|은|는|적인)$", "", m).strip()
            if len(m) >= 2 and m in sit: warn.append(tag + f"{en}: 상황에 정답 뜻 '{m}': {sit}")
        if en not in KO: warn.append(tag + f"{en}: 게임 단어장에 없는 단어")
for en, c in cnt.items():
    if c != 2: bad.append(f"{en}: 대화 {c}줄 (2줄)")
for x in bad: print("❌", x)
for x in warn: print("⚠️", x)
print(f"단어 {len(cnt)} · 대화 {sum(cnt.values())} · ❌ {len(bad)} · ⚠️ {len(warn)}")
