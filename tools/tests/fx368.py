"""(v368) 사용자: 아이폰 13 Pro 에서 달리기가 약간씩 툭툭 끊김
  원인: ① 먼지·바람·조각마다 새 모양·재질을 만들고 지움(GC) ② 마지막 재질이 지워지면 셰이더까지 지워져 다음 효과 때 다시 컴파일
        ③ 문이 나올 때마다 단어판(900×470)을 새 텍스처로 GPU 에 올림
  → 효과 조각은 모아 두었다 다시 씀 · 모양은 같이 씀 · 셰이더는 지우지 않음 · 판 시작 때 미리 컴파일
  → 같은 단어판 텍스처는 같이 씀(쓰는 문 수를 셈) · 다음 문제 단어판은 쉬는 틈에 미리 올림"""
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
        # ① 효과 조각 — 다 쓴 것은 다시 씀 · 모양은 하나
        r = await pg.evaluate("""()=>{ const g0=THREE.__geoDisposed||0, m0=THREE.__matDisposed||0;
            for(let k=0;k<3;k++){ for(let i=0;i<6;i++){ puff(0,0,0,0xffffff,5); burst(0,0,0,0xff0000,4); } updateFx(0.01); updateFx(2); }
            const made1=FxPool.made;
            for(let k=0;k<5;k++){ for(let i=0;i<6;i++){ puff(0,0,0,0xffffff,5); burst(0,0,0,0xff0000,4); } updateFx(0.01); updateFx(2); }
            return {made1, made2:FxPool.made, free:FxPool.free.length, fx:fx.length, geo:(THREE.__geoDisposed||0)-g0, mat:(THREE.__matDisposed||0)-m0,
              same: FxPool.box(.12,.12,.12)===FxPool.box(.12,.12,.12)}; }""")
        print("fx", r)
        ok(r["made2"] == r["made1"] and r["made1"] <= 60 and r["fx"] == 0, f"효과 조각을 다시 씀 (새로 만들지 않음) {r}")
        ok(r["geo"] == 0 and r["mat"] == 0 and r["same"], "효과가 끝나도 모양·재질을 지우지 않음 (셰이더 다시 컴파일 없음)")
        # ② 셰이더 프로그램은 지우지 않음
        r = await pg.evaluate("""()=>{ const P=renderer.info.programs; P.push({usedTimes:1}, {usedTimes:3}); GLWarm.keep(); GLWarm.keep(); return P.slice(-2).map(q=>q.usedTimes); }""")
        ok(r == [2, 4], f"셰이더 프로그램 붙잡아 두기 (한 번만) {r}")
        # ③ 단어판 텍스처 같이 쓰기
        r = await pg.evaluate("""()=>{ const t0=THREE.__texDisposed||0; const a=signTexture('apple'), b=signTexture('apple'), c=signTexture('banana');
            const same=a===b, diff=a!==c; a.dispose(); const alive1=!a._dead; b.dispose(); const alive2=!a._dead;
            return {same, diff, alive1, alive2, ref:a._ref, disposed:(THREE.__texDisposed||0)-t0}; }""")
        ok(r["same"] and r["diff"] and r["alive1"] and r["alive2"] and r["ref"] == 0 and r["disposed"] == 0, f"같은 단어판은 텍스처 하나 · 쓰는 문이 없어도 캐시에 있으면 남김 {r}")
        r = await pg.evaluate("""()=>{ const t0=THREE.__texDisposed||0; const a=signTexture('zz0'); for(let i=1;i<=SignCache.MAX+2;i++) signTexture('zz'+i).dispose();
            const held=!a._dead; a.dispose(); return {held, dead:a._dead, n:(THREE.__texDisposed||0)-t0}; }""")
        ok(r["held"] and r["dead"] and r["n"] >= 3, f"캐시에서 밀려나면 · 쓰는 문이 다 없어지면 그때 지움 {r}")
        r = await pg.evaluate("""()=>{ const c=[]; const f=renderer.initTexture; renderer.initTexture=t=>c.push(t); G.running=true; signTexWarm('cherry'); renderer.initTexture=f; G.running=false;
            const t=signTexture('cherry'); return [c.length, c[0]===t]; }""")
        ok(r == [1, True], f"다음 문제 단어판은 미리 GPU 에 올림 · 문이 나오면 그 텍스처 그대로 {r}")
        # ④ 판 — 시작(미리 컴파일) · 문 여러 개 · 끝까지 오류 없음
        await pg.evaluate("()=>{ window._cmp=0; const f=renderer.compile.bind(renderer); renderer.compile=(a,b)=>{ _cmp++; return f(a,b); }; G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.evaluate("()=>setInterval(()=>{ try{ const s=G.sets.find(s=>!s.judged); if(s&&s.q){ const g=s.gates.find(g=>g.lane===s.q.answer); if(g) P.x=g.root.position.x; } }catch(e){} }, 50)")
        await pg.wait_for_timeout(9000)
        r = await pg.evaluate("()=>[window._cmp, G.running, G.stage, G.sets.length, G.sets.every(s=>s.gates.every(g=>g.tex && !g.tex._dead))]")
        print("run", r)
        ok(r[0] >= 1 and r[1] and r[2] >= 2 and r[4], f"판 시작에 미리 컴파일 · 문을 지나도 단어판 텍스처 살아 있음 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
