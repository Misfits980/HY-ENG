"""(v304) 🏫 교실 배틀 — 선생님 1 · 아이 3 (이 기기 안 Firebase 흉내): 입장 창으로 방 번호 → 배틀로 연결 · 3·2·1 · 점수 · 순위 · 끝 보석(1등 5 · 2등 3 · 3등 2)"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1024,"height":700})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e))); await boot(host)
        room=await host.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:20, team:false, lbl:'G5-6 Stage 1-1~1-3'})"); print("room", room)
        kids=[]; skill=[0.95, 0.7, 0.4]
        for i,nm in enumerate(["민준","서연","지호"]):
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844}); await boot(k)
            await k.evaluate("()=>{ RaidJoin.open(); }"); await k.wait_for_timeout(100)
            await k.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='{nm}'; document.querySelector('[data-rj=go]').click(); }}")
            await k.wait_for_timeout(400); await k.evaluate("()=>{ Battle.FAST=0; }"); kids.append(k)
        role=await kids[0].evaluate("()=>[Battle.role, Raid.role]"); print("role", role)
        if role[0]!="kid": bad.append(f"입장 창이 배틀로 안 감 {role}")
        await host.wait_for_timeout(300); await host.screenshot(path=OUT+"bt_host_wait.png")
        await host.evaluate("()=>Battle.hostAct('start')"); await host.wait_for_timeout(1500); await kids[0].screenshot(path=OUT+"bt_kid_count.png"); await host.wait_for_timeout(2300)
        import random; random.seed(1)
        for step in range(400):
            for i,k in enumerate(kids):
                good = random.random()<skill[i]
                await k.evaluate("(g)=>{ const q=Battle.q; if(!q||q.done) return; let i=q.opts.findIndex(o=>o.en===q.w.en); if(!g) i=(i+1)%q.opts.length; Battle.answer(i); }", good)
            if step==30: await host.screenshot(path=OUT+"bt_host_run.png"); await kids[1].screenshot(path=OUT+"bt_kid_run.png")
            await host.wait_for_timeout(60)
            if await host.evaluate("()=>Battle.st().s==='end'"): break
        await host.wait_for_timeout(1200)
        res=[await k.evaluate("()=>[Battle.ended, Battle.sc, Battle.rank().indexOf(Battle.me)+1, Battle._gems]") for k in kids]
        print("res", res)
        await host.screenshot(path=OUT+"bt_host_end.png"); await kids[0].screenshot(path=OUT+"bt_kid_end.png")
        if not all(r[0] for r in res): bad.append("안 끝난 아이")
        g={r[2]:r[3] for r in res}
        if g.get(1)!=5 or g.get(2)!=3 or g.get(3)!=2: bad.append(f"순위 보석 {g}")
        print("errs", errs[:5]); await br.close()
    print("결과:", "통과 ✅" if not bad and not errs else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or errs: sys.exit(1)
asyncio.run(main())
