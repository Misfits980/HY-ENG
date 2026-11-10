/* ═════════ 🍉 과일 합치기 — 🎡 놀이 섬 과일 가게
   (v636) 사용자: 「2번은 그 게임 안에 랭킹 이번 주 · 이번 달 · 전체 랭킹 이런 식으로 나와야 해 — 형광판 같은 느낌으로」
   · 위에서 과일을 떨어뜨리면 같은 과일끼리 닿아 다음 과일로 합쳐짐 (체리 → … → 수박 11단계 · 수박 둘이면 펑! 큰 점수)
   · 합쳐질 때 과일 영어 이름이 뿅 (처음 만든 과일은 소리로도) — 그림 = 우리가 그린 웃는 과일 (캔버스)
   · 선 위로 과일이 2.5초 넘게 있으면 끝
   · 📟 형광판(LED) 랭킹: 이번 주 · 이번 달 · 전체 (탭 · 저절로 돌아감) — 시작 화면과 게임 중 둘 다
     서버 /hy/day/frW<해><주>/<코드> · /hy/day/frM<해월>/<코드> · /hy/day/frA/<코드> = {n, s, at} (내 기록이 오를 때만 씀)
   · 상: MG 공통 하루 3판 🪙 (점수 300 / 800 / 1500 넘으면 5 / 7 / 9 · 그 밑 3)
   시험 손잡이: MG.run.B(과일) · .score · .over · .aim(x) · .drop() · .bot · .fast · .board · .tab(k) · .phase · .ready · .lb */
(function(){
"use strict";
if(!window.MG) return;
const FR=[ /* 이름 · 뜻 · 반지름(상자 600 기준) · 색 · 진한 색 */
  ["cherry","체리",22,"#e8344e","#a8132e"],["strawberry","딸기",30,"#ff4d5e","#c62238"],["grape","포도",40,"#9466ee","#5d34b0"],["lemon","레몬",50,"#ffd84a","#d9a90f"],["orange","오렌지",61,"#ff9a3d","#d8641a"],
  ["apple","사과",74,"#f2453d","#b31f1a"],["pear","배",88,"#cfe063","#93a52a"],["peach","복숭아",102,"#ffb19a","#e57a69"],["pineapple","파인애플",118,"#f6c63b","#c48d12"],["melon","멜론",136,"#b8e27c","#6fae3a"],["watermelon","수박",158,"#38b25a","#1d6e35"]];
const EMO=["🍒","🍓","🍇","🍋","🍊","🍎","🍐","🍑","🍍","🍈","🍉"];
const PTS=[1,3,6,10,15,21,28,36,45,55,66], BW=600, BH=820, LINE=128, HOLD_Y=80, GRAV=1500;
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const st=(k,v)=>{ try{ return typeof store==="function" ? store(k,v) : (v===undefined?JSON.parse(localStorage.getItem(k)||"null"):localStorage.setItem(k,JSON.stringify(v))); }catch(e){ return null; } };
const sayW=w=>{ try{ say(w); }catch(e){} };
/* 한국 날짜 → 주 · 달 열쇠 */
function keys(ms){ const d=new Date(ms+9*3600e3), y=d.getUTCFullYear(), m=d.getUTCMonth()+1;
  const t=new Date(Date.UTC(y, d.getUTCMonth(), d.getUTCDate())), dn=(t.getUTCDay()+6)%7; t.setUTCDate(t.getUTCDate()-dn+3); const y1=new Date(Date.UTC(t.getUTCFullYear(),0,4)); const wk=1+Math.round(((t-y1)/864e5-3+((y1.getUTCDay()+6)%7))/7);
  return {W:"frW"+t.getUTCFullYear()+String(wk).padStart(2,"0"), M:"frM"+y+String(m).padStart(2,"0"), A:"frA"}; }
const TABS=[["W","이번 주"],["M","이번 달"],["A","전체"]];

/* ── 우리 과일 그림 (웃는 얼굴) ── */
function fruitArt(g, lv, R, ex){ ex=ex||"n"; const f=FR[lv], c=f[3], dk=f[4]; g.save();
  const gr=g.createRadialGradient(-R*.35,-R*.4,R*.1,0,0,R*1.05); gr.addColorStop(0,"#fff8"); gr.addColorStop(.25,c); gr.addColorStop(1,dk);
  g.beginPath(); g.arc(0,0,R,0,7); g.fillStyle=gr; g.fill();
  g.save(); g.beginPath(); g.arc(0,0,R*.98,0,7); g.clip();
  if(lv===1){ g.fillStyle="#ffe58a"; for(let i=0;i<14;i++){ const a=i*2.4, r=R*(.25+.6*((i*37)%10)/10); g.beginPath(); g.ellipse(Math.cos(a)*r,Math.sin(a)*r+R*.1,R*.05,R*.08,a,0,7); g.fill(); } }
  if(lv===2){ g.fillStyle="rgba(255,255,255,.18)"; [[-.4,-.2],[.05,-.35],[.45,-.1],[-.2,.25],[.25,.3],[-.55,.3],[.55,.35],[0,.62]].forEach(([x,y])=>{ g.beginPath(); g.arc(x*R,y*R,R*.24,0,7); g.fill(); }); }
  if(lv===3||lv===4){ g.fillStyle="rgba(255,255,255,.22)"; for(let i=0;i<22;i++){ const a=i*2.17, r=R*(.15+.75*((i*53)%11)/11); g.beginPath(); g.arc(Math.cos(a)*r,Math.sin(a)*r,R*.035,0,7); g.fill(); } }
  if(lv===6){ g.fillStyle="rgba(120,90,20,.25)"; for(let i=0;i<18;i++){ const a=i*2.3, r=R*(.2+.7*((i*29)%9)/9); g.beginPath(); g.arc(Math.cos(a)*r,Math.sin(a)*r,R*.03,0,7); g.fill(); } }
  if(lv===7){ g.strokeStyle="rgba(200,80,80,.35)"; g.lineWidth=R*.06; g.beginPath(); g.moveTo(R*.15,-R); g.quadraticCurveTo(R*.45,0,R*.1,R); g.stroke(); }
  if(lv===8){ g.strokeStyle="rgba(140,90,0,.4)"; g.lineWidth=R*.045; for(let k=-4;k<=4;k++){ g.beginPath(); g.moveTo(k*R*.4-R,-R); g.lineTo(k*R*.4+R,R); g.stroke(); g.beginPath(); g.moveTo(k*R*.4+R,-R); g.lineTo(k*R*.4-R,R); g.stroke(); } }
  if(lv===9){ g.strokeStyle="rgba(255,255,240,.55)"; g.lineWidth=R*.028; for(let i=0;i<16;i++){ g.beginPath(); const a=i*.9; g.arc(Math.cos(a)*R*.7,Math.sin(a)*R*.7,R*.55,a,a+1.6); g.stroke(); } }
  if(lv===10){ g.fillStyle="#1d6e35"; for(let k=-3;k<=3;k++){ g.beginPath(); g.moveTo(k*R*.34,-R); g.bezierCurveTo(k*R*.34+R*.14,-R*.4,k*R*.34-R*.14,R*.3,k*R*.34+R*.05,R); g.lineTo(k*R*.34+R*.14,R); g.bezierCurveTo(k*R*.34-R*.03,R*.3,k*R*.34+R*.25,-R*.4,k*R*.34+R*.09,-R); g.fill(); } }
  g.restore();
  /* 꼭지 · 잎 */
  if(lv===1||lv===8){ g.fillStyle=lv===1?"#3fc46a":"#4caf50"; const n=lv===1?5:7, w=lv===1?.22:.18; for(let i=0;i<n;i++){ const a=-Math.PI/2+(i-(n-1)/2)*.32; g.beginPath(); g.moveTo(Math.cos(a)*R*.85,Math.sin(a)*R*.85); g.lineTo(Math.cos(a-w)*R*.7,Math.sin(a-w)*R*.7); g.lineTo(Math.cos(a)*R*(lv===8?1.35:1.08),Math.sin(a)*R*(lv===8?1.35:1.08)); g.closePath(); g.fill(); } }
  else { g.strokeStyle="#7a4f2a"; g.lineWidth=Math.max(2,R*.07); g.lineCap="round"; g.beginPath(); g.moveTo(0,-R*.82); g.quadraticCurveTo(R*.05,-R*1.05,R*(lv===0?.25:.1),-R*1.18); g.stroke();
    if(lv!==2 && lv!==10){ g.fillStyle="#4cc36a"; g.beginPath(); g.ellipse(R*.28,-R*1.02,R*.24,R*.11,-.5,0,7); g.fill(); } }
  /* 얼굴 */
  const ey=-R*.02, exx=R*.3, er=Math.max(2.2,R*.1);
  g.strokeStyle=g.fillStyle="#2b1d2a"; g.lineWidth=Math.max(1.6,R*.055); g.lineCap="round";
  if(ex==="s"){ [-1,1].forEach(s=>{ g.beginPath(); g.moveTo(s*exx-er*s,ey-er*.8); g.lineTo(s*exx+er*.6*s,ey); g.lineTo(s*exx-er*s,ey+er*.8); g.stroke(); }); g.beginPath(); for(let i=0;i<=4;i++) g.lineTo(-R*.14+i*R*.07, R*.2+(i%2?-1:1)*R*.03); g.stroke(); }
  else if(ex==="w"){ [-1,1].forEach(s=>{ g.beginPath(); g.arc(s*exx,ey,er*1.15,0,7); g.fill(); }); g.fillStyle="#fff"; [-1,1].forEach(s=>{ g.beginPath(); g.arc(s*exx-er*.35,ey-er*.4,er*.45,0,7); g.fill(); }); g.fillStyle="#2b1d2a"; g.beginPath(); g.ellipse(0,R*.24,R*.09,R*.12,0,0,7); g.fill(); }
  else { [-1,1].forEach(s=>{ g.beginPath(); g.ellipse(s*exx,ey,er*.85,er,0,0,7); g.fill(); }); g.fillStyle="#fff"; [-1,1].forEach(s=>{ g.beginPath(); g.arc(s*exx-er*.3,ey-er*.38,er*.36,0,7); g.fill(); }); g.beginPath(); g.arc(0,R*.14,R*.16,.15*Math.PI,.85*Math.PI); g.stroke(); }
  g.fillStyle="rgba(255,110,140,.45)"; [-1,1].forEach(s=>{ g.beginPath(); g.ellipse(s*R*.52,R*.2,R*.13,R*.08,0,0,7); g.fill(); });
  g.restore(); }

function css(){ if(document.getElementById("frCss")) return; const s=document.createElement("style"); s.id="frCss"; s.textContent=`
#mgUI .frR{position:absolute;inset:0;isolation:isolate;display:flex;flex-direction:column;align-items:center;gap:8px;pointer-events:auto;font-family:var(--kr);color:#24314a;
  padding:calc(56px + env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) calc(10px + env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));
  background:repeating-linear-gradient(90deg,rgba(176,122,80,.10) 0 46px,rgba(176,122,80,0) 46px 92px),linear-gradient(#fff3d6,#ffd9a8)}
#mgUI .frR::before{content:"";position:absolute;left:0;right:0;top:0;height:calc(44px + env(safe-area-inset-top));background:radial-gradient(circle at 23px 100%,transparent 0 15px,#fff3d6 16px) 0 100%/46px 16px repeat-x,repeating-linear-gradient(90deg,#ff4d5e 0 23px,#fff 23px 46px);pointer-events:none;z-index:5}
#mgUI .frR::after{content:"";position:absolute;left:0;right:0;bottom:0;height:calc(26px + env(safe-area-inset-bottom));background:repeating-linear-gradient(90deg,#b07a50 0 70px,#9c6842 70px 72px),#b07a50;box-shadow:0 -4px 0 #8a5a3c;pointer-events:none;z-index:0}
#mgUI .frR > *{position:relative;z-index:1}
#mgUI .frEvo{width:min(100%,560px);height:38px;flex:none;background:rgba(255,255,255,.7);border-radius:14px;box-shadow:0 3px 0 rgba(176,122,80,.35)}
#mgUI .frLed::before{content:"";position:absolute;inset:-9px;border-radius:20px;padding:6px;background:radial-gradient(circle,#ffe14d 0 2.6px,rgba(255,225,77,.25) 3.4px,transparent 4px) 0 0/14px 14px,#3b2a6a;-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:frBulb .8s steps(2) infinite;pointer-events:none}
@keyframes frBulb{50%{background-position:7px 0,0 0}}
#mgUI .frLed{position:relative;margin:6px 0}
#mgUI .frR *{box-sizing:border-box}
#mgUI .puM .ch{display:grid;grid-template-columns:repeat(6,1fr);gap:2px 2px;margin:0 auto 6px;max-width:360px} #mgUI .puM .ch span{display:flex;flex-direction:column;align-items:center;font-size:8.5px;letter-spacing:-.2px;font-family:var(--en);font-weight:800;min-width:0;white-space:nowrap;opacity:.9} #mgUI .puM .ch span i{font-style:normal;font-size:22px} #mgUI .puM .frLed{margin:4px auto 0}
@media (max-height:760px){ #mgUI .puM .ch{display:none} }
#mgUI .frLed{width:min(100%,560px);flex:none;background-color:#06090f;background-image:radial-gradient(rgba(120,255,190,.07) 1px,transparent 1.5px);background-size:4px 4px;border:3px solid #232a3f;border-radius:14px;
  box-shadow:inset 0 0 22px rgba(61,255,154,.12),0 0 0 2px #000,0 6px 18px rgba(0,0,0,.25);padding:6px 10px 8px;color:#3dff9a;font-family:"Courier New",ui-monospace,monospace;font-weight:700;text-shadow:0 0 3px #3dff9a,0 0 10px rgba(61,255,154,.55)}
#mgUI .frLed .mq{white-space:nowrap;overflow:hidden;font-size:13px;color:#ffe14d;text-shadow:0 0 4px #ffe14d,0 0 10px rgba(255,225,77,.6);border-bottom:1px dashed rgba(61,255,154,.3);padding-bottom:3px;margin-bottom:4px}
#mgUI .frLed .mq span{display:inline-block;padding-left:100%;animation:frMq 14s linear infinite}
@keyframes frMq{to{transform:translateX(-100%)}}
#mgUI .frLed .tb{display:flex;gap:6px;margin-bottom:4px}
#mgUI .frLed .tb button{font:inherit;flex:1;border:1.5px solid rgba(61,255,154,.35);background:transparent;color:rgba(61,255,154,.55);border-radius:8px;padding:4px 0;font-size:14px;text-shadow:none;min-height:34px}
#mgUI .frLed .tb button.on{color:#ff5ce1;border-color:#ff5ce1;text-shadow:0 0 4px #ff5ce1,0 0 12px rgba(255,92,225,.7);box-shadow:0 0 10px rgba(255,92,225,.35) inset}
#mgUI .frLed .rw{display:grid;grid-template-columns:2.4em minmax(0,1fr) auto;gap:6px;font-size:15px;line-height:1.55;padding:0 4px;border-radius:6px}
#mgUI .frLed .rw .n{overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
#mgUI .frLed .rw.r1{color:#ffe14d;text-shadow:0 0 4px #ffe14d,0 0 12px rgba(255,225,77,.7)} #mgUI .frLed .rw.r2{color:#bfe6ff;text-shadow:0 0 4px #bfe6ff} #mgUI .frLed .rw.r3{color:#ffad6b;text-shadow:0 0 4px #ffad6b}
#mgUI .frLed .rw.me{background:rgba(255,92,225,.16);color:#ff8ef0;text-shadow:0 0 5px #ff5ce1;animation:frBl 1.2s steps(2) infinite}
@keyframes frBl{50%{background:rgba(255,92,225,.04)}}
#mgUI .frLed .em{font-size:14px;opacity:.75;padding:6px 4px}
#mgUI .frTop{display:flex;align-items:center;gap:8px;width:min(100%,560px);flex:none}
#mgUI .frTop b{background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;box-shadow:0 0 0 2px #fff,0 4px 0 2px rgba(74,46,31,.35);border-radius:999px;padding:3px 12px;font-weight:400;font-size:16px;white-space:nowrap} #mgUI .frTop b.sc{color:#fff;-webkit-text-stroke:5px #4A2E1F;paint-order:stroke fill;font-family:var(--en);font-weight:900;font-size:19px;background:#ff8466}
#mgUI .frTop .nx{margin-left:auto;display:flex;align-items:center;gap:5px;background:rgba(255,255,255,.75);border-radius:14px;padding:2px 10px 2px 8px;font-size:13px}
#mgUI .frTop canvas{width:34px;height:34px}
#mgUI .frBox{position:relative;flex:1;min-height:0;width:100%;display:flex;justify-content:center;align-items:flex-start}
#mgUI .frBox canvas{display:block;border-radius:18px;touch-action:none;background:linear-gradient(#fffdf6,#fff3d9);box-shadow:0 0 0 5px #b07a50,0 0 0 9px #8a5a3c,0 10px 26px rgba(0,0,0,.25)}
#mgUI .frSt{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:10px;z-index:3;padding:calc(60px + env(safe-area-inset-top)) 14px calc(14px + env(safe-area-inset-bottom));background:linear-gradient(rgba(255,243,214,.93),rgba(255,217,168,.97))}
#mgUI .frSt.on{display:flex}
#mgUI .frSt h2{margin:0;font-weight:400;font-size:34px;color:#24314a;text-shadow:0 3px 0 #fff}
#mgUI .frSt .ch{display:flex;flex-wrap:wrap;justify-content:center;gap:2px;font-size:22px;max-width:520px} #mgUI .frSt .ch span{display:flex;flex-direction:column;align-items:center;font-size:9.5px;font-family:var(--en);font-weight:900;color:#24314a;width:56px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap} #mgUI .frSt .ch span i{font-style:normal;font-size:24px}
#mgUI .frSt .go{font:inherit;border:0;border-radius:20px;padding:12px 30px;min-height:58px;background:linear-gradient(135deg,#ff8466,#ffb02e);color:#fff;font-size:22px;box-shadow:0 5px 0 #c8642e}
#mgUI .frSt .go:active{transform:translateY(4px);box-shadow:0 1px 0 #c8642e}
#mgUI .frSt .out{font:inherit;border:0;border-radius:14px;padding:9px 18px;min-height:44px;background:rgba(36,49,74,.15);color:#24314a;font-size:15px}
#mgUI .frSt .sub{font-size:14px;opacity:.85;text-align:center}
#mgUI .frSt .frLed{max-width:420px}
@media (orientation:landscape) and (max-height:620px){
  #mgUI .frR{display:grid;grid-template-columns:minmax(0,1fr) auto;grid-template-rows:auto auto 1fr;grid-template-areas:"top box" "evo box" "led box";column-gap:14px;align-items:start;padding-top:calc(50px + env(safe-area-inset-top))}
  #mgUI .frTop{grid-area:top} #mgUI .frEvo{grid-area:evo;width:100%} #mgUI .frLed{grid-area:led} #mgUI .frBox{grid-area:box;height:calc(100vh - 66px);height:calc(100dvh - 66px - env(safe-area-inset-bottom));width:calc((100vh - 78px)*600/820 + 22px);width:calc((100dvh - 78px - env(safe-area-inset-bottom))*600/820 + 22px)}
  #mgUI .frLed .rw{font-size:13px;line-height:1.4}
  #mgUI .frSt{flex-direction:row;flex-wrap:wrap;align-content:center}
}`; document.head.appendChild(s); }

function start(api){
  const SFX=api.sfx; api.menu=true; css();
  let gone=false, paused=false, fast=0, bot=false, phase="title", ready=false;
  const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  const code=(()=>{ try{ return myCode; }catch(e){ return "ME"; } })(), nick=api.nick;
  const scene=new THREE.Scene(), cam=new THREE.PerspectiveCamera(50,1,.1,10);
  const U=api.ui, R=document.createElement("div"); R.className="frR"; U.insertBefore(R, U.querySelector(".mgTop"));
  const ledHTML='<div class="frLed"><div class="mq"><span></span></div><div class="tb">'+TABS.map(([k,t])=>'<button data-t="'+k+'">'+t+'</button>').join("")+'</div><div class="rows"></div></div>';
  R.innerHTML='<div class="frTop"><b class="sc">0</b><b class="bs"></b><div class="nx">다음 <canvas width="68" height="68"></canvas></div></div>'+ledHTML+'<canvas class="frEvo" width="560" height="76"></canvas>'+'<div class="frBox"><canvas></canvas></div>'+
    '<div class="frSt"></div>';
  ["pointerdown","pointermove","pointerup"].forEach(t=>R.addEventListener(t, e=>e.stopPropagation()));
  const $=s=>R.querySelector(s), cv=$(".frBox canvas"), g=cv.getContext("2d"), NX=$(".nx canvas"), nxg=NX.getContext("2d"), STP=$(".frSt");
  const REC=()=>Object.assign({best:0, top:0, n:0}, st("hyeng_proto_frr")||{});
  const EV=R.querySelector(".frEvo"), evg=EV.getContext("2d");
  function evoPaint(){ if(!ART.length) return; const w=EV.width, h=EV.height, n=FR.length, sp=w/n, mx=Math.max((()=>{ try{ return maxLv; }catch(e){ return 0; } })(), 0), best=REC().top|0; evg.clearRect(0,0,w,h);
    for(let i=0;i<n;i++){ const A=ART[i], x=sp*i+sp/2, y=h/2, R0=FR[i][2]*SC, sz=Math.min(sp*.8, 18+i*2.6), k=sz/(R0*2); const got=i<=Math.max(mx,4)||i<=best;
      if(i===mx && mx>0){ evg.fillStyle="rgba(255,225,77,.6)"; evg.beginPath(); evg.arc(x,y,sz/2+6,0,7); evg.fill(); }
      evg.save(); evg.globalAlpha=got?1:.28; evg.translate(x,y); evg.scale(k,k); evg.drawImage(A.c,-A.h,-A.h); evg.restore();
      if(i<n-1){ evg.fillStyle="rgba(176,122,80,.7)"; evg.beginPath(); evg.moveTo(x+sp/2-3,y-4); evg.lineTo(x+sp/2+3,y); evg.lineTo(x+sp/2-3,y+4); evg.fill(); } } }
  /* ── 과일 그림 미리 (크기별) ── */
  let SC=1; const ART=[];
  function bake(){ for(let lv=0;lv<FR.length;lv++){ const r=FR[lv][2]*SC, sz=Math.ceil(r*2.8), mk=ex=>{ const c=document.createElement("canvas"); c.width=c.height=sz; const q=c.getContext("2d"); q.translate(sz/2,sz/2); fruitArt(q, lv, r, ex); return c; }; ART[lv]={c:mk("n"), s:mk("s"), w:mk("w"), h:sz/2}; } evoPaint(); }
  function fit(){ const bx=cv.parentNode.getBoundingClientRect(); if(bx.width>10 && bx.height>10){ const w=Math.floor(Math.min(bx.width-20, (bx.height-12)*BW/BH)), h=Math.floor(w*BH/BW); if(cv.style.width!==w+'px'){ cv.style.width=w+'px'; cv.style.height=h+'px'; } } const r=cv.getBoundingClientRect(); const dpr=Math.min(2, window.devicePixelRatio||1); const s=Math.max(.3, Math.min(2.4, (r.width||300)*dpr/BW)); if(Math.abs(s-SC)>.01 || !ART.length){ SC=s; cv.width=Math.round(BW*SC); cv.height=Math.round(BH*SC); bake(); } }
  /* ══ 📟 형광판 랭킹 ══ */
  const LB={W:null, M:null, A:null}; let tabK="W", tabT=0, tabHold=0, lbErr=false, K=keys(now()), newRec={};
  async function lbLoad(){ K=keys(now()); try{ await Promise.all(TABS.map(async([k])=>{ const v=await NET.get("/hy/day/"+K[k]); LB[k]=v||{}; })); lbErr=false; }catch(e){ lbErr=true; TABS.forEach(([k])=>{ if(!LB[k]) LB[k]={}; }); } ledPaint(); }
  function rows(k){ const o=LB[k]||{}; return Object.keys(o).map(c=>Object.assign({c}, o[c]||{})).filter(x=>x.s>0).sort((a,b)=>b.s-a.s || (a.at||0)-(b.at||0)); }
  function ledPaint(){ U.querySelectorAll(".frLed").forEach(L=>{ const big=L.closest(".puM") || innerHeight>900 || (innerWidth>innerHeight && innerHeight<=620), n=big?8:4;
    L.querySelectorAll(".tb button").forEach(b=>b.classList.toggle("on", b.dataset.t===tabK));
    const rs=rows(tabK), me=rs.findIndex(x=>x.c===code); let show=rs.slice(0,n); if(me>=n) show=show.slice(0,n-1).concat([rs[me]]);
    L.querySelector(".rows").innerHTML=LB[tabK]==null?'<div class="em">불러오는 중…</div>':!rs.length?'<div class="em">'+(lbErr?'서버에 연결이 안 돼요 — 내 기록만 남아요':'아직 기록이 없어요 — 1등 해 봐요!')+'</div>':
      show.map(x=>{ const r=rs.indexOf(x)+1; return '<div class="rw r'+r+(x.c===code?" me":"")+'"><span>'+(r<=3?["🥇","🥈","🥉"][r-1]:r+".")+'</span><span class="n">'+esc(String(x.n||"친구").slice(0,8))+(newRec[tabK]&&x.c===code?" NEW!":"")+'</span><span>'+(x.s|0).toLocaleString()+'</span></div>'; }).join("");
    const top=TABS.map(([k,t])=>{ const r0=rows(k)[0]; return r0?"★ "+t+" 1등 "+String(r0.n||"").slice(0,8)+" "+(r0.s|0).toLocaleString()+"점":null; }).filter(Boolean);
    const mq=L.querySelector(".mq span"), tx=(top.length?top.join("   "):"★ 과일 합치기 랭킹 ★ 같은 과일을 합쳐서 수박을 만들어요!")+"   ★"; if(mq.textContent!==tx) mq.textContent=tx; }); }
  U.addEventListener("click", e=>{ const b=e.target.closest(".frLed .tb button"); if(!b) return; tabK=b.dataset.t; tabHold=12; tabT=0; ledPaint(); try{ SFX.tone(990,.05,"square",.02); }catch(_){} });
  async function lbSave(score){ K=keys(now()); newRec={}; const rec={n:String(nick||"친구").slice(0,8), s:score|0, at:now()};
    await Promise.all(TABS.map(async([k])=>{ const o=LB[k]=LB[k]||{}, mine=o[code]; if(!mine || (mine.s|0)<score){ o[code]=rec; newRec[k]=1; try{ await NET.put("/hy/day/"+K[k]+"/"+code, rec); }catch(e){} } }));
    ledPaint(); return newRec; }
  /* ══ 시작 화면 ══ */
  function title(){ phase="title"; const r=REC();
    PUI.menu(U, {title:"과일 합치기", sub:"같은 과일끼리 닿으면 쑥! 수박까지 만들어요", av:api.av, nick:api.nick, stats:[["trophy",(r.best|0).toLocaleString(),"내 최고"],[EMO[r.top|0],FR[r.top|0][1],"가장 큰 과일"]],
      deco:[["🍒","left:calc(50% - 128px);top:20%;transform:rotate(-14deg)"],["🍉","left:calc(50% + 72px);top:56%;font-size:36px"]],
      more:'<div class="puExtra"><div class="ch">'+FR.map((f,i)=>'<span><i>'+EMO[i]+'</i>'+f[0]+'</span>').join("")+'</div>'+ledHTML+'</div>', primary:{k:"go", label:"시작!", ic:"play"}, pay:MG.payLeft("fruit"), onPick:()=>{ try{ SFX.up(); }catch(e){} begin(); }});
    ledPaint(); }
  /* ══ 게임 ══ */
  let RG=[], combo=0, lastM=-9, gt=0, B=[], P=[], TX=[], score=0, aimX=BW/2, held=0, next=0, cool=0, danger=0, over=false, idn=0, made={}, maxLv=0, drops=0, merges=0, acc=0, holdOn=false, shake=0;
  const rnd=()=>{ const r=Math.random()*100; return r<30?0:r<55?1:r<75?2:r<90?3:4; };
  function begin(){ PUI.menuHide(U); phase="ready"; B=[]; P=[]; TX=[]; RG=[]; combo=0; lastM=-9; gt=0; score=0; over=false; danger=0; made={}; maxLv=0; drops=0; merges=0; cool=.2; held=rnd(); next=rnd(); aimX=BW/2; fit(); nxPaint(); top(); evoPaint(); PUI.count(U, ()=>{ if(phase==="ready") phase="play"; }, fast); }
  function nxPaint(){ nxg.clearRect(0,0,68,68); const a=ART[next]; if(!a) return; const s=Math.min(1, 26/(FR[next][2]*SC)); nxg.save(); nxg.translate(34,36); nxg.scale(s,s); nxg.drawImage(a.c,-a.h,-a.h); nxg.restore(); }
  function top(){ $(".frTop .sc").textContent=score.toLocaleString(); $(".frTop .bs").textContent="🏆 "+Math.max(REC().best|0, score).toLocaleString(); }
  function drop(){ if(phase!=="play" || over || cool>0) return; const r=FR[held][2]; const x=Math.max(r, Math.min(BW-r, aimX)); B.push({id:++idn, x, y:HOLD_Y, vx:(Math.random()-.5)*4, vy:60, r, lv:held, a:0, age:0, sc:1});
    drops++; held=next; next=rnd(); cool=fast?.3:.55; nxPaint(); try{ SFX.tone(520,.07,"sine",.04,300); }catch(e){} }
  function merge(a, b){ a.dead=b.dead=true; const lv=a.lv, mx=(a.x*a.r*a.r+b.x*b.r*b.r)/(a.r*a.r+b.r*b.r), my=(a.y*a.r*a.r+b.y*b.r*b.r)/(a.r*a.r+b.r*b.r); merges++;
    if(lv>=FR.length-1){ score+=PTS[lv]*4+100; burst(mx,my,lv,40); text(mx,my,"🍉🍉 펑! +"+(PTS[lv]*4+100),"#ff5ce1"); shake=.5; try{ SFX.win(); }catch(e){} return; }
    const n=lv+1, r=FR[n][2]; B.push({id:++idn, x:Math.max(r,Math.min(BW-r,mx)), y:Math.min(BH-r,my), vx:(a.vx+b.vx)/2, vy:Math.min(0,(a.vy+b.vy)/2)-60, r, lv:n, a:0, age:2, sc:.55}); score+=PTS[n];
    burst(mx,my,n,10+n*2); const nmT=FR[n][0]+"!"; RG.push({x:mx,y:my,r:r*.6,t:.45,c:FR[n][3]}); const nm=n>maxLv; maxLv=Math.max(maxLv,n); if(nm) evoPaint();
    combo=gt-lastM<1.1?combo+1:1; lastM=gt; if(combo<2) text(mx,my-r*.4,nmT,"#fff"); if(combo>=2){ const cb=combo*3; score+=cb; text(mx,my-r*.4,nmT+" 콤보 x"+combo+" +"+cb,"#ffe14d"); try{ SFX.tone(700+combo*90,.1,"square",.03); }catch(e){} }
    if(!made[n]){ made[n]=1; if(n>=4) sayW(FR[n][0]); } try{ SFX.tone(440*Math.pow(1.122,n),.14,"triangle",.05,0); SFX.tone(660*Math.pow(1.122,n),.12,"sine",.03,0,.05); }catch(e){} if(n>=8) shake=.25; top(); }
  function burst(x,y,lv,n){ for(let i=0;i<n;i++){ const a=Math.random()*7, s=120+Math.random()*320; P.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s-120,t:.6+Math.random()*.4,c:i%3?FR[lv][3]:"#fff",r:3+Math.random()*5}); } }
  function text(x,y,t,c){ x=Math.max(110,Math.min(BW-110,x)); let cy=y; for(const o of TX.filter(o=>Math.abs(o.x-x)<200).sort((a,b)=>b.y-a.y)){ if(o.y>cy-40){ o.y=cy-40; o.tt=Math.min(o.tt,.6); } cy=o.y; } TX.push({x:Math.max(110,Math.min(BW-110,x)),y,t,c,tt:1.1}); }
  function phys(h){ const L=B;
    for(const b of L){ b.vy+=GRAV*h; b.vx*=1-.6*h; const sp=Math.hypot(b.vx,b.vy); if(sp>1400){ b.vx*=1400/sp; b.vy*=1400/sp; } if(b.vy<-700) b.vy=-700; b.x+=b.vx*h; b.y+=b.vy*h; b.a+=b.vx/b.r*h; b.age+=h; if(b.sc<1) b.sc=Math.min(1,b.sc+h*4); }
    for(const b of L) b.cn=0;
    for(let it=0;it<5;it++){
      for(let i=0;i<L.length;i++){ const a=L[i]; if(a.dead) continue;
        for(let j=i+1;j<L.length;j++){ const b=L[j]; if(b.dead) continue; const dx=b.x-a.x, dy=b.y-a.y, rr=a.r+b.r; if(dx*dx+dy*dy>=rr*rr+1) continue;
          if(a.lv===b.lv && a.age>.05 && b.age>.05){ merge(a,b); break; }
          const d=Math.sqrt(dx*dx+dy*dy)||.01, nx=dx/d, ny=dy/d, ov=rr-d; if(ov<=0) continue; const ma=a.r*a.r, mb=b.r*b.r, ta=mb/(ma+mb), tb=ma/(ma+mb);
          a.x-=nx*ov*ta; a.y-=ny*ov*ta; b.x+=nx*ov*tb; b.y+=ny*ov*tb; if(it===0){ a.cn++; b.cn++; if(!a.land && a.age>.2){ a.land=1; a.sq=.22; } if(!b.land && b.age>.2){ b.land=1; b.sq=.22; } }
          if(it===0){ const vn=(b.vx-a.vx)*nx+(b.vy-a.vy)*ny; if(vn<0){ const j=-(1.15)*vn/(1/ma+1/mb); a.vx-=j*nx/ma; a.vy-=j*ny/ma; b.vx+=j*nx/mb; b.vy+=j*ny/mb;
              const tx=-ny, ty=nx, vt=(b.vx-a.vx)*tx+(b.vy-a.vy)*ty, jt=vt*.08/(1/ma+1/mb); a.vx+=jt*tx/ma; a.vy+=jt*ty/ma; b.vx-=jt*tx/mb; b.vy-=jt*ty/mb; } } } }
      for(const b of L){ if(b.dead) continue; if(b.x<b.r){ b.x=b.r; if(b.vx<0) b.vx*=-.2; } if(b.x>BW-b.r){ b.x=BW-b.r; if(b.vx>0) b.vx*=-.2; } if(b.y>BH-b.r){ b.y=BH-b.r; if(b.vy>0) b.vy*=-.12; b.vx*=.985; if(!b.land){ b.land=1; b.sq=.22; } } } }
    if(L.some(b=>b.dead)) B=L.filter(b=>!b.dead); }
  function step(dt){ if(phase!=="play" || over) return; cool=Math.max(0,cool-dt); gt+=dt; for(const b of B) if(b.sq>0) b.sq=Math.max(0,b.sq-dt); for(const q of RG){ q.t-=dt; q.r+=dt*420; } RG=RG.filter(q=>q.t>0);
    acc+=dt; const H=1/120; let n=0; while(acc>=H && n<12){ phys(H); acc-=H; n++; } if(n>=12) acc=0;
    for(const p of P){ p.vy+=900*dt; p.x+=p.vx*dt; p.y+=p.vy*dt; p.t-=dt; } P=P.filter(p=>p.t>0); for(const t of TX){ t.tt-=dt; t.y-=40*dt; } TX=TX.filter(t=>t.tt>0); shake=Math.max(0,shake-dt);
    const hi=B.some(b=>b.age>1.5 && b.y-b.r<LINE); danger=hi?danger+dt:Math.max(0,danger-dt*2); if(danger>2.5) gameOver();
    if(bot && cool<=0 && !over){ botAim(); drop(); } }
  function botAim(){ /* 같은 과일 위로 · 없으면 아무 데나 */ const same=B.filter(b=>b.lv===held).sort((a,b)=>a.y-b.y)[0]; aimX=same && Math.random()<.35?same.x+(Math.random()-.5)*8:FR[held][2]+Math.random()*(BW-2*FR[held][2]); }
  async function gameOver(){ if(over) return; over=true; phase="over"; try{ SFX.bad(); }catch(e){} const r=REC(); const isBest=score>(r.best|0); r.best=Math.max(r.best|0,score); r.top=Math.max(r.top|0,maxLv); r.n=(r.n|0)+1; st("hyeng_proto_frr", r);
    const nr=await lbSave(score); if(gone) return; const rk=rows("W").findIndex(x=>x.c===code)+1, coins=score>=1500?9:score>=800?7:score>=300?5:3;
    setTimeout(()=>{ if(gone) return; const got=PUI.award(api, {title:score+"점", sub:"과일 합치기", rows:null, coins, again:{}, upd:(b,t)=>{ b.best=Math.max(b.best|0,score); t.top=Math.max(t.top|0,maxLv); }}), left=MG.payLeft("fruit");
      PUI.result(U, {res:"win", stars:score>=1500?3:score>=800?2:score>=300?1:0, title:isBest?"내 최고 기록!":score.toLocaleString()+"점!", sub:"가장 큰 과일 "+EMO[maxLv]+" "+FR[maxLv][0]+" ("+FR[maxLv][1]+")", av:api.av,
        rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"],["🍉", score.toLocaleString(), "점", isBest],["trophy", rk?rk+"등":"-", "이번 주"]],
        extra:(nr.W?'📟 <b style="color:#ff8ef0">이번 주 기록 NEW!</b> ':'')+(nr.A?'<b style="color:#ff8ef0">전체 기록 NEW!</b>':''), prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3},
        onAgain:()=>api.restart({go:"play"}), onMenu:()=>api.restart({}), onOut:()=>MG.exit()}); }, fast?50:900); }
  /* ── 조작: 상자를 눌러 끌기 → 떼면 떨어짐 · 키보드 ←→ 스페이스 ── */
  const toX=e=>{ const r=cv.getBoundingClientRect(); return (e.clientX-r.left)/r.width*BW; };
  cv.addEventListener("pointerdown", e=>{ if(phase!=="play") return; e.preventDefault(); holdOn=true; aimX=toX(e); try{ cv.setPointerCapture(e.pointerId); }catch(_){} });
  cv.addEventListener("pointermove", e=>{ if(phase!=="play") return; if(holdOn || e.pointerType==="mouse") aimX=toX(e); });
  const up=e=>{ if(!holdOn) return; holdOn=false; aimX=toX(e); drop(); }; cv.addEventListener("pointerup", up); cv.addEventListener("pointercancel", ()=>{ holdOn=false; });
  const onKey=e=>{ if(phase!=="play") return; if(e.key==="ArrowLeft") aimX-=24; else if(e.key==="ArrowRight") aimX+=24; else if(e.key===" "||e.key==="Enter"){ drop(); e.preventDefault(); } };
  window.addEventListener("keydown", onKey);
  /* ── 그리기 ── */
  function paint(){ fit(); const s=SC; g.setTransform(1,0,0,1,0,0); g.clearRect(0,0,cv.width,cv.height); const sh=shake>0?(Math.random()-.5)*shake*16*s:0; g.setTransform(s,0,0,s,sh,0);
    { const bg=g.createLinearGradient(0,0,0,BH); bg.addColorStop(0,"#fffdf6"); bg.addColorStop(1,"#ffe9c2"); g.fillStyle=bg; g.fillRect(0,0,BW,BH); g.fillStyle="rgba(255,170,90,.12)"; for(let i=0;i<BW;i+=60) g.fillRect(i,0,30,BH); }
    /* 선 */ const dg=danger>0; g.strokeStyle=dg?(Math.floor(performance.now()/180)%2?"#ff3b5c":"#ffb3c0"):"rgba(255,90,95,.35)"; g.lineWidth=dg?5:3; g.setLineDash([16,12]); g.beginPath(); g.moveTo(0,LINE); g.lineTo(BW,LINE); g.stroke(); g.setLineDash([]);
    if(phase==="play" && !over){ const r=FR[held][2], x=Math.max(r,Math.min(BW-r,aimX)); g.strokeStyle="rgba(36,49,74,.18)"; g.lineWidth=3; g.setLineDash([6,10]); g.beginPath(); g.moveTo(x,HOLD_Y+r); g.lineTo(x,BH); g.stroke(); g.setLineDash([]); cloud(x); if(cool<=0||fast) art(held,x,HOLD_Y,0,1, cool>0?.5:1); }
    for(const b of B) art(b.lv,b.x,b.y,b.a,b.sc,1, b.sc<.9||b.vy>520?"w":b.cn>=4?"s":"n", b.sq);
    for(const q of RG){ g.globalAlpha=Math.max(0,q.t/.45); g.strokeStyle=q.c; g.lineWidth=8; g.beginPath(); g.arc(q.x,q.y,q.r,0,7); g.stroke(); } g.globalAlpha=1;
    { g.fillStyle="rgba(255,255,255,.28)"; g.fillRect(14,LINE+20,10,BH-LINE-60); g.fillRect(30,LINE+40,4,BH-LINE-120); }
    for(const p of P){ g.globalAlpha=Math.min(1,p.t*2); g.fillStyle=p.c; g.beginPath(); g.arc(p.x,p.y,p.r,0,7); g.fill(); } g.globalAlpha=1;
    g.textAlign="center"; g.font='900 32px Jua, "Noto Sans KR", sans-serif'; for(const t of TX){ g.globalAlpha=Math.min(1,t.tt*1.6); g.lineWidth=6; g.strokeStyle="rgba(36,49,74,.8)"; g.strokeText(t.t,t.x,t.y); g.fillStyle=t.c; g.fillText(t.t,t.x,t.y); } g.globalAlpha=1;
    if(over){ g.fillStyle="rgba(36,49,74,.55)"; g.fillRect(0,0,BW,BH); g.fillStyle="#fff"; g.font='900 56px Jua, sans-serif'; g.fillText("끝!",BW/2,BH/2-10); g.font='900 34px sans-serif'; g.fillText(score.toLocaleString()+"점",BW/2,BH/2+44); } }
  function art(lv,x,y,a,sc,al,ex,sq){ const A=ART[lv]; if(!A) return; g.save(); g.globalAlpha=al; g.translate(x,y); const q=sq>0?Math.sin(sq/.22*Math.PI)*.16:0; g.scale(1+q,1-q); g.rotate(a*.35); const k=sc/SC; g.scale(k,k); g.drawImage(ex==="s"?A.s:ex==="w"?A.w:A.c,-A.h,-A.h); g.restore(); }
  function cloud(x){ const y=26, t=performance.now()/400; g.save(); g.translate(x, y+Math.sin(t)*3); g.fillStyle="#fff"; g.strokeStyle="rgba(36,49,74,.18)"; g.lineWidth=3; [[-34,6,20],[-14,-6,24],[12,-8,22],[32,4,18],[0,10,22]].forEach(([cx,cy,r])=>{ g.beginPath(); g.arc(cx,cy,r,0,7); g.fill(); });
    g.fillStyle="#2b1d2a"; [-10,10].forEach(ex=>{ g.beginPath(); g.arc(ex,2,3.5,0,7); g.fill(); }); g.strokeStyle="#2b1d2a"; g.lineWidth=2.5; g.beginPath(); g.arc(0,6,5,.2*Math.PI,.8*Math.PI); g.stroke(); g.fillStyle="rgba(255,110,140,.5)"; [-18,18].forEach(ex=>{ g.beginPath(); g.ellipse(ex,9,5,3,0,0,7); g.fill(); }); g.restore(); }
  /* ── 틀 ── */
  function tick(dt){ if(gone || paused) return; if(fast) dt*=1; step(dt);
    tabT+=dt; tabHold=Math.max(0,tabHold-dt); if(tabT>5 && !tabHold){ tabT=0; tabK=TABS[(TABS.findIndex(t=>t[0]===tabK)+1)%3][0]; ledPaint(); } }
  function render(){ if(phase!=="title") paint(); }
  function dispose(){ gone=true; window.removeEventListener("keydown", onKey); try{ R.remove(); }catch(e){} }
  fit(); title(); lbLoad(); if((api.opt||{}).go==="play") begin(); ready=true;
  return {scene, cam, tick, render, dispose, pause:v=>{ paused=!!v; },
    get B(){ return B; }, get score(){ return score; }, get over(){ return over; }, get phase(){ return phase; }, get ready(){ return ready; }, get maxLv(){ return maxLv; }, get merges(){ return merges; }, get drops(){ return drops; }, get held(){ return held; },
    set bot(v){ bot=!!v; }, set fast(v){ fast=v?1:0; }, aim:x=>{ aimX=x; }, drop, begin, title, tab:k=>{ tabK=k; tabHold=12; ledPaint(); }, get tabK(){ return tabK; }, get lb(){ return LB; }, lbLoad, keys:()=>keys(now()), gameOver, FR, step:dt=>step(dt) };
}
MG.reg("fruit", {ic:"🍉", nm:"과일 합치기", tag:"같은 과일을 합쳐 수박까지 · 📟 이번 주 · 이번 달 · 전체 랭킹", bg:"linear-gradient(135deg,#ff4d5e,#ffd84a 45%,#38b25a)", big:"🍒🍉", menu:true,
  how:[["🍒","같은 과일끼리 닿으면 다음 과일로"],["📟","형광판 랭킹: 이번 주 · 이번 달 · 전체"]], payTxt:"점수 따라 🪙 3~9",
  bestTxt:(b,t)=>'🏆 최고 '+(b.best|0)+'점', ui:{look:false, btns:[]}, start});
})();
