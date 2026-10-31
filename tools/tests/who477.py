"""(v477) 사용자: "개인 패드에서 이미 설정에서 자기 이름을 했는데 Daily 30 을 해도 불가 · 이름을 잘못 설정해서 다른 아이 기록으로 됨 · 공용 패드 때문에 문제가 더 생긴 것 같고 연계를 안 고쳐서"
  ① 설정 이름과 명단 이름이 띄어쓰기·👤만 달라도 저절로 연결 (「김 지후」 = 「김지후」)
  ② 이름만 쓴 아이(「지후」) → 이름 고르기 창 맨 위 「🙋 혹시 이 이름? 김지후」
  ③ 개인 패드에서 설정 이름과 다른 아이(「박유범」)를 누르면 「정말 나예요?」 한 번 더 → 「다시 고르기」/「네」
  ④ 이름이 없을 때 한 Daily 30·달리기 = 미뤄 둠 → 이름을 고르면 공격 기회로 (이번 주만)
  ⑤ 개인 패드 Daily 30 을 열 때 이름이 명단과 안 맞으면 하루 한 번 이름 고르기
  ⑥ 개인 패드 이름을 「한양…」「…패드」(공용 패드 이름)로 못 바꿈"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 430, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        R = """(nick)=>{ localStorage.setItem('hyeng_nick', nick); localStorage.removeItem('hyeng_kid'); localStorage.removeItem('hyeng_teacher_dev'); localStorage.removeItem('hyeng_boss_pend'); localStorage.removeItem('hyeng_kp_ask'); localStorage.removeItem('hyeng_me');
            HyBoss.R=Object.assign(HyBoss.R||{}, {t:{a:{n:'초원', e:'🌱'}}, k:{k1:{n:'박유범', t:'a'}, k2:{n:'김지후', t:'a'}, k3:{n:'👤이서연', t:'a'}}}); HyBoss.refresh=()=>Promise.resolve(); }"""
        # ① (v478: 개인 기기는 저절로 묶임 — 이름 맞추기 규칙은 그대로)
        await E(R, "김 지후"); r = await E("()=>{ HyBoss.ok=true; localStorage.removeItem('hyeng_me'); const m=Kid.me(); return m && [m.id, m.n]; }")
        ok(r == ["k2", "김 지후"], f"① 「김 지후」 → 명단 김지후 저절로 {r}")
        await E(R, "이서연"); r = await E("()=>{ localStorage.removeItem('hyeng_me'); const m=Kid.me(); return m && m.id; }")
        ok(r == "k3", f"① 「이서연」 → 명단 「👤이서연」 저절로 {r}")
        # ② ③ 설정에서 「명단에 내 이름이 따로 있어요」로 열 때(bind)
        await E(R, "지후"); r = await E("()=>Kid.guess()"); ok(r == ["k2"], f"② 「지후」 후보 김지후 {r}")
        await E("()=>KidPick.open(()=>{}, {bind:true})"); await pg.wait_for_timeout(200)
        r = await E("()=>{ const g=document.querySelector('#kidPick .kpGuess'); return g && [g.innerText.replace(/\\s+/g,' '), [...g.querySelectorAll('[data-kp]')].map(b=>b.dataset.kp)]; }")
        ok(r and "혹시 이 이름" in r[0] and r[1] == ["k2"], f"② 이름 고르기 맨 위 「혹시 이 이름? 김지후」 {r}")
        await E("()=>document.querySelector('#kidPick .kpL [data-kp=\"k1\"]:not(.kpGuess *)').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>document.querySelector('#kidPick').innerText.replace(/\\s+/g,' ')")
        ok("박유범" in r and "정말 나예요" in r, f"③ 다른 아이 → 「정말 나예요?」 {r[:80]}")
        await E("()=>document.querySelector('#kidPick [data-kpback]').click()"); await pg.wait_for_timeout(200)
        ok(await E("()=>!!document.querySelector('#kidPick .kpL')"), "③ 「다시 고르기」 → 명단으로")
        await E("()=>KidPick.close()")
        # ④ 공용 패드는 미루지 않음 (미룬 것 쌓기는 who478 ⑤)
        r = await E("()=>{ localStorage.removeItem('hyeng_boss_pend'); localStorage.setItem('hyeng_nick','한양패드1'); HyBoss.pendAdd('s', 10, 10); const n=HyBoss.pendN(); localStorage.setItem('hyeng_nick','지후'); return n; }")
        ok(r == 0, f"④ 공용 패드는 미루지 않음 (따로 흐름) {r}")
        # ⑥
        await E("()=>localStorage.setItem('hyeng_nick','지후')")
        r = await E("()=>[NameCard.change('한양이', false), NameCard.change('내패드', false), localStorage.getItem('hyeng_nick')]")
        ok("공용 패드 이름" in r[0] and "공용 패드 이름" in r[1] and r[2] == "지후", f"⑥ 「한양…」「…패드」로 못 바꿈 {r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
