"""(v720) 사용자: 「지금 나 프린트 뽑기 누르면 앱이 자동으로 멈춰」 (휴대폰 · 따라쓰기)
   원인(찾은 것): 학원 프린터용 = 그림 PDF(html2canvas) — 도구가 쪽마다 문서 전체를 복사하고 복사본의 다 읽기·글꼴·그림을 끝없이 기다림
   → 글꼴(HY Trace) 요청 하나가 멈추면(휴대폰 망) 「쪽 확인 중…」에서 영영 멈추고 다시 눌러도 안 됨
   ① 글꼴 요청이 멈춰도 PDF 가 끝남 ② 보통 때 = 빠르게 · 따라쓰기 글꼴 그대로 · 휴대폰 = 📤 공유 + 💾 받기 ③ 「✕ 그만」
   ④ 복사 줄인 그림 = 예전과 같은 그림 ⑤ 한 쪽이 너무 오래 → 「🖨 보통 인쇄」 ⑥ PC = 「🖨 인쇄 창 열기」 그대로
   ⑦ 단어·문제 수 최대 50 → 200 + 「범위 전체」 (사용자: 「g5-6 리딩 1권 총단어 쓰기 · 반 권 쓰기 · 1-1 부터 2-4 까지 여러 형식으로 … 단어가 제한이 있더라」)"""
import asyncio, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
bad=[]
def ok(c,m):
    print(("OK  " if c else "BAD ")+m, flush=True)
    if not c: bad.append(m)
OPEN="(m)=>{ localStorage.removeItem('hyeng_paper'); localStorage.setItem('hyeng_pp_ver','school'); window._pc=0; window.print=()=>{ window._pc++; }; Paper.open({mode:m}); }"
ST="()=>[!!Paper._pdfF, Paper._pdfBusy, ((document.getElementById('ppPdf')||{}).innerText||'').replace(/\\s+/g,' ').slice(0,60), [...document.querySelectorAll('#ppPdf [data-pp]')].map(b=>b.dataset.pp).join(',')]"
async def waitPdf(E, sec):
    t0=time.time()
    while time.time()-t0<sec:
        s=await E(ST)
        if not s[1] and (s[0] or "못" in s[2]): return s, time.time()-t0
        await asyncio.sleep(.3)
    return await E(ST), time.time()-t0
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        async def page(dev, hang=False):
            ctx=await br.new_context(**dev) if isinstance(dev, dict) and "user_agent" in dev else await br.new_context(viewport=dev)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
            await pg.add_script_tag(path=os.path.join(SITE,"lib","html2canvas.min.js"))
            if hang:
                async def h(route): await asyncio.sleep(300)
                await pg.route("**/hy-trace.ttf", h)
            return ctx, pg
        G=p.devices["Galaxy S9+"]
        # ① 글꼴 요청이 멈춤
        ctx,pg=await page(G, hang=True); E=pg.evaluate
        await E(OPEN, "kw"); await pg.wait_for_timeout(2500)
        await E("()=>document.querySelector('#paper [data-pp=print]').click()")
        s,t=await waitPdf(E, 60)
        ok(s[0] and not s[1] and "pdfShare" in s[3], f"① 따라쓰기 글꼴 요청이 멈춰도 PDF 완성 ({t:.0f}초 · 예전 = 「쪽 확인 중…」에서 영영) {s}")
        await ctx.close()
        # ② 보통 때 · 휴대폰
        ctx,pg=await page(G); E=pg.evaluate
        await E(OPEN, "kw"); await pg.wait_for_timeout(2500)
        await E("()=>document.querySelector('#paper [data-pp=print]').click()")
        s,t=await waitPdf(E, 40)
        f=await E("()=>Paper._kjInfo && Paper._kjInfo.font")
        ok(s[0] and t<15 and f=="HY Trace" and s[3]=="pdfShare,pdfDl,pdfX", f"② 휴대폰 따라쓰기 PDF {t:.1f}초 · 글꼴 {f} · 📤 공유 + 💾 받기 {s}")
        # ③ 그만
        await E("()=>{ document.getElementById('ppPdf').remove(); window.HY_PDF_SLOW=1; const P=Paper, o=P.h2c.bind(P); P.h2c=async()=>{ const f=await o(); return async (a,b)=>{ await new Promise(r=>setTimeout(r,1500)); return f(a,b); }; }; document.querySelector('#paper [data-pp=print]').click(); }")
        await pg.wait_for_timeout(600)
        b=await E("()=>!!document.querySelector('#ppPdf [data-pp=pdfStop]')")
        await E("()=>document.querySelector('#ppPdf [data-pp=pdfStop]').click()")
        for _ in range(30):
            if not await E("()=>Paper._pdfBusy"): break
            await pg.wait_for_timeout(200)
        r=await E("()=>[Paper._pdfBusy, !!document.getElementById('ppPdf'), !!Paper._pdfF]")
        ok(b and r==[0, False, False], f"③ 만드는 중 「✕ 그만」 → 창 닫힘 · 다시 누를 수 있음 {b} {r}")
        # ⑤ 한 쪽이 너무 오래
        await E("()=>{ window.HY_PDF_TO=1200; Paper.h2c=async()=>()=>new Promise(()=>{}); document.querySelector('#paper [data-pp=print]').click(); }")
        s,t=await waitPdf(E, 20)
        ok("못 만들" in s[2] and "pdfPlain" in s[3] and not s[1], f"⑤ 너무 오래 → 「🖨 보통 인쇄」 단추 {s}")
        await E("()=>document.querySelector('#ppPdf [data-pp=pdfPlain]').click()"); await pg.wait_for_timeout(400)
        r=await E("()=>[window._pc, !!document.getElementById('ppPdf'), localStorage.getItem('hyeng_pp_ver')]")
        ok(r==[1, False, "school"], f"⑤ 「보통 인쇄」 = 브라우저 인쇄 한 번 · 설정은 그대로 {r}")
        await ctx.close()
        # ④ 같은 그림 · ⑥ PC
        ctx,pg=await page({"width":1280,"height":720}); E=pg.evaluate
        for m in ("kw","test"):
            await E(OPEN, m); await pg.wait_for_timeout(2500)
            r=await E("""async ()=>{ const pg=document.querySelector('#ppWrap .pp'), host=document.createElement('div'); host.className='ppWrap ppShot'; document.getElementById('paper').appendChild(host);
              const shot=async ign=>{ const c=pg.cloneNode(true); host.innerHTML=''; host.appendChild(c); const o={scale:1, backgroundColor:'#fff', logging:false, scrollX:0, scrollY:0, windowWidth:900};
                if(ign) o.ignoreElements=el=>!(el===document.documentElement || el===document.body || el.contains(host) || host.contains(el) || (el.closest && el.closest('head')));
                const cv=await html2canvas(c, o); return cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; };
              const a=await shot(false), b=await shot(true); host.remove(); let d=0; for(let i=0;i<a.length;i+=4){ if(Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2])>30) d++; } return [a.length, d]; }""")
            ok(r[0]>3000000 and r[1]==0, f"④ {m} 복사를 줄여도 같은 그림 {r}")
            if m=="test": await E("()=>Paper.close && Paper.close()")
        await E(OPEN, "test"); await pg.wait_for_timeout(2000)
        await E("()=>document.querySelector('#paper [data-pp=print]').click()")
        s,t=await waitPdf(E, 40)
        ok(s[0] and "pdfOpen" in s[3] and "pdfShare" not in s[3], f"⑥ PC = 「🖨 인쇄 창 열기」 그대로 {s}")
        # ⑦ 단어·문제 수 = 200 · 범위 전체 (사용자: 「리딩 1권 총단어 쓰기 · 반 권 쓰기 … 단어가 제한이 있더라」)
        for m in ("kw","ks","test"):
            await E("(m)=>{ document.getElementById('ppPdf') && document.getElementById('ppPdf').remove(); Paper.close && Paper.close(); localStorage.setItem('hyeng_paper', JSON.stringify({set:'rd1', n:999, mode:m})); Paper.open({mode:m}); }", m); await pg.wait_for_timeout(1500)
            await E("()=>{ const s=document.getElementById('ppSet'); s.value='rd1'; s.dispatchEvent(new Event('change',{bubbles:true})); }"); await pg.wait_for_timeout(600)
            await E("()=>{ const a=document.getElementById('ppFrom'), b=document.getElementById('ppTo'); a.value=a.options[0].value; a.dispatchEvent(new Event('change',{bubbles:true})); b.value=b.options[b.options.length-1].value; b.dispatchEvent(new Event('change',{bubbles:true})); const n=document.getElementById('ppN'); n.value='999'; n.dispatchEvent(new Event('change',{bubbles:true})); Paper.make(); }"); await pg.wait_for_timeout(1500)
            r=await E("()=>[[...document.querySelectorAll('#ppN option')].map(o=>o.textContent).slice(-3).join(','), Paper.c && Paper.c.n, document.querySelectorAll('#ppWrap .pp').length, document.getElementById('ppInfo').textContent, Paper.c && Paper.c.all, JSON.parse(localStorage.getItem('hyeng_paper')||'{}').n]")
            ok(r[0]=="150,200,범위 전체" and r[1]==400 and r[4] and r[5]==999 and r[2]>=30 and "모자라" not in r[3] and "⚠️" not in r[3] and ("298" in r[3] or "290" in r[3]), f"⑦ {m} 리딩 1 전체 = 범위 단어 다(298) · {r[2]}쪽 · 「모자라」·⚠️ 없음 · 기억 {r[5]} · {r[3][:90]}")
        # ⑦ 400 넘는 범위 = 400 + 안내
        await E("()=>{ const s=document.getElementById('ppSet'); s.value='g56'; s.dispatchEvent(new Event('change',{bubbles:true})); }"); await pg.wait_for_timeout(600)
        await E("()=>{ const a=document.getElementById('ppFrom'), b=document.getElementById('ppTo'); a.value=a.options[0].value; b.value=b.options[b.options.length-1].value; const n=document.getElementById('ppN'); n.value='999'; Paper.make(); }"); await pg.wait_for_timeout(1500)
        r=await E("()=>[document.querySelectorAll('#ppWrap .pp:not(.key) .ppQ').length, document.getElementById('ppInfo').textContent]")
        ok("400문제" in r[1] and "한 번에 400개까지" in r[1], f"⑦ 고학년 단어 전체(2780개) = 400문제 × A·B · 「한 번에 400개까지」 안내 {r[0]} · {r[1][:120]}")
        await ctx.close()
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
