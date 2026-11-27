"""(v738) Daily 30 ✋ 끌어서 짝짓기 — 사용자: 「한 번은 봐줘」
   ① 잘못 놓기 1번 + 다 맞게 놓음 = 맞힘  ② 잘못 놓기 2번 = 틀림  ③ 안 틀리면 맞힘"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

FIND = """async ()=>{ for(let k=0;k<400;k++){ const q=StudyUI.qs[StudyUI.i]; if(q && !StudyUI.locked && !StudyUI._brk && q.t==='drag' && document.querySelector('.dgChip')) return true;
    (%s)(false); await new Promise(z=>setTimeout(z, q && q.t==='drag' ? 450 : 40)); } return false; }""" % SOLVE.strip()
PLAY = """async (nBad)=>{ const q=StudyUI.qs[StudyUI.i], W=q.ws; window._dr=null;
  const r0=StudyUI.result; StudyUI.result=function(ok, m){ if(window._dr===null) window._dr=ok; return r0.call(this, ok, m); };
  const drop=(a,b)=>{ q.pick=document.querySelector('.dgChip[data-en="'+a+'"]'); document.querySelector('.dgT[data-en="'+b+'"]').click(); };
  for(let k=0;k<nBad;k++) drop(W[0].en, W[1].en);
  W.forEach(w=>drop(w.en, w.en)); await new Promise(z=>setTimeout(z, 700)); StudyUI.result=r0; return [window._dr, q.miss, W.length]; }"""

async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ Voice.speak=()=>{}; }catch(e){} }")
        for nBad, want, nm in ((1, True, "① 잘못 놓기 1번 = 맞힘 (한 번은 봐줌)"), (2, False, "② 잘못 놓기 2번 = 틀림"), (0, True, "③ 안 틀리면 맞힘")):
            got = False
            for bk, st in (("g12", 0), ("g12", 1), ("g34", 0), ("g34", 1), ("k", 0), ("g12", 2)):
                await pg.evaluate("([bk,st])=>{ try{ StudyUI.close(); }catch(e){} StudyUI.open(); StudyUI.book=bk; StudyUI.path(); StudyUI.start(st,false); }", [bk, st])
                try: await pg.wait_for_function("()=>StudyUI.qs && StudyUI.qs.length>0", timeout=20000)   # 무거울 때 판이 늦게 열림
                except Exception: pass
                await pg.wait_for_timeout(400)
                if await pg.evaluate(FIND): got = True; break
            ok(got, f"끌어서 짝짓기 문제 찾음 ({nm})")
            if not got: continue
            r = await pg.evaluate(PLAY, nBad)
            ok(r[0] is want and r[1] == nBad, f"{nm} {r}")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await br.close()
    print("BAD: %d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
