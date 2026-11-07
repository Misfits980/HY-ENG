"""(v623) 🛡 GUARD — 오류 기록 · 멈춤 막기 · 렉 줄이기 · 튕김 알아채기 · err.html
사용자(11-07): 「우리 게임 안정성이랑 렉 대비해서 장치를 해야겠지? 그리고 오류를 대비하고 싶어」"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"guard623"+os.sep; os.makedirs(D, exist_ok=True)
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":390,"height":844}, has_touch=True)
        await ctx.add_init_script("window.HY_GUARD_SEND=true")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('GD623')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.removeItem('hyeng_perf_lv'); }")
        await pg.reload(); await pg.wait_for_timeout(2600); await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(240):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        r=await pg.evaluate("()=>({g:!!window.GUARD, page:GUARD.PAGE, lv:GUARD.lv, auto:GUARD.auto})")
        ok(r['g'] and r['page']=='town' and r['lv']==0 and not r['auto'], f"① 마을에 GUARD (자동 시험은 렉 자동 낮춤 꺼짐) {r}")
        # ② 한 프레임 오류 → 마을은 계속 (다음 프레임도 그림)
        r=await pg.evaluate("""async ()=>{ let n=0; const o=window.updCam; window.updCam=function(){ if(n++<3) throw new Error("테스트 오류 A"); return o.apply(this, arguments); };
          await new Promise(r=>setTimeout(r,1500)); const h=HOUSE.hero(); const x0=h.g.position.x; TFAC.warp(h.cx+3, h.cz); await new Promise(r=>setTimeout(r,800));
          return {n, sent:GUARD.sent.filter(s=>s.k==="frame").map(s=>s.m), moved:Math.abs(h.g.position.x-x0)>1, fatal:!!document.getElementById("gdFatal")}; }""")
        ok(r['n']>3 and r['sent']==['테스트 오류 A'] and r['moved'] and not r['fatal'], f"② 프레임 오류 3번 → 기록 1번 · 마을 계속 {r}")
        await pg.wait_for_timeout(1500)
        srv=fakefb.DB.get('hy',{}).get('day',{}); er=[v for k,o in srv.items() if k.startswith('er') for v in o.values()]
        ok(any(x.get('m')=='테스트 오류 A' and x.get('p')=='town' and x.get('pl')=='isle' and x.get('d') for x in er), f"③ 서버 /hy/day/er<날짜> 에 기록 {er[:1]}")
        # ④ 렉 → 가볍게
        r=await pg.evaluate("""async ()=>{ GUARD.auto=true; for(let i=0;i<70;i++) GUARD.frame(50); const a={lv:GUARD.lv, edge:TOON.edge, pr:renderer.getPixelRatio(), sh:sun.castShadow, toast:document.getElementById('toast').textContent, saved:localStorage.getItem('hyeng_perf_lv')};
          await new Promise(r=>setTimeout(r,6200)); for(let i=0;i<70;i++) GUARD.frame(50); a.lv2=GUARD.lv; a.sh2=sun.castShadow; return a; }""")
        ok(r['lv']==1 and r['edge']==False and '가볍게' in r['toast'] and r['saved']=='1' and r['lv2']==2 and r['sh2']==False, f"④ 렉(20fps) → 1단계(테두리 끔) → 2단계(그림자 끔) {r}")
        await pg.screenshot(path=D+"lv2.png")
        # ⑤ 계속 오류 → 「다시 시작」 카드
        r=await pg.evaluate("""async ()=>{ window.updCam=function(){ throw new Error("테스트 오류 B"); }; await new Promise(r=>setTimeout(r,2500)); return {fatal:!!document.getElementById("gdFatal"), txt:(document.getElementById("gdFatal")||{}).textContent}; }""")
        ok(r['fatal'] and '다시 시작' in (r['txt'] or ''), f"⑤ 계속 멈추면 「다시 시작」 카드 {r}")
        await pg.screenshot(path=D+"fatal.png")
        # ⑥ 튕김 알아채기 — 보이는 중에 꺼진 흔적(새 창에서 스크립트보다 먼저 넣음) → 다음에 켤 때 기록 + 한 단계 가볍게
        await pg.evaluate("()=>localStorage.setItem('hyeng_perf_lv','0')")
        cp=await ctx.new_page(); await cp.add_init_script("try{ if(!sessionStorage.getItem('x')){ sessionStorage.setItem('x',1); localStorage.setItem('hyeng_alive_town', JSON.stringify({t:Date.now()-5000, s:Date.now()-60000, pl:'isle'})); } }catch(e){}")
        await cp.route("**/*", fake); await cp.goto(ORIGIN+"proto/house.html?isle=1"); await cp.wait_for_timeout(3200)
        r=await cp.evaluate("()=>({c:!!GUARD.crashed, lv:GUARD.lv, sent:GUARD.sent.map(s=>s.k)})")
        ok(r['c'] and r['lv']==1 and 'crash' in r['sent'], f"⑥ 튕김 → 다음에 켤 때 기록 · 한 단계 가볍게 {r}")
        await cp.close()
        # ⑦ 게임(index.html) — 오류 기록 + 예전 「앗, 잠깐 문제가」 창
        g=await ctx.new_page(); await g.route("**/*", fake); await g.goto(ORIGIN+"index.html"); await g.wait_for_timeout(2500)
        await g.evaluate("()=>setTimeout(()=>{ throw new Error('게임 테스트 오류'); }, 10)"); await g.wait_for_timeout(800)
        r=await g.evaluate("()=>({page:GUARD.PAGE, sent:GUARD.sent.map(s=>s.m), box:getComputedStyle(document.getElementById('err')).display})")
        ok(r['page']=='game' and any('게임 테스트 오류' in x for x in r['sent']) and r['box']=='grid', f"⑦ 게임 오류 기록 + 오류 창 {r}")
        # ⑧ err.html 보기
        await g.wait_for_timeout(800); e=await ctx.new_page(); await e.route("**/*", fake); await e.goto(ORIGIN+"err.html"); await e.wait_for_timeout(1500)
        r=await e.evaluate("()=>({items:document.querySelectorAll('.it').length, txt:document.getElementById('list').textContent, sum:document.getElementById('sum').textContent})")
        ok(r['items']>=3 and '테스트 오류 A' in r['txt'] and '튕김' in r['txt'], f"⑧ err.html 묶어 보기 {r['items']}묶음 · {r['sum']}")
        await e.screenshot(path=D+"err.png", full_page=True)
        await br.close()
    real=[x for x in errs if '테스트 오류' not in x and '게임 테스트' not in x]
    ok(not real, f"오류 없음 {real[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
