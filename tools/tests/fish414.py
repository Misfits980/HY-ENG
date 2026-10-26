"""(v414) 🎣 낚시 깊게 — 사용자 "재미를 느낄 수 있다고 생각해?" → 낚시부터 제대로
  ① 연못에 물고기 그림자 (크기 = 몸집) → 그림자 앞을 누르면 거기로 던짐
  ② 큰 것은 💪 줄다리기: 꾹 = 감기 · 💦 몸부림칠 때 계속 감으면 줄 끊어짐
  ③ 잡는 순간 물 밖으로 튀어 오름 → 카드: 📏 크기 · 🏆 최고 기록 · ✨ 반짝이(×3 값) · ⭐ 오늘의 물고기
  ④ 🕐 아침·낮·저녁·밤 · 🌧 비 · ✨ 황금 물고기 떼(5분) 마다 나오는 것이 다름 · 도감에 크기·힌트"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); localStorage.setItem('hyeng_proto_casts','10'); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        E = pg.evaluate
        async def until(js, n=80):
            for _ in range(n):
                try:
                    if await E(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        await E("()=>{ HOUSE.setWx(false); HOUSE.setRush(false); HOUSE.go('yard'); }"); await until("()=>HOUSE.place()==='yard'")
        # ① 그림자
        await E("()=>{ for(let i=0;i<4;i++) HOUSE.spawnShadow(); }"); await pg.wait_for_timeout(1500)
        r = await E("()=>HOUSE.PS().map(o=>({en:o.f.en, cm:o.cm, rad:o.rad, vis:o.g.visible, st:o.st}))")
        ok(len(r) >= 4 and all(o["vis"] for o in r), f"연못에 물고기 그림자 {len(r)}마리")
        ok(await E("()=>HOUSE.PS().every(o=>(o.cm>0)===!HOUSE.SPEC[o.f.en].junk)"), "그림자마다 크기(cm) — 쓰레기는 크기 없음")
        big = await E("()=>{ const L=HOUSE.PS().filter(o=>!HOUSE.SPEC[o.f.en].junk); const a=L.reduce((m,o)=>o.cm>m.cm?o:m, L[0]); const b=L.reduce((m,o)=>o.cm<m.cm?o:m, L[0]); return a && b && a!==b ? a.rad>=b.rad : true; }")
        ok(big, "큰 물고기 = 큰 그림자")
        await pg.screenshot(path=OUT + "fish414_pond.png")
        # 그림자 앞을 누르면 거기로
        t = await E("()=>{ const o=HOUSE.PS().find(o=>o.st==='swim'); HOUSE.fishTap(7,6,o.g.position.x,o.g.position.z); return [o.g.position.x,o.g.position.z,o.rad]; }")
        ok(await until("()=>HOUSE.F.st==='wait'", 200), "그림자 쪽으로 던짐")
        d = await E("(t)=>Math.hypot(HOUSE.F.target.x-t[0], HOUSE.F.target.z-t[1])", t)
        ok(d < t[2] * 1.5 + 0.6, f"찌가 그림자 바로 앞에 떨어짐 (거리 {d:.2f})")
        # ② 줄다리기 — 몸부림 때 계속 감으면 끊어짐
        await E("()=>{ HOUSE.bite(); const F=HOUSE.F; F.fish=HOUSE.FISH.find(f=>f.en==='shark'); F.cm=300; F.v=0.6; F.sh=0; HOUSE.tapWhileFishing(); }")
        ok(await E("()=>HOUSE.F.st==='fight' && document.getElementById('fight').classList.contains('on')"), "큰 물고기 → 💪 줄다리기 판")
        await pg.wait_for_timeout(400); await pg.screenshot(path=OUT + "fish414_fight.png")
        r = await E("()=>{ const F=HOUSE.F, G=HOUSE.FG; F.hold=true; for(let i=0;i<400 && F.st==='fight';i++){ G.rush=true; G.rt=9; HOUSE.fightStep(0.05); } return [F.st, document.getElementById('toast').innerText]; }")
        ok(r[0] == "idle" and "끊어" in r[1], f"몸부림칠 때 계속 감으면 💥 줄 끊어짐 {r}")
        # 잘하면 잡힘 (몸부림 = 손 떼기)
        await E("()=>HOUSE.setBait(20)")
        await E("()=>HOUSE.fishTap(7,6)"); await until("()=>HOUSE.F.st==='wait'", 200)
        await E("()=>{ HOUSE.bite(); const F=HOUSE.F; F.fish=HOUSE.FISH.find(f=>f.en==='shark'); F.cm=150; F.v=0.2; F.sh=0; HOUSE.tapWhileFishing(); }")
        r = await E("()=>{ const F=HOUSE.F, G=HOUSE.FG; let n=0, mx=0, rushes=0; for(;n<3000 && F.st==='fight';n++){ F.hold=!G.rush; HOUSE.fightStep(0.05); mx=Math.max(mx,G.T); } return [F.st, n, mx, G.n]; }")
        ok(r[0] == "reel" and r[2] < 1, f"몸부림 땐 손 떼고 나머진 꾹 → 끌어옴 {r}")
        ok(r[1] * 0.05 > 2.5 and r[3] >= 1, f"줄다리기는 몇 초 · 몸부림 한 번 이상 ({r[1]*0.05:.1f}초 · {r[3]}번)")
        ok(await until("()=>HOUSE.F.st==='jump' || HOUSE.F.st==='quiz'", 40), "물 밖으로 튀어 오름")
        ok(await until("()=>document.getElementById('quiz').classList.contains('on')", 40), "→ 잡음 카드")
        r = await E("()=>[document.getElementById('qRes').innerText, HOUSE.FR().shark, HOUSE.bag().slice(-1)[0]]")
        ok("1.5 m" in r[0] and r[1]["b"] == 150 and r[2]["cm"] == 150, f"카드에 📏 크기 · 기록 · 가방에 크기 {r}")
        ok("NEW" in r[0], "처음 = 🆕 NEW")
        await pg.screenshot(path=OUT + "fish414_card.png")
        await E("()=>document.getElementById('qOk').click()"); await until("()=>HOUSE.F.st==='idle'")
        # ③ 더 큰 것 = 🏆 최고 기록 · ✨ 반짝이
        await E("()=>HOUSE.fishTap(7,6)"); await until("()=>HOUSE.F.st==='wait'", 200)
        await E("()=>{ HOUSE.bite(); const F=HOUSE.F; F.fish=HOUSE.FISH.find(f=>f.en==='shark'); F.cm=380; F.v=0.9; F.sh=1; HOUSE.tapWhileFishing(); HOUSE.winFight(); }")
        ok(await until("()=>document.getElementById('quiz').classList.contains('on')", 60), "다시 잡음")
        r = await E("()=>[document.getElementById('qRes').innerText, document.getElementById('quiz').className, HOUSE.FR().shark, HOUSE.bag().slice(-1)[0]]")
        ok("최고 기록" in r[0] and "rec" in r[1] and r[2]["b"] == 380, f"더 크면 🏆 최고 기록 {r[0][:40]}")
        ok("반짝이" in r[0] and "sh" in r[1].split() and r[2]["s"] == 1 and r[3]["sh"] == 1, "✨ 반짝이 — 카드 · 기록 · 가방")
        await pg.screenshot(path=OUT + "fish414_shiny.png")
        await E("()=>document.getElementById('qOk').click()"); await until("()=>HOUSE.F.st==='idle'")
        r = await E("()=>{ const b=HOUSE.bag(); const s=b.find(x=>x.en==='shark' && x.sh), n=b.find(x=>x.en==='shark' && !x.sh); return [HOUSE.price(s), HOUSE.price(n)]; }")
        ok(r[0] > r[1] * 3, f"반짝이·큰 것은 훨씬 비쌈 {r}")
        # 작은 것 = 바로 (줄다리기 없음)
        await E("()=>HOUSE.fishTap(7,6)"); await until("()=>HOUSE.F.st==='wait'", 200)
        await E("()=>{ HOUSE.bite(); const F=HOUSE.F; F.fish=HOUSE.FISH.find(f=>f.en==='snail'); F.cm=4; F.sh=0; HOUSE.tapWhileFishing(); }")
        ok(await E("()=>HOUSE.F.st==='reel'"), "작은 것은 줄다리기 없이 바로")
        await until("()=>document.getElementById('quiz').classList.contains('on')", 60); await E("()=>document.getElementById('qOk').click()"); await until("()=>HOUSE.F.st==='idle'")
        # ④ 시간·비·황금 떼
        r = await E("()=>{ return [7,12,18,23].map(h=>HOUSE.tod(Date.UTC(2026,9,27,0)+((h-9+24)%24)*3600e3)); }")
        ok(r == ["a", "d", "e", "n"], f"한국 시간 7·12·18·23시 = 아침·낮·저녁·밤 {r}")
        r = await E("()=>{ const f=n=>HOUSE.FISH.find(x=>x.en===n); return {mermaid:HOUSE.canAppear(f('mermaid')), croc:HOUSE.canAppear(f('crocodile')), tod:HOUSE.tod()}; }")
        ok(r["mermaid"] is False, "인어는 평소엔 안 나옴")
        ok(r["croc"] == (r["tod"] == "n"), f"악어는 밤에만 {r}")
        await E("()=>HOUSE.setRush(true)"); await pg.wait_for_timeout(600)
        r = await E("()=>[HOUSE.canAppear(HOUSE.FISH.find(x=>x.en==='mermaid')), document.getElementById('hEnv').innerText, document.getElementById('hEnv').classList.contains('ru')]")
        ok(r[0] and "✨" in r[1] and r[2], f"✨ 황금 물고기 떼 → 인어 가능 · 위에 남은 시간 {r[1]}")
        await E("()=>HOUSE.setWx(true)"); await pg.wait_for_timeout(1500)
        ok(await E("()=>document.body.classList.contains('rain') && /🌧/.test(document.getElementById('hEnv').innerText)"), "🌧 비 → 마당에 비 · 위에 표시")
        await pg.screenshot(path=OUT + "fish414_rain.png")
        await E("()=>document.getElementById('hEnv').click()"); await pg.wait_for_timeout(300)
        ok(await E("()=>/오늘의 물고기/.test(document.getElementById('info').innerText)"), "날씨 단추 → 지금 나오는 것 · ⭐ 오늘의 물고기")
        await E("()=>{ const b=[...document.querySelectorAll('#info button')].pop(); b && b.click(); }")
        # 도감
        await E("()=>document.getElementById('bDex').click()"); await pg.wait_for_timeout(500)
        r = await E("()=>[!!document.querySelector('#dexBody .dexNow'), document.querySelector('#dexBody [data-say=shark]')?.innerText||'', document.querySelectorAll('#dexBody .dH').length]")
        ok(r[0] and "3.8 m" in r[1] and "✨" in r[1], f"도감: 지금 날씨 · 가장 큰 크기 · 반짝이 {r[1]!r}")
        ok(r[2] >= 8, f"도감: 언제 나오는지 힌트 {r[2]}")
        await pg.screenshot(path=OUT + "fish414_dex.png")
        await E("()=>document.getElementById('dexDone').click()")
        await E("()=>HOUSE.go('room')"); await until("()=>HOUSE.place()==='room'")
        await pg.wait_for_timeout(1200)
        ok(await E("()=>!document.body.classList.contains('rain') && document.getElementById('hEnv').hidden"), "집 안엔 비 안 옴")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
