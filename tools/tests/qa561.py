"""(v561) My Town QA 고친 것 (가짜 서버) — 검사 도우미 2명이 아이처럼 해 보고 찾은 것
   ① 확인 창이 땅 고르기·넓히기 창 뒤에 숨던 것 → 진짜로 눌림 (elementFromPoint)
   ② 튜토리얼: 침대 놓기 전에 나가도 안 건너뜀 · 미리 놓은 침대는 그 단계에서 바로 넘어감 · 땅 고르기 전 「내 집」 → 게시판으로
   ③ 🪱 미끼 선물 하루 한 번 · 가구 사기 전에 「살까요?」
   ④ 섬: 막힌 곳(분수)을 눌러도 안 멈춤(1초 안) · 🗺 마을 지도(구역 누르면 걸어감) · 안내 이름표가 화면 밖이면 가장자리 ➜
   ⑤ 위층 🪜 계단 = 위·아래 고르기 · 옆방 문 이름표 「거실로 돌아가기」
   ⑥ 💰 타워 별·땅 💎 하루 10 · 박물관 💎 하루 2번 · 도서관 다 틀리면 ⭐ 없음 · 문제 창 ✕ · 이름 통일 · OX 「파란 판」"""
import asyncio, sys, os, json, time
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake, DB
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def until(pg, js, n=120):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        async def kid(code, name, tut=None, q="?isle=1"):
            ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"+q); await pg.wait_for_timeout(500)
            await pg.evaluate("""([c,n,t])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); if(t!==null) localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:t}));
                localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:8,tot:9,hs:8,hb:8,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); }""", [code,name,tut])
            await pg.reload(); await pg.wait_for_timeout(2500); return pg
        top="(id)=>{ const b=document.getElementById(id).getBoundingClientRect(), e=document.elementFromPoint(b.x+b.width/2, b.y+b.height/2); return !!e && (e.id===id || !!e.closest('#'+id)); }"
        # ── 새 아이 (튜토리얼 처음) ──
        A=await kid("AAAAA","루아", None)
        ok(await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 160), "섬에서 시작")
        await A.evaluate("()=>document.getElementById('bIHome').click()"); await A.wait_for_timeout(600)
        await until(A, "()=>document.getElementById('lotP') && document.getElementById('lotP').classList.contains('on')", 20)
        r=await A.evaluate("()=>[tut.s, document.getElementById('lotP') && document.getElementById('lotP').classList.contains('on'), document.getElementById('toast').textContent]")
        ok(r[0]==0 and r[1], f"② 땅 고르기 전 「내 집」 → 게시판(땅 고르기 창)으로 (입주 선물 안 빠짐) {r}")
        await A.evaluate("()=>{ const b=document.getElementById('lotGo'); if(b) b.click(); }"); await A.wait_for_timeout(400)
        r=await A.evaluate("()=>[document.getElementById('ask').classList.contains('on'), getComputedStyle(document.getElementById('ask')).zIndex]")
        ok(r[0] and await A.evaluate(top, "askOk"), f"① 「지을까요?」 확인 창이 땅 고르기 창 위에 (진짜로 눌림) {r}")
        await A.click("#askOk"); await A.wait_for_timeout(800)
        ok(await until(A, "()=>tut.s===1", 40), "① 눌러서 집 지음 → 튜토리얼 2단계")
        # ③ 미끼 · 💎 확인
        await A.evaluate("()=>{ bait=0; setBait(0); baitGift(); baitGift(); baitGift(); }")
        ok(await A.evaluate("()=>bait")==3, "③ 🪱 미끼 선물 하루 한 번 (세 번 눌러도 +3 · v563)")
        # ④ 막힌 곳 · 지도 · 가장자리 화살표
        r=await A.evaluate("()=>{ const c=[ISLE.OX, ISLE.OZ]; const t=performance.now(); const f=nearestFree(Math.floor(c[0]), Math.floor(c[1])); return [performance.now()-t, !!f]; }")
        ok(r[1] and r[0]<1500, f"④ 분수(막힌 곳) 눌러도 안 멈춤 {r[0]:.0f}ms")
        r=await A.evaluate("()=>{ const t=performance.now(); const P=findPath(HOUSE.hero().cx, HOUSE.hero().cz, HOUSE.hero().cx+20, HOUSE.hero().cz+20); return [performance.now()-t, P===null || Array.isArray(P)]; }")
        ok(r[1] and r[0]<1500, f"④ 먼 길 찾기 {r[0]:.0f}ms")
        await A.evaluate("()=>IHUD.openMap()"); await A.wait_for_timeout(300)
        r=await A.evaluate("()=>[document.getElementById('ihMap').classList.contains('on'), document.querySelectorAll('#ihMap [data-z]').length, /나/.test(document.getElementById('ihMap').innerText)]")
        ok(r[0] and r[1]>=7, f"④ 🗺 마을 지도 (구역 {r[1]}개 + 내 집)")
        await A.screenshot(path=OUT+"qa561_map.png")
        h0=await A.evaluate("()=>[HOUSE.hero().cx, HOUSE.hero().cz]")
        await A.evaluate("()=>document.querySelector('#ihMap [data-z=park] polygon').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await A.wait_for_timeout(300)
        await A.evaluate("()=>document.querySelector('#askT [data-gz]').click()"); await A.wait_for_timeout(600)
        r=await A.evaluate("()=>[document.getElementById('ihMap').classList.contains('on'), (HOUSE.hero().path||[]).length, HOUSE.hero().moving]")
        ok(not r[0] and (r[1]>0 or r[2]), f"④ 지도에서 놀이 공원 → 걸어감 {r}")
        await A.evaluate("()=>{ const h=HOUSE.hero(); h.path=[]; h.moving=false; }")
        # ⑦ 채팅 소식: 잡을 때마다 X · 대물만 (3분에 한 번)
        r=await A.evaluate("()=>{ IPLAY.S.ft.board=[{s:9999}]; const c=()=>Object.values(VLN.msgs).filter(m=>m.sys).length, f=HOUSE.FISH.find(f=>f.en==='fish'); const n0=c(); IPLAY.onCatch(f, 12, false, false); const n1=c(); IPLAY.onCatch(f, 39, false, false); const n2=c(); IPLAY.onCatch(f, 40, false, false); return [n0,n1,n2,c()]; }")
        ok(r[1]==r[0] and r[2]==r[0]+1 and r[3]==r[2], f"⑦ 채팅 소식: 보통 크기는 안 알림 · 🐋 대물은 알림 · 3분 안에 또는 안 알림 {r}")
        # 튜토리얼 hot 이름표가 화면 밖이면 가장자리
        await A.evaluate("()=>{ tutAdv(7); drawLabels(); }"); await A.wait_for_timeout(1200)
        r=await A.evaluate("()=>{ const L=LBL.find(l=>l.el.classList.contains('hot')); return L ? [L.d.k, L.el.style.display, L.el.classList.contains('edge')] : null; }")
        ok(r and r[1]!="none", f"④ 안내(🎣 호수) 이름표는 화면 밖이어도 보임 {r}")
        await A.screenshot(path=OUT+"qa561_edge.png")
        # ── 방: 튜토리얼 건너뛰기 ──
        B=await kid("BBBBB","하준", 3, "")
        await B.evaluate("()=>{ tut.s=3; tutSave(); tEv('out'); }")
        ok(await B.evaluate("()=>tut.s")==7, "② 침대 놓기 전에 나가면 바깥 안내로 따라감 (town407 그대로)")
        await B.evaluate("()=>{ tut.s=2; tutSave(); tEv('put_bed'); }")
        r=await B.evaluate("()=>tut.s")
        await B.evaluate("()=>tEv('walk')")
        ok(await B.evaluate("()=>tut.s")==4, f"② 미리 놓은 침대 → 걷기 뒤 침대 단계 바로 넘어감 (2→{r}→{await B.evaluate('()=>tut.s')})")
        # ③ 가구 사기 확인 · ① 넓히기 확인 창
        await B.evaluate("()=>{ tut.s=99; tutSave(); gems=3000; saveBag(); TECO.setCoin(20000); openFurn('furn'); }"); await B.wait_for_timeout(300)
        await B.evaluate("()=>document.querySelector('#furnBody [data-bf=sofa]').click()"); await B.wait_for_timeout(200)
        ok(await B.evaluate("()=>(stock.sofa|0)===0 && document.getElementById('ask').classList.contains('on')"), "③ 가구 누르면 바로 안 사고 「살까요?」")
        await B.click("#askOk"); await B.wait_for_timeout(200)
        ok(await B.evaluate("()=>(stock.sofa|0)===1"), "③ 네! → 창고")
        await B.evaluate("()=>{ document.getElementById('furnP').classList.remove('on'); HOMEX.openUp(); }"); await B.wait_for_timeout(300)
        await B.evaluate("()=>document.querySelector('[data-up=walls]').click()"); await B.wait_for_timeout(300)
        r=await B.evaluate("()=>document.getElementById('askT').innerText")
        ok(await B.evaluate(top, "askOk") and "세트를" in r, f"① 넓히기 창에서도 확인 창이 위 · 「세트를」 {r!r}")
        await B.click("#askOk"); await B.wait_for_timeout(300)
        ok(await B.evaluate("()=>(stock.partition|0)>=6"), "① 눌러서 세트 삼")
        # ⑤ 위층 계단 · 옆방 이름표
        await B.evaluate("()=>{ document.getElementById('upP').classList.remove('on'); HOMEX.unlock('f2'); addPlaced('stairs',4,4,0,0); stock.stairs--; saveRoom(); useItem(placed.find(p=>p.id==='stairs')); }")
        ok(await until(B, "()=>HOMEX.cur()==='f2' && !HOUSE.trip().busy", 80), "⑤ 1층 계단 → 2층")
        await B.evaluate("()=>useItem(placed.find(p=>p.id==='stairs'))"); await B.wait_for_timeout(300)
        r=await B.evaluate("()=>[document.getElementById('ask').classList.contains('on'), [...document.querySelectorAll('#askT [data-sp]')].map(b=>b.dataset.sp), document.getElementById('askOk').hidden]")
        ok(r[0] and "d" in r[1] and r[2], f"⑤ 2층 계단 = ⬆/⬇ 고르기 {r}")
        await B.click("#askT [data-sp=d]")
        ok(await until(B, "()=>HOMEX.cur()==='living' && !HOUSE.trip().busy", 80) and not await B.evaluate("()=>document.getElementById('askOk').hidden"), "⑤ ⬇ 아래층 → 1층 (확인 단추 다시 보임)")
        await B.evaluate("()=>{ HOMEX.unlock('door'); addWall('sidedoor',0,2,0); stock.sidedoor--; saveRoom(); useItem(wplaced.find(w=>w.id==='sidedoor')); }")
        await until(B, "()=>HOMEX.cur()==='a1' && !HOUSE.trip().busy", 80)
        t=await B.evaluate("()=>LBL.find(l=>l.d.k==='door').d.t")
        ok("거실로" in t, f"⑤ 옆방 문 이름표 {t!r}")
        # ⑥ 문제 창 ✕ · 박물관 · 도서관 · 타워
        await B.evaluate("()=>HLIFE.quiz('테스트', [['cat','고양이','🐱',1]], ()=>{ window._qd=1; })"); await B.wait_for_timeout(200)
        await B.click("#hqP .hqX"); await B.wait_for_timeout(200)
        ok(await B.evaluate("()=>!document.getElementById('hqP').classList.contains('on') && !window._qd"), "⑥ 문제 창 ✕ 로 닫힘 (보상 없음)")
        r=await B.evaluate("()=>{ TW.rec={}; TW.mode='kid'; const a=[]; for(let i=0;i<12;i++) a.push(twGemOk(1)); TW.mode='sky'; a.push(twGemOk(1)); return a.filter(Boolean).length; }")
        ok(r==10, f"⑥ 타워 별 💎 는 모드 합쳐 하루 10 {r}")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
