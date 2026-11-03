"""(v586) 사용자: 「마당도 우물 설치할 곳 · 그 대신 마당 청소가 먼저 · 그렇게 튜토리얼」 · 「예전에 없앴어야 했던 것들 다 정리 (Mia 빼고)」
   ① 섬 모드 정리: 마당 🏪 좌판 없음 · 친구 창 「🏘 마을 사람 집」 없음 · 섬 광장 「🏘 마을 사람들」 팻말 없음 · 「새 땅」 팻말 없음(다 열림) · 할 일에 예전 마을 사람 없음 · 가게에 우물 없음
   ② 🌳 마당 가꾸기: 🧹 치우기 → 🪣 우물 자리에 우물(🪨3 🪵3 · 치우기 전엔 못 지음) → 🌱 심기 → 💧 우물 물 → 🪙 100
   ③ 예전 아이(새 땅 안 연 마당) = 새 땅이 열리고 옅은 잡초·돌만 (치우기 할 거리)"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('YGD86')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        # ① 정리
        r=await pg.evaluate("""()=>[ISLE_MODE, !scene.userData.stallObj.parent, (LBL_DEF.yard().find(l=>l.k==='shop')||{}).show(), QS.map(q=>q[0]).includes('talk'), QD.map(q=>q[0]).includes('give'), !!OUT_PRICE.well, yd.pc.join(''), yd.m6]""")
        ok(r==[True,True,False,False,False,False,"111",1], f"① 좌판 없음 · 할 일에 예전 마을 사람 없음 · 가게에 우물 없음 · 새 땅 다 열림 {r}")
        r=await pg.evaluate("()=>{ try{ openFr(); }catch(e){} const t=document.getElementById('frP') ? document.getElementById('frP').innerText : ''; document.getElementById('frP') && document.getElementById('frP').classList.remove('on'); return /마을 사람 집/.test(t); }")
        ok(r is False, "① 친구 창에 「🏘 마을 사람 집」 없음")
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        r=await pg.evaluate("()=>[(ISLE.SPOT.shops||[]).some(s=>s.k==='town'), (()=>{ let n=0; ISLE.G.traverse(o=>{ if(o.isSprite && o.userData.lbl==='town') n++; }); return n; })()]")
        ok(r==[False,0], f"① 섬 광장 「🏘 마을 사람들」 팻말 없음 {r}")
        # ② 마당 가꾸기
        await pg.evaluate("()=>ISLE.tripTo('yard')")
        for _ in range(80):
            if await pg.evaluate("()=>HOUSE.place()==='yard' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(2200)
        r=await pg.evaluate("()=>[Object.keys(yd.db).length, !!yd.ws, document.getElementById('yGd') && document.getElementById('yGd').classList.contains('on'), document.getElementById('yGd') && document.getElementById('yGd').innerText.replace(/\\s+/g,' '), scene.userData.wsG && scene.userData.wsG.visible, LBL.some(l=>l.d.k==='wspot' && l.el.style.display!=='none')]")
        ok(r[0]>=9 and r[0]<=26 and r[1] and r[2] and "1/4" in r[3] and "치우기" in r[3] and r[4], f"② 처음 = 치울 것 {r[0]}개 · 🪣 우물 자리 · 안내 1/4 🧹 {r[3]!r}")
        await pg.screenshot(path=OUT+"yguide586_1.png")
        r=await pg.evaluate("()=>{ mats.stone=5; mats.branch=5; yWellAsk(); const a=document.getElementById('ask').classList.contains('on'); const n=yplaced.filter(p=>p.id==='well').length; return [a, n]; }")
        ok(r==[False,0], f"② 치우기 전엔 우물 못 지음 {r}")
        r=await pg.evaluate("""()=>{ mats.stone=0; mats.branch=0; Object.keys(yd.db).forEach(k=>{ yClear(k); }); return [Object.keys(yd.db).length, yd.gc, mats.stone|0, mats.branch|0]; }""")
        ok(r[0]==0 and r[1]==1, f"② 다 치움 → 1단계 끝 · 치우며 모은 🪨{r[2]} 🪵{r[3]}")
        await pg.wait_for_timeout(700)
        t=await pg.evaluate("()=>{ yGuideUpd(true); return document.getElementById('yGd').innerText.replace(/\\s+/g,' '); }")
        ok("2/4" in t and "우물" in t, f"② 안내 2/4 🪣 우물 짓기 {t!r}")
        r=await pg.evaluate("()=>{ mats.stone=3; mats.branch=3; const w=yd.ws.slice(); const ok=yWellBuild(); const it=yplaced.find(p=>p.id==='well'); return [ok, it && [it.x,it.z], w, mats.stone|0, mats.branch|0, scene.userData.wsG.visible, yWS()]; }")
        ok(r[0] is True and r[1]==r[2] and r[3]==0 and r[4]==0 and r[5] is False and r[6] is None, f"② 우물 자리에 우물 완성 (🪨3 🪵3 씀) {r}")
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+"yguide586_well.png")
        r=await pg.evaluate("()=>{ addMat('wheat seeds',1); plant(0,'wheat'); yGuideUpd(true); return [yd.pl, document.getElementById('yGd').innerText.replace(/\\s+/g,' ')]; }")
        ok(r[0]==1 and "4/4" in r[1], f"② 심기 → 안내 4/4 💧 {r}")
        r=await pg.evaluate("()=>{ const c0=TECO.coins(); yd.wl=''; yUse(yplaced.find(p=>p.id==='well')); yGuideUpd(true); return [!!plots[0].wt, yd.gr, TECO.coins()-c0, document.getElementById('yGd').classList.contains('on')]; }")
        ok(r==[True,1,100,False], f"② 우물 물 → 마당 가꾸기 완성 🪙+100 · 안내 사라짐 {r}")
        await pg.reload(); await pg.wait_for_timeout(2600)
        r=await pg.evaluate("()=>{ const d=JSON.parse(localStorage.getItem('hyeng_proto_yard')); return [d.gr, d.gc, d.m6, d.pl, Object.keys(d.db).length]; }")
        ok(r[0]==1 and r[1]==1 and r[2]==1 and r[3]==1, f"② 저장 {r}")
        await ctx.close()
        # ③ 예전 아이 (새 땅 안 연 마당 · 다 치운 상태)
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('OLDKD')); localStorage.setItem('hyeng_nick','민지'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_yard', JSON.stringify({v:1, p:[['well',8,3,0,0]], g:{}, pc:[0,0,0], db:{}, hx:{}, s:{}, gp:['dirt']})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        r=await pg.evaluate("()=>{ const n=Object.keys(yd.db).length, inP=Object.keys(yd.db).every(k=>{ const [x,z]=k.split(',').map(Number); return parcOf(x,z)>=0; }); return [yd.pc.join(''), n, inP, wellBuilt(), yWS()]; }")
        ok(r[0]=="111" and 5<=r[1]<=40 and r[2] and r[3] is True and r[4] is None, f"③ 예전 아이: 새 땅 열림 · 옅은 잡초·돌 {r[1]}개(새 땅에만) · 우물 있으면 우물 자리 없음 {r}")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
