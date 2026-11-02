# v552 🔼 다음 학년 도전 — 학년마다 판 끝 1문제 · 뒤 Stage 일수록 어려움 · 점수 밖 · 💎+2 는 한 번만 · 고등 문제 은행
import asyncio, sys, json
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
import importlib.util; spec=importlib.util.spec_from_file_location("q","/home/claude/hy-eng/tools/tests/qa_d30.py"); mq=importlib.util.module_from_spec(spec); spec.loader.exec_module(mq)
R=[]
def ok(c,m): R.append(bool(c)); print(("✅ " if c else "❌ ")+m)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]; pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
        await pg.evaluate("()=>{ Study.hsqLoad(); Paper.open({set:'mid',from:0,to:3}); }"); await pg.wait_for_timeout(4000); await pg.evaluate("()=>Paper.close()")
        hs=await pg.evaluate("()=>fetch('data/hsq.json').then(r=>r.json()).then(L=>[L.length, L.filter(x=>x.lv===3).length])")
        ok(hs[0]>=160 and hs[1]>=40, f"고등 문제 은행 {hs}")
        for st,nm in [("basic","초3-4"),("elem","초5-6"),("g56","중등"),("mv1","심화")]:
            r=await pg.evaluate("""(st)=>{ const L=Study.lessons(st); let n=0, got=0, bad=0, nm=''; const first=[], last=[];
               L.forEach((x,i)=>{ if(x.fin) return; n++; const q=Study._up(st, i, 3); if(!q) return; got++; nm=q.upNm; if(!q.up || q.opts.indexOf(q.ans)<0 || new Set(q.opts).size!==q.opts.length) bad++;
                 const k=q.x.gk||q.x.kind||q.t; const lv=(q.x.sh?3:0); (i<L.length/3 ? first : i>L.length*2/3 ? last : []).push(k+(lv?'#3':'')); }); return {n, got, bad, nm, first:[...new Set(first)], last:[...new Set(last)]}; }""", st)
            ok(r["got"]>=r["n"]*0.9 and r["bad"]==0 and r["nm"]==nm, f"{st} → {nm} 도전 {r['got']}/{r['n']} · 이상 {r['bad']} · 앞 {r['first']} · 뒤 {r['last']}")
        c=await pg.evaluate("()=>{ const a=Study._bt('g56', 10, 2), b=Study._bt('g56', 10, 3); return [a.length && a[a.length-1].up?1:0, b.length && b[b.length-1].up?1:0]; }")
        ok(c==[1,1], f"★3 · ★4 판 맨 끝에 도전 {c}")
        # 점수 밖 · 보석 한 번
        await pg.evaluate(mq.SETUP, ["mv1","t2"]); await pg.wait_for_timeout(800); await pg.evaluate("()=>{ try{ KidPick.close(); }catch(e){} StudyUI.start(0,false); StudyUI.view('stLesson'); }")
        await pg.evaluate("()=>{ const v=GNote.st(); [].concat(...GNote.LV.map(x=>x[1])).forEach(k=>v.seen[k]=1); GNote.put(v); }")   # (v555) 처음 카드 없이
        async def ans(right):
            return await pg.evaluate("""(right)=>{ const q=Study._up('mv1', 5, 3); Study.ctx('mv1'); StudyUI.locked=false; StudyUI.qs.splice(StudyUI.i,0,q); StudyUI.show(); const f0=StudyUI.first, w0=StudyUI._fw|0, g0=Wallet.gems();
               const b=[...document.querySelectorAll('.stOpt')].find(x=>(x.textContent.trim()===q.ans)===right); b.click(); const c=document.getElementById('stCheck'); if(c && !c.classList.contains('go')) c.click();
               const r=[StudyUI.first-f0, (StudyUI._fw|0)-w0, Wallet.gems()-g0, Object.keys(StudyUI.missed||{}).indexOf(q.w.en)>=0]; StudyUI.locked=false; StudyUI.i++; return r; }""", right)
        a=await ans(False); ok(a[:2]==[0,0] and a[2]==0 and not a[3], f"틀려도 점수·틀린 단어에 안 들어감 {a}")
        b=await ans(True); ok(b[0]==0 and b[2]==2, f"맞히면 💎+2 (점수엔 안 들어감) {b}")
        c2=await ans(True); ok(c2[2]==0, f"같은 판에서 또 맞혀도 보석은 한 번만 {c2}")
        ok(not errs, f"오류 없음 {errs}")
        await br.close()
    print(f"{sum(R)}/{len(R)}")
asyncio.run(main())
