"""(v696) 🕰 하루 리듬 — claude/hy-eng-plan-town-study.md 3번
   ① 🍾 병 편지 하루 1통: 등대 모래섬 · 빈 칸 · 열면 영어 한 문장 + 한글 + 선물(씨앗·과일) · 다시는 안 나옴
   ② ✨ 반짝 땅 3곳: 서로 떨어짐 · 빈 칸 · 파면 재료 · 셋 + 병 = 「✅ 오늘 섬 한 바퀴」 도장
   ③ 밤(HY_HOUR=23): 가게·은행 이름표 🌙 · 누르면 「문을 닫았어요」(가게 창 안 열림) · 이웃 💤 · 안 걸음 · ❗ 없음 · 📱 소식 = 밤
   ④ 아침(HY_HOUR=9): 다시 열림 · 이웃 걸음"""
import asyncio, sys, os
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
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":390,"height":844}, has_touch=True); pg=await ctx.new_page(); pg.set_default_timeout(150000)
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await ctx.add_init_script("window.HY_HOUR=10;")
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("""()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k));
            localStorage.setItem('hyeng_proto_code', JSON.stringify('QD697')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_dev','dQD697'); localStorage.setItem('hyeng_me', JSON.stringify({id:'kQD697', t:'A568'})); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }""")
        await pg.reload(); await pg.wait_for_timeout(2000)
        await pg.evaluate("()=>ISLE.enter()")
        for _ in range(200):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        E=pg.evaluate
        # ① 병 편지
        r=await E("""()=>{ const b=DAYR.B(), M=ISLE_MAP.isles.find(q=>q.k==='beach'); if(!b) return null; const x=b.p[0], z=b.p[2]; return [+Math.hypot(x-ISLE.OX-M.cx, z-ISLE.OZ-M.cz).toFixed(1), M.R, ISLE.blocked(Math.floor(x),Math.floor(z)), LBL.some(l=>l.d.k==='dy_bottle')]; }""")
        ok(r and r[0]<r[1] and not r[2] and r[3], f"① 🍾 병 = 등대 모래섬 안 · 빈 칸 · 이름표 {r}")
        m0=await E("()=>JSON.stringify(mats)")
        await E("()=>DAYR.openBottle()"); await pg.wait_for_timeout(600)
        r=await E("()=>[document.getElementById('dyLt').classList.contains('on'), document.querySelector('#dyLt .en').textContent, document.querySelector('#dyLt .ko').textContent, document.querySelector('#dyLt .gf').textContent, DAYR.st().bottle, !!DAYR.B(), LBL.some(l=>l.d.k==='dy_bottle')]")
        ok(r[0] and len(r[1])>8 and r[2] and "🎁" in r[3] and r[4]==1 and not r[5] and not r[6], f"① 편지 = 영어 + 한글 + 선물 · 병 사라짐 {r[1]} / {r[3]}")
        m1=await E("()=>JSON.stringify(mats)")
        ok(m0!=m1, "① 선물이 가방에")
        await pg.screenshot(path=OUT+"day697_letter.png")
        await E("()=>document.querySelector('#dyLt [data-x]').click()")
        # ② 반짝 땅
        r=await E("""()=>{ const D=DAYR.DG(); let mn=1e9; for(let i=0;i<D.length;i++) for(let j=i+1;j<D.length;j++) mn=Math.min(mn, Math.hypot(D[i].p[0]-D[j].p[0], D[i].p[2]-D[j].p[2])); return [D.length, +mn.toFixed(1), D.every(d=>!ISLE.blocked(Math.floor(d.p[0]),Math.floor(d.p[2]))), LBL.filter(l=>/^dy_dig/.test(l.d.k)).length]; }""")
        ok(r[0]==3 and r[1]>=9 and r[2] and r[3]==3, f"② ✨ 반짝 땅 3곳 (서로 {r[1]}) · 이름표 {r}")
        for i in range(3):
            await E("()=>{ const d=DAYR.DG()[0]; TFAC.warp(d.p[0]+.6, d.p[2]+.6); }"); await pg.wait_for_timeout(700)
            await E("()=>{ const L=LBL.find(l=>/^dy_dig/.test(l.d.k)); if(L) L.d.act(); }"); await pg.wait_for_timeout(900)
        r=await E("()=>[Object.keys(DAYR.st().dig).length, DAYR.DG().length, DAYR.st().done]")
        ok(r==[3,0,1], f"② 3곳 다 팜 → ✅ 오늘 섬 한 바퀴 {r}")
        await pg.wait_for_timeout(1200)
        t=await E("()=>document.getElementById('toast').textContent")
        ok("섬 한 바퀴" in t, f"② 도장 알림 {t[:40]}")
        # ③ 밤
        await E("()=>{ window.HY_HOUR=23; drawLabels(); for(let i=0;i<5;i++) VIL.tick(.1); }"); await pg.wait_for_timeout(400)
        r=await E("""()=>{ const sh=LBL.filter(l=>DAYR.CLOSE.has(l.d.k)); const nb=LBL.filter(l=>/^v_(tom|lily|sam|joe)$/.test(l.d.k)); return [sh.length, sh.every(l=>/🌙/.test(l.d.t)), nb.length, nb.every(l=>/💤/.test(l.d.t)), VIL.W().every(w=>!w.c.g.visible), VIL.nbList().filter(x=>x.bang).length]; }""")
        ok(r[0]>=5 and r[1] and r[2]==4 and r[3] and r[4] and r[5]==0, f"③ 밤: 가게 🌙 · 이웃 💤 · 안 보임 · ❗ 없음 {r}")
        await E("()=>{ const L=LBL.find(l=>l.d.k==='mart'); L.d.act(); }"); await pg.wait_for_timeout(500)
        r=await E("()=>[document.getElementById('toast').textContent, document.querySelector('.sheet.on') ? document.querySelector('.sheet.on').id : '']")
        ok("닫았어요" in r[0] and not r[1], f"③ 마트 누르면 닫힘 안내 · 창 안 열림 {r[0][:30]}")
        await E("()=>VIL.talkNb('tom')"); await pg.wait_for_timeout(500)
        r=await E("()=>[document.getElementById('dlg').classList.contains('on'), document.getElementById('toast').textContent]")
        ok(not r[0] and "자고" in r[1], f"③ 📱 이웃 앱에서 가도 잠 {r[1][:30]}")
        await E("()=>document.getElementById('ihMenu').click()"); await pg.wait_for_timeout(400)
        r=await E("()=>document.getElementById('ihNw').innerText")
        ok("night" in r.lower(), f"③ 📱 소식 = 밤 {r[:50]}")
        await pg.screenshot(path=OUT+"day697_night.png")
        await E("()=>document.getElementById('ihM').classList.remove('on')")
        # ④ 아침
        await E("()=>{ window.HY_HOUR=9; drawLabels(); for(let i=0;i<5;i++) VIL.tick(.1); }"); await pg.wait_for_timeout(300)
        await E("()=>{ const w=VIL.W()[0]; TFAC.warp(w.c.g.position.x+2, w.c.g.position.z+2); }"); await pg.wait_for_timeout(800)
        r=await E("()=>{ for(let i=0;i<5;i++) VIL.tick(.1); return [LBL.filter(l=>DAYR.CLOSE.has(l.d.k)).every(l=>!/🌙/.test(l.d.t)), VIL.W().every(w=>w.c.g.visible)]; }")
        ok(r==[True,True], f"④ 아침: 가게 열림 · 이웃 걸음 {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
