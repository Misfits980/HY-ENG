"""tools/words/auto.json → index.html 의 AUTO 칸 (단어가 늘어도 손으로 붙이지 않게).

  python3 tools/words/sync.py          # 다시 쓰기 (바뀐 게 없으면 그대로)
  python3 tools/words/sync.py --check  # index.html 이 auto.json 과 맞는지만 (테스트용)

auto.json
  course : { 원본 과 이름(kinder=1단계·basic=2단계·elem=3단계·mv1): { 과 번호: [단어…] } }   — COURSE 의 그 과 줄을 바꾸거나 새로 넣음
  ko     : { 게임 반(basic·elem·g56·mv1…): { 과 번호: {단어: 교재 뜻} } }                 — COURSE_KO (단어장 뜻과 다를 때만)
  words  : { 단어: {ko, level, emoji} }                                                  — WORD_BANK.push (게임에 처음 들어오는 단어)
  album  : [[앨범, 단어], …]                                                             — DEX_ADD (앨범 맨 뒤에 붙는 순서. 뒤에만 더할 것)
"""
import json, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUTO = os.path.join(R, "tools", "words", "auto.json")
HTML = os.path.join(R, "index.html")

def js(s): return str(s).replace("\\", "\\\\").replace('"', '\\"')

def course_block(s, raw):
    """COURSE = { … raw:{ … } } 또는 COURSE.raw = { … } 의 (시작, 끝) 위치"""
    m = re.search(r"^const COURSE = \{\n", s, re.M)
    if m:
        m2 = re.compile(r"^  " + re.escape(raw) + r":\{\n(.*?)\n  \}", re.M | re.S).search(s, m.end())
        if m2 and (s.find("\n};", m.end()) > m2.start()): return m2.start(1), m2.end(1)
    m3 = re.search(r"^COURSE\." + re.escape(raw) + r" = \{\n(.*?)\n\};", s, re.M | re.S)
    if m3: return m3.start(1), m3.end(1)
    raise SystemExit(f"COURSE 에서 '{raw}' 과 목록을 못 찾음")

def render(s, A):
    # ① COURSE 과 줄
    for raw, stages in A.get("course", {}).items():
        a, b = course_block(s, raw); body = s[a:b]
        for n, ws in sorted(stages.items(), key=lambda x: int(x[0])):
            line_re = re.compile(r"^(    )" + str(int(n)) + r':"[^"]*"(,?)(.*)$', re.M)
            new = '    %d:"%s"' % (int(n), "|".join(ws))
            m = line_re.search(body)
            if m: body = body[:m.start()] + new + m.group(2) + m.group(3) + body[m.end():]
            else:   # 번호 순서 자리에 넣기
                lines = body.split("\n"); pos = len(lines)
                for i, ln in enumerate(lines):
                    mm = re.match(r"^    (\d+):", ln)
                    if mm and int(mm.group(1)) > int(n): pos = i; break
                lines.insert(pos, new + ",")
                body = "\n".join(lines)
        # 마지막 줄 쉼표 정리
        lines = body.rstrip().split("\n")
        for i, ln in enumerate(lines):
            if re.match(r"^    \d+:\"", ln):
                last = max(j for j, l in enumerate(lines) if re.match(r"^    \d+:\"", l))
                code, _, cmt = ln.partition("   //")
                code = code.rstrip().rstrip(",")
                if i != last: code += ","
                lines[i] = code + ("   //" + cmt if cmt else "")
        s = s[:a] + "\n".join(lines) + s[b:]
    # ② COURSE_KO
    ko = A.get("ko", {})
    s = re.sub(r"AUTO-KO-BEGIN \*/ const COURSE_KO = .*?; /\* AUTO-KO-END",
               lambda m: "AUTO-KO-BEGIN */ const COURSE_KO = " + json.dumps(ko, ensure_ascii=False, separators=(",", ":")) + "; /* AUTO-KO-END", s, count=1, flags=re.S)
    # ③ WORD_BANK
    W = A.get("words", {})
    items = ['{en:"%s",ko:"%s",level:%d%s%s}' % (js(en), js(w["ko"]), int(w["level"]), (',emoji:"%s"' % w["emoji"]) if w.get("emoji") else "", (',src:"%s"' % w["src"]) if w.get("src") else "") for en, w in W.items()]
    s = re.sub(r"(/\* AUTO-WORDS-BEGIN[^\n]*\*/\n).*?(\n/\* AUTO-WORDS-END \*/)",
               lambda m: m.group(1) + ("WORD_BANK.push(" + ", ".join(items) + ");" if items else "") + m.group(2), s, count=1, flags=re.S)
    # ④ 앨범
    alb = {}
    for a, en in A.get("album", []): alb.setdefault(a, []).append(en.replace(" ", "_"))   # 순서 그대로 (앨범 뒤에만)
    lines = ['if(DEX_ADD.%s!=null) DEX_ADD.%s += " %s"; else DEX_ADD.%s="%s";' % (a, a, " ".join(v), a, " ".join(v)) for a, v in alb.items()]
    s = re.sub(r"(/\* AUTO-ALBUM-BEGIN[^\n]*\*/\n).*?(/\* AUTO-ALBUM-END \*/)",
               lambda m: m.group(1) + "".join(l + "\n" for l in lines) + m.group(2), s, count=1, flags=re.S)
    return s

def main():
    A = json.load(open(AUTO, encoding="utf8"))
    s = open(HTML, encoding="utf8").read()
    for mk in ("AUTO-WORDS-BEGIN", "AUTO-WORDS-END", "AUTO-KO-BEGIN", "AUTO-KO-END", "AUTO-ALBUM-BEGIN", "AUTO-ALBUM-END"):
        if mk not in s: raise SystemExit("index.html 에 " + mk + " 표시가 없음")
    # 단어장에 이미 있는 단어를 또 넣지 않게
    base = s.split("/* AUTO-WORDS-BEGIN")[0] + s.split("/* AUTO-WORDS-END */")[1]
    dup = [en for en in A.get("words", {}) if re.search(r'\{en:"' + re.escape(en) + r'",', base)]
    if dup: raise SystemExit("auto.json words 중 이미 게임 단어에 있는 것: " + ", ".join(dup))
    out = render(s, A)
    if "--check" in sys.argv:
        print("맞음" if out == s else "다름 — python3 tools/words/sync.py 를 돌려야 함"); sys.exit(0 if out == s else 1)
    if out != s: open(HTML, "w", encoding="utf8").write(out); print("index.html 다시 씀")
    else: print("바뀐 것 없음")
    print("과 %d · 교재 뜻 %d · 새 단어 %d" % (sum(len(v) for v in A.get("course", {}).values()), sum(len(x) for v in A.get("ko", {}).values() for x in v.values()), len(A.get("words", {}))))

if __name__ == "__main__":
    main()
