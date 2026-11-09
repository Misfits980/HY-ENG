"""(v633) 🃏 컬러팡 — 놀이 섬 카드 카페
   ① 놀이 섬 가운데 카드 카페 건물 · 이름표 · 부딪힘 · 누르면 안내 창(봇 실력 · 오늘 🪙)
   ② 들어가면 3D 탁자 · 봇 3명(아바타) · 7장씩 · 첫 카드는 숫자 · 탁자 테두리 = 지금 색
   ③ 규칙: 못 내는 카드 누르면 흔들림 · 낼 수 있는 카드만 빛남 · 뽑기 → 넘기기 · 🌈 색 고르기 · +2/+4 → 다음 사람 받음 · 한 장! 깜빡 → +2
   ④ 자동 선수(나도 봇처럼)로 여러 판 끝까지: 멈춤 0 · 카드 수 맞음(108장) · 결과 창 · 🪙 · 기록(이긴 판 · 연승)
   ⑤ 폰 세로 · 패드 세로 · 폰 가로 사진 + 날아가는 카드 GIF (사람이 보는 용)"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
OUTD=OUT+"card633/"; os.makedirs(OUTD, exist_ok=True)

async def boot_isle(pg, code):
    await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
    await pg.evaluate("(c)=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_v5','1'); }", code)
    await pg.reload(); await pg.wait_for_timeout(2600)
    await pg.evaluate("()=>HOUSE.exitRoom()")
    for _ in range(160):
        if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
        await pg.wait_for_timeout(250)
    await pg.wait_for_timeout(800)

async def enter(pg, df="normal"):
    await pg.evaluate("(d)=>MG.enter('card',{df:d})", df)
    for _ in range(80):
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
        await pg.wait_for_timeout(200)

# 시험 화면은 느림 → MG.step 으로 시간 넘김 (await 로 약속 이어 가기)
STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } return MG.run && MG.run.G.over; }"""
CHECK = """()=>{ const R=MG.run, G=R.G; const n=G.P.reduce((s,p)=>s+p.h.length,0)+G.draw.length+G.pile.length;
  const ids=new Set(); G.P.forEach(p=>p.h.forEach(k=>ids.add(k.id))); G.draw.forEach(k=>ids.add(k.id)); G.pile.forEach(k=>ids.add(k.id));
  return {total:n, uniq:ids.size, over:G.over, turn:G.turn, hands:G.P.map(p=>p.h.length), hist:G.hist.length, st:G.st}; }"""

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: (m.type in ("error","warning")) and ("CP" in m.text or "MG" in m.text) and errs.append(m.text[:240]))
        await boot_isle(pg, "CP633")
        # ① 카드 카페
        r=await pg.evaluate("""()=>{ const C=MG.SPOT.card, L=LBL.filter(l=>/^mg_/.test(l.d.k)).map(l=>l.d.k).sort().join(",");
            return [!!C, L, C?ISLE.blocked(Math.floor(C[0]),Math.floor(C[2])):null, !!MG.GM.card]; }""")
        ok(r[0] and "mg_card" in r[1] and r[2] and r[3], f"① 놀이 섬 가운데 카드 카페 · 이름표 · 부딪힘 {r}")
        await pg.evaluate("()=>{ const g=MG.SPOT.card; HOUSE.setWx(false); TFAC.warp(g[0]-9, g[2]+2); ISLE.CAM.zoom=2.4; ISLE.CAM.pitch=.8; yaw=yawTo=-Math.PI*.5; ISLE.CAM.dragAt=performance.now()+1e6; }")
        await pg.wait_for_timeout(2600); await pg.screenshot(path=OUTD+"cafe.png")
        await pg.evaluate("()=>MG.lobby('card')"); await pg.wait_for_timeout(500)
        r=await pg.evaluate("()=>{ const b=document.querySelector('#mgLob.on .bx'); return b? [b.innerText.includes('컬러팡'), b.querySelectorAll('[data-o=df]').length, /3판/.test(b.innerText)] : null; }")
        ok(r==[True,2,True], f"① 안내 창 (봇 실력 2 · 오늘 🪙 3판) {r}")
        await pg.screenshot(path=OUTD+"lobby.png")
        await pg.evaluate("()=>document.querySelector('#mgLob .go').click()")
        for _ in range(80):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        # ② 시작
        r=await pg.evaluate(CHECK)
        ok(r["total"]==108 and r["uniq"]==108 and r["hands"]==[7,7,7,7], f"② 108장 · 7장씩 {r['total']} {r['uniq']} {r['hands']}")
        r=await pg.evaluate("()=>{ const G=MG.run.G; return [typeof G.top.v, G.cur===G.top.c, MG.run.SEATS.filter(s=>s&&s.P).length, document.querySelectorAll('#cpHud .cpC').length, MG.run.SEATS[1].hand.children.length]; }")
        ok(r==["number",True,3,7,14], f"② 첫 카드 숫자 · 지금 색 · 봇 아바타 3 · 내 패 7 · 봇 손 카드 {r}")
        # 내 차례가 올 때까지
        for _ in range(60):
            if await pg.evaluate("()=>MG.run.G.myTurn && !MG.run.G.busy"): break
            await pg.evaluate(STEP, 6)
        await pg.wait_for_timeout(1200); await pg.screenshot(path=OUTD+"phone_turn.png")
        # ③ 못 내는 카드 → 흔들림
        r=await pg.evaluate("""()=>{ const R=MG.run, G=R.G, me=G.P[0]; const bad=me.h.find(k=>!R.okCard(k,G.top,G.cur)); const good=me.h.filter(k=>R.okCard(k,G.top,G.cur));
            const okEl=[...document.querySelectorAll('#cpHud .cpC.ok')].length, noEl=[...document.querySelectorAll('#cpHud .cpC.no')].length;
            let shook=null; if(bad){ const el=document.querySelector('#cpHud .cpC[data-id="'+bad.id+'"]'); R.tapCard(bad.id, el); shook=el.classList.contains('shk') && G.myTurn && me.h.length===7; }
            return [okEl===good.length, noEl===me.h.length-good.length, shook]; }""")
        ok(r[0] and r[1] and r[2] in (True,None), f"③ 빛나는 카드 = 낼 수 있는 카드 · 못 내는 카드 누르면 흔들림 {r}")
        # 🌈 색 고르기: 손에 무지개를 넣고 누름
        for _ in range(80):
            if await pg.evaluate("()=>MG.run.G.myTurn && !MG.run.G.busy"): break
            await pg.evaluate(STEP, 4)
        r=await pg.evaluate("""async ()=>{ const R=MG.run, G=R.G, me=G.P[0]; if(!(G.myTurn && !G.busy)) return ['not my turn', G.turn, G.busy, G.over]; const w=G.draw.findIndex(k=>k.v==='wild'); const k=G.draw.splice(w,1)[0]; me.h.push(k); R.drawHand();
            R.tapCard(k.id, null); await null; const P=document.querySelector('#cpHud .cpPick'); return [P.classList.contains('on'), P.querySelectorAll('path[data-c]').length, k.id]; }""")
        ok(r[0] and r[1]==4, f"③ 무지개 → 색 고르기 원판 (4색) {r}")
        await pg.wait_for_timeout(300); await pg.screenshot(path=OUTD+"phone_pick.png")
        wid=r[2]
        r=await pg.evaluate("""async (wid)=>{ const R=MG.run, G=R.G; const nxt=(G.turn+G.dir+4)%4; document.querySelector('#cpHud .cpPick .lb[data-c="g"]').click();
            for(let i=0;i<40;i++){ MG.step(.05,false); await null; await null; } return [G.cur, G.top.id===wid, G.top.v]; }""", wid)
        ok(r[0]=="g" and r[1], f"③ 초록 고르면 탁자 색 = 초록 {r}")
        # 뽑기 → 넘기기
        for _ in range(80):
            if await pg.evaluate("()=>MG.run.G.myTurn && !MG.run.G.busy || MG.run.G.over"): break
            await pg.evaluate(STEP, 6)
        r=await pg.evaluate("""async ()=>{ const R=MG.run, G=R.G, me=G.P[0]; if(G.over) return 'over'; const n0=me.h.length; await R.myDraw(); for(let i=0;i<30;i++){ MG.step(.05,false); await null; await null; }
            return [me.h.length===n0+1, G.drew || !G.myTurn]; }""")
        ok(r=='over' or r==[True,True], f"③ 뽑기 → 1장 · 그다음 넘기기(또는 자동 넘김) {r}")
        # +2 받기: 다음 사람에게 +2 를 내게 만듦
        r=await pg.evaluate("""async ()=>{ const R=MG.run, G=R.G; for(let t=0;t<200 && !(G.myTurn && !G.busy) && !G.over;t++){ MG.step(.05,false); await null; await null; }
            if(G.over) return 'over'; const me=G.P[0]; const i=G.draw.findIndex(k=>k.v==='d2'); const k=G.draw.splice(i,1)[0]; k.c=G.cur; me.h.push(k); R.drawHand();
            const t=(0+G.dir+4)%4, n0=G.P[t].h.length; R.tapCard(k.id,null); for(let j=0;j<60;j++){ MG.step(.05,false); await null; await null; } return [G.P[t].h.length-n0, G.turn!==t]; }""")
        ok(r=='over' or (r[0]>=2), f"③ +2 → 다음 사람 2장 받고 쉼 {r}")
        # 한 장! 깜빡 → +2
        r=await pg.evaluate("""async ()=>{ const R=MG.run, G=R.G; for(let t=0;t<300 && !(G.myTurn && !G.busy) && !G.over;t++){ MG.step(.05,false); await null; await null; }
            if(G.over) return 'over'; const me=G.P[0]; const top=G.top; me.h=[{c:G.cur,v:'skip',id:900},{c:'y',v:3,id:901}]; me.called=false; R.drawHand(); R.cmd();
            const glow=document.querySelector('#cpHud .cpCmd [data-c=one]').classList.contains('glow');
            R.tapCard(900,null); for(let j=0;j<120;j++){ MG.step(.05,false); await null; await null; } return [glow, me.h.length]; }""")
        ok(r=='over' or (r[0] and r[1]==3), f"③ 2장일 때 「한 장!」 반짝 · 안 누르고 내면 +2 → 3장 {r}")
        await pg.evaluate("()=>{ MG.exit(); }"); await pg.wait_for_timeout(800)
        # ④ 자동 선수로 여러 판
        res=[]
        for gi in range(6):
            await enter(pg, "easy" if gi%2 else "normal")
            await pg.evaluate("()=>{ MG.run.auto=true; MG.run.fast=true; }")
            stuck=0; last=None
            for _ in range(400):
                over=await pg.evaluate(STEP, 10)
                if over: break
                s=await pg.evaluate("()=>JSON.stringify([MG.run.G.turn, MG.run.G.P.map(p=>p.h.length), MG.run.G.pile.length])")
                stuck = stuck+1 if s==last else 0; last=s
                if stuck>30: break
            c=await pg.evaluate(CHECK)
            await pg.evaluate(STEP, 60)
            endOn=await pg.evaluate("()=>{ const e=document.querySelector('#cpHud .cpEnd'); return !!e && e.classList.contains('on'); }")
            res.append((c["over"], c["total"], c["uniq"], c["hist"], endOn, stuck))
            if gi==0:
                await pg.evaluate("()=>{ MG.run.fast=false; }"); await pg.wait_for_timeout(1500); await pg.screenshot(path=OUTD+"phone_end.png")
            await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(700)
        ok(all(r[0] and r[1]==108 and r[2]==108 and r[4] and r[5]<=30 for r in res), f"④ 자동 선수 6판 끝까지 · 카드 108장 그대로 · 결과 창 {res}")
        r=await pg.evaluate("()=>{ const r=MG.rec(); return [r.t.card&&r.t.card.play, r.b.card && r.b.card.bs!=null, (r.n||{}).card]; }")
        ok(r[0]>=6 and r[1], f"④ 기록 (판 수 · 연승) {r}")
        ok(not errs, f"오류 0 {errs[:5]}")
        await ctx.close()
        # ⑤ 패드 · 폰 가로 사진
        for nm,vp in [("pad",{"width":820,"height":1180}),("land",{"width":844,"height":390})]:
            ctx=await br.new_context(viewport=vp, device_scale_factor=2 if nm=="pad" else 2, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await boot_isle(pg, "CP633"+nm)
            await enter(pg)
            for _ in range(80):
                if await pg.evaluate("()=>MG.run.G.myTurn && !MG.run.G.busy"): break
                await pg.evaluate(STEP, 6)
            await pg.wait_for_timeout(1500); await pg.screenshot(path=OUTD+nm+"_turn.png")
            await ctx.close()
        ok(not errs, f"오류 0 (패드·가로) {errs[:5]}")
        await br.close()
    print("BAD:", len(bad)); sys.exit(1 if bad else 0)
if __name__=="__main__": asyncio.run(main())
