"""(v317) 도감 — 연습 탭: 🔤 철자 · 📝 빈칸(그 단어의 여러 모양 고르기) · 🧩 문장 만들기 / 검색칸 ✕ 지우기 / cook 모양 이름표"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(400)
        await pg.evaluate("""async ()=>{ for(const b of [1,2,3]) DexData.load(b); loadEasy(); for(let i=0;i<60 && !(DexData.st[1]==='ok'&&DexData.st[2]==='ok'&&DexData.st[3]==='ok');i++) await new Promise(r=>setTimeout(r,100));
            ['cook','party','regret'].forEach(en=>{ Dex.add(en, true); }); }""")
        await pg.evaluate("()=>document.getElementById('btnDex').click()"); await pg.wait_for_timeout(600)
        # 검색칸 ✕
        await pg.evaluate("()=>{ document.querySelector('#dexMode [data-m=dic]').click(); }"); await pg.wait_for_timeout(200)
        await pg.fill("#dexQ", "party"); await pg.wait_for_timeout(200)
        vis = await pg.evaluate("()=>!document.getElementById('dexQx').hidden")
        await pg.screenshot(path=OUT + "dex_q.png")
        await pg.evaluate("()=>document.getElementById('dexQx').click()"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>[document.getElementById('dexQ').value, document.getElementById('dexQx').hidden]")
        ok(vis and r == ["", True], f"검색 ✕ 보임 {vis} → 지움 {r}")
        # cook 모양 이름표
        await pg.evaluate("()=>{ DexDet.tab='f'; DexDet.show('cook', true); }"); await pg.wait_for_timeout(500)
        labs = await pg.evaluate("()=>[...document.querySelectorAll('#dexDet .wPane.on .wForms .fx small')].map(e=>e.textContent)")
        print("cook", labs)
        ok("했어요 (과거)" in labs and "하는 중 (-ing)" in labs and "여러 개" not in labs[1:5], "cook 이름표 = 동사")
        await pg.screenshot(path=OUT + "dex_cook_forms.png")
        # 연습 — 빈칸
        await pg.evaluate("()=>{ DexDet.tab='p'; DexDet._qm='bl'; DexDet.show('cook', true); }"); await pg.wait_for_timeout(500)
        q = await pg.evaluate("()=>({m:DexDet._q && DexDet._q.mode, ans:DexDet._q && DexDet._q.ans, opts:[...document.querySelectorAll('#wQuiz [data-qb]')].map(b=>b.dataset.qb), s:(document.querySelector('#wQuiz .wQs')||{}).textContent})")
        print("blank", q)
        ok(q['m'] == "bl" and q['ans'] and len(q['opts']) >= 3 and "____" in q['s'], "📝 빈칸 문제")
        await pg.screenshot(path=OUT + "dex_blank.png")
        await pg.evaluate("()=>{ const a=DexDet._q.ans.toLowerCase(); [...document.querySelectorAll('#wQuiz [data-qb]')].find(b=>b.dataset.qb.toLowerCase()===a).click(); }"); await pg.wait_for_timeout(300)
        ok("정답" in await pg.evaluate("()=>document.querySelector('#wQuiz .wQm').textContent"), "빈칸 정답")
        # 연습 — 문장 만들기
        await pg.evaluate("()=>document.querySelector('#dexDet [data-qm=\"od\"]').click()"); await pg.wait_for_timeout(300)
        n = await pg.evaluate("()=>DexDet._q.L.length")
        for i in range(n):
            await pg.evaluate("()=>{ const Q=DexDet._q, want=Q.L[Q.got.length], j=Q.T.findIndex(t=>!t.u && t.c===want); document.querySelector('#wQuiz [data-qw=\"'+j+'\"]').click(); }"); await pg.wait_for_timeout(60)
            if i == 2: await pg.screenshot(path=OUT + "dex_order.png")
        ok("완성" in await pg.evaluate("()=>document.querySelector('#wQuiz .wQm').textContent"), f"🧩 문장 만들기 ({n}낱말)")
        await pg.evaluate("()=>document.querySelector('#dexDet [data-qm=\"sp\"]').click()"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>DexDet._q.mode==='sp' && !!document.querySelector('#wQuiz [data-qj]')"), "🔤 철자로 돌아감")
        # (v322) 📝 빈칸: 수 단서가 없으면 한 개·여러 개 짝을 보기에 안 냄 (I eat ___ every day: salad/salads) · 빈칸은 먼저 나오는 모양 (fried … frying pan)
        await pg.evaluate("()=>['salad','fry','eiffel tower','monday','found'].forEach(en=>Dex.add(en, true))")
        r = await pg.evaluate("""()=>{ const out=[]; DexDet.tab='p'; DexDet._qm='bl'; DexDet.show('salad', true);
            for(let k=0;k<6;k++){ DexDet.quizBl('salad', k); const Q=DexDet._q; out.push([Q.c.x[0], Q.ans, [...document.querySelectorAll('#wQuiz [data-qb]')].map(b=>b.dataset.qb.toLowerCase())]); } return out; }""")
        noCue = [x for x in r if x[0].startswith("I eat salad")]
        print("salad", noCue[:1], r[1][:2] if len(r) > 1 else "")
        ok(noCue and all("salads" not in x[2] and len(x[2]) >= 3 for x in noCue), "salad: 수 단서 없는 빈칸에 salads 보기 없음")
        ok(any(x[0].startswith("I made a salad") and "salads" in x[2] for x in r), "salad: 'a ___' 에는 salads 보기 있음")
        r = await pg.evaluate("""()=>{ DexDet.show('fry', true); for(let k=0;k<8;k++){ DexDet.quizBl('fry', k); const Q=DexDet._q; if(/frying pan/.test(Q.c.x[0])) return Q.ans; } return null; }""")
        ok(r == "fried", f"fry: 'We fried fish in a frying pan' 빈칸 = {r}")
        # (v322) 🔤 철자: 띄어쓰기는 미리 채운 칸 · 타일은 글자만 · 고유명사 대문자
        await pg.evaluate("()=>{ DexDet.tab='p'; DexDet._qm='sp'; DexDet.show('eiffel tower', true); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>({h:document.querySelector('#dexDet .wWord h3').textContent, tiles:[...document.querySelectorAll('#wQuiz [data-qj]')].map(b=>b.textContent), fix:document.querySelectorAll('#wQuiz .wQa i.fix').length})")
        print("eiffel", r)
        ok(r["h"] == "Eiffel Tower" and len(r["tiles"]) == 11 and all(t.strip() for t in r["tiles"]) and r["fix"] == 1, "eiffel tower: 제목 대문자 · 글자 타일 11개 · 띄어쓰기 칸")
        await pg.screenshot(path=OUT + "dex_sp_eiffel.png")
        n = await pg.evaluate("()=>DexDet._q.L.length")
        for i in range(n):
            await pg.evaluate("()=>{ const Q=DexDet._q, want=Q.L[Q.got.length], j=Q.T.findIndex(t=>!t.u && t.c===want); document.querySelector('#wQuiz [data-qj=\"'+j+'\"]').click(); }")
        ok("정답" in await pg.evaluate("()=>document.querySelector('#wQuiz .wQm').textContent"), "eiffel tower 철자 완성")
        await pg.evaluate("()=>{ document.getElementById('dexIn').classList.remove('det'); document.getElementById('dexQ').value='monday'; DexDet.drawList(); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#dexList .dRow b')].map(b=>b.textContent)")
        ok("Monday" in r, f"목록에 Monday 대문자 {r[:3]}")
        r = await pg.evaluate("()=>{ DexDet.tab='m'; DexDet.show('found', true); return document.querySelector('#dexDet .wKo').textContent; }")
        ok("찾았다" in r, f"found 도감 제목 뜻 = {r}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
