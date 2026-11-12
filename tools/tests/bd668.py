# v668 🎲 보드게임 (진짜 3D · swiftshader) — ① ⭐ 앞에서 멈춰도 말이 처음 칸으로 돌아가지 않음 (「애들이 날아다녀」) ② 굴리는 동안 아래 안내를 숨김 (주사위가 가려짐) ③ TV = 안내가 맨 아래 한 줄
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
POS = "()=>{ const o=Board.o, c=B3.pc[o.cur], s=B3.slot(o.cur), h=c.home; return {pos:o.P[o.cur].pos, left:o.left, d:Math.round(Math.hypot(c.g.position.x-s.x, c.g.position.z-s.z)*100)/100, hd:Math.round(Math.hypot(h.x-s.x, h.z-s.z)*100)/100, k:c.anim && c.anim.k, ask:!!document.querySelector('.bdStarC')}; }"
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"]); errs = []
        pg = await br.new_page(viewport={"width": 1920, "height": 1080}); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
        await pg.evaluate("()=>Board.begin({sk:'k', set:'elem', from:0, to:3, qt:['mean'], sec:0, rounds:3, star:12, P:[{n:'빨강팀',id:'',ch:4},{n:'파랑팀',id:'',ch:3}]})")
        await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>{ const b=[...document.querySelectorAll('#bdHow button, #bdHow a, #bdHow [data-hw]')].find(x=>/건너뛰기/.test(x.textContent)); if(b) b.click(); }")
        await pg.wait_for_function("()=>!!document.querySelector('#board [data-bd=roll]') && !!B3.R", timeout=90000); await pg.wait_for_timeout(1500)
        # ③ TV = 맨 아래 한 줄 (전: 세 줄 216px · 화면 아래 1/3)
        await pg.evaluate("()=>{ document.getElementById('board').classList.add('tv'); document.getElementById('bdAct').dataset.who='경훈'; Board.o.P[0].it=['mush']; Board.o.P[0].coin=10; Board.turnMenu(); }"); await pg.wait_for_timeout(600)
        r = await pg.evaluate("""()=>{ const a=document.getElementById('bdAct'), c=a.firstElementChild.getBoundingClientRect(), k=[...a.querySelectorAll('.bdHud, .bdTip, .bdBag, .bdRoll')].map(e=>e.getBoundingClientRect());
          return {dock:a.classList.contains('bdDock'), h:Math.round(c.height), bot:Math.round(innerHeight-c.bottom), rows:new Set(k.map(r=>Math.round((r.top+r.bottom)/2/14))).size, in:k.every(r=>r.left>=0 && r.right<=innerWidth), tag:getComputedStyle(a,'::before').content, fs:Math.round(parseFloat(getComputedStyle(a.querySelector('.bdHudS')).fontSize)*(parseFloat(getComputedStyle(a).zoom)||1))}; }""")
        ok(r["dock"] and r["h"] <= 110 and r["rows"] == 1 and r["in"] and "패드에서" in r["tag"] and r["fs"] >= 20, f"③ TV 굴리기 안내 = 맨 아래 한 줄 {r}")
        await pg.screenshot(path=OUT + "bd668_dock.png")
        # ② 굴리는 동안 숨김
        await pg.evaluate("()=>{ const o=Board.o; o.star=(o.P[o.cur].pos+4)%o.N; o.force=6; o.P[o.cur].coin=20; Board.roll(); }"); await pg.wait_for_timeout(900)
        r = await pg.evaluate("()=>{ const a=document.getElementById('bdAct'), c=a.firstElementChild; return [a.classList.contains('bdRollHide'), c ? getComputedStyle(c).opacity : '-', B3.die.visible, B3.die.geometry.parameters.width]; }")
        ok(r[0] and float(r[1]) < 0.5 and r[2] and r[3] >= 1.5, f"② 굴리는 동안 안내 숨김 · 주사위 보임(크기 {r[3]}) {r}")
        await pg.screenshot(path=OUT + "bd668_roll.png")
        # ① 걷다가 ⭐ 앞에서 멈춤 — 말이 그 칸에 그대로
        await pg.wait_for_function("()=>!!document.querySelector('.bdStarC')", timeout=150000)
        a = await pg.evaluate(POS); await pg.wait_for_timeout(2500); b = await pg.evaluate(POS)
        ok(a["pos"] == 4 and a["hd"] < 0.05 and b["d"] < 0.1 and b["hd"] < 0.05, f"① ⭐ 앞에서 물어보는 동안 말이 그 칸에 그대로 (전: 처음 칸으로 8.8 만큼 미끄러져 돌아감) {a} → {b}")
        ok(not await pg.evaluate("()=>document.getElementById('bdAct').classList.contains('bdRollHide') || document.getElementById('bdAct').classList.contains('bdDock')"), "② 다음 카드가 뜨면 안내가 다시 보임 (별 카드는 한 줄 모드 아님)")
        await pg.screenshot(path=OUT + "bd668_star.png")
        await pg.evaluate("()=>{ const b=document.querySelector('[data-bd=skip]'); b && b.click(); }")
        ks = []
        for _ in range(12):
            await pg.wait_for_timeout(120); x = await pg.evaluate(POS); ks.append(x["k"])
        ok("fly" not in ks and "hop" in ks, f"① 이어서 갈 때도 한 칸씩 통통 (날아가지 않음) {ks}")
        ok(await pg.evaluate("()=>{ const c=B3.pc[Board.o.cur]; return c.anim ? c.anim.h : 0.62; }") <= 0.7, "① 뛰는 높이 0.62")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}"); await br.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
