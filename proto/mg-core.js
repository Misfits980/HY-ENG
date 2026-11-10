/* ═════════ (v590) 🎮 놀이 공원 게임 타워 — 미니 게임 틀
   사용자: 「놀이터가 너무 재미가 없다는 피드백」 → 「타워처럼 뭔가 하나씩 게임 입장이 있어야」 → 「애들 이미 아레나랑 다른 거 다 해 본 애들이야」
          → 「1번은 아스날(1인칭 · 아레나 무브) · 2번은 발판 게임(초록 = 안전 · 파랑 = 밟아서 지우기 · 빨강이 오면 점프하거나 피하기)」
   · 섬 🎡 놀이 공원 입구 양옆에 게임 타워 2채 (isle.js → MG.build · MG.labels)
   · 들어가면 섬은 그대로 멈춰 두고(house.html loop 맨 앞 `if(MG.on) return`) 게임 장면을 따로 그림 → 나오면 섬 그 자리
   · 화면 조작(왼손 조이스틱 · 오른손 화면 끌어 보기 · 버튼) · 키보드/마우스 · 결과 창 · 오늘 🪙 (하루 3판) · 내 기록
   게임은 MG.reg(k, def) 로 붙음 — mg-arena.js(💦 물총 아레나) · mg-grid.js(🟦 발판 게임) */
const MG=(()=>{
  const GM={}, ORDER=[];
  const S={on:false, k:null, run:null, raf:0, last:0, pr0:1, sun:null, api:null, busy:false};
  const $$=id=>document.getElementById(id);
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const nick=()=>{ let n=""; try{ n=(localStorage.getItem("hyeng_nick")||"").trim(); }catch(e){} try{ if(typeof PAD!=="undefined" && PAD.kid && PAD.kid.n) n=PAD.kid.n; }catch(e){} return (n||"나").slice(0,8); };
  const today=()=>{ try{ return dayKey(); }catch(e){ return new Date().toISOString().slice(0,10); } };
  function reg(k, def){ def.k=k; GM[k]=def; if(ORDER.indexOf(k)<0) ORDER.push(k); }

  /* ── 기록 · 오늘 상 (하루 3판까지 🪙) ── */
  const DAY_PAY=3;
  function rec(){ let r=null; try{ r=store("hyeng_proto_mg"); }catch(e){} r=r||{}; r.b=r.b||{}; r.t=r.t||{}; if(r.d!==today()){ r.d=today(); r.n={}; } r.n=r.n||{}; return r; }
  function recSave(r){ try{ store("hyeng_proto_mg", r); }catch(e){} }
  function payLeft(k){ return Math.max(0, DAY_PAY-((rec().n[k])|0)); }
  /* 한 판 끝 — 기록 합치기 + 🪙 (오늘 3판까지) · 반환 = 받은 🪙 */
  function finish(k, coins, upd){ const r=rec(); const left=DAY_PAY-((r.n[k])|0); r.n[k]=((r.n[k])|0)+1; r.b[k]=r.b[k]||{}; r.t[k]=r.t[k]||{}; r.t[k].play=((r.t[k].play)|0)+1;
    try{ if(upd) upd(r.b[k], r.t[k]); }catch(e){ console.warn(e); } recSave(r); let got=0;
    if(left>0 && coins>0){ try{ got=TECO.addCoin(coins)|0; }catch(e){ got=0; } }
    try{ tEv("mg"); tEv("mg_"+k); }catch(e){} return got; }

  /* ── 소리 (물소리 · 맞힘 · 올라감) — 게임 버튼을 누른 뒤라 아이패드도 소리 남 ── */
  const SFX=(()=>{ let ac=null, mute=false, vol=1, mgn=null; const out=a=>{ if(!mgn){ mgn=a.createGain(); mgn.gain.value=vol; mgn.connect(a.destination); } return mgn; };   /* (v599) 소리 크기 */ const ctx=()=>{ if(mute) return null; if(!ac){ try{ ac=new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} } if(ac && ac.state==="suspended"){ try{ ac.resume(); }catch(e){} } return ac; };
    function tone(f, d, type, vol, f2, at){ const a=ctx(); if(!a) return; try{ const o=a.createOscillator(), g=a.createGain(), t=a.currentTime+(at||0); o.type=type||"sine"; o.frequency.setValueAtTime(f,t); if(f2) o.frequency.exponentialRampToValueAtTime(f2,t+d); g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(vol||.05,t+.008); g.gain.exponentialRampToValueAtTime(0.0001,t+d); o.connect(g); g.connect(out(a)); o.start(t); o.stop(t+d+.02); }catch(e){} }
    const nb={};
    function noise(d, vol, fr, q, f2){ const a=ctx(); if(!a) return; try{ const key=Math.round(d*100); let b=nb[key]; if(!b){ const n=Math.floor(a.sampleRate*d); b=a.createBuffer(1,n,a.sampleRate); const c=b.getChannelData(0); for(let i=0;i<n;i++) c[i]=(Math.random()*2-1)*Math.pow(1-i/n,1.6); nb[key]=b; }
        const s=a.createBufferSource(); s.buffer=b; const f=a.createBiquadFilter(); f.type="bandpass"; const t=a.currentTime; f.frequency.setValueAtTime(fr||1200,t); if(f2) f.frequency.exponentialRampToValueAtTime(f2,t+d); f.Q.value=q||.8; const g=a.createGain(); g.gain.value=vol||.08; s.connect(f); f.connect(g); g.connect(out(a)); s.start(); }catch(e){} }
    let lastShot=0;
    return { ctx, set mute(v){ mute=!!v; }, get mute(){ return mute; }, set vol(v){ vol=Math.max(0,+v||0); if(mgn) mgn.gain.value=vol; }, get vol(){ return vol; }, tone, noise,
      shot(k, far){ const n=performance.now(); if(n-lastShot<40) return; lastShot=n; const v=far?.022:.07;
        if(k==="shot"||k==="wave"){ noise(.26,v*1.4,900,.6,400); } else if(k==="snipe"){ noise(.32,v*1.2,1800,.9,600); tone(320,.18,"sine",v*.5,120); } else if(k==="balloon"){ tone(260,.16,"sine",v*.9,520); noise(.12,v*.6,1600); } else if(k==="hammer"){ tone(880,.1,"square",v*.35,1500); tone(1500,.12,"triangle",v*.4,900,.08); } else noise(.14,v,2600,.8,1400); },
      hit(head){ tone(head?2200:1700,.06,"square",.035); if(head) tone(2900,.12,"sine",.05,3300,.04); },
      splash(){ noise(.3,.06,700,.7,300); }, soak(){ tone(300,.25,"sine",.07,900); noise(.35,.06,600); }, hurt(){ noise(.18,.05,500); },
      up(){ [523,659,784,1046].forEach((f,i)=>tone(f,.18,"triangle",.05,0,i*.07)); }, win(){ [392,523,659,784,1046,1318].forEach((f,i)=>tone(f,.24,"triangle",.06,0,i*.09)); },
      jump(){ tone(420,.12,"sine",.03,700); }, land(){ noise(.08,.03,500); }, slide(){ noise(.35,.04,1200,.5,500); }, pad(){ tone(300,.35,"sine",.06,1200); noise(.3,.05,900); },
      tile(i){ tone(660*Math.pow(1.06,Math.min(14,i|0)),.12,"triangle",.05); }, bad(){ tone(200,.3,"sawtooth",.04,90); noise(.2,.06,400); }, tick(){ tone(1200,.04,"square",.02); }, clear(){ [659,784,988,1318].forEach((f,i)=>tone(f,.2,"triangle",.055,0,i*.08)); } }; })();

  /* ── 화면 (게임 중 섬 UI 는 숨김) ── */
  function css(){ if($$("mgCss")) return; const st=document.createElement("style"); st.id="mgCss"; st.textContent=`
body.mgOn > :not(#mgUI):not(#cv):not(#fade):not(#mgLob):not(#mgRes):not(script):not(style){visibility:hidden !important}
#mgUI{position:fixed;inset:0;z-index:30;touch-action:none;user-select:none;-webkit-user-select:none;font-family:var(--kr);color:#fff;display:none;overflow:hidden}
#mgUI.on{display:block}
#mgUI .mgTop{position:absolute;left:0;right:0;top:0;padding:calc(8px + env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) 0 max(10px,env(safe-area-inset-left));display:flex;align-items:flex-start;gap:8px;pointer-events:none}
#mgUI .mgX{pointer-events:auto;border:0;background:rgba(20,30,60,.55);color:#fff;font:inherit;font-size:15px;border-radius:14px;padding:8px 12px;min-height:40px}
#mgUI .mgB{position:absolute;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:50%;border:3px solid rgba(255,255,255,.85);background:rgba(20,40,80,.38);color:#fff;font-size:26px;line-height:1;pointer-events:auto;touch-action:none;transition:transform .06s}
#mgUI .mgB small{font-size:11px;margin-top:3px;opacity:.95}
#mgUI .mgB.tx{font-family:var(--en);font-weight:900;font-size:15px;letter-spacing:.04em}
#mgUI .mgB.dn{transform:scale(.9);background:rgba(255,255,255,.35)}
#mgUI .mgJoy{position:absolute;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;border:3px solid rgba(255,255,255,.55);background:rgba(20,40,80,.18);pointer-events:none;display:none}
#mgUI .mgJoy i{position:absolute;left:50%;top:50%;width:54px;height:54px;margin:-27px 0 0 -27px;border-radius:50%;background:rgba(255,255,255,.8)}
#mgUI .mgJoy.on{display:block}
#mgUI .mgJoyH{position:absolute;left:calc(26px + env(safe-area-inset-left));bottom:calc(30px + env(safe-area-inset-bottom));width:110px;height:110px;border-radius:50%;border:3px dashed rgba(255,255,255,.4);pointer-events:none;display:flex;align-items:center;justify-content:center;font-size:12px;color:rgba(255,255,255,.75);text-align:center}
#mgUI.joyOn .mgJoyH{display:none}
#mgUI .mgMsg{position:absolute;left:50%;top:34%;transform:translate(-50%,-50%) scale(.8);opacity:0;transition:all .18s;font-size:30px;text-align:center;text-shadow:0 3px 0 rgba(0,0,0,.35),0 0 18px rgba(0,0,0,.25);pointer-events:none;white-space:nowrap}
#mgUI .mgMsg small{display:block;font-size:16px;margin-top:6px}
#mgUI .mgMsg.on{opacity:1;transform:translate(-50%,-50%) scale(1)}
#mgUI .mgConf{position:absolute;inset:0;display:none;align-items:center;justify-content:center;background:rgba(10,20,40,.45);pointer-events:auto}
#mgUI .mgConf.on{display:flex}
#mgUI .mgConf div{background:#fff8ea;color:#4b3527;border-radius:22px;padding:18px 20px;text-align:center;font-size:18px;min-width:240px;border:3px solid #cfae7e}
#mgUI .mgConf button,#mgRes button,#mgLob button{font:inherit;border:0;border-radius:16px;padding:12px 18px;font-size:17px;margin:12px 4px 0;min-height:48px;background:#e9dcc4;color:#4b3527}
#mgUI .mgConf button.go,#mgRes button.go,#mgLob button.go{background:#ff8466;color:#fff;box-shadow:0 4px 0 #d9604a}
#mgRes,#mgLob{position:fixed;inset:0;z-index:40;display:none;align-items:center;justify-content:center;background:rgba(10,20,40,.55);font-family:var(--kr);touch-action:none}
#mgRes.on,#mgLob.on{display:flex}
#mgRes .bx,#mgLob .bx{width:min(440px,calc(100vw - 28px));max-height:calc(100% - 40px);overflow:auto;background:#fff8ea;color:#4b3527;border-radius:26px;border:3px solid #cfae7e;padding:18px 18px 16px;text-align:center;box-shadow:0 10px 0 rgba(0,0,0,.15)}
#mgRes h3,#mgLob h3{margin:2px 0 4px;font-size:26px;font-weight:400}
#mgRes .sub,#mgLob .sub{color:#9a7e63;font-size:15px}
#mgRes table{width:100%;border-collapse:collapse;margin:12px 0 4px;font-size:16px}
#mgRes td{padding:6px 4px;border-bottom:1px dashed #e4cda8;text-align:left}
#mgRes td.r{text-align:right;white-space:nowrap}
#mgRes tr.me td{background:#fff0c8;font-weight:700}
#mgRes .coin{display:inline-block;margin-top:10px;background:#fff3c4;border:2px solid #f2b33d;border-radius:14px;padding:6px 12px;font-size:17px}
#mgLob .hero{height:120px;border-radius:18px;margin:10px 0 12px;display:flex;align-items:center;justify-content:center;font-size:64px}
#mgLob ul{list-style:none;padding:0;margin:0 0 6px;text-align:left;font-size:15.5px;line-height:1.45}
#mgLob li{padding:5px 0 5px 30px;position:relative}
#mgLob li i{position:absolute;left:0;top:4px;font-style:normal;font-size:18px}
@media (max-height:560px){ #mgLob .hero{height:64px;font-size:40px;margin:6px 0 8px} #mgLob h3{font-size:22px} #mgLob li{padding:3px 0 3px 28px;font-size:14.5px} }
#mgLob .opt{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin:8px 0 2px}
#mgLob .opt button{margin:0;padding:8px 12px;font-size:15px;min-height:42px;background:#f0e4cc}
#mgLob .opt button.on{background:#5aa7ff;color:#fff;box-shadow:0 3px 0 #2f7fb3}
#mgLob .bst{font-size:14.5px;color:#7a5f45;background:#f5e8d0;border-radius:12px;padding:8px 10px;margin-top:8px}
`; document.head.appendChild(st); }

  /* ── 입력: 조이스틱(왼쪽 아무 곳) · 화면 끌기(오른쪽) · 버튼 · 키보드 · 마우스(잠금) ── */
  const I={mx:0,my:0, lx:0,ly:0, fire:0, jump:0, slide:0, jumpP:0, slideP:0, fireP:0, touch:false, mouse:false, lock:false, k:{}};
  const PT=new Map(); let ROOT=null, joyEl=null, joyR=48, cfg=null;
  function resetI(){ I.mx=I.my=I.lx=I.ly=0; I.fire=I.jump=I.slide=0; I.jumpP=I.slideP=I.fireP=0; I.k={}; PT.clear(); }
  function btnSet(b, v){ if(v && !I[b]) I[b+"P"]=1; I[b]=v?1:0; const el=ROOT && ROOT.querySelector('[data-b="'+b+'"]'); if(el) el.classList.toggle("dn", !!v); }
  function onDown(e){ if(!S.on || !ROOT) return; const bt=e.target.closest && e.target.closest("[data-b]"), x=e.clientX, y=e.clientY;
    if(e.target.closest && e.target.closest(".mgX,.mgConf")) return;
    if(S.api && S.api.menu) return;   /* (v599) 게임 메뉴 화면 = 조이스틱·둘러보기 없음 (그냥 누르기) */
    e.preventDefault();
    if(e.pointerType==="mouse"){ I.mouse=true; if(bt){ btnSet(bt.dataset.b,1); PT.set(e.pointerId,{r:"b", b:bt.dataset.b, x, y}); return; }
      if(cfg && cfg.look){ if(I.lock){ if(e.button===0) btnSet("fire",1); else if(e.button===2) btnSet("slide",1); return; }
        try{ const p=ROOT.requestPointerLock && ROOT.requestPointerLock(); if(p && p.catch) p.catch(()=>{}); }catch(_){} PT.set(e.pointerId,{r:"look", x, y}); return; }
      PT.set(e.pointerId,{r:"look", x, y}); return; }
    I.touch=true;
    if(bt){ const b=bt.dataset.b; btnSet(b,1); PT.set(e.pointerId,{r:"b", b, x, y, look:b==="fire" && cfg && cfg.look}); return; }
    const look=!!(cfg && cfg.look);
    if(!look || x<innerWidth*0.45){ for(const [id,q] of [...PT]) if(q.r==="joy") PT.delete(id);   /* (v597) 버그: 화면을 돌리면 손 뗀 신호가 안 와서 조이스틱이 잠김 → 새로 누르면 예전 것은 버림 */ PT.set(e.pointerId,{r:"joy", ox:x, oy:y}); joyEl.style.left=x+"px"; joyEl.style.top=y+"px"; joyEl.classList.add("on"); ROOT.classList.add("joyOn"); joyMove(0,0); return; }
    PT.set(e.pointerId,{r:"look", x, y}); }
  function joyMove(dx, dy){ const d=Math.hypot(dx,dy), k=d>joyR?joyR/d:1; dx*=k; dy*=k; joyEl.firstChild.style.transform="translate("+dx+"px,"+dy+"px)"; let mx=dx/joyR, my=-dy/joyR; const m=Math.hypot(mx,my); if(m<0.12){ mx=my=0; } I.mx=mx; I.my=my; }
  function onMove(e){ if(!S.on) return; if(I.lock && e.pointerType==="mouse"){ I.lx+=e.movementX||0; I.ly+=e.movementY||0; return; } const p=PT.get(e.pointerId); if(!p) return; e.preventDefault();
    if(p.r==="joy"){ joyMove(e.clientX-p.ox, e.clientY-p.oy); return; }
    if(p.r==="look" || p.look){ I.lx+=e.clientX-p.x; I.ly+=e.clientY-p.y; p.x=e.clientX; p.y=e.clientY; } }
  function onUp(e){ if(I.lock && e.pointerType==="mouse"){ if(e.button===0) btnSet("fire",0); if(e.button===2) btnSet("slide",0); } const p=PT.get(e.pointerId); if(!p) return; PT.delete(e.pointerId);
    if(p.r==="joy"){ I.mx=I.my=0; joyEl.classList.remove("on"); if(![...PT.values()].some(q=>q.r==="joy")) ROOT.classList.remove("joyOn"); }
    if(p.r==="b"){ if(![...PT.values()].some(q=>q.r==="b" && q.b===p.b)) btnSet(p.b,0); } }
  const KM={KeyW:"f",ArrowUp:"f",KeyS:"b",ArrowDown:"b",KeyA:"l",ArrowLeft:"l",KeyD:"r",ArrowRight:"r"};
  function keyAx(){ const k=I.k; if(PT.size && [...PT.values()].some(q=>q.r==="joy")) return; I.mx=(k.r?1:0)-(k.l?1:0); I.my=(k.f?1:0)-(k.b?1:0); const m=Math.hypot(I.mx,I.my); if(m>1){ I.mx/=m; I.my/=m; } }
  function onKey(e, dn){ if(!S.on) return; if(KM[e.code]){ I.k[KM[e.code]]=dn; keyAx(); e.preventDefault(); return; }
    if(e.code==="Space"){ btnSet("jump", dn); e.preventDefault(); return; }
    if(e.code==="ShiftLeft"||e.code==="ShiftRight"||e.code==="KeyC"||e.code==="ControlLeft"){ btnSet("slide", dn); e.preventDefault(); return; }
    if(e.code==="KeyF"||e.code==="Enter"){ btnSet("fire", dn); e.preventDefault(); return; }
    if(dn && e.code==="Escape" && !I.lock){ confirmExit(); } }
  addEventListener("pointermove", onMove, {passive:false}); addEventListener("pointerup", onUp); addEventListener("pointercancel", onUp);
  addEventListener("keydown", e=>onKey(e,1)); addEventListener("keyup", e=>onKey(e,0));
  document.addEventListener("pointerlockchange", ()=>{ I.lock=!!ROOT && document.pointerLockElement===ROOT; if(!I.lock) btnSet("fire",0); });
  addEventListener("blur", ()=>{ if(S.on) resetI(); });
  const unstick=()=>{ if(!S.on) return; resetI(); if(joyEl){ joyEl.classList.remove("on"); } if(ROOT) ROOT.classList.remove("joyOn"); ROOT && ROOT.querySelectorAll(".mgB.dn").forEach(b=>b.classList.remove("dn")); };
  addEventListener("orientationchange", unstick); let lastW=innerWidth; addEventListener("resize", ()=>{ if(Math.abs(innerWidth-lastW)>40){ lastW=innerWidth; unstick(); } });   /* 가로 ↔ 세로 */ document.addEventListener("visibilitychange", unstick);
  try{ if(screen.orientation) screen.orientation.addEventListener("change", unstick); }catch(e){}

  function mkUI(def){ css(); let u=$$("mgUI"); if(u) u.remove(); u=document.createElement("div"); u.id="mgUI"; document.body.appendChild(u); ROOT=u; cfg=def.ui||{};
    const B=(cfg.btns||[]).map(b=>'<div class="mgB '+(b.cls||"")+'" data-b="'+b.b+'" style="'+b.st+'">'+b.ic+(b.t?'<small>'+b.t+'</small>':'')+'</div>').join("");
    u.innerHTML='<div class="mgHud"></div><div class="mgJoy"><i></i></div><div class="mgJoyH">여기를 끌어<br>움직여요</div>'+B+'<div class="mgTop"><button class="mgX">✕ 나가기</button><div class="mgTopR" style="flex:1"></div></div><div class="mgMsg"></div><div class="mgConf"><div>게임을 그만할까요?<br><small style="color:#9a7e63">이번 판 기록은 남지 않아요</small><br><button class="no">계속하기</button><button class="go">나가기</button></div></div>';
    joyEl=u.querySelector(".mgJoy");
    u.addEventListener("pointerdown", onDown, {passive:false});
    u.addEventListener("contextmenu", e=>e.preventDefault());
    u.querySelector(".mgX").onclick=()=>confirmExit();
    u.querySelector(".mgConf .no").onclick=()=>{ u.querySelector(".mgConf").classList.remove("on"); if(S.run && S.run.pause) S.run.pause(false); };
    u.querySelector(".mgConf .go").onclick=()=>{ u.querySelector(".mgConf").classList.remove("on"); exit(); };
    u.classList.add("on"); return u; }
  function confirmExit(){ if(!ROOT) return; try{ if(document.pointerLockElement) document.exitPointerLock(); }catch(e){} ROOT.querySelector(".mgConf").classList.add("on"); if(S.run && S.run.pause) S.run.pause(true); resetI(); }
  let msgT=0; function msg(h, ms){ if(!ROOT) return; const m=ROOT.querySelector(".mgMsg"); m.innerHTML=h; m.classList.add("on"); clearTimeout(msgT); msgT=setTimeout(()=>m.classList.remove("on"), ms||1400); }

  /* ── 들어가기 · 나가기 ── */
  function canEnter(){ try{ if(typeof F!=="undefined" && F.st!=="idle") return false; if(typeof trip!=="undefined" && trip.busy) return false; if(typeof TW!=="undefined" && TW.on) return false; }catch(e){} return !S.on && !S.busy; }
  function enter(k, opt){ const def=GM[k]; if(!def || !canEnter()) return false; S.busy=true; try{ SFX.ctx(); }catch(e){}
    try{ hero.path=[]; hero.moving=false; }catch(e){}
    const fd=$$("fade"); if(fd) fd.classList.add("on");
    setTimeout(()=>{ try{
        S.k=k; S.on=true; document.body.classList.add("mgOn"); resetI(); mkUI(def);
        try{ S.sun=[sun.intensity, sun.color.getHex()]; sun.intensity=.95; sun.color.setHex(0xfff0d8); TOON.light(); }catch(e){ S.sun=null; }   /* 툰 그림자 기준 = 낮 (섬이 밤이어도 게임은 밝게) */
        S.pr0=renderer.getPixelRatio(); const pr=Math.min(S.pr0, (typeof LOW!=="undefined" && LOW) ? 1 : 1.5); if(pr!==S.pr0){ renderer.setPixelRatio(pr); try{ TOON.resize(); }catch(e){} }
        S.api={I, ui:ROOT, hud:ROOT.querySelector(".mgHud"), topR:ROOT.querySelector(".mgTopR"), msg, sfx:SFX, nick:nick(), av:(typeof av!=="undefined"?Object.assign({},av):{}), opt:opt||{}, renderer, end:(r)=>result(k, r), low:typeof LOW!=="undefined" && LOW, restart:(o)=>restart(k, o)};
        S.run=def.start(S.api); S.last=performance.now(); cancelAnimationFrame(S.raf); S.raf=requestAnimationFrame(frame);
      }catch(e){ console.warn("MG", e); S.on=false; document.body.classList.remove("mgOn"); }
      S.busy=false; if(fd) setTimeout(()=>fd.classList.remove("on"), 60); }, 240);
    return true; }
  /* (v599) 같은 게임을 처음부터 (메뉴로 · 한 판 더) */
  function restart(k, o){ const def=GM[k]; if(!S.on || !def) return; $$("mgRes") && $$("mgRes").classList.remove("on"); try{ if(document.pointerLockElement) document.exitPointerLock(); }catch(e){}
    try{ if(S.run && S.run.dispose) S.run.dispose(); }catch(e){} resetI(); mkUI(def); S.api.ui=ROOT; S.api.hud=ROOT.querySelector(".mgHud"); S.api.topR=ROOT.querySelector(".mgTopR"); S.api.menu=false; S.api.opt=o||{}; S.run=def.start(S.api); }
  function frame(now){ if(!S.on) return; S.raf=requestAnimationFrame(frame); const dt=Math.min(0.05, Math.max(0,(now-S.last)/1000)); S.last=now; step(dt, true); }
  function step(dt, show){ const R=S.run; if(!R) return; try{ R.tick(dt); }catch(e){ console.warn("MG tick", e); }
    I.jumpP=I.slideP=I.fireP=0;
    if(show){ const cv=renderer.domElement, w=cv.clientWidth||innerWidth, h=cv.clientHeight||innerHeight; if(R.cam && Math.abs(R.cam.aspect-w/h)>1e-3){ R.cam.aspect=w/h; R.cam.updateProjectionMatrix(); }
      try{ if(R.render) R.render(renderer); else draw(R.scene, R.cam); }catch(e){ console.warn("MG draw", e); } } }
  /* 섬과 같은 툰 테두리 (TOON 의 깊이 테두리 후처리를 게임 장면에도) — 느린 기기는 테두리 없이 */
  function draw(sc, cm){ let T=null; try{ T=TOON; }catch(e){} if(T && T.edge && T.post){ try{ if(!T.rt) T.resize(); }catch(e){} }
    if(T && T.edge && T.rt && T.post){ const u=T.post.material.uniforms; u.n.value=cm.near; u.f.value=cm.far; renderer.setRenderTarget(T.rt); renderer.render(sc, cm); renderer.setRenderTarget(null); renderer.render(T.ps, T.pc); }
    else renderer.render(sc, cm); }
  function exit(){ if(!S.on) return; const fd=$$("fade"); if(fd) fd.classList.add("on"); try{ if(document.pointerLockElement) document.exitPointerLock(); }catch(e){}
    setTimeout(()=>{ try{ if(S.run && S.run.dispose) S.run.dispose(); }catch(e){ console.warn(e); } S.run=null; S.on=false; cancelAnimationFrame(S.raf);
      $$("mgRes") && $$("mgRes").classList.remove("on"); if(ROOT){ ROOT.remove(); ROOT=null; } document.body.classList.remove("mgOn"); resetI();
      try{ if(S.sun){ sun.intensity=S.sun[0]; sun.color.setHex(S.sun[1]); TOON.light(); } }catch(e){}
      try{ renderer.autoClear=true; if(renderer.getPixelRatio()!==S.pr0) renderer.setPixelRatio(S.pr0); resize(); }catch(e){}
      try{ dirty=true; last=performance.now(); }catch(e){} try{ drawLabels(); }catch(e){}
      if(fd) setTimeout(()=>fd.classList.remove("on"), 60); }, 240); }

  /* ── 결과 창 ── r = {k, title, sub, rows:[[이름, 오른쪽 글, me]], coins, upd(best,tot)} ── */
  function result(k, r){ const def=GM[k]; if(!S.on) return; css(); try{ if(document.pointerLockElement) document.exitPointerLock(); }catch(e){}
    const got=finish(k, r.coins|0, r.upd); let el=$$("mgRes"); if(!el){ el=document.createElement("div"); el.id="mgRes"; document.body.appendChild(el); }
    const rows=(r.rows||[]).map((x,i)=>'<tr class="'+(x[2]?"me":"")+'"><td>'+(i<3?["🥇","🥈","🥉"][i]:(i+1)+".")+' '+esc(x[0])+'</td><td class="r">'+x[1]+'</td></tr>').join("");
    const left=payLeft(k);
    el.innerHTML='<div class="bx"><h3>'+r.title+'</h3><div class="sub">'+(r.sub||"")+'</div>'+(rows?'<table>'+rows+'</table>':'')+(r.extra||"")+
      (got>0?'<div class="coin">🪙 +'+got+' <small>(오늘 '+(DAY_PAY-left)+'/'+DAY_PAY+'판)</small></div>':'<div class="sub" style="margin-top:10px">오늘 🪙 상은 다 받았어요 — 그래도 기록은 남아요!</div>')+
      '<div><button class="out">🏝 섬으로</button>'+(def.menu?'<button class="mn">'+def.ic+' 메뉴</button>':'')+'<button class="go">🔁 한 판 더</button></div></div>';
    el.classList.add("on"); try{ SFX.win(); }catch(e){}
    el.querySelector(".out").onclick=()=>{ el.classList.remove("on"); exit(); };
    el.querySelector(".go").onclick=()=>{ el.classList.remove("on"); restart(k, Object.assign({}, S.api && S.api.opt, r.again||{})); };
    if(def.menu) el.querySelector(".mn").onclick=()=>{ el.classList.remove("on"); restart(k, {}); };
    return got; }

  /* ── 입구 안내 창 (게임 고르기 전) ── */
  function lobby(k){ const def=GM[k]; if(!def) return; if(def.menu){ enter(k, {}); return; }   /* (v599) 자기 메뉴 화면이 있는 게임은 바로 */ css(); let el=$$("mgLob"); if(!el){ el=document.createElement("div"); el.id="mgLob"; document.body.appendChild(el); }
    const r=rec(), b=r.b[k]||{}, t=r.t[k]||{}, opt={}; (def.opts||[]).forEach(o=>{ let v=null; try{ v=(store("hyeng_proto_mgopt")||{})[k+"."+o.k]; }catch(e){} opt[o.k]=v!=null?v:o.d; });
    const draw=()=>{ const left=payLeft(k);
      el.innerHTML='<div class="bx"><h3>'+def.ic+' '+def.nm+'</h3><div class="sub">'+def.tag+'</div><div class="hero" style="background:'+def.bg+'">'+def.big+'</div><ul>'+def.how.map(h=>'<li><b>'+h[0]+'</b>'+h[1]+'</li>').join("")+'</ul>'+
        (def.opts||[]).map(o=>'<div class="sub" style="margin-top:6px">'+o.t+'</div><div class="opt">'+o.v.map(v=>'<button data-o="'+o.k+'" data-v="'+v[0]+'" class="'+(String(opt[o.k])===String(v[0])?"on":"")+'">'+v[1]+'</button>').join("")+'</div>').join("")+
        '<div class="bst">'+(def.bestTxt?def.bestTxt(b,t):"")+'<br>오늘 🪙 상: '+(left>0?'<b>'+left+'판</b> 남음 ('+def.payTxt+')':'다 받았어요 (기록 도전은 계속!)')+'</div>'+
        '<div><button class="no">돌아가기</button><button class="go">▶ 시작!</button></div></div>';
      el.querySelectorAll("[data-o]").forEach(bn=>bn.onclick=()=>{ const v=bn.dataset.v; opt[bn.dataset.o]=(v==="1"||v==="0")?+v:v; try{ const s=store("hyeng_proto_mgopt")||{}; s[k+"."+bn.dataset.o]=opt[bn.dataset.o]; store("hyeng_proto_mgopt", s); }catch(e){} draw(); });
      el.querySelector(".no").onclick=()=>el.classList.remove("on");
      el.querySelector(".go").onclick=()=>{ el.classList.remove("on"); enter(k, Object.assign({}, opt)); }; };
    draw(); el.classList.add("on"); }

  /* ── 섬 놀이 공원 입구 양옆 게임 타워 2채 ── */
  const SPOT={};
  const GATES=[{k:"arena", at:[46.5,11.5], face:Math.PI*.12}, {k:"grid", at:[65.5,11.5], face:-Math.PI*.12}, {k:"card", at:null, face:-Math.PI/2, sp:"mgCard"}, {k:"draw", at:null, face:-Math.PI/2, sp:"mgDraw"}, {k:"fruit", at:null, face:0, sp:"mgFruit"}, {k:"c4", at:null, face:Math.PI, sp:"mgC4"}, {k:"bowl", at:null, face:Math.PI/2, sp:"mgBowl"}];   /* (v635) 🎨 그림 공방 = 놀이 섬 동쪽 */   /* (v633) 🃏 카드 카페 = 새 섬 놀이 섬 가운데만 */
  function build(ctx){ const {G, OX, OZ, busy, cols, vcMerge}=ctx; if(!vcMerge) return; const L=[], GL=[];
    { const SPm=ctx.MAP && ctx.MAP.spots; if(SPm && SPm.mgArena){ GATES[0].at=SPm.mgArena; GATES[1].at=SPm.mgGrid; GATES[0].face=GATES[1].face=Math.PI; } GATES.forEach(g=>{ if(g.sp) g.at=(SPm && SPm[g.sp]) || null; }); }   /* (v607~) 새 섬 5판 = 🎡 놀이 섬 */
    const add=(geo, col, x, y, z, o)=>{ o=o||{}; const m=new THREE.Matrix4(), q=new THREE.Quaternion().setFromEuler(new THREE.Euler(o.rx||0, o.ry||0, o.rz||0)); m.compose(new THREE.Vector3(x,y,z), q, new THREE.Vector3(o.sx||1,o.sy||1,o.sz||1)); (o.glow?GL:L).push({g:geo, col, m}); };
    const BX=(w,h,d)=>new THREE.BoxGeometry(w,h,d), CY=(a,b,h,n)=>new THREE.CylinderGeometry(a,b,h,n||20), SP=(r)=>new THREE.SphereGeometry(r,18,12);
    GATES.forEach(g=>{ if(!g.at || !GM[g.k]) return; const [gx,gz]=g.at, X=gx+OX, Z=gz+OZ, f=g.face, c=Math.cos(f), s=Math.sin(f), P=(u,y,v,geo,col,o)=>{ o=Object.assign({},o||{}); o.ry=(o.ry||0)+f; add(geo,col, X+u*c+v*s, y, Z-u*s+v*c, o); };
      busy.push([gx,gz,4.2]); cols.push([X,Z,2.3]);
      ctx.disc && ctx.disc(gx,gz,3.3,g.k==="arena"?0xbfe6ff:g.k==="draw"?0xffe2c4:g.k==="fruit"?0xd8f5c8:g.k==="c4"?0xcfdcff:g.k==="bowl"?0xe3d6ff:0xd6d0ff,1);
      if(g.k==="card"){   /* (v633) 🃏 카드 카페 — 크림색 집 · 4색 줄무늬 차양 · 지붕 위 부채꼴 카드 4장(빛남) · 창문 · 문 · 입간판 */
        P(0,1.5,0, BX(4.4,3,3.8), 0xfff1dc); P(0,.12,0, BX(4.6,.24,4), 0x8a5a3c); P(0,3.12,0, BX(4.7,.26,4.1), 0x5b3a7a); P(0,3.34,0, BX(4.3,.18,3.7), 0x7a4fa0);
        for(let i=0;i<8;i++) P(-1.925+i*.55,2.62,2.25, BX(.55,.16,.95), [0xff5a5f,0xffc83d,0x3fc46a,0x3ea2ff][i%4], {rx:.42});
        P(0,1.0,1.92, BX(1.2,1.9,.12), 0x6e4430); P(0,1.95,1.92, CY(.6,.6,.12,18,1,false), 0x6e4430, {rx:Math.PI/2}); P(.38,1.0,2.0, SP(.07), 0xffd36b);
        [-1.45,1.45].forEach(u=>{ P(u,1.55,1.92, BX(1.05,.95,.1), 0xffe9a8, {glow:1}); P(u,1.55,1.95, BX(.08,.95,.06), 0x8a5a3c); P(u,1.55,1.95, BX(1.05,.08,.06), 0x8a5a3c); P(u,1.0,2.02, BX(1.2,.1,.22), 0x8a5a3c); });
        [[0xff5a5f,-.42],[0xffc83d,-.14],[0x3fc46a,.14],[0x3ea2ff,.42]].forEach(([cc,a],i)=>{ P(Math.sin(a)*.9,4.35+Math.cos(a)*.35-.35,.0+i*.02, BX(.95,1.35,.06), 0xfff8ea, {rz:-a}); P(Math.sin(a)*.9,4.35+Math.cos(a)*.35-.35,.04+i*.02, BX(.8,1.2,.04), cc, {rz:-a, glow:1}); });
        P(0,3.55,0, CY(.08,.1,.6,8), 0x8a5a3c);
        P(2.7,.55,2.1, BX(.7,1.0,.08), 0x3b2433, {rx:-.18}); P(2.7,.62,2.15, BX(.55,.7,.04), 0xffe14d, {rx:-.18, glow:1});
        SPOT.card=[X,4.2,Z];
      } else if(g.k==="draw"){   /* (v635) 🎨 그림 공방 — 하얀 벽 · 물감 흘러내림 · 파란 문 · 동그란 창 · 지붕 위 이젤(그림: 해·언덕·집) · 큰 연필 · 물감 통 */
        P(0,.12,0, BX(4.4,.24,3.9), 0x8a5a3c); P(0,1.55,0, BX(4.2,2.9,3.6), 0xfffaf0); P(0,3.1,0, BX(4.5,.24,3.9), 0x5b3a7a); P(0,3.28,0, BX(4.1,.14,3.5), 0x7a4fa0);
        const PC=[0xff5a5f,0xffd23f,0x3fc46a,0x3ea2ff,0x9a6bff,0xff9a3d];
        for(let i=0;i<8;i++){ const hh=.35+((i*37)%5)*.12; P(-1.85+i*.53,2.98-hh/2,1.82, BX(.36,hh,.06), PC[i%6]); P(-1.85+i*.53,2.98-hh,1.83, SP(.18), PC[i%6], {sz:.35}); }
        P(0,1.0,1.82, BX(1.15,1.85,.12), 0x3ea2ff); P(0,1.0,1.9, BX(.95,1.65,.04), 0x5ab8ff); P(.36,1.0,1.94, SP(.07), 0xffd36b);
        [-1.45,1.45].forEach(u=>{ P(u,1.5,1.83, SP(.5), 0x8a5a3c, {sz:.12}); P(u,1.5,1.86, SP(.42), 0xffe9a8, {sz:.1, glow:1}); });
        [-.85,.85].forEach((u,j)=>P(u,4.25,-.35, BX(.12,2.5,.12), 0x8a5a3c, {rz:j?-.12:.12})); P(0,4.0,-.75, BX(.12,1.9,.12), 0x6e4430); P(0,3.75,0, BX(2.4,.12,.45), 0x8a5a3c);
        P(0,4.65,-.2, BX(2.5,1.85,.08), 0x8a5a3c); P(0,4.65,-.14, BX(2.3,1.65,.06), 0xffffff);
        P(-.65,5.05,-.09, SP(.28), 0xffd23f, {sz:.12, glow:1}); P(.35,4.15,-.09, SP(.85), 0x3fc46a, {sy:.42, sz:.08, glow:1}); P(.55,4.55,-.08, BX(.42,.34,.04), 0xff5a5f, {glow:1}); P(.55,4.78,-.075, BX(.5,.14,.04), 0x9a6bff, {rz:.0, glow:1}); P(.45,5.1,-.08, SP(.2), 0x7fe0ff, {sz:.12, glow:1});
        P(2.5,1.6,1.25, CY(.22,.22,2.7,6), 0xffd23f); P(2.5,3.22,1.25, new THREE.ConeGeometry(.22,.55,6), 0xf3c99b); P(2.5,3.44,1.25, SP(.075), 0x3b2433); P(2.5,.32,1.25, CY(.23,.23,.18,6), 0xc8c8d0); P(2.5,.13,1.25, CY(.22,.22,.22,6), 0xff7eb6);
        P(-2.45,.27,1.55, CY(.36,.3,.52,14), 0x3ea2ff); P(-2.45,.55,1.55, CY(.33,.33,.04,14), 0xff5a5f, {glow:1}); P(-2.1,.18,2.0, CY(.25,.21,.36,12), 0xffd23f); P(-2.1,.37,2.0, CY(.23,.23,.03,12), 0x3fc46a, {glow:1});
        SPOT.draw=[X,4.2,Z];
      } else if(g.k==="fruit"){   /* (v636) 🍉 과일 가게 — 노란 벽 · 수박 지붕(둥근 초록 + 빨간 띠) · 빨강·하양 차양 · 과일 진열대 · 지붕 위 큰 체리 2알 · 📟 형광판 간판 */
        P(0,.12,0, BX(4.4,.24,3.7), 0x8a5a3c); P(0,1.4,0, BX(4.1,2.6,3.4), 0xfff2c4);
        P(0,2.72,0, SP(2.35), 0x38b25a, {sy:.62}); P(0,2.72,0, CY(2.36,2.36,.32,28), 0xff4d5e); P(0,2.9,0, CY(2.2,2.36,.06,28), 0xfff6e8);
        for(let i=0;i<7;i++){ const a=i/7*Math.PI*2; P(Math.cos(a)*1.55,3.55,Math.sin(a)*1.55, SP(.42), 0x1d6e35, {sy:.5, ry:-a}); }
        for(let i=0;i<8;i++) P(-1.84+i*.525,2.25,1.95, BX(.52,.14,.8), i%2?0xffffff:0xff4d5e, {rx:.4});
        P(0,.95,1.72, BX(1.1,1.75,.1), 0x6e4430); P(.36,.95,1.79, SP(.07), 0xffd36b);
        [-1.45,1.45].forEach((u,j)=>{ P(u,.55,1.95, BX(1.05,.7,.5), 0xb07a50); [[0xff9a3d,-.3],[0xf2453d,0],[0xffd84a,.3]].forEach(([cc,du],k)=>P(u+du,1.02,1.95+(k%2)*.08, SP(.17), j?[0x9466ee,0x38b25a,0xff4d5e][k]:cc)); });
        [[-.45,0],[.45,.25]].forEach(([u,dz])=>{ P(u,4.55,dz, SP(.55), 0xe8344e, {glow:1}); P(u-.15,4.75,dz-.2, SP(.13), 0xffffff, {glow:1}); });
        P(0,5.35,.1, BX(.08,.9,.08), 0x3f9a4a, {rz:.5}); P(.22,5.32,.2, BX(.08,.9,.08), 0x3f9a4a, {rz:-.45}); P(.08,5.75,.1, SP(.24), 0x4cc36a, {sx:1.6, sy:.5});
        P(2.55,1.25,1.4, BX(.12,2.5,.12), 0x3b2433); P(2.55,2.35,1.48, BX(1.0,.7,.08), 0x06090f); P(2.55,2.35,1.53, BX(.84,.12,.02), 0x3dff9a, {glow:1}); P(2.55,2.5,1.53, BX(.6,.08,.02), 0xff5ce1, {glow:1}); P(2.55,2.2,1.53, BX(.7,.08,.02), 0xffe14d, {glow:1});
        SPOT.fruit=[X,4.6,Z];
      } else if(g.k==="c4"){   /* (v637) 🔴 4줄 탑 — 하늘색 집 · 지붕 위 큰 파란 판(빨강·노랑 알 · 4알 줄이 빛남) · 노란 줄무늬 · 문 */
        P(0,.12,0, BX(4.3,.24,3.5), 0x8a5a3c); P(0,1.2,0, BX(4,2.2,3.2), 0xeaf0ff); P(0,2.38,0, BX(4.2,.2,3.4), 0x2a4fd0);
        for(let i=0;i<5;i++) P(-1.6+i*.8,1.2,1.62, BX(.36,2.1,.05), 0xffd23f);
        P(0,.95,1.64, BX(1.1,1.7,.1), 0x2a4fd0); P(.35,.95,1.71, SP(.07), 0xffd36b);
        P(0,3.9,.2, BX(3.7,2.9,.34), 0x3b6cff); [-1.95,1.95].forEach(u=>P(u,3.4,.2, BX(.22,3.9,.5), 0x2a4fd0)); P(0,2.55,.2, BX(4.2,.2,.7), 0xffc83d);
        const PAT=["ryry","yrry","ryyr"]; for(let r=0;r<3;r++) for(let c=0;c<4;c++){ const k=PAT[r][c], hot=(r===2-c+0 && c<3)||false; P(-1.26+c*.84, 3.05+r*.84, .4, SP(.33), k==="r"?0xff4d5e:0xffd23f, {sz:.3, glow:1}); }
        [[0,0],[1,1],[2,2]].forEach(([c,r])=>P(-1.26+c*.84, 3.05+r*.84, .5, SP(.14), 0xffffff, {sz:.3, glow:1}));
        P(1.5,5.75,.2, SP(.5), 0xff4d5e, {sz:.3, glow:1}); P(1.5,5.75,.32, SP(.2), 0xffffff, {sz:.2, glow:1}); P(.9,5.6,.2, SP(.35), 0xffd23f, {sz:.3, glow:1});
        SPOT.c4=[X,5.2,Z];
      } else if(g.k==="bowl"){   /* (v638) 🎳 볼링장 — 보라 집 · 지붕 위 큰 볼링 핀 + 공 · 앞벽에 큰 다트판 · 네온 줄 */
        P(0,.12,0, BX(4.4,.24,3.7), 0x8a5a3c); P(0,1.35,0, BX(4.1,2.5,3.4), 0x5b3aff); P(0,2.68,0, BX(4.3,.18,3.6), 0x3a2290);
        P(0,2.4,1.72, BX(4.1,.08,.04), 0xff5ce1, {glow:1}); P(0,.42,1.72, BX(4.1,.08,.04), 0x3dff9a, {glow:1});
        P(-.7,.95,1.71, BX(1.0,1.7,.1), 0x1d1640); P(-.38,.95,1.78, SP(.07), 0xffd36b);
        [[1.0,0xffffff],[.82,0x2b2233],[.62,0xff4d5e],[.48,0x3fc46a],[.3,0xffd84a],[.14,0xff4d5e]].forEach(([r,cc],i)=>P(1.1,1.45,1.72+i*.012, SP(r*.62), cc, {sz:.04, glow:i>=2?1:0}));
        P(.0,3.15,-.3, SP(.62), 0xfffaf2, {sy:1.25}); P(0,3.95,-.3, CY(.26,.36,.6,16), 0xfffaf2); P(0,4.45,-.3, SP(.36), 0xfffaf2); [4.0,4.15].forEach(y=>P(0,y,-.3, CY(.29,.3,.07,16), 0xff4d5e));
        P(1.25,3.35,.5, SP(.62), 0xff5ce1, {glow:1}); [[1.05,3.6,.98],[1.3,3.68,1.05],[1.18,3.4,1.1]].forEach(([u,y,v])=>P(u,y,v, SP(.09), 0x1d1640));
        P(-1.4,3.0,.6, SP(.4), 0xfffaf2, {sy:1.2}); P(-1.4,3.55,.6, SP(.22), 0xfffaf2); P(-1.4,3.42,.6, CY(.17,.18,.05,12), 0xff4d5e);
        SPOT.bowl=[X,5.0,Z];
      } else if(g.k==="arena"){   /* 💦 물총 아레나 — 둥근 경기장 · 줄무늬 · 문 · 꼭대기 큰 물방울 · 옆에 큰 물총 */
        P(0,1.3,0, CY(2.1,2.25,2.6,28), 0x5ab8ff); P(0,2.68,0, CY(2.18,2.18,.18,28), 0xffffff); P(0,1.0,0, CY(2.27,2.3,.22,28), 0xffffff);
        P(0,3.15,0, CY(1.75,2.1,.8,28), 0x3d8fe0); P(0,3.62,0, CY(1.8,1.8,.16,28), 0xffd23f);
        P(0,4.7,0, SP(.95), 0x7fe0ff, {sy:1.0, glow:1}); P(0,5.85,0, new THREE.ConeGeometry(.66,1.25,18), 0x7fe0ff, {glow:1}); P(.32,4.95,.72, SP(.22), 0xffffff, {glow:1});
        P(0,.95,2.05, BX(1.35,1.9,.5), 0x2a3550); P(0,1.95,2.12, CY(.68,.68,.5,18,1,false), 0x2a3550, {rx:Math.PI/2}); P(0,2.1,2.35, BX(1.9,.32,.2), 0xffd23f);
        [-1,1].forEach(k=>P(k*.95,1.1,2.25, BX(.26,2.2,.26), 0xff8466));
        /* 큰 물총 (주황 몸 · 파란 물통 · 손잡이) */
        P(-2.5,2.2,.8, BX(.5,.55,1.9), 0xff9a3d, {rx:-.2}); P(-2.5,2.75,.6, CY(.33,.33,.95,16), 0x46b3ff, {rx:Math.PI/2-.2}); P(-2.5,1.75,.2, BX(.36,.75,.36), 0xff9a3d, {rx:.3}); P(-2.5,2.42,1.85, CY(.11,.14,.5,10), 0xffd23f, {rx:Math.PI/2-.2});
        [0,1,2,3,4,5,6,7].forEach(i=>{ const a=i/8*Math.PI*2; P(Math.cos(a)*2.24,1.6,Math.sin(a)*2.24, BX(.12,.9,.12), 0xffffff, {ry:-a}); });
        SPOT.arena=[X,3.9,Z];
      } else {   /* 🟦 발판 게임 — 남색 네모 건물 · 앞면 LED 칸(파랑·초록·빨강) · 지붕 빛 테두리 · 위에 떠 있는 발판 3장 */
        P(0,1.7,0, BX(4,3.4,3.6), 0x2c2f5a); P(0,3.48,0, BX(4.2,.18,3.8), 0x1d1f3d);
        const T=[0x46b3ff,0x46b3ff,0x5ee36b,0x46b3ff,0xff4d6d,0x46b3ff,0x5ee36b,0x46b3ff,0x46b3ff,0xff4d6d,0x46b3ff,0x5ee36b,0x46b3ff,0x46b3ff,0x46b3ff,0x5ee36b];
        for(let i=0;i<4;i++) for(let j=0;j<4;j++){ if(j<2 && (i===1||i===2)) continue; P(-1.35+i*.9, .55+j*.78, 1.82, BX(.78,.66,.06), T[i*4+j], {glow:1}); }
        P(0,1.0,1.84, BX(1.5,1.9,.06), 0x0f1024);
        [[-2.05,0],[2.05,0]].forEach(([u])=>P(u,3.58,0, BX(.1,.1,3.8), 0x7fe0ff, {glow:1})); [[1.85],[-1.85]].forEach(([v])=>P(0,3.58,v, BX(4.2,.1,.1), 0x7fe0ff, {glow:1}));
        [[0,4.45,0,0x46b3ff,.2],[-.9,5.05,.3,0x5ee36b,-.25],[.85,5.6,-.2,0xff4d6d,.35]].forEach(([u,y,v,cc,r])=>{ P(u,y,v, BX(1.1,.16,1.1), cc, {glow:1, ry:r}); P(u,y-.11,v, BX(1.16,.06,1.16), 0x1d1f3d, {ry:r}); });
        P(0,4.05,0, CY(.08,.08,1.3,8), 0x9aa0c8);
        SPOT.grid=[X,3.9,Z];
      } });
    const m=vcMerge(L); m.name="mgGates"; G.add(m);
    if(GL.length){ const gm=vcMerge(GL, new THREE.MeshBasicMaterial({vertexColors:true, toneMapped:false})); gm.castShadow=false; gm.receiveShadow=false; G.add(gm); } }
  function walkNear(p, then){ try{ const x=Math.floor(p[0]), z=Math.floor(p[2]); let best=null; for(let r=2;r<6 && !best;r++) for(let dx=-r;dx<=r && !best;dx++) for(let dz=-r;dz<=r;dz++){ if(Math.max(Math.abs(dx),Math.abs(dz))!==r) continue; if(!ISLE.blocked(x+dx,z+dz)){ best=[x+dx,z+dz]; break; } }
      const hp=hero.g.position; if(Math.hypot(hp.x-p[0],hp.z-p[2])<4.2 || !best){ then(); return; } walkTo(best[0],best[1],then); }catch(e){ then(); } }
  function labels(L){ GATES.forEach(g=>{ const p=SPOT[g.k], d=GM[g.k]; if(!p || !d) return; L.push({k:"mg_"+g.k, ic:d.ic, t:d.nm, p, r:4.4, act:()=>walkNear(p, ()=>lobby(g.k))}); }); }

  /* ══ (v598) 👫 같이 하기 방 — 방 목록 · 대기방 · 방장 시작 → 10초 · 위치 보내기 · 사건(맞음·잡음) 주고받기 ══
     /hy/day/<pre><날>/<방>/{h:{c 방장, n, st, seed, hb, …}, p:{<코드>:상태}, e:{<코드>:{<id>:사건}}, fd:{<id>:소식}, b: 봇(방장)} — 서버 규칙 /hy/day/$d/$k 그대로 */
  function room(api, cfg){ const MAX=cfg.max||6, WAITMS=cfg.wait||10000, OK=typeof NET!=="undefined";
    const code=(()=>{ try{ return myCode; }catch(e){ return "ME"+Math.floor(Math.random()*999); } })(), nm=api.nick;
    const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } }, day=()=>{ try{ return dayKey().replace(/\D/g,""); }catch(e){ return "0"; } };
    const BASE=()=>"/hy/day/"+cfg.pre+day(), esc2=x=>String(x==null?"":x).replace(/[<>&"]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c]));
    const R={code, phase:"room", id:null, path:null, d:null, host:false, rooms:[], busy:false, listT:0, pollT:0, sendT:0, hbT:0, last:null, seenE:{}, seenF:{}, onEv:null, onFeed:null, onStart:null, node:null};
    const P=document.createElement("div"); P.className="mgRoomP"; api.ui.appendChild(P); P.addEventListener("pointerdown", e=>e.stopPropagation());
    if(!$$("mgRoomCss")){ const st=document.createElement("style"); st.id="mgRoomCss"; st.textContent=`#mgUI .mgRoomP{position:absolute;left:50%;top:calc(58px + env(safe-area-inset-top));transform:translateX(-50%);width:min(380px,calc(100vw - 24px));background:rgba(10,14,50,.86);border:2px solid rgba(127,224,255,.55);border-radius:20px;padding:12px 14px;pointer-events:auto;text-align:center;font-size:16px;z-index:3}
#mgUI .mgRoomP h4{margin:0 0 6px;font-size:20px;font-weight:400} #mgUI .mgRoomP .sub{font-size:13.5px;opacity:.85;margin:4px 0}
#mgUI .mgRoomP button{font:inherit;border:0;border-radius:14px;padding:10px 14px;margin:5px 3px 0;min-height:46px;background:#2f8cff;color:#fff;font-size:16px} #mgUI .mgRoomP button.go{background:#2fd866;color:#10123a} #mgUI .mgRoomP button.gr{background:rgba(255,255,255,.18)}
#mgUI .mgRoomP .rl{display:flex;flex-direction:column;gap:6px;margin:8px 0;max-height:34vh;overflow:auto} #mgUI .mgRoomP .rl button{margin:0;width:100%;text-align:left;background:rgba(255,255,255,.12)}
#mgUI .mgRoomP .pl{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:8px 0} #mgUI .mgRoomP .pl span{background:rgba(255,255,255,.14);border-radius:12px;padding:5px 10px} #mgUI .mgRoomP .pl span.me{background:#ff8466} #mgUI .mgRoomP .pl span.bt{opacity:.5;border:1.5px dashed rgba(255,255,255,.5);background:none}
#mgUI .mgRoomCnt{position:absolute;left:50%;top:40%;transform:translate(-50%,-50%);font-size:84px;font-family:var(--en);font-weight:900;text-shadow:0 5px 0 rgba(0,0,0,.35);pointer-events:none;color:#fff}`; document.head.appendChild(st); }
    const CNT=document.createElement("div"); CNT.className="mgRoomCnt"; api.ui.appendChild(CNT);
    function live(withMe){ const d=R.d||{}, t=now(), L=[]; Object.keys(d.p||{}).forEach(k=>{ const p=d.p[k]; if(!p) return; if(k!==code && t-(p.t||0)>10000) return; if(!withMe && k===code) return; L.push(Object.assign({}, p, {k})); }); if(withMe && !L.some(p=>p.k===code)) L.push({k:code, n:nm}); return L.sort((a,b)=>a.k<b.k?-1:1); }
    function ui(){ if(R.phase!=="room" && R.phase!=="wait"){ P.style.display="none"; return; } P.style.display="";
      if(R.phase==="room"){ P.innerHTML='<h4>👫 '+cfg.title+' <small style="font-size:13px;opacity:.8">(최대 '+MAX+'명)</small></h4><div class="sub">친구 방에 들어가거나, 내 방을 만들어요</div><div class="rl">'+(R.rooms.length?R.rooms.map(r=>'<button data-j="'+r.id+'">'+cfg.ic+' '+esc2(r.n)+'의 방 · '+(cfg.tag?cfg.tag(r.h)+' · ':'')+r.c+'/'+MAX+'명</button>').join(""):'<div class="sub">아직 열린 방이 없어요</div>')+'</div><button class="go" data-mk="1">＋ 내 방 만들기</button>'+(cfg.back?'<button class="gr" data-bk="1">← 뒤로</button>':''); }
      else { const h=(R.d&&R.d.h)||{}, ps=live(true); P.innerHTML='<h4>'+cfg.ic+' '+esc2(h.n||"")+'의 방</h4><div class="pl">'+ps.map(p=>'<span class="'+(p.k===code?"me":"")+'">'+(p.k===h.c?"👑 ":"")+esc2(p.n)+'</span>').join("")+(cfg.fill?Array.from({length:Math.max(0,MAX-ps.length)},()=>'<span class="bt">🤖 봇</span>').join(""):'')+'</div><div class="sub">'+(cfg.tag?cfg.tag(h)+' · ':'')+ps.length+' / '+MAX+'명'+(cfg.fill?' · 빈자리는 봇이 채워요':'')+'</div>'+
        (h.st?'<div class="sub">곧 시작해요!</div>':R.host?'<button class="go" data-st="1">▶ 게임 시작 (10초 뒤)</button>':'<div class="sub">방장(👑)이 「게임 시작」을 누르면 10초 뒤 시작해요</div>')+'<button class="gr" data-lv="1">방 나가기</button>'; } }
    P.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b || R.busy) return; if(b.dataset.mk) R.make(); else if(b.dataset.j) R.join(b.dataset.j); else if(b.dataset.st) R.start(); else if(b.dataset.lv) R.leave(true); else if(b.dataset.bk && cfg.back) cfg.back(); });
    R.list=async()=>{ if(!OK) return; let d=null; try{ d=await NET.get(BASE()); }catch(e){ return; } const t=now(), L=[];
      Object.keys(d||{}).forEach(id=>{ const r=d[id]; if(!r || !r.h || r.h.st) return; if(t-(r.h.hb||0)>15000) return; const c=Object.values(r.p||{}).filter(p=>p && t-(p.t||0)<10000).length; if(c<MAX) L.push({id, n:r.h.n||"친구", c, h:r.h}); });
      R.rooms=L.sort((a,b)=>b.c-a.c).slice(0,6); if(R.phase==="room") ui(); };
    R.make=async()=>{ if(!OK){ api.msg("서버에 연결이 안 돼요", 1500); return; } R.busy=true; const id=code+"_"+(Date.now()%100000); R.id=id; R.path=BASE()+"/"+id; R.host=true;
      const h=Object.assign({c:code, n:nm, st:0, hb:now(), at:now()}, (typeof cfg.h==="function"?cfg.h():cfg.h)||{}); const me=Object.assign({n:nm, t:now()}, R.node?R.node():{}); try{ await NET.put(R.path, {h, p:{[code]:me}}); }catch(e){} R.d={h, p:{[code]:me}}; R.phase="wait"; R.busy=false; ui(); };
    R.join=async(id)=>{ R.busy=true; const path=BASE()+"/"+id; let d=null; try{ d=await NET.get(path); }catch(e){} const t=now(), c=d && d.p ? Object.values(d.p).filter(p=>p && t-(p.t||0)<10000).length : 0;
      if(!d || !d.h || d.h.st || c>=MAX){ R.busy=false; api.msg(d && d.h && d.h.st?"이미 시작한 방이에요":"방이 꽉 찼어요 (최대 "+MAX+"명)", 1500); R.list(); return; }
      R.id=id; R.path=path; R.host=false; R.d=d; try{ await NET.put(path+"/p/"+code, Object.assign({n:nm, t:now()}, R.node?R.node():{})); }catch(e){} R.phase="wait"; R.busy=false; ui(); };
    R.start=async()=>{ if(!R.host || !R.path) return; const at=now()+WAITMS, seed=(Math.random()*4294967296)>>>0; try{ await NET.patch(R.path+"/h", {st:at, seed}); }catch(e){} R.d.h=Object.assign({}, R.d.h, {st:at, seed}); ui(); };
    R.leave=(toList)=>{ if(R.path && OK){ NET.del(R.path+"/p/"+code).catch(()=>{}); if(R.host && R.phase==="wait") NET.del(R.path).catch(()=>{}); } R.id=R.path=null; R.d=null; R.host=false; if(toList){ R.phase="room"; R.list(); ui(); } };
    R.live=live; R.now=now;
    R.authority=()=>{ const h=(R.d&&R.d.h)||{}, L=live(true).map(p=>p.k); return L.indexOf(h.c)>=0 ? h.c===code : L[0]===code; };
    R.ev=(to, o)=>{ if(!R.path || !OK) return; const id=Date.now().toString(36)+Math.floor(Math.random()*1e4).toString(36); NET.put(R.path+"/e/"+to+"/"+id, Object.assign({at:now()}, o)).catch(()=>{}); };
    R.feed=(o)=>{ if(!R.path || !OK) return; const id=Date.now().toString(36)+Math.floor(Math.random()*1e4).toString(36); R.seenF[id]=1; NET.put(R.path+"/fd/"+id, o).catch(()=>{}); };
    R.put=(sub, v)=>{ if(R.path && OK) NET.put(R.path+"/"+sub, v).catch(()=>{}); };
    async function poll(){ if(!R.path || R.busy) return; let d=null; try{ d=await NET.get(R.path); }catch(e){ return; } if(!R.path) return;
      if(!d || !d.h){ if(R.phase==="wait"){ api.msg("방이 닫혔어요", 1400); R.leave(true); } return; } R.d=d;
      const my=(d.e||{})[code]||{}; Object.keys(my).forEach(id=>{ if(R.seenE[id]) return; R.seenE[id]=1; NET.del(R.path+"/e/"+code+"/"+id).catch(()=>{}); try{ R.onEv && R.onEv(my[id]); }catch(e){ console.warn(e); } });
      Object.keys(d.fd||{}).forEach(id=>{ if(R.seenF[id]) return; R.seenF[id]=1; try{ R.onFeed && R.onFeed(d.fd[id]); }catch(e){} });
      if(R.phase==="wait"){ if(d.h.st) R.phase="count"; ui(); } }
    R.tick=(dt)=>{ if(!OK) return;
      if(R.phase==="room"){ R.listT-=dt; if(R.listT<=0){ R.listT=1.5; R.list(); } return; }
      if(!R.path) return;
      R.sendT-=dt; if(R.sendT<=0){ R.sendT=cfg.send||.1; const m=Object.assign({n:nm, t:now()}, R.node?R.node():{}); const s0=R.last; if(!s0 || JSON.stringify(Object.assign({},s0,{t:0}))!==JSON.stringify(Object.assign({},m,{t:0})) || m.t-s0.t>1500){ R.last=m; NET.put(R.path+"/p/"+code, m).catch(()=>{}); } }
      R.pollT-=dt; if(R.pollT<=0){ R.pollT=cfg.poll||.25; poll(); }
      if(R.host && R.phase==="wait"){ R.hbT-=dt; if(R.hbT<=0){ R.hbT=3; NET.put(R.path+"/h/hb", now()).catch(()=>{}); } }
      if(R.phase==="count"){ const left=((R.d.h.st||0)-now())/1000; CNT.textContent=left>0?Math.ceil(left):""; if(left<=3 && left>0 && Math.ceil(left)!==R.lc){ R.lc=Math.ceil(left); try{ api.sfx.tick(); }catch(e){} }
        if(left<=0){ CNT.textContent=""; R.phase="play"; try{ R.onStart && R.onStart(R.d.h, live(true)); }catch(e){ console.warn(e); } } } };
    R.dispose=()=>{ R.leave(false); try{ P.remove(); CNT.remove(); }catch(e){} };
    R.list(); ui(); return R; }

  return {reg, GM, ORDER, draw, room, build, labels, lobby, enter, exit, step, result, rec, payLeft, SFX, I, SPOT, GATES, get on(){ return S.on; }, get run(){ return S.run; }, get k(){ return S.k; }, msg, DAY_PAY};
})();
window.MG=MG;
