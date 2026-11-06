# 시험지 문제 자료 QA (보기 수·겹침·정답 있음·뜻 겹침·그림 같음·문장에 답 보임)
import asyncio, sys, json
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
JS = r"""async (a)=>{ const [set, tyMode, n, seed]=a; const P=Paper; const out={set, tyMode, n, issues:[]}; const I=(t,x)=>out.issues.push([t,x]);
  const gr=P.gr(set); const L=Study.lessons(set); const allTy=P.ORD.filter(k=>{ const T=P.T[k]; return T && (!T[3] || T[3].split(' ').indexOf(gr)>=0); });
  const ty = tyMode==='def' ? (P.DEF[gr]||['mean']) : tyMode==='all' ? allTy : [tyMode];
  const c={set, from:0, to:Math.min(L.length-1, 5), n, ty, ab:true, key:true, title:''};
  P.seed=seed; let B; try{ B=P.build(c); }catch(e){ I('BUILD_ERR', e.message); return out; }
  out.total=B.total; out.warn=B.warn; if(B.total<Math.min(n, B.nw)*0.8) I('SHORT', B.total+'/'+n+' nw '+B.nw);
  const tx=o=>typeof o==='string'?o:(o.en||'');
  B.S.forEach(sec=>sec.qs.forEach(q=>{ if(!q){ I('NULLQ', sec.k); return; } const k=sec.k, w=q.w&&q.w.en;
    if(k==='match') return;
    let opts=null, ans=null; if(q.lab){ opts=q.lab.map(String); ans=String(q.ans); } else if(q.opts){ opts=q.opts.map(o=> k==='mean'?o.ko:o.en); ans= k==='mean'?q.w.ko:q.w.en; }
    if(opts){ if(opts.length<3) I('FEWOPT', k+' '+w+' '+opts.join('/'));
      const low=opts.map(o=>String(o).trim().toLowerCase()); if(new Set(low).size<low.length) I('DUPOPT', k+' '+w+' '+opts.join('/'));
      if(!q.noOpt && low.indexOf(String(ans).trim().toLowerCase())<0 && !q.wr) I('NOANS', k+' '+w+' ans='+ans+' | '+opts.join('/'));
      if(k==='mean'){ const sv=s=>String(s).split(/[,·/]/).map(x=>x.replace(/\(.*?\)/g,'').trim()).filter(Boolean); const A=sv(q.w.ko); q.opts.forEach(o=>{ if(o!==q.w && sv(o.ko).some(x=>A.indexOf(x)>=0)) I('MEAN_OVERLAP', w+' '+q.w.ko+' ~ '+o.en+' '+o.ko); }); }
      if(k==='k2e'){ const sv=s=>String(s).split(/[,·/]/).map(x=>x.replace(/\(.*?\)/g,'').trim()).filter(Boolean); const A=sv(q.w.ko); q.opts.forEach(o=>{ if(o!==q.w && sv(o.ko).some(x=>A.indexOf(x)>=0)) I('K2E_OVERLAP', q.w.ko+' '+w+' ~ '+o.en+' '+o.ko); }); }
      if(k==='pic'){ q.opts.forEach(o=>{ if(o!==q.w && o.emoji===q.w.emoji) I('PIC_SAME', w+' ~ '+o.en); }); }
    }
    if(k==='sent' && q.st){ const s=(q.st.pre+' '+q.st.post).toLowerCase(); if(new RegExp('\\b'+q.w.en.toLowerCase()+'\\b').test(s)) I('SENT_LEAK', w+' :: '+q.st.pre+'___'+q.st.post); }
    if(k==='scr' && q.scr && q.scr.join('')===q.w.en) I('SCR_SAME', w);
  }));
  return out; }"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
        await pg.evaluate("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({set:'basic'}); }"); await pg.wait_for_timeout(5000)
        sets=await pg.evaluate("()=>HyExam.sets()")
        res=[]
        for s in sets:
            for tm in ["def","all"]:
                for n in [20,50]:
                    for seed in [1,7]:
                        r=await pg.evaluate(JS, [s,tm,n,seed]); res.append(r)
        json.dump(res, open("/tmp/claude-0/qa1.json","w"), ensure_ascii=False, indent=0)
        from collections import Counter
        C=Counter(); ex={}
        for r in res:
            for t,x in r["issues"]: C[(r["set"],t)]+=1; ex.setdefault(t,[]).append(r["set"]+" "+x)
        for k,v in sorted(C.items()): print(k, v)
        for t,L in ex.items():
            print("==",t); [print("  ",x) for x in sorted(set(L))[:12]]
        print("errs", errs[:5])
        await br.close()
asyncio.run(main())
