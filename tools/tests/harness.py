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
        if p=="three.min.js" and not os.environ.get("HY_REAL3D"): f=os.path.join(HERE,"fake_three.js")   # 테스트용 가짜 3D 엔진 (그림 없이 게임 로직만) — (v289) 저장소에 진짜 three.min.js 가 생겨도 기본은 가짜 (HY_REAL3D=1 이면 진짜)
        if p.startswith("lib/") and not os.environ.get("HY_REAL3D"): return await r.fulfill(status=404, body="nf")   # 가짜 엔진에는 빛 번짐 스크립트를 안 붙인다
        if os.path.isfile(f): return await r.fulfill(path=f, content_type="image/webp" if f.endswith(".webp") else (mimetypes.guess_type(f)[0] or "text/html"))
        return await r.fulfill(status=404, body="nf")
    await r.abort()                                           # 바깥 주소(CDN·구글 시트)는 막는다 → 콘솔의 'Failed to load' 는 정상
def real_errs(errs):
    """콘솔/페이지 오류 중 바깥 주소를 막아서 생긴 것은 뺀다"""
    return [e for e in errs if "Failed to load" not in e and "unknown error occurred when fetching the script" not in e]
async def boot(pg, news=True):
    await pg.route("**/*", route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
    if news: await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
    await pg.evaluate("()=>{ try{ StudyUI.FAST=0; }catch(e){} }")   # (v301) 테스트는 '너무 빨리 누름' 막기를 끈다
# Daily 30 문제 하나를 정답(wrongFirst=true 면 처음엔 오답)으로 푸는 코드 — page.evaluate(SOLVE, wrongFirst)
SOLVE="""(wrongFirst)=>{ const U=StudyUI; if(U._brk){ document.getElementById('stCheck').click(); return 'brk'; }
  const q=U.qs[U.i]; if(!q) return 'none';
  if(U.locked){ document.getElementById('stCheck').click(); return 'cont'; }
  if(q.t==='intro' && q.hd==='sort'){ q.pick=q.pick||{}; q.ws.forEach((w,k)=>{ if(!q.pick[w.en]) q.pick[w.en]=(k%3===0?'s':'c'); }); U.check(); return 'intro'; }   // (v301) 세 칸 나누기
  if(q.t==='intro'){ document.getElementById('stCheck').click(); return 'intro'; }
  if(q.so){ let k=q.opts.indexOf(q.ans); if(wrongFirst && !q.again) k=(k+1)%q.opts.length; document.querySelector('#stQ .stOpt[data-k="'+k+'"]').click(); return q.t; }
  if(q.t==='order'){ const used=[]; q.x.ch.forEach(c=>{ const k=q.tiles.findIndex((ci,j)=>q.x.ch[ci]===c && used.indexOf(j)<0); used.push(k); document.querySelector('.odT[data-o="'+k+'"]').click(); }); document.getElementById('stCheck').click(); return 'order'; }
  if(q.t==='kdict'){ for(const c of (q.kans||q.w.en)) document.querySelector('.kdK[data-kk="'+c+'"]').click(); document.getElementById('stCheck').click(); return 'kdict'; }
  if(q.t==='match'){ q.ws.forEach(w=>{ document.querySelector('.stM.en[data-en="'+w.en+'"]').click(); document.querySelector('.stM.ko[data-ko="'+w.en+'"]').click(); }); document.getElementById('stCheck').click(); return 'match'; }
  if(q.t==='drag'){ q.ws.forEach(w=>{ q.pick=document.querySelector('.dgChip[data-en="'+w.en+'"]'); document.querySelector('.dgT[data-en="'+w.en+'"]').click(); }); return 'drag'; }
  if(q.t==='blend'){ let k=q.opts.indexOf(q.mid); if(wrongFirst && !q.again) k=(k+1)%(q.t==='ox'?2:q.opts.length); document.querySelector('.stOpt[data-k="'+k+'"]').click(); return 'blend'; }
  if(q.t==='sentp'){ let k=q.opts.indexOf(q.form); if(wrongFirst && !q.again) k=(k+1)%q.opts.length; document.querySelector('.stOpt[data-k="'+k+'"]').click(); return 'sentp'; }
  if(q.t==='past'){ let k=q.opts.indexOf(q.w.en); if(wrongFirst && !q.again) k=(k+1)%q.opts.length; document.querySelector('.stOpt[data-k="'+k+'"]').click(); return 'past'; }
  if(q.t==='find'){ let k=q.toks.findIndex(o=>o.ok); if(wrongFirst && !q.again) k=q.toks.findIndex(o=>!o.ok); document.querySelector('#stQ .stOpt[data-k="'+k+'"]').click(); return 'find'; }
  if(q.t==='spell'||q.t==='dict'){ for(const c of q.w.en){ const b=[...document.querySelectorAll('.stTile')].find(x=>!x.disabled && x.textContent===c); b.click(); } document.getElementById('stCheck').click(); document.getElementById('stCheck').click(); return q.t; }
  let k= q.t==='ox' ? (q.truth?0:1) : q.opts.findIndex(o=>o.en===q.w.en); if(wrongFirst && !q.again) k=(k+1)%(q.t==='ox'?2:q.opts.length);
  document.querySelector('.stOpt[data-k="'+k+'"]').click(); return q.t; }"""
