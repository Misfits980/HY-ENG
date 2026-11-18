"""(v710) 📕 책 전체 시험 — 사용자: 「책 끝날 때 볼 시험지 (예: 초5-6 리딩 2권 전체) · 스토리형 문제도 · 50문제 100문제 두 개로 A안 B안 · 우리 프린터를 고려해서」
   ① 모든 책 × A안·B안 × 학원 프린터용·보통: 오류 0 · 50/100문제(모자라면 안내) · 넘친 단 0 · 학원용은 글이 쪽 끝에서 27mm 위 · 100점
   ② 리딩 2: Ⅰ단어 Ⅱ문장 Ⅲ문법 Ⅳ이야기 · 글 3편/6편 · 글마다 빈칸(손으로 고른 보기) ⭕❌ 2 · 제목/요약 · 생각 쓰기 2 · 빈칸 답 = 글에서 뺀 낱말
   ③ Stage 묶음마다 고르게 (단어 문제가 없는 Stage 없음) · 답안지 「Stage별 맞은 수」 번호 = 모든 문제 한 번씩
   ④ 답안지 = 문제 정답 (번호마다) · A·B형 기본 끔 → 📝 시험지로 가면 원래 A·B형 설정
   ⑤ 인쇄 나누기: 시험지만 / 답안지만 PDF 쪽 수 · 🔄 바꾸기 (이야기는 안 바뀜)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

INFO = r"""()=>{ const W=document.getElementById('ppWrap'), B=Paper.B, c=Paper.c, mm=96/25.4;
  const low=[...W.querySelectorAll('.pp')].map(p=>{ const pr=p.getBoundingClientRect(), z=pr.height/Math.max(1,p.offsetHeight); let mx=pr.top; p.querySelectorAll('.ppCol *, .ppKC *').forEach(e=>{ const r=e.getBoundingClientRect(); if(r.height>0 && r.bottom>mx) mx=r.bottom; }); return +((pr.bottom-mx)/z/mm).toFixed(1); });
  return {info:(document.getElementById('ppInfo')||{}).textContent||'', total:B ? B.total : -1, max:c && c.max, n:c && c.n, pages:W.querySelectorAll('.pp').length, key:W.querySelectorAll('.pp.key').length, bad:Paper.bad(), low:Math.min(...low.slice(0, -1).concat([99])),
    parts:B ? B.S.filter(s=>s.part).map(s=>[s.part, s.partN]) : [], st:B ? B.S.filter(s=>s.k==='rd').length : 0}; }"""

async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch()
        ctx=await br.new_context(viewport={"width":1280,"height":900}); pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await boot(pg); E=pg.evaluate
        await pg.add_script_tag(path=os.path.join(SITE, "lib", "html2canvas.min.js"))
        await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} }"); await pg.wait_for_timeout(2500)
        sets=await E("()=>Paper.psets()")
        # ① 모든 책 × A·B × 두 인쇄 모양
        for ver in ("school", "normal"):
            await E("(v)=>localStorage.setItem('hyeng_pp_ver', v)", ver)
            for s in sets:
                for plan in ("a", "b"):
                    await E("(a)=>{ localStorage.setItem('hyeng_paper', JSON.stringify({set:a[0], mode:'bk', bkPlan:a[1]})); Paper.open({mode:'bk', set:a[0]}); }", [s, plan])
                    await pg.wait_for_timeout(900)
                    for _ in range(12):
                        r=await E(INFO)
                        if "받는 중" not in r["info"]: break
                        await pg.wait_for_timeout(500)
                    want=50 if plan=="a" else 100
                    full = r["total"]==want and r["max"]==100
                    short = r["total"]<want and "모자라" in r["info"]
                    lowok = ver!="school" or r["low"]>=27
                    ok((full or short) and not r["bad"] and lowok and r["key"]>=1 and len(r["parts"])>=1,
                       f"① {ver} {s} {plan}: {r['total']}/{want}문제 {r['max']}점 · {r['pages']}쪽(답안지 {r['key']}) · 넘침 {r['bad']} · 아래 {r['low']}mm · {r['parts']} 글 {r['st']}" + ("" if full else " · "+r["info"][-60:]))
        # ② 리딩 2 내용
        await E("()=>localStorage.setItem('hyeng_pp_ver', 'school')")
        for plan, nst in (("a", 3), ("b", 6)):
            await E("(a)=>{ localStorage.setItem('hyeng_paper', JSON.stringify({set:'rd2', mode:'bk', bkPlan:a})); Paper.open({mode:'bk', set:'rd2'}); }", plan); await pg.wait_for_timeout(2500)
            r=await E("""()=>{ const B=Paper.B, S=B.S.filter(s=>s.k==='rd'); const D=(Paper.RDST||{}).rd2||{};
              const chk=S.map(s=>{ const qs=s.qs, bq=qs.find(q=>q.lab && q.lab.length===4 && q.u!=='rd'); const tok=bq && bq.ans; const st=Object.values(D).map(L=>L[0]).find(x=>x.bl && x.bl[0]===tok);
                return {n:qs.length, ox:qs.filter(q=>q.fix && q.lab[0]==='O').length, tcsm:qs.filter(q=>q.lab && q.lab.length===3).length, th:qs.filter(q=>q.ow).length, blank:!!bq, inPsg:!!tok && s.pre.indexOf('( ⓐ )')>0 && s.pre.indexOf('>'+tok+'<')<0 && !new RegExp('\\\\b'+tok+'\\\\b').test(s.pre.replace(/<[^>]+>/g,'')), cur:!!st && JSON.stringify(st.bl)===JSON.stringify(bq.lab)}; });
              return {parts:B.S.filter(s=>s.part).map(s=>s.part), chk}; }""")
            c=r["chk"]
            ok(r["parts"]==["Ⅰ 단어","Ⅱ 문장","Ⅲ 문법","Ⅳ 이야기"] and len(c)==nst and all(x["blank"] and x["inPsg"] and x["cur"] and x["ox"]==2 and x["tcsm"]==1 for x in c) and sum(x["th"] for x in c)==2,
               f"② 리딩 2 {plan}안: {r['parts']} · 글 {len(c)}편 · 빈칸(손으로 고른 보기·글에서 뺌)·⭕❌2·제목/요약·생각 2 {c}")
            # ③ Stage 고르게 · 답안지 Stage 표
            u=await E("""()=>{ const B=Paper.B, U={}; B.S.forEach(s=>{ if(s.k!=='rd') s.qs.forEach(q=>{ U[q.u]=(U[q.u]||0)+1; }); });
              const rows=[...document.querySelectorAll('#ppWrap .ppKU .ppKUr')].map(r=>[r.querySelector('b').textContent, r.querySelector('span').textContent.split(' · ').map(Number)]);
              const all=[].concat(...rows.map(r=>r[1])).sort((a,b)=>a-b); return {U, nU:Paper.c.unm.length, rows:rows.length, all:all.length, uniq:new Set(all).size, tot:B.total, max:Math.max(...all)}; }""")
            ok(len(u["U"])==u["nU"] and min(u["U"].values())>=(2 if plan=="a" else 4) and u["rows"]==u["nU"]+1 and u["all"]==u["tot"]==u["uniq"]==u["max"],
               f"③ {plan}안 Stage 12개 모두 단어·문장·문법 문제 {u['U']} · 답안지 표 {u['rows']}줄 · 번호 {u['all']}개 = 문제 {u['tot']} (겹침 없음)")
            # ④ 답안지 = 정답
            k=await E("""()=>{ const forms=[...document.querySelectorAll('#ppWrap .pp:not(.key)')]; const Q=[...document.querySelectorAll('#ppWrap .pp:not(.key) .ppQ .ppNo')].map(x=>+x.textContent.replace('.','')).filter(Boolean);
              const K=[...document.querySelectorAll('#ppWrap .pp.key .ppKS span i')].map(x=>+x.textContent); const F=Paper.form(Paper.B, Paper.rnd(Paper.seed+1)); let wrong=0, n=0;
              F.forEach(s=>s.qs.forEach(q=>{ n++; if(q.lab && q.lab[q.a]!==q.ans) wrong++; if(q.opts && q.opts[q.a]!==q.w) wrong++; })); return {q:Q.length, k:K.length, n, wrong, seq:Q.every((x,i)=>x===i+1)}; }""")
            ok(k["q"]==k["k"]==k["n"] and k["wrong"]==0 and k["seq"], f"④ {plan}안 문제 {k['q']}개 = 답안지 {k['k']}개 · 정답 어긋남 {k['wrong']} · 번호 차례대로 {k['seq']}")
        ab=await E("()=>[document.getElementById('ppAB').checked, (()=>{ document.querySelector('#ppMd [data-v=test]').click(); return document.getElementById('ppAB').checked; })()]")
        ok(ab[0] is False and ab[1] is True, f"④ 책 시험 A·B형 기본 끔 · 📝 시험지로 가면 원래 설정(켬) {ab}")
        # ⑤ 인쇄 나누기 · 바꾸기
        await E("()=>{ localStorage.setItem('hyeng_paper', JSON.stringify({set:'rd2', mode:'bk', bkPlan:'a'})); Paper.open({mode:'bk', set:'rd2'}); }"); await pg.wait_for_timeout(2500)
        res={}
        for out in ("test", "key", "all"):
            await E("(o)=>{ const S=document.getElementById('ppOut'); S.value=o; S.dispatchEvent(new Event('change',{bubbles:true})); }", out); await pg.wait_for_timeout(1500)
            await E("()=>{ Paper._pdfF=null; Paper.pdf(); }")
            for _ in range(90):
                await pg.wait_for_timeout(500)
                if await E("()=>!!Paper._pdfF && !Paper._pdfBusy"): break
            res[out]=await E("()=>[(document.getElementById('ppPdf')||{}).textContent.match(/(\\d+)쪽/)[1]|0, Paper._pdfF && Paper._pdfF.name, Paper._pdfF && Paper._pdfF.size, document.querySelectorAll('#ppWrap .pp:not(.key)').length, document.querySelectorAll('#ppWrap .pp.key').length]")
            await E("()=>{ const o=document.getElementById('ppPdf'); if(o) o.remove(); }")
        t, kk, a = res["test"], res["key"], res["all"]
        ok(t[0]==t[3] and kk[0]==kk[4] and a[0]==a[3]+a[4] and "답안지" in kk[1] and a[2] < 1.6e6, f"⑤ 인쇄 나누기: 시험지만 {t[0]}쪽 · 답안지만 {kk[0]}쪽 ({kk[1]}) · 전부 {a[0]}쪽 {a[2]//1024}KB")
        sw=await E("""()=>{ const B=Paper.B; const si=B.S.findIndex(s=>s.k==='mean'), ri=B.S.findIndex(s=>s.k==='rd'); const old=B.S[si].qs[0].w.en; const r1=B.swap(si, 0); const nw=B.S[si].qs[0].w.en;
          const q=document.querySelector('#ppWrap .ppPg'); const g=q && q.closest('.ppGrp'); return [r1, old!==nw, B.S[si].qs[0].u!=null, document.querySelectorAll('#ppWrap .ppGrp .ppPg ~ .ppQ[data-src]').length]; }""")
        ok(sw[0] and sw[1] and sw[2] and sw[3]==0, f"⑤ 🔄 단어 문제 바꾸기 됨 · Stage 표시 그대로 · 이야기 문제엔 바꾸기 없음 {sw}")
        await br.close()
    print("errs", errs[:3])
    print("BAD:", len(bad))
    sys.exit(1 if bad or errs else 0)
asyncio.run(main())
