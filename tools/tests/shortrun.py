"""(v267) 초원(첫 지대)에서 끝난 짧은 판은 시트에 줄을 안 만들고, 다음 판의 '짧은 판' 칸에 수를 함께 보낸다"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

END = """(z)=>{ window._subs=window._subs||[]; Online.on=()=>true; Online.submit=o=>{ window._subs.push(o); return Promise.resolve({ok:true}); }; Online.top=()=>Promise.resolve(null);
  G.set='basic'; G.lesson=0; G.rule='normal'; G.diff='normal'; G.testRun=false; G.practice=false; G.cleared=false; G.quit=true;
  G.score=1200; G.stage=z?25:4; G.zone=z; G.right=5; G.wrong=1; G.running=false; G.skipOutro=true; G.overFade=false; G._overDone=false; gameOver(); G.skipOutro=false;
  return {subs:window._subs.length, short:localStorage.getItem('hyeng_short_v1')}; }"""

async def main():
    bad = []
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(300)
        a = await pg.evaluate(END, 0); print("초원 1", a)
        b = await pg.evaluate(END, 0); print("초원 2", b)
        await pg.wait_for_timeout(100)
        c = await pg.evaluate(END, 2); await pg.wait_for_timeout(200)
        subs = await pg.evaluate("()=>window._subs.map(s=>({zone:s.zone, short:s.short, stage:s.stage}))")
        left = await pg.evaluate("()=>localStorage.getItem('hyeng_short_v1')")
        print("다음 판", c, subs, "남은 수", left)
        if a["subs"] != 0 or b["short"] != "2": bad.append("초원 판을 보냄")
        if len(subs) != 1 or subs[0]["short"] != 2 or left != "0": bad.append("짧은 판 수")
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        if bad: print("BAD", bad)
        await br.close()
asyncio.run(main())
