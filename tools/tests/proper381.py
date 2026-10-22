"""(v381) 사용자: 고유명사는 대문자로 바꿔야 (Monday · China · Rome) — 자료·저장 키는 소문자 그대로, 보이는 곳만 (v322 dispEn)
  v322 뒤에도 소문자로 보이던 곳: 확인 판 단어 목록 · 비슷한 말/헷갈리는 짝 같은 글자 보기 · 문장 순서 조각(첫 조각을 소문자로 바꾸던 것) · 교실 배틀·레이드 보기 · 달리기 단어판
  → Daily 30 모든 책·★0~3 의 고유명사 Stage 를 화면에 그려서 소문자 고유명사가 없는지"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
JS = r"""(LV)=>{ Voice.canListen=()=>true; Voice.broken=false; const P=Object.keys(PROPER), re=new RegExp("(^|[^A-Za-z])("+P.join("|")+")(?![A-Za-z])"); const out={}; let n=0;
  const sets=[].concat(...Object.keys(Study.BOOKS).map(k=>Study.BOOKS[k].sets)).filter((v,i,a)=>a.indexOf(v)===i);
  sets.forEach(st=>{ let L=[]; try{ L=Study.lessons(st); }catch(e){ return; }
    L.forEach((x,i)=>{ if(!x.ws.some(w=>PROPER[String(w.en).toLowerCase()])) return; const s=Study.load(), K=Study.key(st,x.n); s.seen={}; if(LV>0) x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[K]=Math.max(0,LV); Study.save();
      StudyUI.book=Study.bookOf(st); StudyUI.set=st; try{ StudyUI.start(i,false); }catch(e){ return; }
      StudyUI.qs.forEach((q,j)=>{ StudyUI.i=j; StudyUI.locked=false; try{ StudyUI.show(); }catch(e){ return; } n++; const d=document.getElementById('stQ'); const t=d.innerText+' '+[...d.querySelectorAll('[data-say]')].map(b=>'').join('');
        const m=t.replace(/china \((도)?자기\)/g,'').match(re);   /* 도자기 china 는 소문자가 맞음 */ if(m){ const k=q.t+':'+m[2]; if(!out[k]) out[k]=[st, q.w&&q.w.en, t.replace(/\s+/g,' ').slice(0,160)]; } }); }); });
  return {n, out}; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(500)
        for LV in (0, 1, 2, 3):
            r = await pg.evaluate(JS, LV)
            ok(r["n"] > 300 and not r["out"], f"★{LV}: 문제 {r['n']}개 화면에 소문자 고유명사 없음 {list(r['out'].items())[:3]}")
        r = await pg.evaluate("()=>[StudyUI.odShow('Africa'), StudyUI.odShow('Monday.'), StudyUI.odShow('The'), StudyUI.odShow('Grandma')]")
        ok(r == ["Africa", "Monday", "the", "grandma"], f"문장 순서 조각: 고유명사는 대문자 그대로 · 다른 첫 말은 소문자 {r}")
        r = await pg.evaluate("""()=>{ const got=[]; const f=CanvasRenderingContext2D.prototype.fillText; CanvasRenderingContext2D.prototype.fillText=function(t){ got.push(String(t)); return f.apply(this, arguments); };
            try{ signCanvasPlain('monday'); signCanvasPlain('apple'); } finally { CanvasRenderingContext2D.prototype.fillText=f; } return got; }""")
        ok("Monday" in r and "monday" not in r and "apple" in r, f"달리기 단어판 {r}")
        r = await pg.evaluate("()=>[Study.word('monday') ? Study.word('monday').en : null, WORD_BANK.some(w=>w.en==='monday')]")
        ok(r == ["monday", True], f"자료 키는 그대로 소문자 (저장 기록 그대로) {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
