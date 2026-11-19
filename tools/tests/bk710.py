"""(v710) 📕 책 전체 시험 — 사용자: 「책 끝날 때 볼 시험지 (예: 초5-6 리딩 2권 전체) · 스토리형 문제도 · 50문제 100문제 두 개로 A안 B안 · 우리 프린터를 고려해서」
   ① 모든 책 × A안·B안 × 학원 프린터용·보통: 오류 0 · 50/100문제(모자라면 안내) · 넘친 단 0 · 학원용은 글이 쪽 끝에서 27mm 위 · 100점
   ② 리딩 2: Ⅰ단어 Ⅱ문장 Ⅲ문법 Ⅳ이야기 · 글 3편/6편 · 글마다 빈칸(손으로 고른 보기) ⭕❌ 2 · 제목/요약 · 생각 쓰기 2 · 빈칸 답 = 글에서 뺀 낱말
   ③ Stage 묶음마다 고르게 (단어 문제가 없는 Stage 없음) · 답안지 「Stage별 맞은 수」 번호 = 모든 문제 한 번씩
   ④ 답안지 = 문제 정답 (번호마다) · A·B형 기본 끔 → 📝 시험지로 가면 원래 A·B형 설정
   ⑤ 인쇄 나누기: 시험지만 / 답안지만 PDF 쪽 수 · 🔄 바꾸기 (이야기는 안 바뀜)
   (v711) 사용자 「시험지 개선이 더 필요해」 → 고른 것 넷
   ⑥ 이야기 = 글 하나 + 그 문제를 한 쪽에 (글은 위 넓게 · 문제 번호 범위 = 그 쪽 문제) · 글마다 세부 내용 · 순서 맞추기 · ⭕❌ 는 문장 끝 O · X
   ⑦ ✍️ 답 적는 칸 = 시험지 끝 한 쪽 (칸 수 = 문제 수 · ✎ = 쓰는 문제) · 답안지 정답 번호표 · 끄면 없음 · 머리에 시험 시간·푸는 법
   ⑧ 단어 고르기: 아래 학년 책에도 있는 단어는 뒤로 · 「반이 자주 틀린 단어 더」 = 선생님 기기 기록의 이 책 단어가 먼저 · 기록 없으면 안내 · 책 시험 과거형 = 불규칙 먼저
   (v712) ⑨ G3-4 · G1-2 도 이야기 (rdst.json elem · basic): 글 3/6편 · G3-4 글마다 빈칸 · O·X 2 · 세부 내용/제목 번갈아 · 생각 = 한 낱말 칸 · G1-2 빈칸 · O·X 2 · 생각 = 둘 중 ○
      · 글 + 그 문제는 한 단에 붙어서(갈라지지 않음 · 번호 범위 = 그 덩어리 문제) · G1-2 글은 한 문장씩 한 줄 · 답 적는 칸 ✎ = 생각 · 답안지 예시 답"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

INFO = r"""()=>{ const W=document.getElementById('ppWrap'), B=Paper.B, c=Paper.c, mm=96/25.4;
  const low=[...W.querySelectorAll('.pp')].map(p=>{ const pr=p.getBoundingClientRect(), z=pr.height/Math.max(1,p.offsetHeight); let mx=pr.top; p.querySelectorAll('.ppCol *, .ppKC *, .ppTop *, .ppAns *').forEach(e=>{ const r=e.getBoundingClientRect(); if(r.height>0 && r.bottom>mx) mx=r.bottom; }); return +((pr.bottom-mx)/z/mm).toFixed(1); });
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
                return {n:qs.length, ox:qs.filter(q=>q.fix && q.lab[0]==='O' && q.oxi).length, tcsm:qs.filter(q=>q.lab && q.lab.length===3).length, th:qs.filter(q=>q.ow).length, blank:!!bq,
                  wh:qs.filter(q=>/ppKo/.test(q.html) && q.lab && q.lab.length===4).length, sq:qs.filter(q=>/ppSq/.test(q.html) && q.lab.length===4 && q.lab.indexOf(q.ans)>=0).length, inPsg:!!tok && s.pre.indexOf('( ⓐ )')>0 && s.pre.indexOf('>'+tok+'<')<0 && !new RegExp('\\\\b'+tok+'\\\\b').test(s.pre.replace(/<[^>]+>/g,'')), cur:!!st && JSON.stringify(st.bl)===JSON.stringify(bq.lab)}; });
              return {parts:B.S.filter(s=>s.part).map(s=>s.part), chk}; }""")
            c=r["chk"]
            ok(r["parts"]==["Ⅰ 단어","Ⅱ 문장","Ⅲ 문법","Ⅳ 이야기"] and len(c)==nst and all(x["blank"] and x["inPsg"] and x["cur"] and x["ox"]==2 and x["tcsm"]==1 and x["wh"]==1 and x["sq"]==1 for x in c) and sum(x["th"] for x in c)==2,
               f"② 리딩 2 {plan}안: {r['parts']} · 글 {len(c)}편 · 빈칸(손으로 고른 보기·글에서 뺌)·⭕❌2(문장 끝)·세부 내용·순서·제목/요약·생각 2 {c}")
            # ③ Stage 고르게 · 답안지 Stage 표
            u=await E("""()=>{ const B=Paper.B, U={}; B.S.forEach(s=>{ if(s.k!=='rd') s.qs.forEach(q=>{ U[q.u]=(U[q.u]||0)+1; }); });
              const rows=[...document.querySelectorAll('#ppWrap .ppKU .ppKUr')].map(r=>[r.querySelector('b').textContent, r.querySelector('span').textContent.split(' · ').map(Number)]);
              const all=[].concat(...rows.map(r=>r[1])).sort((a,b)=>a-b); return {U, nU:Paper.c.unm.length, rows:rows.length, all:all.length, uniq:new Set(all).size, tot:B.total, max:Math.max(...all)}; }""")
            ok(len(u["U"])==u["nU"] and min(u["U"].values())>=(1 if plan=="a" else 3) and u["rows"]==u["nU"]+1 and u["all"]==u["tot"]==u["uniq"]==u["max"],
               f"③ {plan}안 Stage 12개 모두 단어·문장·문법 문제 {u['U']} · 답안지 표 {u['rows']}줄 · 번호 {u['all']}개 = 문제 {u['tot']} (겹침 없음)")
            # ④ 답안지 = 정답
            k=await E("""()=>{ const forms=[...document.querySelectorAll('#ppWrap .pp:not(.key)')]; const Q=[...document.querySelectorAll('#ppWrap .pp:not(.key) .ppQ .ppNo')].map(x=>+x.textContent.replace('.','')).filter(Boolean);
              const K=[...document.querySelectorAll('#ppWrap .pp.key .ppKS span i')].map(x=>+x.textContent); const F=Paper.form(Paper.B, Paper.rnd(Paper.seed+1)); let wrong=0, n=0;
              F.forEach(s=>s.qs.forEach(q=>{ n++; if(q.lab && q.lab[q.a]!==q.ans) wrong++; if(q.opts && q.opts[q.a]!==q.w) wrong++; })); return {q:Q.length, k:K.length, n, wrong, seq:Q.every((x,i)=>x===i+1)}; }""")
            ok(k["q"]==k["k"]==k["n"] and k["wrong"]==0 and k["seq"], f"④ {plan}안 문제 {k['q']}개 = 답안지 {k['k']}개 · 정답 어긋남 {k['wrong']} · 번호 차례대로 {k['seq']}")
            # ⑥ 이야기 쪽 · ⑦ 답 적는 칸
            st=await E("""()=>{ const P=[...document.querySelectorAll('#ppWrap .pp:not(.key)')]; const S=P.filter(p=>p.querySelector('.ppTop .ppPg'));
              const one=S.map(p=>{ const m=(p.querySelector('.ppRg')||{}).textContent.match(/(\\d+)~(\\d+)/); const N=[...p.querySelectorAll('.ppCol .ppNo')].map(x=>parseInt(x.textContent)); return !!m && N.length===(+m[2])-(+m[1])+1 && N[0]===+m[1] && p.querySelectorAll('.ppCol .ppPg').length===0; });
              const G=P.filter(p=>p.querySelector('.ppAns')), cells=G.length ? G[0].querySelectorAll('.ppAG span').length : 0, w=G.length ? G[0].querySelectorAll('.ppAG span.w').length : 0;
              const KG=document.querySelectorAll('#ppWrap .pp.key .ppKGg span').length, hdN=!!document.querySelector('#ppWrap .ppHdN'), oxi=document.querySelectorAll('#ppWrap .pp:not(.key) .ppQ.oxi .ppOXc').length;
              const qn=document.querySelectorAll('#ppWrap .pp:not(.key) .ppQ .ppNo').length, wq=[...document.querySelectorAll('#ppWrap .pp:not(.key) .ppQ')].filter(q=>!q.querySelector('ol.ppOp') && !q.querySelector('.ppOXc')).length;
              return {S:S.length, one:one.every(Boolean), G:G.length, last:P[P.length-1]===G[0], cells, w, wq, KG, hdN, oxi, qn, tot:Paper.B.total}; }""")
            ok(st["S"]==nst and st["one"] and st["oxi"]==2*nst, f"⑥ {plan}안 이야기 {st['S']}쪽 · 글 하나 = 한 쪽(번호 범위 = 그 쪽 문제 · 글은 위) {st['one']} · 문장 끝 O·X {st['oxi']}")
            ok(st["G"]==1 and st["last"] and st["cells"]==st["tot"]==st["qn"] and st["w"]==st["wq"] and st["KG"]==st["tot"] and st["hdN"], f"⑦ {plan}안 답 적는 칸 = 마지막 쪽 · 칸 {st['cells']}개 = 문제 {st['qn']} · ✎ {st['w']} = 쓰는 문제 {st['wq']} · 정답 번호표 {st['KG']} · 안내 줄 {st['hdN']}")
        # ⑦ 끄면 없음
        await E("()=>{ const g=document.getElementById('ppGrid'); g.checked=false; g.dispatchEvent(new Event('change',{bubbles:true})); }"); await pg.wait_for_timeout(1500)
        r=await E("()=>[document.querySelectorAll('#ppWrap .ppAns').length, document.querySelectorAll('#ppWrap .ppKG').length, !!document.querySelector('#ppWrap .ppNote'), JSON.parse(localStorage.getItem('hyeng_paper')).bkGrid]")
        ok(r[0]==0 and r[1]==0 and r[3] is False, f"⑦ 답 적는 칸 끄면 없음 · 기억 {r}")
        await E("()=>{ const g=document.getElementById('ppGrid'); g.checked=true; g.dispatchEvent(new Event('change',{bubbles:true})); }"); await pg.wait_for_timeout(1200)
        # ⑧ 쉬운 단어 뒤로 · 반 오답 · 불규칙
        r=await E("""()=>{ const ez=Paper.bkEasy('g56')||{}, B=Paper.B; const W=[]; B.S.filter(s=>s.k!=='rd').forEach(s=>s.qs.forEach(q=>{ if(q.w && q.w.en) W.push(q.w.en); }));
          const U=Paper.bkUnits('rd2'), all=Object.keys(U.of), hard=all.filter(e=>!ez[e.toLowerCase()]).length;
          const V=B.S.filter(s=>s.k==='vform').flatMap(s=>s.qs.map(q=>q.w)), irr=V.filter(w=>Paper.irr(Paper.vf(w))).length;
          return {ezN:Object.keys(ez).length, used:W.filter(e=>ez[e.toLowerCase()]).length, n:W.length, hard, irr, nv:V.length}; }""")
        ok(r["ezN"]>200 and r["used"]<=1 and r["irr"]==r["nv"], f"⑧ 아래 학년 책 단어 {r['ezN']}개 → 이 시험에 {r['used']}/{r['n']}개 (책에 쉽지 않은 단어 {r['hard']}개) · 과거형 불규칙 {r['irr']}/{r['nv']}")
        await E("()=>localStorage.removeItem('hyeng_admin_rep')")
        await E("()=>{ const S=document.getElementById('ppBkW'); S.value='miss'; S.dispatchEvent(new Event('change',{bubbles:true})); }"); await pg.wait_for_timeout(1500)
        r=await E("()=>document.getElementById('ppInfo').textContent")
        ok("반 오답 기록이 없어요" in r, f"⑧ 반 오답 기록 없으면 안내 · {r[-60:]}")
        await E("""()=>{ localStorage.setItem('hyeng_admin_rep', JSON.stringify({at:Date.now(), d:{miss:[["단어","틀린 수"],["avocado",7],["pollen",5],["Origami",4],["zebra",3],["posture",2]]}})); const S=document.getElementById('ppBkW'); S.dispatchEvent(new Event('change',{bubbles:true})); }"""); await pg.wait_for_timeout(1500)
        r=await E("""()=>{ const W=[]; Paper.B.S.filter(s=>s.k!=='rd').forEach(s=>s.qs.forEach(q=>{ if(q.w && q.w.en) W.push(q.w.en); })); return [document.getElementById('ppInfo').textContent.match(/반 오답 단어 (\\d+)개/), ['avocado','pollen','origami','posture'].filter(e=>W.indexOf(e)>=0), JSON.parse(localStorage.getItem('hyeng_paper')).bkW]; }""")
        ok(r[0] and int(r[0][1])==4 and len(r[1])>=3 and r[2]=="miss", f"⑧ 반이 자주 틀린 단어 더: 이 책 단어 4개 먼저(zebra 는 책에 없음) · 시험에 {r[1]} · 기억 {r[2]}")
        await E("()=>{ const S=document.getElementById('ppBkW'); S.value='even'; S.dispatchEvent(new Event('change',{bubbles:true})); localStorage.removeItem('hyeng_admin_rep'); }"); await pg.wait_for_timeout(1200)
        ab=await E("()=>[document.getElementById('ppAB').checked, (()=>{ document.querySelector('#ppMd [data-v=test]').click(); return document.getElementById('ppAB').checked; })()]")
        ok(ab[0] is False and ab[1] is True, f"④ 책 시험 A·B형 기본 끔 · 📝 시험지로 가면 원래 설정(켬) {ab}")
        # ⑨ G3-4 · G1-2 이야기
        await E("()=>localStorage.setItem('hyeng_pp_ver', 'school')")
        for bk, parts, per in (("elem", ["Ⅰ 단어","Ⅱ 문장","Ⅲ 문법","Ⅳ 이야기"], 4), ("basic", ["Ⅰ 단어","Ⅱ 문장","Ⅲ 이야기"], 3)):
            for plan, nst in (("a", 3), ("b", 6)):
                await E("(a)=>{ localStorage.setItem('hyeng_paper', JSON.stringify({set:a[0], mode:'bk', bkPlan:a[1]})); Paper.open({mode:'bk', set:a[0]}); }", [bk, plan]); await pg.wait_for_timeout(2500)
                r=await E("""(bk)=>{ const B=Paper.B, S=B.S.filter(s=>s.k==='rd'), D=(Paper.RDST||{})[bk]||{};
                  const chk=S.map(s=>{ const qs=s.qs, bq=qs.find(q=>q.lab && q.lab.length===4 && q.u!=='rd'), tok=bq && bq.ans, st=Object.values(D).map(L=>L[0]).find(x=>x.bl && x.bl[0]===tok);
                    return {n:qs.filter(q=>!q.ow).length, ox:qs.filter(q=>q.oxi).length, th:qs.filter(q=>q.ow).length, thk:qs.filter(q=>q.ow).map(q=>/ppCh/.test(q.html) ? 'ch' : /ppThk fr/.test(q.html) ? 'fr' : '?').join(''), wh:qs.filter(q=>/ppKo/.test(q.html) && q.lab && q.lab.length===4).length, tc:qs.filter(q=>q.lab && q.lab.length===3).length,
                      cur:!!st && JSON.stringify(st.bl)===JSON.stringify(bq.lab), gone:!!tok && !new RegExp('\\b'+tok+'\\b').test(s.pre.replace(/<[^>]+>/g,'')), keep:!!s.keep, l1:/ppPg l1/.test(s.pre), ln:(s.pre.match(/class="ln"/g)||[]).length}; });
                  const G=[...document.querySelectorAll('#ppWrap .ppKeep')].map(g=>{ const m=(g.querySelector('.ppRg')||{}).textContent.match(/(\\d+)~(\\d+)/), N=[...g.querySelectorAll('.ppNo')].map(x=>parseInt(x.textContent)); return !!m && N[0]===+m[1] && N[N.length-1]===+m[2] && N.length===(+m[2])-(+m[1])+1 && !!g.closest('.ppCol') && !!g.querySelector('.ppPg'); });
                  const key=[...document.querySelectorAll('#ppWrap .pp.key')].map(k=>k.textContent).join(' ');
                  return {parts:B.S.filter(s=>s.part).map(s=>s.part), chk, G, tot:B.total, bad:Paper.bad(), key:(key.match(/\(예시\)/g)||[]).length, full:document.querySelectorAll('#ppWrap .ppTop .ppPg').length}; }""", bk)
                c=r["chk"]
                lv1=bk=="basic"
                good=r["parts"]==parts and len(c)==nst and r["tot"]==(50 if plan=="a" else 100) and not r["bad"] and r["full"]==0 and len(r["G"])==nst and all(r["G"]) and r["key"]==2 \
                  and all(x["cur"] and x["gone"] and x["keep"] and x["ox"]==2 and x["n"]==per and (x["wh"]+x["tc"]==(0 if lv1 else 1)) and x["l1"]==lv1 and x["ln"]==(3 if lv1 else 0) for x in c) \
                  and "".join(x["thk"] for x in c)==("chch" if lv1 else "frfr")
                ok(good, f"⑨ {bk} {plan}안: {r['parts']} · {r['tot']}문제 · 글 {len(c)}편(한 단에 붙음 {r['G']}) · 글마다 {[(x['n'], x['ox'], x['wh'], x['tc']) for x in c]} · 생각 {[x['thk'] for x in c]} · 답안지 예시 {r['key']} · 넘침 {r['bad']}")
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
