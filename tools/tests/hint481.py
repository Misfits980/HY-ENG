"""(v481) Daily 30 점검: 「모르겠어요」= 바로 정답 → 💡 힌트 사다리
  ① 철자 문제 단추 = 「💡 힌트 · 한 글자」 → 누르면 맞는 글자 하나 더 (틀린 글자는 지움) · 소리
  ② 두 번째 = 「💡 힌트 · 절반까지」 → 절반까지 채움 · 마지막 한 글자는 남김
  ③ 세 번째 = 「🤔 모르겠어요 · 답 보기」 → 예전처럼 답 + 맨 마지막에 다시 (거기서는 힌트 다시 처음부터)
  ④ 힌트 쓰고 맞히면 = 도움 받아 맞힘 (콤보 안 오름 · 한 번에 맞힘 아님)"""
import asyncio, sys, os
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
        pg = await br.new_page(viewport={"width": 390, "height": 844}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        await E("()=>{ localStorage.setItem('hyeng_nick','한양패드1'); const s=Study.load(); s.book='g34'; s.set='elem'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(700)
        await E("()=>{ try{KidPick.close()}catch(e){}; StudyUI.start(0,false); }"); await pg.wait_for_timeout(400)
        PUT = """(en)=>{ const U=StudyUI; let k=U.i; while(U.qs[k] && U.qs[k].t==='intro') k++; U.i=k; const w=Study.word ? (Study.word(en)||U.qs[k].w) : U.qs[k].w;
            const q={t:'spell', w, tiles:shuffle(w.en.split('')), got:'', used:[], step:2}; U.qs.splice(k, 0, q); U.locked=false; U.show(); return [w.en, U.qs.length, k]; }"""
        en, n0, k0 = await E(PUT, "yesterday")
        await pg.wait_for_timeout(200)
        # 틀린 글자 하나 먼저
        await E("(en)=>{ const q=StudyUI.qs[StudyUI.i]; const k=q.tiles.findIndex(c=>c!==en[0]); document.querySelector('.stTile[data-t=\"'+k+'\"]').click(); }", en)
        r = await E("()=>document.getElementById('stIdk').innerText")
        ok("힌트" in r and "한 글자" in r, f"① 첫 단추 = 💡 힌트 · 한 글자 {r!r}")
        await E("()=>document.getElementById('stIdk').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>{ const q=StudyUI.qs[StudyUI.i]; return [q.got, q.hn, document.getElementById('stIdk').innerText, document.querySelectorAll('#stSlots .hn').length, StudyUI.locked]; }")
        ok(r[0] == en[:1] and r[1] == 1 and "절반" in r[2] and r[3] == 1 and r[4] is False, f"① 틀린 글자 지우고 맞는 글자 하나 · 다음 단추 = 절반까지 {r}")
        await E("()=>document.getElementById('stIdk').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>{ const q=StudyUI.qs[StudyUI.i]; return [q.got, q.hn, document.getElementById('stIdk').innerText]; }")
        half = -(-len(en)//2)
        ok(r[0] == en[:half] and r[1] == 2 and "모르겠어요" in r[2], f"② 절반까지({half}) · 다음 단추 = 모르겠어요 {r}")
        # ④ 나머지를 스스로 → 맞힘이지만 도움 받음
        r = await E("""(en)=>{ const U=StudyUI, q=U.qs[U.i], c0=U.combo, f0=U.first; for(let i=q.got.length;i<en.length;i++){ const k=q.tiles.findIndex((c,j)=>c===en[i] && q.used.indexOf(String(j))<0); document.querySelector('.stTile[data-t=\"'+k+'\"]').click(); }
            document.getElementById('stCheck').click(); return [U.combo-c0, U.first-f0, q.again, document.getElementById('stFoot').className]; }""", en)
        ok(r[0] == 0 and r[1] == 0 and r[2] is True and "good" in r[3], f"④ 힌트 쓰고 맞힘 = 맞음 · 콤보·한 번에 맞힘 아님 {r}")
        await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(300)
        # ③ 세 번 누르면 답 보기 + 맨 끝에 다시
        en2, n1, k1 = await E(PUT, "yesterday")
        await pg.wait_for_timeout(200)
        for _ in range(3): await E("()=>document.getElementById('stIdk').click()"); await pg.wait_for_timeout(150)
        r = await E("()=>{ const U=StudyUI, last=U.qs[U.qs.length-1]; return [U.locked, /맨 마지막/.test(document.getElementById('stFoot').innerText), last.idk, last.hn, last.got]; }")
        ok(r[0] is True and r[1] and r[2] == 1 and r[3] == 0 and r[4] == "", f"③ 세 번째 = 답 보기 · 맨 끝에 다시(힌트 처음부터) {r}")
        # 한 글자 남으면 힌트 대신 바로 답 보기 단추
        en3, n2, k2 = await E(PUT, "yesterday")
        await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(200)
        r = await E("""()=>{ const q=StudyUI.qs[StudyUI.i], en=q.w.en; for(let i=0;i<en.length-1;i++){ const k=q.tiles.findIndex((c,j)=>c===en[i] && q.used.indexOf(String(j))<0); document.querySelector('.stTile[data-t=\"'+k+'\"]').click(); } return document.getElementById('stIdk') && document.getElementById('stIdk').innerText; }""")
        ok(r and "모르겠어요" in r, f"한 글자만 남으면 힌트 없이 「모르겠어요」 {r!r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
