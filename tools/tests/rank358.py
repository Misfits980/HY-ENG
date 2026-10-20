"""(v358) 사용자: 주간 보스 화면 랭킹이 1~3등만 → 5등까지 + 내 자리(밖이면 ⋯ 뒤) + 「전체 순위 보기 (n명)」 펼치기/접기"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("""()=>{ const k={}; for(let i=1;i<=9;i++) k['k'+i]={n:'아이'+i}; return FB.set('/hy/roster',{t:{},k}).then(()=>HyBoss.setup({on:true,team:false,split:'eq',restart:true})).then(()=>HyBoss.refresh(true)); }""")
        await pg.evaluate("""()=>{ const D={}; for(let i=1;i<=9;i++) D['k'+i]={n:'아이'+i, d:(10-i)*100, on:{}}; return FB.set('/hy/dmg/'+HyBoss.B.id, D).then(()=>HyBoss.refresh(true)); }""")
        await pg.evaluate("()=>{ Kid.set({id:'k8', n:'아이8', t:'all'}); show('scStart'); WeekBoss.open(); }"); await pg.wait_for_timeout(700)
        R = "()=>[...document.querySelectorAll('#wbTop5 .wbRank li')].map(li=>li.classList.contains('wbGap')?'⋯':li.querySelector('span').textContent+(li.classList.contains('me')?'*':''))"
        r = await pg.evaluate(R)
        print(r)
        ok(r == ["아이1", "아이2", "아이3", "아이4", "아이5", "⋯", "아이8*"], f"5등까지 + ⋯ + 내 자리 {r}")
        b = await pg.evaluate("()=>{ const b=document.querySelector('[data-wbrk]'); return b && b.textContent; }")
        ok(b and "9명" in b, f"전체 순위 보기 버튼 {b}")
        await pg.screenshot(path=OUT + "rank358.png", full_page=True)
        await pg.evaluate("()=>document.querySelector('[data-wbrk]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate(R)
        ok(len(r) == 9 and "⋯" not in r and r[7] == "아이8*", f"펼치면 9명 전부 {r}")
        await pg.evaluate("()=>document.querySelector('[data-wbrk]').click()"); await pg.wait_for_timeout(300)
        ok(len(await pg.evaluate(R)) == 7, "다시 접힘")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
