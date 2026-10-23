"""(v392) 🚩 속도형 깃발 레이스 (FlagRun) — TV 1 · 아이 4 (사자반 2 · 돌고래반 2)
   시작하면 아이 = FlagRun · TV = FlagRun TV · 정답 → 점수·내 속도(v) 서버로 · TV 가 거리(fp) 재서 모두 같은 거리 · 아이템(/fx) 상대 반에 닿음 · 잘 푸는 반이 우승 · 보석"""
import asyncio, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ANS="(g)=>{ const F=FlagRun, q=F.q; if(!q||q.done||!F.o) return null; F._busy=0; q.ice=-1; q.dark=-1; const k=F.ord.find(x=>g ? F.right(x) : !F.right(x)); F.tap(k); return q.t; }"
async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "FAIL ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1280,"height":720}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e))); await boot(host)
        await host.evaluate("()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{ta:{n:'사자반',e:'🦁'}, tb:{n:'돌고래반',e:'🐬'}}, k:{k1:{n:'민준',t:'ta'},k2:{n:'서연',t:'ta'},k3:{n:'지호',t:'tb'},k4:{n:'하린',t:'tb'}}}); }"); await host.wait_for_timeout(500)
        room=await host.evaluate("()=>Battle.host({set:'elem', from:0, to:3, dur:60, mode:'flag', goal:6, qt:['spell','gap','ox','pic','mean'], lbl:'G3-4 Stage 1~2'})")
        kids=[]
        for kid,nm,t in [("k1","민준","ta"),("k2","서연","ta"),("k3","지호","tb"),("k4","하린","tb")]:
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844}); await boot(k)
            await k.evaluate(f"()=>{{ G.char='knight'; HyBoss.start(); return HyBoss.refresh(true).then(()=>{{ Battle.join('{room}', {{id:'{kid}', n:'{nm}', t:'{t}'}}); Battle.FAST=0; }}); }}"); kids.append(k)
        await host.wait_for_timeout(800)
        r=await kids[0].evaluate("()=>!!document.getElementById('frun')"); ok(r is False, f"시작 전엔 무대 없음 {r}")
        await host.evaluate("()=>Battle.hostAct('start')"); await host.wait_for_timeout(4300)
        r=await host.evaluate("()=>[!!document.getElementById('frun'), !!(FlagRun.o && FlagRun.o.tv), FlagRun.o && FlagRun.o.L.map(t=>t.k).join(',')]"); ok(r[0] and r[1] and r[2]=="ta,tb", f"TV = 깃발 레이스 TV (두 반) {r}")
        r=await kids[0].evaluate("()=>[!!document.getElementById('frun'), FlagRun.o && FlagRun.o.mine, !!FlagRun.q, FlagRun.o && FlagRun.o.L.length]"); ok(r==[True,"ta",True,2], f"아이 = 깃발 레이스 (내 반 앞) {r}")
        # 사자반은 잘 풀고 돌고래반은 자주 틀림
        random.seed(5); skill=[0.95,0.9,0.4,0.35]
        for step in range(24):
            for i,k in enumerate(kids): await k.evaluate(ANS, random.random()<skill[i])
            await host.wait_for_timeout(700)
            if step==6:
                fp=await host.evaluate("()=>Battle.st().fp||{}"); ok(fp.get("ta",0)>0, f"TV 가 거리를 잼 {fp}")
                v=await host.evaluate("()=>{ const P=Battle.T().p; return ['k1','k3'].map(k=>[P[k].v, P[k].sc]); }"); ok(v[0][0] and v[0][1]>0, f"아이 속도·점수가 서버로 {v}")
                d=await kids[2].evaluate("()=>[FlagRun.T('ta').p, FlagRun.T('tb').p]"); h=await host.evaluate("()=>[FlagRun.T('ta').p, FlagRun.T('tb').p]")
                ok(abs(d[0]-h[0])<1.0 and abs(d[1]-h[1])<1.0, f"아이 화면 거리 ≈ TV 거리 {d} {h}")
                # 아이템: 지호(돌고래반)가 🧊 → 사자반 아이 카드에 얼음
                await kids[2].evaluate("()=>{ FlagRun.item='ice'; FlagRun.FLY=200; FlagRun.use(); }"); await host.wait_for_timeout(1500)
                r=await kids[0].evaluate("()=>[FlagRun.q && FlagRun.q.ice, (document.getElementById('frBan')||{}).textContent]"); ok(r[0] is not None and r[0]>=0 and "얼음" in (r[1] or ""), f"🧊 얼음이 상대 반 아이 카드에 {r}")
                r=await kids[3].evaluate("()=>FlagRun.q ? FlagRun.q.ice : -1"); ok(r==-1, f"우리 반(돌고래반) 친구 카드는 그대로 {r}")
                await kids[1].evaluate("()=>{ FlagRun.item='snail'; FlagRun.FLY=200; FlagRun.use(); }"); await host.wait_for_timeout(1200)
                r=await host.evaluate("()=>FlagRun.T('tb').slow>performance.now()"); ok(r, "🐌 달팽이 → TV 에서 돌고래반 느려짐")
            if await host.evaluate("()=>Battle.st().s==='end'"): break
        await host.wait_for_timeout(40000 if not await host.evaluate("()=>Battle.st().s==='end'") else 100)
        st=await host.evaluate("()=>[Battle.st().s, Battle.st().win, Battle.st().fp]"); print("end", st)
        ok(st[0]=="end" and st[1]=="ta", f"잘 푼 사자반 우승 {st}")
        await host.wait_for_timeout(3500)
        r=await host.evaluate("()=>!!document.getElementById('frun')"); ok(r is False, "끝나면 TV 무대 닫고 결과")
        res=[await k.evaluate("()=>[Battle.ended, Battle._win, Battle._gems, !!document.getElementById('frun')]") for k in kids]; print("res", res)
        ok([x[1] for x in res]==[True,True,False,False] and [x[2] for x in res]==[4,4,2,2] and not any(x[3] for x in res), f"보석 우승 반 4 · 나머지 2 · 무대 닫힘 {res}")
        await host.screenshot(path=OUT+"flag392_end.png")
        ok(not errs, f"스크립트 오류 없음 {errs[:3]}")
        await br.close()
    print("\nALL OK" if not bad else "\nFAIL", bad)
    if bad: sys.exit(1)
asyncio.run(main())
