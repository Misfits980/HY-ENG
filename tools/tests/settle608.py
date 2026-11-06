# v608 시험지·따라쓰기 — 쪽 나눈 뒤 글꼴·그림이 늦게 들어와 넘치면 다시 나누기
import asyncio, sys
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
OV="()=>{ const W=document.getElementById('ppWrap'), z=W.style.zoom; W.style.zoom=''; const r=[...W.querySelectorAll('.ppCol,.kjBody')].filter(c=>c.scrollHeight>c.clientHeight+1).length; W.style.zoom=z; return [r, W.querySelectorAll('.pp').length, Paper._rfN|0]; }"
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg); E=pg.evaluate
        for st,md in (("basic","test"),("mv1","test"),("elem","ks")):
            await E("(a)=>{ Paper.close(); document.getElementById('ppBig')&&document.getElementById('ppBig').remove(); Paper.open({set:a[0], mode:a[1]}); }", [st,md]); await pg.wait_for_timeout(5000)
            a=await E(OV)
            # 글꼴이 늦게 들어와 글이 커진 것처럼
            await E("()=>{ const s=document.createElement('style'); s.id='ppBig'; s.textContent='.pp .ppQ,.pp .kjB{font-size:112%!important;letter-spacing:.03em}'; document.head.appendChild(s); }")
            b=await E(OV)
            await E("()=>Paper.settle()"); await pg.wait_for_timeout(1500)
            c=await E(OV)
            print(st, md, "처음", a, "글자 커짐", b, "다시 나눔", c)
        # toggle types quickly
        await E("()=>{ Paper.close(); document.getElementById('ppBig').remove(); Paper.open({set:'basic', mode:'test'}); }"); await pg.wait_for_timeout(1500)
        for k in range(6):
            await E("(k)=>{ const b=[...document.querySelectorAll('#ppTy input')]; b[k%b.length].click(); }", k); await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(4500); print("토글 뒤", await E(OV))
        print("ERR", errs); await br.close()
asyncio.run(main())
