"""(v679) 선생님 관리 🖨 시험지 전체 점검 — 사용자: 「어드민모드 시험지 오류 없는지 전체적으로 확인」
   다섯 가지(📝 시험지 · ✏️ 단어 따라쓰기 · ✏️ 문장 따라쓰기 · 💬 생활영어 · 📒 문법)를 책·범위·형식·옵션마다 만들어 보고
   ① 만들기 오류 · 문제 수 모자람  ② 보기 겹침·정답 없음·뜻 겹침·문장에 답 보임  ③ 화면 문제 순서·보기 = 계산한 A형·B형 · 답안지 = 정답
   ④ undefined·null·NaN·[object·&amp; 같은 깨진 글자 · 빈 문제  ⑤ 단 넘침·옆 넘침·보기 잘림·번호 건너뜀·쪽 넘침·빈 쪽
   ⑥ 실제 인쇄(PDF) 쪽 수 = 화면 쪽 수 (빈 쪽·쪽 잘림 없음) · 그림 쪽 몇 장 찍기
   python3 tools/tests/ppall.py [test kw ks lf gm slip pdf]  (빼면 전부) — 결과 out/ppall.json · 그림 out/ppall_*.png"""
import asyncio, sys, os, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

HELP = r"""()=>{
const $=id=>document.getElementById(id), P=Paper;
const bad=/undefined|NaN|\bnull\b|\[object|&amp;|&lt;|&gt;|&quot;|&#\d/;
window.__layout=(W, iss, I)=>{ const pages=[...W.querySelectorAll('.pp')];
  pages.forEach((p,pi)=>{ const key=p.classList.contains('key'), tag='p'+(pi+1)+(key?'key':'');
    if(p.scrollHeight>p.clientHeight+2) I('PAGE_OVER', tag+' '+(p.scrollHeight-p.clientHeight)+'px');
    const pr=p.getBoundingClientRect();
    p.querySelectorAll('.ppCol,.ppKC,.kjBody').forEach((c,ci)=>{ if(c.scrollHeight>c.clientHeight+1) I('COL_OVER', tag+' c'+ci+' +'+(c.scrollHeight-c.clientHeight)+'px');
      const cr=c.getBoundingClientRect(); for(const e of c.querySelectorAll('*')){ const r=e.getBoundingClientRect(); if(r.width && r.height && (r.right>cr.right+2 || r.left<cr.left-2) && getComputedStyle(e).position!=='absolute'){ I('H_OVER', tag+' '+(e.className||e.tagName)+' '+(e.textContent||'').slice(0,40)); break; } }
      c.querySelectorAll('.ppOp li').forEach(li=>{ if(li.scrollWidth>li.clientWidth+2) I('OPT_CLIP', tag+' '+li.textContent.slice(0,40)); }); });
    for(const e of p.querySelectorAll('*')){ const r=e.getBoundingClientRect(); if(r.width && r.height && (r.bottom>pr.bottom+1 || r.right>pr.right+1)){ I('OUT_PAGE', tag+' '+(e.className||e.tagName)+' '+(e.textContent||'').slice(0,30)); break; } }
    const tx=p.innerText; const m=bad.exec(tx); if(m) I('BAD_TEXT', tag+' «'+tx.slice(Math.max(0,m.index-25), m.index+25).replace(/\s+/g,' ')+'»');
    const body=p.querySelector('.ppCol,.ppKC,.kjBody,.slipG'), rd=p.classList.contains('rd'); if(key || rd ? !(body && p.querySelector('.ppBody,.ppKey,.kjBody').textContent.trim()) : !p.querySelector('.ppQ,.kjB,.slip')) I('EMPTY_PAGE', tag);
    const ft=p.querySelector('.ppFt'); if(ft && /(\d+) \/ (\d+)/.test(ft.textContent)){ const m2=/(\d+) \/ (\d+)/.exec(ft.textContent); if(+m2[2]<+m2[1]) I('FOOT', tag+' '+ft.textContent); }
  });
  W.querySelectorAll('img').forEach(im=>{ if(im.complete && !im.naturalWidth) I('IMG_BROKEN', (im.getAttribute('src')||'').slice(-40)); });
  W.querySelectorAll('.ppQ').forEach(q=>{ const t=q.innerText.replace(/^\s*\d+(~\d+)?\.\s*/,'').replace(/[①②③④\s]/g,''); if(!t && !q.querySelector('img,.ppPic,.ppLine')) I('EMPTY_Q', (q.querySelector('.ppNo')||{}).textContent); });
  return pages.length; };
const optTx=(k,q)=> q.lab ? q.lab.map(String) : q.opts ? q.opts.map(o=>k==='mean'?o.ko:dispEn(o.en)) : null;
window.__chk=()=>{ const iss=[], I=(t,x)=>iss.push([t,x]); const W=$('ppWrap'), B=P.B, c=P.c; const z=W.style.zoom; W.style.zoom='';
  if(!B){ W.style.zoom=z; return {iss:[['NO_B','']], pages:0}; }
  if(B.nw!=null && B.nw<4 && !(B.pre && B.pre.length)){ W.style.zoom=z; return {iss, pages:0, skip:$('ppInfo').textContent.slice(0,80)}; }
  const out={iss, total:B.total, n:c.n, warn:(B.warn||[]).slice(), info:$('ppInfo').textContent.slice(0,160)};
  if(B.total===0 && W.querySelector('.pp:not(.rd)')) I('ZERO_Q', '문제 0개인데 시험지 '+W.querySelectorAll('.pp').length+'쪽 · '+$('ppInfo').textContent.slice(0,80));
  if(B.total!=null && B.nw>=4 && B.total<Math.min(c.n, B.nw)*0.8 && !(c.x)) I('SHORT', B.total+'/'+c.n+' (단어 '+B.nw+')');
  if(c.x && B.total!=null && B.total>0 && B.total<Math.min(c.n,10)) I('SHORT_X', B.total+'/'+c.n);
  /* 문제 자료 */
  (B.S||[]).forEach(sec=>sec.qs.forEach(q=>{ const k=sec.k, w=(q && q.w && q.w.en) || ''; if(!q){ I('NULLQ', k); return; } if(k==='match') return;
    const opts=optTx(k,q); if(opts && !q.po){ const low=opts.map(o=>String(o).trim().toLowerCase()); if(opts.length<3 && !q.noOpt && !/gox/.test(k)) I('FEWOPT', k+' '+w+' '+opts.join('/'));
      if(new Set(low).size<low.length) I('DUPOPT', k+' '+w+' '+opts.join('/')); if(low.some(o=>!o)) I('EMPTY_OPT', k+' '+w+' '+opts.join('/'));
      const ans = q.lab ? String(q.ans) : (k==='mean' ? q.w.ko : dispEn(q.w.en)); if(!q.noOpt && low.indexOf(ans.trim().toLowerCase())<0) I('NOANS', k+' '+w+' ans='+ans+' | '+opts.join('/'));
      const sv=s=>String(s).split(/[,·/;]/).map(x=>x.replace(/\(.*?\)|\[.*?\]/g,'').replace(/^~/,'').trim()).filter(Boolean);
      if((k==='mean'||k==='k2e') && q.opts){ const A=sv(q.w.ko); q.opts.forEach(o=>{ if(o!==q.w && sv(o.ko).some(x=>A.indexOf(x)>=0)) I(k==='mean'?'MEAN_OVERLAP':'K2E_OVERLAP', w+' '+q.w.ko+' ~ '+o.en+' '+o.ko); }); }
      if(k==='pic' && q.opts) q.opts.forEach(o=>{ if(o!==q.w && o.emoji===q.w.emoji) I('PIC_SAME', w+' ~ '+o.en); }); }
    if(q.po && q.lab && new Set(q.lab).size<q.lab.length) I('PIC_DUP', k+' '+q.lab.join(' '));
    if(k==='sent' && q.st){ const s=(q.st.pre+' '+q.st.post).toLowerCase(); if(new RegExp('\\b'+q.w.en.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\b').test(s)) I('SENT_LEAK', w+' :: '+q.st.pre+'___'+q.st.post); }
    if(k==='scr' && q.scr && q.scr.join('').toLowerCase()===q.w.en.toLowerCase()) I('SCR_SAME', w);
    if(k==='gap' && q.gap && q.gap.indexOf('_')<0) I('GAP_NONE', w);
    if((q.wr||q.vt||q.at||q.ow) && !String(q.key||'').trim()) I('KEY_EMPTY', k+' '+w);
  }));
  /* A형·B형 다시 계산 → 화면·답안지와 맞추기 */
  const forms = c.ab ? [{F:'A', secs:P.form(B, P.rnd(P.seed+1))}, {F:'B', secs:P.form(B, P.rnd(P.seed+2))}] : [{F:'', secs:P.form(B, P.rnd(P.seed+1))}];
  const pages=[...W.querySelectorAll('.pp')], keyPs=pages.filter(p=>p.classList.contains('key'));
  const keyF={}; keyPs.forEach(p=>p.querySelectorAll('.ppKF').forEach(kf=>{ const h=kf.querySelector('h4'), F=h ? (/^([AB])형/.exec(h.textContent)||[,''])[1] : ''; (keyF[F]=keyF[F]||[]).push(...[...kf.querySelectorAll('.ppKS > span')].map(s=>{ const i=s.querySelector('i'); const no=i?i.textContent:''; return [no, s.textContent.slice(no.length).trim()]; })); }));
  forms.forEach(f=>{ const qp=pages.filter(p=>!p.classList.contains('key') && p.querySelector('.ppQ') && (!f.F || (p.querySelector('.ppFt')||{}).textContent.indexOf(f.F+'형')===0));
    const qEl={}; qp.forEach(p=>p.querySelectorAll('.ppQ').forEach(e=>{ const n=(e.querySelector('.ppNo')||{}).textContent||''; qEl[n.replace(/\.$/,'')]=e; }));
    let no=1; const KE=keyF[f.F]||[]; const kmap={}; KE.forEach(x=>{ kmap[x[0]]=x[1]; });
    if(c.key && !KE.length && B.total) I('KEY_MISSING', f.F||'-');
    f.secs.forEach(s=>s.qs.forEach(q=>{ const k=s.k;
      if(k==='match'){ const id=no+'~'+(no+q.w.length-1), e=qEl[id]; if(!e) I('Q_MISSING', f.F+' '+id); else { const R=[...e.querySelectorAll('.ppM ol.r li')].map(li=>li.textContent.replace(/^[ⓐ-ⓔ]/,'').trim()); const exp=q.right.map(w=>(P.gr(c.set)==='k' && w.emoji) ? '' : w.ko); if(exp.some((x,i)=>x && R[i]!==x)) I('MATCH_ORDER', f.F+' '+id); }
        if(c.key) q.w.forEach((w,i)=>{ const a=kmap[String(no+i)], ex=P.LET[q.right.indexOf(w)]; if(a!==ex) I('KEY_WRONG', f.F+' '+(no+i)+' 답안지 '+a+' / 맞는 답 '+ex+' ('+w.en+')'); }); no+=q.w.length; return; }
      const e=qEl[String(no)]; if(!e) I('Q_MISSING', f.F+' '+no+' '+k);
      const opts=optTx(k,q);
      if(e && opts && !q.po && !q.noOpt){ const R=[...e.querySelectorAll('.ppOp li')].map(li=>li.textContent.replace(/^[①②③④]/,'').trim()); if(R.length!==opts.length || R.some((x,i)=>x!==String(opts[i]).trim())) I('OPT_ORDER', f.F+' '+no+' 화면 '+R.join('/')+' | 계산 '+opts.join('/')); }
      let ex;
      if(q.wr||q.vt||q.at||q.ow) ex=String(q.key); else if(q.lab){ if(q.a<0) I('ANS_NOT_IN', f.F+' '+no+' '+k+' '+q.ans); ex=P.NUM[q.a]+(q.noOpt?' '+q.ans:''); }
      else if(q.opts){ if(q.a<0) I('ANS_NOT_IN', f.F+' '+no+' '+k); ex=P.NUM[q.a]; } else if(k==='wko') ex=q.w.ko; else ex=dispEn(q.w.en);
      if(c.key){ const a=kmap[String(no)]; if(a==null) I('KEY_MISSING_Q', f.F+' '+no+' '+k); else if(a.indexOf(String(ex).trim())!==0) I('KEY_WRONG', f.F+' '+no+' '+k+' 답안지 «'+a.slice(0,30)+'» / 맞는 답 «'+String(ex).slice(0,30)+'»'); }
      no++; })); });
  /* 번호 이어짐 (형마다) */
  const nums={}; pages.filter(p=>!p.classList.contains('key')).forEach(p=>{ const F=((p.querySelector('.ppFt')||{}).textContent.match(/^([AB])형/)||[,'-'])[1]; (nums[F]=nums[F]||[]).push(...[...p.querySelectorAll('.ppQ .ppNo')].map(b=>b.textContent)); });
  Object.entries(nums).forEach(([F,L])=>{ let exp=1; L.forEach(t=>{ const m=t.match(/^(\d+)(?:~(\d+))?/); if(!m) return; if(+m[1]!==exp) I('NUM_GAP', F+' '+exp+'→'+m[1]); exp=(m[2]?+m[2]:+m[1])+1; }); });
  out.pages=__layout(W, iss, I); W.style.zoom=z; return out; };
window.__kjChk=()=>{ const iss=[], I=(t,x)=>iss.push([t,x]), W=$('ppWrap'), z=W.style.zoom; W.style.zoom=''; const c=P.c;
  const out={iss, info:$('ppInfo').textContent.slice(0,160)}; const B=[...W.querySelectorAll('.kjB')];
  if(!B.length && !/없어요|받는 중/.test(out.info)) I('KJ_EMPTY', out.info);
  const nos=B.map(b=>+((b.querySelector('.kjNo')||{}).textContent||0)); nos.forEach((n,i)=>{ if(n!==i+1) I('NUM_GAP', (i+1)+'→'+n); });
  B.forEach(b=>{ const w=(b.querySelector('.kjW b, .kjSt p')||{}).textContent||''; if(!w.trim()) I('KJ_NOWORD', (b.querySelector('.kjNo')||{}).textContent); const ko=(b.querySelector('.kjW small, .kjSt > small')||{}).textContent; if(ko!=null && !ko.trim()) I('KJ_NOKO', w.slice(0,30));
    b.querySelectorAll('.kjT').forEach(t=>{ const p=t.parentNode; if(t.offsetWidth>p.clientWidth+2) I('KJ_TRACE_CLIP', t.textContent.slice(0,30)); });
    if(!b.querySelector('.kjStrip')) I('KJ_NOLINE', w.slice(0,30)); });
  out.n=B.length; out.pages=__layout(W, iss, I); W.style.zoom=z; return out; };
return 1; }"""

TEST_CFG = r"""(a)=>{ const [set, from, to, ty, n, ab, key, note, seed]=a, $=id=>document.getElementById(id), S=$('ppSet');
  if(S.value!==set){ S.value=set; S.dispatchEvent(new Event('change',{bubbles:true})); }
  $('ppFrom').value=from; $('ppTo').value=to; $('ppN').value=String(n); $('ppTitle').value='';
  document.querySelectorAll('#ppTy input').forEach(i=>{ i.checked = ty.indexOf(i.value)>=0; });
  $('ppAB').checked=ab; $('ppKey').checked=key; $('ppNote').checked=note; Paper.seed=seed; Paper._kjMix=false;
  let err=null; try{ Paper.make(); }catch(e){ err=String(e && e.stack || e).slice(0,300); } (Paper._stQ||[]).forEach(clearTimeout); return err; }"""
KJ_CFG = r"""(a)=>{ const [set, from, to, n, rep, tr, gm]=a, $=id=>document.getElementById(id), S=$('ppSet');
  if(S.value!==set){ S.value=set; S.dispatchEvent(new Event('change',{bubbles:true})); }
  $('ppFrom').value=from; $('ppTo').value=to; $('ppN').value=String(n); $('ppTitle').value='';
  const R=$('ppRep'); if(![...R.options].some(o=>o.value==String(rep))) return 'norep'; R.value=String(rep); $('ppTr').checked=tr; $('ppGm').value=gm;
  let err=null; try{ Paper.make(); }catch(e){ err=String(e && e.stack || e).slice(0,300); } (Paper._stQ||[]).forEach(clearTimeout); return err; }"""
X_CFG = r"""(a)=>{ const [lf, g, from, to, ty, n, ab, key, seed]=a, $=id=>document.getElementById(id), S=$(lf?'ppLv':'ppGb');
  if(S.value!==g){ S.value=g; S.dispatchEvent(new Event('change',{bubbles:true})); }
  $(lf?'ppLF':'ppGF').value=from; $(lf?'ppLT':'ppGT').value=to; $('ppN').value=String(n); $('ppTitle').value='';
  document.querySelectorAll('#ppTy input').forEach(i=>{ i.checked = ty.indexOf(i.value)>=0; });
  $('ppAB').checked=ab; $('ppKey').checked=key; Paper.seed=seed;
  let err=null; try{ Paper.make(); }catch(e){ err=String(e && e.stack || e).slice(0,300); } (Paper._stQ||[]).forEach(clearTimeout); return err; }"""

def ranges(L, wide=True):
    if L <= 0: return []
    R = [(0, min(L - 1, 2))]
    if L > 6: R.append((L // 2, min(L - 1, L // 2 + 2)))
    if L > 3: R.append((max(0, L - 3), L - 1))
    if wide and L > 3: R.append((0, L - 1))
    out = []
    [out.append(r) for r in R if r not in out]
    return out

async def main():
    want = set(sys.argv[1:]) or {"test", "kw", "ks", "lf", "gm", "slip", "pdf"}
    res = []; errs = []; t0 = time.time()
    def rec(mode, cfg, r, err=None):
        r = r or {}; r.update(mode=mode, cfg=cfg)
        if err: r.setdefault("iss", []).append(["MAKE_ERR", err])
        res.append(r)
        if r.get("iss"): print(f"  {mode} {cfg} → {sorted(set(x[0] for x in r['iss']))} e.g. {r['iss'][0][1][:110]}", flush=True)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:300])); await boot(pg); E = pg.evaluate
        if os.environ.get("HY_PP_ROOM") == "0":   # (v690) 📏 넉넉하게(기본 켜짐)를 끄고 예전 촘촘한 모양으로 돌려 봄
            await E("()=>localStorage.setItem('hyeng_paper', JSON.stringify({room:false}))")
        await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({mode:'test'}); }"); await pg.wait_for_timeout(6000)
        await E(HELP)
        sets = await E("()=>Paper.psets()")
        info = await E("()=>Paper.psets().map(s=>[s, Study.label(s), Paper.gr(s), Study.lessons(s).length])")
        print("책", len(sets), [(x[1], x[2], x[3]) for x in info], flush=True)
        # ── 📝 시험지
        if "test" in want:
            for s, lab, gr, L in info:
                vis = await E("(s)=>Paper.ORD.filter(k=>Paper.vis(k, s))", s)
                dflt = await E("(g)=>Paper.DEF[g]||Paper.DEF.g34", gr)
                for (f, t) in ranges(L):
                    combos = [("def", dflt, 30, True, True, True, 3), ("all", vis, 50, True, True, True, 5)]
                    if (f, t) == ranges(L)[0] or (f, t) == (0, L - 1):
                        combos += [(k, [k], 20, k in ("mean", "k2e"), True, False, 7) for k in vis]
                        combos += [("def-noab", dflt, 25, False, False, False, 9), ("def40", dflt, 40, True, True, True, 11)]
                    for nm, ty, n, ab, key, note, seed in combos:
                        err = await E(TEST_CFG, [s, f, t, ty, n, ab, key, note, seed])
                        r = await E("()=>__chk()") if not err else {}
                        rec("test", f"{lab} [{f}-{t}] {nm} n{n}{' AB' if ab else ''}", r, err)
                print(f"· 시험지 {lab} 끝 ({int(time.time()-t0)}s)", flush=True)
        # ── ✏️ 따라쓰기
        for m in ("kw", "ks"):
            if m not in want: continue
            await E("(m)=>{ Paper.open({mode:m}); }", m); await pg.wait_for_timeout(1500); await E(HELP)
            await E("()=>Paper.svaLoad()"); await pg.wait_for_timeout(1500)
            reps = await E("(m)=>Paper.KJ_REP[m]", m)
            for s, lab, gr, L in info:
                gms = ["off"] if gr in ("g12", "k") else ["off", "show", "quiz"]
                for (f, t) in ranges(L)[:2] + ([(0, L - 1)] if L > 3 else []):
                    for rep in sorted(set([reps[0], reps[-1]])):
                        for gm in gms:
                            for n in (20, 50):
                                err = await E(KJ_CFG, [s, f, t, n, rep, rep == reps[0], gm])
                                if err == "norep": continue
                                r = await E("()=>__kjChk()") if not err else {}
                                rec(m, f"{lab} [{f}-{t}] ×{rep} {gm} n{n}", r, err)
                print(f"· {m} {lab} 끝 ({int(time.time()-t0)}s)", flush=True)
        # ── 💬 생활영어 · 📒 문법
        for m in ("lf", "gm"):
            if m not in want: continue
            await E("(m)=>{ Paper.open({mode:m}); }", m); await pg.wait_for_timeout(500)
            await E("()=>Paper.xLoad()"); await pg.wait_for_timeout(2500)
            await E("(m)=>{ Paper.open({mode:m}); }", m); await pg.wait_for_timeout(1500); await E(HELP)
            lf = m == "lf"
            groups = await E("(lf)=>Object.keys(lf ? Paper.LV_NM : Paper.GB_NM)", lf)
            for g in groups:
                N = await E("([lf,g])=>(lf ? Life.list(g) : Paper.gmTopics(g)).length", [lf, g])
                tys = await E("""([lf,g])=>{ const S=document.getElementById(lf?'ppLv':'ppGb'); S.value=g; S.dispatchEvent(new Event('change',{bubbles:true})); return [...document.querySelectorAll('#ppTy input')].map(i=>i.value); }""", [lf, g])
                dflt = await E("([lf,g])=>(lf ? Paper.LF_DEF : Paper.GM_DEF)[g]", [lf, g])
                print(f"· {m} {g} 주제 {N} 형식 {tys}", flush=True)
                for (f, t) in ranges(N):
                    combos = [("def", dflt, 30, True, True, 3), ("all", tys, 50, True, True, 5)]
                    if (f, t) == ranges(N)[0]: combos += [(k, [k], 20, False, True, 7) for k in tys]
                    for nm, ty, n, ab, key, seed in combos:
                        err = await E(X_CFG, [lf, g, f, t, ty, n, ab, key, seed])
                        r = await E("()=>__chk()") if not err else {}
                        rec(m, f"{g} [{f}-{t}] {nm} n{n}", r, err)
        # ── 🖨 숙제 쪽지
        if "slip" in want:
            r = await E("""()=>{ const H=window.HwPost||window.Homework||window.HW; return Object.keys(window).filter(k=>{ try{ const v=window[k]; return v && typeof v==='object' && typeof v.slip==='function'; }catch(e){ return false; } }); }""")
            print("· 숙제 쪽지 모듈", r, flush=True)
        # ── 🖨 진짜 인쇄 쪽 수 (PDF) — 모드마다 몇 개
        if "pdf" in want:
            samples = []
            for s, lab, gr, L in info[:: max(1, len(info) // 6)]:
                samples.append(("test", s, lab, gr, L))
            for mode, s, lab, gr, L in samples + [("kw", info[0][0], info[0][1], info[0][2], info[0][3]), ("ks", info[-3][0], info[-3][1], info[-3][2], info[-3][3])]:
                await E("(m)=>{ Paper.open({mode:m}); }", mode); await pg.wait_for_timeout(1200); await E(HELP)
                if mode == "test":
                    ty = await E("(g)=>Paper.DEF[g]||Paper.DEF.g34", gr); await E(TEST_CFG, [s, 0, min(L - 1, 5), ty, 40, True, True, True, 3])
                else:
                    reps = await E("(m)=>Paper.KJ_REP[m]", mode); await E(KJ_CFG, [s, 0, min(L - 1, 3), 20, reps[0], True, "off" if gr in ("g12", "k") else "show"])
                await pg.wait_for_timeout(1500)
                n_pp = await E("()=>document.querySelectorAll('#ppWrap .pp').length")
                await E("()=>{ window.print=()=>{}; Paper.print(); }"); await pg.wait_for_timeout(200)
                pdf = await pg.pdf(prefer_css_page_size=True, print_background=True)
                n_pdf = len(re.findall(rb"/Type\s*/Page(?!s)", pdf))
                await E("()=>{ document.body.classList.remove('ppPrint'); }")
                ok = n_pdf == n_pp
                rec("pdf", f"{mode} {lab}", {"iss": [] if ok else [["PDF_PAGES", f"화면 {n_pp}쪽 · 인쇄 {n_pdf}쪽"]], "pages": n_pp, "pdf": n_pdf})
                print(f"· 인쇄 {mode} {lab}: 화면 {n_pp} · PDF {n_pdf}", flush=True)
        # ── 그림 몇 장
        shots = [("test", "g34", 0), ("test", "mid", 0), ("test", "k", 0), ("kw", "g12", 0), ("ks", "g56", 0), ("lf", "g34", 0), ("gm", "g34", 0)]
        for mode, gr, _ in shots:
            try:
                s = next((x for x in info if x[2] == gr), info[0])
                await E("(m)=>{ Paper.open({mode:m}); }", mode); await pg.wait_for_timeout(1200)
                if mode in ("lf", "gm"):
                    await pg.wait_for_timeout(1500); await E("([lf,g])=>{ const S=document.getElementById(lf?'ppLv':'ppGb'); if([...S.options].some(o=>o.value===g)){ S.value=g; S.dispatchEvent(new Event('change',{bubbles:true})); } }", [mode == "lf", gr])
                elif mode == "test":
                    ty = await E("(g)=>Paper.DEF[g]||Paper.DEF.g34", s[2]); await E(TEST_CFG, [s[0], 0, min(s[3] - 1, 2), ty, 30, True, True, True, 3])
                else:
                    reps = await E("(m)=>Paper.KJ_REP[m]", mode); await E(KJ_CFG, [s[0], 0, min(s[3] - 1, 2), 20, reps[0], True, "off" if s[2] in ("g12", "k") else "show"])
                await pg.wait_for_timeout(1500)
                await E("()=>{ const W=document.getElementById('ppWrap'); W.style.zoom=''; }")
                ps = await pg.query_selector_all("#ppWrap .pp")
                for i, el in enumerate(ps[:1] + ps[-1:]):
                    await el.screenshot(path=OUT + f"ppall_{mode}_{gr}_{'first' if i == 0 else 'last'}.png")
            except Exception as e:
                print("shot fail", mode, gr, str(e)[:120])
        await br.close()
    json.dump(res, open(OUT + "ppall.json", "w"), ensure_ascii=False, indent=0)
    from collections import Counter
    C = Counter(); ex = {}
    for r in res:
        for t, x in r.get("iss", []): C[(r["mode"], t)] += 1; ex.setdefault((r["mode"], t), []).append(r["cfg"] + " :: " + x)
    print("\n== 요약 (만든 시험지 %d개 · %ds)" % (len(res), time.time() - t0))
    for k, v in sorted(C.items()): print("  ", k, v)
    for k, L in ex.items():
        print("==", k); [print("    ", x[:220]) for x in sorted(set(L))[:10]]
    print("JS 오류", len(real_errs(errs)), real_errs(errs)[:5])
asyncio.run(main())
