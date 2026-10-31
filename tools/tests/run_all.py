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
FAST = ["loot491", "study3", "study4", "v243test", "v246test", "v249test", "uitest", "newstest", "homotest",
        "dexgr", "bingotest", "bingo2", "albumtest2", "olytest", "olyfail", "scrolltest2", "bottomtap",
        "shx", "swreload", "v256test", "mv1run", "foottest", "talkshot", "screens", "poptest", "fixedscan", "acctest", "admintest", "dexfound", "shortrun", "ipadtest", "retrytest", "tiertest", "voicetest", "v6test", "datacheck", "raidtest", "bosstest", "battletest", "walktest", "classtest", "stagetest", "flagtest", "wbtest", "jltest", "slimetest", "formscheck", "dexprac", "quiztest", "runfix", "sensetest", "raid2test", "swcache", "weektest", "swmin", "midsplit", "purpletest", "examtest", "polishtest", "examclass", "stocksync", "qa337", "teamtab", "phonics2", "classroom", "battleq", "race351", "live353", "day354", "hw355", "pad356", "sfs357", "rank358", "conn359", "sw360", "kids361", "nick362", "prize364", "dup365", "late367", "fx368", "perf369", "gate370", "zone371", "perf372", "perf373", "spread374", "gc375", "exp376", "aud377", "joy378", "voice379", "voca380", "proper381", "battle382", "pick383","voice385","gram386","admin387","race389","boss392","raid392","flag392","rr392","wk392","admin395","link396","course397","parent397","cup399","cup401","house404","house409","house410","tag404","town406","town407","raid407","bt409","tv410","pad411","ui413","fish414","rank416","land415","pad417","cloud418","auth419","own421","tower422","board424","board428","tv433","town434", "tower435", "yard436", "label437", "d30_438", "fr439", "board440", "mid442", "mid443", "done444", "board447", "tv447", "kid448", "kid451", "kid452", "tower453", "tower455", "tower459", "day459", "av461", "tower462", "tower463", "tower467", "tower472", "town473", "study474", "who476", "who477", "who478", "hint481"]
SLOW = ["runsweep", "sweep1", "board440full"]
TIMEOUT = {"runsweep": 1800, "sweep1": 3600, "board440full": 3600}

BAD_LINE = re.compile(r"(\berrs\s*\[(?!\s*\]))|(^\s*BAD\b)|(\bError:)|(^ERR\b)")

def check_output(out):
    bad = []
    for ln in out.splitlines():
        l2 = re.sub(r"'C:(Failed to load[^']*|An unknown error occurred when fetching the script\.)',?\s*", "", ln)   # 바깥 주소 막힘은 정상
        l2 = re.sub(r"\[\s*,?\s*\]", "[]", l2)
        if BAD_LINE.search(l2): bad.append(ln.strip()[:200])
    return bad

FLAKY = {}   # (v399) 처음 실패하고 다시 돌려 통과한 테스트 — 컴퓨터가 느려 시간이 모자란 것일 수 있어 한 번 더 혼자 돌려 봄

def run_test(name):
    r = run_once(name)
    if r[2] and os.environ.get("HY_RETRY", "1") != "0":
        first = r[2]; r2 = run_once(name)
        if not r2[2]:
            FLAKY[name] = first[:2]; return (name, r[1] + r2[1], [])
        return (name, r[1] + r2[1], ["두 번 다 실패"] + r2[2])
    return r

def run_once(name):
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
    # (v337) QA: v336 을 올렸는데 버전이 v335 그대로였다 (둘이 같이 낡아서 위 검사는 통과) → main 과 게임 파일이 다르면 버전이 main 보다 커야 함
    try:
        mh = subprocess.run(["git", "-C", ROOT, "show", "main:index.html"], capture_output=True, text=True)
        mv = re.search(r'const GAME_VER = "v(\d+)"', mh.stdout or "")
        if mh.returncode == 0 and mv and gv and mh.stdout != html and int(gv.group(1)[1:]) <= int(mv.group(1)):
            probs.append("버전을 올리세요: main 과 index.html 이 다른데 GAME_VER=%s (main v%s)" % (gv.group(1), mv.group(1)))
    except Exception as e:
        print("버전 비교 건너뜀:", e)
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
    with ThreadPoolExecutor(max_workers=int(os.environ.get("HY_WORKERS", "4"))) as ex:   # (v312) 코어가 적으면 HY_WORKERS=2
        for name, secs, probs in ex.map(run_test, names):
            print("  %s %-12s %4ds%s" % ("✅" if not probs else "❌", name, secs, "" if not probs else "  " + " | ".join(probs[:3])))
            if probs: fails.append(name)
    for n, why in FLAKY.items(): print("  ⚠️ %s — 처음엔 실패했다가 다시 돌려 통과 (%s) — 자주 나오면 원인 찾기" % (n, " | ".join(why)))
    ok = not bp and not fails
    print("== 결과:", "모두 통과 ✅" if ok else "실패 ❌ (%s) — 자세한 출력은 tools/tests/out/<이름>.log" % ", ".join(fails + (["기본 검사"] if bp else [])))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
