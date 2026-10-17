"""(v317) 도감 '변하는 모양' 이름표 전체 점검 — 모든 단어의 모양 줄을 실제로 그려서
   동사 모양(-s·-ed·-ed·-ing)에 '여러 개'가 붙거나, 이름표가 빠지거나, 명사·형용사 이름표가 틀린 것을 찾는다."""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

JS = r"""async ()=>{
  for(const b of [1,2,3]) DexData.load(b);
  for(let i=0;i<80 && !(DexData.st[1]==="ok" && DexData.st[2]==="ok" && DexData.st[3]==="ok");i++) await new Promise(r=>setTimeout(r,100));
  const bad=[], n={all:0, rows:0};
  const rowsOf=(en,D)=>{ const s=String(D[2]||""); if(!s || s==="—") return [];
    if(/ \/ /.test(s) || /^(명사|동사|형용사) /.test(s)) return s.split(" / ").map(g=>{ const m=/^(명사|동사|형용사|부사)\s+(.*)$/.exec(g.trim()); return [m?m[2]:g, m?m[1]:D[1], m?m[1]:""]; });
    if(/과거형/.test(D[1])) return [];
    return [[s, D[1], ""]]; };
  Object.keys(DexData.d).forEach(en=>{ const D=DexData.d[en]; if(!D) return; n.all++;
    rowsOf(en,D).forEach(([str,pos,tag])=>{ n.rows++;
      const div=document.createElement("div"); div.innerHTML=DexDet.formRow(en,str,pos,tag);
      const fx=[...div.querySelectorAll(".fx:not(.me)")].map(e=>[e.querySelector("b").textContent, (e.querySelector("small")||{}).textContent||""]);
      const L=fx.map(x=>x[1]), W=fx.map(x=>x[0].toLowerCase());
      const ing=W.some(w=>/ing$/.test(w)) && W.length>=3;
      const why=[];
      if(ing && L.some(l=>l==="여러 개")) why.push("동사 모양에 '여러 개'");
      if(/대명사/.test(tag||pos) && !/\(/.test(str) && L.some(l=>l==="여러 개") && W.some(w=>!/s$/.test(w))) why.push("대명사에 '여러 개'");
      if(ing && L.filter(l=>!l).length && !/^(be|have)$/.test(en)) why.push("동사 이름표 빠짐");
      if(W.length===2 && L.some(l=>l==="여러 개") && !/(^|·)명사/.test(tag||pos)) why.push("비교급·대명사에 '여러 개'?");
      if(W.length===1 && /(^|·)명사/.test(tag||pos) && W[0]!==en.toLowerCase() && !/동사|형용사/.test(tag) && L[0]!=="여러 개" && !/\(/.test(str)) why.push("명사 복수 이름표 없음");
      if(ing && L.length>=4 && !(L.includes("했어요 (과거)") && L.includes("하는 중 (-ing)"))) why.push("과거/-ing 이름표 이상");
      if(why.length) bad.push(en+" ["+(tag||pos)+"] "+str+" → "+L.join(" | ")+"  ⟵ "+why.join(", "));
    }); });
  return {n, bad}; }"""

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate(JS)
        print("단어", r['n']['all'], "모양 줄", r['n']['rows'], "문제", len(r['bad']))
        for b in r['bad'][:80]: print("  ", b)
        await br.close()
        sys.exit(1 if r['bad'] or errs else 0)

asyncio.run(main())
