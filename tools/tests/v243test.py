import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
async def run_session(pg, label, wrongs=()):
    seq=[]
    for step in range(400):
        info=await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q? {t:q.t, en:q.w&&q.w.en, step:q.step, fam:!!q.fam, wu:!!q.wu, hd:q.hd||null, brk:!!U._brk, locked:U.locked} : null }")
        if not info: break
        if not info['brk'] and not info['locked']: seq.append(info)
        r=await pg.evaluate(SOLVE, len(seq) in wrongs)
        await pg.wait_for_timeout(450 if r=='drag' else 15)
        if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
    await pg.wait_for_timeout(300); await pg.screenshot(path=SP+f"{label}_done.png")
    return seq
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        ctx=await br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route)
        # 예전 저장: 짧은 a(short-1) ★2, 단어 몇 개만 봄 / 짧은 e(short-2) ★1, 다 봄
        await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(800)
        await pg.evaluate("""()=>{ const e="red|leg|pen|bed|ten|net|wet|hen|pet|vet|yes|get|desk|neck|bell|belt|help|dress|vest|shell".split("|"); const seen={}; e.concat(["cat","hat","bat","mat"]).forEach(w=>seen[w]=1);
          localStorage.setItem("hyeng_study_v1", JSON.stringify({lv:{"short-1":2,"short-2":1}, seen, set:"short", book:"k", last:{short:2}})); }""")
        await pg.reload(); await pg.wait_for_timeout(1500)
        print('emojifix', await pg.evaluate("()=>EmojiFix.n"), await pg.evaluate("()=>[EmojiFix.ok('🐱'), EmojiFix.ok('🪆'), EmojiFix.ok('🐻‍❄️')]"))
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); }"); await pg.wait_for_timeout(1200)
        print('lv after mig', await pg.evaluate("()=>{ const s=Study.load(); return Object.keys(s.lv).filter(k=>s.lv[k]).map(k=>k+':'+s.lv[k]).join(' ')+' last='+JSON.stringify(s.last)+' phv='+s.phv }"))
        print('lessons', await pg.evaluate("()=>Study.lessons('short').map(x=>Study.stageNo('short',x.n)+'('+x.ws.length+')'+(x.fin?'F':'')).join(' ')"))
        print('long', await pg.evaluate("()=>Study.lessons('long').map(x=>Study.stageNo('long',x.n)+'('+x.ws.length+')').join(' ')"))
        print('digr', await pg.evaluate("()=>Study.lessons('digr').map(x=>Study.stageNo('digr',x.n)+'('+x.ws.length+')').join(' ')"))
        miss=await pg.evaluate("()=>{ const out=[]; ['short','long','digr'].forEach(s=>Object.keys(COURSE[s]).forEach(n=>COURSE[s][n].split('|').forEach(en=>{ if(!Study.word(en)) out.push(s+n+':'+en); }))); return out }")
        print('missing words', miss)
        nodex=await pg.evaluate("()=>{ const out=[]; ['short','long','digr'].forEach(s=>Object.keys(COURSE[s]).forEach(n=>COURSE[s][n].split('|').forEach(en=>{ if(!DexData.of(en)) out.push(en); }))); return [...new Set(out)] }")
        print('no dex', nodex)
        await pg.evaluate("()=>{ StudyUI.book='k'; StudyUI.set='short'; StudyUI.path(); document.getElementById('scStudy').scrollTop=0; }"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=SP+"path_short.png", full_page=False)
        await pg.evaluate("()=>{ const m=document.getElementById('stMap'); const w=m.querySelectorAll('.stWorld')[1]; if(w) w.scrollIntoView({block:'start'}); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"path_short2.png")
        await pg.evaluate("()=>StudyUI.pop(0)"); await pg.wait_for_timeout(200)
        print('pop', await pg.evaluate("()=>document.getElementById('stPop').innerText"))
        await pg.screenshot(path=SP+"pop.png")
        await pg.evaluate("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(400)
        # 첫 카드 = 새 단어 카드(문장 버튼)
        await pg.evaluate("()=>{ const k=StudyUI.qs.findIndex(q=>q.t==='intro' && q.card); }")
        await pg.screenshot(path=SP+"card.png")
        print('card', await pg.evaluate("()=>document.getElementById('stLesson').innerText.slice(0,300)"))
        seq=await run_session(pg, "s11")
        q=[x for x in seq if x['t']!='intro']
        print('1-1 Q', len(q), 'new', len(set(x['en'] for x in q if x['step'] is not None)), 'fam', len([x for x in q if x['fam']]), 'wu', len([x for x in q if x['wu']]))
        print('done', await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.replace(/\\n+/g,' | ').slice(0,300)"))
        # 1-2: 아는 단어로 채우기
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(1,false); }"); await pg.wait_for_timeout(200)
        seq=await run_session(pg, "s12"); q=[x for x in seq if x['t']!='intro']
        print('1-2 Q', len(q), 'new', len(set(x['en'] for x in q if x['step'] is not None)), 'fam', len([x for x in q if x['fam']]), 'fam words', sorted(set(x['en'] for x in q if x['fam'])))
        # 보물상자 3개 (강제)
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); const s=Study.load(); s.chest={d:Study.today(),n:0}; Study.save(); StudyUI._r=Math.random; Math.random=()=>0.1; StudyUI.start(2,false); }")
        await pg.evaluate("()=>{ Math.random=StudyUI._r; }")
        seq=await run_session(pg, "s13")
        # 이건 Math.random 0.1 일 때만 상자 — 다시: rollChest 직접
        html=await pg.evaluate("()=>{ const r=Math.random; Math.random=()=>0.1; const g=StudyUI.rollChest(); Math.random=r; const d=document.getElementById('stDoneIn'); const old=d.querySelector('.stChests'); if(!old){ const x=document.createElement('div'); x.innerHTML=StudyUI.chestHtml(g); d.insertBefore(x.firstChild, d.querySelector('.stGo')); } return g }")
        await pg.wait_for_timeout(200); await pg.screenshot(path=SP+"chest3.png")
        await pg.click(".stCh:nth-child(2)", force=True); await pg.wait_for_timeout(1100); await pg.screenshot(path=SP+"chest_open.png")
        print('chest txt', await pg.evaluate("()=>document.querySelector('.stChests').innerText"))
        # 그림 문제: doll (🪆)
        r=await pg.evaluate("()=>{ const w=Study.word('doll'); return w.emoji }"); print('doll emoji ->', r[:60])
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.book='k'; StudyUI.set='kinder'; StudyUI.path(); const L=Study.lessons('kinder'); const i=L.findIndex(x=>x.ws.some(w=>w.en==='doll')); StudyUI.start(Math.max(0,i),false); const w=Study.word('doll'); const q=Study.stepQ? null:null; StudyUI.qs.splice(StudyUI.i,0,{t:'pic',w,opts:[w,Study.word('cat'),Study.word('ball'),Study.word('sock')]}); StudyUI.show(); }")
        await pg.wait_for_timeout(500); await pg.screenshot(path=SP+"pic_doll.png")
        # 월드 클리어: 1-5 🚩 (모든 단어 본 걸로)
        await pg.evaluate("()=>{ const s=Study.load(); Study.lessons('short').filter(x=>x.wd===1).forEach(x=>x.ws.forEach(w=>s.seen[w.en]=1)); Study.save(); StudyUI.set='short'; StudyUI.book='k'; StudyUI.path(); StudyUI.start(4,false); }")
        seq=await run_session(pg, "s15")
        print('world', await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.replace(/\\n+/g,' | ').slice(0,200)"))
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); document.getElementById('scStudy').scrollTop=0; }"); await pg.wait_for_timeout(300); await pg.screenshot(path=SP+"path_after.png")
        print('errs', errs[:5]); await br.close()
asyncio.run(main())
