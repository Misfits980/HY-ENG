"""(v695) 🐾 단어 손님 — 사용자 「그래 너가 한번 해 봐라」 (claude/hy-eng-plan-town-study.md 2번)
   ① 누가 오나: 오늘·어제 처음 본 동물 단어 = 놀러 옴 ✨(2마리까지) · 기억 칸 3 이상 = 이사 옴 🏡(계속) · 모두 4마리까지
   ② 움직이는 동물(Quaternius) = SkinnedMesh · 뼈가 움직임 · 펫 모형(토끼) 도 나옴
   ③ 자리: 광장 둘레 · 막힌 칸·장식(호박 등) 위가 아님 · 걸어 다녀도 광장 둘레 안
   ④ 이름표 = 영어(fox ✨ / 새로 이사 🆕) → 누르면 게임 대화창 · 이름표에 하트
   ⑤ 🤚 쓰다듬기(하루 한 번 ❤️+1) · 🥕 간식(풀 먹는 동물 · 당근 1개 씀 · ❤️+2) · 📖 모음(17칸 · 모르는 건 ???)
   ⑥ 동물 단어가 없으면 아무도 안 옴
   ⑦ 오늘의 30 끝 화면 한 줄: 「🐾 오늘 배운 fox — My Town 광장에 놀러 와요!」"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

SETUP="""(o)=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); const dn=Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5);
  localStorage.setItem('hyeng_proto_code', JSON.stringify('QG695')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_dev','dQG695'); localStorage.setItem('hyeng_me', JSON.stringify({id:'kQG695', t:'A568'})); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_cam','1');
  const sd={}, srs={}; (o.sd||[]).forEach(([w,d])=>sd[w]=dn+d); (o.srs||[]).forEach(([w,b])=>srs[w]=[b,dn+2]);
  localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:4,tot:6,hs:4,hb:4,last:dn}, sd, srs})); }"""

async def boot(pg, o):
    await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
    await pg.evaluate(SETUP, o)
    await pg.reload(); await pg.wait_for_timeout(2000)
    await pg.evaluate("()=>ISLE.enter()")
    for _ in range(200):
        if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
        await pg.wait_for_timeout(250)

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True); pg=await ctx.new_page(); pg.set_default_timeout(150000)
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await pg.route("**/*", fake)
        E=pg.evaluate
        # ① fox·deer 오늘/어제 · wolf 그저께(안 옴) · cow·horse·rabbit 기억 3+ · cat 기억 2(안 옴)
        await boot(pg, {"sd":[["fox",0],["deer",-1],["wolf",-2],["cow",-6],["horse",-9],["rabbit",-5],["cat",-3]], "srs":[["fox",1],["deer",1],["wolf",1],["cow",3],["horse",4],["rabbit",3],["cat",2]]})
        P=await E("()=>GUEST.picks()")
        vis=[w for w,k in P if k=="v"]; res=[w for w,k in P if k=="r"]
        ok(sorted(vis)==["deer","fox"] and set(res)<= {"cow","horse","rabbit"} and len(P)==4, f"① 놀러 {vis} · 이사 {res} (4마리까지 · wolf·cat 안 옴)")
        H=await E("()=>Object.keys(GUEST.st().home).sort()")
        ok(H==["cow","horse","rabbit"], f"① 이사 기록 {H}")
        for _ in range(60):
            if await E("()=>GUEST.A().length")>=4: break
            await pg.wait_for_timeout(250)
        A=await E("()=>GUEST.A().map(G=>[G.w, G.kind, G.kind0])")
        ok(len(A)==4, f"② 광장에 {len(A)}마리 {A}")
        r=await E("""()=>{ const G=GUEST.A().find(g=>g.kind==='a'); if(!G) return null; let sk=null; G.g.traverse(o=>{ if(o.isSkinnedMesh) sk=o; }); const b=sk.skeleton.bones, q0=b.map(x=>x.quaternion.clone()); G.m.tick(.4); const mv=b.filter((x,i)=>x.quaternion.angleTo(q0[i])>1e-3).length; return [G.w, b.length, mv, !!sk.material.skinning]; }""")
        ok(r and r[1]>=30 and r[2]>=5 and r[3], f"② 움직이는 동물 (뼈 {r and r[1]} 중 {r and r[2]}개 움직임) {r}")
        ok(any(k=="p" for _,k,_ in A) or "rabbit" not in [a[0] for a in A], f"② 토끼 = 펫 모형 {A}")
        # ③ 자리
        r=await E("""()=>GUEST.A().map(G=>{ const p=G.g.position, d=Math.hypot(p.x-ISLE.OX, p.z-ISLE.OZ); return [G.w, +d.toFixed(1), ISLE.blocked(Math.floor(p.x),Math.floor(p.z)), ISLE.busyAt(p.x,p.z,.3)]; })""")
        ok(all(3<=x[1]<=9.6 and not x[2] and not x[3] for x in r), f"③ 광장 둘레 · 막힌 칸/장식 아님 {r}")
        await E("()=>TFAC.warp(ISLE.OX+1, ISLE.OZ+10)"); await pg.wait_for_timeout(800)
        r=await E("""()=>{ const p0=GUEST.A().map(G=>G.g.position.clone()); let mx=0; for(let i=0;i<600;i++){ GUEST.tick(.05); GUEST.A().forEach(G=>{ const p=G.g.position, d=Math.hypot(p.x-ISLE.OX, p.z-ISLE.OZ); if(d>mx) mx=d; if(d<3 || ISLE.blocked(Math.floor(p.x),Math.floor(p.z))) mx=99; }); } return [GUEST.A().filter((G,i)=>G.g.position.distanceTo(p0[i])>.5).length, +mx.toFixed(1)]; }""")
        ok(r[0]>=1 and r[1]<=9.8, f"③ 30초 걸어 다님 (움직인 {r[0]}마리 · 가장 먼 {r[1]}) — 광장 둘레 · 막힌 칸 안 밟음")
        # ④ 이름표
        await E("()=>{ const G=GUEST.A().find(g=>g.w==='fox'); TFAC.warp(G.g.position.x+.8, G.g.position.z+2.4); }"); await pg.wait_for_timeout(1800)
        L=await E("()=>[...document.querySelectorAll('#tls .tl')].map(e=>e.textContent.trim()).filter(t=>/fox|deer|cow|horse|rabbit/.test(t))")
        ok(any("fox" in t and "✨" in t for t in L), f"④ 이름표 영어 {L}")
        lb=await E("()=>{ const L=[]; GUEST.labels(L); return L.map(l=>l.t); }")
        ok(any(t.startswith("cow") and "🆕" in t for t in lb), f"④ 새로 이사 = 🆕 {lb}")
        async def until_ch(n=80):
            for _ in range(n):
                if await E("()=>document.getElementById('dlgCh').classList.contains('on')"): return True
                await E("()=>{ const b=document.getElementById('dlgBox'); if(b) b.click(); }"); await pg.wait_for_timeout(250)
            return False
        async def talk(w):
            await E("(w)=>GUEST.talk(w)", w)
            for _ in range(60):
                if await E("()=>document.getElementById('dlg').classList.contains('on')"): break
                await pg.wait_for_timeout(200)
        await talk("fox")
        r=await E("()=>[document.getElementById('dlg').classList.contains('on'), document.getElementById('dlgName').textContent]")
        ok(r[0] and "fox" in r[1] and "♡" in r[1], f"④ 대화창 · 이름표 {r}")
        ok(await until_ch(), "④ 고르기 나옴")
        await pg.screenshot(path=OUT+"guest695_talk.png")
        ch=await E("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch)")
        ok(ch[:2]==["say","pet"] and "book" in ch and "bye" in ch and "treat" not in ch, f"⑤ 여우 고르기 (간식 없음) {ch}")
        await E("()=>document.querySelector('#dlgCh [data-ch=\"pet\"]').click()"); await pg.wait_for_timeout(400); await until_ch()
        r=await E("()=>[GUEST.st().f.fox|0, [...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch).includes('pet')]")
        ok(r==[1, False], f"⑤ 🤚 쓰다듬기 ❤️+1 · 하루 한 번 {r}")
        await E("()=>{ try{ closeTalk(); }catch(e){} }"); await pg.wait_for_timeout(300)
        # 토끼 간식
        await E("()=>{ HOUSE.addMat('carrot', 2); const G=GUEST.A().find(g=>g.w==='rabbit'); if(G) TFAC.warp(G.g.position.x+.8, G.g.position.z+2.2); }"); await pg.wait_for_timeout(1200)
        if "rabbit" in [a[0] for a in A]:
            await talk("rabbit"); await until_ch()
            ch=await E("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch)")
            c0=await E("()=>mats.carrot|0")
            await E("()=>{ const b=document.querySelector('#dlgCh [data-ch=\"treat\"]'); if(b) b.click(); }"); await pg.wait_for_timeout(500)
            r=await E("()=>[mats.carrot|0, GUEST.st().f.rabbit|0, !!GUEST.st().td.fed.rabbit, GUEST.A().find(g=>g.w==='rabbit').st]")
            ok("treat" in ch and r[0]==c0-1 and r[1]==2 and r[2] and r[3]=="eat", f"⑤ 🥕 간식 → 당근 {c0}→{r[0]} · ❤️ {r[1]} · 먹는 중 {r}")
            await until_ch(); await E("()=>{ try{ closeTalk(); }catch(e){} }")
        # ⑤ 모음
        await E("()=>GUEST.openBook()"); await pg.wait_for_timeout(500)
        r=await E("()=>[document.getElementById('gbP').classList.contains('on'), document.querySelectorAll('#gbP .gC').length, document.querySelectorAll('#gbP .gC.home').length, document.querySelectorAll('#gbP .gC.vis').length, document.querySelectorAll('#gbP .gC.lock').length, document.querySelector('#gbP .gHd b').textContent]")
        ok(r[0] and r[1]==17 and r[2]==3 and r[3]==2 and r[4]>=8 and "3 / 17" in r[5], f"⑤ 📖 단어 손님 모음 {r}")
        await pg.screenshot(path=OUT+"guest695_book.png")
        r=await E("()=>[...document.querySelectorAll('#gbP .gC.lock b')].every(b=>b.textContent==='???')")
        ok(r, "⑤ 모르는 동물 = ???")
        await E("()=>document.getElementById('gbP').classList.remove('on')")
        # ⑥ 동물 단어 없음
        await boot(pg, {"sd":[["apple",0],["red",-1]], "srs":[["apple",3]]})
        await pg.wait_for_timeout(1500)
        r=await E("()=>[GUEST.picks().length, GUEST.A().length]")
        ok(r==[0,0], f"⑥ 동물 단어 없으면 손님 없음 {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        # ⑦ 오늘의 30 끝 화면 한 줄
        g=await br.new_context(viewport={"width":390,"height":844}); g2=await g.new_page(); await g2.route("**/*", route)
        await g2.add_init_script("window.HY_TOWN_GATE=true;")
        await g2.goto(ORIGIN+"index.html"); await g2.wait_for_timeout(1500)
        r=await g2.evaluate("""()=>{ const s=Study.load(); s.sd=s.sd||{}; s.sd.fox=Study.today(); s.sd.cow=Study.today()-3; Study.save(); return [TownGate.guest(), TownGate.line(0)]; }""")
        ok("fox" in r[0] and "cow" not in r[0] and "놀러" in r[0] and "fox" in r[1], f"⑦ 끝 화면 한 줄 {r[0][:90]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
