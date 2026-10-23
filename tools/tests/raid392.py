"""(v392) 수업 레이드 아이 화면 = 아레나 — 시작하면 아레나 · 정답 스킬 데미지가 서버로 · ⚡ 에너지 일반 공격 · 멈춤 글 · 맞으면 하트 · 끝나면 아레나 닫고 시상식 · 친구 자리 (TV 24명 + +N)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "FAIL ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1280,"height":720}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e))); await boot(host)
        room=await host.evaluate("()=>{ Raid.MIN=1000; return Raid.host('g34',['vest','cap','glove','beard','belt'], 0, null, 250); }")
        kids=[]
        for nm in ["민준","서연","지호"]:
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844})
            await boot(k); await k.evaluate(f"()=>{{ G.char='knight'; Raid.FAST=0; Raid.join('{room}','{nm}'); }}"); kids.append(k)
        await host.wait_for_timeout(800)
        r=await kids[0].evaluate("()=>!!document.getElementById('arena')"); ok(r is False, f"시작 전엔 아레나 없음 {r}")
        await host.evaluate("()=>Raid.hostAct('start')"); await host.wait_for_timeout(1500)
        for k in kids: await k.evaluate("()=>{ BossLive.manual=true; }")
        r=await kids[0].evaluate("()=>[!!document.getElementById('arena'), !!(Arena.o&&Arena.o.raid), !!Arena.q, Arena.q && Arena.q.opts.length, Arena.q && Arena.q.opts.some(o=>o.en===Arena.q.w.en)]")
        ok(r==[True,True,True,3,True], f"시작하면 아레나 · 보기 3장에 정답 {r}")
        for i in range(4):
            for k in kids:
                await k.evaluate("()=>{ const q=Arena.q; if(!q||q.done) return; q.ice=-1; if(Arena.cast) Arena.cast.disAt=[1e15]; BossLive.S.busy=0; Arena.tap(q.opts.findIndex(o=>!o.fake && o.en===q.w.en)); }")
            await host.wait_for_timeout(1100)
        r=await host.evaluate("()=>{ const c=Raid.calc(); return [c.sum, Object.values(c.P).map(p=>[p.d|0,p.h|0])]; }")
        ok(r[0]>=3*30 and all(x[1]>=3 for x in r[1]), f"정답 스킬 → 서버 데미지·맞힌 수 {r}")
        e=await kids[0].evaluate("()=>{ const a=Arena.en, d=Raid.dmg; BossLive.S.busy=0; BossLive.press('atk', performance.now()); return [a, Arena.en, Raid.dmg-d]; }")
        ok(e[1]==e[0]-1 and e[2]>0, f"⚔️ 일반 공격 = 에너지 1칸 · 작은 데미지 {e}")
        await kids[0].evaluate("()=>{ Arena.en=0; Arena.hud(); }"); e=await kids[0].evaluate("()=>{ const d=Raid.dmg; BossLive.S.busy=0; BossLive.press('atk', performance.now()); return [Arena.en, Raid.dmg-d]; }")
        ok(e==[0,0], f"에너지 없으면 공격 안 됨 {e}")
        await host.evaluate("()=>Raid.hostAct('pause')"); await host.wait_for_timeout(1200)
        hd=await kids[0].evaluate("()=>{ const t=Arena.cast.t0; return [document.getElementById('arHold').classList.contains('on'), document.getElementById('arHold').textContent, t]; }")
        await kids[0].wait_for_timeout(1500); t2=await kids[0].evaluate("()=>Arena.cast.t0")
        ok(hd[0] and "멈췄" in hd[1] and t2>hd[2], f"멈춤 → 글 · 주문 게이지 멈춤 {hd} {t2}")
        await host.evaluate("()=>Raid.hostAct('pause')"); await host.wait_for_timeout(1000)
        r=await kids[0].evaluate("()=>document.getElementById('arHold').classList.contains('on')"); ok(r is False, "다시 시작 → 글 사라짐")
        h0=await kids[0].evaluate("()=>Raid.hearts")
        await kids[0].evaluate("()=>{ const S=BossLive.S; S.A=null; S.sh=-1e9; S.cd=0; const r=Math.random; Math.random=()=>0.01; BossLive.launch(performance.now()); Math.random=r; const A=S.A; if(A) A.hits.forEach(h=>{ BossLive.tick(h.t+1); }); }"); await kids[0].wait_for_timeout(600)
        h1=await kids[0].evaluate("()=>Raid.hearts"); ok(h1==h0-1, f"보스 공격 맞으면 하트 -1 {h0}→{h1}")
        # 친구 자리: TV 24명 + +N
        r=await host.evaluate("""()=>{ const now=Raid.now(), P={}; for(let i=0;i<30;i++) P['z'+i]={n:'친구'+i, c:'hero', d:1, at:now, la:now-i*1000, t:'all'}; return FB.update('/raids/'+Raid.room+'/p', P).then(()=>new Promise(r=>setTimeout(r,1500))).then(()=>[document.querySelectorAll('#rdStage .rsAllies .rsHero').length, (document.querySelector('#rdStage .rsMore')||{}).textContent||'']); }""")
        ok(r[0]==24 and "+" in r[1], f"TV 친구 24명 + 「+N명」 {r}")
        out=await host.evaluate("""()=>{ const S=document.getElementById('rdStage').getBoundingClientRect(), bad=[]; document.querySelectorAll('#rdStage .rsHero').forEach(e=>{ const r=e.getBoundingClientRect(); if(r.width && (r.left<S.left-2 || r.right>S.right+2 || r.bottom>S.bottom+2)) bad.push(Math.round(r.left-S.left)); }); return bad; }""")
        ok(out==[], f"TV 무대 밖으로 나간 캐릭터 없음 {out}")
        r=await kids[1].evaluate("()=>[document.querySelectorAll('#arStage .rsAllies .rsHero').length, !!document.querySelector('#arStage .rsMore')]")
        ok(r[0]<=4 and r[1], f"아레나 친구는 4명까지 + 「+N명」 {r}")
        await host.evaluate("()=>Raid.hostAct('end')"); await host.wait_for_timeout(3500)
        r=await kids[0].evaluate("()=>[!!document.getElementById('arena'), Raid.ended, !!document.querySelector('.rdEnd')]"); ok(r==[False,True,True], f"끝나면 아레나 닫고 결과·시상식 {r}")
        ok(not errs, f"스크립트 오류 없음 {errs[:3]}")
        await br.close()
    print("\nALL OK" if not bad else "\nFAIL", bad)
    if bad: sys.exit(1)
asyncio.run(main())
