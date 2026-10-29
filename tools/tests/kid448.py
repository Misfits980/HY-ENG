"""(v448) 🎲 아이들끼리 보드게임 + 액션 미니게임 5개 더
  사용자: "아이들끼리 방을 만들어서 하는 보드게임은 어떻게 열 거야? 지금은 관리자 모드로만" → 둘 다 · 한 패드는 관리자 모드에서 켜고 끄기
  ① 🎮 수업 게임 창: 「🎲 친구랑 보드게임 방 만들기」(언제나) · 「🪑 한 패드로 같이」(관리자가 켰을 때만)
  ② 방장 패드 = 판 + 같이 플레이: 방장이 먼저 · 친구 차례 카드는 못 누름 · 미니게임도 방장 화면에서 · 점수 막대
  ③ 액션 ⏱ 10초 멈추기 · 🔢 숫자 · 🍎 과일 · 🧱 탑 · 🏃 점프"""
import asyncio, sys, os
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
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e))); await boot(H)
        async def until(pg, js, n=60, ms=200):
            for _ in range(n):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(ms)
            return False
        await H.evaluate("()=>FB.set('/hy/roster',{t:{a1:{n:'1반',e:'🍎'}}, k:{k1:{n:'루아',t:'a1'}, k2:{n:'주호',t:'a1'}, k3:{n:'라언',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        # ③ 새 액션 게임
        r = await H.evaluate("()=>[MiniG.ACT.length, ['stop','num','fruit','stack','jump'].every(k=>MiniG.ACT.indexOf(k)>=0)]")
        ok(r == [10, True], f"③ 액션 10개 {r}")
        MOUNT = """(k)=>{ const old=document.getElementById('tg'); if(old) old.remove(); const d=document.createElement('div'); d.id='tg'; d.style.cssText='position:fixed;inset:0;z-index:999;display:flex'; d.innerHTML='<div class="mgG" id="tgG" style="flex:1"></div>'; document.body.appendChild(d);
            const S=MiniG.seq(Study.lessons('elem')[0].ws, k); window._g=MiniG.mount(document.getElementById('tgG'), k, S, 'e', {i:0,k:0,col:Board.COL[0]}); return 1; }"""
        await H.evaluate(MOUNT, "stop")
        r = await H.evaluate("()=>{ const g=window._g; g.step(1); g.step(3); const hid=g.host.firstChild.classList.contains('hid'); g.t=9.88; g.stopIt(); return [hid, g.sc, g.host.innerText.replace(/\\n/g,' ')]; }")
        ok(r[0] and r[1] == 88, f"⏱ 3초 뒤 숨김 · 9.88초 = 88점 {r}")
        await H.evaluate(MOUNT, "num")
        r = await H.evaluate("()=>{ const g=window._g; for(let i=0;i<5;i++) g.auto(); const a=g.sc; g.wrong(); return [a, g.sc, g.k]; }")
        ok(r == [5, 5, 6], f"🔢 1~5 차례대로 +5 · 틀린 숫자 = 점수 그대로 {r}")
        r = await H.evaluate("()=>{ const g=window._g; g.lock=0; while(g.k<=g.n){ g.lock=0; g.auto(); } return [g.sc, g.n]; }")
        ok(r[0] == r[1] + 3, f"🔢 다 누르면 +3 보너스 {r}")
        await H.evaluate(MOUNT, "fruit")
        r = await H.evaluate("()=>{ const g=window._g; g.auto(); g.auto(); const a=g.sc; g.wrong(); return [a, g.sc]; }")
        ok(r[0] in (2, 4, 6) and r[1] == r[0] - 2, f"🍎 과일 +1 (🌟 +3) · 💣 −2 {r}")
        await H.evaluate(MOUNT, "stack")
        r = await H.evaluate("()=>{ const g=window._g; g.auto(); g.auto(); const a=[g.sc, g.h, g.L.length]; g.mv.x=g.L[g.L.length-1].x+10; g.lock=0; g.drop(); return a.concat([g.sc, +g.L[g.L.length-1].w.toFixed(1)]); }")
        ok(r[0] == 4 and r[1] == 2 and r[3] == 5 and r[4] == 30.0, f"🧱 딱 맞으면 +2 · 어긋나면 겹친 만큼(40→30) {r}")
        await H.evaluate(MOUNT, "jump")
        r = await H.evaluate("()=>{ const g=window._g; g.jump(); const a=g.vy>0; for(let i=0;i<200;i++) g.step(0.02); return [a, g.os.length>0, g.sc]; }")
        ok(r[0] and r[1], f"🏃 톡 = 점프 · 장애물이 나옴 {r}")
        await H.evaluate("()=>{ window._g.dead=1; document.getElementById('tg').remove(); }")
        # ① 🎮 수업 게임 창
        await H.evaluate("()=>RaidJoin.open()"); await H.wait_for_timeout(500)
        r = await H.evaluate("()=>[!!document.querySelector('[data-rj=bdhost]'), !!document.querySelector('[data-rj=bdpad]')]")
        ok(r == [True, False], f"① 「방 만들기」 있음 · 「한 패드」는 꺼져 있어 안 보임 {r}")
        await H.screenshot(path=OUT + "kid448_join.png")
        await H.evaluate("()=>document.querySelector('[data-rj=bdhost]').click()")
        ok(await H.evaluate("()=>/이름/.test(document.getElementById('rdJoinMsg').textContent)"), "① 이름 없이 누르면 「이름을 먼저」")
        await H.evaluate("()=>{ document.querySelector('[data-rjn=k1]').click(); }"); await H.wait_for_timeout(200)
        await H.evaluate("()=>document.querySelector('[data-rj=bdhost]').click()")
        ok(await until(H, "()=>/^\\d{4}$/.test((document.getElementById('lbRoom')||{}).textContent||'') && document.querySelectorAll('#lbKids .lbKid').length===1"), "② 방장 로비 · 방장 이름이 먼저 있음")
        r = await H.evaluate("()=>[document.querySelector('.bdLob').innerText.replace(/\\n/g,' ').slice(0,160), document.getElementById('lbMode').innerHTML, document.getElementById('lbGo').disabled]")
        ok("방장 루아" in r[0] and r[1] == "" and r[2], f"② 개인전만 · 친구 기다림 {r[0][:90]!r}")
        await H.screenshot(path=OUT + "kid448_lobby.png")
        room = await H.evaluate("()=>BoardTV.room")
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate("()=>HyBoss.refresh(true)"); await K.evaluate(f"()=>BoardPad.join('{room}', {{id:'k2', n:'주호', t:'a1'}})")
        ok(await until(H, "()=>document.querySelectorAll('#lbKids .lbKid').length===2 && !document.getElementById('lbGo').disabled"), "② 친구 들어옴 → 시작 단추")
        await H.evaluate("()=>document.querySelector('[data-lb=len][data-n=\"15\"]').click()")
        await H.evaluate("()=>document.getElementById('lbGo').click()")
        ok(await until(H, "()=>Board.o && Board.o.R===15 && Board.o.P[0].n==='루아' && document.getElementById('board').classList.contains('kidHost')"), "② 시작 · 15라운드 · 방장 먼저")
        await until(H, "()=>!!document.getElementById('bdHow')", 20); await H.evaluate("()=>{ const b=document.querySelector('#bdHow [data-how]'); if(b) b.click(); }")
        ok(await until(H, "()=>!!document.querySelector('#bdAct .bdRoll') && !document.getElementById('bdAct').classList.contains('khWait')", 40), "② 방장 차례 = 방장 화면에서 누름")
        await H.screenshot(path=OUT + "kid448_myturn.png")
        await H.evaluate("()=>{ Board.o.force=1; document.querySelector('#bdAct .bdRoll').click(); }")
        ok(await until(H, "()=>Board.o.cur===1 || !!document.querySelector('#bdAct [data-bd]:not(.bdRoll)')", 60), "② 방장이 굴림")
        # 남은 카드가 있으면 아무거나 (별·상점 등)
        for _ in range(6):
            if await H.evaluate("()=>Board.o.cur===1"): break
            await H.evaluate("()=>{ const b=document.querySelector('#bdAct [data-bd=skip], #bdAct [data-bd=back], #bdAct [data-bd=opt]'); if(b) b.click(); }"); await H.wait_for_timeout(900)
        ok(await until(H, "()=>Board.o.cur===1 && document.getElementById('bdAct').classList.contains('khWait')", 60), "② 친구 차례 = 방장 화면 카드 못 누름")
        ok(await until(K, "()=>!!document.querySelector('#bpBody [data-bd=roll]')", 40), "② 친구 패드에 🎲")
        await H.screenshot(path=OUT + "kid448_wait.png")
        n0 = await H.evaluate("()=>Board.o.P[1].pos")
        await H.evaluate("()=>{ const b=document.querySelector('#bdAct .bdRoll'); if(b) b.click(); }"); await H.wait_for_timeout(600)
        ok(await H.evaluate(f"()=>Board.o.P[1].pos==={n0} && Board.o.cur===1"), "② 방장이 친구 굴리기를 눌러도 안 됨")
        # 미니게임 — 방장도 함
        await H.evaluate("()=>{ clearTimeout(Board._to); BoardTV.rq=null; Board.o.mgOnly='tug'; Board.act(''); Board.mini(); }")
        ok(await until(H, "()=>!!document.getElementById('khG') && document.getElementById('bdTvMG').classList.contains('kh')", 40), "② 방장 화면에 내 미니게임 + 작은 점수 막대")
        ok(await until(H, "()=>!document.getElementById('khIn') && !!document.querySelector('#khG .mgTugB')", 60), "② 같은 시각에 시작")
        for _ in range(12):
            await H.evaluate("()=>{ const b=document.querySelector('#khG .mgTugB'); if(b) b.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }"); await H.wait_for_timeout(60)
        await K.evaluate("()=>{ for(let i=0;i<4;i++) BoardPad.g && BoardPad.g.auto(); }")
        await H.wait_for_timeout(800)
        await H.screenshot(path=OUT + "kid448_mg.png")
        ok(await until(H, "()=>/루아/.test((document.querySelector('#tmBars')||{}).innerText||'') && /12/.test(document.getElementById('tmBars').innerText)", 30), "② 방장 점수가 막대에")
        ok(await until(H, "()=>!!document.getElementById('bdPod')", 80), "② 🏆 시상대")
        r = await H.evaluate("()=>document.querySelector('#bdPod .podC.r1 b').innerText")
        ok(r == "루아", f"② 1등 루아 {r}")
        await H.evaluate("()=>{ Board.close(); BoardTV.stop(); }")
        # ① 관리자 켜기 → 「한 패드로 같이」
        await H.evaluate("()=>FB.set('/hy/roster/bd/pad', 1).then(()=>HyBoss.refresh(true))")
        await H.evaluate("()=>RaidJoin.open()"); await H.wait_for_timeout(500)
        ok(await H.evaluate("()=>!!document.querySelector('[data-rj=bdpad]')"), "① 관리자가 켜면 「🪑 한 패드로 같이」")
        await H.evaluate("()=>document.querySelector('[data-rj=bdpad]').click()"); await H.wait_for_timeout(500)
        r = await H.evaluate("()=>[!!document.getElementById('bdSetup'), document.querySelector('.bdModeT').hidden, Board._mode, document.querySelector('.bdSetHd b').textContent]")
        ok(r[0] and r[1] and r[2] == "pad", f"① 한 패드 설정 (📺 모드 없음) {r}")
        await H.screenshot(path=OUT + "kid448_pad.png")
        # ① 관리자 화면 켜기·끄기 단추
        A = await ctx.new_page(); A.on("pageerror", lambda e: errs.append("A " + str(e))); await boot(A)
        await A.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }")
        await A.reload(); await A.wait_for_timeout(1500)
        await A.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); Admin._tab('now'); }")
        ok(await until(A, "()=>!!document.querySelector('[data-ad=bdPad].on')", 40), "① 관리자: 「한 패드로 같이」 켜짐 표시")
        await A.evaluate("()=>{ const b=document.querySelector('[data-ad=bdPad]'); b.scrollIntoView({block:'center'}); }"); await A.wait_for_timeout(300)
        await A.screenshot(path=OUT + "kid448_admin.png")
        await A.evaluate("()=>document.querySelector('[data-ad=bdPad]').click()")
        ok(await until(A, "()=>!!document.querySelector('[data-ad=bdPad]:not(.on)')", 40), "① 관리자: 누르면 꺼짐")
        r = await A.evaluate("()=>FB.get('/hy/roster/bd/pad')")
        ok(r is None, f"① 서버 값 지워짐 {r}")
        await A.evaluate("()=>document.querySelector('[data-ad=bdPad]').click()")
        ok(await until(A, "()=>!!document.querySelector('[data-ad=bdPad].on')", 40) and await A.evaluate("()=>FB.get('/hy/roster/bd/pad')") == 1, "① 다시 누르면 켜짐")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
