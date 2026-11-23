"""(v718) 🎡 오락실 — 사용자 사진·말 (2026-11-23 수업)
   ① 🎨 그림 맞히기: 옛 아이패드 세로에서 「✔ 확인」 단추가 화면 밖 → 칠판을 남는 높이에 맞춤
   ② 🍉 과일 합치기: 「화면이 커졌다 작아졌다 · 과일들마다 화면이 달라지는 느낌」 → 랭킹 판 높이 고정 · 판 크기 그대로
   ③ 🃏 컬러팡: 「1등이 이겼는데 게임이 안 끝나는 아이들」 → 늦게 받은 친구도 끝 화면 · 방장이 바로 나가면 이어받은 친구가 끝냄 · 방 쓰기 하나씩"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
from playwright.async_api import async_playwright
OUTD=OUT+"arc718/"; os.makedirs(OUTD, exist_ok=True)
bad=[]
def ok(c,m):
    print(("OK  " if c else "BAD ")+m, flush=True)
    if not c: bad.append(m)
async def enter(pg, k, how="enter"):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    for t in range(3):
        await pg.evaluate("(k)=>{ if(!MG.on) MG.enter(k,{}); }", k) if how=="enter" else await pg.evaluate("(k)=>MG.lobby(k)", k)
        for _ in range(80):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
    await pg.wait_for_timeout(400)
STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } }"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        # ① 그림 맞히기 — 혼자(자판) · 친구 줄이 두 줄일 때도 확인 단추가 화면 안
        for vp in ({"width":768,"height":900}, {"width":810,"height":1010}, {"width":390,"height":700}):
            ctx,pg,errs=await boot(br,"루아","DW718A", vp=vp, isle=False)
            await enter(pg, "draw")
            await pg.evaluate("()=>MG.run.menuGo('solo')"); await pg.wait_for_timeout(300)
            if vp["width"] >= 700: await pg.evaluate("""()=>{ const P=document.querySelector('#mgUI .dwPl'); if(P){ P.style.display='flex'; P.innerHTML=Array.from({length:7},(x,i)=>'<span style="display:inline-block;width:150px;height:34px;background:#fff;border-radius:99px">친구'+i+'</span>').join('')+'<div style="width:100%;height:52px"></div>'; } }""")
            await pg.evaluate(STEP, 30); await pg.wait_for_timeout(200)
            r=await pg.evaluate("""()=>{ const b=[...document.querySelectorAll('#mgUI .dwKb button')].find(x=>x.dataset.k==='ok'), R=b && b.getBoundingClientRect(), bd=document.querySelector('#mgUI .dwBd').getBoundingClientRect(), W=document.querySelector('#mgUI .dwR');
                return {ok:!!b, bot:R?Math.round(R.bottom):-1, H:innerHeight, over:W.scrollHeight-W.clientHeight, bd:[Math.round(bd.width), Math.round(bd.height)]}; }""")
            ok(r["ok"] and r["bot"] <= r["H"] and r["over"] <= 1 and r["bd"][0] >= 150, f"① 그림 맞히기 {vp['width']}×{vp['height']}{' (친구 줄 두 줄)' if vp['width'] >= 700 else ''}: ✔ 확인 단추 화면 안 {r}")
            await pg.screenshot(path=OUTD+"draw_%d.png" % vp["width"])
            ok(not errs, f"① 오류 없음 {errs[:3]}")
            await ctx.close()
        # ② 과일 합치기 — 랭킹 탭마다 줄 수가 달라도 판 크기 그대로
        ctx,pg,errs=await boot(br,"루아","FR718A", vp={"width":768,"height":954}, isle=False)
        await pg.evaluate("""async ()=>{ const now=srvNow(), d=new Date(now+9*3600e3); const y=d.getUTCFullYear(), m=d.getUTCMonth()+1;
            const t=new Date(Date.UTC(y,d.getUTCMonth(),d.getUTCDate())), dn=(t.getUTCDay()+6)%7; t.setUTCDate(t.getUTCDate()-dn+3); const y1=new Date(Date.UTC(t.getUTCFullYear(),0,4)); const wk=1+Math.round(((t-y1)/864e5-3+((y1.getUTCDay()+6)%7))/7);
            const K={W:"frW"+t.getUTCFullYear()+String(wk).padStart(2,"0"), M:"frM"+y+String(m).padStart(2,"0"), A:"frA"};
            await NET.put("/hy/day/"+K.W, {X1:{n:"민수",s:420,at:1}});
            await NET.put("/hy/day/"+K.M, {X1:{n:"민수",s:420,at:1}, X2:{n:"지우",s:910,at:2}, X3:{n:"하늘",s:1500,at:3}});
            await NET.put("/hy/day/"+K.A, {X1:{n:"민수",s:420,at:1}, X2:{n:"지우",s:910,at:2}, X3:{n:"하늘",s:1500,at:3}, X4:{n:"별님",s:99999,at:4}, X5:{n:"달님",s:5000,at:5}}); }""")
        await enter(pg, "fruit", "lobby")
        await pg.evaluate("()=>{ const b=document.querySelector('#mgUI .puM [data-m=go]'); if(b) b.click(); else MG.run.begin(); }")
        for _ in range(40):
            if await pg.evaluate("()=>MG.run.phase==='play' || MG.run.phase==='ready'"): break
            await pg.wait_for_timeout(150)
        ws=[]
        for k in ("W", "M", "A", "W", "M"):
            await pg.evaluate("(k)=>MG.run.tab(k)", k); await pg.evaluate(STEP, 70); await pg.wait_for_timeout(120)
            ws.append(await pg.evaluate("()=>{ const c=document.querySelector('#mgUI .frBox canvas'), L=document.querySelector('#mgUI .frR .frLed'); return [Math.round(c.getBoundingClientRect().width), Math.round(L.getBoundingClientRect().height), document.querySelectorAll('#mgUI .frR .frLed .rw').length]; }"))
        ok(len(set(w[0] for w in ws)) == 1 and len(set(w[1] for w in ws)) == 1 and len(set(w[2] for w in ws)) >= 2, f"② 과일 합치기: 랭킹 탭(줄 {[w[2] for w in ws]})이 바뀌어도 판 {[w[0] for w in ws]}px · 랭킹 높이 {[w[1] for w in ws]} 그대로")
        r=await pg.evaluate("()=>{ const B=document.querySelector('#mgUI .frBox').getBoundingClientRect(), c=document.querySelector('#mgUI .frBox canvas').getBoundingClientRect(); return [Math.round(c.bottom), Math.round(B.bottom), innerHeight]; }")
        ok(r[0] <= r[1] + 1 and r[0] <= r[2], f"② 판이 자리 안 {r}")
        await pg.screenshot(path=OUTD+"fruit.png")
        ok(not errs, f"② 오류 없음 {errs[:3]}")
        await ctx.close()
        # ③ 컬러팡 같이 — 방장 A 가 끝 소식을 못 보내고 바로 나감 · C 는 늦게 따라옴
        cA,A_,eA=await boot(br,"루아","CO718A", isle=False); cB,B_,eB=await boot(br,"민수","CO718B", isle=False); cC,C_,eC=await boot(br,"지우","CO718C", isle=False)
        P3=[A_,B_,C_]
        for x in P3: await enter(x, "card")
        async def steps(L, n=6, dt=.1):
            for _ in range(n):
                for x in L: await x.evaluate("async (dt)=>{ MG.step(dt,false); await null; await null; }", dt)
                await A_.wait_for_timeout(40)
        await A_.evaluate("()=>MG.run.menuGo('co')"); await steps(P3, 3)
        await A_.evaluate("()=>MG.run.RM.make()"); await steps(P3, 4)
        for x in (B_, C_):
            await x.evaluate("()=>MG.run.menuGo('co')")
            for _ in range(15):
                await x.evaluate("()=>MG.run.RM.list()"); await steps(P3, 2)
                if await x.evaluate("()=>document.querySelectorAll('#mgUI [data-j]').length"): break
            await x.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await steps(P3, 4)
            for _ in range(16):
                if await x.evaluate("()=>MG.run.RM.phase==='wait'"): break
                await steps(P3, 1)
        await A_.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(P3, 4)
        for x in P3: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+9000; }")
        for _ in range(30):
            await steps(P3, 3)
            r=[await x.evaluate("()=>[MG.run.phase, MG.run.HOST]") for x in P3]
            if all(q[0]=="play" for q in r): break
        ok(all(q[0]=="play" for q in r) and r[0][1] and not r[1][1] and not r[2][1], f"③ 셋이 같은 판 · 방장 A {r}")
        # A 가 보내는 방 상태 중 「끝」 이 든 것은 버림 (= 늦게 도착한 옛 상태가 덮은 것과 같음)
        await A_.evaluate("()=>{ const RM=MG.run.RM, p0=RM.put; RM.put=(sub,v)=>{ if(sub==='g' && v && ((v.A||[]).some(a=>a.t==='end') || (v.s && v.s.over))) return; p0(sub,v); }; }")
        for x in P3: await x.evaluate("()=>{ MG.run.auto=true; MG.run.fast=true; }")
        frozeC=False
        for it in range(600):
            L=[A_,B_] if frozeC else P3
            await steps(L, 2, .1)
            o=await A_.evaluate("()=>[MG.run.G.over, Math.min(...MG.run.G.P.map(p=>p.h.length))]")
            if not frozeC and o[1] <= 2: frozeC=True
            if o[0]: break
        ok(o[0], f"③ A 화면: 판 끝 {o}")
        await A_.evaluate("()=>MG.exit()"); await A_.wait_for_timeout(300)
        for _ in range(30):   # 7초 넘게 방장이 안 보이면 B 가 이어받음 → 빈손 친구가 있으면 끝냄
            await steps([B_], 5, .1)
            if await B_.evaluate("()=>MG.run.phase==='end'"): break
        r=await B_.evaluate("()=>[MG.run.phase, MG.run.HOST, MG.run.G.over, !!document.querySelector('#cpHud .cpEnd.on')]")
        ok(r[0]=="end" and r[1] and r[2] and r[3], f"③ 방장이 끝을 못 보내고 나감 → B 가 이어받아 끝 화면 (예전: 빈손 친구를 두고 차례 계속) {r}")
        # C: 오래 멈췄다 다시 — 방 상태가 이미 「끝」 이면 끝 화면까지 (예전: G.over 만 켜지고 그대로)
        await C_.evaluate("()=>{ MG.run.G.sq=-5; }")
        for _ in range(30):
            await steps([B_, C_], 5, .1)
            if await C_.evaluate("()=>MG.run.phase==='end'"): break
        r=await C_.evaluate("()=>[MG.run.phase, MG.run.G.over, !!document.querySelector('#cpHud .cpEnd.on'), MG.run.G.P.map(p=>p.h.length).join(',')]")
        rb=await B_.evaluate("()=>MG.run.G.P.map(p=>p.h.length).join(',')")
        ok(r[0]=="end" and r[1] and r[2] and r[3]==rb, f"③ 늦게 따라온 C 도 끝 화면 · B 와 같은 손 {r} / {rb}")
        await C_.screenshot(path=OUTD+"card_C_end.png")
        ok(not (eA+eB+eC), f"③ 오류 없음 {(eA+eB+eC)[:4]}")
        # 방 쓰기 하나씩: 같은 칸에 PUT 5개를 한꺼번에 → 서버에 마지막 것
        r=await B_.evaluate("""async ()=>{ const RM=MG.run.RM; if(!RM.path) return 'nopath'; for(let i=1;i<=5;i++) RM.put('zz', {i}); for(let k=0;k<40;k++){ await new Promise(r=>setTimeout(r,100)); const v=await NET.get(RM.path+'/zz'); if(v && v.i===5) return 5; } const v=await NET.get(RM.path+'/zz'); return v && v.i; }""")
        ok(r==5 or r=="nopath", f"③ 같은 칸에 여러 번 쓰면 마지막 것이 남음 {r}")
        for c in (cA,cB,cC): await c.close()
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
