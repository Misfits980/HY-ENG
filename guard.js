/* (v623) 🛡 GUARD — 오류 기록 · 멈춤 막기 · 렉 줄이기 (게임 index.html · 마을 proto/house.html 같이 씀)
   사용자(11-07): 「우리 게임 안정성이랑 렉 대비해서 장치를 해야겠지? 그리고 오류를 대비하고 싶어」
   · 오류 기록: 처음 보는 오류만(한 판에 8개까지) → 서버 /hy/day/er<날짜>/<자동 키> (규칙 /hy/day/$d/$k 쓰기 가능 — 규칙 안 바꿈)
     → 선생님은 err.html 에서 날짜별로 봄 (같은 오류 묶음 · 기기 · 버전 · 몇 번)
   · 튕김 알아채기: 화면이 보이는 동안 꺼지면(아이패드 메모리 부족 등) 다음에 켤 때 「튕김」으로 적고 그 기기는 한 단계 가볍게
   · 멈춤 막기(마을): 한 프레임에서 오류가 나도 다음 프레임은 계속 · 2초에 30번 넘게 나면 「다시 시작」 카드
   · 렉(마을): 그리는 프레임이 3초 동안 평균 25fps 아래면 한 단계 가볍게(PERF 0→3) — 이 기기에 기억 · ?perf=0 이면 되돌림
   · 그래픽 끊김(webglcontextlost): 「다시 시작」 카드
   자동 시험(navigator.webdriver)에서는 서버로 안 보냄(GUARD.sent 에만 쌓음) · 렉 자동 낮춤도 끔(?perf=auto 면 켬) */
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
      GD.sent.push(rec); if(WD && !window.HY_GUARD_SEND) return;
      const base=ls.get("hyeng_fb_url"); let u=(base && URLS.includes(base) ? base : URLS[0])+"/hy/day/er"+day()+".json";
      try{ const a=JSON.parse(ls.get("hyeng_fb_auth")||"null"); if(a && a.t && Date.now()<(+a.e||0)) u+="?auth="+encodeURIComponent(a.t); }catch(e){}   /* 로그인 규칙(auth != null)일 때 — 게임이 받아 둔 토큰 */
      const body=JSON.stringify(rec);
      if(document.visibilityState==="hidden" && navigator.sendBeacon){ try{ navigator.sendBeacon(u, new Blob([body],{type:"text/plain"})); return; }catch(e){} }   /* sendBeacon = POST */
      fetch(u, {method:"POST", body, keepalive:true, headers:{"Content-Type":"text/plain"}}).catch(()=>{});
    }catch(e){}
  };
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
  window.GUARD=GD;
})();
