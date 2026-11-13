"""(v676) 선생님 PC 크롬(1280×593) 점검: 넓고 낮은 화면에서 한쪽만 채움 → 시안대로 두 칸
   ① 난이도 화면: 난이도 카드 왼쪽 | 문제 방법·「다음」 오른쪽 · 「다음」이 화면 안 (예전 430px 한 줄이라 화면 밖)
   ② 주간 보스: 보스·싸우기 왼쪽 | 나·순위·안내 오른쪽 · 순위가 화면 안 · 순위 칸 폭 = 오른쪽 칸 전체 · 싸우기 단추가 칸 전체
   ③ 패드(820×1180·1180×820)·휴대폰(390×844)·가로 폰(844×390)은 예전처럼 한 줄 · 순위 칸이 반쪽이 아님(예전 버그)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ROSTER = "(r)=>FB.set('/hy/roster', r).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true}))"
SETUP = """()=>{ const R=e=>e.getBoundingClientRect(), c=R(document.getElementById('selDiff')), m=R(document.getElementById('selMode')), n=R(document.getElementById('btnStepNext'));
  return {two: m.left>=c.right-1, nextIn: n.bottom<=innerHeight+1 && n.top>=0, cw:Math.round(c.width), nb:Math.round(n.bottom)}; }"""
BOSS = """()=>{ const R=e=>e.getBoundingClientRect(), st=R(document.getElementById('wbStage')), rk=R(document.getElementById('wbTop5')), col=R(document.querySelector('#wbView .wbCols')), sw=R(document.querySelector('#wbView .wbSwing')), fb=R(document.querySelector('#wbView .wbBtns'));
  return {two: rk.left>=st.right-1, rankIn: rk.top<innerHeight-40, rkFull: rk.width>=col.width-2, swFull: sw.width>=fb.width-2, rk:Math.round(rk.width), col:Math.round(col.width)}; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for vp, wide in (({"width": 1280, "height": 593}, True), ({"width": 1366, "height": 657}, True), ({"width": 820, "height": 1180}, False), ({"width": 1180, "height": 820}, False), ({"width": 390, "height": 844}, False), ({"width": 844, "height": 390}, False)):
            ctx = await br.new_context(viewport=vp); await ctx.add_init_script("window.HY_FB_LOCAL=true; localStorage.setItem('hyeng_nick','한양패드');")
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg); E = pg.evaluate
            tag = f"{vp['width']}×{vp['height']}"
            await E("()=>{ const a=document.getElementById('rkAnn'); if(a) a.remove(); Kid.confirm=(cb)=>cb(); document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(500)
            await E("()=>goStep(1)"); await pg.wait_for_timeout(500); r = await E(SETUP)
            if wide: ok(r["two"] and r["nextIn"], f"① {tag} 난이도 두 칸 · 「다음」 화면 안 {r}")
            else: ok(not r["two"], f"③ {tag} 난이도 예전처럼 한 줄 {r}")
            await E("()=>show('scStart')")
            await E("()=>HyBoss.live()"); await E(ROSTER, {"t": {}, "k": {"k1": {"n": "민준"}, "k2": {"n": "서연"}}}); await pg.wait_for_timeout(300)
            await E("()=>{ window.confirm=()=>true; Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',10); }")
            await E("()=>HyBoss.testWeek(true)"); await pg.wait_for_timeout(300); await E("()=>WeekBoss.open()"); await pg.wait_for_timeout(900)
            r = await E(BOSS)
            if wide: ok(r["two"] and r["rankIn"] and r["rkFull"] and r["swFull"], f"② {tag} 주간 보스 두 칸 · 순위 화면 안 · 순위·싸우기 칸 가득 {r}")
            else: ok(not r["two"] and r["rkFull"] and r["swFull"], f"③ {tag} 주간 보스 한 줄 · 순위·싸우기 칸 가득 {r}")
            if vp["width"] == 1280: await pg.screenshot(path=OUT + "wide676_boss.png")
            await ctx.close()
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
