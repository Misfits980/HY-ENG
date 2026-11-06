# 시험지 쪽·잘림 QA: python3 tools/tests/paperqa.py ph|pad|tv (책 10권 × 기본/모든 종류 × 30·50문제)
import asyncio, sys, json
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
SET = r"""(a)=>{ const [set, tyMode, n, seed]=a, P=Paper, gr=P.gr(set), L=Study.lessons(set);
  const allTy=P.ORD.filter(k=>{ const T=P.T[k]; return T && (!T[3] || T[3].split(' ').indexOf(gr)>=0); });
  const ty = tyMode==='def' ? (P.DEF[gr]||['mean']) : tyMode==='all' ? allTy : [tyMode];
  document.getElementById('ppSet').value=set; document.getElementById('ppSet').dispatchEvent(new Event('change',{bubbles:true}));
  document.getElementById('ppFrom').value=0; document.getElementById('ppTo').value=Math.min(L.length-1, 7); document.getElementById('ppN').value=String(n);
  document.querySelectorAll('#ppTy input').forEach(i=>{ i.checked = ty.indexOf(i.value)>=0; });
  P.seed=seed; P.make(); return ty.length; }"""
CHK = r"""()=>{ const W=document.getElementById('ppWrap'), z=W.style.zoom; W.style.zoom=''; const iss=[]; const I=(t,x)=>iss.push([t,x]);
  const pages=[...W.querySelectorAll('.pp')];
  pages.forEach((p,pi)=>{ const key=p.classList.contains('key');
    if(key){ const K=p.querySelector('.ppKey'); p.querySelectorAll('.ppKC').forEach(k=>{ if(k.scrollHeight>k.clientHeight+1) I('KEY_COL_OVER','p'+pi); }); const pr=p.getBoundingClientRect(), ft=p.querySelector('.ppFt'); const kr=K.getBoundingClientRect(); if(K.scrollHeight>K.clientHeight+1 || kr.bottom>pr.bottom-8) I('KEY_OVER', 'p'+pi+' '+Math.round(kr.bottom-pr.bottom)); return; }
    const cols=[...p.querySelectorAll('.ppCol')];
    cols.forEach((c,ci)=>{ if(c.scrollHeight>c.clientHeight+1) I('COL_OVER','p'+pi+'c'+ci);
      const cr=c.getBoundingClientRect(); c.querySelectorAll('*').forEach(e=>{ const r=e.getBoundingClientRect(); if(r.width && r.right>cr.right+2) { I('H_OVER','p'+pi+' '+(e.className||e.tagName)+' '+(e.textContent||'').slice(0,40)); } });
      const last=c.lastElementChild; if(last && last.classList.contains('ppSec')) I('ORPHAN_HEAD','p'+pi);
      c.querySelectorAll('.ppOp li').forEach(li=>{ if(li.scrollWidth>li.clientWidth+2) I('OPT_CLIP', li.textContent.slice(0,40)); });
    });
    const nxt=pages[pi+1]; if(nxt && !nxt.classList.contains('key') && !(nxt.querySelector('.ppHd:not(.sm)'))){ const used=cols.map(c=>{ const l=c.lastElementChild; return l? (l.getBoundingClientRect().bottom-c.getBoundingClientRect().top)/c.clientHeight : 0; }); if(Math.min(...used)<0.62) I('UNDERFILL','p'+pi+' '+used.map(u=>Math.round(u*100)).join('/')); }
  });
  /* numbering per form */
  const forms={}; pages.filter(p=>!p.classList.contains('key')).forEach(p=>{ const f=(p.querySelector('.ppFt').textContent.match(/^([AB])형/)||[,'-'])[1]; (forms[f]=forms[f]||[]).push(...[...p.querySelectorAll('.ppNo')].map(b=>b.textContent)); });
  Object.entries(forms).forEach(([f,L])=>{ let exp=1; L.forEach(t=>{ const m=t.match(/^(\d+)(?:~(\d+))?/); if(!m) return; if(+m[1]!==exp) I('NUM_GAP', f+' '+exp+'→'+m[1]); exp=(m[2]?+m[2]:+m[1])+1; }); });
  const nk=[...W.querySelectorAll('.pp.key .ppKF')].map(k=>k.querySelectorAll('.ppKS span i').length);
  W.style.zoom=z; return {iss, pages:pages.length, nk, info:document.getElementById('ppInfo').textContent.slice(0,120)}; }"""
async def main():
    vw={"ph":(390,844),"pad":(820,1180),"tv":(1920,1080)}[sys.argv[1]]
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={"width":vw[0],"height":vw[1]}); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
        await pg.evaluate("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({set:'basic', mode:'test'}); }"); await pg.wait_for_timeout(5000)
        sets=await pg.evaluate("()=>HyExam.sets()")
        out=[]
        for s in sets:
            for tm,n in (("def",30),("all",50),("def",50)):
                await pg.evaluate(SET, [s,tm,n,3]); await pg.wait_for_timeout(900)
                r=await pg.evaluate(CHK); r.update(set=s, tm=tm, n=n); out.append(r)
                print(s, tm, n, r["pages"], r["nk"], [x[0] for x in r["iss"]][:12], flush=True)
        json.dump(out, open(f"/tmp/claude-0/qa2_{sys.argv[1]}.json","w"), ensure_ascii=False)
        print("ERR", errs[:5]); await br.close()
if __name__=="__main__": asyncio.run(main())
