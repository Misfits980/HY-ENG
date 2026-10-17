"""(v315) 🧪 이번 주만 테스트 슬라임 — 관리 버튼 · 체력 300 · 공격 기회 이어짐 · 잡기 · 보상 · 다음 주는 원래 보스 · 끄면 원래대로"""
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
        await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'},k2:{n:'서연'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }""")
        await pg.wait_for_timeout(500)
        # 원래 보스에서 기회 모으기 + 조금 깎기
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드'); Kid.set({id:'k1',n:'민준',t:'all'}); G.char='knight'; HyBoss.earn(Kid.get(),'study',6); HyBoss.earn(Kid.get(),'run',4); HyBoss.add(Kid.get(), 40, 'study'); }")
        await pg.wait_for_timeout(300)
        b0 = await pg.evaluate("()=>({id:HyBoss.B.id, i:HyBoss.B.i, n:HyBoss.B.n, st:HyBoss.stock('k1'), hp:HyBoss.state('all').hp})")
        print("before", b0)
        # 관리 화면 — 🧪 버튼 누르기
        await pg.evaluate("()=>{ window.confirm=()=>true; Admin.open ? Admin.open() : null; }")
        await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>HyBoss.testWeek(true).then(()=>({id:HyBoss.B.id, test:HyBoss.B.test, n:HyBoss.B.n, img:HyBoss.B.img, max:HyBoss.B.max, nx:HyBoss.nextOf().n, line:HyBoss.lineOf().atk[0]}))")
        print("test on", r)
        ok(r['test'] and r['img'] == 'hbS' and r['max'].get('all') == 300, "테스트 슬라임 · 체력 300")
        ok(r['nx'] == b0['n'], f"다음 주 = 원래 이번 주 보스 ({r['nx']})")
        ok(r['line'] == "말랑 몸통 박치기", "공격 이름 = 슬라임")
        await pg.wait_for_timeout(500)
        st = await pg.evaluate("()=>HyBoss.stock('k1')")
        ok(st == b0['st'], f"공격 기회 이어짐 {st} == {b0['st']}")
        nxtw = await pg.evaluate("()=>{ const wk=HyBoss.B.wk, nw=HyBoss.dayOf(HyBoss.kd(wk)+7*864e5); return [HyBoss.idxOf(nw), HyBoss.B.i]; }")
        ok(nxtw[0] == nxtw[1], f"다음 주 보스 번호 {nxtw}")
        # 첫 화면 알림 · 보스 화면
        await pg.evaluate("()=>show('scStart')"); await pg.wait_for_timeout(500)
        ban = await pg.evaluate("()=>document.getElementById('hbBan').innerText"); print("banner", ban.replace("\n", " / "))
        ok("슬라임" in ban, "첫 화면 알림에 슬라임")
        await pg.evaluate("()=>WeekBoss.open()"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=OUT + "slime_view.png")
        v = await pg.evaluate("()=>document.getElementById('wbView').innerText")
        ok("슬라임" in v and "300" in v, "보스 화면에 슬라임 · 체력 300")
        # 휘둘러서 잡기 (기회를 넉넉히)
        for i in range(60):
            if await pg.evaluate("()=>HyBoss.state('all').dead || !!document.getElementById('wbRes')"): break
            await pg.evaluate("()=>{ if(HyBoss.stock('k1').r+HyBoss.stock('k1').s<2) HyBoss.earn(Kid.get(),'study',5); if(WeekBoss.F){ WeekBoss.F.next=99; WeekBoss.F.lock=0; } WeekBoss.swing(); }")
            await pg.wait_for_timeout(180)
            if i == 3: await pg.screenshot(path=OUT + "slime_fight.png")
        await pg.wait_for_selector("#wbRes", timeout=6000); await pg.wait_for_timeout(1300); await pg.screenshot(path=OUT + "slime_dead.png")
        rs = await pg.evaluate("()=>document.getElementById('wbRes').innerText"); print("result", rs.replace("\n", " / "))
        ok("쓰러뜨렸어요" in rs and b0['n'] in rs, "쓰러뜨림 + 다음 주 원래 보스 안내")
        g = await pg.evaluate("()=>HyBoss.reward(Kid.get())")
        ok(g == 10, f"보상 💎{g} (혼자 깎음 = 10)")
        # 관리 화면 줄
        await pg.evaluate("()=>{ const r=document.getElementById('wbRes'); if(r) r.remove(); WeekBoss.close && WeekBoss.close(); }")
        # 끄기 → 원래 보스, 원래 데미지 그대로
        r2 = await pg.evaluate("()=>HyBoss.testWeek(false).then(()=>({id:HyBoss.B.id, test:HyBoss.B.test, n:HyBoss.B.n, hp:HyBoss.state('all').hp, st:HyBoss.stock('k1')}))")
        print("test off", r2)
        ok(not r2['test'] and r2['id'] == b0['id'] and r2['hp'] == b0['hp'], "끄면 원래 보스 · 원래 체력")
        nx2 = await pg.evaluate("()=>{ const wk=HyBoss.B.wk, nw=HyBoss.dayOf(HyBoss.kd(wk)+7*864e5); return [HyBoss.idxOf(nw), HyBoss.B.i+1]; }")
        ok(nx2[0] == nx2[1], f"끄면 다음 주는 다시 차례대로 {nx2}")
        # 다시 켜면 새 칸 (앞 테스트 처치 기록과 섞이지 않음)
        r3 = await pg.evaluate("()=>HyBoss.testWeek(true).then(()=>({id:HyBoss.B.id, dead:!!HyBoss.state('all').dead, hp:HyBoss.state('all').hp}))")
        ok(r3['id'] != r['id'] and not r3['dead'] and r3['hp'] == 300, f"다시 켜면 새 테스트 {r3}")
        ok(not errs, "페이지 오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
