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
    if(/ \/ /.test(s) || /^(명사|동사|형용사|부사|조동사) /.test(s)) return s.split(" / ").map(g=>{ const m=/^(명사|동사|형용사|부사|조동사|대명사)\s+(.*)$/.exec(g.trim()); return [m?m[2]:g, m?m[1]:D[1], m?m[1]:""]; });
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
      if(W.length===1 && /(^|·)명사/.test(tag||pos) && W[0]!==en.toLowerCase() && !/동사|형용사/.test(tag) && L[0]!=="여러 개" && L[0]!=="한 개" && !/\(/.test(str)) why.push("명사 복수 이름표 없음");   // (v322) teeth → tooth = 한 개
      if(ing && L.length>=4 && !(L.includes("했어요 (과거)") && L.includes("하는 중 (-ing)"))) why.push("과거/-ing 이름표 이상");
      if(W.some(w=>/^[—–-]$/.test(w))) why.push("'—' 를 모양으로 그림");   // (v322)
      if(W.some(w=>/^(명사|동사|형용사|부사|조동사|대명사) /.test(w))) why.push("품사 이름을 모양으로 그림");   // (v322) '조동사 could'
      if(/\(([^)]*[가-힣][^)]*)\)/.test(str) && !/\(단수\)/.test(str) && fx.some((x,k)=>{ const m=/([A-Za-z][A-Za-z' -]*?)\s*\(([^)]*[가-힣][^)]*)\)/.exec(str); return m && x[0]===m[1].trim() && x[1]!==m[2]; })) why.push("한글 괄호 메모가 안 보임");   // (v322) eleventh (열한 번째)
      if(why.length) bad.push(en+" ["+(tag||pos)+"] "+str+" → "+L.join(" | ")+"  ⟵ "+why.join(", "));
    }); });
  /* (v322) 점검에서 나온 것 — 이름표가 꼭 이래야 함 (표제어 이름표 · 바뀐 모양 이름표) */
  const ROW=(en,k)=>{ const D=DexData.d[en]; if(!D) return null; const R=rowsOf(en,D)[k||0]; if(!R) return null; const div=document.createElement("div"); div.innerHTML=DexDet.formRow(en,R[0],R[1],R[2]);
    return [...div.querySelectorAll(".fx")].map(e=>e.querySelector("b").textContent+"="+((e.querySelector("small")||{}).textContent||"")).join(" "); };
  const EXP=[["eleven",0,"eleventh=열한 번째"],["people",0,"people=여러 개"],["people",0,"person=한 사람"],["teeth",0,"teeth=여러 개"],["teeth",0,"tooth=한 개"],["chores",0,"chore=한 개"],
    ["police",0,"police officer=경찰관 한 명"],["men",0,"man=한 명"],["can",1,"could=했어요 (과거)"],["could",0,"could=했어요 (과거)"],["could",0,"can=지금 모양"],
    ["said",0,"said=했어요 (과거)"],["said",0,"say=원래 모양"],["ran",0,"ran=했어요 (과거)"],["has",0,"has=그가 해요 (he·she)"],["has",0,"have=원래 모양"],["have",0,"has=그가 해요 (he·she)"],
    ["wind",0,"winds=여러 개"],["tear",0,"tears=여러 개"],["coach",1,"coached=했어요 (과거)"],["look",0,"looks=그가 해요 (he·she)"],["usual",0,"most usual=가장 ~한"],["water",1,"water=모양이 바뀌지 않아요"]];
  EXP.forEach(([en,k,want])=>{ const r=ROW(en,k); if(r==null || r.split(" ").join(" ").indexOf(want)<0) bad.push("기대: "+en+" ["+k+"] 에 '"+want+"' → "+r); });
  ["wind","tear"].forEach(en=>{ const r=ROW(en,0)||""; if(/wound|tore|torn/.test(r)) bad.push(en+" 명사 줄에 동사 모양: "+r); });
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
