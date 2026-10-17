"""(v322) 뜻이 여럿인 단어 — Stage 뜻과 다른 뜻의 예문·대화로 문제가 나오지 않는지
   점검에서: mean(단어장 '의미하다')에 '못된' 예문/대화, found('찾았다')에 '설립하다' 예문, cycle·pop·navy.
   ① Stage 단어마다 sentOf·talkOf·useInfo 를 여러 번 불러, 뜻 번호가 Stage 뜻과 다른 v6 예문·대화가 나오면 BAD
   ② mean·found 는 그 Stage 뜻 예문/대화가 실제로 나오는지 (예문을 다 빼 버리지 않았는지)
   ③ 도감 제목 뜻: found = 찾았다 (find)"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

JS = r"""async ()=>{
  for(const b of [1,2,3]) DexData.load(b); loadEasy(); loadTalk(); loadBex();
  for(let i=0;i<100 && !(DexData.st[1]==='ok'&&DexData.st[2]==='ok'&&DexData.st[3]==='ok'&&Object.keys(TALK).length&&Object.keys(BEX).length);i++) await new Promise(r=>setTimeout(r,100));
  const bad=[], seen={}, n={w:0, sent:0, talk:0, use:0};
  const WS=["mean","found","cycle","pop","navy","board","take","second","play","rule","face","view","coach","back","work","post","party","keep"];
  for(const set of Study.SETS){ let L=[]; try{ L=Study.lessons(set); }catch(e){ continue; }
    for(const les of L) for(const w of les.ws){ if(WS.indexOf(w.en)<0) continue; const k=set+"|"+w.en+"|"+w.ko; if(seen[k]) continue; seen[k]=1; n.w++;
      const S=senseNos(w.en, w.ko); if(!S) continue;
      const D=DexData.of(w.en)||[], wrongX=(BEX[w.en]&&BEX[w.en].x||[]).concat(D[3]||[]).filter(x=>x[2] && S.indexOf(+x[2])<0).map(x=>x[0]);
      const wrongT=(TALK[w.en]||[]).filter(x=>x[4] && S.indexOf(+x[4])<0).map(x=>x[0]+" / "+x[1]);
      Study._opts(w, set, les.ws);   // 그 반 문맥(ctx)으로
      for(let i=0;i<40;i++){
        const st=Study.sentOf(w); if(st){ n.sent++; if(wrongX.some(s=>s.startsWith(st.pre) && s.endsWith(st.post) && s.length===st.pre.length+w.en.length+st.post.length)) bad.push(set+" "+w.en+"("+w.ko+") 예문: "+st.pre+"___"+st.post); }
        const tk=Study.talkOf(w); if(tk){ n.talk++; if(wrongT.indexOf(tk.lines.join(" / "))>=0) bad.push(set+" "+w.en+"("+w.ko+") 대화: "+tk.lines.join(" / ")); }
      }
      const U=Study.useInfo(w, set); n.use++; (U.ex||[]).forEach(e=>{ if(wrongX.indexOf(e.en)>=0) bad.push(set+" "+w.en+"("+w.ko+") 쓰임 카드: "+e.en); });
    } }
  /* ② 맞는 뜻은 나오는지 */
  const got=(en,set,ko,re)=>{ const w=Object.assign({}, WORD_BANK.find(x=>x.en===en), ko?{ko}:{}); Study._opts(w, set, []); for(let i=0;i<60;i++){ const st=Study.sentOf(w), tk=Study.talkOf(w);
      if(st && re.test(st.pre+en+st.post)) return true; if(tk && re.test(tk.lines.join(" "))) return true; } return false; };
  const need=[["mean","g56",null,/sign on the classroom door|What does this word/],["found","g56",null,/lost key/],["found","mv1","설립하다, 세우다",/animal shelter|club for people|found one together/],
              ["mean","jl","못된, 심술궂은",/laugh at someone|older boy/],["cycle","g56","순환, 주기",/water cycle|life cycle/]];
  need.forEach(([en,set,ko,re])=>{ if(!got(en,set,ko,re)) bad.push("맞는 뜻 예문이 안 나옴: "+en+" "+set+" "+(ko||"")); });
  /* ③ 도감 제목 */
  const tf=DexDet.title(DexDet.word("found"), DexData.of("found")), tm=DexDet.title(DexDet.word("mean"), DexData.of("mean"));
  if(!/찾았다/.test(tf)) bad.push("도감 found 제목 "+tf); if(!/의미하다/.test(tm)) bad.push("도감 mean 제목 "+tm);
  return {n, bad, tf, tm}; }"""

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(300)
        r = await pg.evaluate(JS)
        print("단어", r["n"], "· 도감 제목", r["tf"], "/", r["tm"])
        for b in r["bad"][:40]: print("BAD", b)
        if errs: print("errs", errs[:3])
        print("결과:", "통과" if not r["bad"] and not errs else f"실패 {len(r['bad'])}")
        await br.close()
        sys.exit(1 if r["bad"] or errs else 0)

asyncio.run(main())
