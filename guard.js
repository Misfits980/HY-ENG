/* (v623) 🛡 GUARD — 오류 기록 · 멈춤 막기 · 렉 줄이기 (게임 index.html · 마을 proto/house.html 같이 씀)
   사용자(11-07): 「우리 게임 안정성이랑 렉 대비해서 장치를 해야겠지? 그리고 오류를 대비하고 싶어」
   · 오류 기록: 처음 보는 오류만(한 판에 8개까지) → 서버 /hy/day/er<날짜>/<자동 키> (규칙 /hy/day/$d/$k 쓰기 가능 — 규칙 안 바꿈)
     → 선생님은 err.html 에서 날짜별로 봄 (같은 오류 묶음 · 기기 · 버전 · 몇 번)
   · 튕김 알아채기: 화면이 보이는 동안 꺼지면(아이패드 메모리 부족 등) 다음에 켤 때 「튕김」으로 적고 그 기기는 한 단계 가볍게
   · 멈춤 막기(마을): 한 프레임에서 오류가 나도 다음 프레임은 계속 · 2초에 30번 넘게 나면 「다시 시작」 카드
   · 렉(마을): 그리는 프레임이 3초 동안 평균 25fps 아래면 한 단계 가볍게(PERF 0→3) — 이 기기에 기억 · ?perf=0 이면 되돌림
   · 그래픽 끊김(webglcontextlost): 「다시 시작」 카드
   자동 시험(navigator.webdriver)에서는 서버로 안 보냄(GUARD.sent 에만 쌓음) · 렉 자동 낮춤도 끔(?perf=auto 면 켬) */
/* (v700) 🧪 점검 모드 — 주소에 ?qa=1 (이 탭만, sessionStorage hyeng_qa · 마을로 넘어가도 이어짐)
   사용자(11-17): QA 때 크롬 iframe 으로 막다가 마을로 넘어가는 순간 막는 장치가 빠져 테스트 기록이 서버에 올라간 사고 →
   게임이 스스로: Firebase 쓰기(PUT·POST·PATCH·DELETE) · 구글 시트(Apps Script) POST·조치(act=1) · sendBeacon = 보내지 않고 가짜 성공.
   읽기(랭킹·주간 보스·친구 위치)는 진짜. 이 기기 저장(localStorage hyeng*)은 들어올 때 sessionStorage 에 두었다가 「끝내기」(= ?qa=0)로 되돌림.
   되돌리기는 다음 페이지가 시작할 때(이 파일 맨 앞) 함 — 페이지를 닫을 때(pagehide) 게임이 다시 쓰는 것까지 지우려고. */
(function(){
  let on=false, ss=null, ls=null; try{ ss=window.sessionStorage; }catch(e){} try{ ls=window.localStorage; }catch(e){}
  const BK="hyeng_qa_bak", alive=k=>/^hyeng_alive_/.test(k);
  const restore=S=>{ try{ if(!S || !ls) return false; const K=[]; for(let i=0;i<ls.length;i++){ const k=ls.key(i); if(/^hyeng/.test(k) && k!==BK) K.push(k); }
      K.forEach(k=>{ if(!(k in S) || alive(k)) ls.removeItem(k); }); Object.keys(S).forEach(k=>{ if(!alive(k) && k!==BK) ls.setItem(k, S[k]); }); return true; }catch(e){ return false; } };
  const parse=t=>{ try{ return JSON.parse(t||"null"); }catch(e){ return null; } };
  try{ const q=location.search, inQa=!!ss && ss.getItem("hyeng_qa")==="1";
    if(/[?&]qa=0(&|$)/.test(q)){ const S=parse(ss && ss.getItem("hyeng_qa_snap")) || parse(ls && ls.getItem(BK)); if(S) window.HY_QA_RESTORED=restore(S); if(ss){ ss.removeItem("hyeng_qa"); ss.removeItem("hyeng_qa_snap"); } if(ls) ls.removeItem(BK);
      /* (v702) 크롬 점검: 「끝내기」 뒤 ?qa=0 이 게임을 보통 모드로 바로 켜서(서버에 쓰기 시작) 점검이 끝나자마자 기록이 나갔음 → 여기서 멈추고 「끝냈어요 · 게임 열기」만 보여 줌 */
      try{ window.stop(); }catch(e){} window.HY_QA_END=true;
      const home=location.pathname.replace(/[^/]*$/, "")+"index.html";
      try{ document.documentElement.innerHTML='<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>점검 끝</title></head><body style="margin:0;min-height:100vh;display:grid;place-items:center;background:#1d1830;color:#fff;font:16px/1.55 sans-serif;text-align:center"><div style="padding:24px"><div style="font-size:42px">🧪</div><b style="font-size:20px">점검 모드를 끝냈어요</b><p style="opacity:.85;margin:8px 0 16px">이 기기 저장을 점검 전으로 되돌렸어요'+(S ? '' : ' (되돌릴 것이 없었어요)')+'</p><a id="hyQaHome" href="'+home+'" style="display:inline-block;padding:12px 22px;border-radius:12px;background:#ffd25e;color:#2a2340;font-weight:800;text-decoration:none">게임 열기</a></div></body>'; }catch(e){} }
    else { if(!inQa && ls && ls.getItem(BK)){ window.HY_QA_RESTORED=restore(parse(ls.getItem(BK))); ls.removeItem(BK); }   /* 점검하던 탭을 「끝내기」 없이 닫았으면 → 다음에 열 때(이 기기 어느 탭이든) 점검 전으로 되돌림 */
      if(/[?&]qa=1(&|$)/.test(q) && ss) ss.setItem("hyeng_qa","1"); }
    on=!!ss && ss.getItem("hyeng_qa")==="1"; }catch(e){}
  window.HY_QA=on; if(!on) return;
  try{ if(!ss.getItem("hyeng_qa_snap")){ const S={}; for(let i=0;i<localStorage.length;i++){ const k=localStorage.key(i); if(/^hyeng/.test(k) && !alive(k) && k!==BK) S[k]=localStorage.getItem(k); } const j=JSON.stringify(S); ss.setItem("hyeng_qa_snap", j); try{ localStorage.setItem(BK, j); }catch(e){} } }catch(e){}
  const FBH=/firebasedatabase\.app|firebaseio\.com/, GAS=/script\.google(usercontent)?\.com/, LOG=window.HY_QA_LOG=[];
  const fake=o=>Promise.resolve(new Response(JSON.stringify(o===undefined?null:o), {status:200, headers:{"Content-Type":"application/json"}}));
  const of=window.fetch ? window.fetch.bind(window) : null;
  if(of) window.fetch=function(u, o){ const url=String((u && u.url) || u), m=String((o && o.method) || (u && u.method) || "GET").toUpperCase();
    if(FBH.test(url) && m!=="GET"){ LOG.push([m, url.split("?")[0].replace(/^https:\/\/[^/]+/, "")]); let b=null; try{ b=o && o.body ? JSON.parse(o.body) : null; }catch(e){}
      if(b && typeof b==="object" && b[".sv"]) b=Date.now(); return fake(m==="POST" ? {name:"-qa"+Date.now().toString(36)} : b); }
    if(GAS.test(url) && (m!=="GET" || /[?&]act=1/.test(url))){ LOG.push([m, "sheet"]); return fake(/[?&]act=1/.test(url) ? {ok:true, list:[]} : {ok:true, qa:1}); }
    return of(u, o); };
  try{ const sb=navigator.sendBeacon && navigator.sendBeacon.bind(navigator); if(sb) navigator.sendBeacon=function(u, d){ if(FBH.test(String(u)) || GAS.test(String(u))){ LOG.push(["BEACON", ""]); return true; } return sb(u, d); }; }catch(e){}
  const badge=()=>{ if(document.getElementById("hyQa")) return; const b=document.createElement("div"); b.id="hyQa";
    b.style.cssText="position:fixed;left:6px;bottom:6px;z-index:2147483000;background:#7a1fa2;color:#fff;font:700 12px/1.2 sans-serif;padding:6px 8px;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,.3);display:flex;gap:6px;align-items:center;opacity:.92";
    b.innerHTML='🧪 점검 모드 · 서버에 안 씀 <button type="button" style="font:700 12px sans-serif;border:0;border-radius:7px;padding:3px 7px;background:#fff;color:#7a1fa2;cursor:pointer">끝내기</button>';
    b.querySelector("button").onclick=e=>{ e.stopPropagation(); const town=/house\.html/.test(location.pathname); location.href=(town ? "../index.html" : location.pathname)+"?qa=0"; };
    b.title="누르면 반대쪽 구석으로"; b.onclick=()=>{ const t=b.dataset.top!=="1"; b.dataset.top=t?"1":""; b.style.top=t?"6px":""; b.style.bottom=t?"":"6px"; b.style.left=t?"":"6px"; b.style.right=t?"6px":""; };   /* (v702) 시험지 아래 칸을 가려서 — 누르면 오른쪽 위로 */
    document.body.appendChild(b); };
  if(document.body) badge(); else document.addEventListener("DOMContentLoaded", badge);
})();
(function(){
  "use strict";
  if(window.GUARD) return;
  const PAGE=/house\.html/.test(location.pathname) ? "town" : "game";
  const WD=!!navigator.webdriver;
  const URLS=["https://hy-eng-raid-default-rtdb.asia-southeast1.firebasedatabase.app","https://hy-eng-raid-default-rtdb.firebaseio.com","https://hy-eng-raid-default-rtdb.europe-west1.firebasedatabase.app"];
  const ls={ get(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }, set(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }, del(k){ try{ localStorage.removeItem(k); }catch(e){} } };
  const day=()=>{ const d=new Date(Date.now()+9*3600e3); return d.toISOString().slice(0,10).replace(/-/g,""); };   /* 한국 날짜 */
  const dev=()=>{ const u=navigator.userAgent||""; let os=/iPad|Macintosh.*Mobile|Macintosh/.test(u) && navigator.maxTouchPoints>1 ? "iPad" : /iPhone/.test(u) ? "iPhone" : /Android/.test(u) ? (/Mobile/.test(u)?"Android폰":"Android패드") : /Windows/.test(u) ? "Windows" : /Mac/.test(u) ? "Mac" : "기타";
    const iv=(u.match(/OS (\d+)[._](\d+)/)||[])[1], cv=(u.match(/Chrome\/(\d+)/)||[])[1], sv=(u.match(/Version\/(\d+)/)||[])[1];
    return os+(iv?" "+iv:"")+(cv?" · 크롬 "+cv:sv?" · 사파리 "+sv:"")+" · "+(screen.width||0)+"×"+(screen.height||0)+" · 코어 "+(navigator.hardwareConcurrency||"?")+(navigator.deviceMemory?" · "+navigator.deviceMemory+"GB":""); };
  let ver=window.GAME_VER||"";
  try{ if(!ver && window.caches) caches.keys().then(K=>{ const k=K.find(x=>/^hyeng-v\d+$/.test(x)); if(k && !ver) ver=k.slice(6); }).catch(()=>{}); }catch(e){}
  const seen={}; let n=0;
  const GD={ PAGE, sent:[], lv:0, errs:0, fatal:false };
  function who(){ try{ return (ls.get("hyeng_nick")||"").slice(0,16); }catch(e){ return ""; } }
  function where(){ try{ if(PAGE==="town" && typeof place!=="undefined" && typeof PL!=="undefined"){ for(const k in PL) if(PL[k]===place) return k; } }catch(e){} try{ if(PAGE==="game" && typeof G!=="undefined" && G && G.running) return "run"; }catch(e){} return ""; }
  /* 📮 기록 보내기 — 같은 것은 한 번 · 한 판에 8개까지 */
  GD.report=function(kind, msg, extra){
    try{
      msg=String(msg||"").replace(/\s+/g," ").slice(0,220); const key=kind+"|"+msg; if(seen[key]) { seen[key]++; return; } seen[key]=1; if(n>=8) return; n++;
      const rec={k:kind, m:msg, p:PAGE, pl:where(), v:String(window.GAME_VER||ver||""), d:dev(), w:who(), t:Date.now()};
      if(extra) for(const x in extra) rec[x]=typeof extra[x]==="string" ? extra[x].slice(0,600) : extra[x];
      send(rec);
    }catch(e){}
  };
  function send(rec){
    try{
      GD.sent.push(rec); if(WD && !window.HY_GUARD_SEND) return;
      const base=ls.get("hyeng_fb_url"); let u=(base && URLS.includes(base) ? base : URLS[0])+"/hy/day/er"+day()+".json";
      try{ const a=JSON.parse(ls.get("hyeng_fb_auth")||"null"); if(a && a.t && Date.now()<(+a.e||0)) u+="?auth="+encodeURIComponent(a.t); }catch(e){}   /* 로그인 규칙(auth != null)일 때 — 게임이 받아 둔 토큰 */
      const body=JSON.stringify(rec);
      if(document.visibilityState==="hidden" && navigator.sendBeacon){ try{ navigator.sendBeacon(u, new Blob([body],{type:"text/plain"})); return; }catch(e){} }   /* sendBeacon = POST */
      fetch(u, {method:"POST", body, keepalive:true, headers:{"Content-Type":"text/plain"}}).catch(()=>{});
    }catch(e){}
  }
  const stackOf=e=>{ try{ return String(e && e.stack || "").split("\n").slice(0,4).map(s=>s.trim().replace(/https?:\/\/[^/]+\/[^ )]*?\/(?=[^/ )]+:\d)/,"")).join(" | "); }catch(_){ return ""; } };
  addEventListener("error", e=>{ if(e && e.target && e.target!==window) return; GD.errs++; GD.report("err", e && e.message, {s:(e && e.filename ? String(e.filename).split("/").pop()+":"+e.lineno+":"+e.colno : ""), st:stackOf(e && e.error)}); });
  addEventListener("unhandledrejection", e=>{ const r=e && e.reason; const m=r && (r.message||r.name) || String(r||""); if(/NotAllowedError|AbortError|play\(\)|interrupted|The operation was aborted/i.test(m)) return; GD.report("promise", m, {st:stackOf(r)}); });
  /* 💥 튕김 알아채기 — 화면이 보이는 동안 꺼졌으면 다음에 켤 때 적음 (숨겨진 뒤 꺼진 건 셈 안 함) */
  const AK="hyeng_alive_"+PAGE;
  try{ const a=ls.get(AK); if(a){ const o=JSON.parse(a); if(o && Date.now()-o.t<15*60e3){ GD.crashed=o; setTimeout(()=>GD.report("crash", "화면이 보이는 중에 꺼짐 (메모리 부족·튕김 추정)", {pl:o.pl||"", up:Math.round((o.t-o.s)/1000)}), 1500); if(PAGE==="town"){ const L=+(ls.get("hyeng_perf_lv")||0); if(L<2) ls.set("hyeng_perf_lv", String(L+1)); } } } }catch(e){}
  let s0=Date.now(); const alive=()=>ls.set(AK, JSON.stringify({t:Date.now(), s:s0, pl:where()}));
  alive(); setInterval(()=>{ if(document.visibilityState!=="hidden") alive(); }, 20000);
  addEventListener("visibilitychange", ()=>{ if(document.visibilityState==="hidden") ls.del(AK); else alive(); });
  addEventListener("pagehide", ()=>ls.del(AK));
  /* 🧯 「다시 시작」 카드 */
  GD.fatalCard=function(title, sub, why){ if(GD.fatal) return; GD.fatal=true; GD.report("fatal", why||title);
    const d=document.createElement("div"); d.id="gdFatal"; d.setAttribute("style","position:fixed;inset:0;z-index:99;display:grid;place-items:center;background:rgba(30,18,40,.55);padding:16px;font-family:system-ui,sans-serif");
    d.innerHTML='<div style="background:#fff8ea;border:3px solid #3b2433;border-radius:22px;box-shadow:0 5px 0 #3b2433;padding:20px 18px;max-width:340px;text-align:center;color:#3b2433"><div style="font-size:44px">🛠️</div><b style="font-size:19px">'+title+'</b><p style="margin:8px 0 14px;font-size:15px;color:#6b5a4e">'+(sub||"다시 시작하면 대부분 괜찮아져요. 모은 것은 그대로예요.")+'</p><button id="gdRe" style="font:800 17px system-ui;padding:12px 22px;border-radius:14px;border:3px solid #3b2433;background:#7bd389;box-shadow:0 3px 0 #3b2433">🔄 다시 시작</button></div>';
    document.body.appendChild(d); d.querySelector("#gdRe").onclick=()=>location.reload(); };
  /* 🧱 프레임 오류 — 마을 loop 가 부름 */
  let fe=[];
  GD.frameErr=function(e){ const now=performance.now(); fe.push(now); while(fe.length && now-fe[0]>2000) fe.shift(); GD.report("frame", e && e.message || String(e), {st:stackOf(e)});
    if(fe.length===1){ try{ console.warn("[GUARD] frame", e); }catch(_){} }
    if(fe.length>30) GD.fatalCard("앗, 마을이 멈췄어요", "다시 시작하면 괜찮아져요. 집·가방·보석은 그대로예요.", "frame x30: "+(e && e.message)); };
  /* 🎞 그래픽 끊김 */
  GD.watchGL=function(canvas){ try{ canvas.addEventListener("webglcontextlost", ev=>{ ev.preventDefault(); GD.report("gl", "webglcontextlost"); setTimeout(()=>{ if(!GD.glBack) GD.fatalCard("그래픽이 잠깐 끊겼어요", "다시 시작하면 돌아와요. 모은 것은 그대로예요.", "webglcontextlost"); }, 2500); }, false);
    canvas.addEventListener("webglcontextrestored", ()=>{ GD.glBack=true; }, false); }catch(e){} };
  /* 🐢 렉 줄이기 (마을) — 단계: 0 그대로 · 1 화소 1.5 + 테두리 끔 · 2 화소 1 + 그림자 끔 + 안개 가깝게 · 3 화소 0.8 */
  const q=new URLSearchParams(location.search);
  if(q.get("perf")==="0") ls.set("hyeng_perf_lv","0");
  GD.lv=Math.max(0, Math.min(3, +(ls.get("hyeng_perf_lv")||0)));
  GD.auto=(!WD || q.get("perf")==="auto") && q.get("perf")!=="off";
  let acc=0, cnt=0, since=0, lastChange=0;
  GD.onLevel=null;   /* 페이지가 단계 바꾸는 함수를 넣음 */
  GD.setLevel=function(l, why){ l=Math.max(0,Math.min(3,l)); if(l===GD.lv) return; const up=l>GD.lv; GD.lv=l; ls.set("hyeng_perf_lv", String(l)); lastChange=performance.now(); try{ GD.onLevel && GD.onLevel(l, why); }catch(e){} if(up && why) GD.report("perf", "가볍게 "+l+"단계", {fps:why}); };
  /* 그린 프레임마다 부름 (ms = 지난 프레임부터 걸린 시간) */
  GD.frame=function(ms){ if(!GD.auto || document.visibilityState==="hidden" || ms>400) { acc=0; cnt=0; since=0; return; } acc+=ms; cnt++; since+=ms;
    if(since<3000) return; const avg=acc/cnt, now=performance.now(); acc=0; cnt=0; since=0;
    if(avg>40 && GD.lv<3 && now-lastChange>6000){ GD.setLevel(GD.lv+1, Math.round(1000/avg)+"fps"); } };
  /* (v721) 🌐 연결 재기 — 사용자: 「게임이 끊기기도 하고 렉이 너무 심해 · 다른 게임들을 만들 때 아이들이 힘들 것 같아서」 (한국 서버로 옮길지 정하기 전에 숫자로)
     수업 게임·오락실·섬에 있는 동안 20초마다 ① 게임 서버(Firebase · 싱가포르)까지 한 번 주고받는 시간 ② 2초 동안 화면 속도(fps)·멈칫(0.1초 넘는 프레임)
     ③ 페이지마다 한 번: 참고 서버 서울·싱가포르(AWS ping, 내용 없음)까지 시간 — 「서울 서버면 얼마나 빨라질까」
     페이지가 HY_NETTAG()(지금 게임 이름 · 없으면 "") · HY_NETD(실시간 연결 끊김 수)를 줌 → 게임이 바뀌거나 화면을 끄거나 5분마다 한 줄(k:"net") → err.html 「🌐 연결」 */
  const NM={S:null, busy:0, n:0, ref:0, refV:null};
  const srt=a=>a.slice().sort((x,y)=>x-y), med=a=>a.length ? Math.round(srt(a)[Math.floor(a.length/2)]) : 0, pct=(a,p)=>a.length ? Math.round(srt(a)[Math.min(a.length-1, Math.floor(a.length*p))]) : 0;
  /* 걸린 시간 = 브라우저 네트워크가 잰 값(Resource Timing duration) — 패드가 바빠 화면이 멈칫해도 그만큼 늘지 않게 · 없으면 직접 잰 값 */
  async function ping(u){ let c=null; try{ c=new AbortController(); }catch(e){} const to=setTimeout(()=>{ try{ c && c.abort(); }catch(e){} }, 6000), t=performance.now(),
      url=u+(u.indexOf("?")<0?"?":"&")+"_="+Date.now().toString(36)+Math.random().toString(36).slice(2,5);
    try{ try{ if(performance.getEntriesByType("resource").length>200) performance.clearResourceTimings(); }catch(e){}
      await fetch(url, Object.assign({cache:"no-store", credentials:"omit", mode:"no-cors"}, c?{signal:c.signal}:{})); const t1=performance.now();
      let d=0; for(let k=0;k<3 && !d;k++){ try{ const E=performance.getEntriesByName(url); const x=E && E[E.length-1]; if(x && x.duration>0) d=x.duration; }catch(e){} if(!d) await new Promise(r=>setTimeout(r,30)); }
      return Math.round(d || (t1-t)); }
    catch(e){ return -1; } finally{ clearTimeout(to); } }
  const best=async u=>{ let m=-1; for(let i=0;i<3;i++){ const r=await ping(u); if(r>=0 && (m<0 || r<m)) m=r; } return m; };   /* 세 번 중 가장 빠른 것 = 거리 */
  const fpsWin=ms=>new Promise(res=>{ if(!window.requestAnimationFrame) return res(null); let n=0, t0=0, last=0, jank=0, done=0; const end=v=>{ if(!done){ done=1; res(v); } };
    const f=t=>{ if(done) return; if(!t0){ t0=last=t; } else { n++; if(t-last>100) jank++; last=t; } if(t-t0<ms) requestAnimationFrame(f); else end({fps:n*1000/Math.max(1,t-t0), jank}); };
    requestAnimationFrame(f); setTimeout(()=>end(null), ms+1500); });
  const fbBase=()=>{ const b=ls.get("hyeng_fb_url"); return b && URLS.includes(b) ? b : URLS[0]; };
  const nmTag=()=>{ try{ return String((window.HY_NETTAG && window.HY_NETTAG()) || "").slice(0,40); }catch(e){ return ""; } }, nmD=()=>{ try{ return +window.HY_NETD||0; }catch(e){ return 0; } };
  const avg=a=>a.length ? Math.round(a.reduce((x,y)=>x+y,0)/a.length) : null;
  function nmFlush(){ const S=NM.S; NM.S=null; if(!S || S.r.length+S.f<2 || NM.n>=12) return; NM.n++;
    send({k:"net", m:S.tag, p:PAGE, v:String(window.GAME_VER||ver||""), d:dev(), w:who(), t:Date.now(), t0:S.t0, sec:Math.round((Date.now()-S.t0)/1000),
      n:S.r.length, rtt:med(S.r), p90:pct(S.r,.9), mx:S.r.length?Math.max(...S.r):0, fail:S.f, fb3:S.fb3, sel:S.sel, sg:S.sg,
      fps:avg(S.fp), fpsMin:S.fp.length?Math.round(Math.min(...S.fp)):null, jank:S.j, drop:Math.max(0, nmD()-S.d0)}); }
  async function nmTick(){ if(NM.busy || (WD && !window.HY_NETMON) || window.HY_FB_LOCAL) return;
    const tag=document.visibilityState==="hidden" ? "" : nmTag();
    if(NM.S && (NM.S.tag!==tag || Date.now()-NM.S.t0>300e3)) nmFlush(); if(!tag) return;
    NM.busy=1;
    try{ if(!NM.S) NM.S={tag, t0:Date.now(), r:[], f:0, fp:[], j:0, d0:nmD(), fb3:null, sel:null, sg:null}; const S=NM.S;
      if(!NM.ref){ NM.ref=1; const fb=await best(fbBase()+"/.json?shallow=true"), se=await best("https://dynamodb.ap-northeast-2.amazonaws.com/ping"), sg=await best("https://dynamodb.ap-southeast-1.amazonaws.com/ping"); NM.refV=[fb, se, sg]; }
      if(NM.refV && S.sel==null){ S.fb3=NM.refV[0]; S.sel=NM.refV[1]; S.sg=NM.refV[2]; }
      const r=await ping(fbBase()+"/.json?shallow=true"); if(r>=0) S.r.push(r); else S.f++;
      const F=await fpsWin(2000); if(F){ S.fp.push(F.fps); S.j+=F.jank; }
    }catch(e){} finally{ NM.busy=0; } }
  GD.net={tick:nmTick, flush:nmFlush, get S(){ return NM.S; }, get ref(){ return NM.refV; }};
  try{ setInterval(nmTick, +window.HY_NETMS || 20000); setTimeout(nmTick, 4000);
    document.addEventListener("visibilitychange", ()=>{ if(document.visibilityState==="hidden") nmFlush(); });
    addEventListener("pagehide", ()=>nmFlush()); }catch(e){}
  window.GUARD=GD;
})();
