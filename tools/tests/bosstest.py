"""(v303) 👹 학원 보스 · 반 대항전 — 탭 4개(선생님 1 · 아이 3)로 이 기기 안 Firebase 흉내(HY_FB_LOCAL):
   반 명단 만들기 → 반 대항 보스 → 수업 레이드에서 반마다 깎기 → 한 반 쓰러뜨림 → 보상 나눔(똑같이) · 집 공부(Daily 30 판 끝) 데미지 하루 300 까지"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ANS="""()=>{ const R=Raid, q=R.atk ? R.atk.q : R.q; if(!q || q.done || (R.atk && !R.atk.shown)) return 'none'; const k=q.opts.findIndex(o=>o.en===q.w.en); R.answer(k); return 'x'; }"""
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1024,"height":700})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e)))
        await boot(host)
        await host.evaluate("""()=>{ HyBoss.start(); FB.set('/hy/roster', {t:{ta:{n:'사자반',e:'🦁'}, tb:{n:'돌고래반',e:'🐬'}}, k:{k1:{n:'민준',t:'ta'}, k2:{n:'서연',t:'ta'}, k3:{n:'지호',t:'tb'}}}); }""")
        await host.wait_for_timeout(200)
        await host.evaluate("()=>HyBoss.make({n:'시험 문지기', per:300, gems:30, split:'eq', team:true, words:[]})")
        await host.wait_for_timeout(300)
        b=await host.evaluate("()=>({max:HyBoss.B.max, team:HyBoss.B.team})"); print("boss", b)
        if not b["team"] or set(b["max"].keys())!={"ta","tb"}: bad.append(f"반 대항 보스 {b}")
        room=await host.evaluate("()=>Raid.host('g34',[])")
        kids=[]
        for kid,nm,t in [("k1","민준","ta"),("k2","서연","ta"),("k3","지호","tb")]:
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844})
            await boot(k); await k.evaluate(f"()=>{{ Raid.FAST=0; HyBoss.start(); }}"); await k.wait_for_timeout(200)
            await k.evaluate(f"()=>{{ const v={{id:'{kid}',n:'{nm}',t:'{t}'}}; Kid.set(v); Raid.join('{room}', v); }}"); kids.append(k)
        await host.wait_for_timeout(400); await host.evaluate("()=>Raid.hostAct('start')"); await host.wait_for_timeout(500)
        for step in range(500):
            for k in kids: await k.evaluate(ANS)
            await host.wait_for_timeout(80)
            st=await host.evaluate("()=>({a:HyBoss.state('ta'), b:HyBoss.state('tb')})")
            if st["a"]["dead"]: break
        print("states", json.dumps(st, ensure_ascii=False)[:300])
        await host.screenshot(path=OUT+"boss_host.png")
        if not st["a"]["dead"]: bad.append("사자반 보스가 안 쓰러짐")
        if st["b"]["dead"]: bad.append("돌고래반(1명)이 먼저 쓰러뜨림?")
        await kids[0].wait_for_timeout(1500); await kids[0].screenshot(path=OUT+"boss_kid_end.png")
        c0=await kids[0].evaluate("()=>[Raid.ended, Raid._claim, Wallet.paid('bs-'+HyBoss.B.id)]")
        c2=await kids[2].evaluate("()=>[Raid.ended, Raid._claim]")
        print("claim 민준", c0, "지호", c2)
        if not c0[0] or c0[1]!=15: bad.append(f"사자반 보상(30÷2=15) {c0}")
        if c2[0]: bad.append(f"돌고래반은 아직 끝나면 안 됨 {c2}")
        # 집 공부 — 지호가 Daily 30 한 판 끝 → 데미지 (하루 300 까지)
        k=kids[2]
        await k.evaluate("()=>{ Raid.leave(); }"); await k.wait_for_timeout(300)
        d0=await k.evaluate("()=>HyBoss.mine('k3').d|0")
        await k.evaluate("()=>{ StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.path(); StudyUI.start(0,false); }")
        for i in range(300):
            await k.evaluate(SOLVE, False); await k.wait_for_timeout(15)
            if await k.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
        await k.wait_for_timeout(300)
        d1=await k.evaluate("()=>[HyBoss.mine('k3').d|0, ((HyBoss.mine('k3').on||{})[Study.today()])|0, !!document.querySelector('.stBossAdd')]")
        print("home dmg", d0, d1)
        if not (d1[0]>d0 and 0<d1[1]<=300 and d1[2]): bad.append(f"집 공부 데미지 {d0} {d1}")
        await k.evaluate("()=>document.getElementById('stBack').click()"); await k.wait_for_timeout(300)
        card=await k.evaluate("()=>document.getElementById('stBossCard').innerText")
        print("card", card.replace("\n"," / "))
        await k.screenshot(path=OUT+"boss_card.png")
        if "돌고래반" not in card: bad.append("보스 카드 반 이름")
        print("errs", errs[:5]); await br.close()
    print("결과:", "통과 ✅" if not bad and not errs else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or errs: sys.exit(1)
asyncio.run(main())
