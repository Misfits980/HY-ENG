"""(v263) 오늘의 30 정답률 — 중간에 그만둘 때도 처음에 틀린 문제를 세는지 · 이어 하기 뒤에도 그대로인지"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *


async def solve_until(pg, n_first, wrong_at):
    """처음 보는 문제를 n_first 개 풀 때까지 (wrong_at 번째는 틀리게)"""
    seen = 0
    for _ in range(300):
        st = await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return {t:q&&q.t, again:!!(q&&q.again), locked:U.locked, brk:!!U._brk} }")
        fresh = st['t'] and st['t'] != 'intro' and not st['again'] and not st['locked'] and not st['brk']
        if fresh and seen >= n_first: return
        await pg.evaluate(SOLVE, bool(fresh and seen in wrong_at))
        if fresh: seen += 1
        await pg.wait_for_timeout(450 if st['t'] == 'drag' else 20)

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("""()=>{ window._subs=[]; Online.on=()=>true; Online.submit=o=>window._subs.push(o);
          StudyUI.open(); StudyUI.book='g12'; StudyUI.set='basic'; StudyUI.path(); StudyUI.start(0,false); }""")
        await pg.wait_for_timeout(300)
        await solve_until(pg, 9, {0})                      # 처음 9문제: 1개 틀림 → 8/9
        a = await pg.evaluate("()=>({first:StudyUI.first, fw:StudyUI._fw, acc:StudyUI.acc1(), wrong:StudyUI.wrong, done:StudyUI.done})")
        print("before resume", a)
        StudyUI_ok = a['acc'] == round(8 / 9 * 100)
        # 이어 하기로 다시 불러와도 틀린 수가 남는지
        await pg.evaluate("()=>StudyUI.saveCur()")
        r = await pg.evaluate("()=>{ StudyUI.qs=[]; StudyUI._fw=0; const ok=StudyUI.resume(); return {ok, fw:StudyUI._fw, acc:StudyUI.acc1()} }")
        print("after resume", r)
        await pg.evaluate("()=>{ if(StudyUI.locked) document.getElementById('stCheck').click(); }")
        await pg.wait_for_timeout(100)
        await pg.evaluate("()=>document.getElementById('stQuit').click()")
        await pg.wait_for_timeout(200)
        subs = await pg.evaluate("()=>window._subs")
        print("sent", [(s['rule'], s['end'], s['acc'], s['right'], s['wrong']) for s in subs])
        ok = StudyUI_ok and r['ok'] and r['fw'] == a['fw'] and len(subs) == 1 and subs[0]['end'] == 'quit' and subs[0]['acc'] == a['acc'] < 100
        # 끝까지 푼 판은 예전과 같은 값 (한 번에 맞힘 = first/total)
        await pg.evaluate("()=>{ window._subs=[]; StudyUI.start(1,false); }"); await pg.wait_for_timeout(200)
        for _ in range(400):
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
            st = await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q&&q.t }")
            await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(450 if st == 'drag' else 20)
        f = await pg.evaluate("()=>({acc:StudyUI.acc1(), old:Math.round(StudyUI.first/Math.max(1,StudyUI.total)*100), subs:window._subs.map(s=>[s.end,s.acc])})")
        print("full stage", f)
        ok = ok and f['acc'] == f['old'] == 100 and f['subs'] and f['subs'][0] == ['clear', 100]
        e = real_errs(errs)
        print("errs", e)
        if not ok: print("BAD accuracy")
        await br.close()
asyncio.run(main())
