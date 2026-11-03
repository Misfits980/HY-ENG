"""(v584) 사용자: 「마당에 쓸 만한 가구 · 흔들그네 막 그런 거」
   ① 새 마당 가구 5 (흔들그네 · 해먹 · 흔들의자 · 달걀 의자 · 바베큐) = 가게에 있고 그려짐 · 가게 줄에 「🎠 타기」 같은 표시
   ② 누르면: 흔들그네·그네 = 타고 같이 흔들림 · 해먹 = 누움 · 벤치 = 앉기 · 미끄럼틀 = 올라가 미끄러짐 · 방방 = 통통 · 다른 곳 누르면 내림
   ③ 우물 = 목마른 밭에 물 (하루 한 번) · 바베큐 = 요리 창 · 친구 마당 그네도 탐"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

NEW=["pswing","hammock","rocker","eggchair","bbq"]

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('YFURN')); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        await pg.evaluate("()=>{ go('yard', [DOOR[0],DOOR[1]+1]); }"); await pg.wait_for_timeout(2000)
        r=await pg.evaluate("(L)=>L.map(id=>[id, !!OUT_PRICE[id], (()=>{ try{ const g=OUT[id].build(0); return !!g && (OUT[id].use==='cook' || !!g.userData.seat); }catch(e){ return String(e); } })()])", NEW)
        ok(all(x[1] and x[2] is True for x in r), f"① 새 마당 가구 5 = 가게에 있고 앉는 자리 있음 {r}")
        t=await pg.evaluate("()=>{ openFurn('yard'); yCat='furn'; drawFurn(); return document.getElementById('furnBody').innerText; }")
        ok("porch swing" in t and "타기" in t and "눕기" in t, f"① 가게 줄 = 흔들그네 · 🎠 타기 · 🛌 눕기 {t[:80]!r}")
        await pg.screenshot(path=OUT+"yfurn584_shop.png")
        await pg.evaluate("()=>document.getElementById('furnP').classList.remove('on')")
        # 놓기
        r=await pg.evaluate("""()=>{ const put=(id)=>{ for(let z=1;z<YN;z++) for(let x=1;x<YN;x++) if(!yLocked(x,z) && yFits(id,x,z,0)===1){ return yAdd(id,x,z,0,0); } return null; };
            const P={}; ['trampoline','pswing','hammock','swing','slide','bbq','well','obench'].forEach(id=>{ const q=put(id); P[id]=q?[q.x,q.z]:null; }); ySave(); window._P=P; return P; }""")
        ok(all(r.values()), f"마당에 놓기 {r}")
        async def use(id):
            await pg.evaluate("""(id)=>{ const it=yplaced.find(p=>p.id===id); standUp(); const C=yCells(it.id,it.x,it.z,it.r); let s=null; for(const [x,z] of C){ for(const [a,b] of [[0,1],[1,0],[0,-1],[-1,0],[1,1],[-1,1],[1,-1],[-1,-1]]){ const q=[x+a,z+b]; if(!s && !PL[place.key].blocked(q[0],q[1]) && !C.some(c=>c[0]===q[0]&&c[1]===q[1])) s=q; } }
                if(s){ hero.path=[]; hero.moving=false; hero.cx=s[0]; hero.cz=s[1]; hero.g.position.set(s[0]+.5,0,s[1]+.5); } yGo(it); }""", id)   # 걷기가 느린 시험 화면 → 옆 칸으로 옮겨 놓고 누르기
            for _ in range(80):
                await pg.wait_for_timeout(150)
                if await pg.evaluate("()=>!hero.moving && !hero.path.length"): break
            await pg.wait_for_timeout(300)
        # 흔들그네 — 타고 같이 흔들림
        await use("pswing"); await pg.wait_for_timeout(700)
        r=await pg.evaluate("""()=>{ const a=hero.g.position.clone(); return new Promise(res=>setTimeout(()=>{ const b=hero.g.position; res([hero.seat && hero.seat.how, hero.act, +a.distanceTo(b).toFixed(3), +hero.g.position.y.toFixed(2)]); }, 500)); }""")
        ok(r[0]=="ride" and r[1]=="sit" and r[2]>0.005 and r[3]>0.2, f"② 흔들그네 = 앉아서 같이 흔들림 {r}")
        await pg.evaluate("()=>{ ISLE && 0; yaw=yawTo=0.8; dirty=true; }"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=OUT+"yfurn584_pswing.png")
        # 다른 곳 누르면 내림
        await pg.evaluate("()=>walkTo(DOOR[0],DOOR[1]+2)"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>[!!hero.seat, hero.act, yplaced.find(p=>p.id==='pswing').obj.userData.ride|0]")
        ok(r[0] is False and r[2]==0, f"② 걸어가면 내림 {r}")
        await pg.wait_for_timeout(1500)
        await use("hammock"); await pg.wait_for_timeout(500)
        r=await pg.evaluate("()=>[hero.seat && hero.seat.how, +hero.body.rotation.x.toFixed(2)]")
        ok(r[0]=="lie" and r[1]<-1.4, f"② 해먹 = 누움 {r}")
        await pg.screenshot(path=OUT+"yfurn584_hammock.png")
        await use("swing"); await pg.wait_for_timeout(400)
        ok(await pg.evaluate("()=>hero.seat && hero.seat.how==='ride' && hero.seat.y.id==='swing'"), "② 그네 타기")
        await use("slide")
        r=await pg.evaluate("""()=>{ let maxY=0; for(let i=0;i<60 && hero.seat;i++){ yRide(0.05); maxY=Math.max(maxY, hero.g.position.y); } return [+maxY.toFixed(2), !!hero.seat, +hero.g.position.y.toFixed(2)]; }""")   # 시험 화면은 느려서 시간을 직접 넘김
        ok(r[0]>0.8 and r[1] is False and r[2]<0.05, f"② 미끄럼틀 = 올라갔다 내려와서 끝 {r}")
        await use("trampoline")
        r=await pg.evaluate("""()=>{ let maxY=0; for(let i=0;i<120 && hero.seat;i++){ yRide(0.05); maxY=Math.max(maxY, hero.g.position.y); } return [+maxY.toFixed(2), !!hero.seat]; }""")
        ok(r[0]>1.0 and r[1] is False, f"② 방방 = 통통 뛰고 끝 {r}")
        await use("obench"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>hero.seat && hero.seat.how==='sit'"), "② 벤치 = 앉기")
        # ③ 우물
        r=await pg.evaluate("""()=>{ plots[0]={s:'wheat', g:0, wt:0}; plots[1]={s:'carrot', g:0, wt:0}; saveFarm(); yd.wl=''; const it=yplaced.find(p=>p.id==='well'); yUse(it); const a=[!!plots[0].wt, !!plots[1].wt]; plots[0].wt=0; yUse(it); return [a, !!plots[0].wt, yd.wl===dayKey()]; }""")
        ok(r==[[True,True],False,True], f"③ 우물 = 목마른 밭에 물 · 하루 한 번 {r}")
        r=await pg.evaluate("()=>{ yUse(yplaced.find(p=>p.id==='bbq')); return document.getElementById('craftP').classList.contains('on'); }")
        ok(r, "③ 🍖 바베큐 = 요리 창")
        await pg.evaluate("()=>document.getElementById('craftP').classList.remove('on')")
        # 친구 마당
        await pg.evaluate("""()=>{ const v={code:'QQQQQ', n:'민지', data:{y:{v:1, fp:[[2,2]], p:[['swing',4,3,0,0]], g:{}, pc:[0,0,0], db:{}, hx:{}}, av:{}}}; yEnterVisit(v); }""")
        await pg.wait_for_timeout(2600)
        await use("swing"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>place===PL.yvisit && hero.seat && hero.seat.how==='ride'"), "③ 친구 마당 그네도 탐")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
