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
  const SFX=(()=>{ let ac=null, mute=false; const ctx=()=>{ if(mute) return null; if(!ac){ try{ ac=new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} } if(ac && ac.state==="suspended"){ try{ ac.resume(); }catch(e){} } return ac; };
    function tone(f, d, type, vol, f2, at){ const a=ctx(); if(!a) return; try{ const o=a.createOscillator(), g=a.createGain(), t=a.currentTime+(at||0); o.type=type||"sine"; o.frequency.setValueAtTime(f,t); if(f2) o.frequency.exponentialRampToValueAtTime(f2,t+d); g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(vol||.05,t+.008); g.gain.exponentialRampToValueAtTime(0.0001,t+d); o.connect(g); g.connect(a.destination); o.start(t); o.stop(t+d+.02); }catch(e){} }
    const nb={};
    function noise(d, vol, fr, q, f2){ const a=ctx(); if(!a) return; try{ const key=Math.round(d*100); let b=nb[key]; if(!b){ const n=Math.floor(a.sampleRate*d); b=a.createBuffer(1,n,a.sampleRate); const c=b.getChannelData(0); for(let i=0;i<n;i++) c[i]=(Math.random()*2-1)*Math.pow(1-i/n,1.6); nb[key]=b; }
        const s=a.createBufferSource(); s.buffer=b; const f=a.createBiquadFilter(); f.type="bandpass"; const t=a.currentTime; f.frequency.setValueAtTime(fr||1200,t); if(f2) f.frequency.exponentialRampToValueAtTime(f2,t+d); f.Q.value=q||.8; const g=a.createGain(); g.gain.value=vol||.08; s.connect(f); f.connect(g); g.connect(a.destination); s.start(); }catch(e){} }
    let lastShot=0;
    return { ctx, set mute(v){ mute=!!v; }, get mute(){ return mute; }, tone, noise,
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
    e.preventDefault();
    if(e.pointerType==="mouse"){ I.mouse=true; if(bt){ btnSet(bt.dataset.b,1); PT.set(e.pointerId,{r:"b", b:bt.dataset.b, x, y}); return; }
      if(cfg && cfg.look){ if(I.lock){ if(e.button===0) btnSet("fire",1); else if(e.button===2) btnSet("slide",1); return; }
        try{ const p=ROOT.requestPointerLock && ROOT.requestPointerLock(); if(p && p.catch) p.catch(()=>{}); }catch(_){} PT.set(e.pointerId,{r:"look", x, y}); return; }
      PT.set(e.pointerId,{r:"look", x, y}); return; }
    I.touch=true;
    if(bt){ const b=bt.dataset.b; btnSet(b,1); PT.set(e.pointerId,{r:"b", b, x, y, look:b==="fire" && cfg && cfg.look}); return; }
    const look=!!(cfg && cfg.look);
    if(!look || x<innerWidth*0.45){ if([...PT.values()].some(q=>q.r==="joy")) return; PT.set(e.pointerId,{r:"joy", ox:x, oy:y}); joyEl.style.left=x+"px"; joyEl.style.top=y+"px"; joyEl.classList.add("on"); ROOT.classList.add("joyOn"); joyMove(0,0); return; }
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
        S.api={I, ui:ROOT, hud:ROOT.querySelector(".mgHud"), topR:ROOT.querySelector(".mgTopR"), msg, sfx:SFX, nick:nick(), av:(typeof av!=="undefined"?Object.assign({},av):{}), opt:opt||{}, renderer, end:(r)=>result(k, r), low:typeof LOW!=="undefined" && LOW};
        S.run=def.start(S.api); S.last=performance.now(); cancelAnimationFrame(S.raf); S.raf=requestAnimationFrame(frame);
      }catch(e){ console.warn("MG", e); S.on=false; document.body.classList.remove("mgOn"); }
      S.busy=false; if(fd) setTimeout(()=>fd.classList.remove("on"), 60); }, 240);
    return true; }
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
      '<div><button class="out">🏝 섬으로</button><button class="go">🔁 한 판 더</button></div></div>';
    el.classList.add("on"); try{ SFX.win(); }catch(e){}
    el.querySelector(".out").onclick=()=>{ el.classList.remove("on"); exit(); };
    el.querySelector(".go").onclick=()=>{ el.classList.remove("on"); const o=S.api && S.api.opt; try{ if(S.run && S.run.dispose) S.run.dispose(); }catch(e){} resetI(); mkUI(def); S.api.ui=ROOT; S.api.hud=ROOT.querySelector(".mgHud"); S.api.topR=ROOT.querySelector(".mgTopR"); S.run=def.start(S.api); };
    return got; }

  /* ── 입구 안내 창 (게임 고르기 전) ── */
  function lobby(k){ const def=GM[k]; if(!def) return; css(); let el=$$("mgLob"); if(!el){ el=document.createElement("div"); el.id="mgLob"; document.body.appendChild(el); }
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
  const GATES=[{k:"arena", at:[46.5,11.5], face:Math.PI*.12}, {k:"grid", at:[65.5,11.5], face:-Math.PI*.12}];
  function build(ctx){ const {G, OX, OZ, busy, cols, vcMerge}=ctx; if(!vcMerge) return; const L=[], GL=[];
    const add=(geo, col, x, y, z, o)=>{ o=o||{}; const m=new THREE.Matrix4(), q=new THREE.Quaternion().setFromEuler(new THREE.Euler(o.rx||0, o.ry||0, o.rz||0)); m.compose(new THREE.Vector3(x,y,z), q, new THREE.Vector3(o.sx||1,o.sy||1,o.sz||1)); (o.glow?GL:L).push({g:geo, col, m}); };
    const BX=(w,h,d)=>new THREE.BoxGeometry(w,h,d), CY=(a,b,h,n)=>new THREE.CylinderGeometry(a,b,h,n||20), SP=(r)=>new THREE.SphereGeometry(r,18,12);
    GATES.forEach(g=>{ const [gx,gz]=g.at, X=gx+OX, Z=gz+OZ, f=g.face, c=Math.cos(f), s=Math.sin(f), P=(u,y,v,geo,col,o)=>{ o=Object.assign({},o||{}); o.ry=(o.ry||0)+f; add(geo,col, X+u*c+v*s, y, Z-u*s+v*c, o); };
      busy.push([gx,gz,4.2]); cols.push([X,Z,2.3]);
      ctx.disc && ctx.disc(gx,gz,3.3,g.k==="arena"?0xbfe6ff:0xd6d0ff,1);
      if(g.k==="arena"){   /* 💦 물총 아레나 — 둥근 경기장 · 줄무늬 · 문 · 꼭대기 큰 물방울 · 옆에 큰 물총 */
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

  return {reg, GM, ORDER, draw, build, labels, lobby, enter, exit, step, result, rec, payLeft, SFX, I, SPOT, GATES, get on(){ return S.on; }, get run(){ return S.run; }, get k(){ return S.k; }, msg, DAY_PAY};
})();
window.MG=MG;
