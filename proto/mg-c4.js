/* ═════════ 🔴 4줄 팡 — 🎡 놀이 섬 4줄 탑
   (v637) 사용자: 「3번도 좋다」 = 가로·세로·대각선으로 내 알 4개를 먼저 이으면 이김 (7칸 × 6줄)
   · 🤖 봇: 🐣 쉬움 · 🐥 보통 · 🦅 어려움 (알파-베타 찾기 · 깊이 1/4/6)
   · 👫 친구랑 1:1 (MG.room 2명) — 차례인 사람만 방 g.mv(놓은 칸 목록)를 씀 → 둘 다 같은 순서로 놓음 · 30초 지나면 아무 데나 · 친구가 나가면 이김
   · 3D 판(구멍 뚫린 파란 판 · 알이 톡톡 떨어짐 · 이기면 4알 반짝) · 화면 아무 데나 눌러 칸 고르기
   · 상: MG 공통 하루 3판 🪙 (이김 8 · 비김 5 · 짐 3)
   시험 손잡이: MG.run.mode · .bd(칸[c][r]) · .mv · .turn · .me · .over · .win · .play(c) · .ai(lv) · .fast · .menuGo(k) · .ready */
(function(){
"use strict";
if(!window.MG) return;
const C=7, Rw=6;
const LV={easy:{nm:"쉬움",ic:"🐣",d:1,rnd:.35}, normal:{nm:"보통",ic:"🐥",d:4,rnd:.06}, hard:{nm:"어려움",ic:"🦅",d:6,rnd:0}};
const st=(k,v)=>{ try{ return typeof store==="function" ? store(k,v) : (v===undefined?JSON.parse(localStorage.getItem(k)||"null"):localStorage.setItem(k,JSON.stringify(v))); }catch(e){ return null; } };
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
/* ── 판 규칙 (bd[c] = 아래부터 0/1 목록) ── */
const fresh=()=>Array.from({length:C},()=>[]);
const at=(bd,c,r)=>(c<0||c>=C||r<0)?undefined:bd[c][r];
function line4(bd, c, r){ const p=at(bd,c,r); if(p===undefined) return null; for(const [dx,dy] of [[1,0],[0,1],[1,1],[1,-1]]){ const L=[[c,r]];
    for(const s of [1,-1]){ let x=c+dx*s, y=r+dy*s; while(at(bd,x,y)===p){ L.push([x,y]); x+=dx*s; y+=dy*s; } } if(L.length>=4) return L; } return null; }
const full=bd=>bd.every(col=>col.length>=Rw);
/* 봇 */
function score(bd, me){ let s=0; const op=1-me; for(let c=0;c<C;c++) for(let r=0;r<Rw;r++) for(const [dx,dy] of [[1,0],[0,1],[1,1],[1,-1]]){ let m=0,o=0,ok=true; for(let k=0;k<4;k++){ const x=c+dx*k, y=r+dy*k; if(x<0||x>=C||y<0||y>=Rw){ ok=false; break; } const v=bd[x][y]; if(v===me) m++; else if(v===op) o++; } if(!ok) continue;
      if(m&&!o) s+=m===3?20:m===2?4:1; else if(o&&!m) s-=o===3?24:o===2?4:1; }
  for(let r=0;r<bd[3].length;r++) s+=bd[3][r]===me?3:-3; return s; }
const ORD=[3,2,4,1,5,0,6];
function search(bd, d, a, b, who, me){ for(const c of ORD){ if(bd[c].length>=Rw) continue; bd[c].push(who); const w=line4(bd,c,bd[c].length-1); bd[c].pop(); if(w) return who===me?1e6+d:-1e6-d; }
  if(d===0 || full(bd)) return score(bd, me);
  if(who===me){ let v=-Infinity; for(const c of ORD){ if(bd[c].length>=Rw) continue; bd[c].push(who); v=Math.max(v, search(bd,d-1,a,b,1-who,me)); bd[c].pop(); a=Math.max(a,v); if(a>=b) break; } return v; }
  let v=Infinity; for(const c of ORD){ if(bd[c].length>=Rw) continue; bd[c].push(who); v=Math.min(v, search(bd,d-1,a,b,1-who,me)); bd[c].pop(); b=Math.min(b,v); if(a>=b) break; } return v; }
function aiMove(bd, me, lv){ const L=LV[lv]||LV.normal, ok=ORD.filter(c=>bd[c].length<Rw); if(!ok.length) return -1;
  for(const c of ok){ bd[c].push(me); const w=line4(bd,c,bd[c].length-1); bd[c].pop(); if(w) return c; }   /* 이길 수 있으면 */
  if(lv!=="easy" || Math.random()<.6) for(const c of ok){ bd[c].push(1-me); const w=line4(bd,c,bd[c].length-1); bd[c].pop(); if(w) return c; }   /* 막기 */
  if(Math.random()<L.rnd) return ok[Math.floor(Math.random()*ok.length)];
  let best=ok[0], bv=-Infinity; for(const c of ok){ bd[c].push(me); const v=search(bd, L.d-1, -Infinity, Infinity, 1-me, me)+(Math.random()*.5); bd[c].pop(); if(v>bv){ bv=v; best=c; } } return best; }

function css(){ if(document.getElementById("c4Css")) return; const s=document.createElement("style"); s.id="c4Css"; s.textContent=`
#mgUI .c4R{position:absolute;inset:0;pointer-events:none;font-family:var(--kr);color:#fff} #mgUI.c4On .mgJoyH,#mgUI.c4On .mgJoy{display:none!important}
#mgUI .c4Hit{position:absolute;inset:0;pointer-events:auto;touch-action:none}
#mgUI .c4Top{position:absolute;left:50%;top:calc(56px + env(safe-area-inset-top));transform:translateX(-50%);display:flex;gap:8px;align-items:center;pointer-events:none;width:min(94vw,520px)}
#mgUI .c4P{flex:1;display:flex;align-items:center;gap:7px;background:rgba(20,26,60,.6);border:2px solid rgba(255,255,255,.25);border-radius:16px;padding:6px 10px;min-width:0;transition:all .2s}
#mgUI .c4P i{width:24px;height:24px;border-radius:50%;flex:none;box-shadow:inset 0 -3px 0 rgba(0,0,0,.25)} #mgUI .c4P b{font-weight:400;font-size:16px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
#mgUI .c4P.on{border-color:#ffe14d;background:rgba(40,46,110,.85);box-shadow:0 0 0 3px rgba(255,225,77,.35);transform:scale(1.04)}
#mgUI .c4Tm{width:46px;height:46px;flex:none;border-radius:50%;background:conic-gradient(#ffe14d var(--p,100%),rgba(255,255,255,.18) 0);display:flex;align-items:center;justify-content:center;font-family:var(--en);font-weight:900;font-size:15px}
#mgUI .c4Tm span{width:36px;height:36px;border-radius:50%;background:#20265a;display:flex;align-items:center;justify-content:center}
#mgUI .c4Say{position:absolute;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translateX(-50%);background:rgba(20,26,60,.72);border-radius:16px;padding:8px 16px;font-size:17px;white-space:nowrap;pointer-events:none}
#mgUI .c4Menu{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:12px;pointer-events:auto;padding:calc(60px + env(safe-area-inset-top)) 16px calc(16px + env(safe-area-inset-bottom));background:rgba(16,22,58,.55)}
#mgUI .c4Menu.on{display:flex} #mgUI .c4Menu h2{margin:0;font-weight:400;font-size:34px;text-shadow:0 3px 0 rgba(0,0,0,.3)} #mgUI .c4Menu .sub{font-size:14.5px;opacity:.9;text-align:center}
#mgUI .c4Menu .g{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;width:min(100%,460px)}
#mgUI .c4Menu button{font:inherit;border:0;border-radius:18px;background:#fff;color:#20265a;box-shadow:0 5px 0 #9aa6d8;padding:10px 6px;min-height:96px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:17px}
#mgUI .c4Menu button .e{font-size:34px} #mgUI .c4Menu button small{font-size:12px;opacity:.7} #mgUI .c4Menu button.co{grid-column:1/-1;min-height:70px;flex-direction:row;gap:10px;background:linear-gradient(135deg,#ff5a5f,#ffc83d);color:#fff;box-shadow:0 5px 0 #c8642e}
#mgUI .c4Menu button:active{transform:translateY(4px);box-shadow:0 1px 0 #9aa6d8} #mgUI .c4Menu .out{min-height:46px;background:rgba(255,255,255,.2);color:#fff;box-shadow:none;padding:8px 20px}
#mgUI .c4Menu .rec{font-size:13.5px;opacity:.9;text-align:center}
@media (orientation:landscape) and (max-height:620px){ #mgUI .c4Top{top:calc(8px + env(safe-area-inset-top));width:min(54vw,480px)} #mgUI .c4Menu .g{grid-template-columns:repeat(4,1fr);width:min(100%,640px)} #mgUI .c4Menu button.co{grid-column:auto;flex-direction:column;min-height:96px} }`; document.head.appendChild(s); }

function start(api){
  const SFX=api.sfx, LOW=!!api.low; api.menu=true; css(); api.ui.classList.add("c4On");
  let gone=false, paused=false, fast=0, mode="menu", ready=false;
  const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  const REC=()=>Object.assign({w:{}, n:0, bs:0, s:0}, st("hyeng_proto_c4r")||{});
  const TM=[]; const later=(s,fn)=>TM.push({t:fast?Math.min(s,.03):s, fn});
  /* ══ 3D ══ */
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x8fd0ff); scene.fog=new THREE.Fog(0x8fd0ff, 45, 95);
  const cam=new THREE.PerspectiveCamera(38, 1, .1, 80);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x88aa77, .55)); const sun=new THREE.DirectionalLight(0xfff2dc,.75); sun.position.set(4,9,8); scene.add(sun);
  if(!LOW){ sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); Object.assign(sun.shadow.camera,{left:-7,right:7,top:8,bottom:-2,near:1,far:30}); }
  const disp=[]; const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const MS=(c,o)=>{ const m=toon(new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.7},o||{}))); disp.push(m); return m; };
  const GE=g=>{ disp.push(g); return g; };
  { const fl=new THREE.Mesh(GE(new THREE.CircleGeometry(30,40)), MS(0x8fdc8f)); fl.rotation.x=-Math.PI/2; fl.receiveShadow=true; scene.add(fl);
    const rug=new THREE.Mesh(GE(new THREE.CircleGeometry(6,40)), MS(0xfff2c4)); rug.rotation.x=-Math.PI/2; rug.position.y=.01; rug.receiveShadow=true; scene.add(rug);
    for(let i=0;i<14;i++){ const a=i/14*Math.PI*2, t=new THREE.Mesh(GE(new THREE.ConeGeometry(1.1,2.8,7)), MS(0x3fae5a)); t.position.set(Math.cos(a)*16, 1.4, Math.sin(a)*16-6); scene.add(t); } }
  const CS=1, BX0=-(C-1)/2*CS, BY0=.9;
  const cx=c=>BX0+c*CS, cy=r=>BY0+r*CS;
  const board=new THREE.Group(); scene.add(board);
  { const W=C*CS+.5, H=Rw*CS+.4, tw=C*96+48, th=Rw*96+38; const cv=document.createElement("canvas"); cv.width=tw; cv.height=th; const g=cv.getContext("2d");
    g.fillStyle="#3b6cff"; g.fillRect(0,0,tw,th); g.fillStyle="rgba(255,255,255,.08)"; for(let i=0;i<tw;i+=24) g.fillRect(i,0,10,th);
    g.globalCompositeOperation="destination-out"; for(let c=0;c<C;c++) for(let r=0;r<Rw;r++){ g.beginPath(); g.arc(24+c*96+48, th-19-r*96-48, 38, 0, 7); g.fill(); }
    g.globalCompositeOperation="source-over"; g.strokeStyle="rgba(20,40,140,.55)"; g.lineWidth=6; for(let c=0;c<C;c++) for(let r=0;r<Rw;r++){ g.beginPath(); g.arc(24+c*96+48, th-19-r*96-48, 40, 0, 7); g.stroke(); }
    const t=new THREE.CanvasTexture(cv); t.encoding=THREE.sRGBEncoding; t.anisotropy=4; disp.push(t);
    /* (alpha 구멍은 툰 재질에서 안 뚫려서) 구멍 뚫린 모양(Shape) 판 */
    const y0=BY0-.5+H/2-.2, sh=new THREE.Shape(); sh.moveTo(-W/2,-H/2); sh.lineTo(W/2,-H/2); sh.lineTo(W/2,H/2); sh.lineTo(-W/2,H/2); sh.lineTo(-W/2,-H/2);
    for(let c=0;c<C;c++) for(let r=0;r<Rw;r++){ const hp=new THREE.Path(); hp.absarc(cx(c), cy(r)-y0, .4, 0, Math.PI*2, true); sh.holes.push(hp); }
    const pg=GE(new THREE.ShapeGeometry(sh, 10)), pm=MS(0x1c3cc4,{side:THREE.DoubleSide});
    [.17,-.17].forEach(z=>{ const p=new THREE.Mesh(pg,pm); p.position.set(0, y0, z); p.castShadow=true; board.add(p); });
    const rg=GE(new THREE.TorusGeometry(.41,.025,6,28)), rm=MS(0x2440b0); for(let c=0;c<C;c++) for(let r=0;r<Rw;r++){ const q=new THREE.Mesh(rg,rm); q.position.set(cx(c), cy(r), .18); board.add(q); }
    const fm=MS(0x1a2f9a); [[-W/2-.15,0],[W/2+.15,0]].forEach(([x])=>{ const b=new THREE.Mesh(GE(new THREE.BoxGeometry(.3,H+.9,.6)), fm); b.position.set(x, BY0-.5+H/2-.2+.0, 0); b.castShadow=true; board.add(b); });
    const base=new THREE.Mesh(GE(new THREE.BoxGeometry(W+1.4,.35,1.6)), MS(0xffc83d)); base.position.set(0,.17,0); base.castShadow=base.receiveShadow=true; board.add(base);
    const bot=new THREE.Mesh(GE(new THREE.BoxGeometry(W,.18,.5)), fm); bot.position.set(0,BY0-.6,0); board.add(bot); }
  /* 알 */
  const COL=[0xff4d5e, 0xffd23f], COLS=["#ff4d5e","#ffd23f"];
  const dg=GE(new THREE.CylinderGeometry(.42,.42,.24,28)); dg.rotateX(Math.PI/2);
  const dmat=[MS(COL[0]), MS(COL[1])], rim=[MS(0xc8213a), MS(0xd9a90f)];
  const iconTex=(k)=>{ const cv=document.createElement("canvas"); cv.width=cv.height=128; const g=cv.getContext("2d"); g.fillStyle=COLS[k]; g.fillRect(0,0,128,128); g.fillStyle="rgba(255,255,255,.9)"; g.font="80px sans-serif"; g.textAlign="center"; g.textBaseline="middle";
    if(k===0){ g.beginPath(); for(let i=0;i<10;i++){ const a=-Math.PI/2+i*Math.PI/5, rr=i%2?20:44; g.lineTo(64+Math.cos(a)*rr,64+Math.sin(a)*rr); } g.fill(); } else { g.beginPath(); g.moveTo(64,100); g.bezierCurveTo(10,60,30,18,64,44); g.bezierCurveTo(98,18,118,60,64,100); g.fill(); }
    const t=new THREE.CanvasTexture(cv); t.encoding=THREE.sRGBEncoding; disp.push(t); return t; };
  const fmat=[MS(0xffffff,{map:iconTex(0)}), MS(0xffffff,{map:iconTex(1)})], fg=GE(new THREE.CircleGeometry(.34,28));
  function discMesh(p){ const g=new THREE.Group(); const m=new THREE.Mesh(dg,[dmat[p],fmat[p],fmat[p]]); m.castShadow=!LOW; g.add(m); const ring=new THREE.Mesh(GE(new THREE.TorusGeometry(.36,.035,6,28)), rim[p]); ring.position.z=.125; g.add(ring); const r2=ring.clone(); r2.position.z=-.125; g.add(r2); return g; }
  /* CylinderGeometry 윗면 = +z 쪽 (회전 뒤) — 재질 [옆, 위, 아래] */
  const DM=[]; const FALL=[]; const ghost=discMesh(0); ghost.traverse(o=>{ if(o.material){ o.material=o.material.length?o.material.map(m=>{ const q=m.clone(); q.transparent=true; q.opacity=.5; disp.push(q); return q; }):(()=>{ const q=o.material.clone(); q.transparent=true; q.opacity=.5; disp.push(q); return q; })(); } }); ghost.visible=false; scene.add(ghost);
  const arrow=new THREE.Mesh(GE(new THREE.ConeGeometry(.22,.4,4)), MS(0xffffff,{emissive:0x666666})); arrow.rotation.x=Math.PI; scene.add(arrow); arrow.visible=false;
  /* 카메라 맞추기 */
  function fitCam(){ const w=innerWidth, h=innerHeight, asp=w/h; cam.aspect=asp; const land=asp>1.2, needW=C*CS+2.2, needH=Rw*CS+(land?2.6:4.4);
    const t=Math.tan(cam.fov*Math.PI/360), dW=needW/2/t/asp, dH=needH/2/t, d=Math.max(dW,dH); cam.position.set(0, BY0+Rw*CS/2+ (land?.6:1.2), d+.4); cam.lookAt(0, BY0+Rw*CS/2-(land?.1:1.1), 0); cam.updateProjectionMatrix(); }
  /* ══ 화면 ══ */
  const U=api.ui, R=document.createElement("div"); R.className="c4R"; U.insertBefore(R, U.querySelector(".mgTop"));
  R.innerHTML='<div class="c4Hit"></div><div class="c4Top"><div class="c4P p0"><i></i><b></b></div><div class="c4Tm"><span>30</span></div><div class="c4P p1"><i></i><b></b></div></div><div class="c4Say"></div><div class="c4Menu"></div>';
  ["pointerdown","pointermove","pointerup"].forEach(t=>R.addEventListener(t, e=>e.stopPropagation()));
  const $=s=>R.querySelector(s), HIT=$(".c4Hit"), MENU=$(".c4Menu"), SAY=$(".c4Say"), TMR=$(".c4Tm");
  const say=t=>{ SAY.textContent=t||""; SAY.style.display=t?"":"none"; };
  /* ══ 판 상태 ══ */
  let bd=fresh(), mv=[], first=0, me=0, over=false, win=null, busy=false, opp="bot", lv="normal", names=["나","봇"], turnT=0, hov=-1, RM=null, oppGone=0, coStart=0;
  const turn=()=>(first+mv.length)%2;
  function seats(){ [0,1].forEach(p=>{ const el=$(".c4P.p"+p); el.querySelector("i").style.background=COLS[p]; el.querySelector("b").textContent=names[p]; el.classList.toggle("on", !over && turn()===p); }); }
  function clearDiscs(){ DM.forEach(d=>board.remove(d)); DM.length=0; FALL.length=0; }
  function newGame(o){ bd=fresh(); mv=[]; over=false; win=null; busy=false; clearDiscs(); first=o.first|0; me=o.me|0; opp=o.opp; lv=o.lv||lv; names=o.names; turnT=0; oppGone=0; mode=o.mode; MENU.classList.remove("on"); TMR.style.display=""; seats();
    say(turn()===me?"내 차례! 칸을 눌러요 👆":(opp==="bot"?LV[lv].ic+" 봇이 생각 중…":"친구 차례예요")); if(opp==="bot" && turn()!==me) later(.7, botGo); }
  function put(c, p, anim){ const r=bd[c].length; if(r>=Rw) return false; bd[c].push(p); mv.push(c); const d=discMesh(p); d.position.set(cx(c), anim?cy(Rw)+.6:cy(r), 0); board.add(d); DM.push(d);
    if(anim) FALL.push({d, y:cy(Rw)+.6, ty:cy(r), v:0, b:0}); else d.position.y=cy(r);
    try{ SFX.tone(p?520:660,.06,"triangle",.04); }catch(e){}
    const w=line4(bd,c,r); if(w){ over=true; win={p, L:w}; later(fast?.02:.55, ()=>finish()); } else if(full(bd)){ over=true; win={p:-1}; later(fast?.02:.4, ()=>finish()); }
    turnT=0; seats(); if(!over){ say(turn()===me?"내 차례! 칸을 눌러요 👆":(opp==="bot"?LV[lv].ic+" 봇이 생각 중…":"친구 차례예요")); } return true; }
  function play(c){ if(over || busy || turn()!==me || mode==="menu") return false; if(c<0||c>=C||bd[c].length>=Rw){ try{ SFX.bad(); }catch(e){} return false; }
    put(c, me, true); if(opp==="co" && RM) RM.put("g", {mv:mv.slice(), first, ro:coRo, sq:mv.length}); else if(!over) later(fast?.02:.55, botGo); return true; }
  function botGo(){ if(over || opp!=="bot" || turn()===me || gone) return; const c=aiMove(bd.map(x=>x.slice()), 1-me, lv); if(c>=0) put(c, 1-me, true); }
  function finish(){ if(gone) return; const r=REC(); const res=win.p<0?"draw":win.p===me?"win":"lose";
    if(win.L) win.L.forEach(([c,rr])=>{ const i=DM.findIndex(d=>Math.abs(d.position.x-cx(c))<.01 && Math.abs(d.position.y-cy(rr))<.05); if(i>=0) DM[i].userData.glow=1; });
    if(res==="win"){ try{ SFX.win(); }catch(e){} say("🎉 4줄 팡! 이겼어요!"); } else if(res==="lose"){ try{ SFX.bad(); }catch(e){} say(opp==="bot"?"아깝다! 다시 해 봐요":"친구가 이겼어요!"); } else say("비겼어요 🤝");
    const key=opp==="bot"?lv:"co"; r.n++; if(res==="win"){ r.w[key]=(r.w[key]|0)+1; r.s++; r.bs=Math.max(r.bs,r.s); } else if(res==="lose") r.s=0; st("hyeng_proto_c4r", r);
    seats(); TMR.style.display="none";
    later(fast?.05:1.8, ()=>{ if(gone) return; const coins=res==="win"?8:res==="draw"?5:3; const vs=opp==="bot"?LV[lv].ic+" "+LV[lv].nm+" 봇":"👫 "+esc(names[1-me]);
      api.end({title:res==="win"?"🎉 이겼어요!":res==="draw"?"🤝 비겼어요":"😅 졌어요", sub:"4줄 팡 · "+vs+" · "+mv.length+"수", rows:null, coins, again:opp==="bot"?{go:lv}:{},
        extra:'<div class="sub" style="margin-top:6px">🏆 이긴 판 🐣 '+(r.w.easy|0)+' · 🐥 '+(r.w.normal|0)+' · 🦅 '+(r.w.hard|0)+' · 👫 '+(r.w.co|0)+' · 🔥 최고 '+r.bs+'연승</div>',
        upd:(b,t)=>{ if(res==="win") t.win=(t.win|0)+1; if(opp==="co") t.co=(t.co|0)+1; }}); try{ if(RM){ RM.dispose(); RM=null; } }catch(e){} }); }
  /* ── 칸 고르기 (화면 x → 칸) ── */
  const v3=new THREE.Vector3();
  function colAt(px){ const r=HIT.getBoundingClientRect(); const sx=c=>{ v3.set(cx(c),cy(Rw/2),0).project(cam); return (v3.x+1)/2*r.width+r.left; }; const x0=sx(0), x1=sx(C-1), w=(x1-x0)/(C-1); const c=Math.round((px-x0)/w); return (c<0||c>=C||px<x0-w*.8||px>x1+w*.8)?-1:c; }
  HIT.addEventListener("pointermove", e=>{ hov=colAt(e.clientX); });
  HIT.addEventListener("pointerdown", e=>{ e.preventDefault(); hov=colAt(e.clientX); });
  HIT.addEventListener("pointerup", e=>{ const c=colAt(e.clientX); if(c>=0) play(c); hov=e.pointerType==="mouse"?c:-1; });
  const onKey=e=>{ if(/^[1-7]$/.test(e.key)) play(+e.key-1); };
  window.addEventListener("keydown", onKey);
  /* ══ 메뉴 ══ */
  function menuShow(){ mode="menu"; over=true; clearDiscs(); bd=fresh(); MENU.classList.add("on"); TMR.style.display="none"; say(""); const r=REC();
    MENU.innerHTML='<h2>🔴 4줄 팡</h2><div class="sub">내 알 <b>4개</b>를 가로 · 세로 · 대각선으로 먼저 이으면 이겨요!</div><div class="g">'+
      Object.keys(LV).map(k=>'<button data-m="'+k+'"><span class="e">'+LV[k].ic+'</span>'+LV[k].nm+'<small>봇이랑 · 이김 '+(r.w[k]|0)+'</small></button>').join("")+
      '<button class="co" data-m="co"><span class="e">👫</span><span>친구랑 1:1<br><small style="opacity:.95">같은 놀이 섬 친구랑</small></span></button></div>'+
      '<div class="rec">🔥 최고 '+r.bs+'연승 · 오늘 🪙 상 '+(MG.payLeft("c4")>0?MG.payLeft("c4")+'판 남음':'다 받았어요')+'</div><button class="out">🏝 섬으로</button>'; }
  MENU.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b) return; if(b.classList.contains("out")){ MG.exit(); return; } menuGo(b.dataset.m); });
  function menuGo(k){ try{ SFX.tone(660,.06,"triangle",.04); }catch(e){} if(k==="co"){ startCo(); return; } const f=Math.random()<.5?0:1; newGame({mode:"bot", opp:"bot", lv:k, first:f, me:0, names:[String(api.nick||"나"), LV[k].ic+" 봇"]}); }
  /* ══ 👫 친구랑 1:1 ══ */
  let coRo=[], lastSq=-1;
  function startCo(){ mode="co"; MENU.classList.remove("on"); say("");
    RM=MG.room(api, {pre:"mgf", title:"4줄 팡 1:1", ic:"🔴", max:2, fill:false, wait:4000, send:.5, poll:.3, back:()=>{ try{ RM.dispose(); }catch(e){} RM=null; menuShow(); }});
    { const st0=RM.start; RM.start=async()=>{ const L=RM.live(true).map(p=>p.k); if(L.length<2){ api.msg("친구가 들어오면 시작할 수 있어요 👫", 1500); return; } try{ await NET.patch(RM.path+"/h", {ro:L.slice(0,2)}); }catch(e){} if(RM.d && RM.d.h) RM.d.h.ro=L.slice(0,2); return st0(); }; }
    RM.onStart=(h, L)=>{ coRo=(h.ro&&h.ro.length?h.ro:L.map(p=>p.k)).slice(0,2); const PD=(RM.d&&RM.d.p)||{}; const nm=coRo.map(c=>String((PD[c]&&PD[c].n)||(L.find(q=>q.k===c)||{}).n||"친구").slice(0,8));
      lastSq=-1; coStart=now(); newGame({mode:"co-play", opp:"co", first:(h.seed|0)%2, me:Math.max(0,coRo.indexOf(RM.code)), names:nm}); }; }
  function coTick(dt){ if(!RM) return; try{ RM.tick(dt); }catch(e){} if(mode!=="co-play" || over) return;
    const g=RM.d && RM.d.g; if(g && g.mv && g.sq!==lastSq && g.sq>mv.length){ lastSq=g.sq; for(let i=mv.length;i<g.mv.length && !over;i++) put(g.mv[i], turn(), true); }
    const live=RM.live(true).map(p=>p.k), oc=coRo[1-me]; oppGone=(oc && live.indexOf(oc)<0)?oppGone+dt:0;
    if(oppGone>8){ over=true; win={p:me}; say("친구가 나갔어요 — 이겼어요!"); later(.5, finish); } }
  /* ══ 틀 ══ */
  function tick(dt){ if(gone || paused) return;
    for(let i=TM.length-1;i>=0;i--){ TM[i].t-=dt; if(TM[i].t<=0){ const f=TM[i].fn; TM.splice(i,1); try{ f(); }catch(e){ console.warn("C4", e); } } }
    if(RM) coTick(dt);
    for(let i=FALL.length-1;i>=0;i--){ const f=FALL[i]; f.v-=(fast?200:28)*dt; f.y+=f.v*dt; if(f.y<=f.ty){ f.y=f.ty; if(f.b<2 && Math.abs(f.v)>2){ f.v=-f.v*.28; f.b++; try{ SFX.tone(300+f.b*80,.04,"sine",.03); }catch(e){} } else FALL.splice(i,1); } f.d.position.y=f.y; }
    if(mode!=="menu" && !over){ turnT+=dt; const lim=30, left=Math.max(0,lim-turnT); TMR.style.setProperty("--p", (left/lim*100)+"%"); TMR.querySelector("span").textContent=Math.ceil(left);
      if(turn()===me && turnT>lim){ const ok=[...Array(C).keys()].filter(c=>bd[c].length<Rw); play(ok[Math.floor(Math.random()*ok.length)]); }
      if(opp==="co" && turn()!==me && turnT>lim+20){ over=true; win={p:me}; say("친구가 오래 안 놔서 이겼어요"); later(.5, finish); } }
    const showG=mode!=="menu" && !over && turn()===me && hov>=0 && bd[hov].length<Rw; ghost.visible=arrow.visible=showG;
    if(showG){ ghost.position.set(cx(hov), cy(Rw)+.6, 0); arrow.position.set(cx(hov), cy(Rw)+1.35+Math.sin(performance.now()/180)*.08, 0); }
    const tg=performance.now()/1000; DM.forEach(d=>{ if(d.userData.glow){ const s=1+Math.sin(tg*8)*.12; d.scale.set(s,s,1); } }); }
  function render(){ fitCam(); MG.draw(scene, cam); }
  function dispose(){ gone=true; TM.length=0; window.removeEventListener("keydown", onKey); try{ if(RM) RM.dispose(); }catch(e){} RM=null; try{ R.remove(); }catch(e){} disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); }
  fitCam(); const O=api.opt||{}; if(O.go && LV[O.go]) menuGo(O.go); else menuShow(); ready=true;
  return {scene, cam, tick, render, dispose, pause:v=>{ paused=!!v; },
    get mode(){ return mode; }, get bd(){ return bd; }, get mv(){ return mv; }, get turn(){ return turn(); }, get me(){ return me; }, get over(){ return over; }, get win(){ return win; }, get ready(){ return ready; }, get RM(){ return RM; }, get falling(){ return FALL.length; },
    set fast(v){ fast=v?1:0; }, play, menuGo, menuShow, ai:(l,p)=>aiMove(bd.map(x=>x.slice()), p==null?me:p, l||"normal"), colAt, aiMove, line4 };
}
MG.reg("c4", {ic:"🔴", nm:"4줄 팡", tag:"알 4개를 먼저 이어요 · 봇 3단계 · 친구랑 1:1", bg:"linear-gradient(135deg,#3b6cff,#ff4d5e 60%,#ffd23f)", big:"🔴🟡", menu:true,
  how:[["🔴","알을 떨어뜨려 4개를 이어요"],["👫","친구랑 1:1"]], payTxt:"이김 🪙8 · 비김 5 · 짐 3",
  bestTxt:(b,t)=>'🏆 이긴 판 '+(t.win|0), ui:{look:false, btns:[]}, start});
})();
