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

# (v280) apply 를 복사본에서 끝까지 — 과 목록·교재 뜻·새 단어·앨범이 index.html 에 들어가고 sync --check 가 맞음
import shutil, json
tmp = tempfile.mkdtemp()
for d in ("data", "tools"): shutil.copytree(os.path.join(R, d), os.path.join(tmp, d), ignore=shutil.ignore_patterns("out", "__pycache__", "*.png"))
shutil.copy(os.path.join(R, "index.html"), tmp)
t = open(S, encoding="utf8").read().replace("| coil |", "| kayak |").replace(" coil", " kayak").replace("coiled", "kayaked").replace("coils · ", "kayaks · ").replace("coiling", "kayaking").replace("명사 coils /", "명사 kayaks /")
dayf = os.path.join(tmp, "DAY31.md"); open(dayf, "w", encoding="utf8").write(t)
r = subprocess.run([sys.executable, os.path.join(tmp, "tools", "basic", "v6.py"), "apply", dayf, "--level", "L3"], capture_output=True, text=True); print(r.stdout[-700:], r.stderr[-500:])
h = open(os.path.join(tmp, "index.html"), encoding="utf8").read()
ok = ('31:"permit|kayak"' in h) and ('{en:"kayak",ko:"똬리, 감긴 것",level:2}' in h) and ("kayak" in h.split("AUTO-ALBUM-BEGIN")[1].split("AUTO-ALBUM-END")[0])
chk = subprocess.run([sys.executable, os.path.join(tmp, "tools", "words", "sync.py"), "--check"], capture_output=True, text=True).stdout
print("apply →", ok, chk.strip())
if not ok or "맞음" not in chk: bad.append("apply 가 index.html 에 안 들어감")
shutil.rmtree(tmp)
if bad: print("BAD", bad)
