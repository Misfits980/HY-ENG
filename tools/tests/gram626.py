# v626 문법 늘리기 — 새 문법 8개(초3-4 There is·can·in/on/under·Let's · 초5-6 의문사·목적격·빈도부사·want to)가 길·노트·레슨에서 끝까지 됨
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/gram626_")
NEW = ["g34-9", "g34-10", "g34-11", "g34-12", "g56-9", "g56-10", "g56-11", "g56-12"]
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

PLAY = """async (id)=>{ const G=GramUI; let k=0;
  while(k++<200){
    if(G.mode==='cards'){ if(!G.ck){ G.ck=1; G.draw(); } else { const q=G.cq||(G.cards()[G.ci]||{}).q; if(q && !q.res){ if(q.k==='pick') G.pick(q.opts?q.opts.indexOf(q.a):q.o.indexOf(q.a)); } G.cnext ? G.cnext() : G.qnext(); } }
    else if(G.mode==='quiz'){ const q=G.qs[G.qi]; if(!q.res){ if(q.k==='pick') G.pick(q.opts.indexOf(q.a)); else if(q.k==='ox') G.ox(q.ok?'o':'x'); else if(q.k==='fix'){ const ts=q.s.split(' '); G.fixTap(ts.findIndex(t=>t.replace(/[.,!?]/g,'')===q.bad)); } else { q.pickd=q.w.map((w,i)=>i); G.ochk(); } } G.qnext(); }
    else break;
    await new Promise(r=>setTimeout(r,15)); }
  return {mode:G.mode, st:Gram.stars(id), first:G.first, n:G.n}; }"""

PLAY2 = """async (id)=>{ const G=GramUI; let k=0, seen={};
    while(k++<400 && G.mode!=='end'){
      if(G.mode==='cards'){ if(!G.ck) G.chk(); else { const q=G.cur(); if(q && q.res!=='ok' && q.k==='pick') G.pick(q.opts.indexOf(q.a)); G.cnext(); } }
      else if(G.mode==='quiz'){ const q=G.qs[G.qi]; seen[q.k]=1; if(!q.res){ if(q.k==='pick') G.pick(q.opts.indexOf(q.a)); else if(q.k==='ox') G.ox(q.ok?'o':'x'); else if(q.k==='fix'){ const ts=q.s.split(' '); G.fixTap(ts.findIndex(t=>t.replace(/[.,!?]/g,'')===q.bad)); } else { q.pickd=q.w.map((w,i)=>i); G.ochk(); } } G.qnext(); }
      else { const b=document.querySelector('#stGram [data-gr=go]'); if(b) b.click(); else break; }
      await new Promise(r=>setTimeout(r,15)); }
    return {mode:G.mode, st:Gram.stars(id), first:G.first, n:G.n, kinds:Object.keys(seen).sort().join(',')}; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nm, (w, h) in (("ph", (390, 844)), ("pad", (820, 1180))):
            pg = await b.new_page(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await boot(pg)
            r = await pg.evaluate("()=>Gram.load().then(()=>({g34:Gram.list('g34').map(g=>g.id), g56:Gram.list('g56').map(g=>g.id)}))")
            ok(len(r["g34"]) == 12 and len(r["g56"]) == 12 and all(x in r["g34"] + r["g56"] for x in NEW), f"{nm} 문법 12개씩 {r}")
            for gid in NEW:
                await pg.evaluate("(id)=>{ localStorage.removeItem('hyeng_gram_v1'); Gram.list(Gram.bookOf(id)).forEach(g=>{ if(g.id!==id) Gram.put(g.id,{s:1}); }); Online.on=()=>false; const s=Study.load(); s.book=Gram.bookOf(id); s.set=Gram.MAIN[s.book]; Study.save(); StudyUI.open(); GramUI.start(id); }", gid)
                await pg.wait_for_timeout(500)
                m = await pg.evaluate("()=>GramUI.mode")
                if nm == "ph" or gid in ("g34-9", "g56-9"):
                    await pg.screenshot(path=f"{OUT}{nm}_{gid}_card.png")
                r = await pg.evaluate("""()=>{ const c=document.querySelector('#stGram .grCard'); const sc=document.getElementById('scStudy'); return {card:!!c, ex:c?c.querySelectorAll('.grExR').length:0, hl:c?c.querySelectorAll('.grExR b u, .grExR b em, .grExR b i, .grExR mark, .grExR .hl').length:0}; }""")
                ok(m == "cards" and r["card"] and r["ex"] >= 2, f"{nm} {gid} 첫 카드 {m} {r}")
                # 카드·확인 문제 넘기기 → 퀴즈 → 끝
                res = await pg.evaluate("""async (id)=>{ const G=GramUI; let k=0, seen={};
                    while(k++<400 && G.mode!=='end'){
                      if(G.mode==='cards'){ if(!G.ck) G.chk(); else { const q=G.cur(); if(q && q.res!=='ok'){ if(q.k==='pick') G.pick(q.opts.indexOf(q.a)); else if(q.k==='ox') G.ox(q.ok?'o':'x'); } G.cnext(); } }
                      else if(G.mode==='quiz'){ const q=G.qs[G.qi]; seen[q.k]=1; if(!q.res){ if(q.k==='pick') G.pick(q.opts.indexOf(q.a)); else if(q.k==='ox') G.ox(q.ok?'o':'x'); else if(q.k==='fix'){ const ts=q.s.split(' '); G.fixTap(ts.findIndex(t=>t.replace(/[.,!?]/g,'')===q.bad)); } else { q.pickd=q.w.map((w,i)=>i); G.ochk(); } } G.qnext(); }
                      else { const b=document.querySelector('#stGram [data-gr=go]'); if(b) b.click(); else break; }
                      await new Promise(r=>setTimeout(r,15)); }
                    return {mode:G.mode, st:Gram.stars(id), first:G.first, n:G.n, kinds:Object.keys(seen)}; }""", gid)
                ok(res["mode"] == "end" and res["st"] >= 1, f"{nm} {gid} 끝까지 · 별 {res}")
                if nm == "ph":   # 높은 별(★5·★6) = 고치기·순서·섞기까지
                    for t in (3, 5):
                        await pg.evaluate("(a)=>{ Gram.put(a[0], {s:a[1]}); GramUI.start(a[0]); }", [gid, t]); await pg.wait_for_timeout(300)
                        r2 = await pg.evaluate(PLAY2, gid)
                        ok(r2["mode"] == "end" and r2["st"] == t + 1, f"{nm} {gid} ★{t+1} 끝까지 {r2}")
            # 원래 문법 16개 = 문제 27개 넘게
            r = await pg.evaluate("()=>Gram.list('g34').concat(Gram.list('g56')).filter(g=>NEWX.indexOf(g.id)<0).map(g=>g.qs.length)".replace("NEWX", str(NEW)))
            ok(len(r) == 16 and min(r) >= 27, f"{nm} 원래 문법 문제 수 {r}")
            # 중등 섞어 풀기 — 새로 문제 은행에 넣은 동명사·완료·관계대명사
            await pg.evaluate("()=>{ const v=GNote.st(); v.seen={}; v.mx={}; ['ger','perf','rel'].forEach(k=>v.seen[k]=Date.now()); GNote.put(v); }")
            await pg.evaluate("()=>GramUI.mixStart('mid')"); await pg.wait_for_timeout(1200)
            r = await pg.evaluate("()=>({mode:GramUI.mode, n:GramUI.qs.length, k:[...new Set(GramUI.qs.map(q=>q.gk))].sort().join(',')})")
            ok(r["mode"] == "quiz" and r["n"] == 10 and r["k"] == "ger,perf,rel", f"{nm} 중등 섞어 풀기 새 문법 {r}")
            if nm == "ph": await pg.screenshot(path=f"{OUT}{nm}_mix_mid_new.png")
            r2 = await pg.evaluate(PLAY2, "mix")
            ok(r2["mode"] == "end", f"{nm} 중등 섞어 풀기 끝까지 {r2}")
            e = real_errs(errs); ok(not e, f"{nm} 오류 없음 {e[:3]}")
            # 길에 문법 돌 (초3-4 Stage 4 · 초5-6 Stage 3)
            r = await pg.evaluate("()=>{ Online.on=()=>false; const s=Study.load(); s.book='g34'; s.set='elem'; Study.save(); StudyUI.open(); return new Promise(z=>setTimeout(()=>z([...document.querySelectorAll('#stPath [data-gram]')].map(x=>x.dataset.gram)), 900)); }")
            ok("g34-9" in r and "g34-12" in r, f"{nm} 초3-4 길에 새 문법 돌 {r}")
            await pg.close()
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
