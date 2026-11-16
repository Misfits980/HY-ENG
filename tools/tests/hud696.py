"""(v696) 📱 My Town 화면 정리 — claude/hy-eng-plan-town-study.md 4번 (시안 ①②)
   ① 왼쪽 위 = 시각·날씨 + 있는 곳 · 돈 알약 하나 · 접힌 「📋 오늘 n/3」 · 🧰 도구 펼침 없음
   ② 📱 HY폰 = 앱 12칸 + 맨 위 오늘 소식 한 줄(이웃 ❗) · 빨간 숫자
   ③ 🐻 이웃 앱 = 4명 · ❗ 줄 · 「가기」(멀면 지도 길 고르기)
   ④ 🐾 단어 손님 앱 = 모음 창
   ⑤ 상황 단추: 가까운 것(여우) = 「💬 말 걸기」 → 대화 · 아무것도 없으면 숨김
   ⑥ 화면 4가지(휴대폰·패드 세로/가로)에서 HUD 끼리 안 겹침 · 화면 안
   ⑦ 패드 = HUD 1.3배 · 대화 글자 크게 · 카메라 한 걸음 뒤"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

SETUP="""()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); const dn=Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5);
  localStorage.setItem('hyeng_proto_code', JSON.stringify('QH696')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_dev','dQH696'); localStorage.setItem('hyeng_me', JSON.stringify({id:'kQH696', t:'A568'})); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_cam','1');
  localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:4,tot:6,hs:4,hb:4,last:dn}, sd:{fox:dn, cow:dn-5}, srs:{fox:[1,dn+1], cow:[3,dn+3]}})); }"""
OVL="""()=>{ const ids=['ihMe','ihMenu','ihRes','ihQ','ihChat','ihAct','ijump','ijoy'], R={}; ids.forEach(id=>{ const e=document.getElementById(id); if(!e || !e.getClientRects().length || getComputedStyle(e).display==='none') return; R[id]=e.getBoundingClientRect(); });
  const out=[], off=[]; const K=Object.keys(R); for(let i=0;i<K.length;i++){ const a=R[K[i]]; if(a.left<-1 || a.top<-1 || a.right>innerWidth+1 || a.bottom>innerHeight+1) off.push(K[i]); for(let j=i+1;j<K.length;j++){ const b=R[K[j]]; const ox=Math.min(a.right,b.right)-Math.max(a.left,b.left), oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top); if(ox>2 && oy>2) out.push(K[i]+'×'+K[j]); } }
  return {n:K.length, ov:out, off}; }"""

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        cams={}
        for nm,vw in [("ph",(390,844)),("pad",(820,1180)),("phL",(844,390)),("padL",(1180,820))]:
            ctx=await br.new_context(viewport={"width":vw[0],"height":vw[1]}, has_touch=True); pg=await ctx.new_page(); pg.set_default_timeout(150000)
            pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
            await pg.evaluate(SETUP); await pg.reload(); await pg.wait_for_timeout(2000)
            await pg.evaluate("()=>ISLE.enter()")
            for _ in range(200):
                if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
                await pg.wait_for_timeout(250)
            for _ in range(40):
                if await pg.evaluate("()=>GUEST.A().length")>=2: break
                await pg.wait_for_timeout(250)
            E=pg.evaluate
            await E("()=>TFAC.warp(ISLE.OX+1, ISLE.OZ+11)"); await pg.wait_for_timeout(1500)
            if nm=="ph":
                r=await E("()=>[document.getElementById('ihMe').innerText, document.querySelectorAll('#ihRes>span').length, getComputedStyle(document.getElementById('ihRes')).borderTopWidth, document.getElementById('ihQ').innerText, !!document.getElementById('ihTool'), document.querySelectorAll('.ihF').length]")
                ok(("오전" in r[0] or "오후" in r[0]) and r[1]>=3 and r[2]!="0px" and "오늘" in r[3] and not r[4] and r[5]==0, f"① 시각·날씨 · 돈 알약 하나 · 접힌 할 일 · 도구 펼침 없음 {r}")
                await E("()=>document.getElementById('ihMenu').click()"); await pg.wait_for_timeout(500)
                r=await E("()=>[document.getElementById('ihM').classList.contains('on'), document.querySelectorAll('#ihM .bx [data-m]').length, document.getElementById('ihNw').innerText, document.getElementById('ihNw').dataset.go, document.querySelector('#ihMenu u').textContent, document.querySelector('#ihM [data-m=nb] u').textContent]")
                ok(r[0] and r[1]==12 and r[3]=="nb" and "help" in r[2] and int(r[4] or 0)>=2 and r[5]=="2", f"② 📱 HY폰 앱 12칸 · 소식 = 이웃 ❗ · 빨간 숫자 {r}")
                await pg.screenshot(path=OUT+"hud696_phone.png")
                await E("()=>document.querySelector('#ihM [data-m=nb]').click()"); await pg.wait_for_timeout(500)
                r=await E("()=>[document.getElementById('nbP').classList.contains('on'), document.querySelectorAll('#nbP .nR').length, document.querySelectorAll('#nbP .nR.bang').length, !document.getElementById('ihM').classList.contains('on')]")
                ok(r==[True,4,2,True], f"③ 🐻 이웃 앱 4명 · ❗ 2 {r}")
                await pg.screenshot(path=OUT+"hud696_nb.png")
                await E("()=>document.querySelector('#nbP [data-ngo=tom]').click()"); await pg.wait_for_timeout(500)
                r=await E("()=>[document.getElementById('ask').classList.contains('on'), (document.getElementById('ask').innerText||'').slice(0,60)]")
                ok(r[0] and "버섯" in r[1], f"③ 「가기」 멀면 → 지도 길 고르기 {r}")
                await E("()=>{ document.getElementById('ask').classList.remove('on'); }"); await pg.wait_for_timeout(300)
                await E("()=>{ document.getElementById('ihMenu').click(); document.querySelector('#ihM [data-m=guest]').click(); }"); await pg.wait_for_timeout(500)
                r=await E("()=>[document.getElementById('gbP') && document.getElementById('gbP').classList.contains('on'), document.querySelectorAll('#gbP .gC').length]")
                ok(r==[True,17], f"④ 🐾 단어 손님 앱 {r}")
                await E("()=>document.getElementById('gbP').classList.remove('on')")
                # ⑤ 상황 단추
                await E("()=>TFAC.warp(ISLE.OX+1, ISLE.OZ+30)"); await pg.wait_for_timeout(1200)
                await E("()=>{ const L=LBL.filter(l=>l.near); return L.length; }")
                r0=await E("()=>[document.getElementById('ihAct').classList.contains('on'), LBL.filter(l=>l.near).map(l=>l.d.k)]")
                await E("()=>{ const G=GUEST.A().find(g=>g.w==='fox'); TFAC.warp(G.g.position.x+.8, G.g.position.z+1.4); }"); await pg.wait_for_timeout(1500)
                r=await E("()=>[document.getElementById('ihAct').classList.contains('on'), document.getElementById('ihAct').innerText.replace(/\\s+/g,' ')]")
                ok((not r0[0] or r0[1]) and r[0] and "말 걸기" in r[1], f"⑤ 상황 단추 — 멀면 {r0} · 여우 옆 {r}")
                await E("()=>document.getElementById('ihAct').click()")
                for _ in range(40):
                    if await E("()=>document.getElementById('dlg').classList.contains('on')"): break
                    await pg.wait_for_timeout(200)
                r=await E("()=>[document.getElementById('dlg').classList.contains('on'), document.getElementById('dlgName').textContent, document.getElementById('ihAct').classList.contains('on')]")
                ok(r[0] and "fox" in r[1] and not r[2], f"⑤ 누르면 대화 · 대화 중엔 단추 숨김 {r}")
                cams[nm]=await E("()=>camera.position.distanceTo(hero.g.position)")
                await E("()=>{ try{ closeTalk(); }catch(e){} }")
            if nm=="pad":
                r=await E("()=>[Math.round(document.getElementById('ihMe').getBoundingClientRect().height), Math.round(document.getElementById('ihMenu').getBoundingClientRect().width)]")
                ok(r[0]>=60 and r[1]>=60, f"⑦ 패드 HUD 크게 {r}")
                await E("()=>{ const G=GUEST.A().find(g=>g.w==='fox'); TFAC.warp(G.g.position.x+.8, G.g.position.z+1.4); }"); await pg.wait_for_timeout(1200)
                await E("()=>GUEST.talk('fox')")
                for _ in range(40):
                    if await E("()=>document.getElementById('dlg').classList.contains('on')"): break
                    await pg.wait_for_timeout(200)
                r=await E("()=>[parseFloat(getComputedStyle(document.getElementById('dlgEn')).fontSize), camera.position.distanceTo(hero.g.position)]")
                cams[nm]=r[1]
                ok(r[0]>=27, f"⑦ 패드 대화 글자 {r[0]}px")
                async def settle():
                    a=-1
                    for _ in range(40):
                        await E("()=>{ dirty=true; }"); await pg.wait_for_timeout(300); b=await E("()=>camD")
                        if abs(b-a)<.03: return b
                        a=b
                    return a
                await E("()=>{ try{ closeTalk(); }catch(e){} }")
                d=await settle()
                await pg.screenshot(path=OUT+"hud696_pad.png")
                await E("()=>{ ISLE.CAM.zoom=1/1.4; dirty=true; }"); d0=await settle()
                await E("()=>{ ISLE.CAM.zoom=1; dirty=true; }"); await settle()
                cams["padWalk"]=d; cams["pad0"]=d0
            await E("()=>TFAC.warp(ISLE.OX+1, ISLE.OZ+11)"); await pg.wait_for_timeout(1000)
            r=await E(OVL)
            ok(r["n"]>=6 and not r["ov"] and not r["off"], f"⑥ {nm} HUD {r['n']}개 안 겹침·화면 안 {r}")
            if nm=="ph":
                cams["phWalk"]=await E("()=>camera.position.distanceTo(hero.g.position)")
            await ctx.close()
        ok(cams.get("padWalk",0)>cams.get("pad0",99)*1.25, f"⑦ 패드 카메라 한 걸음 뒤 (예전 {cams.get('pad0',0):.1f} → 지금 {cams.get('padWalk',0):.1f} · 휴대폰 {cams.get('phWalk',0):.1f})")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
