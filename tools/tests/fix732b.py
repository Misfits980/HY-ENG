"""(v732) ChatGPT 코드 QA 55건 고치기 — 오락실 쪽
   #39 4줄 팡 첫 차례 -1 · #40 끊기면 둘 다 승리 · #9 방 만들기 실패 · #47 「10초 뒤」 · #52 나가기 창 뒤 키보드 · #10 대기 중 방장이 나감
   #22·#23 과일 순위 덮기 · #48 과일 🪙 먼저 · #51 컬러팡 일시정지 · #34 볼링 0 → 10 = 스페어 · #54 다트 라운드 · #55 두 번째 손가락"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from draw635 import boot
from playwright.async_api import async_playwright
STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } }"""

async def enter(pg, k):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    await pg.evaluate("(k)=>MG.lobby(k)", k)
    for _ in range(80):
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
        await pg.wait_for_timeout(200)
    await pg.wait_for_timeout(500)

async def leave(pg):
    await pg.evaluate("()=>{ try{ MG.exit(); }catch(e){} }")
    for _ in range(40):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    await pg.wait_for_timeout(300)

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","FB732A", isle=False, vp={"width":900,"height":700})
        E=pg.evaluate

        # ══ 🔴 4줄 팡 ══
        await enter(pg, "c4")
        # #52 나가기 창 뒤로 키가 안 감
        await E("()=>{ MG.run.fast=true; MG.run.menuGo('easy'); }"); await E(STEP, 30)
        for _ in range(30):
            if await E("()=>MG.run.turn===MG.run.me && !MG.run.over"): break
            await E(STEP, 8)
        n0=await E("()=>MG.run.mv.length")
        await E("()=>document.querySelector('#mgUI .mgX').click()"); await pg.wait_for_timeout(200)
        await pg.keyboard.press("4"); await E(STEP, 4)
        n1=await E("()=>MG.run.mv.length")
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(200)
        conf=await E("()=>document.querySelector('#mgUI .mgConf').classList.contains('on')")
        await pg.keyboard.press("4"); await E(STEP, 4)
        n2=await E("()=>MG.run.mv.length")
        ok(n1==n0 and not conf and n2>n0, f"#52 「그만할까요?」 창이 떠 있을 땐 키 4 가 판에 안 감 · Esc = 계속하기 · 그 뒤엔 됨 {[n0,n1,n2,conf]}")
        await E("()=>{ (document.querySelector('#mgUI .puR')||{remove(){}}).remove(); MG.run.menuShow(); }")
        # #9 방 만들기 실패 → 대기실로 안 감 · #47 안내 초
        r=await E("""async ()=>{ MG.run.menuGo('co'); await new Promise(r=>setTimeout(r,300)); const R=MG.run.RM, P=NET.put; NET.put=()=>Promise.reject('off'); try{ await R.make(); }finally{ NET.put=P; } const a=[R.phase, R.path];
            await R.make(); await new Promise(r=>setTimeout(r,300)); const t=(document.querySelector('#mgUI .mgRoomP')||{}).textContent||''; return [a, R.phase, t]; }""")
        ok(r[0][0]=="room" and r[0][1] is None, f"#9 방이 서버에 안 만들어지면 대기실로 안 감 {r[0]}")
        ok(r[1]=="wait" and "4초 뒤" in r[2] and "10초" not in r[2], f"#47 대기실 「게임 시작 (4초 뒤)」 = 실제 기다림 {r[1]} {r[2][-40:]!r}")
        # #39 첫 차례 · #40 끊김
        r=await E("""()=>{ const R=MG.run.RM; R.onStart({seed:4294967295, ro:[R.code,'ZZ999']}, [{k:R.code, n:'나'},{k:'ZZ999', n:'친구'}]); return [MG.run.mode, MG.run.turn]; }""")
        ok(r[0]=="co-play" and r[1] in (0,1), f"#39 seed 가 2^31 넘어도 첫 차례 = 0 또는 1 (예전 -1 → 둘 다 못 놓음) {r}")
        n_rec=await E("()=>(store('hyeng_proto_c4r')||{}).n|0")
        await E("()=>{ const R=MG.run.RM; R.fresh=()=>9999; R.live=()=>[{k:R.code, n:'나'}]; }")
        await E(STEP, 200)   # 10초
        r=await E("()=>[MG.run.mode, MG.run.over, MG.run.win, (document.querySelector('#mgUI .c4Say')||{}).textContent||'']")
        ok(r[0]=="co-play" and r[2] is None and "연결" in r[3], f"#40 내 쪽 연결이 끊기면 「친구가 나갔어요 — 이겼어요」 안 함 · 「연결 확인 중」 {r}")
        await E(STEP, 260)   # +13초
        r=await E("()=>[MG.run.mode, (store('hyeng_proto_c4r')||{}).n|0]")
        ok(r[0]=="menu" and r[1]==n_rec, f"#40 20초 넘게 끊기면 이 판은 기록 없이 메뉴로 {r} (전 {n_rec})")
        await leave(pg)

        # ══ 🍉 과일 합치기 ══
        await enter(pg, "fruit")
        K=await E("()=>MG.run.keys()")
        await E("(K)=>NET.put('/hy/day/'+K.A+'/'+myCode, {n:'루아', s:5000, at:Date.now()})", K)
        await E("()=>MG.run.lbLoad()")
        await E("()=>{ MG.run.lb.W=Object.assign({}, MG.run.lb.W, {[myCode]:{n:'루아', s:99999, at:1}}); MG.run.lb.A={}; }")   # W = 지난 주 같은 옛 칸 · A = 못 받은 것처럼 빈 칸
        c0=await E("()=>TECO.coins()")
        await E("()=>{ MG.run.fast=true; MG.run.bot=true; MG.run.begin(); }")
        for _ in range(30):
            await E(STEP, 40)
            if await E("()=>MG.run.score>0 && MG.run.drops>8"): break
        r=await E("""async ()=>{ const G=NET.get; let hang=0; NET.get=p=>{ if(String(p).indexOf('/hy/day/fr')===0){ hang++; return new Promise(()=>{}); } return G(p); };
            const sc=MG.run.score; MG.run.gameOver(); await new Promise(r=>setTimeout(r,300)); const c=TECO.coins(); NET.get=G; return [sc, c, hang]; }""")
        ok(r[1]>c0, f"#48 판이 끝난 순간 🪙 (순위 저장을 기다리지 않음) {c0} → {r[1]} · 점수 {r[0]}")
        await leave(pg)
        await enter(pg, "fruit")
        await E("()=>MG.run.lbLoad()")
        await E("()=>{ MG.run.lb.W=Object.assign({}, MG.run.lb.W, {[myCode]:{n:'루아', s:99999, at:1}}); MG.run.lb.A={}; }")
        await E("()=>{ MG.run.fast=true; MG.run.bot=true; MG.run.begin(); }")
        for _ in range(30):
            await E(STEP, 40)
            if await E("()=>MG.run.score>0 && MG.run.drops>8"): break
        r=await E("""async (K)=>{ const sc=MG.run.score; await MG.run.gameOver(); await new Promise(r=>setTimeout(r,800)); const a=await NET.get('/hy/day/'+K.A+'/'+myCode), w=await NET.get('/hy/day/'+K.W+'/'+myCode); return [sc, a && a.s, w && w.s]; }""", K)
        ok(r[1]==5000, f"#22 순위를 못 받았어도(빈 목록) 서버의 더 높은 내 기록(5000)을 낮은 점수({r[0]})로 안 덮음 {r}")
        ok(r[2]==r[0] or (r[2] or 0)>=r[0], f"#23 옛 칸(지난 주 99999)과 안 비교 — 이번 주 서버 칸에 기록이 남음 {r}")
        await leave(pg)

        # ══ 🃏 컬러팡 #51 ══
        await enter(pg, "card")
        await E("()=>{ const b=document.querySelector('#cpHud .cpMenu [data-m=solo]'); if(b) b.click(); }")
        for _ in range(80):
            if await E("()=>MG.run.phase==='play' && MG.run.G.turn===MG.run.ME && !MG.run.G.lock && !!MG.run.G.dl"): break
            await E(STEP, 6)
        r=await E("""()=>{ const R=MG.run, G=R.G; const left0=G.dl-srvNow(); R.pause(true); TWN8.test=(TWN8.test||0)+45000; R.pause(false); const left1=G.dl-srvNow(); return [Math.round(left0/1000), Math.round(left1/1000), G.turn===R.ME]; }""")
        await E(STEP, 4)
        r2=await E("()=>[MG.run.G.turn===MG.run.ME, (document.querySelector('#cpHud .cpFeed')||{}).textContent||'']")
        ok(r[2] and abs(r[1]-r[0])<=2 and r2[0], f"#51 혼자 하기: 나가기 창을 45초 열어 둬도 내 차례 시간이 그대로 {r} {r2[0]}")
        await leave(pg)

        # ══ 🎳 볼링 #34 · 🎯 다트 #54 · #55 ══
        await enter(pg, "bowl")
        async def wait_aim(n=400):
            for _ in range(n):
                q=await E("()=>[MG.run.bw.ph, MG.run.mode]")
                if q[0]=="aim" or q[1]!="bowl": return q
                await E(STEP, 6)
        await E("()=>{ MG.run.fast=true; MG.run.menuGo('bowl'); }"); await E(STEP, 4)
        await E("()=>{ const b=document.querySelector('#mgUI .spBtn'); if(b && MG.run.SET.bump) b.click(); }")
        s0=await E("()=>(store('hyeng_proto_spr')||{}).strikes|0")
        await E("()=>MG.run.throwBall(-.85, -1.4, 9)"); await wait_aim()
        r0=await E("()=>MG.run.bw.rolls.slice()")
        await E("()=>{ MG.run.pins.forEach(p=>{ if(p.up) p.down=true; }); MG.run.throwBall(0, 0, 13); }")
        await E(STEP, 2); await E("()=>{ MG.run.pins.forEach(p=>{ if(p.up) p.down=true; }); }"); await wait_aim()
        r=await E("()=>[MG.run.bw.rolls.slice(), (store('hyeng_proto_spr')||{}).strikes|0, MG.run.bowlScore(MG.run.bw.rolls).marks[0]]")
        ok(r0==[0] and r[0][:2]==[0,10] and r[1]==s0 and r[2]==["-","/"], f"#34 0개 → 10개 = 스페어(/) · 스트라이크 기록 안 늘어남 {r0} {r} (전 {s0})")
        await E("()=>{ (document.querySelector('#mgUI .puR')||{remove(){}}).remove(); MG.run.menuShow(); MG.run.menuGo('dart'); }"); await E(STEP, 4)
        await E("()=>{ MG.run.fast=false; }")
        for i in range(3):
            await E("()=>MG.run.dart(0, .3)")
            for _ in range(60):
                if await E("()=>!MG.run.dt.fly"): break
                await E(STEP, 2)
        r=await E("()=>{ const a=MG.run.dart(0, .3); return [a===null, MG.run.dt.n, MG.run.dt.darts.length]; }")
        await E(STEP, 40)
        r2=await E("()=>[MG.run.dt.darts.length, MG.run.dart(0,.3)!==null]")
        ok(r[0] and r[1]==3 and r2[0]==0 and r2[1], f"#54 셋째 다트 뒤 라운드가 바뀌는 동안엔 못 던짐 · 그다음 새 라운드 {r} {r2}")
        for _ in range(60):
            if await E("()=>!MG.run.dt.fly"): break
            await E(STEP, 2)
        await E(STEP, 40)
        # #55 두 번째 손가락
        r=await E("""async ()=>{ const H=document.querySelector('#mgUI .spHit') || document.querySelector('#mgUI [class*=Hit]'); if(!H) return ['no hit']; const n0=MG.run.dt.n;
            const ev=(t,id,x,y)=>H.dispatchEvent(new PointerEvent(t, {pointerId:id, clientX:x, clientY:y, bubbles:true, isPrimary:id===1, pointerType:'touch'}));
            ev('pointerdown',1,450,350); ev('pointermove',1,455,345); ev('pointerdown',2,700,600); ev('pointerup',2,700,600); await null; const mid=MG.run.dt.n+(MG.run.dt.fly?1:0);
            ev('pointerup',1,455,345); await null; const end=MG.run.dt.n+(MG.run.dt.fly?1:0); return [n0, mid, end]; }""")
        ok(r[0]!="no hit" and r[1]==r[0] and r[2]==r[0]+1, f"#55 두 번째 손가락을 떼도 안 던짐 · 처음 손가락을 떼면 한 번 {r}")
        await leave(pg)

        ok(not [e for e in real_errs(errs) if "rror" in e], f"오류 0 {real_errs(errs)[:4]}")
        await ctx.close()

        # ══ #10 대기 중 방장이 나감 → 남은 아이가 👑 ══
        cA,A_,eA=await boot(br,"루아","FB732H", isle=False); cB,B_,eB=await boot(br,"민수","FB732G", isle=False)
        for x in (A_,B_): await enter(x, "c4")
        async def steps(P, n=6, dt=.1):
            for _ in range(n):
                for x in P: await x.evaluate("async (dt)=>{ MG.step(dt,false); await null; await null; }", dt)
                await P[0].wait_for_timeout(60)
        await A_.evaluate("()=>MG.run.menuGo('co')"); await steps([A_,B_],3)
        await A_.evaluate("()=>MG.run.RM.make()"); await steps([A_,B_],4)
        await B_.evaluate("()=>MG.run.menuGo('co')")
        for _ in range(15):
            await B_.evaluate("()=>MG.run.RM.list()"); await steps([A_,B_],2)
            if await B_.evaluate("()=>document.querySelectorAll('#mgUI [data-j]').length"): break
        await B_.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await steps([A_,B_],4)
        for _ in range(20):
            if await B_.evaluate("()=>MG.run.RM.phase==='wait'"): break
            await steps([A_,B_],2)
        r0=await B_.evaluate("()=>[MG.run.RM.phase, MG.run.RM.host]")
        await cA.close()
        await B_.evaluate("()=>{ TWN8.test=(TWN8.test||0)+13000; }")
        await steps([B_], 12)
        r=await B_.evaluate("()=>{ const R=MG.run.RM; return [R.phase, R.host, R.d && R.d.h && R.d.h.c===R.code, !!document.querySelector('#mgUI [data-st]')]; }")
        ok(r0==["wait",False] and r==["wait",True,True,True], f"#10 대기 중 방장이 끊기면 남은 아이가 👑 방장 · 「게임 시작」 단추 {r0} {r}")
        await cB.close()
        await br.close()
    print("FAIL" if bad else "PASS", len(bad))
    sys.exit(1 if bad else 0)

asyncio.run(main())
