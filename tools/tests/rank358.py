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
        # (v363) 같은 이름(자기 기기 번호 + 명단 이름)은 한 줄로 합침
        await pg.evaluate("""()=>{ const D={k1:{n:'김지후', d:833, on:{}}, dvx:{n:'김지후', d:521, on:{}}, k2:{n:'스트로베리', d:1378, on:{}}, dvy:{n:'👤스트로베리', d:295, on:{}}, k3:{n:'빈', d:100, on:{}}};
            return FB.set('/hy/dmg/'+HyBoss.B.id, D).then(()=>HyBoss.refresh(true)); }""")
        await pg.evaluate("()=>{ WeekBoss._rkAll=true; localStorage.setItem('hyeng_nick','한양패드'); /* (v478) 고르기 = 공용 패드 */ Kid.set({id:'dvx', n:'김지후', t:'all'}); WeekBoss.draw(); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#wbTop5 .wbRank li')].map(li=>li.querySelector('span').textContent+'|'+li.querySelector('em').textContent.replace(/\\D/g,'')+(li.classList.contains('me')?'*':''))")
        ok(r == ["스트로베리|1673", "김지후|1354*", "빈|100"], f"같은 이름은 한 줄 · 공격 합침 · 내 줄 {r}")
        # (v363) 보상 자격(3번 이상 휘두름)도 같은 이름 합쳐서 · 받음 표시는 한 번만
        r = await pg.evaluate("""()=>{ const s0=HyBoss.stateOf, B={id:'wtest', gems:500, split:'eq', team:false};
            HyBoss.stateOf=()=>({dead:true, sum:1000, max:1000});
            const D={a1:{n:'김지후', d:40, sw:2}, a2:{n:'👤김지후', d:30, sw:2}, b1:{n:'빈', d:50, sw:3}, c1:{n:'서연', d:20, sw:2}};
            const one=HyBoss.swOk(B, D.a1), merged=HyBoss.swOk(B, HyBoss.group(D, 'a1', '김지후'));
            const g=HyBoss.rewardOf(B, D, 'a1', {id:'a1', n:'김지후'}), gc=HyBoss.rewardOf(B, D, 'c1', {id:'c1', n:'서연'});
            HyBoss.stateOf=s0; return [one, merged, g, gc]; }""")
        ok(r == [False, True, 250, 0], f"번호 하나로는 2번이지만 합치면 4번 → 보상 · 나눔은 이름당 한 명(김지후·빈 = 500÷2) · 서연(2번)은 없음 {r}")
        r = await pg.evaluate("""()=>{ const s0=HyBoss.stateOf, B={id:'wtest', gems:500, split:'eq', team:false}; HyBoss.stateOf=()=>({dead:true, sum:1000, max:1000});
            const D={a1:{n:'김지후', d:40, sw:2}, a2:{n:'👤김지후', d:30, sw:2}};
            const p1={id:'a2', n:'김지후'}, g1=HyBoss.can(B, D, p1); Wallet.pay(HyBoss.key(B, p1)); HyBoss.markC(B, D, p1); D.a1.c=1;
            const g2=HyBoss.can(B, D, {id:'a1', n:'김지후'}); HyBoss.stateOf=s0; return [g1>0, g2, !!D.a1.c, !!D.a2.c]; }""")
        ok(r == [True, 0, True, True], f"한 번호로 받으면 다른 번호로는 못 받음 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
