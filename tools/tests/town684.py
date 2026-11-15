"""(v684) My Town 버그 찾기 — 사용자: 「마이타운 버그 한번 찾아봐 이참에」 + 「크롬으로도 확인하고」
   ① 🪙 새 이모지 → 그림: 학원 PC(Windows 10 크롬)는 🪙·🪱·🪜 를 ⊠ 로 그림 (크롬에서 은행·가게·놀이 공원 값이 다 ⊠) → emoji-dom.js
      (못 그리는 기기 흉내 = ?emjfix=1) 글자는 남기고(textContent 그대로) 그림을 깖 · 그림 파일이 다 있음 · 게임 첫 화면도
   ② 안내 화살표: 멀리 앞에 있는 곳(카메라 far 밖)이 반대쪽에 그려지던 것 — 「🎣 호수」가 앞인데 왼쪽 아래
   ③ 이름 없는 아이: 「알겠어요」 하나뿐이라 방에서 못 나감 → 「이름 정하기」 → 게임 이름 창(#townname) → 정하면 바로 마을로
   ④ GPU 도형 쌓임: 같은 가게를 드나들 때마다 · 컬러팡 한 판마다 · 표정 바뀔 때마다 늘던 것
   ⑤ 휴대폰 세로: Mia 안내 말풍선이 💬 말하기 단추를 덮던 것"""
import asyncio, sys, os, re, json, math
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
    # ① 그림 파일 — emoji-dom.js 목록마다 assets/emoji/<코드>.svg
    src=open(os.path.join(SITE,"emoji-dom.js"),encoding="utf-8").read(); codes=re.search(r'const CODES = "([^"]+)"', src).group(1).split()
    miss=[c for c in codes if not os.path.isfile(os.path.join(SITE,"assets","emoji",c+".svg"))]
    ok(len(codes)>=75 and not miss and {"1fa99","1fab1","1fa9c"}<=set(codes), f"① 그림 {len(codes)}개 다 있음 (🪙 1fa99 · 🪱 · 🪜) 없음 {miss}")
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def kid(code, name, q="?isle=1", tut=99, vw=(390,844), init=None):
            ctx=await br.new_context(viewport={"width":vw[0],"height":vw[1]}, is_mobile=vw[0]<500, has_touch=True)
            if init: await ctx.add_init_script(init)
            pg=await ctx.new_page(); pg.set_default_timeout(150000); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)[:200]))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"+q); await pg.wait_for_timeout(400)
            await pg.evaluate("""([c,n,t])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); if(n) localStorage.setItem('hyeng_nick', n); if(t!==null) localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:t}));
                localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:4,tot:6,hs:4,hb:4,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); }""", [code,name,tut])
            await pg.reload(); await pg.wait_for_timeout(2000); return pg
        async def until(pg, js, n=200):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        ISLE_OK="()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"
        # ── ① 못 그리는 기기 흉내 (?emjfix=1)
        A=await kid("QA684","루아", q="?isle=1&emjfix=1")
        await A.evaluate("()=>ISLE.enter()"); ok(await until(A, ISLE_OK), "섬")
        await A.wait_for_timeout(800)
        r=await A.evaluate("""async ()=>{ const R=document.getElementById('ihRes'), sp=[...R.querySelectorAll('.emjF')], bg=sp.map(s=>s.style.backgroundImage);
            const coin=bg.find(b=>/1fa99/.test(b)); let st=0; if(coin){ try{ st=(await fetch(coin.replace(/^url\\("?|"?\\)$/g,''))).status; }catch(e){} }
            return {n:EMOJI_DOM.n, sp:sp.length, txt:R.textContent.includes('🪙') && R.textContent.includes('🪱'), coin:!!coin, st, w:sp[0] ? Math.round(sp[0].getBoundingClientRect().width) : 0, col:sp[0] ? getComputedStyle(sp[0]).color : ''}; }""")
        ok(r["n"]>=60 and r["sp"]>=2 and r["txt"] and r["coin"] and r["st"]==200 and r["w"]>=10 and "0, 0, 0, 0" in r["col"], f"① 섬 💎🪙🪱 칸: 🪙·🪱 = 그림 · 글자는 그대로(투명) · 그림 파일 받아짐 {r}")
        await A.evaluate("()=>TECO.openBank()"); await A.wait_for_timeout(500)
        r=await A.evaluate("()=>{ const B=document.getElementById('teBank'); return [B.querySelectorAll('.emjF').length, (B.textContent.match(/🪙/g)||[]).length]; }")
        ok(r[0]>=4 and r[0]==r[1], f"① 은행: 🪙 마다 그림 {r}")
        await A.evaluate("()=>{ document.getElementById('teBank').classList.remove('on'); const d=document.createElement('div'); d.id='__t'; d.textContent='🪙 5 · 🪜 2층'; document.body.appendChild(d); }"); await A.wait_for_timeout(100)
        r=await A.evaluate("()=>{ const d=document.getElementById('__t'); const a=[d.querySelectorAll('.emjF').length, d.textContent]; d.firstChild && (d.textContent='🪱 9'); return new Promise(res=>setTimeout(()=>res(a.concat([d.querySelectorAll('.emjF').length, d.textContent])), 60)); }")
        ok(r[0]==2 and r[1]=="🪙 5 · 🪜 2층" and r[2]==1 and r[3]=="🪱 9", f"① 새로 생긴 글·바뀐 글도 바로 그림 (textContent 같음) {r}")
        # ── ④ GPU 도형: 같은 가게 · 컬러팡 · 표정
        MEM="()=>renderer.info.memory.geometries"
        g=[]
        for i in range(3):
            await A.evaluate("()=>{ const S=ISLE.SPOT.shops[0]; SHOPIN.enter(S); }"); await until(A, "()=>SHOPIN.is() && !HOUSE.trip().busy")
            await A.wait_for_timeout(500); await A.evaluate("()=>{ try{ SHOPUI.close(); }catch(e){} SHOPIN.exit(); }"); await until(A, ISLE_OK); await A.wait_for_timeout(700); g.append(await A.evaluate(MEM))
        ok(g[2]-g[0]<=1, f"④ 같은 가게 3번 드나들기: 도형 수 그대로 {g}")
        g=[]
        for i in range(3):
            await A.evaluate("()=>MG.enter('card', {quick:1, mode:'solo'})"); await until(A, "()=>MG.on", 60); await A.wait_for_timeout(2500)
            await A.evaluate("()=>MG.exit()"); await until(A, "()=>!MG.on", 60); await A.wait_for_timeout(900); g.append(await A.evaluate(MEM))
        ok(g[2]-g[0]<=8, f"④ 🃏 컬러팡 3판 들어갔다 나오기: 도형 수 그대로 {g}")
        r=await A.evaluate("()=>{ const P=buildAvatar({}); scene.add(P.g); renderer.render(scene, camera); const a=renderer.info.memory.geometries; for(let i=0;i<6;i++){ P.setExpr(i%2?'grin':'smile'); renderer.render(scene, camera); } const b=renderer.info.memory.geometries; scene.remove(P.g); return [a,b]; }")
        ok(r[1]-r[0]<=0, f"④ 표정 「grin」 6번 바꿔도 도형 안 늘어남 {r}")
        await A.context.close()
        # ── ⑤ 휴대폰 세로: 첫 시작 Mia 안내 말풍선 · 💬 말하기
        B=await kid("QB684","하늘", tut=None)
        ok(await until(B, ISLE_OK+" && document.getElementById('coach').classList.contains('on')"), "⑤ 새 아이 = 섬 광장 + Mia 안내")
        await B.wait_for_timeout(900)   # 말풍선이 올라오는 움직임(.3초)이 끝난 뒤
        r=await B.evaluate("""()=>{ const c=document.getElementById('ihChat').getBoundingClientRect(), m=document.getElementById('coach').getBoundingClientRect(); const e=document.elementFromPoint(c.x+c.width/2, c.y+c.height/2);
            return {hit: !!e && (e.id==='ihChat' || !!e.closest('#ihChat')), over: !(m.left>=c.right || m.right<=c.left || m.top>=c.bottom || m.bottom<=c.top), coach:[Math.round(m.left), Math.round(m.right)], vw:innerWidth}; }""")
        ok(r["hit"] and not r["over"] and r["coach"][1]<=r["vw"], f"⑤ 말풍선이 💬 말하기를 안 덮음 {r}")
        # ── ② 안내 화살표 (🎣 호수 = 섬 동쪽 끝 · 멀리) — 카메라를 네 방향으로 돌려 봄
        await B.evaluate("()=>{ tutAdv(7); }"); await B.wait_for_timeout(300)
        res=[]
        for k in range(8):
            r=await B.evaluate("""(k)=>{ yaw=yawTo=k*Math.PI/4; ISLE.CAM.dragAt=performance.now()+1e6; return new Promise(res=>setTimeout(()=>{
                const L=LBL.find(l=>l.el.classList.contains('hot') && l.d.k==='lake'); if(!L) return res(null);
                const v=new THREE.Vector3(L.d.p[0],L.d.p[1],L.d.p[2]), cv=v.clone().applyMatrix4(camera.matrixWorldInverse), b=L.el.getBoundingClientRect();
                const dx=b.left+b.width/2-innerWidth/2, dy=b.top+b.height/2-VH()/2, ex=cv.x, ey=-cv.y;   /* 화면에서 가야 할 쪽 = 카메라 공간 (x, -y) */
                res({edge:L.el.classList.contains('edge'), front:cv.z<0, far:-cv.z>camera.far, dot:Math.round((dx*ex+dy*ey)/Math.max(1,Math.hypot(dx,dy))/Math.max(1e-6,Math.hypot(ex,ey))*100)/100}); }, 450)); }""", k)
            res.append(r)
        good=[x for x in res if x]
        ok(len(good)>=6 and all(x["dot"]>0 for x in good if x["edge"]) and any(x["edge"] and x["front"] and x["far"] for x in good), f"② 화면 밖 「🎣 호수」 화살표가 늘 그쪽을 가리킴 (앞쪽 먼 곳 포함) {good}")
        await B.context.close()
        # ── ③ 이름 없는 아이 → 이름 정하기 → 마을로 (게임 이름 창은 HY_TOWN_NAME 으로 켬)
        C=await kid("QC684","", tut=99, init="window.HY_TOWN_NAME=true;")
        r=await C.evaluate("()=>ISLE.enter()")
        await C.wait_for_timeout(300)
        r2=await C.evaluate("()=>[document.getElementById('ask').classList.contains('on'), document.getElementById('askT').innerText.replace(/\\s+/g,' ')]")
        ok(r=="gate" and r2[0] and "이름" in r2[1] and "정할까요" in r2[1], f"③ 이름 없으면 「이름 정할까요?」 (네/아니요) {r} {r2}")
        await C.click("#askOk")
        ok(await until(C, "()=>/index\\.html$/.test(location.pathname)", 60), "③ 「네!」 → 게임으로")
        ok(await until(C, "()=>!!document.getElementById('twNm')", 40), "③ 게임에서 바로 이름 창 (#townname)")
        await C.fill("#twNm", "PLAYER"); await C.evaluate("()=>document.querySelector('#townMt [data-ok]').click()"); await C.wait_for_timeout(300)
        r=await C.evaluate("()=>[!!document.getElementById('townMt'), document.getElementById('twNmMsg').textContent, location.pathname]")
        ok(r[0] and "다른 이름" in r[1] and r[2].endswith("index.html"), f"③ 「PLAYER」 는 안 됨 {r}")
        await C.fill("#twNm", "서윤"); await C.evaluate("()=>document.querySelector('#townMt [data-ok]').click()")
        ok(await until(C, "()=>/proto\\/house\\.html$/.test(location.pathname)", 60), "③ 정하면 바로 마을로")
        await C.wait_for_timeout(1500)
        r=await C.evaluate("()=>[localStorage.getItem('hyeng_nick'), ISLE.nameOk()]")
        ok(r==["서윤", True], f"③ 이름 = 서윤 · 이제 마을에 들어감 {r}")
        await C.context.close()
        # ── 게임 첫 화면 (emoji-dom 이 index.html 에도) — 못 그리는 기기 흉내
        D=await br.new_page(viewport={"width":390,"height":844}); D.on("pageerror", lambda e: errs.append("index: "+str(e)[:200]))
        await D.route("**/*", route); await D.goto(ORIGIN+"index.html"); await D.evaluate("()=>localStorage.setItem('hyeng_emjfix','1')"); await D.reload(); await D.wait_for_timeout(1500)
        r=await D.evaluate("()=>{ const d=document.createElement('p'); d.textContent='미끼 🪱 +5'; document.body.appendChild(d); return new Promise(res=>setTimeout(()=>res([EMOJI_DOM.n, d.querySelectorAll('.emjF').length, d.textContent]), 50)); }")
        ok(r[0]>=60 and r[1]==1 and r[2]=="미끼 🪱 +5", f"① 게임 화면도 (못 그리는 기기) {r}")
        await D.evaluate("()=>localStorage.removeItem('hyeng_emjfix')"); await D.reload(); await D.wait_for_timeout(1200)
        r=await D.evaluate("()=>[typeof EMOJI_DOM, EMOJI_DOM.n, document.querySelectorAll('.emjF').length]")
        ok(r[0]=="object", f"① 잘 그리는 기기는 손대지 않음 (이 시험 기기 = {r[1]}개 못 그림) {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
