"""(v265) 도감 — 위쪽 제목 줄 ✕ · 📍 나오는 곳(짧게 · 눌러서 바로 가기) · 관리 화면 도감 모으기"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

PICK = """()=>{ let best=null, bn=-1;
  DEX_BASE.slice(0,900).forEach(w=>{ let n=0; try{ Study.SETS.forEach(id=>Study.lessons(id).forEach(l=>{ if(l.ws.some(x=>x.en===w.en)) n++; })); }catch(e){}
    if(n>bn){ bn=n; best=w.en; } }); return [best,bn]; }"""

async def main():
    bad = []
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("try{ sessionStorage.setItem('hyeng_admin_ok','1'); }catch(e){}")
        await boot(pg); await pg.wait_for_timeout(400)
        # 관리 화면에서 G1-2 도감 모으기 (보상 없이)
        await pg.evaluate("()=>{ Admin._tab('fix'); Admin.open(); }"); await pg.wait_for_timeout(400)
        pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await pg.select_option("#adDexG", "g12"); await pg.click('[data-ad="dexFill"]'); await pg.wait_for_timeout(400)
        print("admin fill:", await pg.evaluate("()=>document.getElementById('adMsg').innerText"), "| gifts left", await pg.evaluate("()=>Dex.gifts().filter(x=>!Wallet.paid(x.key)).length"))
        await pg.screenshot(path=OUT + "dexf_admin.png")
        if await pg.evaluate("()=>Dex.gifts().filter(x=>!Wallet.paid(x.key)).length") != 0: bad.append("보상이 남음")
        await pg.evaluate("()=>Admin.close()")
        # 도감 열기 + 앨범 + 내려도 제목 줄 ✕
        await pg.evaluate("()=>document.getElementById('btnDex').click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>{ const a=document.querySelector('#dexShelf [data-a], #dexShelf button'); if(a) a.click(); }"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=OUT + "dexf_top.png")
        x = await pg.evaluate("""()=>{ const s=document.querySelector('#shDex .sheetIn'); s.scrollTop=1500; const x=document.querySelector('#shDex .shX'), h=x.closest('.shopHead');
            const r=x.getBoundingClientRect(), hr=h.getBoundingClientRect(), sr=s.getBoundingClientRect(); const e=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2);
            return {inHead: !!h, headTop: Math.round(hr.top-sr.top), hit: e===x, n: document.querySelectorAll('#shDex .shX').length} }""")
        await pg.wait_for_timeout(200); await pg.screenshot(path=OUT + "dexf_scrolled.png")
        print("x", x)
        if not (x['inHead'] and x['hit'] and x['n'] == 1 and abs(x['headTop']) <= 2): bad.append("도감 ✕")
        # 나오는 곳이 많은 단어
        en, n = await pg.evaluate(PICK); print("word", en, n)
        await pg.evaluate(f"()=>{{ document.querySelector('#shDex .sheetIn').scrollTop=0; DexDet.show('{en}', true); }}"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ const f=document.querySelector('.wFind'); if(f) f.scrollIntoView(); }"); await pg.wait_for_timeout(200)
        info = await pg.evaluate("()=>{ const f=document.querySelector('.wFind'); return f ? {txt:f.innerText, h:Math.round(f.getBoundingClientRect().height), run:f.querySelectorAll('[data-run]').length, st:f.querySelectorAll('[data-study]').length} : null }")
        print("found", info)
        await pg.screenshot(path=OUT + "dexf_found.png")
        if not info or info['st'] > 4 or info['h'] > 200: bad.append("나오는 곳 길이")
        # 달리기 칸 → 바로 달리기
        rid = await pg.evaluate("()=>document.querySelector('.wFind [data-run]').dataset.run")
        await pg.evaluate("()=>document.querySelector('.wFind [data-run]').click()"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("()=>({running:!!G.running, set:G.set, dex:document.getElementById('shDex').classList.contains('on')})")
        print("run chip", rid, r)
        if not (r['running'] and r['set'] == rid and not r['dex']): bad.append("달리기 바로 가기")
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }")
        await pg.evaluate(f"()=>{{ document.getElementById('btnDex').click(); }}"); await pg.wait_for_timeout(500)
        await pg.evaluate(f"()=>DexDet.show('{en}', true)"); await pg.wait_for_timeout(400)
        sid = await pg.evaluate("()=>{ const b=document.querySelector('.wFind [data-study]'); return b ? [b.dataset.study, +b.dataset.si] : null }")
        await pg.evaluate("()=>document.querySelector('.wFind [data-study]').click()"); await pg.wait_for_timeout(800)
        r2 = await pg.evaluate("()=>({lesson:document.getElementById('stLesson').style.display!=='none' && document.getElementById('scStudy').classList.contains('on'), set:StudyUI.set, i:Study.lessons(StudyUI.set).indexOf(StudyUI.les)})")
        print("study chip", sid, r2)
        await pg.screenshot(path=OUT + "dexf_study.png")
        if not (r2['lesson'] and sid and r2['set'] == sid[0] and r2['i'] == sid[1]): bad.append("Daily 30 바로 가기")
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        if bad: print("BAD", bad)
        await br.close()
asyncio.run(main())
