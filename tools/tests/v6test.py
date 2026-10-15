"""(v278) 노션 v6 검사기 — 예시 DAY 는 ❌ 0, 일부러 망친 DAY 는 ❌ 가 잡혀야 한다 (자료는 바꾸지 않음)"""
import subprocess, sys, os, re, tempfile
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V6 = os.path.join(R, "tools", "basic", "v6.py"); S = os.path.join(R, "tools", "basic", "v6sample", "DAY99.md")
bad = []
r = subprocess.run([sys.executable, V6, "check", S, "--level", "L3"], capture_output=True, text=True); print(r.stdout[-600:])
if "❌ 0" not in r.stdout: bad.append("예시 DAY 에 ❌")
t = open(S, encoding="utf8").read()
t = t.replace("허락하다, 허가하다 |", "허락하다, 허가증 |").replace("Please coil it and put it away.", "I coiled it already.")
f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf8"); f.write(t); f.close()
r = subprocess.run([sys.executable, V6, "check", f.name, "--level", "L3"], capture_output=True, text=True); print(r.stdout[-900:])
n = int(re.search(r"❌ (\d+)", r.stdout.split("합계:")[-1]).group(1))
if n < 2 or "품사 섞임" not in r.stdout or "변한 꼴" not in r.stdout: bad.append("망친 DAY 를 못 잡음")
os.unlink(f.name)
if bad: print("BAD", bad)
