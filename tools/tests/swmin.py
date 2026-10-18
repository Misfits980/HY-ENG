"""(v323) 주간 보스 — 똑같이 나누기는 ⚔️ 3번 이상 휘두른 친구만 보상 (반격은 안 셈 · 예전 기록은 깎은 체력 ÷ 8 로 어림) · 깎은 만큼 나누기는 그대로"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'},k2:{n:'서연'},k3:{n:'지우'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }""")
        await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드'); HyBoss.CAP=1e9; }")
        # 민준 3번 · 서연 2번 + 반격 1번 · 지우 1번
        r = await pg.evaluate("""()=>{ const A={id:'k1',n:'민준',t:'all'}, B={id:'k2',n:'서연',t:'all'}, C={id:'k3',n:'지우',t:'all'};
            for(let i=0;i<3;i++) HyBoss.add(A, 10, 'study'); for(let i=0;i<2;i++) HyBoss.add(B, 10, 'study'); HyBoss.add(B, HyBoss.COUNTER, 'study', 0); HyBoss.add(C, 10, 'study');
            return [HyBoss.swOf(HyBoss.mine('k1')), HyBoss.swOf(HyBoss.mine('k2')), HyBoss.swOf(HyBoss.mine('k3'))]; }""")
        ok(r == [3, 2, 1], f"휘두른 수 (반격은 안 셈) {r}")
        # 쓰러뜨리기 (민준이 마지막 한 방)
        await pg.evaluate("()=>{ HyBoss.add({id:'k1',n:'민준',t:'all'}, HyBoss.state('all').hp, 'study'); }"); await pg.wait_for_timeout(300)
        g = await pg.evaluate("()=>HyBoss.refresh(true).then(()=>[!!HyBoss.state('all').dead, HyBoss.B.gems, HyBoss.rewardOf(HyBoss.B, HyBoss.D, 'k1', {id:'k1'}), HyBoss.rewardOf(HyBoss.B, HyBoss.D, 'k2', {id:'k2'}), HyBoss.rewardOf(HyBoss.B, HyBoss.D, 'k3', {id:'k3'})])")
        print("rewards", g)
        ok(g[0] and g[2] == g[1] and g[3] == 0 and g[4] == 0, f"3번 넘은 민준만 보상 전부 · 서연·지우 0 {g}")
        # 서연 화면 — 안내 글
        await pg.evaluate("()=>{ Kid.set({id:'k2',n:'서연',t:'all'}); show('scStudy'); StudyUI.path(); }"); await pg.wait_for_timeout(400)
        card = await pg.evaluate("()=>document.getElementById('stBossCard').innerText")
        ok("쓰러뜨림" in card and "보상 받기" not in card, "카드: 쓰러뜨림 · 보상 버튼 없음 — " + card.replace("\n", " / ")[:160])   # (v331) 자세한 안내는 보스 화면
        await pg.evaluate("()=>WeekBoss.open()"); await pg.wait_for_timeout(600)
        me = await pg.evaluate("()=>(document.getElementById('wbMe')||{}).innerText||''")
        ok("3번 이상" in me and "지금 2번" in me and "보상 받기" not in me, "보스 화면 안내: " + me.replace("\n", " / "))
        gd = await pg.evaluate("()=>document.querySelector('#wbView .wbGuide2') ? document.querySelector('#wbView .wbGuide2').innerText : ''")
        ok("3번 이상 휘두른 친구" in gd, "설명에 규칙")
        await pg.screenshot(path=OUT + "boss_swmin.png")
        # 예전 기록 (sw 칸 없음) — 깎은 체력 ÷ 8 로 어림 · 다음 휘두르기에 어림값을 같이 씀
        r = await pg.evaluate("""()=>{ const x={d:20}, y={d:24}; const a=[HyBoss.swOf(x), HyBoss.swOf(y), HyBoss.swOk(HyBoss.B, x), HyBoss.swOk(HyBoss.B, y), HyBoss.swOk({split:'prop'}, x)]; return a; }""")
        ok(r == [2, 3, False, True, True], f"예전 기록 어림 · 깎은 만큼 나누기는 그대로 {r}")
        # 깎은 만큼 나누기 — 1번만 휘둘러도 깎은 만큼
        await pg.evaluate("()=>HyBoss.setup({on:true, team:false, split:'prop', restart:true})"); await pg.wait_for_timeout(400)
        g = await pg.evaluate("""()=>{ const A={id:'k1',n:'민준',t:'all'}, C={id:'k3',n:'지우',t:'all'}; HyBoss.add(C, 100, 'study'); HyBoss.add(A, HyBoss.state('all').hp, 'study');
            return HyBoss.refresh(true).then(()=>[HyBoss.B.split, HyBoss.rewardOf(HyBoss.B, HyBoss.D, 'k3', {id:'k3'})]); }""")
        ok(g[0] == "prop" and g[1] > 0, f"깎은 만큼 — 1번도 보상 {g}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
