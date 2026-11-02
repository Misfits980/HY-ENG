# v555 📒 문법 설명 — ① 처음 만나는 문법은 카드 먼저(아이마다 기억) ② 📒 규칙 버튼 ③ 틀리면 고른 것 ✗ → 정답 ✓ · 두 번 틀리면 카드 다시 ④ 문법 노트
import asyncio, sys
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
import importlib.util; spec=importlib.util.spec_from_file_location("q","/home/claude/hy-eng/tools/tests/qa_d30.py"); mq=importlib.util.module_from_spec(spec); spec.loader.exec_module(mq)
R=[]
def ok(c,m): R.append(bool(c)); print(("✅ " if c else "❌ ")+m)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]; pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
        await pg.evaluate("()=>{ Study.hsqLoad(); GNote.load(); Gram.load(); }"); await pg.wait_for_timeout(2500)
        c=await pg.evaluate("()=>{ const K=[].concat(...GNote.LV.map(x=>x[1])); return [K.length, K.filter(k=>GNote.cards(k).length>=1).length, K.filter(k=>GNote.cards(k).length<1)]; }")
        ok(c[0]==c[1], f"문법 {c[0]}가지 모두 설명 카드 있음 {c}")
        await pg.evaluate(mq.SETUP, ["mv1","t2"]); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ try{ KidPick.close(); }catch(e){} localStorage.removeItem(GNote.sk()); StudyUI.start(0,false); }"); await pg.wait_for_timeout(800)
        r=await pg.evaluate("""()=>{ let Q=null, q=null; for(let i=0;i<14 && !q;i++){ Q=Study._bt('mv1', i, 3); q=Q.find(x=>x.t==='gram' && GNote.keyOf(x)); } const k=GNote.keyOf(q);
           StudyUI.qs=[q, Object.assign({}, q, {retry:0}), Object.assign({}, q)]; StudyUI.i=0; StudyUI.show(); const a=StudyUI.qs[0]; return [k, a.t, a.hd, StudyUI.qs.length, document.getElementById('scStudy').scrollHeight<=844]; }""")
        k=r[0]; ok(r[1]=="intro" and r[2]=="gl" and r[3]>=4 and r[4], f"① 처음 만난 문법({k}) → 카드 먼저, 스크롤 없음 {r}")
        n=0
        while await pg.evaluate("()=>StudyUI.qs[StudyUI.i].t==='intro'") and n<4: await pg.evaluate("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(350); n+=1
        ok(await pg.evaluate("(k)=>GNote.seen(k)", k), "카드를 다 보면 배운 문법으로 기억")
        ok(await pg.evaluate("()=>!!document.querySelector('.stGlB')"), "② 문제 화면에 📒 규칙 버튼")
        await pg.evaluate("()=>document.querySelector('.stGlB').click()"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>!!document.querySelector('#glPop .grCard') && !StudyUI.locked"), "📒 누르면 카드가 겹쳐 보이고 답은 안 고른 상태")
        await pg.evaluate("()=>document.querySelector('#glPop [data-glx]').click()"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>!document.getElementById('glPop')"), "닫기")
        wrong="()=>{ const q=StudyUI.qs[StudyUI.i]; const b=[...document.querySelectorAll('.stOpt')].find(x=>x.textContent.trim()!==q.ans); b.click(); const c=document.getElementById('stCheck'); if(c && !c.classList.contains('go')) c.click(); return document.querySelector('.stCmp') ? document.querySelector('.stCmp').textContent : ''; }"
        t=await pg.evaluate(wrong); await pg.wait_for_timeout(300)
        ok("✗" in t and "✓" in t, f"③ 틀리면 고른 것 ✗ → 정답 ✓ : {t}")
        # 두 번째 틀림 → 카드 다시
        await pg.evaluate("()=>{ StudyUI.locked=false; StudyUI.i++; StudyUI.show(); while(StudyUI.qs[StudyUI.i] && StudyUI.qs[StudyUI.i].t==='intro'){ StudyUI.i++; } StudyUI.show(); }"); await pg.wait_for_timeout(300)
        await pg.evaluate(wrong); await pg.wait_for_timeout(300)
        a=await pg.evaluate("()=>{ const n=StudyUI.qs[StudyUI.i+1]; return n ? [n.t, n.hd, !!n.again] : null; }")
        ok(a==["intro","gl",True], f"같은 문법 두 번 틀리면 카드 다시 {a}")
        # 다시 열어도 처음 카드 안 나옴
        r2=await pg.evaluate("""(k)=>{ let Q=null, q=null; for(let i=0;i<14 && !q;i++){ Q=Study._bt('mv1', i, 3); q=Q.find(x=>x.t==='gram' && GNote.keyOf(x)===k); } if(!q) return 'none'; StudyUI.qs=[q]; StudyUI.i=0; StudyUI.show(); return StudyUI.qs[0].t; }""", k)
        ok(r2 in ("gram","none"), f"배운 문법은 다음 판에서 바로 문제 {r2}")
        st=await pg.evaluate("(k)=>GNote.st().s[k]", k)
        ok(st and st[1]>=1, f"맞힌 비율 기록 {st}")
        # ④ 노트
        await pg.evaluate("()=>{ StudyUI.path(); }"); await pg.wait_for_timeout(600)
        b=await pg.evaluate("()=>{ const b=document.querySelector('#stHead [data-gnote]'); return b ? b.textContent : null; }")
        ok(b and "📒" in b, f"중등 길에 📒 문법 버튼 {b}")
        await pg.evaluate("()=>GramUI.note('mid')"); await pg.wait_for_timeout(800)
        nn=await pg.evaluate("()=>[document.querySelectorAll('#stGram .glN .grNR').length, document.querySelectorAll('#stGram .glN .grNR.done').length, (document.querySelector('#stGram .stSub')||{}).textContent]")
        ok(nn[0]==30 and nn[1]>=1, f"④ 노트: 문법 30가지 · 배운 것 표시 {nn}")
        await pg.screenshot(path="/tmp/claude-0/hs/gl_note.png")
        await pg.evaluate("()=>document.querySelector('#stGram .glN .grNR').click()"); await pg.wait_for_timeout(400)
        ok(await pg.evaluate("()=>!!document.querySelector('#glPop .grCard')"), "노트에서 누르면 카드")
        await pg.evaluate("()=>GramUI.note('g56')"); await pg.wait_for_timeout(800)
        g=await pg.evaluate("()=>[document.querySelectorAll('#stGram .grNote:not(.glN) .grNR').length, document.querySelectorAll('#stGram .glN .grNR').length]")
        ok(g[0]==8 and g[1]==14, f"초5-6 노트: 문법 돌 8 + 만난 문법 14 {g}")
        ok(not errs, f"오류 없음 {errs}")
        await br.close()
    print(f"{sum(R)}/{len(R)}")
asyncio.run(main())
