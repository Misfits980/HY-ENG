# v579 ✏️ 단어 깜지 · 문장 깜지 (시험지 창 모드)
import asyncio, sys
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":1280,"height":1800}, device_scale_factor=1.5); pg.on("pageerror", lambda e: errs.append(str(e)[:300])); await boot(pg); E=pg.evaluate
        for st,md in (("basic","kw"),("elem","ks"),("mv1","kw"),("mv1","ks"),("g56","ks")):
            await E("(a)=>{ Paper.close(); Paper.open({set:a[0], mode:a[1]}); }", [st,md]); await pg.wait_for_timeout(1800)
            info=await E("()=>[document.getElementById('ppInfo').textContent, document.querySelectorAll('#ppWrap .pp').length, document.getElementById('ppRep').value, document.getElementById('ppTr').checked, getComputedStyle(document.getElementById('ppTy')).display]")
            print(st, md, info)
            await E("()=>{ document.getElementById('ppWrap').style.zoom=1; }")
            await pg.locator("#ppWrap .pp").first.screenshot(path=f"/tmp/claude-0/kj579_{st}_{md}.png")
        # mode switch back to test
        await E("()=>document.querySelector('#ppMd [data-v=test]').click()"); await pg.wait_for_timeout(800)
        print("test", await E("()=>[document.querySelectorAll('#ppWrap .ppQ').length, getComputedStyle(document.getElementById('ppTy')).display, document.getElementById('ppNL').textContent]"))
        await E("()=>document.querySelector('#ppMd [data-v=kw]').click()"); await pg.wait_for_timeout(500)
        await E("()=>document.querySelector('#paper [data-pp=new]').click()"); await pg.wait_for_timeout(500)
        print("mix", await E("()=>document.getElementById('ppInfo').textContent"))
        print("errs", errs)
        await br.close()
        # phone bar
        br=await p.chromium.launch(); pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2); await boot(pg)
        await pg.evaluate("()=>Paper.open({set:'basic', mode:'kw'})"); await pg.wait_for_timeout(1800)
        await pg.screenshot(path="/tmp/claude-0/kj579_phone.png"); await br.close()
asyncio.run(main())
