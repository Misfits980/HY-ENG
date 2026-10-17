"""(v302) ⚔️ 수업 레이드 — 같은 브라우저 탭 4개(선생님 1 · 아이 3)로 BroadcastChannel 방: 입장 · 시작 · 공격 · 막기 · 방패 · 쓰러뜨림 · 보석"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
O=OUT
ANS="""()=>{ const R=Raid, q=R.atk ? R.atk.q : R.q; if(!q || q.done || (R.atk && !R.atk.shown)) return 'none'; const k=q.opts.findIndex(o=>o.en===q.w.en); R.answer(k); return (R.atk?'blk':q.sh?'sh':'hit'); }"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1024,"height":700}); errs=[]
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e)))
        await boot(host); room=await host.evaluate("()=>Raid.host('g34',['vest','cap','glove','beard','belt'])"); print("room", room)
        kids=[]
        for nm in ["민준","서연","지호"]:
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844})
            await boot(k); await k.evaluate(f"()=>{{ Raid.FAST=0; Raid.join('{room}','{nm}'); }}"); kids.append(k)
        await host.wait_for_timeout(500); await host.screenshot(path=O+"30_host_wait.png"); await kids[0].screenshot(path=O+"31_kid_wait.png")
        await host.evaluate("()=>Raid.hostAct('start')"); await host.wait_for_timeout(800)
        print("max", await host.evaluate("()=>Raid.calc().max"))
        await kids[0].screenshot(path=O+"32_kid_q.png")
        kinds={}
        for step in range(400):
            for k in kids:
                r=await k.evaluate(ANS); kinds[r]=kinds.get(r,0)+1
            await host.wait_for_timeout(120)
            c=await host.evaluate("()=>{ const c=Raid.calc(); return [c.hp, c.shield, c.rage, Raid.st().s] }")
            if step==5: await host.screenshot(path=O+"33_host_run.png")
            if c[1] and not kinds.get('shot'): kinds['shot']=1; await kids[1].wait_for_timeout(700); await kids[1].screenshot(path=O+"34_kid_shield.png"); await host.screenshot(path=O+"35_host_shield.png")
            if any([await k.evaluate("()=>!!(Raid.atk && Raid.atk.shown && !Raid.atk.res)") for k in kids]) and not kinds.get('ashot'):
                kinds['ashot']=1
                for k in kids:
                    if await k.evaluate("()=>!!(Raid.atk && Raid.atk.shown)"): await k.screenshot(path=O+"36_kid_block.png"); break
            if c[3]=="end": break
        print("kinds", kinds, "final", c)
        await host.wait_for_timeout(2600); await host.screenshot(path=O+"37_host_end.png"); await kids[0].screenshot(path=O+"38_kid_end.png")
        # (v310) 🏆 시상식 — TV 가 상을 정해 적고, 아이 기기는 칭호 + 💎3
        aw=await host.evaluate("()=>(Raid.awList(Raid.st())||[]).map(x=>[x.id,x.n])"); print("awards", aw)
        mine=await kids[0].evaluate("()=>[(Raid._myAw||[]).map(x=>x.id), TITLES.filter(t=>/^t-r-/.test(t.id) && Wallet.owns(t.id)).map(t=>t.id), document.querySelectorAll('.rdAwC').length]"); print("kid0 aw", mine)
        tot=0
        for k in kids: tot+=await k.evaluate("()=>(Raid._myAw||[]).length")
        print("kid0", await kids[0].evaluate("()=>[Raid.dmg, Raid.blk, Raid.shk, Wallet.gems()]"))
        bad=[]
        n=await host.evaluate("()=>Object.keys(RaidNet.get().p||{}).length")
        k0=await kids[0].evaluate("()=>[Raid.dmg, Raid.blk, Raid.shk, Raid._gems|0]")
        if n!=3: bad.append(f"접속 {n}명")
        if c[3]!="end" or c[0]!=0: bad.append(f"끝 {c}")
        if not kinds.get('sh'): bad.append("방패 단어 없음")
        if not k0[3]: bad.append(f"보석 {k0}")
        if len(aw)<4 or aw[0][0]!="mvp" or not any(x[0]=="last" for x in aw): bad.append(f"시상식 {aw}")
        if tot!=len(aw): bad.append(f"아이 기기 상 {tot} != {len(aw)}")
        if mine[2]<4: bad.append(f"아이 화면 시상식 카드 {mine}")
        if not await host.evaluate("()=>!!document.querySelector('.rdAw.big .rdAwC')"): bad.append("TV 시상식")
        print("errs", errs[:5]); await br.close()
        print("결과:", "통과 ✅" if not bad and not errs else "실패 ❌"); [print(" BAD", b) for b in bad]
        if bad or errs: sys.exit(1)
asyncio.run(main())
