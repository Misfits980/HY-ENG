"""(v396) 사용자: 게임마다 연계가 정확한지 — QA 에서 찾은 구멍
  · 📌 숙제 진행은 아이가 Stage 를 끝낸 바로 뒤 선생님께 (예전엔 「스테이지로 돌아가기」로 길 화면을 열어야만 갔다 → 끝내고 앱을 닫으면 선생님은 0/2)
  · Daily 30 한 Stage → 💎 · 오늘의 미션 · ⚔️ 공격 기회 · 📅 오늘 한 아이 · 시트(study) · 도감/등급 기록"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("""()=>{ window._subs=[]; Online.on=()=>true; Online.submit=o=>{ window._subs.push(o); return Promise.resolve({ok:true}); }; Online.top=()=>Promise.resolve(null); Voice.canListen=()=>true; HyBoss.live();
          return FB.set('/hy/roster', {t:{a:{n:'초등반'}}, k:{k1:{n:'민준',t:'a'}}}).then(()=>HyBoss.setup({on:true, team:true, split:'eq', restart:true})).then(()=>FB.set('/hy/hw/cur', {ha:{id:'ha', on:1, team:'a', set:'mid', from:60, to:61, goal:1, due:Date.now()+864e5*3, title:'숙제', at:1}})); }"""); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ Kid.set({id:'k1',n:'민준',t:'a'}); return Promise.all([HyBoss.refresh(true), HyHW.check(true)]); }"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ StudyUI.open(); StudyUI.book='mid'; StudyUI.set='mid'; StudyUI.path(); }"); await pg.wait_for_timeout(500)
        g0 = await pg.evaluate("()=>Wallet.gems()")
        for stg in (60, 61):
            await pg.evaluate("(i)=>StudyUI.start(i,false)", stg); await pg.wait_for_timeout(300)
            for s in range(200):
                if not await pg.evaluate("()=>!!StudyUI.qs[StudyUI.i]"): break
                await pg.evaluate(SOLVE, False)
                if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
                await pg.wait_for_timeout(25)
            await pg.wait_for_timeout(1000)   # (길 화면으로 돌아가지 않음)
            r = await pg.evaluate("()=>FB.get('/hy/hw/res/ha/k1')")
            ok(r and r.get("done") == stg - 59 and r.get("tot") == 2, f"Stage {stg} 끝난 바로 뒤 선생님께 숙제 {stg-59}/2 {r and (r.get('done'), r.get('tot'))}")
            if stg == 60:
                await pg.evaluate("()=>{ [...document.querySelectorAll('#stDone button')].find(x=>/다음 스테이지/.test(x.textContent)).click(); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[Wallet.gems(), DM.list().map(m=>m.id+':'+m.n).join(','), HyBoss.stock('k1').s, window._subs.map(s=>s.diff).join(','), FB.get('/hy/day/'+HyDay.key()+'/k1').then(d=>d&&d.s)]")
        day = await pg.evaluate("()=>FB.get('/hy/day/'+HyDay.key()+'/k1').then(d=>d&&d.s)")
        ok(r[0] > g0, f"💎 올라감 {g0}→{r[0]}")
        ok("les" in r[1] or "q20" in r[1] or "q30" in r[1], f"오늘의 미션에 공부가 셈 {r[1]}")
        ok(r[2] > 0, f"⚔️ 공격 기회 {r[2]}")
        ok("study" in r[3], f"시트 전송 {r[3]}")
        ok((day or 0) >= 2, f"📅 오늘 한 아이 공부 {day}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:2]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
