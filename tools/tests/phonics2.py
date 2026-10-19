"""(v345~v346) 파닉스 판 점검 — 단모음·장모음·이중자음·이중모음 판은 「처음 글자」(한 글자) 문제가 안 나오고, 소리 문제는 그 판 소리로 ·
   끝소리 y 판도 소리 문제 · 파닉스 판 뜻(saw = 톱 · round = 둥근 · tie = 넥타이)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

GRP = {'a': ['a'], 'e': ['e'], 'i': ['i'], 'o': ['o'], 'u': ['u'], 'v1': list('aeiou'), 'ae': ['a'], 'ie': ['i'], 'oue': ['o', 'u'], 'mix': list('aiou'),
       'ee': ['ee', 'ea'], 'ai': ['ai', 'ay'], 'oa': ['oa', 'ow'], 'oo': ['oo'], 'ou': ['ou', 'ow'], 'oi': ['oi', 'oy'], 'ar': ['ar', 'or'], 'er': ['er', 'ir', 'ur'],
       'igh': ['igh', 'ie'], 'y': ['y'], 'ue': ['ue', 'ew'], 'au': ['au', 'aw'], 'lb': ['bl', 'cl', 'fl', 'gl', 'pl', 'sl'], 'rb': ['br', 'cr', 'dr', 'fr', 'gr', 'pr', 'tr'],
       'sb': ['sk', 'sm', 'sn', 'sp', 'st', 'sw'], 'sh': ['sh'], 'ch': ['ch', 'tch'], 'th': ['th'], 'wp': ['wh', 'ph', 'ck', 'ng'], 'nk': ['nk']}
JS = r"""()=>{ Voice.broken=false; const R=[];
  for(const st of ['short','long','digr','vowel2']){ const L=Study.lessons(st);
    L.forEach((x,i)=>{ if(x.fin) return; for(const lv of [1,2,3]){ const s=Study.load(), K=Study.key(st,x.n); s.seen={}; x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[K]=lv; Study.save();
      StudyUI.book=Study.bookOf(st); StudyUI.set=st; StudyUI.start(i, false);
      StudyUI.qs.forEach(q=>{ if(q.t==='intro') return; R.push([st, Study.stageNo(st,x.n), x.hl, q.t, (q.w||{}).en, q.mid||null, q.ans||null]); }); } }); }
  return R; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(800)
        R = await pg.evaluate(JS)
        first = [r for r in R if r[3] in ("first", "bal")]
        ok(not first, f"파닉스 판에 한 글자 「처음 글자」 문제 없음 ({len(first)}) {first[:4]}")
        wrong = [r for r in R if r[3] == "blend" and r[2] in GRP and r[5] not in GRP[r[2]]]
        ok(not wrong, f"소리 문제 = 그 판 소리 ({len(wrong)}) {wrong[:4]}")
        y = [r for r in R if r[2] == "y" and r[3] == "blend"]
        ok(len(y) >= 10, f"끝소리 y 판 소리 문제 {len(y)}개")
        sense = await pg.evaluate("()=>{ const f=(st,en)=>{ for(const x of Study.lessons(st)){ const w=x.ws.find(w=>w.en===en); if(w) return w.ko; } return null; }; return [f('vowel2','saw'), f('vowel2','round'), f('vowel2','tie')]; }")
        ok(sense == ["톱", "둥근", "넥타이"], f"파닉스 뜻 {sense}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:2]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
