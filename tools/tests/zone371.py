"""(v371) 아이폰 측정 보고서(v370): 사막 들어갈 때(11단계) 판정 27ms(문 만들기 19ms) + 그리기 44ms
  원인: 다음 문제 단어판을 옛 지대 그림으로만 미리 그려 두어서, 새 지대에 들어서면 그 자리에서 다시 그리고 올림
  → 맞히면 지대가 바뀌는 문제는 새 지대 단어판으로도 쉬는 틈에 미리 그려 올림 · 들어설 때 새로 그리지 않음"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(1200)
        r = await pg.evaluate("""()=>{ const zi=ZONES.findIndex(z=>zoneArt(z)==='desert'); const st=[...Array(200).keys()].find(n=>zoneIndex(n)===zi);
            const a=signArtFor(ZONES[zi]), a0=signArtFor(); G.stage=st-1; clearSets(); spawnSet(); return {zi, st, desert:a && a.key, now:a0 && a0.key, opts:G.nextQ.options.map(String)}; }""")
        print("setup", r)
        ok(r["desert"] and r["desert"] != r["now"], f"사막 단어판 그림이 따로 있음 {r['desert']}")
        await pg.wait_for_timeout(2500)
        r2 = await pg.evaluate("""(o)=>{ const keys=[...SignCache.m.keys()]; return o.opts.map(t=>[t, keys.some(k=>k===o.desert+'|'+t), keys.some(k=>k.indexOf('|'+t)>0 && !k.startsWith(o.desert))]); }""", r)
        ok(all(x[1] and x[2] for x in r2), f"다음 문제 단어판을 지금 지대·사막 둘 다 미리 그림 {r2}")
        # 맞혀서 사막으로 → 그 자리에서 단어판을 새로 그리지 않음
        r3 = await pg.evaluate("""()=>{ let n=0; const f=window.signCanvasArt, g=window.signCanvasPlain; window.signCanvasArt=function(){ n++; return f.apply(this, arguments); }; window.signCanvasPlain=function(){ n++; return g.apply(this, arguments); };
            const s=G.sets.find(s=>!s.judged); G.lane=s.q.answer; P.x=laneX(s.q.answer, G.lanes); judge(s); window.signCanvasArt=f; window.signCanvasPlain=g; return {n, zone:zoneArt(), stage:G.stage}; }""")
        ok(r3["zone"] == "desert" and r3["n"] == 0, f"사막에 들어서도 단어판을 새로 그리지 않음 {r3}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
