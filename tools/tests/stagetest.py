"""(v307) ⚔️ 레이드 무대 — 내 캐릭터·친구·보스가 움직이는지: 맞히면 달려가 때림(숫자·번쩍) · 틀리면 비틀 · 보스 공격 예고(빨간 테두리) → 못 막으면 밀려남 · 막으면 방패 · TV 는 모두 줄 서서 · 쓰러뜨리면 사라짐"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ANS="(good)=>{ const R=Raid, q=R.atk ? R.atk.q : R.q; if(!q || q.done || (R.atk && !R.atk.shown)) return 'none'; let k=q.opts.findIndex(o=>o.en===q.w.en); if(!good) k=(k+1)%q.opts.length; R.answer(k); return R.atk?'atk':'q'; }"
async def main():
    bad=[]; errs=[]; shots=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1280,"height":760})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e))); await boot(host)
        room=await host.evaluate("()=>Raid.host('g34',[],3)")
        kids=[]
        for nm,ch in [("민준","knight"),("서연","wolf"),("지호","mage")]:
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844}); await boot(k)
            await k.evaluate(f"()=>{{ G.char='{ch}'; Raid.FAST=0; Raid.join('{room}','{nm}'); }}"); kids.append(k)
        await host.wait_for_timeout(600); await host.evaluate("()=>Raid.hostAct('start')"); await host.wait_for_timeout(800)
        k0=kids[0]
        info=await k0.evaluate("()=>{ const s=document.getElementById('rdStage'); return [!!s.querySelector('.rsHero.me'), (s.querySelector('.rsHero.me .rsSpr')||{}).style.backgroundImage, s.querySelectorAll('.rsAllies .rsHero').length, !!s.querySelector('.rsBoss img')]; }")
        print("kid stage", info)
        if not info[0] or "run-knight" not in (info[1] or "") or info[2]!=2 or not info[3]: bad.append(f"아이 무대 {info}")
        # 맞히기 → 달려감 · 숫자
        r=await k0.evaluate(ANS, True); await k0.wait_for_timeout(90)
        d=await k0.evaluate("()=>[RaidStage.me.dash, (RaidStage.me.el.style.transform||'')]"); await k0.wait_for_timeout(120)
        n=await k0.evaluate("()=>[document.querySelectorAll('#rdStage .rsNum').length, document.querySelector('#rdStage .rsBossIn').classList.contains('hit')]")
        print("hit", r, d, n)
        if not d[0] or n[0]<1 or not n[1]: bad.append(f"맞히면 달려가 때림 {d} {n}")
        for i in range(10):   # 기록용 연속 공격 (GIF)
            await k0.evaluate(ANS, True); await kids[1].evaluate(ANS, True)
            for j in range(3):
                await k0.wait_for_timeout(110); shots.append(await k0.screenshot(clip={"x":0,"y":0,"width":390,"height":470}))
            await k0.wait_for_timeout(500)
        # 친구 공격 → 친구 캐릭터가 달려감
        await kids[1].evaluate(ANS, True)   # (v311) 바쁠 때도 — 바로 앞에서 한 번 더 공격하고 몇 초 기다림
        try: await k0.wait_for_function("()=>Object.values(RaidStage.al).some(a=>a.dashT && Date.now()-a.dashT<4000)", timeout=6000); ad=True
        except Exception: ad=False
        print("ally dash", ad)
        if not ad: bad.append("친구가 공격해도 안 움직임")
        # 틀리기
        await k0.wait_for_timeout(700)
        for t in range(40):   # 문제가 준비될 때까지 (보스 공격·쉬는 중이면 기다림)
            if await k0.evaluate("()=>{ const R=Raid; return !!(R.q && !R.q.done && !R.atk); }"): break
            await k0.wait_for_timeout(150)
        await k0.evaluate(ANS, False); await k0.wait_for_timeout(60)
        if not await k0.evaluate("()=>RaidStage.me.el.classList.contains('oops')"): bad.append("틀리면 비틀 없음")
        # 보스 공격: 예고 → 못 막음
        await k0.wait_for_timeout(1600)
        await k0.evaluate("()=>{ Raid.atk=null; Raid.nextAtk=1; Raid.restTo=0; }"); await k0.wait_for_timeout(400)
        w=await k0.evaluate("()=>[document.getElementById('rdStage').classList.contains('warn'), (document.querySelector('#rdStage .rsAtkName')||{}).textContent]"); print("warn", w)
        if not w[0] or "⚠️" not in (w[1] or ""): bad.append(f"공격 예고 {w}")
        for j in range(4): await k0.wait_for_timeout(250); shots.append(await k0.screenshot(clip={"x":0,"y":0,"width":390,"height":470}))
        await k0.wait_for_timeout(1700); r2=await k0.evaluate(ANS, False)
        for j in range(6): await k0.wait_for_timeout(150); shots.append(await k0.screenshot(clip={"x":0,"y":0,"width":390,"height":470}))
        hurt=await k0.evaluate("()=>[RaidStage.me.el.classList.contains('ouch'), document.querySelector('#rdStage .rsAtk').classList.contains('on')||true, Raid.hearts]"); print("hurt", r2, hurt)
        if not hurt[0]: bad.append(f"못 막으면 밀려남 {hurt}")
        await k0.screenshot(path=OUT+"stage_kid.png")
        # TV
        tv=await host.evaluate("()=>{ const s=document.getElementById('rdStage'); return [s.className, s.querySelectorAll('.rsAllies .rsHero').length, [...s.querySelectorAll('.rsName')].map(x=>x.textContent)]; }"); print("tv", tv)
        if "big" not in tv[0] or tv[1]!=3: bad.append(f"TV 무대 {tv}")
        await host.screenshot(path=OUT+"stage_tv.png")
        # 쓰러뜨림
        await k0.evaluate("()=>Raid.addDmg(99999,'hit')"); await k0.wait_for_timeout(900)
        dead=await host.evaluate("()=>document.getElementById('rdStage').classList.contains('dead')"); print("dead", dead)
        if not dead: bad.append("쓰러뜨려도 보스 그대로")
        print("errs", errs[:5]); await br.close()
    # GIF
    try:
        from PIL import Image; import io
        fr=[Image.open(io.BytesIO(b)).convert("RGB").resize((312,376)) for b in shots]
        fr[0].save(OUT+"stage_kid.gif", save_all=True, append_images=fr[1:], duration=120, loop=0)
    except Exception as e: print("gif", e)
    e=real_errs(errs)
    print("결과:", "통과 ✅" if not bad and not e else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or e: sys.exit(1)
asyncio.run(main())
