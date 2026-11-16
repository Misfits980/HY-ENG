"""(v674) 사용자: PC 크롬으로 시험지를 인쇄하면 한 장 뽑히고 멈춤 → 「🪶 가벼운 PDF」 켜기·끄기 단추
   (v700) → 「🏫 학원 프린터용 | 🖨 보통」 두 가지 — 학원용 = 여백 넉넉(ppSafe) + 그림 PDF · 보통 = 예전 모양 + 브라우저 인쇄
   켜면 인쇄 = 쪽마다 그림 한 장인 PDF 를 만들어 → 「🖨 인쇄 창 열기」(새 탭) · 「💾 PDF 파일로 받기」 · 끄면 예전 브라우저 인쇄 · 기기에 기억"""
import asyncio, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1280, "height": 720}, accept_downloads=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg); E = pg.evaluate
        await pg.add_script_tag(path=os.path.join(SITE, "lib", "html2canvas.min.js"))   # 시험 도구는 lib/ 를 막아서 직접 붙임
        await E("()=>{ localStorage.removeItem('hyeng_paper'); localStorage.removeItem('hyeng_pp_light'); localStorage.removeItem('hyeng_pp_ver'); Paper.open({}); }"); await pg.wait_for_timeout(1200)
        r = await E("()=>[[...document.querySelectorAll('#paper .ppVer button.on')].map(b=>b.dataset.v), document.querySelector('#paper [data-pp=print]').textContent, Paper.pdfMode(), document.getElementById('paper').classList.contains('ppSafe')]")
        ok(r == [["normal"], "🖨 인쇄 / PDF 저장", False, False], f"처음(자동 시험) = 보통 · 브라우저 인쇄 {r}")
        p0 = await E("()=>{ const p=document.querySelector('#ppWrap .pp'); return getComputedStyle(p).paddingBottom; }")
        await E("()=>document.querySelector('#paper .ppVer [data-v=school]').click()"); await pg.wait_for_timeout(400)
        r = await E("()=>[[...document.querySelectorAll('#paper .ppVer button.on')].map(b=>b.dataset.v), document.querySelector('#paper [data-pp=print]').textContent, Paper.pdfMode(), localStorage.getItem('hyeng_pp_ver'), document.getElementById('paper').classList.contains('ppSafe'), getComputedStyle(document.querySelector('#ppWrap .pp')).paddingBottom]")
        ok(r[:5] == [["school"], "🏫 인쇄용 PDF 만들기", True, "school", True] and float(r[5][:-2]) > float(p0[:-2]) + 40, f"🏫 학원 프린터용 = 그림 PDF · 아래 여백 {p0} → {r[5]} · 기기에 기억 {r}")
        n = await E("()=>document.querySelectorAll('#ppWrap .pp').length")
        printed = await E("()=>{ window._pc=0; window.print=()=>{ window._pc++; }; document.querySelector('#paper [data-pp=print]').click(); return 1; }")
        for _ in range(60):
            if await E("()=>!!Paper._pdfF && !Paper._pdfBusy"): break
            await pg.wait_for_timeout(250)
        r = await E("()=>{ const o=document.getElementById('ppPdf'); return [window._pc, !!Paper._pdfF, Paper._pdfF && Paper._pdfF.size, o && o.innerText.slice(0,30), !!(o && o.querySelector('[data-pp=pdfOpen]')), !!(o && o.querySelector('[data-pp=pdfDl]'))]; }")
        ok(r[0] == 0 and r[1] and r[2] > 50000 and "인쇄용 PDF 완성" in (r[3] or "") and r[4] and r[5], f"인쇄 = 그림 PDF ({n}쪽) · 인쇄 창 열기 · 파일로 받기 {r}")
        async with ctx.expect_page() as np:
            await E("()=>document.querySelector('#ppPdf [data-pp=pdfOpen]').click()")
        w = await np.value
        ok(w is not None, f"「인쇄 창 열기」 = 새 탭이 열림 (시험 브라우저엔 PDF 보기가 없어 주소는 비어 있음) {w.url[:20]!r}")
        await w.close()
        async with pg.expect_download() as dl:
            await E("()=>document.querySelector('#ppPdf [data-pp=pdfDl]').click()")
        d = await dl.value
        ok(d.suggested_filename.endswith(".pdf"), f"「PDF 파일로 받기」 {d.suggested_filename}")
        await E("()=>{ document.getElementById('ppPdf').remove(); document.querySelector('#paper .ppVer [data-v=normal]').click(); }"); await pg.wait_for_timeout(200)
        r = await E("()=>{ window._pc=0; document.querySelector('#paper [data-pp=print]').click(); return [Paper.pdfMode(), localStorage.getItem('hyeng_pp_ver')]; }")
        await pg.wait_for_timeout(300)
        r.append(await E("()=>window._pc"))
        ok(r == [False, "normal", 1], f"🖨 보통 = 예전 브라우저 인쇄 {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
