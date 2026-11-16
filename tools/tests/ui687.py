"""(v687) 사용자: 「그래 의견도 너가 잘 만져 봐」 + 「글자 배열이든지 위치가 안 맞는다든지 체크해 줘 그리고 고쳐」 + 「앱 전체 시스템 다」
   ① 글자 배열: 한글이 낱자 중간에서 줄이 바뀌지 않음 (「멀/면」 「봐/요」) — 마을 · 게임 둘 다 body keep-all · 채팅 말풍선도
   ② 가게 긴 이름(strawberry seeds)이 「strawberry …」로 잘리지 않음 (글자만 조금 작게)
   ③ 순위표 창이 위에서부터 (가운데 정렬로 위 칸이 비던 것)
   ④ 가방 씨앗 = 작물 그림 씨앗 봉투 (모두 🌰 이던 것)
   ⑤ 섬: 카메라 바로 앞 물건(벚나무 · 다리 기둥)은 점점이 비침 — 방 안 · 놀이 공원에선 꺼짐
   ⑥ 튜토리얼 「🎣 호수」: 멀면 Mia 가 첫 기차 공짜 (한 번만 · 코인 그대로)
   ⑦ 집에서 나오면 문 앞에서 길 쪽으로 두어 걸음 (반투명한 집이 캐릭터와 겹치지 않게)
   ⑧ 화면 밖 안내 화살표가 이름표 글자를 덮지 않음 (이름표 테두리 밖)"""
import asyncio, sys, os, json, math
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

BRK = r"""(sel)=>{ const root=document.querySelector(sel); if(!root) return ['noroot '+sel]; const R=document.createRange(), HG=/[가-힣]/, out=[];
  const tw=document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while(tw.nextNode()){ const n=tw.currentNode, t=n.data; if(!HG.test(t) || !n.parentElement || n.parentElement.closest('.emjF')) continue; R.selectNodeContents(n); if(R.getClientRects().length<2) continue;
    let pt=null; for(let i=0;i<t.length;i++){ R.setStart(n,i); R.setEnd(n,i+1); const cr=R.getClientRects(); if(!cr.length) continue; if(pt!==null && cr[0].top>pt+3 && HG.test(t[i-1]) && HG.test(t[i])){ out.push(t.slice(Math.max(0,i-6),i)+'|'+t.slice(i,i+6)); break; } pt=cr[0].top; } }
  return out; }"""

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def kid(code, name, q="?isle=1", tut=99, vw=(390,844)):
            ctx=await br.new_context(viewport={"width":vw[0],"height":vw[1]}, is_mobile=vw[0]<500, has_touch=True)
            pg=await ctx.new_page(); pg.set_default_timeout(150000); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)[:200]))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"+q); await pg.wait_for_timeout(400)
            await pg.evaluate("""([c,n,t])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_dev', 'd'+c); localStorage.setItem('hyeng_me', JSON.stringify({id:'k'+c, t:'g34'})); if(t!==null) localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:t}));
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
        A=await kid("QA687","루아")
        await A.evaluate("()=>ISLE.enter()"); ok(await until(A, ISLE_OK), "섬")
        await A.wait_for_timeout(600)
        # ① 마을: body keep-all · 채팅 빈 글 · 말풍선
        r=await A.evaluate("()=>[getComputedStyle(document.body).wordBreak, (()=>{ const p=document.createElement('p'); p.className='vcB'; document.body.appendChild(p); const w=getComputedStyle(p).wordBreak; p.remove(); return w; })()]")
        ok(r==["keep-all","keep-all"], f"① 마을 글자: 띄어쓰기에서만 줄바꿈 (body · 채팅 말풍선) {r}")
        await A.evaluate("()=>{ try{ vcOpen(); }catch(e){} }"); await A.wait_for_timeout(500)
        r=await A.evaluate(BRK, "#vcPane"); ok(r==[], f"① 채팅 창: 낱자 중간 줄바꿈 없음 {r}")
        await A.evaluate("()=>{ try{ vcClose(); }catch(e){ document.getElementById('vcPane') && document.getElementById('vcPane').classList.remove('on'); } }")
        # ④ 가방 씨앗 봉투
        await A.evaluate("()=>{ HOUSE.addMat('carrot seeds', 3); HOUSE.addMat('wheat seeds', 2); HOUSE.openBag(); }"); await A.wait_for_timeout(500)
        r=await A.evaluate("()=>[...document.querySelectorAll('#bagP .slot i.pk')].map(i=>i.closest('.slot').dataset.slot+'='+i.textContent)")
        ok(len(r)>=2 and any("carrot seeds=🥕" in x for x in r) and any(x.startswith("wheat seeds=") and not x.endswith("🌰") for x in r), f"④ 가방 씨앗 = 작물 그림 봉투 {r}")
        await A.evaluate("()=>document.getElementById('bagP').classList.remove('on')")
        # ② 가게 긴 이름
        await A.evaluate("()=>HLIFE.openMart()"); await A.wait_for_timeout(800)
        r=await A.evaluate("()=>[...document.querySelectorAll('#suP .suC .nm')].map(n=>[n.textContent, n.scrollWidth-n.clientWidth, parseFloat(getComputedStyle(n).fontSize)])")
        st=[x for x in r if x[0]=="strawberry seeds"]
        ok(st and st[0][1]<=1 and 10<=st[0][2]<14 and all(x[1]<=1 for x in r), f"② 가게 이름이 칸 안에 다 들어감 (strawberry seeds 글자만 작게) {st} · 넘침 {[x for x in r if x[1]>1]}")
        await A.evaluate("()=>{ try{ SHOPUI.close(); }catch(e){} document.querySelectorAll('#suP.on').forEach(e=>e.classList.remove('on')); }")
        # ⑤ 카메라 바로 앞 비침
        await A.wait_for_timeout(500)
        v=await A.evaluate("()=>TOON.nearV()")
        r=await A.evaluate("""()=>{ const m=new THREE.MeshStandardMaterial({color:0xff2020}); TOON.mat(m); const b=new THREE.Mesh(new THREE.BoxGeometry(1.2,1.2,1.2), m);
            const d=new THREE.Vector3(); camera.getWorldDirection(d); b.position.copy(camera.position).addScaledVector(d, 2.2); if(b.position.y<1.2) b.position.y=1.2; b.lookAt(camera.position); scene.add(b);
            const W=renderer.domElement.width, H=renderer.domElement.height, rt=new THREE.WebGLRenderTarget(W,H), px=new Uint8Array(40*40*4);
            const cnt=(nv)=>{ TOON.near(nv); renderer.setRenderTarget(rt); renderer.render(scene, camera); renderer.readRenderTargetPixels(rt, Math.floor(W/2)-20, Math.floor(H/2)-20, 40, 40, px); renderer.setRenderTarget(null); let n=0; for(let i=0;i<px.length;i+=4) if(px[i]>110 && px[i+1]<90 && px[i+2]<90) n++; return n; };
            const a=cnt(3.4), z=cnt(0); scene.remove(b); b.geometry.dispose(); m.dispose(); rt.dispose(); return [a, z]; }""")
        ok(v>=2 and r[1]>=1200 and r[0]<=r[1]*.4, f"⑤ 섬: 카메라 2칸 앞 물건은 점점이 비침 (uNear {v} · 빨간 칸 비침 {r[0]} / 그대로 {r[1]})")
        await A.evaluate("()=>MG.enter('card', {quick:1, mode:'solo'})"); await until(A, "()=>MG.on", 60); await A.wait_for_timeout(1200)
        v2=await A.evaluate("()=>TOON.nearV()"); await A.evaluate("()=>MG.exit()"); await until(A, "()=>!MG.on", 60)
        await A.evaluate("()=>ISLE.enterHome()"); await until(A, "()=>HOUSE.place()==='room' && !HOUSE.trip().busy"); await A.wait_for_timeout(600)
        v3=await A.evaluate("()=>TOON.nearV()")
        ok(v2==0 and v3==0, f"⑤ 놀이 공원 · 방 안에선 꺼짐 {v2} {v3}")
        # ⑦ 집에서 나오기 → 길 쪽으로 걸어 나감
        await A.evaluate("()=>{ const b=document.getElementById('infoOk'); if(document.getElementById('info').classList.contains('on')) b.click(); exitRoom(); }")
        ok(await until(A, ISLE_OK), "⑦ 섬으로 나옴")
        D="()=>{ const d=ISLE.doorCell(), p=HOUSE.hero().g.position; return Math.hypot(p.x-d[0]-.5, p.z-d[1]-.5); }"
        d0=await A.evaluate(D)
        moved=await until(A, D.replace("return Math.hypot","return 2.2<=Math.hypot"), 80); await A.wait_for_timeout(1500)
        d1=await A.evaluate(D)
        ok(moved and d1>=2.2, f"⑦ 문 앞 {d0:.1f} → 길 쪽으로 {d1:.1f}칸")
        await A.context.close()
        # ⑥ 튜토리얼 🎣 호수 · 첫 기차 공짜 + ⑧ 화살표 · ① 안내 글
        B=await kid("QB687","하늘", tut=7)
        await B.evaluate("()=>ISLE.enter()"); ok(await until(B, ISLE_OK), "섬 (튜토리얼 🎣 호수)")
        await B.wait_for_timeout(1200)
        r=await B.evaluate("()=>{ const L=ISLE.SPOT.lake, p=HOUSE.hero().g.position, b=document.getElementById('coachNext'); return {tut:HOUSE.tut().s, far:Math.round(Math.hypot(p.x-L[0], p.z-L[2])), on:document.getElementById('coach').classList.contains('on'), btn:!b.hidden, t:b.textContent, coin:TECO.coins()}; }")
        ok(r["on"] and r["far"]>18 and r["btn"] and "기차" in r["t"], f"⑥ 호수가 멀면 「🚂 기차 타고 호수로 (공짜)」 {r}")
        b=await B.evaluate(BRK, "#coach"); ok(b==[], f"① Mia 안내 글: 낱자 중간 줄바꿈 없음 {b}")
        # ⑧ 화살표: 카메라를 돌려 「🎣 호수」 이름표가 화면 끝에 붙을 때
        res=[]
        for k in range(8):
            x=await B.evaluate("""(k)=>{ yaw=yawTo=k*Math.PI/4; ISLE.CAM.dragAt=performance.now()+1e6; return new Promise(res=>setTimeout(()=>{ const L=LBL.find(l=>l.el.classList.contains('hot') && l.d.k==='lake'); if(!L || !L.el.classList.contains('edge')) return res(null);
                const a=getComputedStyle(L.el,'::after'), m=new DOMMatrix(a.transform), b=L.el.getBoundingClientRect(), cx=b.left+b.width/2+m.e, cy=b.top+b.height/2+m.f, ea=Math.atan2(m.b, m.a), rad=Math.abs(Math.cos(ea))*b.width/2+Math.abs(Math.sin(ea))*b.height/2;
                const hud=['ihMe','ihRes','ihMenu','ihQ'].filter(id=>{ const e=document.getElementById(id); if(!e || !e.getClientRects().length) return false; const q=e.getBoundingClientRect(); return cx+14>q.left && cx-14<q.right && cy+14>q.top && cy-14<q.bottom; }); res([a.content.includes('➜'), Math.round(Math.hypot(m.e,m.f)), Math.round(rad), Math.round(cx), Math.round(cy), getComputedStyle(L.el,'::before').display, hud.join()]); }, 450)); }""", k)
            if x: res.append(x)
        ok(res and all(a[0] and a[1]>=a[2]+16 and 14<=a[3]<=376 and a[5]=="none" and not a[6] for a in res), f"⑧ 화면 밖 안내: 「➜」 화살표가 이름표 바깥 · 화면 안 · 위쪽 칸에 안 가림 · 👇 숨김 [➜, 거리, 이름표 반지름, x, y, 👇, 가린 칸] {res}")
        c0=r["coin"]
        await B.evaluate("()=>document.getElementById('coachNext').click()"); await B.wait_for_timeout(600)
        r=await B.evaluate("()=>[!!document.getElementById('tfRide') && document.getElementById('tfRide').classList.contains('on'), TECO.coins(), localStorage.getItem('hyeng_proto_tride')]")
        ok(r[0] and r[1]==c0 and r[2] is not None, f"⑥ 눌러서 기차 (코인 그대로 {c0}→{r[1]} · 한 번 탔다고 기록) {r}")
        await B.wait_for_timeout(3200)
        await B.evaluate("()=>{ const b=document.querySelector('#tfRide [data-a=lake]') || [...document.querySelectorAll('#tfRide button')].find(x=>/lake|호수/i.test(x.textContent)); if(b) b.click(); }")
        ok(await until(B, "()=>{ const L=ISLE.SPOT.lake, p=HOUSE.hero().g.position; return Math.hypot(p.x-L[0], p.z-L[2])<14 && !(document.getElementById('tfRide')||{classList:{contains:()=>false}}).classList.contains('on'); }", 60), "⑥ 호수 섬에 내림")
        await B.wait_for_timeout(500)
        r=await B.evaluate("()=>{ const b=document.getElementById('coachNext'); return [HOUSE.tut().s, b.hidden || !/기차/.test(b.textContent)]; }")
        ok(r[0]==7 and r[1], f"⑥ 내린 뒤엔 기차 단추 없음 (아직 낚시 단계) {r}")
        await B.context.close()
        # ⑨ 이름표가 위쪽 💎🪙 칸 · 내 얼굴 · ☰ 밑에 숨지 않음 (처음 온 아이 = 「📋 땅 고르기」 안내)
        C=await kid("QC687","별", tut=0)
        await C.evaluate("()=>ISLE.enter()"); ok(await until(C, ISLE_OK), "섬 (처음 온 아이)")
        await C.wait_for_timeout(1200)
        hits=[]; seen=0
        for k in range(8):
            x=await C.evaluate("""(k)=>{ yaw=yawTo=k*Math.PI/4; ISLE.CAM.dragAt=performance.now()+1e6; return new Promise(res=>setTimeout(()=>{ const H=['ihRes','ihMe','ihMenu'].map(id=>document.getElementById(id).getBoundingClientRect()), out=[]; let n=0;
                document.querySelectorAll('#tls .tl').forEach(e=>{ if(e.style.display==='none' || e.classList.contains('far') || e.classList.contains('hudx') || !e.getClientRects().length) return; const b=e.getBoundingClientRect(); if(b.width<4) return; n++; const cx=b.left+b.width/2, cy=b.top+b.height/2;
                    if(H.some(q=>cx>q.left && cx<q.right && cy>q.top && cy<q.bottom)) out.push(e.textContent.trim().slice(0,12)); }); res([n,out]); }, 700)); }""", k)
            seen+=x[0]; hits+=x[1]
        ok(seen>=4 and not hits, f"⑨ 이름표가 위쪽 칸(💎🪙 · 얼굴 · ☰) 밑에 숨지 않음 (본 이름표 {seen}) 숨은 것 {hits}")
        await C.context.close()
        # ①③ 게임 화면 (index.html)
        G=await br.new_page(viewport={"width":390,"height":844}); G.on("pageerror", lambda e: errs.append("index: "+str(e)[:200]))
        await boot(G)
        r=await G.evaluate("()=>getComputedStyle(document.body).wordBreak"); ok(r=="keep-all", f"① 게임 글자: 띄어쓰기에서만 줄바꿈 {r}")
        await G.evaluate("()=>showRank('study')"); await G.wait_for_timeout(700)
        r=await G.evaluate("()=>{ const P=document.querySelector('#scRank .panel'); return [getComputedStyle(P).justifyContent, Math.round(P.firstElementChild.getBoundingClientRect().top - P.getBoundingClientRect().top)]; }")
        ok(r[0]=="flex-start" and r[1]<60, f"③ 순위표가 위에서부터 {r}")
        b=await G.evaluate(BRK, "#scRank"); ok(b==[], f"① 순위표: 낱자 중간 줄바꿈 없음 {b}")
        await G.evaluate("()=>openSettings()"); await G.wait_for_timeout(600)
        b=await G.evaluate(BRK, "#shSettings"); ok(b==[], f"① 설정: 낱자 중간 줄바꿈 없음 {b}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
