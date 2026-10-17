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
  /* (v322) 같은 뜻 비교를 뜻 조각 전체로 (예전엔 첫 조각만: teeth '이, 이빨' · tooth '이빨' 을 못 봄) · 🚩 판도.
     첫 뜻이 같으면 ❌, 다른 조각이 겹치면 ⚠️ (게임은 decoys 가 겹치는 조각을 보기에서 빼므로 문제는 안 되지만 볼 것) */
  const seenP={};
  sets.forEach(set=>{ Study.lessons(set).forEach(x=>{
    const ko={}, kp={}; x.ws.forEach(w=>{ const k=String(w.ko).replace(/\([^)]*\)/g,"").split(/[,(]/)[0].trim(); if(k && ko[k] && ko[k]!==w.en){ const m=set+" Stage "+Study.stageNo(set,x.n)+": '"+ko[k]+"' 과 '"+w.en+"' 뜻이 같음 ("+k+")"; if(x.fin) W("🚩 판에 첫 뜻이 같은 단어 (보기에서는 서로 빠짐)", m); else R.bad.push(m); } ko[k]=w.en;
      koParts(w.ko).forEach(p=>{ const o=kp[p]; if(o && o!==w.en){ const t=[o, w.en].sort().join(" · ")+" ("+p+")"; if(!seenP[t]){ seenP[t]=1; W("같은 Stage 에 뜻 조각이 겹침", set+" "+t); } } kp[p]=w.en; }); });
    if(x.fin) return;
    if(["basic","elem","g56"].includes(set)) x.ws.forEach(w=>{ if((TALK[w.en]||[]).length<2) W("대화 2개 미만 ("+set+")", w.en); }); }); });
  // ④ Stage 문제 만들기 · 그리기 (★1 · ★2 · 💜 심화)
  const S=Study.load(), keep=JSON.stringify(S); let built=0, shown=0;
  const pick=set=>{ const L=Study.lessons(set).filter(x=>!x.fin); if(full) return L; if(set==="g56") return L.filter(x=>x.n<11600).concat(L.filter(x=>x.n>=11600).slice(0,3)); return L.slice(0,3); };
  /* (v322) 보기에 뜻 조각이 정답과 겹치는 단어 (정답 둘) — 뜻·대화·문장 보기 (q.opts 가 단어일 때) */
  const dupOpt=(q, where)=>{ if(!q || !q.w || !Array.isArray(q.opts) || !/^(k2e|e2k|sent|talk|listen|pic|opic)$/.test(q.t)) return; const P=koParts(q.w.ko);
    q.opts.forEach(o=>{ if(o && typeof o==="object" && o.en!==q.w.en && koParts(o.ko).some(p=>P.indexOf(p)>=0)) R.bad.push(where+" "+q.t+" 보기 정답 둘: "+q.w.en+"("+q.w.ko+") · "+o.en+"("+o.ko+")"); }); };
  /* (v322) 🚩 마지막 시험 판도 만들고 그려 본다 (기본은 반마다 앞 2개, --full 은 전부) */
  let olyN=0;
  for(const set of sets){ const F=Study.lessons(set).filter(x=>x.fin && Study.olyOn(set,x)); for(const x of (full ? F : F.slice(0,2))){
    let qs=null; try{ qs=Study.buildOly(set, x); built++; olyN++; }catch(e){ R.bad.push(set+" 🚩 "+x.n+" 만들기 오류: "+e.message); continue; }
    if(!qs || !qs.length){ R.bad.push(set+" 🚩 "+x.n+" 문제 0개"); continue; }
    StudyUI.set=set; StudyUI.les=x; StudyUI.qs=qs; StudyUI.tier=0; StudyUI.test=false; StudyUI.oly=true; StudyUI.rv=false; StudyUI.retryMode=false; StudyUI.begin();
    qs.forEach(q=>dupOpt(q, set+" 🚩 "+Study.stageNo(set,x.n)));
    for(let i=0;i<qs.length;i++){ StudyUI.i=i; StudyUI.locked=false; StudyUI._brk=false;
      try{ StudyUI.show(); shown++; const h=document.getElementById("stQ").innerHTML; if(/undefined|NaN|\[object Object\]/.test(h)) R.bad.push(set+" 🚩 "+x.n+" "+qs[i].t+" 화면에 undefined: "+(qs[i].w||{}).en); }
      catch(e){ R.bad.push(set+" 🚩 "+x.n+" "+qs[i].t+" 그리기 오류: "+e.message+" ("+(qs[i].w||{}).en+")"); } }
    try{ StudyUI.tStop(); }catch(e){} } }
  R.info["🚩 판"]=olyN;
  for(const set of sets){ for(const x of pick(set)){
    for(const lv of [0,1,2]){
      const s=Study.load(); s.lv[Study.key(set,x.n)]=lv; if(lv>=1) x.ws.forEach(w=>s.seen[w.en]=1); else x.ws.forEach(w=>delete s.seen[w.en]); s.dp=s.dp||{}; s.dp[Study.key(set,x.n)]=lv>=2?1:0; Study.save();
      let qs=null; try{ qs=Study.build(set, x.n, false); built++; }catch(e){ R.bad.push(set+" "+x.n+" ★"+(lv+1)+" 만들기 오류: "+e.message); continue; }
      if(!qs || !qs.length){ R.bad.push(set+" "+x.n+" ★"+(lv+1)+" 문제 0개"); continue; }
      qs.forEach(q=>dupOpt(q, set+" "+Study.stageNo(set,x.n)+" ★"+(lv+1)));
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
