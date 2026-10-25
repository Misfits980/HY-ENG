"""(v397) 🧭 오늘의 코스 — 첫 화면 버튼 하나가 다음 할 일 (📚 공부 → 🏃 달리기 → ⚔️ 보스) · 다 하면 💎5 한 번
  ① 처음엔 「공부부터」 · 점 2개(보스 없음) ② 공부 끝 → 점 1 · 「다음: 달리기」 ③ 눌러서 그 Stage 단어로 바로 달리기(보상 판)
  ④ 달리기(맞힘 4+) → 점 2 · 💎+5 · 완주 표시 ⑤ 같은 날 다시 해도 💎 한 번만 ⑥ 주간 보스가 열려 있고 기회가 있으면 점 3개 → ⚔️ 휘두르면 완주
  ⑦ 연습 달리기·짧은 판은 안 셈 ⑧ 다음 날이 되면 처음으로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
KEEP="""()=>{ if(window.__k) return; window.__k=setInterval(()=>{ try{ if(!G.running) return; if(G.lives<G.maxLives) G.lives=G.maxLives; G.inv=5; const s=activeSet(); if(s&&s.gates&&s.q){ P.x=s.gates[s.q.answer].root.position.x; P.vx=0; } }catch(e){} },40); }"""
async def txt(pg): return await pg.evaluate("()=>{ const b=document.getElementById('crsBtn'); return b && !b.hidden ? [b.innerText.replace(/\\s+/g,' ').trim(), b.querySelectorAll('.crsDots i').length, b.querySelectorAll('.crsDots i.on').length, b.classList.contains('fin')] : null; }")
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ Voice.canListen=()=>true; show('scStart'); Course.s=null; DM.paint(); }"); await pg.wait_for_timeout(300)
        r=await txt(pg); ok(r and "공부부터" in r[0] and r[1]==2 and r[2]==0, f"처음: 공부부터 · 점 2 {r}")
        await pg.screenshot(path=OUT+"crs_start.png")
        g0=await pg.evaluate("()=>Wallet.gems()")
        # 공부
        await pg.evaluate("()=>document.getElementById('crsBtn').click()"); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("()=>document.getElementById('scStudy').classList.contains('on')"), "누르면 공부 화면")
        await pg.evaluate("()=>{ StudyUI.book='mid'; StudyUI.set='mid'; StudyUI.path(); StudyUI.start(60,false); }"); await pg.wait_for_timeout(300)
        for s in range(200):
            if not await pg.evaluate("()=>!!StudyUI.qs[StudyUI.i]"): break
            await pg.evaluate(SOLVE, False)
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
            await pg.wait_for_timeout(25)
        await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.close(); }"); await pg.wait_for_timeout(400)
        r=await txt(pg); ok(r and "다음: 🏃" in r[0] and r[2]==1, f"공부 뒤: 다음 달리기 · 점 1 {r}")
        # 달리기 — 코스 버튼으로 (보상 판)
        await pg.evaluate("()=>document.getElementById('crsBtn').click()"); await pg.wait_for_timeout(1800)
        info=await pg.evaluate("()=>({running:G.running, practice:!!G.practice, words:(G.words||[]).length, set:G.set})")
        ok(info["running"] and not info["practice"] and info["words"]>=5, f"눌러서 배운 Stage 단어로 바로 달리기(보상 판) {info}")
        await pg.evaluate(KEEP)
        for i in range(40):
            await pg.wait_for_timeout(500)
            if await pg.evaluate("()=>G.right>=5"): break
        await pg.evaluate("()=>{ G.quit=false; gameOver(); }"); await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnMain'); if(b) b.click(); show('scStart'); DM.paint(); }"); await pg.wait_for_timeout(400)
        r=await txt(pg); g1=await pg.evaluate("()=>Wallet.gems()")
        ok(r and r[2]==2 and r[3] and "완주" in r[0], f"달리기 뒤: 완주 {r}")
        ok(g1-g0>=5, f"완주 보너스 💎+5 이상 {g0}→{g1}")
        # 한 번만
        n=await pg.evaluate("()=>{ const g=Wallet.gems(); Course.s.got=0; Course.check(); return Wallet.gems()-g; }"); ok(n==0, f"같은 날 보너스 두 번 안 줌 {n}")
        # 연습 달리기는 안 셈
        await pg.evaluate("()=>{ Course.s={day:DM.day(), s:1, r:0, b:0, got:0}; Course.save(); }")
        await pg.evaluate("()=>{ StudyUI.set='mid'; StudyUI.run(60); }"); await pg.wait_for_timeout(1500)
        await pg.evaluate(KEEP)
        for i in range(40):
            await pg.wait_for_timeout(500)
            if await pg.evaluate("()=>G.right>=5"): break
        pr=await pg.evaluate("()=>!!G.practice")
        await pg.evaluate("()=>{ G.quit=false; gameOver(); }"); await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnMain'); if(b) b.click(); show('scStart'); }"); await pg.wait_for_timeout(300)
        ok(pr and await pg.evaluate("()=>Course.load().r")==0, "연습 달리기는 코스에 안 셈")
        # 보스
        await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{a:{n:'초등반'}}, k:{k1:{n:'민준',t:'a'}}}).then(()=>HyBoss.setup({on:true, team:true, split:'eq', restart:true})); }"""); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ Kid.set({id:'k1',n:'민준',t:'a'}); return HyBoss.refresh(true).then(()=>HyBoss.earn(Kid.get(),'study',5)); }"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ Course.s=null; Course._k=''; localStorage.removeItem(Course.key()); Course.s={day:DM.day(), s:1, r:1, b:0, got:0}; Course.save(); DM.paint(); }")
        r=await txt(pg); ok(r and r[1]==3 and "보스" in r[0] and r[2]==2 and not r[3], f"보스가 열려 있고 기회가 있으면 점 3 · 다음 보스 {r}")
        g0=await pg.evaluate("()=>Wallet.gems()"); await pg.evaluate("()=>Course.add('b')"); await pg.wait_for_timeout(300)
        r=await txt(pg); g1=await pg.evaluate("()=>Wallet.gems()")
        ok(r and r[2]==3 and r[3] and g1-g0==0, f"보스까지 하면 완주 표시 · 보너스는 하루 한 번이라 이미 받았으면 또 안 줌 {r} {g0}→{g1}")
        # 다음 날
        await pg.evaluate("()=>{ const s=Course.load(); s.day='2000-01-01'; Course.save(); Course.s=null; DM.paint(); }")
        r=await txt(pg); ok(r and r[2]==0 and not r[3], f"날이 바뀌면 처음으로 {r}")
        # 화면 크기
        for (w,h) in [(360,640),(390,844),(820,1180),(1180,820),(844,390)]:
            await pg.set_viewport_size({"width":w,"height":h}); await pg.wait_for_timeout(300)
            m=await pg.evaluate("()=>{ const b=document.getElementById('crsBtn').getBoundingClientRect(), s=document.getElementById('scStart'); const last=[...document.querySelectorAll('#scStart .menu > *')].filter(e=>e.getBoundingClientRect().height>0).pop().getBoundingClientRect(); return {bw:Math.round(b.width), bh:Math.round(b.height), over:document.documentElement.scrollWidth>innerWidth+1, lastBottom:Math.round(last.bottom), H:innerHeight, scroll:s.scrollHeight>s.clientHeight+2}; }")
            print(f"  {w}x{h}", m)
            ok(not m["over"] and m["bw"]>150 and m["bh"]>=36, f"{w}x{h} 가로 넘침 없음 · 버튼 {m['bw']}x{m['bh']}")
            await pg.screenshot(path=OUT+f"crs_{w}x{h}.png")
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:2]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 "+str(bad))
asyncio.run(main())
