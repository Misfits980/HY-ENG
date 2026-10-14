import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
import os; os.makedirs(SP, exist_ok=True)
async def run_session(pg, label, wrongs=(), shots=True):
    seq=[]; shot=set()
    for step in range(400):
        info=await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q? {t:q.t, en:q.w&&q.w.en, step:q.step, fam:!!q.fam, wu:!!q.wu, hd:q.hd||null, again:!!q.again, again2:!!q.again2, brk:!!U._brk, locked:U.locked} : null }")
        if not info: break
        if not info['brk'] and not info['locked']:
            seq.append(info)
            key=(info['t'], info['hd'], info['again2'])
            if shots and key not in shot and len(shot)<12: shot.add(key); await pg.screenshot(path=SP+f"{label}_{len(shot):02d}_{info['t']}{'_'+info['hd'] if info['hd'] else ''}{'_again' if info['again2'] else ''}.png")
        r=await pg.evaluate(SOLVE, len(seq) in wrongs)
        await pg.wait_for_timeout(450 if r=='drag' else 15)
        if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
    await pg.wait_for_timeout(300); await pg.screenshot(path=SP+f"{label}_done.png")
    return seq
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); }"); await pg.wait_for_timeout(1500)
        L=await pg.evaluate("()=>{ StudyUI.book='g12'; StudyUI.set='basic'; StudyUI.path(); const L=Study.lessons('basic'); return L.slice(0,3).map(x=>x.ws.length) }")
        print('stage sizes', L)
        await pg.evaluate("()=>StudyUI.pop(0)"); await pg.wait_for_timeout(200); await pg.screenshot(path=SP+"pop1.png")
        print('pop', await pg.evaluate("()=>document.getElementById('stPop').innerText"))
        await pg.evaluate("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(200)
        seq=await run_session(pg, "s1", wrongs=(6,7,12,30))
        q=[x for x in seq if x['t']!='intro']
        print('S1 questions', len(q), 'intro', len([x for x in seq if x['t']=='intro']), 'again', len([x for x in q if x['again']]))
        steps={}
        for k,x in enumerate(seq):
            if x['t']!='intro' and x['step'] is not None and not x['again']: steps.setdefault(x['en'],[]).append((k,x['step'],x['t']))
        print('new words', len(steps), 'steps-per-word', sorted(set(len(v) for v in steps.values())))
        ex=list(steps.items())[:3]; print('example', ex)
        print('fam', len([x for x in q if x['fam']]), 'types', sorted(set(x['t'] for x in q)))
        print('done', await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.slice(0,260)"))
        print('lv', await pg.evaluate("()=>Study.lv('basic',Study.lessons('basic')[0].n)"), 'left', await pg.evaluate("()=>Study.unseenLeft('basic',Study.lessons('basic')[0].n)"))
        # 두 번째 판: 복습할 때가 됐다고 치고
        await pg.evaluate("()=>{ const s=Study.load(); Object.keys(s.srs||{}).forEach(en=>s.srs[en][1]=0); Study.save(); document.getElementById('stBack').click(); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>StudyUI.pop(0)"); print('pop2', await pg.evaluate("()=>document.getElementById('stPop').innerText"))
        await pg.evaluate("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(200)
        seq2=await run_session(pg, "s2", wrongs=())
        q2=[x for x in seq2 if x['t']!='intro']
        print('S2 questions', len(q2), 'wu', len([x for x in q2 if x['wu']]), 'fam', len([x for x in q2 if x['fam']]), 'new', len(set(x['en'] for x in q2 if x['step'] is not None)), 'first', [ (x['t'],x['hd']) for x in seq2[:2]])
        print('done2', await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.slice(0,200)"))
        print('lv2', await pg.evaluate("()=>Study.lv('basic',Study.lessons('basic')[0].n)"))
        # 이어 하기: 중간에 저장 · 다시 불러오기
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(1,false); }")
        for i in range(9): await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(15)
        r=await pg.evaluate("()=>{ const a=StudyUI.i, n=StudyUI.qs.length; StudyUI.qs=[]; const ok=StudyUI.resume(); return {a, n, ok, b:StudyUI.i, n2:StudyUI.qs.length, st:StudyUI.qs.filter(q=>q.step!=null).length} }")
        print('resume', r)
        wu=await pg.evaluate("()=>StudyUI.qs.slice(0,9).map(q=>q.t+(q.hd?':'+q.hd:'')+(q.wu?'*':''))"); print('stage2 head', wu)
        # 같은 단어 두 번 틀리기 → 다시 보기 카드 + 쉬운 문제
        await pg.evaluate("()=>{ StudyUI.start(2,false); }")
        out=[]
        for i in range(14):
            info=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q? q.t+'|'+(q.w&&q.w.en)+'|'+q.step+(q.again?'|again':'')+(q.again2?'|card':'') : null }")
            tgt=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q && q.w && q.w.en }")
            first = await pg.evaluate("()=>StudyUI.qs.find(q=>q.t!=='intro' && !q.wu).w.en")
            wrong = (tgt==first)
            r=await pg.evaluate(SOLVE, wrong); out.append(info+(' X' if wrong and 'intro' not in info else ''))
            if not await pg.evaluate("()=>StudyUI.locked"): pass
            else: await pg.evaluate("()=>document.getElementById('stCheck').click()")
            await pg.wait_for_timeout(20)
        print('adapt', out)
        await pg.screenshot(path=SP+'adapt.png')
        seenBad=await pg.evaluate("()=>{ const L=Study.lessons('basic')[2]; const S=Study.load().seen; return L.ws.filter(w=>S[w.en]).length }"); print('stage3 seen after 14 steps', seenBad)
        print('errs', errs[:5]); await br.close()
asyncio.run(main())
