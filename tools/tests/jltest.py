"""(v314) 🎧 중등 리스닝 — Stage 24개(× 나눈 판) · 단원 제목 · 교재 뜻 · 대화 · 한 판 끝까지 · 🚩 시험."""
import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP = OUT
os.makedirs(SP, exist_ok=True)
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

async def play(pg, label, maxstep=300):
    types = set(); n = 0
    for step in range(maxstep):
        info = await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q? {t:q.t, en:q.w&&q.w.en, brk:!!U._brk, locked:U.locked} : null }")
        if not info: break
        if not info['brk'] and not info['locked']:
            types.add(info['t']); n += 1
            if n in (1, 6, 14): await pg.screenshot(path=SP + f"jl_{label}_{n:02d}_{info['t']}.png")
        await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(20)
        if await pg.evaluate("()=>StudyUI.locked"): await pg.evaluate("()=>document.getElementById('stCheck').click()")
        if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
    await pg.wait_for_timeout(300); await pg.screenshot(path=SP + f"jl_{label}_done.png")
    return n, types

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""async ()=>{ loadEasy(); for(let i=0;i<60 && !(Object.keys(TALK).length && Object.keys(BEX).length);i++) await new Promise(r=>setTimeout(r,100));
          const L=Study.lessons('jl'), fin=L.filter(x=>x.fin);
          const at=(n,en)=>{ const x=fin.find(y=>y.pn===n); const w=x && x.ws.find(w=>w.en===en); return w ? w.ko : null; };
          return {n:L.length, fin:fin.length, words:fin.reduce((a,x)=>a+x.ws.length,0), t1:fin[0].title, t24:fin[23].title,
            party:at(22,'party'), stop:at(23,'stop'), cause:at(24,'cause'), sharp:at(5,'sharp'), down:at(9,'down'),
            talk:(TALK['laureate']||[]).length, talkStop:(TALK['school zone']||[]).length, bex:!!(BEX['laureate']&&BEX['laureate'].x),
            book:Object.keys(StudyUI)&&1, inMid:(Study.lessons('mid')||[]).some(x=>x.ws.some(w=>w.en==='laureate')),
            stageName:Study.stageNo('jl', fin[21].n) }; }""")
        print(r)
        ok(r['fin'] == 24, f"Stage 24개 (판 {r['n']})")
        ok(r['words'] == 360, f"단어 360 ({r['words']})")
        ok(r['t1'] == "인사 / 자기소개" and r['t24'] == "사건 묘사", "단원 제목")
        ok(r['party'] and r['party'].startswith("일행"), f"party = 일행 ({r['party']})")
        ok(r['stop'] and r['stop'].startswith("정류장"), f"stop = 정류장 ({r['stop']})")
        ok(r['sharp'] and r['sharp'].startswith("정각"), f"sharp = 정각 ({r['sharp']})")
        ok(r['talk'] >= 2 and r['talkStop'] >= 2, f"대화 laureate {r['talk']} · school zone {r['talkStop']}")
        ok(r['bex'], "예문 (bex)")
        ok(not r['inMid'], "리스닝 새 단어는 중등 단어 묶음에 안 섞임 (src jl)")
        # 비슷한 말 짝은 서로 오답 보기로 안 나옴
        nb = await pg.evaluate("""()=>{ const L=Study.lessons('jl'), out={};
          [['commend',10,['praise','compliment']],['pleased',7,['delighted','joyful']],['seasick',14,['dizzy']],['stunning',10,['spectacular']],['down',9,['depressed']]].forEach(([en,st,nb])=>{
            const x=L.find(y=>y.fin && y.pn===st), w=x.ws.find(v=>v.en===en); let hit=0;
            for(let i=0;i<120;i++){ if(Study._opts(w,'jl',x.ws).some(v=>nb.indexOf(v)>=0)) hit++; }
            out[en]=hit; }); return out; }""")
        print("비슷한 말 보기", nb)
        ok(all(v == 0 for v in nb.values()), "비슷한 말 짝이 오답 보기로 안 나옴")
        # 책장 · 길 화면
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); StudyUI.book='mid'; StudyUI.set='jl'; StudyUI.path(); document.getElementById('scStudy').scrollTop=0; }")
        await pg.wait_for_timeout(600); await pg.screenshot(path=SP + "jl_path.png")
        txt = await pg.evaluate("()=>document.getElementById('scStudy').innerText")
        ok("인사 / 자기소개" in txt, "길에 단원 제목")
        tabs = await pg.evaluate("()=>document.getElementById('scStudy').innerText")
        ok("리스닝" in tabs, "중등 탭에 리스닝")
        # 한 판 (Stage 1-1) 끝까지
        await pg.evaluate("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(300)
        n, types = await play(pg, "s1")
        print("문제", n, sorted(types))
        ok(n >= 10, f"한 판 문제 {n}개")
        ok(await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"), "판 끝 화면")
        # 🚩 마지막 시험 (Stage 1 전체)
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); }"); await pg.wait_for_timeout(300)
        fi = await pg.evaluate("()=>Study.lessons('jl').findIndex(x=>x.fin)")
        prof = await pg.evaluate("()=>{ try{ return Study.olyProf ? Study.olyProf('jl') : null }catch(e){ return null } }")
        await pg.evaluate(f"()=>{{ StudyUI.FAST=0; StudyUI.start({fi},false); }}"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=SP + "jl_flag_intro.png")
        n2, types2 = await play(pg, "flag")
        print("시험", n2, sorted(types2), prof)
        ok(15 <= n2 <= 20, f"🚩 문제 {n2}개 (단어마다 1문제)")
        ok(await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"), "🚩 끝 화면")
        # 달리기 책
        rb = await pg.evaluate("()=>{ try{ return RunBook.lessons('jl').length }catch(e){ return 'err '+e } }")
        ok(rb == 48, f"달리기 책 리스닝 판 {rb} (Stage마다 2판)")
        ok(not errs, "페이지 오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
