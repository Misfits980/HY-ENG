"""(v386) 📒 문법 쉬어 가기 — G3-4 8개 · G5-6 8개 (data/gram.json)
  · 단어 길(elem · g56) 중간 돌(1-2) 옆 땅에 문법 돌 + 샛길 · 첫 문법은 열림, 나머지는 앞 문법 ★1 · 붙은 Stage 시작(★1)이면 열림
  · 별 6개 · 별마다 💎5 · ★1 배우기(설명 전부 → 같이 해 보기 → 5문제, 💡 힌트) · ★2부터 「기억나요?」 → 문제 (단계마다 어렵게)
  · ★2 연습 6 · ★3 순서 포함 8 · ★4 틀린 단어 찾기 8 · ★5 앞 문법 섞어 10 · ★6 어려운 문제 10 (90%)
  · 못 넘으면 별 없음 · 모든 문제를 실제 화면으로 풀어 봄"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

ANS = """(wrong)=>{ const U=GramUI, q=U.cur(); if(!q) return 'none';
  if(q.k==='pick'){ let k=q.opts.indexOf(q.a); if(wrong) k=q.opts.findIndex(o=>o!==q.a); document.querySelector('#stGram [data-gk="'+k+'"]').click(); }
  else if(q.k==='ox'){ let v=q.ok?'o':'x'; if(wrong) v=v==='o'?'x':'o'; document.querySelector('#stGram [data-gox="'+v+'"]').click(); }
  else if(q.k==='order'){ const seq=q.w.map((w,i)=>i); if(wrong){ const t=seq[0]; seq[0]=seq[1]; seq[1]=t; } seq.forEach(i=>document.querySelector('#stGram .grTiles [data-gt="'+i+'"]').click()); const c=document.querySelector('#stGram [data-gr=ochk]'); if(c) c.click(); }
  else if(q.k==='fix'){ const toks=q.s.split(' '), st=t=>t.replace(/[.,!?]/g,''); let k=toks.findIndex(t=>st(t)===q.bad); if(wrong) k=(k+1)%toks.length; document.querySelector('#stGram [data-gf="'+k+'"]').click(); }
  return q.k+':'+(q.res||'-'); }"""
# 혼자 풀기 끝까지 — wrongIdx 에 있는 문제(처음 번호)만 틀림
RUNQ = """async (a)=>{ const [ANS, wrong]=a; const f=eval(ANS); let i=0, seen=0;
  for(let g=0; g<40 && GramUI.mode==='quiz'; g++){ const q=GramUI.cur(); const w=!q.again && wrong.indexOf(seen)>=0; if(!q.again) seen++; f(w); document.querySelector('#stGram [data-gr=qnext]').click(); }
  return GramUI.mode; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    D = json.load(open(os.path.join(SITE, "data", "gram.json"), encoding="utf-8"))
    ok(len(D["g34"]) == 8 and len(D["g56"]) == 8, "문법 G3-4 8개 · G5-6 8개")
    ok(all(sum(1 for q in g["qs"] if q.get("hd")) >= 3 and sum(1 for q in g["qs"] if q["k"] == "fix") >= 2 for g in D["g34"] + D["g56"]), "문법마다 어려운 문제 3 · 틀린 단어 찾기 2 이상")
    ok(any(c.get("h", "").startswith("누가") for c in next(g for g in D["g34"] if g["id"] == "g34-3")["cards"]), "be동사: 누가(주어) 바꾸기 카드")
    ok(any("지금 vs 매일" in c.get("h", "") for c in next(g for g in D["g56"] if g["id"] == "g56-1")["cards"]), "-ing: 언제 써요(지금 vs 매일) 카드")
    sw = open(os.path.join(SITE, "sw.js"), encoding="utf-8").read()
    ok("./data/gram.json" in sw, "서비스워커: 문법 자료 저장")
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("window.HY_FB_LOCAL=true; window._subs=[];")
        await boot(pg)
        await pg.evaluate("()=>{ Online.submit=function(r){ window._subs.push(r); return Promise.resolve({ok:true}); }; window.confirm=()=>true; Voice.speak=()=>true; }")
        await pg.evaluate("()=>{ const s=Study.load(); s.book='g34'; s.set='elem'; Study.save(); StudyUI.open(); }")
        await pg.wait_for_timeout(900)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#stMap .grWN')].map(b=>[b.querySelector('[data-gram]').dataset.gram, b.classList.contains('lock')])")
        ok(len(r) == 8 and r[0] == ["g34-1", False] and all(x[1] for x in r[1:]), f"G3-4 길: 문법 돌 8개 · 첫째만 열림 {r[:3]}")
        ok(await pg.evaluate("()=>!!document.querySelector('[data-gnote=g34]')"), "📒 문법 노트 버튼")
        await pg.evaluate("()=>document.querySelector('[data-gram=\"g34-2\"]').click()"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>document.getElementById('stGram').style.display==='none'"), "잠긴 문법은 열리지 않음")
        # ── ★1 배우기
        await pg.evaluate("()=>document.querySelector('[data-gram=\"g34-1\"]').click()"); await pg.wait_for_timeout(400)
        ok(await pg.evaluate("()=>GramUI.tier===1 && GramUI.mode==='cards' && !!document.querySelector('#stGram .grCard')"), "★1: 설명 카드부터")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=peek]').click()")
        ok(await pg.evaluate("()=>document.querySelectorAll('#stGram .grPeek .grCard').length") == 3, "📒 규칙: 설명 카드 3장")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=unpeek]').click()")
        n = await pg.evaluate("()=>GramUI.cards().length")
        for i in range(n - 1): await pg.evaluate("()=>document.querySelector('#stGram [data-gr=next]').click()")
        await pg.evaluate(ANS, True)
        ok(await pg.evaluate("()=>GramUI.cur().res===null && !!document.querySelector('#stGram .stOpt.bad')"), "같이 해 보기: 틀리면 다시 고를 수 있음")
        for i in range(2):
            await pg.evaluate(ANS, False); await pg.evaluate("()=>document.querySelector('#stGram [data-gr=tnext]').click()")
        r = await pg.evaluate("()=>[GramUI.mode, GramUI.qs.length, GramUI.qs.every(q=>q.k==='pick'||q.k==='ox'), GramUI.qs.some(q=>q.hd), !!document.querySelector('#stGram .grHint')]")
        ok(r == ["quiz", 5, True, False, True], f"★1: 쉬운 5문제(고르기·OX) · 💡 힌트 보임 {r}")
        g0 = await pg.evaluate("()=>Wallet.gems()")
        m = await pg.evaluate(RUNQ, [ANS, [0]])
        r = await pg.evaluate("()=>[GramUI.mode, GramUI.first, Gram.stars('g34-1'), GramUI.res.gem, Wallet.gems()]")
        ok(r[0] == "end" and r[1] == 4 and r[2] == 1 and r[3] == 5 and r[4] - g0 == 5, f"★1: 4/5 → 별 1 · 💎5 {r}")
        sub = await pg.evaluate("()=>window._subs.slice(-1)[0]")
        ok(sub and sub.get("rule") == "study-grammar" and "G3-4 문법 · a / an ★1" in sub.get("set", "") and sub.get("clear") == 1, f"기록 전송 {sub and sub.get('set')}")
        ok(await pg.evaluate("()=>!!document.querySelector('#stGram [data-gram=\"g34-2\"]')"), "★1 받으면 다음 문법도 열림")
        # ── ★2: 「기억나요?」 먼저
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=again]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[GramUI.tier, GramUI.mode, document.querySelectorAll('#stGram .grRecap .grExR').length, (document.querySelector('#stGram .grGoal')||{}).textContent]")
        ok(r[0] == 2 and r[1] == "recap" and r[2] == 3 and "★2 연습" in (r[3] or ""), f"★2: 바로 문제 X → 「기억나요?」 요약 {r}")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=full]').click()"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>GramUI.mode==='cards' && GramUI.tier===2"), "📒 자세히 → 설명 카드 전부 (별 단계는 그대로)")
        await pg.evaluate("()=>{ GramUI.start('g34-1'); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=go]').click()")
        r = await pg.evaluate("()=>[GramUI.qs.length, !!document.querySelector('#stGram .grHint')]")
        ok(r == [6, False], f"★2: 6문제 · 힌트 안 보임 {r}")
        await pg.evaluate(RUNQ, [ANS, [0, 1, 2]])
        r = await pg.evaluate("()=>[Gram.stars('g34-1'), GramUI.res.pass, GramUI.res.gem, !!document.querySelector('#stGram [data-gr=full]')]")
        ok(r == [1, False, 0, True], f"★2 못 넘음(3/6): 별 그대로 · 규칙 보고 다시 하기 {r}")
        # ★2 ~ ★6 다 맞히기
        kinds = {}
        for t in range(2, 7):
            await pg.evaluate("()=>{ GramUI.start('g34-1'); }"); await pg.wait_for_timeout(250)
            await pg.evaluate("()=>document.querySelector('#stGram [data-gr=go]').click()")
            kinds[t] = await pg.evaluate("()=>[GramUI.qs.length, GramUI.qs.map(q=>q.k).filter((v,i,a)=>a.indexOf(v)===i).sort().join(','), GramUI.qs.filter(q=>q.hd).length]")
            await pg.evaluate(RUNQ, [ANS, []])
        r = await pg.evaluate("()=>[Gram.stars('g34-1'), Wallet.gems()]")
        ok(r[0] == 6 and r[1] - g0 == 30, f"별 6개 · 💎 5×6=30 {r} {kinds}")
        ok(kinds[3][0] == 8 and "order" in kinds[3][1], f"★3: 8문제 · 순서 맞추기 {kinds[3]}")
        ok(kinds[4][0] == 8 and "fix" in kinds[4][1], f"★4: 8문제 · 틀린 단어 찾기 {kinds[4]}")
        ok(kinds[5][0] == 10, f"★5: 10문제 {kinds[5]}")
        ok(kinds[6][0] == 10 and kinds[6][2] >= 3, f"★6: 10문제 · 어려운 문제 3 {kinds[6]}")
        await pg.evaluate("()=>{ GramUI.start('g34-1'); }"); await pg.wait_for_timeout(250)
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=go]').click()"); await pg.evaluate(RUNQ, [ANS, []])
        ok(await pg.evaluate("()=>GramUI.res.gem===0 && Gram.stars('g34-1')===6"), "별 6개 뒤 다시 하면 보석 없음")
        # ★5 섞어서: 앞 문법 문제가 섞임
        await pg.evaluate("()=>{ Gram.put('g34-2', {s:4}); GramUI.start('g34-2'); }"); await pg.wait_for_timeout(250)
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=go]').click()")
        r = await pg.evaluate("()=>[GramUI.tier, GramUI.qs.filter(q=>q.from==='a / an').length]")
        ok(r == [5, 4], f"★5: 앞에서 배운 문법(a / an) 4문제 섞임 {r}")
        await pg.evaluate("()=>{ GramUI.qi=GramUI.qs.findIndex(q=>q.from); GramUI.draw(); }")
        ok(await pg.evaluate("()=>!!document.querySelector('#stGram .grFrom')"), "섞인 문제에 「앞에서 배운 …」 표시")
        # 길: 별 6 표시 · 노트
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=quit]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#stMap .grWN')].slice(0,3).map(b=>b.className+'|'+b.querySelector('.stWS').textContent)")
        ok("done" in r[0] and "★★★" in r[0] and "lock" not in r[1], f"길: 별 표시 · 둘째 열림 {r}")
        await pg.evaluate("()=>document.querySelector('[data-gnote=g34]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[document.querySelectorAll('#stGram .grNR').length, document.querySelectorAll('#stGram .grNR.done').length]")
        ok(r == [8, 2], f"문법 노트: 8개 · 별 받은 것 2 {r}")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=home]').click()"); await pg.wait_for_timeout(200)
        opened = await pg.evaluate("()=>{ const x=Study.lessons('elem').find(x=>x.wd==5); const o=Study.lv; Study.lv=(st,n)=>(st==='elem'&&n===x.n)?1:o.call(Study,st,n); const r=Gram.open('g34-4'); Study.lv=o; return [r, Gram.open('g34-5')]; }")
        ok(opened == [True, False], f"붙은 Stage 를 시작(★1)하면 그 문법이 열림 {opened}")
        # G5-6 · 리딩
        await pg.evaluate("()=>{ StudyUI.book='g56'; StudyUI.set='g56'; StudyUI.path(); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#stMap .grWN [data-gram]')].map(b=>b.dataset.gram)")
        ok(len(r) == 8 and r[0] == "g56-1", f"G5-6 길: 문법 돌 8개 {r[:2]}")
        await pg.evaluate("()=>{ StudyUI.set='rd1'; StudyUI.path(); }"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>!document.querySelector('#stMap .grWN') && !!document.querySelector('[data-gnote=g56]')"), "리딩 책: 돌 없이 📒 문법 노트만")
        # 모든 문제 풀어 보기
        res = await pg.evaluate("""async (ANS)=>{ const f=eval(ANS); const out=[]; for(const bk of ['g34','g56']) for(const g of Gram.list(bk)){
            GramUI.g=g; GramUI.tier=2; GramUI.full=false; GramUI.mode='quiz'; GramUI.peek=false; StudyUI.view('stGram'); GramUI.qs=g.qs.map(q=>GramUI.prep(Object.assign({}, q))); GramUI.qi=0; GramUI.first=0; GramUI.n=GramUI.qs.length; GramUI.miss=[]; GramUI.t0=Date.now(); GramUI.draw();
            for(let i=0;i<g.qs.length;i++){ f(false); const q=GramUI.qs[i]; if(q.res!=='ok') out.push(g.id+' '+i+' '+q.k+' '+(q.s||q.w.join(' '))); document.querySelector('#stGram [data-gr=qnext]').click(); }
            if(GramUI.mode!=='end') out.push(g.id+' 끝 안 남'); }
          return out; }""", ANS)
        ok(res == [], f"모든 문법의 모든 문제(302개)를 정답으로 풀 수 있음 {res[:4]}")
        # '안 붙여요' 정답 문장
        r = await pg.evaluate("()=>GramUI.right({k:'pick', s:'I drink ___ water.', a:'-'})")
        ok(r == "I drink water.", f"「안 붙여요」 정답 문장 {r}")
        # 화면 저장
        await pg.evaluate("()=>{ Gram.put('g56-1',{s:3}); GramUI.start('g56-1'); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT + "gram386_recap.png")
        await pg.evaluate("()=>{ GramUI.start('g34-3', true); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ GramUI.ci=3; GramUI.draw(); }"); await pg.screenshot(path=OUT + "gram386_who.png")
        ok(not real_errs(errs), f"스크립트 오류 없음 {errs[:2]}")
        await br.close()
    print("\nFAIL" if bad else "\nALL OK", bad)
    sys.exit(1 if bad else 0)
asyncio.run(main())
