# v576 홈 화면 앱(아이폰) 시험지 → PDF 파일 만들기 · 공유
import asyncio, sys, base64
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True, device_scale_factor=2)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:300])); await boot(pg); E=pg.evaluate
        await pg.route("**/lib/html2canvas.min.js", lambda r: r.fulfill(path="/home/claude/hy-eng/lib/html2canvas.min.js", content_type="application/javascript"))
        await E("()=>{ Paper.forcePdf=1; window._sh=[]; navigator.canShare=()=>true; navigator.share=(d)=>{ window._sh.push(d.files[0].name+':'+d.files[0].size); return Promise.resolve(); }; Paper.open({set:'elem'}); }")
        await pg.wait_for_timeout(2500)
        print(await E("()=>document.querySelector('#paper [data-pp=print]').textContent"))
        await pg.locator("#paper [data-pp=print]").tap(); await pg.wait_for_timeout(600)
        await pg.screenshot(path="/tmp/claude-0/pdf576_pdf_busy.png")
        for i in range(60):
            await pg.wait_for_timeout(500)
            if await E("()=>!Paper._pdfBusy"): break
        await pg.screenshot(path="/tmp/claude-0/pdf576_pdf_done.png")
        print(await E("()=>[document.getElementById('ppPdf').textContent, Paper._pdfF && Paper._pdfF.size, Paper._pdfF && Paper._pdfF.name, document.querySelectorAll('.ppShot').length, document.getElementById('ppWrap').style.zoom]"))
        b64=await E("()=>new Promise(r=>{ const fr=new FileReader(); fr.onload=()=>r(fr.result.split(',')[1]); fr.readAsDataURL(Paper._pdfF); })")
        open("/tmp/claude-0/pdf576_out.pdf","wb").write(base64.b64decode(b64))
        await pg.locator("#paper [data-pp=pdfShare]").tap(); await pg.wait_for_timeout(300)
        print("share", await E("()=>window._sh"))
        await pg.locator("#paper [data-pp=pdfX]").tap(); await pg.wait_for_timeout(200)
        print("closed", await E("()=>!document.getElementById('ppPdf')"), "ERR", errs[:5])
        await br.close()
asyncio.run(main())
