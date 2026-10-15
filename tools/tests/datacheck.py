"""(v280) 단어 자료 검사 — 단어가 많아져도 빠진 곳이 없게. 게임 코드를 그대로 써서 본다.
   ❌ (테스트 실패): Stage 목록 단어가 게임 단어에 없음 · Stage 문제 만들기/그리기 오류 · 같은 Stage 에 같은 뜻 단어 둘
   ⚠️ (숫자만 보고): 도감 설명 없음 · '새 단어' 앨범으로 몰린 단어 · 예문에 그 단어 없음 · 대화 2개 미만
   --full : 교재 Stage 전부를 ★1·★2·💜 심화로 만들어 문제마다 화면에 그려 본다 (기본은 G5-6 3단계 1~15과 + 각 반 앞 3개)"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

FULL = "--full" in sys.argv
JS = r"""async (full)=>{
  const R={bad:[], warn:{}, info:{}}, W=(k,v)=>{ (R.warn[k]=R.warn[k]||[]).push(v); };
  for(const b of [1,2,3]) DexData.load(b); loadEasy(); loadTalk(); loadBex();
  for(let i=0;i<60 && !(DexData.st[1]==="ok" && DexData.st[2]==="ok" && DexData.st[3]==="ok" && Object.keys(TALK).length && Object.keys(BEX).length); i++) await new Promise(r=>setTimeout(r,100));
  const byEn={}; WORD_BANK.forEach(w=>byEn[w.en]=w);
  // ① Stage 목록 단어가 게임 단어에 있는지
  Object.keys(COURSE).forEach(c=>Object.keys(COURSE[c]).forEach(n=>String(COURSE[c][n]).split("|").forEach(en=>{ if(en && !byEn[en]) R.bad.push("COURSE."+c+"."+n+" 의 '"+en+"' 이 게임 단어에 없음"); })));
  // ② 단어마다: 도감 설명 · 앨범 · 예문에 단어
  const reW=en=>new RegExp("(^|[^A-Za-z])"+en.replace(/[.*+?^${}()|[\]\\]/g,"\\$&").replace(/e$/,"e?").replace(/y$/,"(y|i)")+"","i");
  let nd=0; WORD_BANK.forEach(w=>{ if(w.level<1 || w.sw) return; nd++; const D=DexData.of(w.en);
    if(!D) { W("도감 설명 없음", w.en); return; }
    const wh=Dex.where(w.en); if(!wh || wh.a.id==="new") W("'새 단어' 앨범", w.en);
    const ex=(D[3]||[]).filter(x=>x && x[0]); if(!ex.length) W("예문 없음", w.en); else if(!ex.some(x=>reW(w.en).test(x[0]))) W("예문에 단어 없음", w.en); });
  R.info["검사한 단어"]=nd;
  // ③ 교재 반: 대화 · 같은 Stage 같은 뜻
  const sets=Study.SETS.filter(s=>!["kinder","abc","short","long","digr","vowel2","sight","phrase"].includes(s));
  sets.forEach(set=>{ Study.lessons(set).forEach(x=>{ if(x.fin) return;
    const ko={}; x.ws.forEach(w=>{ const k=String(w.ko).split(/[,(]/)[0].trim(); if(ko[k] && ko[k]!==w.en) R.bad.push(set+" Stage "+Study.stageNo(set,x.n)+": '"+ko[k]+"' 과 '"+w.en+"' 뜻이 같음 ("+k+")"); ko[k]=w.en; });
    if(["basic","elem","g56"].includes(set)) x.ws.forEach(w=>{ if((TALK[w.en]||[]).length<2) W("대화 2개 미만 ("+set+")", w.en); }); }); });
  // ④ Stage 문제 만들기 · 그리기 (★1 · ★2 · 💜 심화)
  const S=Study.load(), keep=JSON.stringify(S); let built=0, shown=0;
  const pick=set=>{ const L=Study.lessons(set).filter(x=>!x.fin); if(full) return L; if(set==="g56") return L.filter(x=>x.n<11600).concat(L.filter(x=>x.n>=11600).slice(0,3)); return L.slice(0,3); };
  for(const set of sets){ for(const x of pick(set)){
    for(const lv of [0,1,2]){
      const s=Study.load(); s.lv[Study.key(set,x.n)]=lv; if(lv>=1) x.ws.forEach(w=>s.seen[w.en]=1); else x.ws.forEach(w=>delete s.seen[w.en]); s.dp=s.dp||{}; s.dp[Study.key(set,x.n)]=lv>=2?1:0; Study.save();
      let qs=null; try{ qs=Study.build(set, x.n, false); built++; }catch(e){ R.bad.push(set+" "+x.n+" ★"+(lv+1)+" 만들기 오류: "+e.message); continue; }
      if(!qs || !qs.length){ R.bad.push(set+" "+x.n+" ★"+(lv+1)+" 문제 0개"); continue; }
      const miss=x.ws.filter(w=>!qs.some(q=>q.w && q.w.en===w.en || (q.ws||[]).some(o=>o.en===w.en)));
      if(miss.length && !(lv===0 && x.ws.length>20)) W("판에 안 나온 단어 (★"+(lv+1)+")", set+" "+Study.stageNo(set,x.n)+": "+miss.map(w=>w.en).join(","));
      StudyUI.set=set; StudyUI.les=x; StudyUI.qs=qs; StudyUI.tier=Study.tierCur(); StudyUI.test=false; StudyUI.oly=false; StudyUI.rv=false; StudyUI.retryMode=false; StudyUI.begin();
      for(let i=0;i<qs.length;i++){ StudyUI.i=i; StudyUI.locked=false; StudyUI._brk=false;
        try{ StudyUI.show(); shown++; const h=document.getElementById("stQ").innerHTML; if(/undefined|NaN|\[object Object\]/.test(h)) R.bad.push(set+" "+Study.stageNo(set,x.n)+" "+qs[i].t+" 화면에 undefined: "+(qs[i].w||{}).en); }
        catch(e){ R.bad.push(set+" "+Study.stageNo(set,x.n)+" ★"+(lv+1)+" "+qs[i].t+" 그리기 오류: "+e.message+" ("+(qs[i].w||{}).en+")"); } }
    } } }
  localStorage.setItem("hyeng_study_v1", keep); try{ localStorage.removeItem("hyeng_study_cur_v1"); }catch(e){}
  R.info["만든 판"]=built; R.info["그린 문제"]=shown;
  return R; }"""

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ try{ Voice.speak=()=>true; Voice.say=()=>{}; }catch(e){} StudyUI.open(); }")
        R = await pg.evaluate(JS, FULL)
        print("정보", json.dumps(R["info"], ensure_ascii=False))
        for k, v in R["warn"].items(): print(f"⚠️ {k} {len(v)}: {', '.join(v[:12])}{' …' if len(v) > 12 else ''}")
        for b in R["bad"][:40]: print("❌", b)
        e = real_errs(errs)
        if e: print("❌ 페이지 오류:", e[:5])
        if R["bad"] or e: print("BAD", len(R["bad"]))
        await br.close()
asyncio.run(main())
