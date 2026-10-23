"""(v392) 워드 게이트 레이스 TV = 경기장 (FlagRun TV · 거리 = 점수) — 🔴🔵 두 팀 2줄 + 아이 무리 · 개인 = 점수 높은 5명 레인 · 점수가 오르면 앞으로 · 끝나면 닫힘"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
SEED="""([room,n,auto])=>{ const CH=['hero','knight','wolf','cat','mage','archer'], P={}; for(let i=0;i<n;i++) P['k'+i]={n:'아이'+i, c:CH[i%6], sc:(n-i)*100, ok:0, ng:0, at:Date.now(), tm: auto ? (i%2?'b':'r') : undefined};
  return FB.update('/battle/'+room+'/p', JSON.parse(JSON.stringify(P))); }"""
async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "FAIL ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for auto in [True, False]:
            ctx=await br.new_context(viewport={"width":1280,"height":720}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
            T=await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e))); await boot(T)
            room=await T.evaluate("(a)=>Battle.host({kind:'run', rset:'elem', diff:'normal', dur:120, mode:a?'auto':'score', set:'elem', words:[], lbl:'달리기'})", auto)
            await T.wait_for_timeout(500); await T.evaluate(SEED, [room, 12, auto]); await T.wait_for_timeout(800)
            await T.evaluate("()=>Battle.hostAct('start')"); await T.wait_for_timeout(5500)
            r=await T.evaluate("()=>[!!document.getElementById('frun'), FlagRun.o && FlagRun.o.fixed, FlagRun.o && FlagRun.o.L.map(t=>t.k).join(',')]")
            ok(r[0] and r[1] and (r[2]=="b,r" if auto else len(r[2].split(","))==5), f"{'두 팀' if auto else '개인'}: TV = 경기장 {r}")
            if auto:
                r=await T.evaluate("()=>[document.querySelectorAll('#frun .frKid').length, (document.querySelector('#frun .frMore')||{}).textContent]"); ok(r[0]==12 or r[0]>=10, f"두 팀: 아이 무리 {r}")
            p0=await T.evaluate("()=>FlagRun.o.L.map(t=>[t.k, Math.round(t.p*100)/100])")
            await T.evaluate("(room)=>FB.update('/battle/'+room+'/p/k11', {sc:5000})", room); await T.wait_for_timeout(2500)
            p1=await T.evaluate("()=>FlagRun.o.L.map(t=>[t.k, Math.round(t.p*100)/100])")
            lead=await T.evaluate("()=>{ const L=FlagRun.o.L.slice().sort((a,b)=>b.p-a.p); return L[0].k; }")
            ok(lead==("b" if auto else "kk11"), f"점수가 오르면 앞으로 {p0} → {p1} 1등 {lead}")
            out=await T.evaluate("""()=>{ const S=document.getElementById('frStage').getBoundingClientRect(), bad=[]; document.querySelectorAll('#frun .frSpr, #frun .frKid').forEach(e=>{ const r=e.getBoundingClientRect(); if(r.width && (r.left<S.left-1 || r.right>S.right+1)) bad.push(Math.round(r.left-S.left)); }); return bad; }""")
            ok(out==[], f"경기장 밖 없음 {out}")
            await T.screenshot(path=OUT+("rr392_auto.png" if auto else "rr392_solo.png"))
            await T.evaluate("()=>Battle.hostAct('end')"); await T.wait_for_timeout(2500)
            r=await T.evaluate("()=>!!document.getElementById('frun')"); ok(r is False, "끝나면 경기장 닫힘")
            await ctx.close()
        ok(not errs, f"스크립트 오류 없음 {errs[:3]}")
        await br.close()
    print("\nALL OK" if not bad else "\nFAIL", bad)
    if bad: sys.exit(1)
asyncio.run(main())
