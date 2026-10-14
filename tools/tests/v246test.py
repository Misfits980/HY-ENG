import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT

SOLVE0=SOLVE
SOLVE="""(wrong)=>{ const U=StudyUI, q=U.qs[U.i]; if(q && q.t==='find' && !U.locked && !U._brk){ let k=q.toks.findIndex(o=>o.ok); if(wrong) k=q.toks.findIndex(o=>!o.ok); document.querySelectorAll('#stQ .stOpt')[k].click(); return 'find'; } return ("""+SOLVE0+""")(wrong); }"""
async def run_session(pg, label, wrongs=(), shots=False):
    seq=[]; seen=set()
    for step in range(400):
        info=await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q? {t:q.t, en:q.w&&q.w.en, step:q.step, fam:!!q.fam, brk:!!U._brk, locked:U.locked} : null }")
        if not info: break
        if not info['brk'] and not info['locked']:
            seq.append(info)
            if shots and info['t'] not in seen: seen.add(info['t']); await pg.wait_for_timeout(120); await pg.screenshot(path=SP+f"{label}_{info['t']}.png")
        r=await pg.evaluate(SOLVE, len(seq) in wrongs)
        await pg.wait_for_timeout(450 if r=='drag' else 15)
        if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
    return seq
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(800)
        # v243 저장(phv 1): long-41 ★2 (ee 다 봄), long-31 ★1
        await pg.evaluate("""()=>{ const seen={}; "bee|tree|see|knee|three|bone|cone|stone|phone|home".split("|").forEach(w=>seen[w]=1);
          localStorage.setItem("hyeng_study_v1", JSON.stringify({lv:{"long-41":2,"long-31":1,"short-11":3}, seen, set:"long", book:"k", phv:1})); }""")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); Voice.canListen=()=>true; }"); await pg.wait_for_timeout(1200)
        print('mig', await pg.evaluate("()=>{ const s=Study.load(); return Object.keys(s.lv).filter(k=>s.lv[k]).map(k=>k+':'+s.lv[k]).join(' ')+' phv='+s.phv }"))
        print('easy loaded', await pg.evaluate("()=>Object.keys(EASY).length"))
        for st in ['abc','short','long','digr','vowel2','sight']:
            r=await pg.evaluate(f"()=>{{ const L=Study.lessons('{st}'); const miss=[]; Object.keys(COURSE['{st}']).forEach(n=>COURSE['{st}'][n].split('|').forEach(en=>{{ if(!Study.word(en)) miss.push(en); if(!DexData.of(en)) miss.push('dex:'+en); if(!EASY[en]) miss.push('easy:'+en); }})); return L.map(x=>Study.stageNo('{st}',x.n)+(x.fin?'F':'')+'('+x.ws.length+')').join(' ')+' | miss '+[...new Set(miss)].join(',') }}")
            print(st, r)
        # blend check
        print('blend', await pg.evaluate("""()=>[["cat","c1"],["kid","c1"],["box","c1x"],["flag","lb"],["truck","rb"],["star","sb"],["duck","wp"],["snow","oa"],["cow","ou"],["moon","oo"],["coin","oi"],["corn","ar"],["bird","er"],["cake","ae"]].map(([w,c])=>{ const q=Study.stepQ(Study.word(w),1,[Study.word(w)],c,[],true); return w+':'+q.t+(q.opts?'['+q.opts.join('/')+']':''); })"""))
        print('mark', await pg.evaluate("()=>[['queen','c1'],['box','c1x'],['yes','c1x'],['flower','lb'],['yellow','oa'],['tiger','er']].map(([w,c])=>phonicsMark(w,c)).join(' ')"))
        # 길 화면
        for st in ['abc','digr','vowel2','sight']:
            await pg.evaluate(f"()=>{{ StudyUI.book='k'; StudyUI.set='{st}'; StudyUI.path(); document.getElementById('scStudy').scrollTop=0; }}"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=SP+f"path_{st}.png")
        # 단자음 1-1
        await pg.evaluate("()=>{ StudyUI.set='abc'; StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        seq=await run_session(pg,'abc',shots=True); q=[x for x in seq if x['t']!='intro']
        print('abc 1-1', len(q), sorted(set(x['t'] for x in q)))
        # 사이트 워드 1-1
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.set='sight'; StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"sight_card.png")
        seq=await run_session(pg,'sight',shots=True,wrongs=(5,)); q=[x for x in seq if x['t']!='intro']
        print('sight 1-1', len(q), sorted(set(x['t'] for x in q)), [x['t'] for x in q][:20])
        print('done', await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.replace(/\\n+/g,' | ').slice(0,200)"))
        # 이중모음 1-1 (옮긴 별)
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.set='vowel2'; StudyUI.start(2,false); }"); await pg.wait_for_timeout(300)
        seq=await run_session(pg,'v2',shots=True); q=[x for x in seq if x['t']!='intro']
        print('vowel2 1-3', len(q), sorted(set(x['t'] for x in q)))
        # 달리기 풀에 sw 없음
        print('run pool sw', await pg.evaluate("()=>WORD_BANK.filter(w=>w.sw).length+' sw · dex has the? '+DEX_BASE.some(w=>w.en==='the')+' · setCount basic '+setCount('basic')"))
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.set='sight'; StudyUI.path(); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"subs.png")
        print('errs', errs[:5]); await br.close()
asyncio.run(main())
