"""(v587) 사용자: 「새로 마을을 만들어 주고 퀘스트를 줘 · 아이들이 은화 20개 30개씩 퀘스트를 고르게」 · 「마을 사람 + 의뢰판 + 섬 빈 자리에 새 마을 · 마을만의 뭔가」
   ① 🍄 버섯 마을 = 섬 구역(지도) · 버섯 집 4 · 📌 의뢰판 · 🍄 큰 버섯 · 마을 사람 4명이 걸어 다님 · 이름표
   ② 의뢰판: 오늘 6개 · 3개까지 고르기 · 해 오기(받은 뒤 센 것) · 가져다주기(가진 것 건넴) → 🪙 20/30 + ❤️
   ③ ❤️ 3 → 🍄 버섯 의자 선물 · 🍄 큰 버섯 하루 한 번 · 다시 열어도 그대로"""
import asyncio, sys, os
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
        for nm,vp in [("pad",{"width":820,"height":1180}),("phone",{"width":390,"height":844})]:
            ctx=await br.new_context(viewport=vp, is_mobile=nm=="phone", has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
            await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('VIL87')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
            await pg.reload(); await pg.wait_for_timeout(2800)
            await pg.evaluate("()=>HOUSE.exitRoom()")
            for _ in range(160):
                if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
                await pg.wait_for_timeout(250)
            await pg.wait_for_timeout(1000)
            if nm=="pad":
                r=await pg.evaluate("()=>[!!ISLE_MAP.zones.find(z=>z.k==='vil'), !!(VIL.SP()||{}).board, !!(VIL.SP()||{}).big, VIL.W().length, ISLE.blocked(Math.floor(VIL.SP().board[0]), Math.floor(VIL.SP().board[2]))]")
                ok(r[0] and r[1] and r[2] and r[3]==4 and r[4], f"① 🍄 버섯 마을 구역 · 의뢰판 · 큰 버섯 · 마을 사람 4 · 부딪힘 {r}")
            await pg.evaluate("()=>{ const s=ISLE_MAP.spots.vil; HOUSE.setWx(false); TFAC.warp(s[0]+ISLE.OX+1, s[1]+ISLE.OZ+8.5); ISLE.CAM.zoom="+("2.3" if nm=="pad" else "2.0")+"; ISLE.CAM.pitch=.95; yaw=yawTo=Math.PI; ISLE.CAM.dragAt=performance.now()+1e6; }")
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=OUT+"vil587_"+nm+".png")
            if nm=="pad":
                r=await pg.evaluate("()=>{ const W=VIL.W(); const a=W.map(w=>w.c.g.position.clone()); for(let i=0;i<40;i++) VIL.tick(0.1); return [W.filter((w,i)=>w.c.g.position.distanceTo(a[i])>0.05).length, LBL.filter(l=>/^v_/.test(l.d.k)).map(l=>l.d.k)]; }")   # 시험 화면은 느려서 시간을 직접 넘김
                ok(r[0]>=1 and "v_board" in r[1] and "v_tom" in r[1], f"① 마을 사람이 걸어 다님 · 이름표 {r}")
                # ② 의뢰판
                await pg.evaluate("()=>VIL.open()"); await pg.wait_for_timeout(500)
                r=await pg.evaluate("()=>[document.querySelectorAll('#vlP .vQ').length, [...document.querySelectorAll('#vlP [data-acc]')].length, document.getElementById('vlP').innerText.includes('🪙')]")
                ok(r[0]==6 and r[1]==6 and r[2], f"② 의뢰판 = 오늘 6개 · 고르기 {r}")
                await pg.screenshot(path=OUT+"vil587_board.png")
                r=await pg.evaluate("""()=>{ const L=VIL.today(); for(let i=0;i<4;i++){ const b=document.querySelector('#vlP [data-acc]:not(:disabled)'); if(b) b.click(); } const s=VIL.st(); return [Object.keys(s.acc).length, document.querySelectorAll('#vlP [data-acc]:disabled').length]; }""")
                ok(r[0]==3 and r[1]==3, f"② 3개까지만 고름 (나머지 막힘) {r}")
                r=await pg.evaluate("""()=>{ const s=VIL.st(), L=VIL.today().filter(q=>s.acc[q.id]); const c0=TECO.coins();
                    L.forEach(q=>{ if(q.kind==='d'){ for(let i=0;i<q.n;i++) tEv(q.x); } else if(q.x==='fish'){ for(let i=0;i<q.n;i++) bag.push({en:'fish', at:Date.now(), cm:20}); } else addMat(q.x, q.n); });
                    const ready=L.map(q=>[q.id, q.kind, q.x]); let sum=0; L.forEach(q=>{ if(VIL.claim(q)) sum+=q.r; }); return [ready.length, TECO.coins()-c0, sum, VIL.hearts(), L.every(q=>s.done[q.id])]; }""")
                ok(r[0]==3 and r[1]==r[2] and r[2]>=60 and r[3]==3 and r[4], f"② 의뢰 3개 끝 → 🪙 {r[1]} · ❤️ 3 {r}")
                await pg.wait_for_timeout(2000)
                r=await pg.evaluate("()=>[ystock.mushstool|0, VIL.st().g.mushstool]")
                ok(r==[1,1], f"③ ❤️ 3 → 🍄 버섯 의자 선물 {r}")
                r=await pg.evaluate("()=>{ const s=VIL.st(); s.d=''; VIL.st(); const L=VIL.today(); const q=L.find(q=>q.kind==='d'); VIL.accept(q); tEv(q.x); const a=s.acc[q.id].c; return [a, Object.keys(s.done).length]; }")
                ok(r[0]==1 and r[1]==0, f"② 다음 날 = 새 의뢰 · 받은 뒤부터 셈 {r}")
                r=await pg.evaluate("()=>{ const c0=TECO.coins(), b0=bait; VIL.bigShroom(); const a=TECO.coins()-c0+(bait-b0)+(mats['strawberry seeds']|0); const c1=TECO.coins(); VIL.bigShroom(); return [a>0, TECO.coins()-c1]; }")
                ok(r==[True,0], f"③ 🍄 큰 버섯 = 하루 한 번 선물 {r}")
                await pg.evaluate("()=>document.getElementById('vlP').classList.remove('on')")
                r=await pg.evaluate("()=>{ openQ(); const t=document.getElementById('qBody').innerText; document.getElementById('qP').classList.remove('on'); return [/버섯 마을 의뢰/.test(t), /의뢰판 보기/.test(t)]; }")
                ok(r==[True,True], f"② 📋 할 일 창에 「📌 버섯 마을 의뢰」 {r}")
                r=await pg.evaluate("()=>{ TFAC.openStation && 0; const d=[...document.querySelectorAll('[data-ds]')].map(b=>b.dataset.ds); return true; }")
                await pg.reload(); await pg.wait_for_timeout(2600)
                r=await pg.evaluate("()=>[VIL.hearts(), VIL.st().g.mushstool|0, !!localStorage.getItem('hyeng_proto_vil')]")
                ok(r==[3,1,True], f"③ 다시 열어도 하트·선물 그대로 {r}")
            await ctx.close()
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
