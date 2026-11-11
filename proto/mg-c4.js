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
#mgUI .c4P{flex:1;display:flex;align-items:center;gap:7px;background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:999px;padding:3px 10px 3px 3px;min-width:0;transition:all .2s;box-shadow:0 0 0 3px #fff,0 5px 0 3px rgba(74,46,31,.35)}
#mgUI .c4P i{width:20px;height:20px;border-radius:50%;flex:none;border:3px solid #4A2E1F;box-shadow:inset 0 -3px 0 rgba(0,0,0,.2)} #mgUI .c4P b{font-weight:400;font-size:18px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;flex:1;min-width:0} #mgUI .c4P.p1{flex-direction:row-reverse;text-align:right}
#mgUI .c4P canvas{width:46px;height:46px;border-radius:50%;flex:none;border:3px solid #4A2E1F;background:#bfe6ff;box-shadow:0 0 0 3px var(--c,#fff)}
#mgUI .c4Bub{position:absolute;transform:translate(-50%,-100%);background:#fff;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:16px;padding:5px 12px;font-size:17px;white-space:nowrap;pointer-events:none;box-shadow:0 4px 0 #4A2E1F;display:none}
#mgUI .c4Bub::after{content:"";position:absolute;left:50%;bottom:-12px;margin-left:-8px;border:8px solid transparent;border-top-color:#4A2E1F;border-bottom:0}
#mgUI .c4Bub.on{display:block;animation:c4Pop .25s}
@keyframes c4Pop{from{transform:translate(-50%,-100%) scale(.5)}to{transform:translate(-50%,-100%) scale(1)}}
#mgUI .c4P.on{background:#fff;box-shadow:0 0 0 3px #FFC53D,0 5px 0 3px #4A2E1F;transform:scale(1.04)}
#mgUI .c4Tm{width:50px;height:50px;flex:none;border-radius:50%;border:3px solid #4A2E1F;background:conic-gradient(#3CC46B var(--p,100%),#fff 0);display:flex;align-items:center;justify-content:center;font-family:var(--en);font-weight:900;font-size:16px;box-shadow:0 4px 0 #4A2E1F;color:#4A2E1F}
#mgUI .c4Tm span{width:36px;height:36px;border-radius:50%;background:#FFF6E3;display:flex;align-items:center;justify-content:center;border:2px solid #4A2E1F}
#mgUI .c4Say{position:absolute;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translateX(-50%);background:#4A2E1F;color:#fff;border-radius:16px;padding:9px 18px;font-size:17px;white-space:nowrap;pointer-events:none;box-shadow:0 0 0 3px #fff}
#mgUI .c4Ban{top:calc(126px + env(safe-area-inset-top))}
#mgUI .c4Menu{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:12px;pointer-events:auto;padding:calc(60px + env(safe-area-inset-top)) 16px calc(16px + env(safe-area-inset-bottom));background:rgba(16,22,58,.55)}
#mgUI .c4Menu.on{display:flex} #mgUI .c4Menu h2{margin:0;font-weight:400;font-size:34px;text-shadow:0 3px 0 rgba(0,0,0,.3)} #mgUI .c4Menu .sub{font-size:14.5px;opacity:.9;text-align:center}
#mgUI .c4Menu .g{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;width:min(100%,460px)}
#mgUI .c4Menu button{font:inherit;border:0;border-radius:18px;background:#fff;color:#20265a;box-shadow:0 5px 0 #9aa6d8;padding:10px 6px;min-height:96px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:17px}
#mgUI .c4Menu button .e{font-size:34px} #mgUI .c4Menu button small{font-size:12px;opacity:.7} #mgUI .c4Menu button.co{grid-column:1/-1;min-height:70px;flex-direction:row;gap:10px;background:linear-gradient(135deg,#ff5a5f,#ffc83d);color:#fff;box-shadow:0 5px 0 #c8642e}
#mgUI .c4Menu button:active{transform:translateY(4px);box-shadow:0 1px 0 #9aa6d8} #mgUI .c4Menu .out{min-height:46px;background:rgba(255,255,255,.2);color:#fff;box-shadow:none;padding:8px 20px}
#mgUI .c4Menu .rec{font-size:13.5px;opacity:.9;text-align:center}
#mgUI .c4Emo{position:absolute;left:calc(12px + env(safe-area-inset-left));bottom:calc(76px + env(safe-area-inset-bottom));display:flex;flex-direction:column;gap:8px;pointer-events:auto}
#mgUI .c4Emo button{width:52px;height:52px;border-radius:16px;border:3px solid #4A2E1F;background:#fff;font-size:26px;padding:0;box-shadow:0 4px 0 #4A2E1F} #mgUI .c4Emo button:active{transform:scale(.9)}
#mgUI .c4Me{position:absolute;left:calc(66px + env(safe-area-inset-left));bottom:calc(150px + env(safe-area-inset-bottom));font-size:40px;pointer-events:none;opacity:0;transition:all .3s;transform:translateY(10px)} #mgUI .c4Me.on{opacity:1;transform:none}
#mgUI.c4Menu0 .c4Top,#mgUI.c4Menu0 .c4Emo,#mgUI.c4Menu0 .c4Ban{display:none}
@media (orientation:landscape) and (max-height:620px){ #mgUI .c4Say{left:auto;right:calc(14px + env(safe-area-inset-right));transform:none} #mgUI .c4Emo{flex-direction:row;bottom:calc(14px + env(safe-area-inset-bottom))} #mgUI .c4Me{bottom:calc(70px + env(safe-area-inset-bottom));left:calc(20px + env(safe-area-inset-left))} #mgUI .c4Top{top:calc(8px + env(safe-area-inset-top));width:min(60vw,520px)} #mgUI .c4Ban{top:calc(74px + env(safe-area-inset-top))} #mgUI .c4Menu .g{grid-template-columns:repeat(4,1fr);width:min(100%,640px)} #mgUI .c4Menu button.co{grid-column:auto;flex-direction:column;min-height:96px} }`; document.head.appendChild(s); }

function start(api){
  const SFX=api.sfx, LOW=!!api.low; api.menu=true; css(); api.ui.classList.add("c4On");
  let gone=false, paused=false, fast=0, mode="menu", ready=false;
  const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  const REC=()=>Object.assign({w:{}, n:0, bs:0, s:0}, st("hyeng_proto_c4r")||{});
  const TM=[]; const later=(s,fn)=>TM.push({t:fast?Math.min(s,.03):s, fn});
  /* ══ 3D: 보드게임 방 (탁자 위 판 · 맞은편 친구가 높은 의자에 앉아 알을 넣음) ══ */
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x22305a); scene.fog=new THREE.Fog(0x22305a, 7, 16);
  const cam=new THREE.PerspectiveCamera(44, 1, .05, 40);
  scene.add(new THREE.HemisphereLight(0xeaf2ff, 0x3a3050, .6));
  { const rim=new THREE.DirectionalLight(0xbcd4ff,.45); rim.position.set(-2,3,-4); scene.add(rim); }
  const sun=new THREE.DirectionalLight(0xfff0dc,.7); sun.position.set(1.6,4.2,2.6); scene.add(sun); scene.add(sun.target);
  if(!LOW){ sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); Object.assign(sun.shadow.camera,{left:-2.2,right:2.2,top:2.2,bottom:-2.2,near:1,far:10}); sun.shadow.bias=-.0008; }
  { const lp=new THREE.PointLight(0xffd9a0,1.1,5,1.6); lp.position.set(0,2.2,-.2); scene.add(lp); }
  const disp=[]; const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const MS=(c,o)=>{ const m=toon(new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.7},o||{}))); disp.push(m); return m; };
  const GE=g=>{ disp.push(g); return g; };
  function tex(w,h,draw){ const c=document.createElement("canvas"); c.width=w; c.height=h; draw(c.getContext("2d"),w,h); const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding; t.anisotropy=4; disp.push(t); return t; }
  const TY=.5;
  { /* 바닥 (체크 타일) · 깔개 */
    const ft=tex(256,256,(g,w)=>{ for(let i=0;i<4;i++) for(let j=0;j<4;j++){ g.fillStyle=(i+j)%2?"#2f6bd8":"#fff3dc"; g.fillRect(i*64,j*64,64,64); } }); ft.wrapS=ft.wrapT=THREE.RepeatWrapping; ft.repeat.set(6,6);
    const fl=new THREE.Mesh(GE(new THREE.PlaneGeometry(14,14)), MS(0xffffff,{map:ft})); fl.rotation.x=-Math.PI/2; fl.receiveShadow=true; scene.add(fl);
    const rug=new THREE.Mesh(GE(new THREE.CircleGeometry(1.9,40)), MS(0xff4d5e,{roughness:.95})); rug.rotation.x=-Math.PI/2; rug.position.set(0,.005,-.3); rug.receiveShadow=true; scene.add(rug);
    const r2=new THREE.Mesh(GE(new THREE.RingGeometry(1.6,1.72,40)), MS(0xffd23f)); r2.rotation.x=-Math.PI/2; r2.position.set(0,.008,-.3); scene.add(r2);
    /* 벽 · 창 · 간판 · 줄 전구 */
    const wm=MS(0x3a64c8), wl=MS(0x2a4aa0); [[0,-3.2,0],[-3.4,0,Math.PI/2],[3.4,0,-Math.PI/2]].forEach(([x,z,r])=>{ const w=new THREE.Mesh(GE(new THREE.PlaneGeometry(9,5)), wm); w.position.set(x,2.5,z); w.rotation.y=r; scene.add(w); const b=new THREE.Mesh(GE(new THREE.PlaneGeometry(9,1)), wl); b.position.set(x+(r?(x<0?.01:-.01):0),.5,z+(r?0:.01)); b.rotation.y=r; scene.add(b); });
    const win=new THREE.MeshBasicMaterial({color:0xffe6a8}); disp.push(win); [-2.2,2.2].forEach(x=>{ const q=new THREE.Mesh(GE(new THREE.PlaneGeometry(1.2,1.4)), win); q.position.set(x,2.2,-3.18); scene.add(q); const f=new THREE.Mesh(GE(new THREE.PlaneGeometry(1.36,.08)), MS(0xffffff)); f.position.set(x,2.2,-3.17); scene.add(f); const f2=new THREE.Mesh(GE(new THREE.PlaneGeometry(.08,1.56)), MS(0xffffff)); f2.position.set(x,2.2,-3.17); scene.add(f2); });
    const sg=tex(512,200,(g,w,h)=>{ g.fillStyle="#1a2450"; g.fillRect(0,0,w,h); g.strokeStyle="#ffd23f"; g.lineWidth=8; g.strokeRect(5,5,w-10,h-10); g.font="900 92px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle";
      ["4","줄","팡","!"].forEach((t,i)=>{ g.fillStyle=["#ff4d5e","#ffd23f","#ff4d5e","#ffd23f"][i]; g.fillText(t, 110+i*100, h/2+6); }); [0,1].forEach(k=>{ g.fillStyle=k?"#ffd23f":"#ff4d5e"; g.beginPath(); g.arc(k?w-34:34, h/2, 18, 0, 7); g.fill(); }); });
    const sm=new THREE.MeshBasicMaterial({map:sg}); disp.push(sm); const sign=new THREE.Mesh(GE(new THREE.PlaneGeometry(2.4,.94)), sm); sign.position.set(0,2.55,-3.15); scene.add(sign);
    const bg=GE(new THREE.SphereGeometry(.045,6,4)), bms=[0xff4d5e,0xffd23f,0xffffff].map(c=>{ const m=new THREE.MeshBasicMaterial({color:c}); disp.push(m); return m; });
    for(let i=0;i<34;i++){ const t=i/33, b=new THREE.Mesh(bg,bms[i%3]); b.position.set(-3.3+t*6.6, 3.55-Math.sin(t*Math.PI)*.45, -3.12); scene.add(b); }
    /* 화분 · 선반 위 큰 알 */
    [[-2.7,-2.6],[2.7,-2.6]].forEach(([x,z])=>{ const pot=new THREE.Mesh(GE(new THREE.CylinderGeometry(.24,.19,.4,14)), MS(0xd8743a)); pot.position.set(x,.2,z); scene.add(pot); for(let k=0;k<3;k++){ const l=new THREE.Mesh(GE(new THREE.ConeGeometry(.22-k*.04,.55,7)), MS(0x3fae5a)); l.position.set(x,.6+k*.3,z); scene.add(l); } });
    /* 매단 등 */
    const sh=new THREE.Mesh(GE(new THREE.ConeGeometry(.34,.26,20,1,true)), MS(0xffd23f,{side:THREE.DoubleSide, emissive:0x5a3a00})); sh.position.set(0,2.35,-.2); scene.add(sh);
    const cord=new THREE.Mesh(GE(new THREE.CylinderGeometry(.01,.01,1.4,4)), MS(0x222222)); cord.position.set(0,3.15,-.2); scene.add(cord); }
  /* 탁자 */
  { const top=new THREE.Mesh(GE(new THREE.BoxGeometry(2.1,.08,1.3)), MS(0xb57a4c,{roughness:.55})); top.position.set(0,TY-.04,-.25); top.castShadow=top.receiveShadow=true; scene.add(top);
    const edge=new THREE.Mesh(GE(new THREE.BoxGeometry(2.14,.03,1.34)), MS(0x8a5a3c)); edge.position.set(0,TY-.085,-.25); scene.add(edge);
    const lm=MS(0x7a4a2c); [[-.95,.3],[.95,.3],[-.95,-.8],[.95,-.8]].forEach(([x,z])=>{ const l=new THREE.Mesh(GE(new THREE.BoxGeometry(.08,TY-.08,.08)), lm); l.position.set(x,(TY-.08)/2,z); l.castShadow=true; scene.add(l); }); }
  const CS=1, BX0=-(C-1)/2*CS, BY0=.9, BS=.13;
  const cx=c=>BX0+c*CS, cy=r=>BY0+r*CS;
  const board=new THREE.Group(); board.scale.setScalar(BS); board.position.set(0,TY,-.15); scene.add(board);
  { const W=C*CS+.5, H=Rw*CS+.4;
    /* 구멍 뚫린 모양(Shape) 판 (알파 구멍은 툰 재질에서 안 뚫림) */
    const y0=BY0-.5+H/2-.2, sh=new THREE.Shape(); sh.moveTo(-W/2,-H/2); sh.lineTo(W/2,-H/2); sh.lineTo(W/2,H/2); sh.lineTo(-W/2,H/2); sh.lineTo(-W/2,-H/2);
    for(let c=0;c<C;c++) for(let r=0;r<Rw;r++){ const hp=new THREE.Path(); hp.absarc(cx(c), cy(r)-y0, .4, 0, Math.PI*2, true); sh.holes.push(hp); }
    const pg=GE(new THREE.ShapeGeometry(sh, 10)), pm=MS(0x1c3cc4,{side:THREE.DoubleSide});
    [.17,-.17].forEach(z=>{ const p=new THREE.Mesh(pg,pm); p.position.set(0, y0, z); p.castShadow=true; board.add(p); });
    const rg=GE(new THREE.TorusGeometry(.41,.035,6,28)), rm=MS(0x3b6cff); for(let c=0;c<C;c++) for(let r=0;r<Rw;r++){ const q=new THREE.Mesh(rg,rm); q.position.set(cx(c), cy(r), .18); board.add(q); }
    const fm=MS(0x1a2f9a); [-1,1].forEach(s=>{ const b=new THREE.Mesh(GE(new THREE.BoxGeometry(.3,H+.9,.6)), fm); b.position.set(s*(W/2+.15), y0+.1, 0); b.castShadow=true; board.add(b); const ft=new THREE.Mesh(GE(new THREE.BoxGeometry(.5,.25,2.6)), fm); ft.position.set(s*(W/2+.15),.12,0); board.add(ft); });
    const bot=new THREE.Mesh(GE(new THREE.BoxGeometry(W,.18,.5)), fm); bot.position.set(0,BY0-.6,0); board.add(bot);
    const cap=new THREE.Mesh(GE(new THREE.BoxGeometry(W+.6,.16,.5)), MS(0xffd23f)); cap.position.set(0,y0+H/2+.05,0); board.add(cap);
    const back=new THREE.Mesh(GE(new THREE.PlaneGeometry(W,H)), MS(0x16204a)); back.position.set(0,y0,-.6); board.add(back); }
  /* 알 */
  const COL=[0xff4d5e, 0xffd23f], COLS=["#ff4d5e","#ffd23f"];
  const dg=GE(new THREE.CylinderGeometry(.42,.42,.24,28)); dg.rotateX(Math.PI/2);
  const dmat=[MS(COL[0]), MS(COL[1])], rim=[MS(0xc8213a), MS(0xd9a90f)];
  const iconTex=(k)=>tex(128,128,(g)=>{ g.fillStyle=COLS[k]; g.fillRect(0,0,128,128); g.fillStyle="rgba(255,255,255,.92)";
    if(k===0){ g.beginPath(); for(let i=0;i<10;i++){ const a=-Math.PI/2+i*Math.PI/5, rr=i%2?20:44; g.lineTo(64+Math.cos(a)*rr,64+Math.sin(a)*rr); } g.fill(); } else { g.beginPath(); g.moveTo(64,100); g.bezierCurveTo(10,60,30,18,64,44); g.bezierCurveTo(98,18,118,60,64,100); g.fill(); } });
  const fmat=[MS(0xffffff,{map:iconTex(0)}), MS(0xffffff,{map:iconTex(1)})], torG=GE(new THREE.TorusGeometry(.36,.035,6,28));
  function discMesh(p){ const g=new THREE.Group(); const m=new THREE.Mesh(dg,[dmat[p],fmat[p],fmat[p]]); m.castShadow=!LOW; g.add(m); const ring=new THREE.Mesh(torG, rim[p]); ring.position.z=.125; g.add(ring); const r2=ring.clone(); r2.position.z=-.125; g.add(r2); return g; }
  const DM=[]; const FALL=[];
  const ghost=discMesh(0); ghost.traverse(o=>{ if(o.material){ const one=m=>{ const q=m.clone(); q.transparent=true; q.opacity=.55; disp.push(q); return q; }; o.material=Array.isArray(o.material)?o.material.map(one):one(o.material); } }); ghost.visible=false; board.add(ghost);
  const arrow=new THREE.Mesh(GE(new THREE.ConeGeometry(.3,.55,4)), MS(0xffffff,{emissive:0x888888})); arrow.rotation.x=Math.PI; board.add(arrow); arrow.visible=false;
  /* 알 받침 (남은 알 쌓기) */
  const flatG=GE(new THREE.CylinderGeometry(.42*BS,.42*BS,.22*BS,20));
  const TRAY=[{x:.78,z:.15},{x:-.78,z:-.62}].map((o,p)=>{ const g=new THREE.Group(); g.position.set(o.x,TY,o.z); scene.add(g); const t=new THREE.Mesh(GE(new THREE.BoxGeometry(.32,.025,.2)), MS(0x7a4a2c)); t.position.y=.012; t.receiveShadow=true; g.add(t); o.g=g; o.m=[]; return o; });
  function trays(){ const used=[0,0]; mv.forEach((c,i)=>used[(first+i)%2]++); [0,1].forEach(p=>{ const T=TRAY[p], n=Math.max(0,21-used[p]); while(T.m.length>n) T.g.remove(T.m.pop()); while(T.m.length<n){ const k=T.m.length, m=new THREE.Mesh(flatG,[dmat[p],fmat[p],fmat[p]]); m.position.set(((k/11)|0)*.09-.045, .03+(k%11)*.021, 0); m.castShadow=!LOW; T.g.add(m); T.m.push(m); } }); }
  /* 맞은편 친구 (높은 의자) */
  const OPP={G:new THREE.Group(), P:null, avK:"", t:0, act:0, reach:0, think:0};
  OPP.G.position.set(0,0,-1.35); OPP.G.scale.setScalar(.72); scene.add(OPP.G);
  { const cm=MS(0xff8a3d), cd=MS(0xb0561c); const B=(w,h,d,x,y,z,m)=>{ const q=new THREE.Mesh(GE(new THREE.BoxGeometry(w,h,d)), m); q.position.set(x,y,z); q.castShadow=!LOW; OPP.G.add(q); };
    B(.56,.07,.52,0,.95,0,cm); B(.56,.55,.07,0,1.26,-.24,cm); [[-.23,-.21],[.23,-.21],[-.23,.21],[.23,.21]].forEach(([x,z])=>B(.06,.95,.06,x,.47,z,cd)); B(.5,.04,.04,0,.35,.21,cd); B(.5,.04,.04,0,.35,-.21,cd); }
  function oppAv(av){ const k=JSON.stringify(av||{}); if(OPP.avK===k && OPP.P) return; OPP.avK=k; if(OPP.P){ OPP.G.remove(OPP.P.g); OPP.P=null; }
    try{ const P=buildAvatar(av||{}); P.g.scale.setScalar(1.08); P.g.position.set(0,.78-(typeof AVB!=="undefined"?AVB.leg*1.08:0),-.02);   /* (v660) 다리가 길어진 만큼 내려 앉힘 */  OPP.G.add(P.g); P.legL.rotation.x=P.legR.rotation.x=-1.45; P.armL.rotation.set(-.9,0,.25); P.armR.rotation.set(-.9,0,-.25); P.expr0=(av&&av.expr)||"smile"; OPP.P=P; }catch(e){ console.warn("C4 av", e); }
    if(OPP_POR){ try{ PSc.remove(OPP_POR.g); }catch(e){} OPP_POR=null; } try{ OPP_POR=buildAvatar(av||{}); OPP_POR.g.position.x=6; PSc.add(OPP_POR.g); }catch(e){} }
  /* 얼굴 사진 (HUD) */
  const PSc=new THREE.Scene(); PSc.background=new THREE.Color(0x2b3a5a); PSc.add(new THREE.HemisphereLight(0xffffff,0x445566,.85)); { const l=new THREE.DirectionalLight(0xffffff,.55); l.position.set(.6,1.4,1.4); PSc.add(l); }
  const PCm=new THREE.PerspectiveCamera(26,1,.1,10); PCm.position.set(.05,1.0,1.75); PCm.lookAt(0,.88,0);
  const PCo=new THREE.PerspectiveCamera(26,1,.1,10); PCo.position.set(6.05,1.0,1.75); PCo.lookAt(6,.88,0);
  let ME_AV=null, OPP_POR=null; try{ ME_AV=buildAvatar(api.av||{}); PSc.add(ME_AV.g); }catch(e){}
  /* 이긴 줄 · 꽃가루 */
  let winBar=null; const CONF=[];
  function confetti(n){ const g=GE(new THREE.PlaneGeometry(.04,.065)); for(let i=0;i<n;i++){ const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:[0xff4d5e,0xffd23f,0x3fc46a,0x3ea2ff,0xffffff][i%5],side:THREE.DoubleSide})); disp.push(m.material);
      m.position.set((Math.random()-.5)*2.2, 1.6+Math.random()*1.4, -.6+Math.random()*1.2); m.rotation.set(Math.random()*6,Math.random()*6,0); m.userData.v=.35+Math.random()*.5; m.userData.s=(Math.random()-.5)*4; scene.add(m); CONF.push(m); } }
  function clearFx(){ if(winBar){ board.remove(winBar); winBar=null; } CONF.forEach(m=>scene.remove(m)); CONF.length=0; }
  /* 카메라 (내 자리에서 조금 위 — 판 너머로 친구 얼굴이 보임) */
  const CT=new THREE.Vector3(0, TY+.62, -.45), CD=new THREE.Vector3(0, .5, 1).normalize();
  function fitCam(){ const w=innerWidth, h=innerHeight, asp=w/h; cam.aspect=asp; const land=asp>1.15, needW=land?2.5:1.22, needH=land?1.95:1.7;
    const tv=Math.tan(cam.fov*Math.PI/360), th=tv*asp, d=Math.max(needW/2/th, needH/2/tv); cam.position.copy(CT).addScaledVector(CD, d); cam.lookAt(CT.x, CT.y-(land?0:.08), CT.z); cam.updateProjectionMatrix(); }
  /* ══ 화면 ══ */
  const U=api.ui, R=document.createElement("div"); R.className="c4R"; U.insertBefore(R, U.querySelector(".mgTop"));
  R.innerHTML='<div class="c4Hit"></div><div class="c4Top"><div class="c4P p0"><canvas></canvas><b></b><i></i></div><div class="c4Tm"><span>30</span></div><div class="c4P p1"><canvas></canvas><b></b><i></i></div></div><div class="c4Bub"></div><div class="paBan c4Ban"></div><div class="c4Say"></div><div class="c4Emo"><button>😆</button><button>😮</button><button>👍</button></div><div class="c4Me"></div><div class="c4Menu"></div>';
  ["pointerdown","pointermove","pointerup"].forEach(t=>R.addEventListener(t, e=>e.stopPropagation()));
  const $=s=>R.querySelector(s), HIT=$(".c4Hit"), MENU=$(".c4Menu"), SAY=$(".c4Say"), TMR=$(".c4Tm");
  const say=t=>{ SAY.textContent=t||""; SAY.style.display=t?"":"none"; };
  const BUB=$(".c4Bub"); let bubT=0; const bub=(t,s)=>{ BUB.textContent=t; BUB.classList.remove("on"); void BUB.offsetWidth; BUB.classList.add("on"); bubT=s||1.6; };
  const POR=[...R.querySelectorAll(".c4P canvas")].map(c=>({c, g:c.getContext("2d")}));
  const EMX={"😆":"grin","😮":"wow","👍":"wink"}; let meT=0;
  function myEmo(e, send){ const M=$(".c4Me"); M.textContent=e; M.classList.add("on"); meT=1.6; if(ME_AV) ME_AV.setExpr(EMX[e]||"grin"); try{ SFX.tone(880,.06,"triangle",.04); }catch(_){}
    if(send!==false){ if(opp==="co" && RM) RM.feed({t:"emo", s:RM.code, e}); else if(opp==="bot" && Math.random()<.8) later(.7, ()=>{ const r=["😆","😝","👍","😮"][Math.floor(Math.random()*4)]; bub(r, 1.4); if(OPP.P){ OPP.P.setExpr(EMX[r]||"wink"); OPP.act=1.4; } }); } }
  R.querySelectorAll(".c4Emo button").forEach(b=>b.addEventListener("click", ()=>{ if(mode!=="menu") myEmo(b.textContent); }));
  /* ══ 판 상태 ══ */
  let bd=fresh(), mv=[], first=0, me=0, over=false, win=null, busy=false, opp="bot", lv="normal", names=["나","봇"], turnT=0, hov=-1, RM=null, oppGone=0, coStart=0;
  const turn=()=>(first+mv.length)%2;
  function seats(){ [0,1].forEach(k=>{ const p=k===0?me:1-me, el=$(".c4P.p"+k); el.querySelector("i").style.background=COLS[p]; el.style.setProperty("--c", COLS[p]); el.querySelector("canvas").style.borderColor=COLS[p]; el.querySelector("b").textContent=names[p]; el.classList.toggle("on", !over && turn()===p); }); trays(); const B=$(".c4Ban"), t=over||mode==="menu"?"":turn()===me?"내 차례!":names[1-me]+" 차례"; if(B.textContent!==t){ B.textContent=t; B.style.display=t?"":"none"; B.className="paBan c4Ban pop "+(turn()===me?"":"y"); } }
  function clearDiscs(){ DM.forEach(d=>board.remove(d)); DM.length=0; FALL.length=0; clearFx(); }
  function newGame(o){ bd=fresh(); mv=[]; over=false; win=null; busy=false; clearDiscs(); first=o.first|0; me=o.me|0; opp=o.opp; lv=o.lv||lv; names=o.names; turnT=0; oppGone=0; mode=o.mode; U.classList.remove("c4Menu0"); TMR.style.display=""; oppAv(o.av); oppRest(); if(ME_AV) ME_AV.setExpr("smile"); seats();
    bub(opp==="bot"?["한 판 해요! 😆","내가 이길걸? 😝","잘 부탁해! 👋"][Math.floor(Math.random()*3)]:"반가워! 👋", 1.8);
    busy=true; PUI.count(U, ()=>{ busy=false; turnT=0; if(opp==="bot" && turn()!==me && !over) later(.4, botGo); }, fast);
    say(turn()===me?"칸을 콕! 알 넣기 👆":(opp==="bot"?"생각하는 중…":"친구 차례예요")); }
  function put(c, p, anim){ const r=bd[c].length; if(r>=Rw) return false; bd[c].push(p); mv.push(c); const d=discMesh(p); d.position.set(cx(c), anim?cy(Rw)+.6:cy(r), 0); board.add(d); DM.push(d); d.userData.c=c; d.userData.r=r; if(p!==me){ OPP.reach=.55; OPP.col=c; }
    if(anim) FALL.push({d, y:cy(Rw)+.6, ty:cy(r), v:0, b:0}); else d.position.y=cy(r);
    try{ SFX.tone(p?520:660,.06,"triangle",.04); }catch(e){}
    const w=line4(bd,c,r); if(w){ over=true; win={p, L:w}; later(fast?.02:.55, ()=>finish()); } else if(full(bd)){ over=true; win={p:-1}; later(fast?.02:.4, ()=>finish()); }
    turnT=0; seats(); if(!over){ say(turn()===me?"칸을 콕! 알 넣기 👆":(opp==="bot"?"생각하는 중…":"친구 차례예요")); } return true; }
  function play(c){ if(over || busy || turn()!==me || mode==="menu") return false; if(c<0||c>=C||bd[c].length>=Rw){ try{ SFX.bad(); }catch(e){} return false; }
    const thr=threat(1-me); put(c, me, true); if(!over && thr>=0 && thr!==c) { try{ OPP.P && OPP.P.setExpr("wow"); OPP.act=1.2; }catch(e){} } if(opp==="co" && RM) RM.put("g", {mv:mv.slice(), first, ro:coRo, sq:mv.length}); else if(!over) later(fast?.02:.45, botGo); return true; }
  function threat(p){ for(let c=0;c<C;c++){ if(bd[c].length>=Rw) continue; bd[c].push(p); const w=line4(bd,c,bd[c].length-1); bd[c].pop(); if(w) return c; } return -1; }
  function botGo(){ if(over || opp!=="bot" || turn()===me || gone) return; OPP.think=fast?.02:(.7+Math.random()*.7); if(Math.random()<.45) bub(["🤔","음…","어디 둘까?"][Math.floor(Math.random()*3)], 1); later(OPP.think, botPut); }
  function botPut(){ if(over || opp!=="bot" || turn()===me || gone) return; OPP.think=0; const c=aiMove(bd.map(x=>x.slice()), 1-me, lv); if(c<0) return;
    const b=bd.map(x=>x.slice()); b[c].push(me); const blk=!!line4(b,c,b[c].length-1); put(c, 1-me, true); if(over) return; if(blk) bub("막았다! 😝", 1.6); else if(Math.random()<.15) bub(["여기!","헤헤","좋았어!"][Math.floor(Math.random()*3)], 1.1); }
  function finish(){ if(gone) return; const r=REC(); const res=win.p<0?"draw":win.p===me?"win":"lose";
    if(win.L) win.L.forEach(([c,rr])=>{ const i=DM.findIndex(d=>Math.abs(d.position.x-cx(c))<.01 && Math.abs(d.position.y-cy(rr))<.05); if(i>=0) DM[i].userData.glow=1; });
    if(win.L){ const L=win.L.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1]), a=L[0], b=L[L.length-1], ax=cx(a[0]), ay=cy(a[1]), bx=cx(b[0]), by=cy(b[1]), len=Math.hypot(bx-ax,by-ay)+.9;
      winBar=new THREE.Mesh(GE(new THREE.CylinderGeometry(.12,.12,len,10)), new THREE.MeshBasicMaterial({color:0xffffff, transparent:true, opacity:.85})); disp.push(winBar.material); winBar.position.set((ax+bx)/2,(ay+by)/2,.32); winBar.rotation.z=Math.atan2(by-ay,bx-ax)-Math.PI/2; board.add(winBar); }
    oppReact(res); if(res==="win") confetti(LOW?40:90);
    if(res==="win"){ try{ SFX.win(); }catch(e){} say("🎉 4줄 팡! 이겼어요!"); } else if(res==="lose"){ try{ SFX.bad(); }catch(e){} say(opp==="bot"?"아깝다! 다시 해 봐요":"친구가 이겼어요!"); } else say("비겼어요 🤝");
    const key=opp==="bot"?lv:"co"; r.n++; if(res==="win"){ r.w[key]=(r.w[key]|0)+1; r.s++; r.bs=Math.max(r.bs,r.s); } else if(res==="lose") r.s=0; st("hyeng_proto_c4r", r);
    seats(); TMR.style.display="none";
    later(fast?.05:1.8, ()=>{ if(gone) return; const coins=res==="win"?8:res==="draw"?5:3, B=opp==="bot"?botOf(lv):null, vs=opp==="bot"?LV[lv].ic+" "+B.nm:"👫 "+esc(names[1-me]);
      const stars=res==="win"?((opp!=="bot"||lv==="hard"||mv.length<=16)?3:2):res==="draw"?1:0, tw=Object.values(r.w).reduce((a,b)=>a+(b|0),0);
      const got=PUI.award(api, {title:res==="win"?"이겼어요!":res==="draw"?"비겼어요":"졌어요", sub:"4줄 팡 · "+vs, rows:null, coins, again:opp==="bot"?{go:lv}:{}, upd:(b,t)=>{ if(res==="win") t.win=(t.win|0)+1; if(opp==="co") t.co=(t.co|0)+1; }});
      const left=MG.payLeft("c4");
      PUI.result(U, {res, stars, title:res==="win"?"이겼어요!":res==="draw"?"비겼어요!":"아깝다!", sub:vs+(res==="win"?"를 ":"와 ")+mv.length+"수 만에 "+(res==="win"?"이겼어요":res==="draw"?"비겼어요":"졌어요 — 다시 해 봐요!"), av:api.av,
        rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"],["fire", r.s, "연승", res==="win" && r.s>=r.bs && r.s>1],["trophy", tw, "이긴 판"]],
        prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3}, onAgain:()=>api.restart(opp==="bot"?{go:lv}:{}), onMenu:()=>api.restart({}), onOut:()=>MG.exit()});
      try{ if(RM){ RM.dispose(); RM=null; } }catch(e){} }); }
  /* ── 칸 고르기 (화면 x → 칸) ── */
  const v3=new THREE.Vector3();
  function colAt(px){ const r=HIT.getBoundingClientRect(); const sx=c=>{ v3.set(cx(c),cy(Rw/2),0); board.localToWorld(v3); v3.project(cam); return (v3.x+1)/2*r.width+r.left; }; const x0=sx(0), x1=sx(C-1), w=(x1-x0)/(C-1); const c=Math.round((px-x0)/w); return (c<0||c>=C||px<x0-w*.8||px>x1+w*.8)?-1:c; }
  HIT.addEventListener("pointermove", e=>{ hov=colAt(e.clientX); });
  HIT.addEventListener("pointerdown", e=>{ e.preventDefault(); hov=colAt(e.clientX); });
  HIT.addEventListener("pointerup", e=>{ const c=colAt(e.clientX); if(c>=0) play(c); hov=e.pointerType==="mouse"?c:-1; });
  const onKey=e=>{ if(/^[1-7]$/.test(e.key)) play(+e.key-1); };
  window.addEventListener("keydown", onKey);
  /* ══ 메뉴 ══ */
  function menuShow(){ mode="menu"; U.classList.add("c4Menu0"); over=true; clearDiscs(); bd=fresh(); TMR.style.display="none"; say(""); const r=REC(), tw=Object.values(r.w).reduce((a,b)=>a+(b|0),0);
    PUI.menu(U, {title:"4줄 팡!", sub:"알 4개를 먼저 이으면 이겨요", av:api.av, nick:api.nick, stats:[["trophy",tw,"이긴 판"],["fire",r.bs,"최고 연승"]],
      deco:[["🔴","left:calc(50% - 130px);top:20%;transform:rotate(-14deg)"],["🟡","left:calc(50% - 104px);top:52%;font-size:30px"]],
      tiles:Object.keys(LV).map((k,i)=>{ const B=botOf(k); return {k, pic:PUI.av(B.av,"bust"), bg:["#bfe6ff","#ffe08a","#ffc2d6"][i], nm:B.nm, sub:LV[k].nm+" · 이김 "+(r.w[k]|0), bd:"★".repeat(i+1)}; }),
      primary:{k:"co", label:"친구랑 1:1", ic:"swords"}, pay:MG.payLeft("c4"), onPick:k=>menuGo(k)}); }
  function menuGo(k){ PUI.menuHide(U); try{ SFX.tone(660,.06,"triangle",.04); }catch(e){} if(k==="co"){ startCo(); return; } const f=Math.random()<.5?0:1, B=botOf(k); newGame({mode:"bot", opp:"bot", lv:k, first:f, me:0, names:[String(api.nick||"나"), B.nm], av:B.av}); }
  function botOf(k){ const L=(window.CPA&&CPA.BOTS)||[], i={easy:0,normal:1,hard:2}[k]|0; return L[i]||{nm:"봇", av:{}}; }
  /* ══ 👫 친구랑 1:1 ══ */
  let coRo=[], lastSq=-1;
  function startCo(){ mode="co"; PUI.menuHide(U); say(""); U.classList.add("c4Menu0");
    RM=MG.room(api, {pre:"mgf", title:"4줄 팡 1:1", ic:"🔴", max:2, fill:false, wait:4000, send:.5, poll:.3, back:()=>{ try{ RM.dispose(); }catch(e){} RM=null; menuShow(); }}); RM.node=()=>({av:api.av||null}); RM.onFeed=f=>{ if(f && f.t==="emo" && f.s!==RM.code){ bub(f.e, 1.5); if(OPP.P){ OPP.P.setExpr(EMX[f.e]||"grin"); OPP.act=1.5; } } };
    { const st0=RM.start; RM.start=async()=>{ const L=RM.live(true).map(p=>p.k); if(L.length<2){ api.msg("친구가 들어오면 시작할 수 있어요 👫", 1500); return; } try{ await NET.patch(RM.path+"/h", {ro:L.slice(0,2)}); }catch(e){} if(RM.d && RM.d.h) RM.d.h.ro=L.slice(0,2); return st0(); }; }
    RM.onStart=(h, L)=>{ coRo=(h.ro&&h.ro.length?h.ro:L.map(p=>p.k)).slice(0,2); const PD=(RM.d&&RM.d.p)||{}; const nm=coRo.map(c=>String((PD[c]&&PD[c].n)||(L.find(q=>q.k===c)||{}).n||"친구").slice(0,8));
      lastSq=-1; coStart=now(); const mi=Math.max(0,coRo.indexOf(RM.code)), oc=coRo[1-mi]; newGame({mode:"co-play", opp:"co", first:(h.seed|0)%2, me:mi, names:nm, av:(PD[oc]&&PD[oc].av)||{}}); }; }
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
    const tg=performance.now()/1000; DM.forEach(d=>{ if(d.userData.glow){ const s=1+Math.sin(tg*8)*.12; d.scale.set(s,s,1); } }); if(winBar) winBar.material.opacity=.55+Math.sin(tg*10)*.3;
    for(const m of CONF){ m.position.y-=m.userData.v*dt; m.rotation.x+=m.userData.s*dt; m.rotation.y+=dt*2; if(m.position.y<TY+.01 && Math.abs(m.position.x)<1.05 && m.position.z>-.9 && m.position.z<.4) m.position.y=TY+.01; else if(m.position.y<.01) m.position.y=.01; }
    if(meT>0){ meT-=dt; if(meT<=0){ $(".c4Me").classList.remove("on"); if(ME_AV && !over) ME_AV.setExpr("smile"); } } oppTick(dt); if(bubT>0){ bubT-=dt; if(bubT<=0) BUB.classList.remove("on"); } }
  /* 맞은편 친구 움직임 */
  function oppRest(){ const P=OPP.P; if(!P) return; P.armL.rotation.set(-.9,0,.25); P.armR.rotation.set(-.9,0,-.25); P.head.rotation.set(0,0,0); P.g.position.y=.78; OPP.act=0; OPP.reach=0; OPP.think=0; P.setExpr(P.expr0||"smile"); }
  function oppReact(res){ const P=OPP.P; if(!P) return; OPP.act=99; if(res==="lose"){ P.armL.rotation.set(-2.7,0,.4); P.armR.rotation.set(-2.7,0,-.4); P.setExpr("grin"); bub(opp==="bot"?"이겼다! 🎉":"🎉", 2.5); } else if(res==="win"){ P.armL.rotation.set(-1.3,0,-.35); P.armR.rotation.set(-1.3,0,.35); P.setExpr("wow"); P.head.rotation.x=.25; bub(opp==="bot"?"와… 졌다! 👏":"👏", 2.5); } else { P.setExpr("wink"); bub("비겼다! 🤝", 2); }
    if(ME_AV) ME_AV.setExpr(res==="win"?"grin":res==="lose"?"wow":"wink"); }
  const hv=new THREE.Vector3();
  function oppTick(dt){ const P=OPP.P; if(!P) return; OPP.t+=dt; const t=OPP.t; if(OPP.act<90){ P.g.position.y=.78+(OPP.think>0?Math.abs(Math.sin(t*5))*.02:Math.sin(t*1.6)*.006);
      if(OPP.reach>0){ OPP.reach-=dt; const k=Math.min(1,OPP.reach/.25); P.armR.rotation.set(-.9-1.6*k,0,-.25+(OPP.col-3)*.06*k); P.head.rotation.x=-.15*k; }
      else if(OPP.think>0){ P.head.rotation.set(-.1, Math.sin(t*2.2)*.3, Math.sin(t*1.6)*.12); P.armR.rotation.set(-1.9,0,-.6); P.armL.rotation.set(-.9,0,.25); }
      else { P.armR.rotation.set(-.9,0,-.25); const lc=hov>=0&&turn()===me?hov:3; P.head.rotation.set(-.12, (lc-3)*-.08+Math.sin(t*.7)*.05, 0); }
      if(OPP.act>0){ OPP.act-=dt; if(OPP.act<=0) P.setExpr(P.expr0||"smile"); } }
    if(BUB.classList.contains("on")){ P.head.getWorldPosition(hv); hv.y+=.32; hv.project(cam); BUB.style.left=((hv.x+1)/2*innerWidth)+"px"; BUB.style.top=((1-hv.y)/2*innerHeight)+"px"; } }
  let fr=0;
  function render(rn){ fr++; fitCam(); if(mode!=="menu" && fr%8===1){ [[ME_AV,PCm,0],[OPP_POR,PCo,1]].forEach(([A,PC,k])=>{ const o=POR[k]; if(!A || !o) return; const r=o.c.getBoundingClientRect(), pr=rn.getPixelRatio(), sz=Math.max(8,Math.round(r.width)); if(o.c.width!==Math.round(sz*pr)) o.c.width=o.c.height=Math.round(sz*pr);
      try{ rn.setScissorTest(true); rn.setScissor(0,0,sz,sz); rn.setViewport(0,0,sz,sz); rn.render(PSc,PC); o.g.clearRect(0,0,o.c.width,o.c.height); o.g.drawImage(rn.domElement,0,rn.domElement.height-o.c.height,o.c.width,o.c.height,0,0,o.c.width,o.c.height); }catch(e){}
      rn.setScissorTest(false); const c=rn.domElement; rn.setViewport(0,0,c.width/rn.getPixelRatio(),c.height/rn.getPixelRatio()); }); }
    MG.draw(scene, cam); }
  function dispose(){ gone=true; TM.length=0; window.removeEventListener("keydown", onKey); try{ if(RM) RM.dispose(); }catch(e){} RM=null; try{ R.remove(); }catch(e){} disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); }
  fitCam(); oppAv(botOf("normal").av); trays(); const O=api.opt||{}; if(O.go && LV[O.go]) menuGo(O.go); else menuShow(); ready=true;
  return {scene, cam, tick, render, dispose, pause:v=>{ paused=!!v; },
    get mode(){ return mode; }, get bd(){ return bd; }, get mv(){ return mv; }, get turn(){ return turn(); }, get me(){ return me; }, get over(){ return over; }, get win(){ return win; }, get ready(){ return ready; }, get RM(){ return RM; }, get falling(){ return FALL.length; }, get board(){ return board; }, get opp(){ return OPP; },
    set fast(v){ fast=v?1:0; }, play, menuGo, menuShow, ai:(l,p)=>aiMove(bd.map(x=>x.slice()), p==null?me:p, l||"normal"), colAt, aiMove, line4 };
}
MG.reg("c4", {ic:"🔴", nm:"4줄 팡", tag:"알 4개를 먼저 이어요 · 봇 3단계 · 친구랑 1:1", bg:"linear-gradient(135deg,#3b6cff,#ff4d5e 60%,#ffd23f)", big:"🔴🟡", menu:true,
  how:[["🔴","알을 떨어뜨려 4개를 이어요"],["👫","친구랑 1:1"]], payTxt:"이김 🪙8 · 비김 5 · 짐 3",
  bestTxt:(b,t)=>'🏆 이긴 판 '+(t.win|0), ui:{look:false, btns:[]}, start});
})();
