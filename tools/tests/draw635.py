"""(v635) 🎨 그림 맞히기 — 사용자 「1번 응 다 좋은데 글자를 직접 써야 한다고 봐」
   ① 놀이 섬 🎨 그림 공방(동쪽) · 누르면 바로 메뉴 (혼자 · 같이 · 그려 보기 · 그림첩 · 단계)
   ② 🧩 혼자 그림 퍼즐: 물감 칸이 떨어짐 · 글자 칸 = 단어 길이 · 틀림 ❌ · 거의 🔥 · 💡 힌트 · 🤔 모르겠어요 = 뒤에 다시 · 8문제 끝 → 🪙
   ③ 🖍️ 그려 보기 → 그림첩 1장
   ④ 👫 같이 3명: 같은 방 → 차례로 그림 · 고르기 → 줄이 친구 화면에 · 친구가 직접 써서 맞힘 · 틀린 글자는 서버에 안 감 · 6판 끝 · 세 화면 같은 점수
   ⑤ 사진 폰 · 패드 · 가로"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from playwright.async_api import async_playwright
OUTD=OUT+"draw635/"; os.makedirs(OUTD, exist_ok=True)

async def boot(br, nick, code, vp=None, isle=True):
    ctx=await br.new_context(viewport=vp or {"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: (m.type in ("error","warning")) and ("DW" in m.text or "MG" in m.text) and errs.append(m.text[:240]))
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
        await pg.evaluate("()=>{ if(!MG.on) MG.enter('draw',{}); }")
        for _ in range(60):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
    await pg.wait_for_timeout(300)

STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } }"""

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","DW635A", vp={"width":900,"height":700})
        # ① 건물 · 이름표 · 메뉴
        r=await pg.evaluate("()=>{ const L=[]; MG.labels(L); return [!!MG.SPOT.draw, L.map(x=>x.k).sort().join(','), MG.GM.draw && MG.GM.draw.menu]; }")
        ok(r[0] and "mg_draw" in r[1] and r[2], f"① 그림 공방 자리 · 이름표 mg_draw · 메뉴 게임 {r}")
        await pg.evaluate("()=>{ const g=MG.SPOT.draw; HOUSE.setWx(false); TFAC.warp(g[0]-5, g[2]+3); yaw=yawTo=-Math.PI/2+.35; ISLE.CAM.zoom=2.5; ISLE.CAM.pitch=.42; ISLE.CAM.dragAt=performance.now()+1e6; }")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=OUTD+"building.png")
        await ctx.close()
        ctx,pg,errs=await boot(br,"루아","DW635A")
        await pg.evaluate("()=>MG.lobby('draw')")
        for _ in range(80):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        await pg.wait_for_timeout(400)
        r=await pg.evaluate("()=>{ const M=document.querySelector('#mgUI .puM'); return [MG.run.mode, getComputedStyle(M).display, [...M.querySelectorAll('[data-m]')].map(b=>b.dataset.m).join(','), M.querySelectorAll('[data-sg]').length, !!M.querySelector('.out')]; }")
        ok(r==["menu","flex","solo,sketch,gal,co",3,True], f"① 공방 → 바로 메뉴 (혼자·같이·그려 보기·그림첩 · 단계 3) {r}")
        await pg.screenshot(path=OUTD+"menu.png")
        # ② 혼자 그림 퍼즐
        c0=await pg.evaluate("()=>TECO.coins()")
        await pg.evaluate("()=>MG.run.menuGo('solo')"); await pg.wait_for_timeout(200)
        r=await pg.evaluate("()=>{ const R=MG.run, S=R.S, w=R.ans(); return [R.mode, S.q.length+1, w.length, document.querySelectorAll('#mgUI .dwBx i').length, document.querySelectorAll('#mgUI .dwCov i').length, document.querySelectorAll('#mgUI .dwCov i.off').length, document.querySelectorAll('#mgUI .dwKb button').length]; }")
        ok(r[0]=="solo" and r[1]==8 and r[2]==r[3] and r[4]==12 and r[5]==0 and r[6]>=30, f"② 8문제 · 글자 칸 = 단어 길이 · 물감 칸 12 · 자판 {r}")
        await pg.evaluate(STEP, 60)   # 3초 → 칸 2개쯤 떨어짐
        r=await pg.evaluate("()=>[MG.run.S.pop, document.querySelectorAll('#mgUI .dwCov i.off').length]")
        ok(r[0]>=2 and r[0]==r[1], f"② 시간이 지나면 물감 칸이 떨어짐 {r}")
        await pg.wait_for_timeout(700); await pg.screenshot(path=OUTD+"solo.png")
        # 틀림 · 거의 · 힌트
        r=await pg.evaluate("""()=>{ const R=MG.run, w=R.ans(); const wrong=(w[0]==='q'?'z':'q').repeat(w.length); R.typeWord(wrong); R.submit(); const a=[R.fb, R.typed, R.S.miss];
            const nr=w.slice(0,-1)+(w.slice(-1)==='z'?'y':'z'); R.typeWord(nr); R.submit(); const b=R.fb; R.hint(); return [a, b, R.fb, Object.keys(R.hints).length]; }""")
        ok("❌" in r[0][0] and r[0][1]=="" and r[0][2]==1 and "거의" in r[1] and "💡" in r[2] and r[3]>=1, f"② 틀림 ❌ · 글자 지움 · 거의 🔥 · 💡 힌트 1글자 {r}")
        await pg.wait_for_timeout(300); await pg.screenshot(path=OUTD+"solo_near.png")
        # 모르겠어요 → 뒤에 다시
        r=await pg.evaluate("()=>{ const R=MG.run, S=R.S, w=R.ans(), cur=S.cur; R.giveUp(); return [S.q.indexOf(cur)>=0, /다시 나와요/.test(R.fb), S.wait, w]; }")
        ok(r[0] and r[1] and r[2], f"② 🤔 모르겠어요 → 정답 보여 줌 · 그 단어는 뒤에 다시 {r}")
        await pg.wait_for_timeout(250); await pg.screenshot(path=OUTD+"solo_give.png")
        await pg.evaluate(STEP, 60)
        # 끝까지 맞히기 (모르겠어요 한 단어도 다시 나와서 맞힘)
        seen=[]
        for _ in range(14):
            r=await pg.evaluate("()=>[MG.run.mode, MG.run.S.wait, MG.run.ans()]")
            if r[0]!="solo": break
            if not r[1]:
                seen.append(r[2]); await pg.evaluate("(w)=>{ MG.run.typeWord(w); MG.run.submit(); }", r[2])
            await pg.evaluate(STEP, 45)
        await pg.wait_for_timeout(800)
        r=await pg.evaluate("()=>{ const el=document.querySelector('#mgUI .puR'); return [MG.run.mode, MG.run.S.ok, MG.run.S.done, !!el, el?el.textContent:'', TECO.coins(), MG.payLeft('draw'), (store('hyeng_proto_dwr')||{}).ok]; }")
        ok(r[0]=="solo-end" and r[1]==8 and r[2]==8 and r[3] and "8 / 8" in r[4] and r[5]>c0 and r[6]==2 and r[7]==8, f"② 8문제 끝(다시 나온 단어도 맞힘) · 결과 창 · 🪙 · 하루 판 수 · 기록 {r} 문제 {len(seen)}")
        await pg.screenshot(path=OUTD+"solo_end.png")
        # 한 판 더 = 바로 혼자
        await pg.evaluate("()=>document.querySelector('#mgUI .puR .again').click()"); await pg.wait_for_timeout(400)
        r=await pg.evaluate("()=>[MG.run.mode, MG.run.S && MG.run.S.done]")
        ok(r==["solo",0], f"② 🔁 한 판 더 → 바로 그림 퍼즐 {r}")
        # ③ 그려 보기 → 그림첩
        await pg.evaluate("()=>MG.run.menuShow()"); await pg.evaluate("()=>MG.run.menuGo('sketch')"); await pg.wait_for_timeout(200)
        r=await pg.evaluate("()=>document.querySelectorAll('#mgUI .dwOv.on [data-p]').length")
        await pg.evaluate("()=>{ MG.run.pick(1); MG.run.demo(3); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUTD+"sketch.png")
        await pg.evaluate("()=>MG.run.sketchDone()"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>document.querySelector('#mgUI .dwOv [data-a=menu]').click()"); await pg.evaluate("()=>MG.run.menuGo('gal')"); await pg.wait_for_timeout(300)
        r2=await pg.evaluate("()=>[(store('hyeng_proto_dwg')||[]).length, document.querySelectorAll('#mgUI .dwGal figure img').length, (store('hyeng_proto_dwr')||{}).drawn]")
        ok(r==3 and r2==[1,1,1], f"③ 그려 보기: 3단어 중 고름 → 그림 → 그림첩 1장 {r} {r2}")
        await pg.screenshot(path=OUTD+"gallery.png")
        ok(not errs, f"오류 0 {errs[:5]}")
        await ctx.close()

        # ④ 같이 3명
        cA,A_,eA=await boot(br,"루아","CO635A", isle=False); cB,B_,eB=await boot(br,"민수","CO635B", isle=False); cC,C_,eC=await boot(br,"지우","CO635C", isle=False)
        P3=[A_,B_,C_]
        for x in P3: await menu(x)
        async def steps(n=6, dt=.1):
            for _ in range(n):
                for x in P3: await x.evaluate("async (dt)=>{ MG.step(dt,false); await null; await null; }", dt)
                await A_.wait_for_timeout(60)
        await A_.evaluate("()=>MG.run.menuGo('co')"); await steps(3)
        await A_.evaluate("()=>MG.run.RM.make()"); await steps(4)
        # 혼자면 시작 안 됨
        await A_.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(3)
        r=await A_.evaluate("()=>[MG.run.RM.phase, !!(MG.run.RM.d.h.st)]")
        ok(r==["wait",False], f"④ 혼자면 시작 안 됨 (친구 1명 더) {r}")
        for x in (B_, C_):
            await x.evaluate("()=>MG.run.menuGo('co')")
            for _ in range(15):
                await x.evaluate("()=>MG.run.RM.list()"); await steps(2)
                if await x.evaluate("()=>document.querySelectorAll('#mgUI [data-j]').length"): break
            await x.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await steps(4)
        r=[await x.evaluate("()=>[MG.run.RM.phase, document.querySelectorAll('#mgUI .mgRoomP .pl span').length]") for x in P3]
        ok(all(q==["wait",3] for q in r), f"④ 셋이 같은 방 {r}")
        await A_.screenshot(path=OUTD+"co_room.png")
        for x in P3: await x.evaluate("()=>{ MG.run.fast=true; }")
        await A_.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(4)
        for x in P3: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+7000; }")
        for _ in range(30):
            await steps(3)
            r=[await x.evaluate("()=>[MG.run.mode, MG.run.G.ph, MG.run.G.rd, MG.run.G.dr, (MG.run.G.ro||[]).join(',')]") for x in P3]
            if all(q[0]=="co-play" and q[1]=="pick" for q in r): break
        ok(all(q[0]=="co-play" and q[1]=="pick" and q[2]==1 for q in r) and len(set(q[3] for q in r))==1 and len(set(q[4] for q in r))==1, f"④ 모두 같은 판 · 1판 고르기 · 같은 그리는 사람 {r}")
        codes={"CO635A":A_,"CO635B":B_,"CO635C":C_}
        rounds=[]; wrongSent=False; nearSeen=False; popSeen=False; ovOk=True
        for rd in range(1,8):
            st=await A_.evaluate("()=>[MG.run.G.ph, MG.run.G.rd, MG.run.G.dr, MG.run.G.nr]")
            if st[0]=="end": break
            D=codes[st[2]]; others=[x for k,x in codes.items() if k!=st[2]]
            # 고르는 화면: 그리는 사람만 3단어
            r=[await x.evaluate("()=>document.querySelectorAll('#mgUI .dwOv.on [data-p]').length") for x in [D]+others]
            ovOk = ovOk and r==[3,0,0]
            if rd==1: await D.screenshot(path=OUTD+"co_pick.png")
            await D.evaluate("()=>document.querySelector('#mgUI .dwOv.on [data-p]').click()"); await steps(5)
            for _ in range(20):
                if all([await x.evaluate("()=>MG.run.G.ph==='draw'") for x in P3]): break
                await steps(2)
            await D.evaluate("()=>MG.run.demo(3)"); await steps(6)
            w=await D.evaluate("()=>MG.run.ans()")
            sig=[await x.evaluate("()=>[MG.run.sig.split(',').filter(Boolean).length, MG.run.wl, document.querySelectorAll('#mgUI .dwBx i').length, getComputedStyle(document.querySelector('#mgUI .dwKb')).display]") for x in others]
            dTools=await D.evaluate("()=>[getComputedStyle(document.querySelector('#mgUI .dwTl')).display, MG.run.MY.length]")
            if rd==1:
                await others[0].screenshot(path=OUTD+"co_guess.png"); await D.screenshot(path=OUTD+"co_draw.png")
            # 첫 친구: 틀린 말 → ❌ (서버에 글자 안 감) · 거의 → 🔥
            await others[0].evaluate("()=>{ MG.run.typeWord('zzqzzqzzqzzq'.slice(0, MG.run.wl)); MG.run.submit(); }"); await steps(4)
            nw=w[:-1]+('y' if w[-1]=='z' else 'z')
            await others[0].evaluate("(s)=>{ MG.run.typeWord(s); MG.run.submit(); }", nw); await steps(3)
            nearSeen = nearSeen or ("거의" in await others[0].evaluate("()=>MG.run.fb"))
            popSeen = popSeen or await D.evaluate("()=>document.querySelectorAll('#mgUI .dwPl em').length>0") or await others[1].evaluate("()=>document.querySelectorAll('#mgUI .dwPl em').length>0")
            dbs=json.dumps(fakefb.DB, ensure_ascii=False)
            wrongSent = wrongSent or ('zzqzz' in dbs) or (nw in dbs.replace(w, ''))
            for x in others: await x.evaluate("(s)=>{ MG.run.typeWord(s); MG.run.submit(); }", w)
            await steps(6)
            sc=await A_.evaluate("(rd)=>MG.run.G.rd===rd?JSON.stringify(MG.run.G.ok):'{}'", rd)
            if rd==1: await others[0].screenshot(path=OUTD+"co_ok.png")
            for _ in range(30):
                ph=[await x.evaluate("()=>[MG.run.G.ph, MG.run.G.rd, JSON.stringify(MG.run.G.ok)]") for x in P3]
                if ph[0][1]==rd and len(json.loads(ph[0][2]))>len(json.loads(sc)): sc=ph[0][2]
                if all(q[0]=="show" or q[1]>rd or q[0]=="end" for q in ph): break
                await steps(2)
            if rd==1: await steps(1); await B_.screenshot(path=OUTD+"co_show.png")
            rounds.append((rd, st[2][-1], w, sig, dTools, sc))
            for _ in range(30):
                ph=[await x.evaluate("()=>[MG.run.G.ph, MG.run.G.rd]") for x in P3]
                if all(q[1]>rd or q[0]=="end" for q in ph): break
                await steps(2)
        print(rounds)
        hist=None
        for _ in range(20):
            hist=await A_.evaluate("()=>MG.run.G.hist||null")
            if hist and len(hist)>=6: break
            await steps(2)
        ok(ovOk, "④ 고를 때: 그리는 사람만 3단어 · 친구는 「고르는 중…」")
        ok(all(x[3][0][0]>=3 and x[3][1][0]>=3 and x[3][0][1]==len(x[2]) and x[3][0][2]==len(x[2]) and x[3][0][3]=="flex" and x[4][0]=="flex" for x in rounds), f"④ 그린 줄이 친구 화면에 · 친구는 글자 칸(길이)+자판 · 그리는 사람은 도구 {[ (x[0],x[3],x[4]) for x in rounds][:3]}")
        ok(len(rounds)==6 and sorted(x[1] for x in rounds)==sorted("ABCABC") and hist==[2]*6, f"④ 6판 · 셋이 두 번씩 그림 · 판마다 둘 다 맞힘 {[(x[0],x[1],x[2]) for x in rounds]} {hist}")
        ok(not wrongSent and nearSeen and popSeen, f"④ 틀린 글자는 서버에 안 감 · 거의 🔥 · 친구 이름표에 ❌/🔥 표시 {[wrongSent, nearSeen, popSeen]}")
        await steps(20)
        r=[await x.evaluate("()=>{ const el=document.querySelector('#mgUI .puR'); return [MG.run.G.ph, !!el, el?[...el.querySelectorAll('.puRank div')].map(t=>t.textContent).join('|'):'']; }") for x in P3]
        ok(all(q[0]=="end" and q[1] for q in r) and len(set(q[2] for q in r))==1, f"④ 끝 · 세 화면 같은 순위·점수 {r}")
        await C_.screenshot(path=OUTD+"co_end.png")
        r=[await x.evaluate("()=>[(MG.rec().t.draw||{}).co, (store('hyeng_proto_dwg')||[]).length]") for x in P3]
        ok(all(q==[1,2] for q in r), f"④ 같이 한 판 기록 · 내가 그린 그림 2장 그림첩에 {r}")
        ok(not (eA+eB+eC), f"오류 0 (같이) {(eA+eB+eC)[:5]}")
        for c_ in (cA,cB,cC): await c_.close()
        # ⑤ 사진 패드 · 가로
        for nm,vp in [("pad",{"width":820,"height":1180}),("land",{"width":844,"height":390})]:
            ctx,pg,errs=await boot(br,"루아","DW635"+nm, vp=vp, isle=False); await menu(pg); await pg.screenshot(path=OUTD+nm+"_menu.png")
            await pg.evaluate("()=>MG.run.menuGo('solo')"); await pg.evaluate(STEP, 80)
            await pg.evaluate("()=>{ MG.run.typeWord(MG.run.ans().slice(0,2)); }"); await pg.wait_for_timeout(800); await pg.screenshot(path=OUTD+nm+"_solo.png")
            r=await pg.evaluate("()=>{ const b=document.querySelector('#mgUI .dwBd').getBoundingClientRect(), k=document.querySelector('#mgUI .dwKb').getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height), Math.round(b.bottom), Math.round(k.top), Math.round(k.bottom), innerHeight, document.documentElement.scrollWidth<=innerWidth]; }")
            ok(r[0]>200 and (r[2]<=r[3]+2 or nm=="land") and r[4]<=r[5] and r[6], f"⑤ {nm}: 그림판 · 자판 화면 안 · 안 겹침 {r}")
            await pg.evaluate("()=>{ MG.run.menuShow(); MG.run.menuGo('sketch'); MG.run.pick(0); MG.run.demo(2); }"); await pg.wait_for_timeout(500); await pg.screenshot(path=OUTD+nm+"_sketch.png")
            await ctx.close()
            ok(not errs, f"오류 0 ({nm}) {errs[:3]}")
        await br.close()
    print("BAD:", len(bad)); sys.exit(1 if bad else 0)
if __name__=="__main__": asyncio.run(main())
