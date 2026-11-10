# v651 중등 문법 코스 — 단원 자유 선택 · ★4 부터 ⌨️ 직접 쓰기 · 검사기(tools/check_gram.py)
import asyncio, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
OUT = os.environ.get("HY_OUT", "/tmp/gram651_")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

# 문제를 끝까지 (wrong = 직접 쓰기 첫 문제를 일부러 틀림)
PLAY = """async (opt)=>{ const G=GramUI; let k=0, wr=0, log=[];
  while(k++<400 && G.mode!=='end'){
    if(G.mode==='recap'){ document.querySelector('[data-gr=go]').click(); }
    else if(G.mode==='cards'){ if(!G.ck) G.chk(); else { const q=G.cur(); if(q.res==='ok') G.cnext(); else G.pick(q.opts.indexOf(q.a)); } }
    else if(G.mode==='quiz'){ const q=G.qs[G.qi]; if(!q.res){ log.push(q.k);
        if(q.k==='pick') G.pick(q.opts.indexOf(q.a)); else if(q.k==='ox') G.ox(q.ok?'o':'x');
        else if(q.k==='fix'){ const ts=q.s.split(' '); G.fixTap(ts.findIndex(t=>t.replace(/[.,!?]/g,'')===q.bad)); }
        else if(q.k==='write'){ wr++; const a=(opt.wrong && wr===1 && !q.again) ? 'zz' : (opt.alt && q.alt ? q.alt[0] : q.a); for(const c of a) document.querySelector('#stGram [data-gw="'+(c==="'"?"\\\\'":c)+'"]').click(); document.querySelector('[data-gr=wchk]').click(); }
        else { q.pickd=q.w.map((x,i)=>i); G.ochk(); } } else G.qnext(); }
    else break; await new Promise(r=>setTimeout(r,8)); }
  return {mode:G.mode, log, res:G.res}; }"""

async def main():
    c = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "check_gram.py")], capture_output=True, text=True)
    print(c.stdout.strip().split("\n")[-1]); ok(c.returncode == 0, "검사기: ❌ 오류 0 (g34 · g56 · mid)")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ Online.on=()=>true; window.__sub=[]; Online.submit=r=>{ window.__sub.push(r); return Promise.resolve({ok:true}); }; localStorage.removeItem('hyeng_gram_v1'); return Gram.load(); }")
        r = await pg.evaluate("()=>({n:Gram.list('mid').length, open:Gram.list('mid').every(g=>Gram.open(g.id)), k:Gram.list('mid').map(g=>g.qs.filter(q=>q.k==='write').length), g34:Gram.open('g34-5'), t4:Gram.tiers('mid')[4].mix.write, e4:Gram.tiers('g34')[4].mix.write||0})")
        ok(r["n"] >= 23 and r["open"] and r["t4"] == 3 and r["e4"] == 0, f"중등 단원 {r['n']}개 · 처음부터 다 열림 · 직접 쓰기 문제 · 초등 단계는 그대로 {r}")
        ok(r["g34"] is False, "초등 문법은 예전처럼 잠김")
        # 노트 = 코스 목록
        await pg.evaluate("()=>{ StudyUI.book='mid'; StudyUI.set=Study.BOOKS.mid.sets[0]; StudyUI.open(); GramUI.note('mid'); }"); await pg.wait_for_timeout(600)
        r = await pg.evaluate("()=>[document.querySelectorAll('#stGram .grNR').length, document.querySelectorAll('#stGram .grNR.lock').length, document.querySelector('#stGram .stSub').textContent, document.querySelector('#stGram .grNoteP').textContent]")
        ok(r[0] >= 4 and r[1] == 0 and "0 / " in r[2] and "어느 단원이든" in r[3], f"📒 노트에 중등 단원 목록 (잠금 없음) {r[:3]}"); await pg.screenshot(path=OUT + "note_ph.png")
        r = await pg.evaluate("()=>[[...document.querySelectorAll('#stGram .grSec')].map(x=>x.textContent), [...document.querySelectorAll('#stGram .grNR[data-gram]')].map(x=>x.dataset.gram)]")
        ok(r[0] == ["중등 문법", "어법 심화", "초등 문법 복습 · 직접 쓰기"] and r[1][0] == "mid-11" and r[1][-4:] == ["mid-1", "mid-2", "mid-3", "mid-4"], f"묶음 3개 · 새 주제 먼저 · 초등 복습은 맨 아래 {r[0]} {r[1][:3]}")
        # (v652) 이미 만들어 둔 중·고등 자료로 만든 단원: 모든 단원 × 모든 단계가 문제 수를 채우고, 한 판에 같은 문장이 두 번 안 나옴
        r = await pg.evaluate("""()=>{ const G=GramUI, bad=[]; let nq=0; Gram.list('mid').forEach(g=>{ for(let t=1;t<=6;t++){ for(let rep=0;rep<4;rep++){ G.g=g; G.tier=t; G.build(); const T=G.T(), sids=G.qs.filter(q=>q.sid!=null && !q.from).map(q=>q.sid);
              if(G.qs.length!==T.n) bad.push(g.id+' ★'+t+' '+G.qs.length+'/'+T.n); if(new Set(sids).size!==sids.length) bad.push(g.id+' ★'+t+' 같은 문장 두 번'); nq+=G.qs.length;
              G.qs.forEach(q=>{ try{ if(!G.qHtml(q,false) || !G.right(q)) bad.push(g.id+' 그리기'); }catch(e){ bad.push(g.id+' '+e.message); } }); } } });
            G.mode='note'; return {bad:bad.slice(0,6), nq, units:Gram.list('mid').length, cards:Gram.list('mid').every(g=>g.cards.length>=3 && g.cards.every(c=>c.q && c.q.o.indexOf(c.q.a)>=0))}; }""")
        ok(not r["bad"] and r["cards"], f"단원 {r['units']}개 × ★1~6 × 4번 = {r['nq']}문제 모두 그려짐 · 수 맞음 · 겹침 없음 {r['bad']}")
        await pg.evaluate("()=>{ GramUI.start('mid-15'); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate(PLAY, {}); ok(r["mode"] == "end" and r["res"]["pass"], f"현재완료(만들어 둔 자료) ★1 통과 {r['log']}")
        await pg.evaluate("()=>{ Gram.put('mid-15', {s:3}); GramUI.start('mid-15'); }"); await pg.wait_for_timeout(300); await pg.evaluate("()=>document.querySelector('[data-gr=go]').click()"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>GramUI.qs.map(q=>q.k)"); ok(r.count("write") == 3, f"현재완료 ★4 = 직접 쓰기 3 {r}")
        await pg.evaluate("()=>{ Gram.put('mid-19', {s:1}); GramUI.start('mid-19'); }"); await pg.wait_for_timeout(300); await pg.evaluate("()=>document.querySelector('[data-gr=go]').click()"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("""()=>{ const G=GramUI; G.qi=G.qs.findIndex(q=>q.k==='pick' && q.wr); G.draw(); const q=G.cur(), bad=q.opts.findIndex(o=>o!==q.a && q.wr[o]); G.pick(bad); return [(document.querySelector('#stGram .grFbW.no')||{}).textContent||'', q.opts[bad], q.wr[q.opts[bad]]]; }""")
        ok(r[1] in r[0] and r[2] in r[0], f"틀리면 내가 고른 보기가 왜 틀렸는지 「{r[0]}」"); await pg.screenshot(path=OUT + "wr_ph.png")
        await pg.evaluate("()=>GramUI.note('mid')"); await pg.wait_for_timeout(400)
        # 3번째 단원부터 시작해도 됨 → ★1
        await pg.click('#stGram [data-gram="mid-3"]'); await pg.wait_for_timeout(300)
        r = await pg.evaluate(PLAY, {}); ok(r["mode"] == "end" and r["res"]["pass"] and r["res"]["tier"] == 1 and "write" not in r["log"], f"mid-3 ★1 (고르기·⭕❌만) {r['log']}")
        s = await pg.evaluate("()=>window.__sub.slice(-1)[0].set"); ok(s.startswith("중등 문법 · 과거시제 ★1"), f"기록 이름 {s}")
        # ★4 = 직접 쓰기
        await pg.evaluate("()=>{ Gram.put('mid-3', {s:3}); GramUI.start('mid-3'); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>document.querySelector('[data-gr=go]').click()"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>GramUI.qs.map(q=>q.k)"); ok(r.count("write") == 3 and r.count("fix") == 2 and len(r) == 8, f"★4 문제 = 직접 쓰기 3 · 고치기 2 {r}")
        await pg.evaluate("()=>{ const G=GramUI; G.qi=G.qs.findIndex(q=>q.k==='write'); G.draw(); }"); await pg.wait_for_timeout(150)
        q = await pg.evaluate("()=>{ const q=GramUI.cur(); return {s:q.s, a:q.a}; }")
        r = await pg.evaluate("()=>[document.querySelectorAll('#stGram .stOpt').length, document.querySelectorAll('#stGram [data-gw]').length, document.querySelector('[data-gr=wchk]').disabled, (document.querySelector('#stGram .grCue')||{}).textContent||'', document.querySelector('#stGram .grS').textContent.includes('(')]")
        ok(r[0] == 0 and r[1] == 29 and r[2] and "힌트" in r[3] and not r[4], f"보기 없음 · 자판 · 힌트는 따로 {r}")
        fit = await pg.evaluate("()=>{ const S=document.getElementById('scStudy'); return [S.scrollHeight-S.clientHeight, Math.round(document.querySelector('[data-gr=wchk]').getBoundingClientRect().bottom), innerHeight]; }")
        ok(fit[0] <= 1 and fit[1] <= fit[2], f"휴대폰: 직접 쓰기 화면 스크롤 없음 {fit}"); 
        await pg.keyboard.type("Zz"); await pg.keyboard.press("Backspace"); await pg.keyboard.type("x")
        r = await pg.evaluate("()=>GramUI.cur().got"); ok(r == "zx", f"진짜 자판도 됨 (소문자로) {r}"); await pg.screenshot(path=OUT + "write_ph.png")
        await pg.keyboard.press("Enter"); await pg.wait_for_timeout(150)
        r = await pg.evaluate("()=>[GramUI.cur().res, (document.querySelector('#stGram .grWrMine')||{}).textContent||'', document.querySelector('#stGram .grFbS').textContent, GramUI.qs.length]")
        ok(r[0] == "bad" and "zx" in r[1] and q["a"] in r[2].lower() and "(" not in r[2] and r[3] == 9, f"틀리면 내가 쓴 것 · 정답 문장(힌트 괄호 없이) · 뒤에 다시 {r}"); await pg.screenshot(path=OUT + "write_bad_ph.png")
        # 줄임말 ↔ 풀어 쓴 말 · 문장 처음 대문자
        r = await pg.evaluate("""()=>{ const G=GramUI, mk=o=>{ const q=G.prep(Object.assign({k:'write', ko:'', w:''}, o)); G.qs=[q]; G.qi=0; G.mode='quiz'; G.draw(); return q; }; const out=[];
            let q=mk({s:'She ___ meat. (not, eat)', a:"doesn't eat", alt:['does not eat']}); 'does  not eat '.split('').forEach(c=>G.wkey(c)); G.wchk(); out.push(q.res);
            q=mk({s:'She ___ meat. (not, eat)', a:"doesn't eat", alt:['does not eat']}); "doesn't eat".split('').forEach(c=>G.wkey(c)); G.wchk(); out.push(q.res);
            q=mk({s:'___ you ready now? (be)', a:'are'}); 'are'.split('').forEach(c=>G.wkey(c)); const shown=document.querySelector('#stGram .grBl').textContent.trim(); G.wchk(); out.push(q.res, shown, G.right(q));
            q=mk({s:'She ___ meat. (not, eat)', a:"doesn't eat"}); "dont eat".split('').forEach(c=>G.wkey(c)); G.wchk(); out.push(q.res); return out; }""")
        ok(r == ["ok", "ok", "ok", "Are", "Are you ready now?", "bad"], f"풀어 쓴 말도 정답 · 빈칸 두 번 무시 · 문장 처음은 대문자로 보임 {r}")
        # ★4 끝까지 (풀어 쓴 말로) → ★5 섞어서(다른 단원) → ★6
        for tier, st in ((4, 3), (5, 4), (6, 5)):
            await pg.evaluate("(s)=>{ Gram.put('mid-3', {s}); Gram.put('mid-1', {s:1}); GramUI.start('mid-3'); }", st); await pg.wait_for_timeout(250)
            r = await pg.evaluate(PLAY, {"alt": True, "wrong": tier == 4})
            ok(r["mode"] == "end" and r["res"]["tier"] == tier and r["res"]["pass"] and "write" in r["log"], f"★{tier} 통과 (직접 쓰기 {r['log'].count('write')}문제 · 처음 맞힌 비율 {round(r['res']['pct']*100)}%)")
        await pg.screenshot(path=OUT + "end_ph.png")
        r = await pg.evaluate("()=>Gram.stars('mid-3')"); ok(r == 6, f"별 6개 {r}")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        # 5화면: 직접 쓰기 문제가 화면 안 (가장 긴 문장으로)
        for nm, vp in (("phL", (915, 412)), ("pad", (820, 1180)), ("padL", (1180, 820)), ("se", (375, 667)), ("tv", (1920, 1080))):
            await pg.set_viewport_size({"width": vp[0], "height": vp[1]}); await pg.wait_for_timeout(200)
            await pg.evaluate("""()=>{ const G=GramUI; G.g=Gram.get('mid-1'); G.tier=4; G.peek=false; const qs=[].concat(...Gram.list('mid').map(g=>g.qs.filter(q=>q.k==='write'))).sort((a,b)=>b.s.length-a.s.length); const q=G.prep(Object.assign({}, qs[0])); G.qs=[q]; G.qi=0; G.mode='quiz'; StudyUI.view('stGram'); G.draw(); 'were'.split('').forEach(c=>G.wkey(c)); document.getElementById('scStudy').scrollTop=0; }""")
            await pg.wait_for_timeout(150)
            fit = await pg.evaluate("()=>{ const S=document.getElementById('scStudy'), R=[...document.querySelectorAll('#stGram button')].map(b=>b.getBoundingClientRect()); return [S.scrollHeight-S.clientHeight, Math.round(Math.max(...R.map(r=>r.bottom))), innerHeight, Math.round(Math.max(...R.map(r=>r.right))), innerWidth]; }")
            ok(fit[1] <= fit[2] and fit[3] <= fit[4], f"{nm}: 직접 쓰기 — 자판·확인이 스크롤 없이 보임 {fit}"); await pg.screenshot(path=f"{OUT}write_{nm}.png")
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
