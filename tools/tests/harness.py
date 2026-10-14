"""HY ENG 테스트 공용 — 저장소 파일을 그대로 깃허브 주소처럼 열어 준다 (복사 필요 없음).
   from harness import *  →  route, ORIGIN, SITE, OUT, SOLVE, boot(pg), real_errs(errs)"""
import asyncio, os, mimetypes, json, sys
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
SITE=os.path.abspath(os.path.join(HERE, "..", ".."))          # 저장소 맨 위 (index.html 이 있는 곳)
ORIGIN="https://misfits980.github.io/HY-ENG/"
OUT=os.path.join(HERE, "out")+os.sep                          # 스크린샷 (git 에 안 올림)
os.makedirs(OUT, exist_ok=True)
async def route(r):
    url=r.request.url
    if url.startswith(ORIGIN):
        p=url[len(ORIGIN):].split("?")[0] or "index.html"; f=os.path.join(SITE,p)
        if p=="three.min.js" and not os.path.isfile(f): f=os.path.join(HERE,"fake_three.js")   # 테스트용 가짜 3D 엔진 (그림 없이 게임 로직만)
        if os.path.isfile(f): return await r.fulfill(path=f, content_type="image/webp" if f.endswith(".webp") else (mimetypes.guess_type(f)[0] or "text/html"))
        return await r.fulfill(status=404, body="nf")
    await r.abort()                                           # 바깥 주소(CDN·구글 시트)는 막는다 → 콘솔의 'Failed to load' 는 정상
def real_errs(errs):
    """콘솔/페이지 오류 중 바깥 주소를 막아서 생긴 것은 뺀다"""
    return [e for e in errs if "Failed to load" not in e and "unknown error occurred when fetching the script" not in e]
async def boot(pg, news=True):
    await pg.route("**/*", route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
    if news: await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
# Daily 30 문제 하나를 정답(wrongFirst=true 면 처음엔 오답)으로 푸는 코드 — page.evaluate(SOLVE, wrongFirst)
SOLVE="""(wrongFirst)=>{ const U=StudyUI; if(U._brk){ document.getElementById('stCheck').click(); return 'brk'; }
  const q=U.qs[U.i]; if(!q) return 'none';
  if(U.locked){ document.getElementById('stCheck').click(); return 'cont'; }
  if(q.t==='intro'){ document.getElementById('stCheck').click(); return 'intro'; }
  if(q.t==='match'){ q.ws.forEach(w=>{ document.querySelector('.stM.en[data-en="'+w.en+'"]').click(); document.querySelector('.stM.ko[data-ko="'+w.en+'"]').click(); }); document.getElementById('stCheck').click(); return 'match'; }
  if(q.t==='drag'){ q.ws.forEach(w=>{ q.pick=document.querySelector('.dgChip[data-en="'+w.en+'"]'); document.querySelector('.dgT[data-en="'+w.en+'"]').click(); }); return 'drag'; }
  if(q.t==='blend'){ let k=q.opts.indexOf(q.mid); if(wrongFirst && !q.again) k=(k+1)%(q.t==='ox'?2:q.opts.length); document.querySelector('.stOpt[data-k="'+k+'"]').click(); return 'blend'; }
  if(q.t==='past'){ let k=q.opts.indexOf(q.w.en); if(wrongFirst && !q.again) k=(k+1)%q.opts.length; document.querySelector('.stOpt[data-k="'+k+'"]').click(); return 'past'; }
  if(q.t==='find'){ let k=q.toks.findIndex(o=>o.ok); if(wrongFirst && !q.again) k=q.toks.findIndex(o=>!o.ok); document.querySelector('#stQ .stOpt[data-k="'+k+'"]').click(); return 'find'; }
  if(q.t==='spell'||q.t==='dict'){ for(const c of q.w.en){ const b=[...document.querySelectorAll('.stTile')].find(x=>!x.disabled && x.textContent===c); b.click(); } document.getElementById('stCheck').click(); document.getElementById('stCheck').click(); return q.t; }
  let k= q.t==='ox' ? (q.truth?0:1) : q.opts.findIndex(o=>o.en===q.w.en); if(wrongFirst && !q.again) k=(k+1)%(q.t==='ox'?2:q.opts.length);
  document.querySelector('.stOpt[data-k="'+k+'"]').click(); return q.t; }"""
