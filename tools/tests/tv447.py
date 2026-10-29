"""(v447) 📺 수업판 미니게임 — 사용자: "애들마다 시간이 제각각 · 누구는 끝나서 점수가 나오는데 누구는 시간이 넘었는데 계속 · 누가 이겼는지 확인이 안 됨"
  ① TV 가 서버 시각으로 시작·끝을 정함 → 모든 패드가 같은 순간에 시작·끝 (늦게 받은 패드도)
  ② 끝나면 TV·패드 모두 🏆 시상대 (내 자리 표시) → 🪙
  ③ 🎨 땅따먹기 = Firebase 로 서로 칠한 칸이 보임 · TV 에 판 · 점수 = 판에 남은 칸
  ④ 시작 안내 5장이 패드에도 · 🔄 자리 바꾸기 두 번 눌러도 한 번"""
import asyncio, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 1280, "height": 720}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        async def until(pg, js, n=60, ms=200):
            for _ in range(n):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(ms)
            return False
        await T.evaluate("()=>FB.set('/hy/roster',{t:{a1:{n:'1반',e:'🍎'}}, k:{k1:{n:'루아',t:'a1'}, k2:{n:'주호',t:'a1'}, k3:{n:'라언',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        await T.evaluate("()=>BoardTV.host({sk:'e', set:'elem', from:0, to:3, qt:['mean'], sec:20, rounds:10})")
        ok(await until(T, "()=>/^\\d{4}$/.test((document.getElementById('lbRoom')||{}).textContent||'')"), "로비")
        room = await T.evaluate("()=>BoardTV.room")
        K = []
        for i, (kid, n) in enumerate([("k1","루아"),("k2","주호"),("k3","라언")]):
            pg = await ctx.new_page(); await pg.set_viewport_size({"width": 820, "height": 1180}); pg.on("pageerror", lambda e, i=i: errs.append(f"K{i} " + str(e))); await boot(pg)
            await pg.evaluate("()=>HyBoss.refresh(true)"); await pg.evaluate(f"()=>BoardPad.join('{room}', {{id:'{kid}', n:'{n}', t:'a1'}})"); K.append(pg)
        ok(await until(T, "()=>document.querySelectorAll('#lbKids .lbKid').length===3"), "로비에 3명")
        await T.evaluate("()=>document.getElementById('lbGo').click()")
        ok(await until(T, "()=>!!document.getElementById('bdHow')", 40), "④ TV 시작 안내")
        ok(await until(K[0], "()=>!!document.getElementById('bpHow') && /우승/.test(document.getElementById('bpHow').innerText)", 40), "④ 패드에도 같은 안내 장")
        await K[0].screenshot(path=OUT + "tv447_how_pad.png")
        await T.evaluate("()=>document.querySelector('#bdHow [data-how]').click()")
        ok(await until(K[0], "()=>!document.getElementById('bpHow')", 40), "④ 안내 끝 → 패드도 닫힘")
        # 미니게임 강제 — 🎨 땅따먹기 (짧게 8초)
        await T.wait_for_timeout(800)
        await T.evaluate("()=>{ clearTimeout(Board._to); BoardTV.rq=null; const o=Board.o; o.mgOnly='paint'; MiniG.L.paint[2]=8; Board.act(''); Board.mini(); }")
        # 패드 하나는 늦게 받은 것처럼 (1.5초 동안 듣기 끊김 흉내)
        ok(await until(T, "()=>!!BoardTV.mgO && !!document.getElementById('tmPt')", 30), "③ TV 미니게임 창 · 땅따먹기 판")
        for pg in K:
            await pg.evaluate("()=>{ window._st=null; window._en=null; const f=MiniG.mount.bind(MiniG); MiniG.mount=function(){ window._st=Date.now(); return f(...arguments); }; }")
        ok(all([await until(pg, "()=>!!window._st", 60) for pg in K]), "① 모든 패드에서 시작")
        st = [await pg.evaluate("()=>window._st") for pg in K]
        go = await T.evaluate("()=>BoardTV.mgO ? BoardTV.mgO.go : 0")
        ok(max(st) - min(st) < 400, f"① 시작 시각 차이 {max(st)-min(st)}ms (TV go 와 {[s-go for s in st]})")
        # 칠하기 — 루아 많이, 주호 조금
        for _ in range(14):
            await K[0].evaluate("()=>BoardPad.g && BoardPad.g.auto()"); await K[0].wait_for_timeout(120)
        for _ in range(4):
            await K[1].evaluate("()=>BoardPad.g && BoardPad.g.auto()"); await K[1].wait_for_timeout(120)
        await K[0].wait_for_timeout(600)
        r = await K[2].evaluate("()=>{ const g=BoardPad.g; return g ? [g.sh.get().filter(v=>v===0).length, g.sh.get().filter(v=>v===1).length] : null; }")
        ok(r and r[0] >= 10 and r[1] >= 3, f"③ 라언 패드에 루아·주호가 칠한 칸이 보임 {r}")
        r = await T.evaluate("()=>[BoardTV.mgO.pt.filter(v=>v===0).length, BoardTV.mgO.pt.filter(v=>v===1).length, [...document.querySelectorAll('#tmPt i')].filter(i=>i._c).length]")
        ok(r[0] >= 10 and r[2] >= 13, f"③ TV 판에도 {r}")
        await T.screenshot(path=OUT + "tv447_paint_tv.png"); await K[0].screenshot(path=OUT + "tv447_paint_pad.png")
        # 끝 — 모두 같은 순간
        for pg in K:
            await pg.evaluate("()=>{ const iv=setInterval(()=>{ if(BoardPad.g && BoardPad.g.dead && !window._en){ window._en=Date.now(); clearInterval(iv); } }, 20); }")
        ok(all([await until(pg, "()=>!!window._en", 80) for pg in K]), "① 모든 패드 끝")
        en = [await pg.evaluate("()=>window._en") for pg in K]
        ok(max(en) - min(en) < 400, f"① 끝 시각 차이 {max(en)-min(en)}ms")
        ok(await until(K[1], "()=>/결과 발표/.test((document.querySelector('.bpMgEnd')||{}).innerText||'')", 20), "① 끝난 패드 = 「결과 발표를 기다려요」")
        # 시상대
        ok(await until(T, "()=>!!document.getElementById('bdPod')", 60), "② TV 🏆 시상대")
        ok(await until(K[0], "()=>!!document.getElementById('bpPod')", 40), "② 패드에도 🏆 시상대")
        r = await K[0].evaluate("()=>[document.querySelector('#bpPod .podC.r1 b').innerText, !!document.querySelector('#bpPod .me'), document.querySelector('#bpPod .podT').innerText]")
        ok(r[0] == "루아" and r[1] and "땅따먹기" in r[2], f"② 1등 루아 · 내 자리 표시 {r}")
        await T.screenshot(path=OUT + "tv447_pod_tv.png"); await K[0].screenshot(path=OUT + "tv447_pod_pad.png")
        ok(await until(T, "()=>!document.getElementById('bdPod')", 40), "② 시상대 끝")
        ok(await until(K[0], "()=>!document.getElementById('bpPod')", 40), "② 패드 시상대도 닫힘")
        r = await T.evaluate("()=>Board.o.P.map(p=>p.coin)")
        ok(r[0] >= 20, f"② 루아 🪙 +10 {r}")
        # 늦게 받은 패드 — 시작 시각이 지나서 받으면 남은 시간만
        await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ clearTimeout(Board._to); BoardTV.rq=null; Board.o.mgOnly='tug'; Board.act(''); Board.mini(); }")
        await K[2].evaluate("()=>{ BoardPad.h.close(); }")
        await T.wait_for_timeout(6500 + 4200)   # (v451) 시작 전 설명 4.2초 (MiniG.HOWMS)
        await K[2].evaluate("()=>{ window._st=null; BoardPad.h=FB.listen('/battle/'+BoardPad.room+'/st', s=>{ BoardPad.st=s||{}; BoardPad.draw(); }); }")
        ok(await until(K[2], "()=>!!BoardPad.g", 30), "① 늦게 받은 패드도 바로 시작")
        r = await K[2].evaluate("()=>{ const m=BoardPad.st.mg; return m ? [(m.end-BoardPad.now())/1000] : null; }")
        ok(r and r[0] < 9, f"① 늦은 패드 = 남은 시간만 {r}")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
