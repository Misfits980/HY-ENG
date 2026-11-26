"""(v736) 📝 Daily 30 빈칸 보기에 「같이 맞는 말」 — 사용자: 「어제 아이가 데일리 30 에서 문제를 맞췄는데 틀렸다고 나온대」
   시트: G5-6 Stage 6-1 틀린 단어 fair · circus / 7-2 fashionable → 그 Stage 빈칸 문제 보기에 같이 맞는 말이 있었음
   ① science ___ (fair) 에 contest ② clowns at the ___ (circus) 에 fair ③ very ___ · a ___ hat (fashionable) 에 comfortable ④ ___ chairs (more) 에 enough — 이제 안 나옴
   ② 빈칸 문제는 늘 보기 4개 · 오류 없음 (G5-6 · 중등)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

BUILD = """async ([tag, stages, rep, opt])=>{ opt=opt||{}; const set=Object.keys(WORD_SETS).find(k=>{ try{ return Study.tag(k)===tag; }catch(e){ return false; } });
  try{ await Study.hsqLoad(); }catch(e){} try{ loadBex(); }catch(e){} try{ if(!opt.noTalk) loadTalk(); }catch(e){} for(let k=0;k<60 && (Object.keys(BEX).length<500 || (!opt.noTalk && Object.keys(TALK).length<500));k++) await new Promise(r=>setTimeout(r,100));
  const L=Study.lessons(set), out=[], err=[];
  for(let i=0;i<L.length;i++){ const les=L[i], sn=Study.stageNo(set, les.n); if(stages.length && stages.indexOf(sn)<0) continue;
    for(let r=0;r<rep;r++) for(const md of ["new","oly"]){ let qs=[]; try{ qs = md==="oly" ? Study.buildOly(set, les) : Study.build(set, les.n, false); }catch(e){ err.push(sn+" "+md+" "+e); continue; }
      qs.forEach(q=>{ if(q.t!=="sent" && q.t!=="sent2" && q.t!=="talk") return; out.push({sn, t:q.t, en:q.w.en, o:(q.opts||[]).map(x=>x && x.en), pre:q.t==="talk" ? q.tk.pre : q.st ? q.st.pre : ""}); }); } }
  return {set, out, err, nbex:Object.keys(BEX).length, ntalk:Object.keys(TALK).length}; }"""
PAIRS = [("fair","contest"), ("contest","fair"), ("circus","fair"), ("fashionable","comfortable"), ("more","enough"), ("enough","more"), ("few","enough"), ("enough","few")]

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={"width":820,"height":1180})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(1200)
        for mode in ({"noTalk":1}, {}):   # 대화 자료 없이(예전 기기 · 받기 전) = 문장 빈칸 / 대화 자료 있음 = 대화 빈칸 (진짜 기기는 대부분 이쪽)
          r=await pg.evaluate(BUILD, ["G5-6", ["4-2","4-4","6-1","6-4","7-2","7-4"], 12, mode])
          tl=sum(1 for q in r["out"] if q["t"]=="talk")
          ok(mode or tl>=30, f"대화 빈칸 문제도 나옴 {tl} (대화 자료 {r['ntalk']})")
          ok(r["nbex"]>500, f"예문 자료 불러옴 {r['nbex']}")
          hit={}
          for q in r["out"]:
              for a,b in PAIRS:
                  if q["en"]==a and b in q["o"]: hit[(q["sn"],a,b)]=hit.get((q["sn"],a,b),0)+1
          n=sum(1 for q in r["out"] if q["en"] in ("fair","circus","fashionable","more","enough","few"))
          ok(n>=40 and not hit, f"① 같이 맞는 보기 없음 (그 단어 빈칸 {n}개) {hit}")
          ok(not r["err"], f"만들기 오류 없음 {r['err'][:3]}")
        for tag in ("G5-6","중등 voca 1"):
            r=await pg.evaluate(BUILD, [tag, [], 1])
            four=[q for q in r["out"] if len(set(x for x in q["o"] if x))!=4 or q["en"] not in q["o"]]
            ok(len(r["out"])>=20 and not four and not r["err"], f"② {tag} 빈칸 {len(r['out'])}개 · 보기 4개 아님 {len(four)} {four[:2]} · 오류 {r['err'][:2]}")
        await br.close()
    print("오류", real_errs(errs)[:4])
    if real_errs(errs): bad.append("errors")
    print("BAD: %d" % len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
