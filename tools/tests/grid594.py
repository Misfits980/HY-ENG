"""(v594) 사용자: 「애들이랑 발판 게임 같이 하면 스테이지마다 안전한 지역이 변해야 하고 레이저 패턴도 달라져야 · 다 같이 최대 5명」
   → 「혼자 하기 · 같이 하기 대기방 · 방장이 게임 시작 → 10초 뒤 · 순위 말고 같이 몇 점」
   ① 판마다 🟩 안전 칸 모양 · 🟥 무늬 테마가 바뀜 · 같은 번호 = 같은 판
   ② 같이 하기: A 가 방 만들기 → B·C 가 방 목록에서 들어감 · 5명 넘으면 못 들어감 · 방장만 「게임 시작」 · 10초 세기
   ③ 세 화면이 같은 판(같은 칸·같은 빨강 시간표) · B 가 밟은 칸이 A·C 에서도 지워짐 · 함께 점수 같음 · 친구 모습이 보임
   ④ 파랑을 다 지우면 방장이 다음 판 → 모두 2판 (안전 칸 자리 바뀜) · ❤️ 다 쓰면 구경 → 모두 구경이면 끝 → 결과 = 「🤝 함께 ⭐ N점」"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def boot(br, nick, code):
    ctx=await br.new_context(viewport={"width":420,"height":760}, is_mobile=True, has_touch=True)
    pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
    await pg.evaluate("([n,c])=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }", [nick, code])
    await pg.reload(); await pg.wait_for_timeout(2400)
    await pg.evaluate("()=>MG.enter('grid',{mode:'co'})"); await pg.wait_for_timeout(1500)
    return ctx, pg, errs

async def steps(pgs, n=8, dt=.1):
    for _ in range(n):
        for pg in pgs: await pg.evaluate("(dt)=>{ MG.step(dt,false); }", dt)
        await pgs[0].wait_for_timeout(60)

async def main():
    bad=[]; allerr=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        cA,A,eA=await boot(br,"루아","AAAA2"); cB,B,eB=await boot(br,"민수","BBBB3"); cC,C,eC=await boot(br,"지우","CCCC4")
        P3=[A,B,C]
        # ① 판 설계
        r=await A.evaluate("""()=>{ const R=MG.run, g=s=>[...R.plan(77,s).cell].map((v,i)=>v===2?i:-1).filter(i=>i>=0).join(","), th=s=>R.plan(77,s).th, H=s=>R.plan(77,s).H.map(h=>h.k);
            const same=g(0)===R.plan(77,0).G.slice().sort((a,b)=>a-b).join(",") || true; const a=[0,1,2,3,4].map(g), k=[0,1,2,3,4].map(H);
            return [new Set(a).size, [0,1,2,3,4].map(th), k.map(x=>[...new Set(x)].sort().join("+")), JSON.stringify(R.plan(77,3))===JSON.stringify(R.plan(77,3))]; }""")
        ok(r[0]==5 and r[1]==[0,1,2,3,4] and len(set(r[2]))>=4 and r[3], f"① 판마다 🟩 안전 칸 모양 5가지 · 🟥 무늬 테마 {r}")
        # ② 방 만들기 · 들어가기
        await A.evaluate("()=>MG.run.mkRoom()"); await A.wait_for_timeout(500)
        await A.screenshot(path=OUT+"grid594_room_host.png")
        for _ in range(12):
            await B.evaluate("()=>MG.run.listRooms()"); await B.wait_for_timeout(300)
            r=await B.evaluate("()=>[...document.querySelectorAll('#mgUI [data-j]')].map(b=>b.textContent)")
            if r: break
        ok(len(r)==1 and "루아" in r[0], f"② B 화면 방 목록에 「루아의 방」 {r}")
        await B.screenshot(path=OUT+"grid594_list.png")
        await B.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await B.wait_for_timeout(600)
        rid=await A.evaluate("()=>MG.run.R.id")
        # 5명 꽉 참 → 못 들어감
        await A.evaluate("(id)=>{ const t=srvNow(); ['F1','F2','F3','F4'].forEach(k=>NET.put('/hy/day/mgg'+dayKey().replace(/\\D/g,'')+'/'+id+'/p/'+k, {n:k, x:0,z:0,y:0,l:3,o:0,t})); }", rid); await A.wait_for_timeout(300)
        await C.evaluate("(id)=>MG.run.joinRoom(id)", rid); await C.wait_for_timeout(600)
        r=await C.evaluate("()=>MG.run.st.phase")
        ok(r=="room", f"② 6명이면 못 들어감 (C 는 방 목록에 남음) {r}")
        await A.evaluate("(id)=>{ ['F1','F2','F3','F4'].forEach(k=>NET.del('/hy/day/mgg'+dayKey().replace(/\\D/g,'')+'/'+id+'/p/'+k)); }", rid); await A.wait_for_timeout(300)
        await C.evaluate("(id)=>MG.run.joinRoom(id)", rid); await C.wait_for_timeout(600)
        await steps(P3, 6)
        r=[await x.evaluate("()=>[MG.run.st.phase, document.querySelectorAll('#mgUI .gRoom .pl span').length, !!document.querySelector('#mgUI [data-st]')]") for x in P3]
        ok(all(q[0]=="wait" and q[1]==3 for q in r) and r[0][2] and not r[1][2] and not r[2][2], f"② 셋 다 대기방 · 3명 보임 · 「게임 시작」은 방장만 {r}")
        await A.screenshot(path=OUT+"grid594_wait.png")
        # 시작 → 10초 세기
        await A.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await A.wait_for_timeout(500)
        await steps(P3, 5)
        r=[await x.evaluate("()=>[MG.run.st.phase, document.querySelector('#mgUI .gCnt').textContent]") for x in P3]
        ok(all(q[0]=="count" and q[1] in ("10","9","8","7") for q in r), f"② 방장이 시작 → 모두 10초 세기 {r}")
        for x in P3: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+10500; }")
        await steps(P3, 6)
        # ③ 같은 판
        r=[await x.evaluate("()=>{ const R=MG.run; return [R.st.phase, R.st.stage, R.st.seed, [...R.cell].join(''), R.st.pl.H.length, R.st.pl.H.slice(0,3).map(h=>h.k+h.t0.toFixed(2)).join(',')]; }") for x in P3]
        ok(all(q[0]=="play" for q in r) and len(set(q[2] for q in r))==1 and len(set(q[3] for q in r))==1 and len(set(q[5] for q in r))==1, f"③ 세 화면 같은 판 (번호·칸·빨강 시간표) {[q[:3] for q in r]}")
        q=await B.evaluate("()=>{ const R=MG.run; R.P.inv=9; const q=[...R.cell].findIndex(v=>v===1); R.P.p.set(R.cx(q%R.N),0,R.cx(Math.floor(q/R.N))); MG.step(.03,false); return q; }")
        await steps(P3, 6)
        r=[await x.evaluate("(q)=>[MG.run.cell[q], MG.run.st.score, Object.keys(MG.run.R.peers).length]", q) for x in P3]
        ok(all(z[0]==3 for z in r) and len(set(z[1] for z in r))==1 and r[0][1]==10 and all(z[2]==2 for z in r), f"③ B 가 밟은 칸 = 모두 지워짐 · 함께 점수 같음 · 친구 2명 보임 {r}")
        await A.evaluate("()=>{ const R=MG.run; R.P.p.set(0,0,2); }"); await B.evaluate("()=>{ MG.run.P.p.set(-2,0,0); }"); await C.evaluate("()=>{ MG.run.P.p.set(2.5,0,-1); }")
        await steps(P3, 8)
        await A.wait_for_timeout(1200); await A.screenshot(path=OUT+"grid594_play.png")
        # ④ 다 지우면 다음 판
        g1=await A.evaluate("()=>[...MG.run.cell].map((v,i)=>v===2?i:-1).filter(i=>i>=0).join(',')")
        await B.evaluate("""async ()=>{ const R=MG.run; R.P.inv=99; for(let q=0;q<R.N*R.N;q++){ if(R.cell[q]===1){ R.P.p.set(R.cx(q%R.N),0,R.cx(Math.floor(q/R.N))); MG.step(.02,false); } } }""")
        await steps(P3, 8)
        r=[await x.evaluate("()=>[MG.run.st.blue, MG.run.st.clrS, MG.run.R.d.h.sg && MG.run.R.d.h.sg.s, MG.run.st.stage]") for x in P3]
        ok(all(z[1]==0 or z[3]==1 for z in r) and r[0][2]==1, f"④ 파랑 다 지움(1판 깸) → 방장이 다음 판 예약 {r}")
        for x in P3: await x.evaluate("()=>{ TWN8.test+=3000; }")
        await steps(P3, 6)
        r=[await x.evaluate("()=>[MG.run.st.stage, [...MG.run.cell].map((v,i)=>v===2?i:-1).filter(i=>i>=0).join(','), MG.run.st.score]") for x in P3]
        ok(all(z[0]==1 for z in r) and len(set(z[1] for z in r))==1 and r[0][1]!=g1 and len(set(z[2] for z in r))==1, f"④ 모두 2판 · 안전 칸 자리 바뀜 · 함께 점수 {r[0][2]}")
        # 구경 → 모두 구경이면 끝
        await C.evaluate("()=>{ const R=MG.run; R.st.lives=1; R.P.inv=0; const z=[...R.cell].findIndex(v=>v===0); R.P.p.set(R.cx(z%R.N),0,R.cx(Math.floor(z/R.N))); R.st.pl.H.push({t0:R.st.el, k:'blink', L:[z], w:0, on:5}); MG.step(.03,false); }")
        await steps(P3, 6)
        r=[await C.evaluate("()=>[MG.run.st.out, MG.run.st.over, getComputedStyle(document.querySelector('#mgUI .gOut')).display]"), await A.evaluate("()=>Object.values(MG.run.R.peers).filter(p=>p.o).length")]
        ok(r[0][0] and not r[0][1] and r[0][2]!="none" and r[1]==1, f"④ C ❤️ 다 씀 → 구경 (끝나지 않음) · A 에서 C 가 구경으로 보임 {r}")
        for x in (A,B): await x.evaluate("()=>{ const R=MG.run; R.st.lives=1; R.P.inv=0; const z=[...R.cell].findIndex(v=>v===0); R.P.p.set(R.cx(z%R.N),0,R.cx(Math.floor(z/R.N))); R.st.pl.H.push({t0:R.st.el, k:'blink', L:[z], w:0, on:5}); MG.step(.03,false); }")
        await steps(P3, 10)
        await A.wait_for_timeout(1800)
        r=[await x.evaluate("()=>{ const el=document.getElementById('mgRes'); return [!!el && el.classList.contains('on'), el ? el.querySelector('h3').textContent : '']; }") for x in P3]
        ok(all(z[0] for z in r) and len(set(z[1] for z in r))==1 and "함께" in r[0][1], f"④ 모두 구경 → 끝 · 결과 = 같은 「함께 점수」 {r}")
        await A.screenshot(path=OUT+"grid594_result.png")
        # 혼자 하기도 판마다 바뀜
        await A.evaluate("()=>{ document.querySelector('#mgRes .out').click(); }"); await A.wait_for_timeout(1300)
        await A.evaluate("()=>MG.enter('grid',{mode:'solo'})"); await A.wait_for_timeout(1500)
        r=await A.evaluate("()=>{ const R=MG.run; const g0=[...R.cell].map((v,i)=>v===2?i:-1).filter(i=>i>=0).join(','); R.P.inv=99; for(let q=0;q<R.N*R.N;q++){ if(R.cell[q]===1){ R.P.p.set(R.cx(q%R.N),0,R.cx(Math.floor(q/R.N))); MG.step(.02,false); } } for(let i=0;i<60;i++) MG.step(.05,false); const g1=[...R.cell].map((v,i)=>v===2?i:-1).filter(i=>i>=0).join(','); return [R.st.phase, R.st.stage, g0!==g1]; }")
        ok(r==["play",1,True], f"혼자 하기: 2판에서 안전 칸 자리가 바뀜 {r}")
        allerr=eA+eB+eC
        await br.close()
    ok(not allerr, f"오류 없음 {allerr[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__=="__main__": asyncio.run(main())
