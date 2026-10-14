import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT

async def run_session(pg, label, shots=()):
    seq=[]; seen=set()
    for step in range(400):
        info=await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q? {t:q.t, en:q.w&&q.w.en, step:q.step, fam:!!q.fam, brk:!!U._brk, locked:U.locked} : null }")
        if not info: break
        if not info['brk'] and not info['locked']:
            seq.append(info)
            if info['t'] in shots and info['t'] not in seen: seen.add(info['t']); await pg.wait_for_timeout(150); await pg.screenshot(path=SP+f"{label}_{info['t']}.png")
        r=await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(450 if r=='drag' else 15)
        if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
    return seq
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(800)
        # 예전 저장: basic-1 ★2 (1과 단어 다 봄), last basic=2
        words=await pg.evaluate("()=>COURSE.basic[1].split('|').slice(0,12)")
        await pg.evaluate("(ws)=>{ const seen={}; ws.forEach(w=>seen[w]=1); localStorage.setItem('hyeng_study_v1', JSON.stringify({lv:{'basic-1':2}, seen, set:'basic', book:'g12', last:{basic:2}, phv:2})); }", words)
        await pg.reload(); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); Voice.canListen=()=>true; }"); await pg.wait_for_timeout(2000)
        print('mig', await pg.evaluate("()=>{ const s=Study.load(); return Object.keys(s.lv).filter(k=>s.lv[k]).map(k=>k+':'+s.lv[k]).join(' ')+' last='+JSON.stringify(s.last)+' spv='+s.spv }"))
        for st in ['basic','elem','g56','rd1','mid']:
            print(st, await pg.evaluate(f"()=>{{ const L=Study.lessons('{st}'); return L.length+' stages: '+L.slice(0,9).map(x=>Study.stageNo('{st}',x.n)+(x.fin?'F':'')+'('+x.ws.length+')').join(' ') }}"))
        print('marks', await pg.evaluate("()=>['cake','green','ship','one','come','rain','bird','dog','house'].map(w=>phonicsMark(w, ['one','come'].includes(w)?'g12t':'g12')).join(' ')"))
        print('past', await pg.evaluate("()=>{ const out=[]; Study.ctx('elem'); ['went','ate','said','took','bought','swam'].forEach(en=>{ const w=Study.word(en); if(!w) return; const q=Study.stepQ(w,1,[w],null,[],false); for(let i=0;i<40 && q.t!=='past';i++){} out.push(en+':'+JSON.stringify(Study.stepQ(w,1,[w],null,[],false).t)); }); return out.join(' ') }"))
        await pg.evaluate("()=>{ StudyUI.book='g12'; StudyUI.set='basic'; StudyUI.path(); document.getElementById('scStudy').scrollTop=0; }"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=SP+"path_basic.png")
        print('pop', await pg.evaluate("()=>{ StudyUI.pop(Study.cur('basic')); return document.getElementById('stPop').innerText.replace(/\\n/g,' | ') }"))
        await pg.evaluate("()=>{ StudyUI.pop(null); StudyUI.start(Study.cur('basic'),false); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"basic_card.png")
        seq=await run_session(pg,'basic',shots=('blend','intro','spell'))
        q=[x for x in seq if x['t']!='intro']; print('basic session Q', len(q), 'new', len(set(x['en'] for x in q if x['step'] is not None)), 'fam', len([x for x in q if x['fam']]), sorted(set(x['t'] for x in q)))
        print('done', await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.replace(/\\n+/g,' | ').slice(0,220)"))
        # elem 과거형 들어간 과 찾아서
        i=await pg.evaluate("()=>{ const L=Study.lessons('g56'); return L.findIndex(x=>!x.fin && x.ws.filter(w=>/다\\s*\\([a-z]+\\)$/.test(w.ko)).length>=2) }")
        await pg.evaluate(f"()=>{{ document.getElementById('stBack').click(); StudyUI.book='g56'; StudyUI.set='g56'; StudyUI.start({i},false); }}"); await pg.wait_for_timeout(300)
        seq=await run_session(pg,'elem',shots=('past',)); q=[x for x in seq if x['t']!='intro']
        print('elem', i, 'Q', len(q), sorted(set(x['t'] for x in q)), 'past n', len([x for x in q if x['t']=='past']))
        # 이어 하기 with past
        await pg.evaluate(f"()=>{{ document.getElementById('stBack').click(); StudyUI.start({i},false); }}")
        for k in range(12): await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(15)
        print('resume', await pg.evaluate("()=>{ const a=StudyUI.i, pst=StudyUI.qs.filter(q=>q.t==='past').length; StudyUI.qs=[]; const ok=StudyUI.resume(); return {ok, a, b:StudyUI.i, pst, pst2:StudyUI.qs.filter(q=>q.t==='past' && typeof q.opts[0]==='string').length} }"))
        await pg.evaluate("()=>{ StudyUI.path(); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ StudyUI.book='g56'; StudyUI.set='rd1'; StudyUI.path(); document.getElementById('scStudy').scrollTop=0; }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"path_rd1.png")
        print('errs', errs[:5]); await br.close()
asyncio.run(main())
