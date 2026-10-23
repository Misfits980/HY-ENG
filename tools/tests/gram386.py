"""(v386) 📒 문법 곁가지 — G3-4 8개 · G5-6 8개 (data/gram.json)
  · 단어 길(elem · g56) 🚩 옆 땅에 「쉬어 가기」 돌 + 샛길 · 첫 곁가지는 열림, 나머지는 앞 곁가지를 끝내거나 붙은 Stage 를 시작하면 열림
  · 설명 카드 → 같이 해 보기(틀려도 다시) → 혼자 풀기 8문제(틀리면 3문제 뒤 한 번 더) → 별 · 💎(처음 3, 처음 ★3 2) · 기록 전송
  · 📒 문법 노트 · 문제 중 📒 규칙 · 모든 곁가지의 모든 문제 유형을 실제로 풀어 봄"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

ANS = """(wrong)=>{ const U=GramUI, q=U.cur(); if(!q) return 'none';
  if(q.k==='pick'){ let k=q.opts.indexOf(q.a); if(wrong) k=q.opts.findIndex(o=>o!==q.a); document.querySelector('#stGram [data-gk="'+k+'"]').click(); }
  else if(q.k==='ox'){ let v=q.ok?'o':'x'; if(wrong) v=v==='o'?'x':'o'; document.querySelector('#stGram [data-gox="'+v+'"]').click(); }
  else if(q.k==='order'){ const seq=q.w.map((w,i)=>i); if(wrong){ const t=seq[0]; seq[0]=seq[1]; seq[1]=t; } seq.forEach(i=>document.querySelector('#stGram .grTiles [data-gt="'+i+'"]').click()); const c=document.querySelector('#stGram [data-gr=ochk]'); if(c) c.click(); }
  else if(q.k==='fix'){ const toks=q.s.split(' '), st=t=>t.replace(/[.,!?]/g,''); let k=toks.findIndex(t=>st(t)===q.bad); if(wrong) k=(k+1)%toks.length; document.querySelector('#stGram [data-gf="'+k+'"]').click(); }
  return q.k+':'+(q.res||'-'); }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    D = json.load(open(os.path.join(SITE, "data", "gram.json"), encoding="utf-8"))
    ok(len(D["g34"]) == 8 and len(D["g56"]) == 8, "문법 G3-4 8개 · G5-6 8개")
    sw = open(os.path.join(SITE, "sw.js"), encoding="utf-8").read()
    ok("./data/gram.json" in sw, "서비스워커: 문법 자료 저장")
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("window.HY_FB_LOCAL=true; window._subs=[];")
        await boot(pg)
        await pg.evaluate("()=>{ const f=Online.submit.bind(Online); Online.submit=function(r){ window._subs.push(r); return Promise.resolve({ok:true}); }; window.confirm=()=>true; Voice.speak=()=>true; }")
        await pg.evaluate("()=>{ const s=Study.load(); s.book='g34'; s.set='elem'; Study.save(); StudyUI.open(); }")
        await pg.wait_for_timeout(900)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#stMap .grWN')].map(b=>[b.querySelector('[data-gram]').dataset.gram, b.classList.contains('lock')])")
        ok(len(r) == 8 and r[0] == ["g34-1", False] and all(x[1] for x in r[1:]), f"G3-4 길: 곁가지 8개 · 첫째만 열림 {r[:3]}")
        ok(await pg.evaluate("()=>!!document.querySelector('[data-gnote=g34]')"), "📒 문법 노트 버튼")
        # 잠긴 곁가지 누르면 안내만
        await pg.evaluate("()=>document.querySelector('[data-gram=\"g34-2\"]').click()"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>document.getElementById('stGram').style.display==='none'"), "잠긴 곁가지는 열리지 않음")
        # 첫 곁가지
        await pg.evaluate("()=>document.querySelector('[data-gram=\"g34-1\"]').click()"); await pg.wait_for_timeout(400)
        ok(await pg.evaluate("()=>document.getElementById('stGram').style.display!=='none' && !!document.querySelector('#stGram .grCard')"), "곁가지 열면 설명 카드")
        # 📒 규칙 열고 닫기
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=peek]').click()")
        ok(await pg.evaluate("()=>document.querySelectorAll('#stGram .grPeek .grCard').length") == 2, "📒 규칙: 설명 카드 2장")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=unpeek]').click()")
        # 설명 → 같이 해 보기
        n = await pg.evaluate("()=>GramUI.cards().length")
        for i in range(n - 1): await pg.evaluate("()=>document.querySelector('#stGram [data-gr=next]').click()")
        ok(await pg.evaluate("()=>GramUI.cur() && GramUI.cur().k==='pick'"), "설명 다음은 같이 해 보기")
        await pg.evaluate(ANS, True)
        ok(await pg.evaluate("()=>GramUI.cur().res===null && !!document.querySelector('#stGram .stOpt.bad')"), "같이 해 보기: 틀리면 다시 고를 수 있음")
        for i in range(2):
            await pg.evaluate(ANS, False); await pg.evaluate("()=>document.querySelector('#stGram [data-gr=tnext]').click()")
        ok(await pg.evaluate("()=>GramUI.mode==='quiz' && GramUI.qs.length===8"), "혼자 풀기 8문제")
        kinds = await pg.evaluate("()=>GramUI.qs.map(q=>q.k).join(',')")
        ok(kinds == "pick,pick,ox,pick,order,ox,pick,order", "G3-4 순서: 고르기 4 · OX 2 · 순서 2 " + kinds)
        # 첫 문제 틀리고 나머지 맞힘
        await pg.evaluate(ANS, True)
        ok(await pg.evaluate("()=>GramUI.qs.length===9 && GramUI.qs[3].again===1"), "틀리면 3문제 뒤에 한 번 더")
        ok(await pg.evaluate("()=>!!document.querySelector('#stGram .grFb.bad [data-gr=peek]')"), "틀리면 📒 규칙 다시 보기 버튼")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=qnext]').click()")
        for i in range(20):
            if await pg.evaluate("()=>GramUI.mode") != "quiz": break
            await pg.evaluate(ANS, False); await pg.evaluate("()=>document.querySelector('#stGram [data-gr=qnext]').click()")
        g0 = await pg.evaluate("()=>Wallet.gems()")
        r = await pg.evaluate("()=>[GramUI.mode, GramUI.first, GramUI.n, Gram.stars('g34-1'), GramUI.res.gem]")
        ok(r[0] == "end" and r[1] == 7 and r[3] == 2 and r[4] == 3, f"7/8 → ★2 · 💎3 {r}")
        sub = await pg.evaluate("()=>window._subs.slice(-1)[0]")
        ok(sub and sub.get("rule") == "study-grammar" and "G3-4 문법 · a / an" in sub.get("set", "") and sub.get("right") == 7, f"기록 전송 {sub and sub.get('set')}")
        ok(await pg.evaluate("()=>!!document.querySelector('#stGram [data-gram=\"g34-2\"]')"), "끝나면 다음 문법이 열림 (다음 문법 버튼)")
        # 다시 하기 → 모두 맞힘 → ★3 · 💎2 더
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=again]').click()"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ GramUI.build(); GramUI.mode='quiz'; GramUI.draw(); }")
        for i in range(20):
            if await pg.evaluate("()=>GramUI.mode") != "quiz": break
            await pg.evaluate(ANS, False); await pg.evaluate("()=>document.querySelector('#stGram [data-gr=qnext]').click()")
        r = await pg.evaluate("()=>[Gram.stars('g34-1'), GramUI.res.gem]")
        ok(r == [3, 2], f"다 맞히면 ★3 · 💎2 더 (처음 한 번) {r}")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=again]').click()"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ GramUI.build(); GramUI.mode='quiz'; GramUI.draw(); }")
        for i in range(20):
            if await pg.evaluate("()=>GramUI.mode") != "quiz": break
            await pg.evaluate(ANS, False); await pg.evaluate("()=>document.querySelector('#stGram [data-gr=qnext]').click()")
        ok(await pg.evaluate("()=>GramUI.res.gem") == 0, "세 번째는 보석 없음")
        # 길로 돌아가기 → 둘째 열림
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=home]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#stMap .grWN')].slice(0,3).map(b=>b.className)")
        ok("done" in r[0] and "lock" not in r[1] and "lock" in r[2], f"길: 첫째 끝 · 둘째 열림 · 셋째 잠김 {r}")
        # 붙은 Stage 를 시작하면 열림 (Stage 5 → this/that)
        opened = await pg.evaluate("()=>{ const x=Study.lessons('elem').find(x=>x.wd==5); const o=Study.lv; Study.lv=(st,n)=>(st==='elem'&&n===x.n)?1:o.call(Study,st,n); const r=Gram.open('g34-4'); Study.lv=o; return r; }")
        ok(opened, "붙은 Stage 를 시작(★1)하면 그 곁가지가 열림")
        # 문법 노트
        await pg.evaluate("()=>document.querySelector('[data-gnote=g34]').click()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[document.querySelectorAll('#stGram .grNR').length, document.querySelectorAll('#stGram .grNR.done').length, document.querySelectorAll('#stGram .grNR.lock').length]")
        ok(r == [8, 1, 6], f"문법 노트: 8개 · 끝 1 · 잠김 6 {r}")
        await pg.evaluate("()=>document.querySelector('#stGram [data-gr=home]').click()"); await pg.wait_for_timeout(200)
        # G5-6 길
        await pg.evaluate("()=>{ StudyUI.book='g56'; StudyUI.set='g56'; StudyUI.path(); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#stMap .grWN [data-gram]')].map(b=>b.dataset.gram)")
        ok(len(r) == 8 and r[0] == "g56-1", f"G5-6 길: 곁가지 8개 {r[:2]}")
        await pg.evaluate("()=>{ StudyUI.set='rd1'; StudyUI.path(); }"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>!document.querySelector('#stMap .grWN') && !!document.querySelector('[data-gnote=g56]')"), "리딩 책: 곁가지 없이 📒 문법 노트만")
        # 모든 곁가지 · 모든 문제를 실제 화면으로 풀어 보기 (맞힘)
        res = await pg.evaluate("""async (ANS)=>{ const f=eval(ANS); const out=[]; for(const bk of ['g34','g56']) for(const g of Gram.list(bk)){
            GramUI.g=g; GramUI.mode='quiz'; GramUI.peek=false; StudyUI.view('stGram'); GramUI.qs=g.qs.map(q=>GramUI.prep(Object.assign({}, q))); GramUI.qi=0; GramUI.first=0; GramUI.n=GramUI.qs.length; GramUI.miss=[]; GramUI.t0=Date.now(); GramUI.draw();
            for(let i=0;i<g.qs.length;i++){ f(false); const q=GramUI.qs[i]; if(q.res!=='ok') out.push(g.id+' '+i+' '+q.k+' '+(q.s||q.w.join(' '))); document.querySelector('#stGram [data-gr=qnext]').click(); }
            if(GramUI.mode!=='end') out.push(g.id+' 끝 안 남'); }
          return out; }""", ANS)
        ok(res == [], f"모든 곁가지의 모든 문제(238개)를 정답으로 풀 수 있음 {res[:4]}")
        # G5-6 구성 · 틀린 단어 찾기 화면
        await pg.evaluate("()=>{ GramUI.g=Gram.get('g56-1'); GramUI.build(); GramUI.mode='quiz'; GramUI.draw(); }")
        ok(await pg.evaluate("()=>GramUI.qs.map(q=>q.k).join(',')") == "pick,pick,ox,order,pick,ox,fix,order", "G5-6 순서: 틀린 단어 찾기 포함")
        await pg.evaluate("()=>{ GramUI.qi=GramUI.qs.findIndex(q=>q.k==='fix'); GramUI.draw(); }")
        await pg.evaluate(ANS, True); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("()=>!!document.querySelector('#stGram .grFx b') && !!document.querySelector('#stGram .grFT.ok')"), "틀린 단어 찾기: 틀리면 고친 말을 보여 줌")
        await pg.screenshot(path=OUT + "gram386_fix.png")
        await pg.evaluate("()=>{ GramUI.qi=GramUI.qs.findIndex(q=>q.k==='order'); const q=GramUI.qs[GramUI.qi]; q.res=null; q.pickd=[]; GramUI.draw(); }")
        await pg.evaluate("()=>document.querySelector('#stGram .grTiles .grT').click()")
        await pg.screenshot(path=OUT + "gram386_order.png")
        ok(not real_errs(errs), f"스크립트 오류 없음 {errs[:2]}")
        await br.close()
    print("\nFAIL" if bad else "\nALL OK", bad)
    sys.exit(1 if bad else 0)
asyncio.run(main())
