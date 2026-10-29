"""(v459) 사용자 캡처: 선생님 관리 「어제 한 아이」에 김지후가 두 줄 (자기 패드 = 기기 번호 · 선생님 패드에서 고름 = 명단 번호)
  → 같은 이름(👤 떼고·소문자)은 한 줄로 합침: 판·분·정답 수는 더하고 최고 점수는 큰 것 · 반은 아는 반 · 마지막 시각은 늦은 것"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 430, "height": 900})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate("()=>FB.set('/hy/roster', {t:{g:{n:'고학년', e:'🐸'}}, k:{k9:{n:'김지후',t:'g'}}}).then(()=>HyBoss.refresh(true))")
        r = await K.evaluate("""()=>{ const D={dlx48:{n:'김지후', t:'zz', r:3, rr:50, rw:6, rs:240, b:9954, bs:29, s:7, la:1000, lk:'r'}, k9:{n:'👤김지후', t:'g', s:1, so:28, sw:2, la:2000, lk:'s'}, dvb:{n:'빈', r:1, rr:10, rw:1, b:5776, bs:20, la:500}};
            const L=HyDay.merge(D), j=L.find(x=>x.n.indexOf('지후')>=0); HyDay.D['2026-10-29']=D; HyDay.day='2026-10-29'; const h=HyDay.card(), rows=(h.match(/<tr>/g)||[]).length-1;
            return [L.length, j.r, j.s, j.b, j.bs, j.rr, j.t, j.la, j.lk, j.ks.length, rows, /고학년/.test(h), (h.match(/김지후/g)||[]).length]; }""")
        ok(r[0] == 2 and r[1] == 3 and r[2] == 8 and r[3] == 9954 and r[4] == 29 and r[5] == 50 and r[6] == "g" and r[7] == 2000 and r[8] == "s" and r[9] == 2, f"김지후 두 칸 → 한 줄 (달리기 3 · 공부 1+7 · 최고 9,954 · 반 = 🐸 고학년 · 마지막 = 늦은 것) {r}")
        ok(r[10] == 2 and r[11] and r[12] == 1, f"카드 = 2줄 (김지후 1 · 빈 1) · 반 이름 고학년 {r[10:]}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
