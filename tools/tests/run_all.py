#!/usr/bin/env python3
"""HY ENG — 배포 전에 한 번에 돌리는 검사.

    python3 tools/tests/run_all.py            # 빠른 검사 (약 5~8분, 4개씩 동시에)
    python3 tools/tests/run_all.py --slow     # + 전 세트 전 스테이지 자동 풀이·달리기 289조합 (30분 이상)
    python3 tools/tests/run_all.py olytest    # 이름을 주면 그 테스트만

통과 기준 (v247 사고 뒤 정한 규칙): 종료 코드 0 · Traceback 없음 · 실제 오류 줄 없음
('errs [...]' 가 비어 있지 않음, 'BAD', 'Error:' — 바깥 주소를 막아서 생긴 'Failed to load' 는 제외).
기본 검사: index.html 스크립트 문법(node) · GAME_VER 와 sw.js VERSION 일치 · 대화 단문 검사(tools/talk/check.py).
"""
import os, re, sys, subprocess, time, json
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FAST = ["study3", "study4", "v243test", "v246test", "v249test", "uitest", "newstest", "homotest",
        "dexgr", "bingotest", "bingo2", "albumtest2", "olytest", "olyfail", "scrolltest2", "bottomtap",
        "shx", "swreload", "v256test", "mv1run", "foottest", "talkshot", "screens", "poptest", "fixedscan", "acctest", "admintest", "dexfound", "shortrun", "ipadtest", "retrytest", "tiertest", "voicetest", "v6test", "datacheck", "raidtest", "bosstest","battletest"]
SLOW = ["runsweep", "sweep1"]
TIMEOUT = {"runsweep": 1800, "sweep1": 3600}

BAD_LINE = re.compile(r"(\berrs\s*\[(?!\s*\]))|(^\s*BAD\b)|(\bError:)|(^ERR\b)")

def check_output(out):
    bad = []
    for ln in out.splitlines():
        l2 = re.sub(r"'C:(Failed to load[^']*|An unknown error occurred when fetching the script\.)',?\s*", "", ln)   # 바깥 주소 막힘은 정상
        l2 = re.sub(r"\[\s*,?\s*\]", "[]", l2)
        if BAD_LINE.search(l2): bad.append(ln.strip()[:200])
    return bad

def run_test(name):
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, name + ".py")], cwd=HERE,
                           capture_output=True, text=True, timeout=TIMEOUT.get(name, 600))
        out = p.stdout + p.stderr; code = p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""; code = "timeout"
    probs = []
    if code != 0: probs.append("종료 코드 %s" % code)
    if "Traceback" in out: probs.append("Traceback")
    probs += check_output(out)
    with open(os.path.join(HERE, "out", name + ".log"), "w") as f: f.write(out)
    return name, round(time.time() - t0), probs

def basic_checks():
    probs = []
    html = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
    sw = open(os.path.join(ROOT, "sw.js"), encoding="utf8").read()
    gv = re.search(r'const GAME_VER = "(v\d+)"', html); sv = re.search(r'VERSION = "hyeng-(v\d+)"', sw)
    if not gv or not sv or gv.group(1) != sv.group(1):
        probs.append("버전 불일치: GAME_VER=%s sw.js=%s" % (gv and gv.group(1), sv and sv.group(1)))
    js = ("const s=require('fs').readFileSync(%r,'utf8'); const m=s.match(/<script>([\\s\\S]*?)<\\/script>/g)||[];"
          "let bad=0; m.forEach((x,i)=>{ try{ new Function(x.replace(/^<script>|<\\/script>$/g,'')); }catch(e){ bad++; console.log('script '+i+': '+e.message); } });"
          "console.log('scripts '+m.length+' bad '+bad);") % os.path.join(ROOT, "index.html")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    if "bad 0" not in r.stdout: probs.append("스크립트 문법: " + r.stdout.strip()[:300])
    for f in ["data/dex1.json", "data/dex2.json", "data/dex3.json", "data/easy.json", "data/talk.json", "data/bex.json"]:
        try: json.load(open(os.path.join(ROOT, f), encoding="utf8"))
        except Exception as e: probs.append("%s 읽기 실패: %s" % (f, e))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "words", "sync.py"), "--check"], capture_output=True, text=True)   # (v280) 단어 자동 칸
    if r.returncode: probs.append("단어 자동 칸: " + (r.stdout + r.stderr).strip()[-200:])
    for g in ["g12", "g34", "g56"]:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "talk", "check.py"), g], capture_output=True, text=True)
        if "BAD" in r.stdout or "missing count 0" not in r.stdout or r.returncode: probs.append("대화 %s: %s" % (g, r.stdout.strip()[-200:]))
    return probs

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = args or (FAST + (SLOW if "--slow" in sys.argv else []))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    print("== 기본 검사"); bp = basic_checks()
    print("  " + ("통과" if not bp else "\n  ".join("❌ " + x for x in bp)))
    print("== 테스트 %d개 (4개씩 동시에)" % len(names))
    fails = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for name, secs, probs in ex.map(run_test, names):
            print("  %s %-12s %4ds%s" % ("✅" if not probs else "❌", name, secs, "" if not probs else "  " + " | ".join(probs[:3])))
            if probs: fails.append(name)
    ok = not bp and not fails
    print("== 결과:", "모두 통과 ✅" if ok else "실패 ❌ (%s) — 자세한 출력은 tools/tests/out/<이름>.log" % ", ".join(fails + (["기본 검사"] if bp else [])))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
