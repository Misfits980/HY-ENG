"""(v322) Daily 30 문제·보기 점검 — 정답이 둘이 되는 보기 · 과거형 표제어 · 유치원 판 크기 · 🚩 모아서 복습 · 쉬는 화면 저장 · 길 맨 위 칩
   python3 tools/tests/quiztest.py   (BAD 줄이 없으면 통과)"""
import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

WAIT = """async ()=>{ for(const b of [1,2,3]) DexData.load(b); loadEasy(); loadTalk(); loadBex();
  for(let i=0;i<100 && !(DexData.st[1]==='ok'&&DexData.st[2]==='ok'&&DexData.st[3]==='ok'&&Object.keys(EASY).length&&Object.keys(TALK).length&&Object.keys(BEX).length&&Object.keys(MIDX).length);i++) await new Promise(r=>setTimeout(r,100)); return 1; }"""

# 공용 도우미 (페이지 안)
HELP = """
  const D=en=>DexData.of(en)||[]; const posP=en=>String(D(en)[1]||'').split(/[·,\\/\\s]+/).filter(Boolean);
  const rel=(en,ks)=>{ const R=D(en)[7]||{}; return ks.map(k=>String(R[k]||'')).join(',').toLowerCase().replace(/\\([^)]*\\)/g,'').split(/[,·\\/]/).map(t=>t.trim()).filter(Boolean); };
  const syn=en=>rel(en,['s']), opp=en=>rel(en,['o']);
  const TOP={people:1,body:1,food:1,home:1,play:1,time:1,place:1,animal:1}; const alb=en=>{ const w=Dex.where(en); return w? w.a.id.split('-').pop() : '?'; };
  const noun=en=>posP(en).includes('명사');
  const pastHead=en=>/과거형/.test(String(D(en)[1]||''));
"""

async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]; bad=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.evaluate("()=>StudyUI.open()"); await pg.evaluate(WAIT)

        # 1) 과거형 표제어(went·saw)는 과거형 문제 안 냄 · be/have 뒤 과거형(수동태·완료)은 과거형 빈칸으로 안 씀
        r=await pg.evaluate("()=>{"+HELP+"""
          const out=[], n={sentp:0};
          ['went','saw','ate','came'].forEach(en=>{ if(Study._pastOf(en)) out.push('pastOf '+en+'='+Study._pastOf(en)); ['ptype','form','tense'].forEach(t=>{ const q=Study._mk(t,en,'g56',3); if(q) out.push(t+' '+en+' → '+(q.kans||q.ans)); }); });
          const L=Study.lessons('g56'), x=L.find(y=>y.ws.some(w=>w.en==='went')), S=Study.load(), k=Study.key('g56',x.n), t=Study.today();
          x.ws.forEach(w=>S.seen[w.en]=1); S.ck=S.ck||{}; S.dp=S.dp||{}; S.d1=S.d1||{};
          for(const [lv,dp,ck,d1] of [[1,0,1,null],[2,1,1,null],[1,0,0,t-1]]){ S.lv[k]=lv; S.dp[k]=dp; if(ck) S.ck[k]=1; else delete S.ck[k]; if(d1!=null) S.d1[k]=d1; else delete S.d1[k];
            for(let r=0;r<12;r++) Study.build('g56',x.n).forEach(q=>{ if(!q.w || !pastHead(q.w.en)) return;
              if(q.t==='sentp' || (q.t==='kdict' && q.kans) || q.t==='form' || (q.t==='gram' && q.x && /pastc|tense/.test(q.x.kind||''))) out.push('past-head '+q.t+' '+q.w.en+' → '+(q.kans||q.ans||q.form)); }); }
          delete S.lv[k]; delete S.ck[k]; delete S.dp[k]; delete S.d1[k];
          L.slice(0,40).forEach(y=>{ const kk=Study.key('g56',y.n); y.ws.forEach(w=>S.seen[w.en]=1); S.lv[kk]=1; S.ck[kk]=1;
            for(let r=0;r<2;r++) Study.build('g56',y.n).forEach(q=>{ if(q.t!=='sentp') return; n.sentp++; if(/\\b(am|is|are|was|were|be|been|being|has|have|had)\\s+(not\\s+)?$/i.test(q.st.pre)) out.push('passive '+q.w.en+': '+q.st.pre+'___'); });
            delete S.lv[kk]; delete S.ck[kk]; });
          return {out, n}; }""")
        print('past', r['n'], len(r['out'])); bad += ['past: '+s for s in r['out']]

        # 2) 사이트 워드 문장 빈칸 — 정답과 품사가 같은 보기·관사끼리 X · can(깡통) 예문 X
        r=await pg.evaluate("()=>{"+HELP+"""
          const out=[]; let n=0; const S=Study.load();
          for(const x of Study.lessons('sight').slice(0,8)){ for(let r=0;r<6;r++){ x.ws.forEach(w=>S.seen[w.en]=1); S.lv[Study.key('sight',x.n)]=1+(r%2);
            Study.build('sight',x.n).forEach(q=>{ if(q.t!=='sent' || !q.opts) return; n++; const a=q.w.en, ap=posP(a), art=/^(a|an|the)$/.test(a);
              q.opts.forEach(o=>{ if(o.en===a) return; if((art && /^(a|an|the)$/.test(o.en)) || posP(o.en).some(p=>ap.includes(p))) out.push(q.st.pre+'___'+q.st.post+' ['+q.opts.map(o=>o.en).join('/')+'] ans '+a); });
              if(a==='can' && !/수 ?있|수 ?없|할 줄/.test(q.st.ko)) out.push('can 다른 뜻 예문: '+q.st.pre+'___'+q.st.post); }); } }
          return {out:[...new Set(out)], n}; }""")
        print('sight sent', r['n'], len(r['out'])); bad += ['sight: '+s for s in r['out'][:10]]

        # 3) 비슷한 말·반대말 문제 — 정답이 둘 X
        r=await pg.evaluate("()=>{"+HELP+"""
          const out=[]; let n=0; const seen={};
          for(const set of ['elem','g56','jl','mid']){ Study.load().set=set; Study.lessons(set).slice(0,60).forEach(x=>x.ws.forEach(w=>{ if(seen[w.en]) return; seen[w.en]=1;
            for(let r=0;r<2;r++){ const q=Study._mk('rel',w.en,set,3); if(!q) break; n++; const A=q.ans.toLowerCase(), kd=q.x.kd;
              const b=q.opts.filter(o=>o!==q.ans).filter(o=> kd==='s' ? (syn(o).includes(A)||syn(A).includes(o)||syn(o).includes(w.en)) : (opp(o).includes(w.en)||opp(w.en).includes(o)||syn(o).includes(A)||syn(A).includes(o)));
              if(b.length) out.push(set+' '+w.en+(kd==='s'?' ≈ ':' ↔ ')+'['+q.opts.join('/')+'] ans '+q.ans+' ALSO '+b.join(',')); } })); }
          return {out, n}; }""")
        print('rel', r['n'], len(r['out'])); bad += ['rel: '+s for s in r['out'][:10]]

        # 4) 🚩 그림 문제(opic) — 같은 그림 보기 X  ·  5) 대화·문장 빈칸 — 반대말·비슷한 말·같은 무리·같은 앨범 명사 보기 X
        r=await pg.evaluate("()=>{"+HELP+"""
          const out=[], n={opic:0, blank:0};
          for(const set of ['basic','elem','g56','jl']){ for(const L of Study.lessons(set)){ for(let k=0;k<2;k++){ let qs=[];
              if(L.fin) qs=Study.buildOly(set,L); else { const s=Study.load(); s.lv[Study.key(set,L.n)]=1; L.ws.forEach(x=>s.seen[x.en]=1); qs=Study.build(set,L.n,false); delete s.lv[Study.key(set,L.n)]; }
              qs.forEach(q=>{ if(!q.opts || !q.w) return; const a=q.w.en;
                if((q.t==='opic' || q.opic) && q.w.emoji){ n.opic++; const b=q.opts.filter(o=>o.en!==a && o.emoji===q.w.emoji); if(b.length) out.push('opic '+set+' '+a+q.w.emoji+' vs '+b.map(o=>o.en)); }
                if(q.t==='talk'||q.t==='sent'||q.t==='sent2'){ n.blank++; const ra=rel(a,['o','s','g']);
                  const b=q.opts.filter(o=>o.en!==a && (ra.includes(o.en.toLowerCase()) || rel(o.en,['o','s','g']).includes(a) || (noun(a)&&noun(o.en)&&TOP[alb(a)]&&alb(a)===alb(o.en))));
                  if(b.length) out.push('blank '+set+' '+q.t+' '+a+' vs '+b.map(o=>o.en)); } }); } } }
          return {out:[...new Set(out)], n}; }""")
        print('opic/blank', r['n'], len(r['out'])); bad += [s for s in r['out'][:12]]

        # 6) 뜻 조각·영어가 포함 관계인 보기 X (up '~을 따라 위로' / along '~을 따라' · website / site · bicycle / cycle · argue / argument)
        r=await pg.evaluate("""()=>{ const out=[]; const W=en=>Study.word(en);
          const cases=[[Object.assign({},W('up'),{ko:'~을 따라 위로'}),'along'],[W('website'),'site'],[W('bicycle'),'cycle'],[Object.assign({},W('argue'),{ko:'다투다, 말다툼하다'}),'argument']];
          cases.forEach(([w,o])=>{ if(!w || !W(o)) { out.push('missing '+o); return; } for(let r=0;r<15;r++){ const ops=Study._opts(w,'g56',[W(o)]); if(ops.includes(o)){ out.push(w.en+' ['+ops.join('/')+'] has '+o); break; } } });
          return out; }""")
        print('partial', len(r)); bad += ['partial: '+s for s in r]

        # 7) 유치원 그림 단어 ★1 — 새 단어 10개까지 · 11) hpic 보기에 뜻이 같은 그림(rat/mouse · dish/bowl · puppy/dog) X
        r=await pg.evaluate("""()=>{ const out=[]; const L=Study.lessons('kinder'), x=L[0], S=Study.load(); x.ws.forEach(w=>delete S.seen[w.en]); delete S.lv[Study.key('kinder',x.n)];
          const P=Study.plan('kinder',x.n), qs=Study.build('kinder',x.n), cards=qs.filter(q=>q.t==='intro' && q.card).length, n=qs.filter(q=>q.t!=='intro').length;
          if(P.nw>10 || cards>10) out.push('kinder ★1 nw '+P.nw+' cards '+cards+' q '+n);
          const W=en=>Study.word(en);
          [['rat',['mouse']],['mouse',['rat']],['dish',['bowl','plate']],['bowl',['dish']],['puppy',['dog']],['rabbit',['bunny']]].forEach(([a,os])=>{ if(!W(a)) return;
            for(let r=0;r<20;r++){ const q=Study._q('hpic',a,'kinder',os.map(W).filter(Boolean)); const b=(q.opts||[]).filter(o=>os.includes(o.en)); if(b.length){ out.push('hpic '+a+' with '+b.map(o=>o.en)); break; } } });
          return {out, nw:P.nw, cards, n}; }""")
        print('kinder', r['nw'], r['cards'], r['n']); bad += ['kinder: '+s for s in r['out']]

        # 8) 파닉스·사이트 🚩 모아서 복습 — 새 단어 카드 없이 문제만 · 팝업 문제 수 = 실제
        r=await pg.evaluate("""()=>{ const out=[], S=Study.load();
          for(const set of ['abc','short','digr','sight']){ const L=Study.lessons(set), f=L.find(x=>x.fin); f.ws.forEach(w=>S.seen[w.en]=1); delete S.lv[Study.key(set,f.n)];
            const qs=Study.build(set,f.n), cards=qs.filter(q=>q.t==='intro').length, n=qs.filter(q=>q.t!=='intro').length, P=Study.plan(set,f.n);
            if(cards || n!==P.qn) out.push(set+' 🚩 cards '+cards+' q '+n+' plan '+P.qn); }
          return out; }""")
        print('fin review', len(r)); bad += ['fin: '+s for s in r]

        # 11) 짝말 빈칸(colb) — 정답이 짝말에 또 보이면 X · 품사 바꾸기(famf) 가짜 보기가 진짜 말 X
        r=await pg.evaluate("()=>{"+HELP+"""
          const out=[]; let nc=0, nf=0;
          Object.keys(DexData.d).filter(en=>/^[a-z]+$/.test(en) && Study.word(en) && String(D(en)[6]||'').split(/\\s*·\\s*/).some(ph=>(ph.match(new RegExp('\\\\b'+en+'\\\\b','gi'))||[]).length>=2)).slice(0,40).forEach(en=>{
            for(let r=0;r<6;r++){ const q=Study._mk('colb',en,'elem',3); if(!q) break; nc++; if(new RegExp('\\\\b'+en+'\\\\b','i').test(q.st.pre+' '+q.st.post)) { out.push('colb '+en+': '+q.st.pre+'___'+q.st.post); break; } } });
          const real={}; Object.keys(DexData.d).forEach(k=>{ real[k]=1; const d=DexData.d[k]; String(d[2]||'').toLowerCase().split(/[^a-z]+/).forEach(x=>{ if(x) real[x]=1; }); const R=d[7]||{}; ['f','s','o','g'].forEach(kk=>String(R[kk]||'').toLowerCase().split(/[^a-z]+/).forEach(x=>{ if(x.length>3) real[x]=1; })); });
          const seen={}; Study.load().set='mid';
          for(const set of ['g56','mid']) Study.lessons(set).slice(0,40).forEach(x=>x.ws.forEach(w=>{ if(seen[w.en]) return; seen[w.en]=1;
            for(let r=0;r<2;r++){ const q=Study._mk('famf',w.en,set,3); if(!q) break; nf++; const b=q.opts.filter(o=>o!==q.ans && real[o]); if(b.length){ out.push('famf '+w.en+' ['+q.opts.join('/')+'] real '+b); break; } } }));
          return {out, nc, nf}; }""")
        print('colb/famf', r['nc'], r['nf'], len(r['out'])); bad += [s for s in r['out'][:10]]

        # 9) 라운드 쉬는 화면에서 꺼져도 다음 문제부터 (saveCur)
        r=await pg.evaluate("""async ()=>{ StudyUI.book='g12'; StudyUI.set='basic'; StudyUI.path(); StudyUI.start(1,false);
          for(let k=0;k<200 && !StudyUI._brk;k++){ const q=StudyUI.qs[StudyUI.i]; if(!q) break; (%s)(false); await new Promise(r=>setTimeout(r,20)); if(StudyUI.locked && !StudyUI._brk) document.getElementById('stCheck').click(); }
          const c=StudyUI.getCur(); return {brk:!!StudyUI._brk, i:StudyUI.i, ci:c&&c.i, done:StudyUI.done, cd:c&&c.done}; }""" % SOLVE)
        print('break save', r)
        if not r['brk']: bad.append('break: 쉬는 화면이 안 나옴 '+json.dumps(r))
        elif r['i']!=r['ci'] or r['done']!=r['cd']: bad.append('break: 저장 위치 '+json.dumps(r))

        # 10) 길 맨 위 — 머리말 'Stage n / 24' · '확인할 단어' · 390×844 에서 첫 Stage 보임 · 12) '다음에' 뒤 작은 '🔁 복습' 칩
        await pg.evaluate("""()=>{ try{ localStorage.removeItem(StudyUI.CUR); }catch(e){} const S=Study.load(), t=Study.today(); const L=Study.lessons('jl'); const k=x=>Study.key('jl',x.n);
          S.d1=S.d1||{}; S.ck=S.ck||{}; S.sd=S.sd||{}; S.srs=S.srs||{}; delete S.rvLater;
          [0,1].forEach(i=>{ L[i].ws.forEach(w=>{ S.seen[w.en]=1; S.sd[w.en]=t; S.srs[w.en]=[1,t-1]; }); S.lv[k(L[i])]=1; delete S.ck[k(L[i])]; });
          S.d1[k(L[0])]=t-1; S.d1[k(L[1])]=t; Study.save(); StudyUI.view('stPath'); StudyUI.book='mid'; StudyUI.set='jl'; StudyUI.path(); }""")
        await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ scrollTo(0,0); document.querySelectorAll('#scStudy, #scStudy *').forEach(e=>{ if(e.scrollTop) e.scrollTop=0; }); }"); await pg.wait_for_timeout(100)
        r=await pg.evaluate("""()=>{ const em=document.querySelector('#stHead em'), d=document.querySelector('#stMap .stDot'), top=d.getBoundingClientRect().top;
          return {em:em&&em.textContent, chk:!!document.querySelector('.stChkRow') && document.querySelector('.stChkRow').innerText.includes('확인할 단어'), rv:!!document.querySelector('.cpRow .cpRv.go [data-review]'), wk:!!document.querySelector('.stWeek'), top, h:innerHeight}; }""")
        print('path', r)
        if r['em']!='Stage 1 / 24': bad.append('path: 머리말 '+str(r['em']))
        if not r['chk'] or not r['rv'] or not r['wk']: bad.append('path: 맨 위 칩 '+json.dumps(r))
        if r['top']+40>r['h']: bad.append('path: 첫 Stage 가 화면 밖 '+json.dumps(r))
        await pg.screenshot(path=OUT+"quiz_path.png")
        # (v331) 맨 위 한 줄 캠프 — 상자·보스·표지판 그림, 서로·Stage 돌과 안 겹침 · '다음에' → 닫힌 상자 (그래도 누르면 복습)
        OV="""()=>{ const R=e=>e.getBoundingClientRect(), A=[...document.querySelectorAll('.cpRow > .cpO:not([hidden])')].map(R), D=[...document.querySelectorAll('.stWMap .stDot, .stWMap .stWT')].map(R), x=(a,b)=>a.left<b.right-2 && b.left<a.right-2 && a.top<b.bottom-2 && b.top<a.bottom-2;
          let n=0; A.forEach((a,i)=>{ D.forEach(d=>{ if(x(a,d)) n++; }); A.forEach((b,j)=>{ if(j>i && x(a,b)) n++; }); }); return {objs:A.length, hit:n, later:!!document.querySelector('[data-rvlater]'), closed:!!document.querySelector('.cpRv.later [data-review]')}; }"""
        r=await pg.evaluate(OV); print('camp', r)
        if r['objs']<2 or r['hit'] or not r['later']: bad.append('캠프: '+json.dumps(r))
        await pg.evaluate("()=>document.querySelector('[data-rvlater]').click()"); await pg.wait_for_timeout(200)
        r=await pg.evaluate(OV); print('rvLater', r)
        if r['later'] or not r['closed'] or r['hit']: bad.append('rvLater: '+json.dumps(r))

        for b in bad: print('BAD', b)
        print('errs', real_errs(errs)[:5])
        await br.close()
        if bad or real_errs(errs): sys.exit(1)
asyncio.run(main())
