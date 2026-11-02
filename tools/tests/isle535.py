"""(v535) 🏝 우리 마을 새 화면(HUD 1안) · 집 모양·색 · 공부로 집 자람 · 땅 꾸밈 · 🗼 타워 B 툰
   ① HUD: 얼굴 배지(이름·지금 있는 곳) · ☰ · 💎🪱 · 오늘 할 일 카드 · 💬 · 🧰 도구 · 옛 위/아래 단추 숨김
   ② 🧰 도구 → 4개가 점프 둘레로 펼침 (화면 안 · 서로/점프와 안 겹침) · 다시 누르면 접힘 · 꾸미기 → 집 꾸미기 창
   ③ ☰ → 색 칸 6개 · 칸 누르면 해당 창 (할 일·우리 땅)
   ④ 가까이 가면 초록 말풍선 + 바닥 빛 고리 · 멀면 작은 아이콘
   ⑤ 잡았다! 카드에 📖 도감
   ⑥ 집 모양·색: 고르면 서버 h · 내 집 모양 바뀜 · 친구 화면에도 · 공부한 날 → 단계 t 서버 · 단계별 꾸밈(울타리 등)
   ⑦ 그리기 횟수 적당 (집 48채여도) · 문 길 그대로
   ⑧ 🗼 타워: 10층마다 테마 색 · 풀섬 · 오류 없음"""
import asyncio, sys, os, json
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
        async def kid(code,name,days):
            ctx=await br.new_context(viewport={"width":390,"height":760}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(600)
            await pg.evaluate("""([c,n,d])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')||k.startsWith('hyeng_isle')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); localStorage.setItem('hyeng_isle_cam','1');
                localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:d,tot:d}})); }""", [code,name,days])
            await pg.reload(); await pg.wait_for_timeout(1800); return pg
        async def until(pg, js, n=120):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        async def enter(pg):
            await pg.evaluate("()=>HOUSE.exitRoom()"); return await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy && !HOUSE.hero().slide")
        A=await kid("AAAAA","루아",12)
        ok(await enter(A), "🏝 들어감"); await A.wait_for_timeout(1500)
        # ①
        r=await A.evaluate("""()=>{ const v=id=>{ const e=document.getElementById(id); if(!e) return false; const s=getComputedStyle(e), r=e.getBoundingClientRect(); return s.display!=='none' && r.width>0 && r.right<=innerWidth+1 && r.left>=-1; };
            return {me:v('ihMe'), menu:v('ihMenu'), res:v('ihRes'), q:v('ihQ'), chat:v('ihChat'), tool:v('ihTool'), jump:v('ijump'), joy:v('ijoy'), oldTop:getComputedStyle(document.querySelector('.bar.top .tools')).display, oldBot:getComputedStyle(document.querySelector('.bar.bot')).display, oldHud:getComputedStyle(document.getElementById('hud')).display,
              name:document.getElementById('ihMe').innerText, gem:document.getElementById('ihGem').textContent, q4:document.querySelector('#ihQ h4').innerText}; }""")
        print("①", r)
        ok(all(r[k] for k in ("me","menu","res","q","chat","tool","jump","joy")), "① 새 화면 단추 다 보임 (화면 안)")
        ok(r["oldTop"]=="none" and r["oldBot"]=="none" and r["oldHud"]=="none", "① 옛 위·아래 단추 숨김")
        ok("루아" in r["name"] and ("동" in r["name"] or "광장" in r["name"] or "길" in r["name"]), f"① 얼굴 배지 = 이름 + 있는 곳 {r['name']!r}")
        ok("오늘 할 일" in r["q4"], f"① 할 일 카드 {r['q4']!r}")
        # ②
        await A.evaluate("()=>document.getElementById('ihTool').click()"); await A.wait_for_timeout(700)
        r=await A.evaluate("""()=>{ const B=[...document.querySelectorAll('.ihF')].map(b=>b.getBoundingClientRect()), J=document.getElementById('ijump').getBoundingClientRect(), T=document.getElementById('ihTool').getBoundingClientRect();
            const c=r=>[r.left+r.width/2, r.top+r.height/2], d=(a,b)=>Math.hypot(c(a)[0]-c(b)[0], c(a)[1]-c(b)[1]);
            let minP=1e9; for(let i=0;i<B.length;i++) for(let j=i+1;j<B.length;j++) minP=Math.min(minP, d(B[i],B[j]));
            return {n:B.length, inView:B.every(r=>r.left>=0 && r.right<=innerWidth && r.top>=0), minP, minJ:Math.min(...B.map(b=>d(b,J))), minT:Math.min(...B.map(b=>d(b,T))), open:document.getElementById('ih').classList.contains('fan'), op:getComputedStyle(document.querySelector('.ihF')).opacity}; }""")
        print("②", r)
        ok(r["n"]==4 and r["open"] and r["inView"], "② 🧰 도구 → 4개 펼침 (화면 안)")
        ok(r["minP"]>=50 and r["minJ"]>=70 and r["minT"]>=50, f"② 안 겹침 (서로 {r['minP']:.0f} · 점프 {r['minJ']:.0f} · 도구 {r['minT']:.0f})")
        await A.evaluate("()=>document.querySelector('.ihF[data-f=deco]').click()")
        ok(await until(A, "()=>document.getElementById('hsP') && document.getElementById('hsP').classList.contains('on') && !document.getElementById('ih').classList.contains('fan')", 20), "② 🎨 꾸미기 → 집 꾸미기 창 (도구는 접힘)")
        # ⑥ 집 모양
        await A.wait_for_timeout(800)
        lid=await A.evaluate("()=>ISLE.myHouse().id")
        rec=DB["hy"]["isle"]["lot2"][lid]
        ok(rec.get("t")==3, f"⑥ 공부한 날 12일 → 3단계 서버 {rec}")
        r=await A.evaluate("()=>{ const t=document.querySelector('.hsTop').innerText; return [t, document.querySelectorAll('[data-hs]').length]; }")
        ok("3단계" in r[0] and r[1]==12, f"⑥ 창: 3단계 · 모양·색 12개 (뾰족·넓은·모던 × 4색) {r}")
        o0=await A.evaluate("()=>{ window.__o=ISLE.myHouse().obj; return ISLE.myHouse().style; }")
        pick="B_green" if o0!="B_green" else "A_blue"
        await A.evaluate("(k)=>document.querySelector('[data-hs=\"'+k+'\"]').click()", pick); await A.wait_for_timeout(700)
        r=await A.evaluate("()=>[ISLE.myHouse().style, ISLE.myHouse().obj!==window.__o, !!ISLE.myHouse().obj.parent, ISLE.myHouse().obj.userData.lot===ISLE.myHouse(), document.querySelector('[data-hs].on').dataset.hs]")
        ok(r[0]==pick and r[1] and r[2] and r[3] and r[4]==pick, f"⑥ 고르면 내 집이 바로 바뀜 {r}")
        ok(DB["hy"]["isle"]["lot2"][lid].get("h")==pick, f"⑥ 서버 h = {DB['hy']['isle']['lot2'][lid].get('h')}")
        await A.evaluate("()=>document.getElementById('hsX').click()")
        B=await kid("BBBBB","하준",0)
        ok(await enter(B), "친구 들어감"); await B.wait_for_timeout(1200)
        r=await B.evaluate("(id)=>{ const L=ISLE.lots.find(l=>l.id===id), M=ISLE.myHouse(); return [L.style, L.tier, M.tier, ISLE.TIER[M.tier-1].s]; }", lid)
        ok(r[0]==pick and r[1]==3, f"⑥ 친구 화면에도 루아 집 = {pick} · 3단계 {r}")
        ok(r[2]==1, f"⑥ 공부 0일 = 1단계 작은 집 {r}")
        # ⑦ 그리기 횟수 · 문 길
        await B.evaluate("""async ()=>{ const ids=[]; for(let h=1;h<=3;h++) for(let n=1;n<=16;n++) ids.push(h+'-'+n);
            for(const id of ids){ const v=await NET.get('/hy/isle/lot2/'+id); if(!v) await NET.put('/hy/isle/lot2/'+id, {k:'x'+id, c:'ZZZZZ', n:'친구'+id, at:1, h:['A_red','B_blue','A_yellow','B_green'][id.length%4], t:1+(+id.split('-')[1])%4}); } await ISLE.loadLots(); ISLE.rebuild(); }""")
        await B.wait_for_timeout(1500)
        r=await B.evaluate("()=>{ renderer.info.autoReset=true; TOON.draw(); return {calls:renderer.info.render.calls, owned:ISLE.lots.filter(l=>l.owner).length, stuck:ISLE.stuckDoors(), meshes:ISLE.G.children.length, t4:ISLE.lots.filter(l=>l.tier===4).length}; }")
        print("⑦", r)
        ok(r["owned"]>=48 and not r["stuck"], f"⑦ 집 {r['owned']}채 · 문 길 막힘 없음")
        ok(r["calls"]<260, f"⑦ 한 장면 그리기 {r['calls']}번 (울타리·꽃은 한 덩어리)")
        # ④ 말풍선 · 빛 고리
        await A.evaluate("()=>{ const S=ISLE.SPOT.lake, h=HOUSE.hero(); h.g.position.set(S[0]-1,0,S[2]); h.cx=Math.floor(S[0]-1); h.cz=Math.floor(S[2]); camSnap=true; }")
        ok(await until(A, "()=>IHUD.ring() && IHUD.ring().visible", 30), "④ 가까운 할 일 = 바닥 빛 고리")
        r=await A.evaluate("()=>{ const L=LBL.find(l=>l.d.k==='lake'), F=LBL.find(l=>l.d.k==='tower'); return [L && !L.el.classList.contains('far'), getComputedStyle(L.el).backgroundImage.indexOf('gradient')>=0, F && F.el.classList.contains('far'), F && getComputedStyle(F.el).opacity]; }")
        ok(r[0] and r[1] and r[2] and float(r[3])>0.3, f"④ 가까이 = 초록 말풍선 · 멀리 = 작은 아이콘(보임) {r}")
        # ③ 메뉴
        await A.evaluate("()=>document.getElementById('ihMenu').click()"); await A.wait_for_timeout(400)
        r=await A.evaluate("()=>[document.getElementById('ihM').classList.contains('on'), document.querySelectorAll('#ihM [data-m]').length]")
        ok(r==[True,6], f"③ ☰ → 색 칸 6개 {r}")
        await A.evaluate("()=>document.querySelector('#ihM [data-m=q]').click()")
        ok(await until(A, "()=>document.getElementById('qP').classList.contains('on') && !document.getElementById('ihM').classList.contains('on')", 20), "③ 📋 할 일 칸 → 할 일 창")
        await A.evaluate("()=>document.getElementById('qP').classList.remove('on')")
        await A.evaluate("()=>{ document.getElementById('ihMenu').click(); document.querySelector('#ihM [data-m=lot]').click(); }")
        ok(await until(A, "()=>document.getElementById('lotP') && document.getElementById('lotP').classList.contains('on')", 30), "③ 🏡 우리 땅 → 땅 고르기")
        await A.evaluate("()=>document.getElementById('lotP').classList.remove('on')")
        # ⑤ 잡았다 카드
        await A.evaluate("()=>{ F.cm=20; F.sh=false; quiz(HOUSE.FISH[1]); }"); await A.wait_for_timeout(400)
        r=await A.evaluate("()=>[document.getElementById('quiz').classList.contains('on'), !!document.getElementById('qDexB'), getComputedStyle(document.querySelector('#quiz .box'),'::before').content]")
        ok(r[0] and r[1] and "잡았다" in r[2], f"⑤ 잡았다! 카드 + 📖 도감 {r}")
        await A.evaluate("()=>document.getElementById('qDexB').click()")
        ok(await until(A, "()=>document.getElementById('dexP').classList.contains('on')", 20), "⑤ 📖 도감 → 도감 창")
        await A.evaluate("()=>document.getElementById('dexP').classList.remove('on')")
        # ⑧ 타워
        await A.evaluate("()=>HOUSE.twEnterGo('sky')")
        ok(await until(A, "()=>HOUSE.TW.on && !HOUSE.trip().busy", 80), "⑧ 🗼 타워 들어감")
        r=await A.evaluate("()=>[twCol(0), twCol(12), twCol(25), twCol(33), HOUSE.TW.S.length, (()=>{ let n=0; towerG.traverse(o=>{ if(o.isMesh && o.geometry && o.geometry.type==='ConeGeometry' && o.geometry.parameters.height===9) n++; }); return n; })()]")
        ok(len(set(r[:4]))==4 and r[4]>50 and r[5]==1, f"⑧ 10층마다 다른 테마 색 · 풀섬 {r}")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
