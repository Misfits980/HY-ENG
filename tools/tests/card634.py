"""(v634) 🃏 컬러팡 5가지 — 사용자 「5번까지다」
   ① 메뉴(혼자·같이·배우기·미션·뒷면·규칙) — 놀이 섬 카드 카페를 누르면 바로 메뉴
   ② 🎯 오늘의 미션 3개 · 판 끝나면 「한 판 끝까지」 완료 → 🪙 · 🎴 뒷면 9가지(잠김 · 1승이면 별밤 열림 · 고르면 내 뽑기 더미)
   ③ ⚙️ 규칙: 시작 5장 · 📚 +2 쌓기 (쌓이면 +2 만 낼 수 있음 · 받기 = 쌓인 만큼)
   ④ 📖 배우기: 손에 무지개·+2 · 따라 하기 말풍선 + 손가락 · 🪙·하루 판 수 안 셈
   ⑤ 👫 같이 하기 3명(+봇 1): 방 → 시작 → 모두 같은 판 · 자리 다름 · 끝까지 · 같은 결과
   ⑥ 자동 선수 4판(보통·쉬움·5장·쌓기) 108장 그대로 · 사진 폰/패드/가로"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
OUTD=OUT+"card634/"; os.makedirs(OUTD, exist_ok=True)

async def boot(br, nick, code, vp=None, isle=True):
    ctx=await br.new_context(viewport=vp or {"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: (m.type in ("error","warning")) and ("CP" in m.text) and errs.append(m.text[:240]))
    await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
    await pg.evaluate("([n,c])=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_v5','1'); }", [nick, code])
    await pg.reload(); await pg.wait_for_timeout(2600)
    if isle:
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
    return ctx, pg, errs

async def menu(pg):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    for t in range(3):
        await pg.evaluate("()=>{ if(!MG.on) MG.enter('card',{}); }")
        for _ in range(60):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
    await pg.wait_for_timeout(300)

STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } return MG.run && MG.run.G.over; }"""
CHECK = """()=>{ const R=MG.run, G=R.G; const n=G.P.reduce((s,p)=>s+p.h.length,0)+G.draw.length+G.pile.length;
  const ids=new Set(); G.P.forEach(p=>p.h.forEach(k=>ids.add(k))); G.draw.forEach(k=>ids.add(k)); G.pile.forEach(k=>ids.add(k));
  return {total:n, uniq:ids.size, over:G.over, hands:G.P.map(p=>p.h.length), phase:R.phase}; }"""

async def run_auto(pg, maxit=500):
    stuck=0; last=None
    for _ in range(maxit):
        if await pg.evaluate(STEP, 10): break
        s=await pg.evaluate("()=>JSON.stringify([MG.run.G.turn, MG.run.G.P.map(p=>p.h.length), MG.run.G.pile.length, MG.run.G.pend])")
        stuck = stuck+1 if s==last else 0; last=s
        if stuck>40: break
    await pg.evaluate(STEP, 60)
    return stuck

async def main():
    bad=[]; errs_all=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","CP634A"); errs_all.append(errs)
        # ① 메뉴
        await pg.evaluate("()=>MG.lobby('card')")
        for _ in range(80):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        await pg.wait_for_timeout(400)
        r=await pg.evaluate("()=>{ const M=document.querySelector('#cpHud .cpMenu'); return [MG.run.phase, getComputedStyle(M).display, [...M.querySelectorAll('[data-m]')].map(b=>b.dataset.m).join(','), M.querySelectorAll('[data-df]').length, !!M.querySelector('[data-m=tut].new'), !document.getElementById('mgLob')||!document.getElementById('mgLob').classList.contains('on')]; }")
        ok(r[0]=="menu" and r[1]=="flex" and r[2]=="solo,co,tut,mis,bk,rule,out" and r[3]==2 and r[4] and r[5], f"① 카페 → 바로 메뉴 (혼자·같이·배우기(처음이면 여기!)·미션·뒷면·규칙·섬으로) {r}")
        await pg.screenshot(path=OUTD+"menu.png")
        # ② 미션 · 뒷면
        await pg.evaluate("()=>MG.run.menuGo('mis')"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>[document.querySelectorAll('#cpHud .cpMenu .mi').length, /한 판 끝까지/.test(document.querySelector('#cpHud .cpMenu').innerText)]")
        ok(r==[3,True], f"② 오늘의 미션 3개 (「한 판 끝까지」 늘 있음) {r}")
        await pg.screenshot(path=OUTD+"missions.png")
        await pg.evaluate("()=>MG.run.menuGo('bk')"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>{ const M=document.querySelector('#cpHud .cpMenu'); const L=M.querySelectorAll('.bk'), lk=M.querySelectorAll('.bk.lock'); M.querySelector('[data-bk=night]').click(); return [L.length, lk.length, MG.run.SET.bk]; }")
        ok(r==[9,8,"base"], f"② 뒷면 9가지 · 잠김 8 · 잠긴 것 눌러도 안 바뀜 {r}")
        await pg.screenshot(path=OUTD+"backs.png")
        # ③ 규칙
        await pg.evaluate("()=>{ MG.run.menuGo('rule'); }"); await pg.wait_for_timeout(200)
        await pg.evaluate("()=>{ document.querySelector('#cpHud .cpMenu [data-hs=\"5\"]').click(); }"); await pg.wait_for_timeout(100)
        await pg.evaluate("()=>{ document.querySelector('#cpHud .cpMenu [data-stk=\"1\"]').click(); }"); await pg.wait_for_timeout(100)
        r=await pg.evaluate("()=>[MG.run.SET.hs, MG.run.SET.stk, (store('hyeng_proto_cpset')||{}).stk]")
        ok(r==[5,1,1], f"③ 규칙: 시작 5장 · +2 쌓기 켬 (저장) {r}")
        await pg.screenshot(path=OUTD+"rules.png")
        # ④ 배우기
        c0=await pg.evaluate("()=>TECO.coins()")
        await pg.evaluate("()=>MG.run.menuGo('tut')")
        for _ in range(80):
            if await pg.evaluate("()=>MG.run.isMyTurn()"): break
            await pg.evaluate(STEP, 4)
        await pg.wait_for_timeout(900)
        r=await pg.evaluate("""()=>{ const R=MG.run, G=R.G, h=G.P[0].h.map(R.CARD); return [R.TUT, G.P[0].h.length, h.some(k=>k.v==='wild'), h.some(k=>k.v==='d2'), G.top.c+G.top.v, !!document.querySelector('#cpHud .cpCoach'), !!document.querySelector('#cpHud .cpFinger'), R.coach.card]; }""")
        ok(r[0] and r[1]==7 and r[2] and r[3] and r[4]=="b5" and r[5] and r[6] and r[7]==1, f"④ 배우기: 7장(무지개·+2) · 첫 카드 파랑 5 · 말풍선+손가락 {r}")
        await pg.screenshot(path=OUTD+"tut.png")
        r=await pg.evaluate("""async ()=>{ const R=MG.run, G=R.G; const id=[...document.querySelectorAll('#cpHud .cpC.ok')].map(e=>+e.dataset.id).find(id=>!R.CARD(id).c || typeof R.CARD(id).v==='number'); const k=R.CARD(id); R.tapCard(id,null);
            if(!k.c) document.querySelector('#cpHud .cpPick .lb[data-c=b]').click(); for(let i=0;i<40;i++){ MG.step(.05,false); await null; await null; } return [R.coach.card, !document.querySelector('#cpHud .cpCoach .x'), G.pile.length]; }""")
        ok(r[0]==2 and r[2]>=2, f"④ 빛나는 카드 내면 말풍선 닫힘 {r}")
        await pg.evaluate("()=>{ MG.run.auto=true; MG.run.fast=true; }")
        st=await run_auto(pg)
        r=await pg.evaluate("()=>[MG.run.G.over, MG.payLeft('card'), (MG.rec().t.card||{}).tut, TECO.coins()]")
        ok(r[0] and r[1]==3 and r[2]==1 and r[3]==c0, f"④ 배우기 끝까지 · 🪙·하루 판 수 안 셈 · 기록 tut {r} (멈춤 {st})")
        await pg.evaluate("()=>MG.run.fast=false"); await pg.wait_for_timeout(1200); await pg.screenshot(path=OUTD+"tut_end.png")
        await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(700)
        # ③ 쌓기 규칙 (5장 · 쌓기)
        await menu(pg); await pg.evaluate("()=>MG.run.menuGo('solo')")
        for _ in range(80):
            if await pg.evaluate("()=>MG.run.isMyTurn()"): break
            await pg.evaluate(STEP, 4)
        r=await pg.evaluate("()=>MG.run.G.hist[0]")
        ok(r==[5,5,5,5], f"③ 시작 5장씩 {r}")
        r=await pg.evaluate("""async ()=>{ const R=MG.run, G=R.G, me=G.P[0];
            /* 내가 +2 를 내면 쌓임 → 다음 사람(봇)은 +2 가 있으면 넘기고 없으면 받음 */
            const i=G.draw.findIndex(id=>R.CARD(id).v==='d2' && R.CARD(id).c===G.cur); const id=G.draw.splice(i,1)[0]; me.h.push(id); R.drawHand();
            const nx=(0+G.dir+4)%4, n0=G.P[nx].h.length; const has=G.P[nx].h.some(q=>R.CARD(q).v==='d2'||R.CARD(q).v==='wild4');
            const tot0=G.P.reduce((s,p)=>s+p.h.length,0); R.tapCard(id,null); let pend=0; for(let j=0;j<12;j++){ MG.step(.05,false); await null; await null; pend=Math.max(pend,G.pend); }
            let mx=pend; for(let j=0;j<600;j++){ MG.step(.05,false); await null; await null; mx=Math.max(mx,G.pend); if(G.pend===0 && !G.lock) break; }
            return [pend, mx, G.pend, G.P.reduce((s,p)=>s+p.h.length,0)-tot0]; }""")
        ok(r[0]==2 and r[1]<=8 and r[2]==0 and r[3]>=r[1]-1-3, f"③ +2 쌓기: 내가 내면 +2 쌓임 → 넘기다가 못 내는 사람이 다 받음 (최대 8) {r}")
        r=await pg.evaluate("""async ()=>{ const R=MG.run, G=R.G; for(let t=0;t<400 && !(R.isMyTurn()) && !G.over;t++){ MG.step(.05,false); await null; await null; }
            if(G.over) return 'over'; const me=G.P[0];
            /* 쌓인 상태 만들기: 맨 위 +2 · 쌓인 2 */ const i=G.draw.findIndex(id=>R.CARD(id).v==='d2'); const d=G.draw.splice(i,1)[0]; G.pile.push(d); G.top=R.CARD(d); G.cur=G.top.c; G.pend=2;
            const j=G.draw.findIndex(id=>R.CARD(id).v==='d2'); const mine=G.draw.splice(j,1)[0]; me.h.push(mine); R.drawHand(); R.cmd();
            const ok=me.h.filter(id=>R.okC(R.CARD(id))).map(id=>R.CARD(id).v); const lab=document.querySelector('#cpHud .cpCmd [data-c=draw] b').textContent;
            R.tapCard(mine,null); for(let k=0;k<12;k++){ MG.step(.05,false); await null; await null; } return [ok.every(v=>v==='d2'||v==='wild4'), lab, G.pend]; }""")
        ok(r=='over' or (r[0] and r[1]=="2장 받기" and r[2]==4), f"③ 쌓였을 때 +2 만 빛남 · 단추 「2장 받기」 · 내가 +2 내면 4 {r}")
        await pg.evaluate("()=>{ MG.run.auto=true; MG.run.fast=true; }")
        st=await run_auto(pg); c=await pg.evaluate(CHECK)
        ok(c["over"] and c["total"]==108 and c["uniq"]==108 and st<=40, f"③ 쌓기 규칙 판 끝까지 · 108장 {c} 멈춤 {st}")
        # ② 미션 완료 (한 판 끝까지) → 🪙
        r=await pg.evaluate("()=>{ const m=store('hyeng_proto_cpm')||{}; return [m.got&&m.got.games, (m.p||{}).games, MG.run.missList().find(x=>x.k==='games').ok]; }")
        ok(r[0]==1 and r[1]>=1 and r[2], f"② 미션 「한 판 끝까지」 완료 · 저장 {r}")
        await pg.evaluate("()=>MG.run.fast=false"); await pg.wait_for_timeout(1300); await pg.screenshot(path=OUTD+"end.png")
        r=await pg.evaluate("()=>[!!document.querySelector('#cpHud .cpEnd .ms'), document.querySelectorAll('#cpHud .cpEnd .ms div').length]")
        ok(r==[True,3], f"② 끝 화면에 미션 3줄 {r}")
        await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(700)
        # ② 뒷면 열림 (1승) → 고르기 → 뽑기 더미
        await pg.evaluate("()=>{ const r=MG.rec(); r.t.card=r.t.card||{}; r.t.card.win=Math.max(1,r.t.card.win|0); store('hyeng_proto_mg', r); }")
        await menu(pg); await pg.evaluate("()=>MG.run.menuGo('bk')"); await pg.wait_for_timeout(200)
        r=await pg.evaluate("()=>{ const M=document.querySelector('#cpHud .cpMenu'); const lk=M.querySelector('[data-bk=night]').classList.contains('lock'); M.querySelector('[data-bk=night]').click(); return [lk, MG.run.SET.bk, (store('hyeng_proto_cpset')||{}).bk]; }")
        ok(r==[False,"night","night"], f"② 1승 → 별밤 뒷면 열림 · 고름 · 저장 {r}")
        await pg.screenshot(path=OUTD+"backs2.png")
        # ⑥ 자동 4판 (보통 · 쉬움, 7장 · 쌓기 끔)
        await pg.evaluate("()=>{ MG.run.menuGo('home'); const s=MG.run.SET; s.hs=7; s.stk=0; store('hyeng_proto_cpset', s); }")
        await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(500)
        res=[]
        for gi in range(4):
            await menu(pg); await pg.evaluate("(d)=>{ MG.run.SET.df=d; MG.run.menuGo('solo'); MG.run.auto=true; MG.run.fast=true; }", "easy" if gi%2 else "normal")
            st=await run_auto(pg); c=await pg.evaluate(CHECK)
            res.append((c["over"], c["total"], c["uniq"], st))
            await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(500)
        ok(all(x[0] and x[1]==108 and x[2]==108 and x[3]<=40 for x in res), f"⑥ 자동 4판 끝까지 · 108장 {res}")
        ok(not errs, f"오류 0 {errs[:5]}")
        await ctx.close()

        # ⑤ 같이 하기 (3명 + 봇 1)
        cA,A_,eA=await boot(br,"루아","CO634A", isle=False); cB,B_,eB=await boot(br,"민수","CO634B", isle=False); cC,C_,eC=await boot(br,"지우","CO634C", isle=False)
        P3=[A_,B_,C_]
        for x in P3: await menu(x)
        async def steps(n=6, dt=.1):
            for _ in range(n):
                for x in P3: await x.evaluate("async (dt)=>{ MG.step(dt,false); await null; await null; }", dt)
                await A_.wait_for_timeout(50)
        await A_.evaluate("()=>MG.run.menuGo('co')"); await steps(3)
        await A_.evaluate("()=>MG.run.RM.make()"); await steps(4)
        for x in (B_, C_):
            await x.evaluate("()=>MG.run.menuGo('co')")
            for _ in range(15):
                await x.evaluate("()=>MG.run.RM.list()"); await steps(2)
                if await x.evaluate("()=>document.querySelectorAll('#mgUI [data-j]').length"): break
            await x.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await steps(4)
        r=[await x.evaluate("()=>[MG.run.RM.phase, document.querySelectorAll('#mgUI .mgRoomP .pl span').length]") for x in P3]
        ok(all(q[0]=="wait" for q in r) and r[0][1]==4, f"⑤ 셋이 같은 방 · 자리 4 (빈자리 🤖) {r}")
        await A_.screenshot(path=OUTD+"co_room.png")
        await A_.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(4)
        for x in P3: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+9000; }")
        for _ in range(30):
            await steps(3)
            r=[await x.evaluate("()=>[MG.run.phase, MG.run.ME, MG.run.HOST, MG.run.G.top?MG.run.G.top.id:-1, MG.run.G.P.map(p=>p.nm+(p.bot?'🤖':'')).join(',')]") for x in P3]
            if all(q[0]=="play" and q[3]>=0 for q in r): break
        ok(all(q[0]=="play" for q in r) and sorted(q[1] for q in r)==[0,1,2] and [q[2] for q in r]==[True,False,False] and len(set(q[3] for q in r))==1 and len(set(q[4] for q in r))==1 and r[0][4].count("🤖")==1,
           f"⑤ 모두 같은 판 · 자리 0/1/2 · 방장 A · 같은 첫 카드 · 같은 자리표 {r}")
        await steps(6)
        await B_.screenshot(path=OUTD+"co_B.png")
        for x in P3: await x.evaluate("()=>{ MG.run.auto=true; MG.run.fast=true; }")
        done=False
        for it in range(500):
            await steps(2, .1)
            o=[await x.evaluate("()=>[MG.run.G.over, MG.run.phase]") for x in P3]
            if all(q[0] for q in o): done=True; break
        await steps(20)
        r=[await x.evaluate("()=>{ const G=MG.run.G; return [G.over, G.P.map(p=>p.h.length).join(','), G.pile.length+G.draw.length+G.P.reduce((s,p)=>s+p.h.length,0), MG.run.phase, !!document.querySelector('#cpHud .cpEnd.on')]; }") for x in P3]
        ok(done and len(set(q[1] for q in r))==1 and all(q[2]==108 for q in r) and all(q[4] for q in r), f"⑤ 같이 끝까지 · 세 화면 같은 결과 · 108장 · 끝 화면 {r}")
        await C_.screenshot(path=OUTD+"co_end.png")
        r=[await x.evaluate("()=>(MG.rec().t.card||{}).co") for x in P3]
        ok(all(q==1 for q in r), f"⑤ 같이 한 판 기록 (우정 뒷면 조건) {r}")
        for e in (eA,eB,eC): errs_all.append(e)
        ok(not (eA+eB+eC), f"오류 0 (같이) {(eA+eB+eC)[:5]}")
        for c_ in (cA,cB,cC): await c_.close()
        # 사진 패드 · 가로 (메뉴)
        for nm,vp in [("pad",{"width":820,"height":1180}),("land",{"width":844,"height":390})]:
            ctx,pg,errs=await boot(br,"루아","CP634"+nm, vp=vp, isle=False); await menu(pg); await pg.screenshot(path=OUTD+nm+"_menu.png")
            await pg.evaluate("()=>MG.run.menuGo('solo')")
            for _ in range(80):
                if await pg.evaluate("()=>MG.run.isMyTurn()"): break
                await pg.evaluate(STEP, 6)
            await pg.wait_for_timeout(1300); await pg.screenshot(path=OUTD+nm+"_turn.png"); await ctx.close()
            ok(not errs, f"오류 0 ({nm}) {errs[:3]}")
        await br.close()
    print("BAD:", len(bad)); sys.exit(1 if bad else 0)
if __name__=="__main__": asyncio.run(main())
