"""(v310) 🚩 반 깃발 레이스 + 새 배틀 문제 (철자 · 빈칸 글자 · ⭕❌ · 그림 · 듣기) — 선생님 1 · 아이 4 (사자반 2 · 돌고래반 2)
   깃발 칸 = 반 정답 합 ÷ 반 인원 · 먼저 목표에 닿은 반 우승 · 우승 반 💎4 · 나머지 💎2 · 문제 종류마다 정답 칸이 맞는지"""
import asyncio, json, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ANS="(g)=>{ const q=Battle.q; if(!q||q.done) return null; let i = q.ans!=null ? q.ans : q.opts.findIndex(o=>o.en===q.w.en); if(!g) i=(i+1)%q.opts.length; const t=q.t; Battle.answer(i); return [t, q.ok]; }"
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1280,"height":800})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e))); await boot(host)
        await host.evaluate("()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{ta:{n:'사자반',e:'🦁'}, tb:{n:'돌고래반',e:'🐬'}}, k:{k1:{n:'민준',t:'ta'},k2:{n:'서연',t:'ta'},k3:{n:'지호',t:'tb'},k4:{n:'하린',t:'tb'}}}); }"); await host.wait_for_timeout(300)
        # 문제 만들기만 먼저 — 종류마다 정답 칸
        chk=await host.evaluate("""()=>{ Battle._ws=null; Battle.h={get:()=>({cfg:{set:'elem', from:0, to:3, qt:['spell','gap','ox','pic','lsn','mean']}})}; const seen={}, wrong=[];
          for(let i=0;i<400;i++){ const q=Battle.mkQ(); Battle.q=q; seen[q.t]=(seen[q.t]||0)+1;
            if(q.t==='spell'){ if(q.lab[q.ans]!==q.w.en || new Set(q.lab).size!==q.lab.length || q.lab.length<3) wrong.push(['spell',q.lab,q.w.en]); }
            if(q.t==='gap'){ if(q.gap.replace('_', q.lab[q.ans])!==q.w.en || new Set(q.lab).size!==4) wrong.push(['gap',q.gap,q.lab]); }
            if(q.t==='ox'){ if((q.ko===q.w.ko)!==(q.ans===0)) wrong.push(['ox',q.ko,q.w.ko]); }
            if(q.t==='pic'){ if(q.opts[q.ans]!==q.w || !q.w.emoji) wrong.push(['pic',q.w.en]); }
            if(q.t==='lsn'){ if(q.lab[q.ans]!==q.w.ko) wrong.push(['lsn',q.w.en]); } }
          Battle.h=null; Battle.q=null; Battle._ws=null; return [seen, wrong.slice(0,5)]; }""")
        print("types", chk)
        for t in ["spell","gap","ox","pic","lsn"]:
            if not chk[0].get(t): bad.append(f"문제 종류 안 나옴 {t}")
        if chk[1]: bad.append(f"정답 칸 틀림 {chk[1]}")
        room=await host.evaluate("()=>Battle.host({set:'elem', from:0, to:3, dur:120, mode:'flag', goal:6, qt:['spell','gap','ox','pic','mean'], lbl:'G3-4 Stage 1~2'})"); print("room", room)
        kids=[]; skill=[0.95, 0.9, 0.55, 0.5]
        for i,(kid,nm,t) in enumerate([("k1","민준","ta"),("k2","서연","ta"),("k3","지호","tb"),("k4","하린","tb")]):
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844}); await boot(k)
            await k.evaluate(f"()=>{{ HyBoss.start(); return HyBoss.refresh(true).then(()=>{{ Battle.join('{room}', {{id:'{kid}', n:'{nm}', t:'{t}'}}); Battle.FAST=0; }}); }}"); kids.append(k)
        await host.wait_for_timeout(500); await host.screenshot(path=OUT+"flag_host_wait.png")
        await host.evaluate("()=>Battle.hostAct('start')"); await host.wait_for_timeout(3900)
        random.seed(3); kinds={}; shots=set()
        for step in range(300):
            for i,k in enumerate(kids):
                r=await k.evaluate(ANS, random.random()<skill[i])
                if r:
                    kinds[r[0]]=kinds.get(r[0],0)+1
                    if r[0] in ("spell","gap","ox","pic") and r[0] not in shots and i==2:
                        shots.add(r[0]); await k.screenshot(path=OUT+f"flag_kid_{r[0]}.png")
            if step==8: await host.screenshot(path=OUT+"flag_host_run.png")
            await host.wait_for_timeout(40)
            if await host.evaluate("()=>Battle.st().s==='end'"): break
        st=await host.evaluate("()=>[Battle.st().s, Battle.st().win, Battle.teamsOf().map(a=>[a.t, Math.round(a.p*10)/10])]"); print("end", st, kinds)
        await host.wait_for_timeout(3200)
        res=[await k.evaluate("()=>[Battle.ended, Battle._win, Battle._gems, Battle.ok]") for k in kids]; print("res", res)
        await host.screenshot(path=OUT+"flag_host_end.png"); await kids[0].screenshot(path=OUT+"flag_kid_end.png")
        if st[0]!="end" or st[1]!="ta": bad.append(f"사자반 우승 {st}")
        if st[2][0][1] < 6: bad.append(f"목표 전에 끝 {st}")
        if [r[2] for r in res]!=[(g if r[3]>0 else 0) for g,r in zip([4,4,2,2],res)] or [r[1] for r in res]!=[True,True,False,False]: bad.append(f"보석 (맞힌 게 있으면 우승 4 · 나머지 2) {res}")
        if not await host.evaluate("()=>!!document.querySelector('.btWin')"): bad.append("TV 우승 글자")
        print("errs", errs[:5]); await br.close()
    print("결과:", "통과 ✅" if not bad and not errs else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or errs: sys.exit(1)
asyncio.run(main())
