/* ═════════ 🎳🎯 볼링 · 다트 — 🎡 놀이 섬 볼링장
   (v638) 사용자: 「5번은 한 번씩 좋다」 = 한 건물에서 🎳 볼링 · 🎯 다트 하나 골라 한 판
   · 🎳 볼링 5프레임: 레인을 위로 쓱 밀면(빠르기 · 방향) 굴러감 · 콕 누르면 그쪽으로 · 🛡 범퍼(도랑 막기) 켜고 끄기
       핀끼리 부딪혀 넘어짐(원 충돌) · 스트라이크 X · 스페어 / · 점수 = 진짜 볼링 셈(5프레임)
   · 🎯 다트 3라운드 × 3개: 손가락으로 조준점을 옮기고 떼면 던짐(조준점이 살짝 흔들림) · 트리플 · 더블 · 불
       맞힌 숫자는 영어로 (triple twenty! → 60) — 숫자 영어 말하기 연습
   · 상: MG 공통 하루 3판 🪙 (볼링 40/70/100 · 다트 90/180/300 넘으면 5/7/9 · 그 밑 3)
   시험 손잡이: MG.run.mode · .bw(볼링 상태) · .dt(다트 상태) · .throwBall(x, vx, vz) · .dart(x, y) · .fast · .menuGo(k) · .ready · .score */
(function(){
"use strict";
if(!window.MG) return;
const st=(k,v)=>{ try{ return typeof store==="function" ? store(k,v) : (v===undefined?JSON.parse(localStorage.getItem(k)||"null"):localStorage.setItem(k,JSON.stringify(v))); }catch(e){ return null; } };
const sayW=w=>{ try{ say(w); }catch(e){} };
const NUMW=["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen","twenty"];
const SEG=[20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5];
const NF=5;
/* 볼링 점수 (NF 프레임) → [프레임별 누계(null=아직)] · 표시 글자 */
function bowlScore(rolls){ const out=[], marks=[]; let i=0, tot=0;
  for(let f=0;f<NF;f++){ const last=f===NF-1, a=rolls[i], b=rolls[i+1], c=rolls[i+2];
    if(a===undefined){ out.push(null); marks.push([]); continue; }
    if(!last){ if(a===10){ marks.push(["X"]); if(b!==undefined && c!==undefined){ tot+=10+b+c; out.push(tot); } else out.push(null); i+=1; }
      else { marks.push([a===0?"-":String(a), b===undefined?"":(a+b===10?"/":b===0?"-":String(b))]); if(b===undefined){ out.push(null); i+=1; continue; } if(a+b===10){ if(c!==undefined){ tot+=10+c; out.push(tot); } else out.push(null); } else { tot+=a+b; out.push(tot); } i+=2; } }
    else { const m=[]; const r=[a,b,c].filter(x=>x!==undefined); let pinsLeft=10;
      r.forEach((x,k)=>{ if(x===10 && pinsLeft===10){ m.push("X"); pinsLeft=10; } else if(pinsLeft<10 && x===pinsLeft){ m.push("/"); pinsLeft=10; } else { m.push(x===0?"-":String(x)); pinsLeft=pinsLeft===10?10-x:10; } });
      marks.push(m); const need=(a===10 || (b!==undefined && a+b===10))?3:2; if(r.length>=need){ tot+=r.slice(0,need).reduce((s,x)=>s+x,0); out.push(tot); } else out.push(null); i+=3; } }
  return {out, marks, total:tot}; }
function bowlDone(rolls){ let i=0; for(let f=0;f<NF-1;f++){ if(rolls[i]===undefined) return false; i+=rolls[i]===10?1:2; } const r=rolls.slice(i); if(r.length<2) return false; if(r[0]===10 || r[0]+r[1]===10) return r.length>=3; return true; }
function rollsInFrame(rolls){ /* 지금 프레임에서 몇 번째 굴림인지 · 핀을 새로 세울지 */ let i=0, f=0; while(f<NF-1){ if(i>=rolls.length) return {f, k:0, reset:true}; if(rolls[i]===10){ i++; f++; continue; } if(i+1>=rolls.length) return {f, k:1, reset:false}; i+=2; f++; }
  const r=rolls.slice(i), k=r.length; let reset=true; if(k===1) reset=r[0]===10; else if(k===2) reset=(r[0]===10&&r[1]===10)||(r[0]!==10&&r[0]+r[1]===10)||(r[0]===10&&false); if(k===2 && r[0]===10 && r[1]<10) reset=false; return {f:NF-1, k, reset:k===0?true:reset}; }

function css(){ if(document.getElementById("spCss")) return; const s=document.createElement("style"); s.id="spCss"; s.textContent=`
#mgUI .spR{position:absolute;inset:0;pointer-events:none;font-family:var(--kr);color:#fff} #mgUI.spOn .mgJoyH,#mgUI.spOn .mgJoy{display:none!important}
#mgUI .spHit{position:absolute;inset:0;pointer-events:auto;touch-action:none}
#mgUI .spSc{position:absolute;left:50%;top:calc(56px + env(safe-area-inset-top));transform:translateX(-50%);display:flex;gap:3px;pointer-events:none;background:rgba(14,20,50,.72);border-radius:14px;padding:5px;max-width:96vw}
#mgUI .spSc div{width:54px;background:#fff;color:#1d2450;border-radius:8px;text-align:center;font-family:var(--en);font-weight:900;overflow:hidden}
#mgUI .spSc div.cur{box-shadow:0 0 0 3px #ffe14d}
#mgUI .spSc div small{display:block;background:#1d2450;color:#fff;font-size:10px;font-weight:700;padding:1px 0}
#mgUI .spSc div .m{display:flex;justify-content:flex-end;gap:4px;font-size:13px;min-height:18px;padding:1px 3px} #mgUI .spSc div .m span{min-width:12px} #mgUI .spSc div .t{font-size:17px;min-height:22px}
#mgUI .spSc div.tot{width:64px;background:#ffe14d}
#mgUI .spBig{position:absolute;left:50%;top:38%;transform:translate(-50%,-50%) scale(.6);opacity:0;font-family:var(--en);font-weight:900;font-size:58px;text-shadow:0 4px 0 #c8213a,0 0 24px rgba(255,90,95,.6);transition:all .25s;pointer-events:none;white-space:nowrap;text-align:center}
#mgUI .spBig.on{opacity:1;transform:translate(-50%,-50%) scale(1)} #mgUI .spBig small{display:block;font-size:22px;font-family:var(--kr);font-weight:400;text-shadow:0 2px 0 rgba(0,0,0,.4)}
#mgUI .spSay{position:absolute;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translateX(-50%);background:rgba(14,20,50,.72);border-radius:16px;padding:8px 16px;font-size:16.5px;white-space:nowrap;pointer-events:none}
#mgUI .spBtn{position:absolute;right:calc(14px + env(safe-area-inset-right));bottom:calc(74px + env(safe-area-inset-bottom));pointer-events:auto;font:inherit;border:0;border-radius:14px;padding:8px 12px;min-height:44px;background:rgba(14,20,50,.62);color:#fff;font-size:14.5px}
#mgUI .spAim{position:absolute;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 2px rgba(0,0,0,.4),inset 0 0 0 2px rgba(0,0,0,.3);pointer-events:none;display:none}
#mgUI .spAim::before,#mgUI .spAim::after{content:"";position:absolute;background:#ff4d5e;left:50%;top:50%} #mgUI .spAim::before{width:2px;height:56px;margin:-28px 0 0 -1px} #mgUI .spAim::after{height:2px;width:56px;margin:-1px 0 0 -28px}
#mgUI .spMenu{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:12px;pointer-events:auto;padding:calc(60px + env(safe-area-inset-top)) 16px calc(16px + env(safe-area-inset-bottom));background:rgba(20,16,50,.55)}
#mgUI .spMenu.on{display:flex} #mgUI .spMenu h2{margin:0;font-weight:400;font-size:32px;text-shadow:0 3px 0 rgba(0,0,0,.3)} #mgUI .spMenu .sub{font-size:14px;opacity:.9;text-align:center}
#mgUI .spMenu .g{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:min(100%,460px)}
#mgUI .spMenu .g button{font:inherit;border:0;border-radius:20px;background:#fff;color:#1d2450;box-shadow:0 5px 0 #9aa6d8;padding:12px 8px;min-height:150px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-size:20px}
#mgUI .spMenu .g button .e{font-size:54px} #mgUI .spMenu .g button small{font-size:12.5px;opacity:.7}
#mgUI .spMenu .g button:active{transform:translateY(4px);box-shadow:0 1px 0 #9aa6d8}
#mgUI .spMenu .tg{font:inherit;border:0;border-radius:14px;padding:8px 14px;min-height:44px;background:rgba(255,255,255,.2);color:#fff;font-size:15px} #mgUI .spMenu .tg.on{background:#3fc46a}
#mgUI .spMenu .out{font:inherit;border:0;border-radius:14px;padding:9px 20px;min-height:44px;background:rgba(255,255,255,.18);color:#fff;font-size:15px}
@media (orientation:landscape) and (max-height:620px){ #mgUI .spSc{top:calc(8px + env(safe-area-inset-top))} #mgUI .spMenu .g button{min-height:110px} }`; document.head.appendChild(s); }

function start(api){
  const SFX=api.sfx, LOW=!!api.low; api.menu=true; css(); api.ui.classList.add("spOn");
  let gone=false, paused=false, fast=0, mode="menu", ready=false;
  const SET=Object.assign({bump:1}, st("hyeng_proto_spset")||{});
  const REC=()=>Object.assign({bw:0, dt:0, strikes:0, bulls:0}, st("hyeng_proto_spr")||{});
  const TM=[]; const later=(s,fn)=>TM.push({t:fast?Math.min(s,.03):s, fn});
  /* ══ 3D ══ */
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x2a2150); scene.fog=new THREE.Fog(0x2a2150, 30, 60);
  const cam=new THREE.PerspectiveCamera(50, 1, .05, 60);
  scene.add(new THREE.HemisphereLight(0xfff0ff, 0x3a2a60, .7)); const sun=new THREE.DirectionalLight(0xffffff,.7); sun.position.set(2,8,4); scene.add(sun);
  if(!LOW){ sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); Object.assign(sun.shadow.camera,{left:-4,right:4,top:4,bottom:-18,near:1,far:30}); }
  const disp=[]; const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const MS=(c,o)=>{ const m=toon(new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.6},o||{}))); disp.push(m); return m; };
  const GE=g=>{ disp.push(g); return g; };
  function tex(w,h,draw){ const c=document.createElement("canvas"); c.width=w; c.height=h; draw(c.getContext("2d"),w,h); const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding; t.anisotropy=4; disp.push(t); return t; }
  /* ── 볼링 레인 ── */
  const BOWL=new THREE.Group(); scene.add(BOWL);
  const LW=2.0, LZ=-12.5, HZ=-10.3, BR=.24, PR=.12;
  { const lt=tex(128,1024,(g,w,h)=>{ for(let i=0;i<16;i++){ g.fillStyle=i%2?"#e8b77a":"#dfa968"; g.fillRect(i*8,0,8,h); } g.fillStyle="rgba(255,255,255,.18)"; g.fillRect(0,0,w,h*.6);
      g.fillStyle="#ff4d5e"; [-2,-1,0,1,2].forEach(k=>{ const x=w/2+k*16, y=h*.8; g.beginPath(); g.moveTo(x,y-18); g.lineTo(x-6,y); g.lineTo(x+6,y); g.fill(); }); g.fillStyle="#3ea2ff"; for(let k=-4;k<=4;k++) { g.beginPath(); g.arc(w/2+k*12, h*.93, 3, 0, 7); g.fill(); } g.fillStyle="#2b2233"; g.fillRect(0,h-6,w,6); });
    const lane=new THREE.Mesh(GE(new THREE.PlaneGeometry(LW, -LZ+1)), MS(0xffffff,{map:lt, roughness:.35})); lane.rotation.x=-Math.PI/2; lane.position.set(0,0,LZ/2+.5); lane.receiveShadow=true; BOWL.add(lane);
    const gm=MS(0x3b3366); [-1,1].forEach(s=>{ const gt=new THREE.Mesh(GE(new THREE.BoxGeometry(.32,.04,-LZ+1)), gm); gt.position.set(s*(LW/2+.16),-.06,LZ/2+.5); BOWL.add(gt); const wall=new THREE.Mesh(GE(new THREE.BoxGeometry(.18,.5,-LZ+1)), MS(0x6a4fd0)); wall.position.set(s*(LW/2+.41),.2,LZ/2+.5); wall.castShadow=true; BOWL.add(wall); });
    const pit=new THREE.Mesh(GE(new THREE.BoxGeometry(LW+1.2,2.4,.3)), MS(0x1d1640)); pit.position.set(0,1,LZ-.4); BOWL.add(pit);
    const sign=new THREE.Mesh(GE(new THREE.PlaneGeometry(4,1.1)), new THREE.MeshBasicMaterial({map:tex(512,140,(g,w,h)=>{ g.fillStyle="#1d1640"; g.fillRect(0,0,w,h); g.font="900 84px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; "BOWLING".split("").forEach((ch,i)=>{ g.fillStyle=["#ff4d5e","#ffd23f","#3fc46a","#3ea2ff","#ff5ce1","#ff9a3d","#3dff9a"][i]; g.fillText(ch,46+i*70,h/2+4); }); })})); disp.push(sign.material); sign.position.set(0,2.6,LZ-.2); BOWL.add(sign);
    const floor=new THREE.Mesh(GE(new THREE.PlaneGeometry(14,30)), MS(0x3a2a6a)); floor.rotation.x=-Math.PI/2; floor.position.set(0,-.08,-8); floor.receiveShadow=true; BOWL.add(floor);
    /* (개선) 네온 볼링장: 뒤쪽 우주 무늬 카펫 · 옆 레인 2개(핀 서 있음) · 천장 네온 줄 · 공 돌아오는 기계 · 의자 · 옆 벽 별빛 */
    const ct=tex(256,256,(g,w,h)=>{ g.fillStyle="#24164f"; g.fillRect(0,0,w,h); const C=["#ff5ce1","#3dff9a","#ffd23f","#3ea2ff"]; for(let i=0;i<46;i++){ g.fillStyle=C[i%4]; const x=(i*53)%w, y=(i*97)%h; if(i%3===0){ g.beginPath(); g.arc(x,y,5,0,7); g.fill(); } else if(i%3===1){ g.fillRect(x,y,10,3); } else { g.beginPath(); g.moveTo(x,y-6); g.lineTo(x+5,y+4); g.lineTo(x-5,y+4); g.fill(); } } });
    ct.wrapS=ct.wrapT=THREE.RepeatWrapping; ct.repeat.set(4,2); const cp=new THREE.Mesh(GE(new THREE.PlaneGeometry(14,5)), MS(0xffffff,{map:ct, roughness:.95})); cp.rotation.x=-Math.PI/2; cp.position.set(0,-.07,3.2); cp.receiveShadow=true; BOWL.add(cp);
    const foul=new THREE.Mesh(GE(new THREE.BoxGeometry(LW+.8,.02,.06)), new THREE.MeshBasicMaterial({color:0xff3b5c})); disp.push(foul.material); foul.position.set(0,.01,.55); BOWL.add(foul);
    const laneM=MS(0xffffff,{map:lt, roughness:.35});
    [-3.1,3.1].forEach(x=>{ const l2=new THREE.Mesh(GE(new THREE.PlaneGeometry(LW, -LZ+1)), laneM); l2.rotation.x=-Math.PI/2; l2.position.set(x,0,LZ/2+.5); l2.receiveShadow=true; BOWL.add(l2);
      const pit2=new THREE.Mesh(GE(new THREE.BoxGeometry(LW+1.2,2.4,.3)), MS(0x1d1640)); pit2.position.set(x,1,LZ-.4); BOWL.add(pit2); });
    const NC=[0xff5ce1,0x3dff9a,0x3ea2ff,0xffd23f]; for(let i=0;i<9;i++){ const nm=new THREE.MeshBasicMaterial({color:NC[i%4]}); disp.push(nm); const n=new THREE.Mesh(GE(new THREE.BoxGeometry(6.8,.05,.05)), nm); n.position.set(0,3.9,1.5-i*1.6); BOWL.add(n); }
    [-1.55,1.55].forEach(x=>{ const nm=new THREE.MeshBasicMaterial({color:x<0?0xff5ce1:0x3ea2ff}); disp.push(nm); const n=new THREE.Mesh(GE(new THREE.BoxGeometry(.05,.05,-LZ+2)), nm); n.position.set(x,3.85,LZ/2); BOWL.add(n); });
    const rt=new THREE.Group(); rt.position.set(1.85,0,1.5); BOWL.add(rt); { const b=new THREE.Mesh(GE(new THREE.BoxGeometry(.7,.55,1.1)), MS(0x5b3aff)); b.position.y=.28; rt.add(b); const hood=new THREE.Mesh(GE(new THREE.SphereGeometry(.38,16,10,0,Math.PI*2,0,Math.PI/2)), MS(0x9ad8ff,{transparent:true,opacity:.6})); hood.position.set(0,.55,-.2); rt.add(hood);
      [[0xff5ce1,-.15],[0x3dff9a,.15],[0xffd23f,.42]].forEach(([c,z])=>{ const bb=new THREE.Mesh(GE(new THREE.SphereGeometry(.15,14,10)), MS(c,{roughness:.2})); bb.position.set(0,.66,z); rt.add(bb); }); }
    [-2.2,2.6].forEach((x,i)=>{ const sg=new THREE.Group(); sg.position.set(x,0,3.0); BOWL.add(sg); const c=MS(i?0x3ea2ff:0xff5ce1); const s1=new THREE.Mesh(GE(new THREE.BoxGeometry(1.4,.4,.5)), c); s1.position.y=.3; sg.add(s1); const s2=new THREE.Mesh(GE(new THREE.BoxGeometry(1.4,.6,.15)), c); s2.position.set(0,.7,.25); sg.add(s2); }); }
  /* 점수 전광판 (레인 끝 위) */
  const monC=document.createElement("canvas"); monC.width=512; monC.height=160; const monG=monC.getContext("2d"); const monT=new THREE.CanvasTexture(monC); monT.encoding=THREE.sRGBEncoding; disp.push(monT);
  { const mm=new THREE.MeshBasicMaterial({map:monT}); disp.push(mm); const mon=new THREE.Mesh(GE(new THREE.PlaneGeometry(3.2,1.0)), mm); mon.position.set(0,3.0,LZ+.2); BOWL.add(mon); const fr=new THREE.Mesh(GE(new THREE.BoxGeometry(3.35,1.15,.08)), MS(0x111122)); fr.position.set(0,3.0,LZ+.15); BOWL.add(fr); }
  function monPaint(big){ const g=monG, w=512, h=160; g.fillStyle="#08061a"; g.fillRect(0,0,w,h); g.fillStyle="rgba(255,255,255,.05)"; for(let y=0;y<h;y+=4) g.fillRect(0,y,w,2);
    if(big){ g.font="900 92px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillStyle=big==="STRIKE!"?"#ffd23f":big==="SPARE!"?"#3dff9a":"#ff5ce1"; g.shadowColor=g.fillStyle; g.shadowBlur=24; g.fillText(big,w/2,h/2+6); g.shadowBlur=0; }
    else { const sc=bowlScore(BW.rolls); g.font="bold 22px sans-serif"; g.textAlign="center"; for(let i=0;i<NF;i++){ const x=14+i*84; g.strokeStyle="#3ea2ff"; g.lineWidth=2; g.strokeRect(x,22,78,110); g.fillStyle="#9ad8ff"; g.fillText(i+1,x+39,44); g.fillStyle="#fff"; g.fillText((sc.marks[i]||[]).join(" "),x+39,76); g.fillStyle="#ffd23f"; g.font="bold 28px sans-serif"; g.fillText(sc.out[i]==null?"":sc.out[i],x+39,118); g.font="bold 22px sans-serif"; }
      g.fillStyle="#ff5ce1"; g.font="900 40px sans-serif"; g.fillText(sc.total, 470, 92); }
    monT.needsUpdate=true; }
  const BUMP=[]; [-1,1].forEach(s=>{ const b=new THREE.Mesh(GE(new THREE.CylinderGeometry(.08,.08,-LZ-1,10)), MS(0xff5ce1,{emissive:0x551144})); b.rotation.x=Math.PI/2; b.position.set(s*(LW/2+.06),.1,LZ/2); BOWL.add(b); BUMP.push(b); });
  /* 핀 */
  const pinGeo=(()=>{ const pts=[[0,0],[.07,0],[.11,.08],[.12,.22],[.1,.36],[.055,.47],[.05,.52],[.065,.6],[.07,.66],[.05,.72],[0,.75]].map(([x,y])=>new THREE.Vector2(x,y)); return GE(new THREE.LatheGeometry(pts,16)); })();
  const pinM=MS(0xfffaf2,{roughness:.3}), stripeM=MS(0xff4d5e), stG=GE(new THREE.CylinderGeometry(.056,.054,.05,16));
  const PINS=[]; for(let k=0;k<4;k++) for(let i=0;i<=k;i++){ const g=new THREE.Group(); const m=new THREE.Mesh(pinGeo,pinM); m.castShadow=!LOW; g.add(m); const s1=new THREE.Mesh(stG,stripeM); s1.position.y=.55; g.add(s1); const s2=s1.clone(); s2.position.y=.62; g.add(s2); BOWL.add(g); PINS.push({g, hx:(i-k/2)*.5, hz:HZ-k*.45, x:0,z:0,vx:0,vz:0, down:false, up:true, tilt:0, ta:0}); }
  [-3.1,3.1].forEach(x=>{ for(let k=0;k<4;k++) for(let i=0;i<=k;i++){ const m=new THREE.Mesh(pinGeo,pinM); m.position.set(x+(i-k/2)*.5,0,HZ-k*.45); BOWL.add(m); } });   /* 옆 레인 핀 */
  const ball=new THREE.Mesh(GE(new THREE.SphereGeometry(BR,28,20)), MS(0x5b3aff,{roughness:.2, map:tex(256,128,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,w,h); gr.addColorStop(0,"#ff5ce1"); gr.addColorStop(.5,"#5b3aff"); gr.addColorStop(1,"#3ea2ff"); g.fillStyle=gr; g.fillRect(0,0,w,h); g.fillStyle="#1d1640"; [[100,40],[124,36],[112,62]].forEach(([x,y])=>{ g.beginPath(); g.arc(x,y,7,0,7); g.fill(); }); g.fillStyle="#fff"; g.font="bold 30px sans-serif"; g.fillText("★",30,80); })}));
  ball.castShadow=!LOW; BOWL.add(ball);
  /* (개선) 내 캐릭터 (공 오른쪽 · 등이 보이게) · 굴리는 팔 동작 · 겨냥 점선 · 꽃가루 */
  let MEAV=null; try{ MEAV=buildAvatar(api.av||{}); MEAV.g.rotation.y=Math.PI; MEAV.g.scale.setScalar(.78); BOWL.add(MEAV.g); MEAV.armR.rotation.set(.2,0,0); }catch(e){}
  const AV={sw:0, cheer:0, sad:0, t:0};
  const guide=new THREE.Group(); BOWL.add(guide); { const gm=new THREE.MeshBasicMaterial({color:0xffe14d, transparent:true, opacity:.75}); disp.push(gm); const gg=GE(new THREE.CircleGeometry(.07,12)); for(let i=0;i<14;i++){ const d=new THREE.Mesh(gg,gm); d.rotation.x=-Math.PI/2; guide.add(d); } } guide.visible=false;
  function guideTo(tx, tz){ const n=guide.children.length; guide.children.forEach((d,i)=>{ const t=(i+1)/n; d.position.set(BW.bx+(tx-BW.bx)*t, .02, .3+(tz-.3)*t); }); guide.visible=true; }
  const CONF=[]; function confetti(x,y,z,n){ const g=GE(new THREE.PlaneGeometry(.09,.14)); for(let i=0;i<n;i++){ const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:[0xff5ce1,0xffd23f,0x3dff9a,0x3ea2ff,0xffffff][i%5],side:THREE.DoubleSide})); disp.push(m.material);
      const a=Math.random()*Math.PI*2, sp=1+Math.random()*2.5; m.position.set(x,y,z); m.userData={vx:Math.cos(a)*sp, vy:2+Math.random()*3, vz:Math.sin(a)*sp*.6, s:(Math.random()-.5)*8, life:2.4}; scene.add(m); CONF.push(m); } }
  function confStep(dt){ for(let i=CONF.length-1;i>=0;i--){ const m=CONF[i], u=m.userData; u.vy-=4*dt; u.vx*=1-dt; m.position.x+=u.vx*dt; m.position.y+=u.vy*dt; m.position.z+=u.vz*dt; m.rotation.x+=u.s*dt; m.rotation.y+=dt*3; u.life-=dt; if(u.life<=0 || m.position.y<0){ scene.remove(m); CONF.splice(i,1); } } }
  function avStep(dt){ if(!MEAV) return; AV.t+=dt; const P=MEAV; P.g.position.set(Math.max(-.55,Math.min(.95,BW.bx+.55)), 0, 1.05);
    if(AV.sw>0){ AV.sw=Math.max(0,AV.sw-dt); const k=AV.sw/.55; P.armR.rotation.set(-1.5+2.6*k*k,0,0); P.body.rotation.x=.18*(1-k); }
    else if(AV.cheer>0){ AV.cheer-=dt; P.armL.rotation.set(-2.7,0,.4); P.armR.rotation.set(-2.7,0,-.4); P.g.position.y=Math.abs(Math.sin(AV.t*9))*.12; if(AV.cheer<=0){ P.setExpr(P.expr0||"smile"); } }
    else if(AV.sad>0){ AV.sad-=dt; P.head.rotation.x=.35; P.armL.rotation.set(0,0,.1); P.armR.rotation.set(0,0,-.1); if(AV.sad<=0){ P.head.rotation.x=0; P.setExpr(P.expr0||"smile"); } }
    else { P.body.rotation.x=0; P.armL.rotation.set(0,0,.12); P.armR.rotation.set(BW.ph==="aim"?.25+Math.sin(AV.t*2)*.05:0,0,-.12); P.g.position.y=0; } }
  const arrowM=new THREE.Mesh(GE(new THREE.ConeGeometry(.12,.4,4)), new THREE.MeshBasicMaterial({color:0xffe14d, transparent:true, opacity:.85})); disp.push(arrowM.material); arrowM.rotation.x=-Math.PI/2; BOWL.add(arrowM);
  /* ── 다트 ── */
  const chC=document.createElement("canvas"); chC.width=256; chC.height=330; const chG=chC.getContext("2d"); const chT=new THREE.CanvasTexture(chC); chT.encoding=THREE.sRGBEncoding; disp.push(chT);
  const DART=new THREE.Group(); scene.add(DART); DART.visible=false;
  const DB={y:1.7, z:-5.2, R:1.0};
  { const bt=tex(1024,1024,(g,w)=>{ const c=w/2, R=w/2*.8; g.fillStyle="#1d1640"; g.fillRect(0,0,w,w); g.beginPath(); g.arc(c,c,w/2*.98,0,7); g.fillStyle="#2b2233"; g.fill();
      const ring=(r0,r1,cols)=>{ for(let i=0;i<20;i++){ const a0=-Math.PI/2+(i-.5)*Math.PI/10, a1=a0+Math.PI/10; g.beginPath(); g.arc(c,c,r1*R,a0,a1); g.arc(c,c,r0*R,a1,a0,true); g.closePath(); g.fillStyle=cols[i%2]; g.fill(); } };
      ring(.094,1,["#fff6e0","#2b2233"]); ring(.582,.629,["#ff4d5e","#3fc46a"]); ring(.953,1,["#ff4d5e","#3fc46a"]); ring(.1,.582,["#ffd84a","#5b3aff"]); ring(.629,.953,["#ffd84a","#5b3aff"]);
      g.beginPath(); g.arc(c,c,.094*R,0,7); g.fillStyle="#3fc46a"; g.fill(); g.beginPath(); g.arc(c,c,.037*R,0,7); g.fillStyle="#ff4d5e"; g.fill();
      g.strokeStyle="rgba(255,255,255,.5)"; g.lineWidth=2; for(let i=0;i<20;i++){ const a=-Math.PI/2+(i-.5)*Math.PI/10; g.beginPath(); g.moveTo(c+Math.cos(a)*.094*R,c+Math.sin(a)*.094*R); g.lineTo(c+Math.cos(a)*R,c+Math.sin(a)*R); g.stroke(); }
      g.fillStyle="#fff"; g.font="900 54px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; SEG.forEach((n,i)=>{ const a=-Math.PI/2+i*Math.PI/10; g.fillText(n, c+Math.cos(a)*R*1.1, c+Math.sin(a)*R*1.1); }); });
    const bd=new THREE.Mesh(GE(new THREE.CircleGeometry(DB.R*1.25,64)), MS(0xffffff,{map:bt, roughness:.9})); bd.position.set(0,DB.y,DB.z); DART.add(bd);
    const rimm=new THREE.Mesh(GE(new THREE.TorusGeometry(DB.R*1.25,.06,8,64)), MS(0x8a5a3c)); rimm.position.copy(bd.position); DART.add(rimm);
    const wall=new THREE.Mesh(GE(new THREE.PlaneGeometry(10,6)), MS(0x3d2f7a)); wall.position.set(0,2,DB.z-.05); DART.add(wall);
    const fl=new THREE.Mesh(GE(new THREE.PlaneGeometry(10,10)), MS(0x2a2150)); fl.rotation.x=-Math.PI/2; fl.position.set(0,0,-2); DART.add(fl);
    for(let i=0;i<7;i++){ const b=new THREE.Mesh(GE(new THREE.SphereGeometry(.06,8,6)), new THREE.MeshBasicMaterial({color:[0xff5ce1,0xffd23f,0x3dff9a][i%3]})); disp.push(b.material); b.position.set(-3+i,3.6,DB.z+.02); DART.add(b); }
    [[1.42,0xff5ce1],[1.56,0x3ea2ff]].forEach(([r,c])=>{ const nm=new THREE.MeshBasicMaterial({color:c}); disp.push(nm); const t=new THREE.Mesh(GE(new THREE.TorusGeometry(r,.035,6,72)), nm); t.position.set(0,DB.y,DB.z+.01); DART.add(t); });
    const wd=tex(256,512,(g,w,h)=>{ for(let i=0;i<8;i++){ g.fillStyle=i%2?"#8a5a3c":"#9c6842"; g.fillRect(i*32,0,32,h); } }); const pan=new THREE.Mesh(GE(new THREE.PlaneGeometry(10,6)), MS(0xffffff,{map:wd})); pan.position.set(0,2,DB.z-.04); DART.add(pan);
    const ch=new THREE.Mesh(GE(new THREE.PlaneGeometry(1.25,1.6)), new THREE.MeshBasicMaterial({map:chT})); disp.push(ch.material); ch.position.set(2.55,DB.y,DB.z+.02); DART.add(ch); const chf=new THREE.Mesh(GE(new THREE.BoxGeometry(1.35,1.7,.04)), MS(0x6e4430)); chf.position.set(2.55,DB.y,DB.z); DART.add(chf); }
  function chPaint(){ const g=chG, w=256, h=330; g.fillStyle="#1f3b2c"; g.fillRect(0,0,w,h); g.strokeStyle="rgba(255,255,255,.12)"; g.lineWidth=2; for(let i=0;i<8;i++){ g.beginPath(); g.moveTo(Math.random()*w,Math.random()*h); g.lineTo(Math.random()*w,Math.random()*h); g.stroke(); }
    g.fillStyle="#fff"; g.font="bold 30px Jua,sans-serif"; g.textAlign="center"; g.fillText("SCORE", w/2, 40); g.font="bold 26px sans-serif"; for(let r=0;r<3;r++){ const x=DT.rnd.slice(r*3,r*3+3); g.fillStyle="#ffe14d"; g.textAlign="left"; g.fillText((r+1)+".", 16, 92+r*62); g.fillStyle="#fff"; g.fillText(x.map(q=>q.s).join(" · "), 52, 92+r*62); }
    g.fillStyle="#ff9ad8"; g.textAlign="center"; g.font="bold 40px sans-serif"; g.fillText(DT.sum, w/2, 305); chT.needsUpdate=true; }
  const dartGeo=(()=>{ const g=new THREE.Group(); return g; })();
  function dartMesh(c){ const g=new THREE.Group(); const body=new THREE.Mesh(GE(new THREE.CylinderGeometry(.025,.02,.32,8)), MS(0xc8c8d0)); body.rotation.x=Math.PI/2; g.add(body);
    const tip=new THREE.Mesh(GE(new THREE.ConeGeometry(.012,.09,6)), MS(0x888899)); tip.rotation.x=-Math.PI/2; tip.position.z=-.2; g.add(tip);
    const fm=MS(c,{side:THREE.DoubleSide}); [0,Math.PI/2].forEach(r=>{ const f=new THREE.Mesh(GE(new THREE.PlaneGeometry(.12,.14)), fm); f.position.z=.18; f.rotation.set(0,Math.PI/2,r); g.add(f); }); g.scale.setScalar(1.7); return g; }
  const hand=dartMesh(0xff4d5e); hand.visible=false; DART.add(hand);
  /* ══ 화면 ══ */
  const U=api.ui, R=document.createElement("div"); R.className="spR"; U.insertBefore(R, U.querySelector(".mgTop"));
  R.innerHTML='<div class="spHit"></div><div class="spSc"></div><div class="spAim"></div><div class="spBig"></div><div class="spSay"></div><button class="spBtn"></button><div class="spMenu"></div>';
  ["pointerdown","pointermove","pointerup"].forEach(t=>R.addEventListener(t, e=>e.stopPropagation()));
  const $=s=>R.querySelector(s), HIT=$(".spHit"), SC=$(".spSc"), AIM=$(".spAim"), BIG=$(".spBig"), SAY=$(".spSay"), BTN=$(".spBtn"), MENU=$(".spMenu");
  const say=t=>{ SAY.textContent=t||""; SAY.style.display=t?"":"none"; };
  function big(t, sub, s){ BIG.innerHTML=t+(sub?'<small>'+sub+'</small>':''); BIG.classList.add("on"); clearTimeout(big.h); big.h=setTimeout(()=>BIG.classList.remove("on"), (s||1.2)*1000*(fast?.05:1)); }
  /* ══ 메뉴 ══ */
  function menuShow(){ mode="menu"; TM.length=0; MENU.classList.add("on"); SC.style.display="none"; BTN.style.display="none"; AIM.style.display="none"; say(""); BOWL.visible=true; DART.visible=false; const r=REC();
    MENU.innerHTML='<h2>🎳 볼링 · 🎯 다트</h2><div class="sub">하나 골라 한 판!</div><div class="g"><button data-m="bowl"><span class="e">🎳</span>볼링<small>5프레임 · 최고 '+r.bw+'점</small></button><button data-m="dart"><span class="e">🎯</span>다트<small>9개 던지기 · 최고 '+r.dt+'점</small></button></div>'+
      '<button class="tg'+(SET.bump?" on":"")+'" data-t="bump">🛡 볼링 범퍼 '+(SET.bump?"켬 (도랑 막기)":"끔")+'</button><div class="sub">오늘 🪙 상 '+(MG.payLeft("bowl")>0?MG.payLeft("bowl")+'판 남음':'다 받았어요')+' · 🎳 스트라이크 '+r.strikes+' · 🎯 불 '+r.bulls+'</div><button class="out">🏝 섬으로</button>'; }
  MENU.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b) return; try{ SFX.tone(660,.06,"triangle",.04); }catch(_){} if(b.classList.contains("out")){ MG.exit(); return; }
    if(b.dataset.t==="bump"){ SET.bump=SET.bump?0:1; st("hyeng_proto_spset", SET); menuShow(); return; } menuGo(b.dataset.m); });
  function menuGo(k){ TM.length=0; CONF.forEach(m=>scene.remove(m)); CONF.length=0; MENU.classList.remove("on"); if(k==="bowl") bowlStart(); else dartStart(); }
  BTN.addEventListener("click", ()=>{ if(mode==="bowl"){ SET.bump=SET.bump?0:1; st("hyeng_proto_spset", SET); BTN.textContent="🛡 범퍼 "+(SET.bump?"켬":"끔"); BUMP.forEach(b=>b.visible=!!SET.bump); } });

  /* ══ 🎳 볼링 ══ */
  const BW={rolls:[], ph:"aim", bx:0, vx:0, vz:0, t:0, rolling:false, gutter:false, standing:10, camZ:3.4};
  function bowlStart(){ mode="bowl"; BOWL.visible=true; DART.visible=false; SC.style.display=""; BTN.style.display=""; BTN.textContent="🛡 범퍼 "+(SET.bump?"켬":"끔"); BUMP.forEach(b=>b.visible=!!SET.bump);
    BW.rolls=[]; setPins(true); readyBall(); sheet(); }
  function setPins(all){ PINS.forEach(p=>{ if(all){ p.up=true; } if(p.up){ p.down=false; p.x=p.hx; p.z=p.hz; p.vx=p.vz=0; p.tilt=0; p.g.visible=true; p.g.rotation.set(0,0,0); p.g.position.set(p.x,0,p.z); } else p.g.visible=false; }); }
  function readyBall(){ BW.ph="aim"; BW.bx=0; BW.vx=BW.vz=0; BW.t=0; BW.gutter=false; ball.position.set(0,BR,.3); guide.visible=false; camP=null; ball.visible=true; arrowM.visible=true; BW.camZ=3.4; const f=rollsInFrame(BW.rolls); say((f.f+1)+"프레임 "+(f.k+1)+"번째 · 위로 쓱! 또는 콕 👆"); }
  function sheet(){ const s=bowlScore(BW.rolls), f=rollsInFrame(BW.rolls).f; SC.innerHTML=s.marks.map((m,i)=>'<div class="'+(i===f && mode==="bowl"?"cur":"")+'"><small>'+(i+1)+'</small><div class="m">'+m.map(x=>'<span>'+x+'</span>').join("")+'</div><div class="t">'+(s.out[i]==null?"":s.out[i])+'</div></div>').join("")+'<div class="tot"><small>합계</small><div class="m"></div><div class="t">'+s.total+'</div></div>'; if(!monBig) monPaint(); }
  let monBig=0;
  function throwBall(x, vx, vz){ if(mode!=="bowl" || BW.ph!=="aim") return false; BW.bx=Math.max(-LW/2+BR, Math.min(LW/2-BR, x)); BW.vx=Math.max(-1.6,Math.min(1.6,vx)); BW.vz=-Math.max(5, Math.min(16, vz)); BW.ph="roll"; BW.t=0; arrowM.visible=false; guide.visible=false; ball.position.x=BW.bx; AV.sw=.55; say(""); try{ SFX.noise(1.2,.05,300,.5,150); }catch(e){} return true; }
  function bowlStep(dt){ if(BW.ph==="aim"){ const t=performance.now()/1000; arrowM.position.set(BW.bx, .03, -1.0+Math.sin(t*4)*.08); return; }
    if(BW.ph!=="roll") return; const H=1/240; let n=Math.ceil(dt/H); const h=dt/n;
    while(n--){ BW.t+=h; const b=ball.position;
      if(BW.vz<0 || Math.abs(BW.vx)>0){ b.x+=BW.vx*h; b.z+=BW.vz*h; ball.rotation.x+=BW.vz*h/BR; }
      if(!BW.gutter){ if(SET.bump){ if(b.x<-LW/2+BR){ b.x=-LW/2+BR; BW.vx=Math.abs(BW.vx)*.6; try{ SFX.tone(240,.05,"square",.03); }catch(e){} } if(b.x>LW/2-BR){ b.x=LW/2-BR; BW.vx=-Math.abs(BW.vx)*.6; try{ SFX.tone(240,.05,"square",.03); }catch(e){} } }
        else if(Math.abs(b.x)>LW/2-BR*.4 && b.z>HZ+.4){ BW.gutter=true; BW.vx=0; b.x=Math.sign(b.x)*(LW/2+.16); b.y=BR-.12; big("😅 도랑!", "", 1); } }
      if(b.z<LZ+.1){ BW.vz=0; BW.vx=0; ball.visible=false; }
      /* 공 → 핀 · 핀 → 핀 */
      if(!BW.gutter && ball.visible) PINS.forEach(p=>{ if(!p.g.visible) return; const dx=p.x-b.x, dz=p.z-b.z, d=Math.hypot(dx,dz), rr=BR+PR; if(d<rr && d>0){ const nx=dx/d, nz=dz/d, ov=rr-d; p.x+=nx*ov; p.z+=nz*ov; const vn=(BW.vx-p.vx)*nx+(BW.vz-p.vz)*nz; if(vn>0){ const j=1.5*vn/(1/6+1/1.5); p.vx+=j*nx/1.5; p.vz+=j*nz/1.5; BW.vx-=j*nx/6; BW.vz-=j*nz/6; hitSnd(); } } });
      for(let i=0;i<PINS.length;i++){ const a=PINS[i]; if(!a.g.visible) continue; for(let j=i+1;j<PINS.length;j++){ const c=PINS[j]; if(!c.g.visible) continue; const dx=c.x-a.x, dz=c.z-a.z, d=Math.hypot(dx,dz), rr=PR*2*(a.down||c.down?1.15:1); if(d<rr && d>0){ const nx=dx/d, nz=dz/d, ov=rr-d; a.x-=nx*ov/2; a.z-=nz*ov/2; c.x+=nx*ov/2; c.z+=nz*ov/2; const vn=(a.vx-c.vx)*nx+(a.vz-c.vz)*nz; if(vn>0){ const jj=vn*.75; a.vx-=jj*nx; a.vz-=jj*nz; c.vx+=jj*nx; c.vz+=jj*nz; hitSnd(); } } } }
      PINS.forEach(p=>{ if(!p.g.visible) return; p.x+=p.vx*h; p.z+=p.vz*h; const sp=Math.hypot(p.vx,p.vz); if(sp>0){ const k=Math.max(0,sp-3.5*h)/sp; p.vx*=k; p.vz*=k; } if(!p.down && (sp>.9 || Math.hypot(p.x-p.hx,p.z-p.hz)>.16)){ p.down=true; p.ta=Math.atan2(p.vx,p.vz)||0; }
        if(Math.abs(p.x)>LW/2+.3 || p.z<LZ){ p.vx*=.5; p.vz*=.5; } }); }
    PINS.forEach(p=>{ if(!p.g.visible) return; if(p.down) p.tilt=Math.min(Math.PI/2, p.tilt+dt*7); p.g.position.set(p.x, p.down?Math.sin(p.tilt)*PR:0, p.z); p.g.rotation.set(Math.cos(p.ta)*p.tilt, 0, -Math.sin(p.ta)*p.tilt); });
    const moving=PINS.some(p=>p.g.visible && Math.hypot(p.vx,p.vz)>.05);
    if((ball.position.z<LZ+.2 || BW.vz===0) && (!moving || BW.t>7) || BW.t>9){ BW.ph="count"; later(fast?.02:.6, countPins); } }
  let hitT=0; function hitSnd(){ const n=performance.now(); if(n-hitT<45) return; hitT=n; try{ SFX.tone(900+Math.random()*500,.05,"square",.03); SFX.noise(.08,.05,2200); }catch(e){} }
  function countPins(){ const f=rollsInFrame(BW.rolls); const before=PINS.filter(p=>p.up).length; PINS.forEach(p=>{ if(p.up && p.down) p.up=false; }); const after=PINS.filter(p=>p.up).length; const got=before-after; BW.rolls.push(got);
    const r=REC(); if(got===10 && before===10){ big("STRIKE!", "스트라이크 🎉", 1.6); r.strikes++; st("hyeng_proto_spr", r); try{ SFX.win(); }catch(e){} fx("STRIKE!", 70); } else if(after===0){ big("SPARE!", "스페어 👏", 1.4); try{ SFX.clear(); }catch(e){} fx("SPARE!", 36); } else if(got===0){ big("0", "괜찮아요!", 1); AV.sad=1.4; if(MEAV) MEAV.setExpr("wow"); } else { big(String(got), got>=7?"좋아요!":"핀 "+got+"개", 1); if(got>=7){ AV.cheer=.8; if(MEAV) MEAV.setExpr("grin"); } }
    sheet(); if(bowlDone(BW.rolls)){ later(fast?.05:1.8, bowlEnd); return; }
    const nf=rollsInFrame(BW.rolls); later(fast?.05:1.3, ()=>{ setPins(nf.reset); readyBall(); sheet(); }); }
  function fx(t, n){ confetti(0,.8,HZ-.6,LOW?Math.round(n/2):n); AV.cheer=1.6; if(MEAV) MEAV.setExpr("grin"); monBig=1; monPaint(t); later(fast?.05:1.6, ()=>{ monBig=0; monPaint(); }); }
  function bowlEnd(){ const s=bowlScore(BW.rolls).total, r=REC(), best=s>r.bw; r.bw=Math.max(r.bw,s); st("hyeng_proto_spr", r); const coins=s>=100?9:s>=70?7:s>=40?5:3;
    api.end({title:(best?"🎉 내 최고! ":"🎳 ")+s+"점", sub:"볼링 5프레임 · "+(SET.bump?"🛡 범퍼":"범퍼 없이")+" · 스트라이크 "+BW.rolls.filter((x,i)=>x===10).length, rows:null, coins, again:{go:"bowl"}, upd:(b,t)=>{ b.bw=Math.max(b.bw|0,s); }}); }
  /* 볼링 조작: 위로 쓱(빠르기 · 방향) · 콕 = 그쪽으로 */
  const ray=new THREE.Raycaster(), v2=new THREE.Vector2(), pl=new THREE.Plane(new THREE.Vector3(0,1,0),0), hitP=new THREE.Vector3();
  function lanePt(e){ const r=HIT.getBoundingClientRect(); v2.set((e.clientX-r.left)/r.width*2-1, -((e.clientY-r.top)/r.height*2-1)); ray.setFromCamera(v2,cam); return ray.ray.intersectPlane(pl,hitP)?hitP.clone():null; }
  let pd=null, trail=[];
  HIT.addEventListener("pointerdown", e=>{ e.preventDefault(); pd={x:e.clientX, y:e.clientY, t:performance.now()}; trail=[pd]; if(mode==="dart") dartDown(e); });
  HIT.addEventListener("pointermove", e=>{ if(!pd) return; trail.push({x:e.clientX,y:e.clientY,t:performance.now()}); if(trail.length>12) trail.shift();
    if(mode==="bowl" && BW.ph==="aim"){ const p=lanePt(e); if(p && p.z>-2.5) { BW.bx=Math.max(-LW/2+BR, Math.min(LW/2-BR, p.x)); ball.position.x=BW.bx; } const p0=trail[0], dy=p0.y-e.clientY, dx=e.clientX-p0.x; if(dy>20){ const vx=dx/Math.max(dy,1)*3.2; guideTo(BW.bx+vx*HZ/-11, HZ+1.2); } else if(p && p.z<-2) guideTo(p.x, p.z); else guide.visible=false; } if(mode==="dart") dartMove(e); });
  HIT.addEventListener("pointerup", e=>{ if(!pd) return; const p0=trail[0], dy=p0.y-e.clientY, dx=e.clientX-p0.x, dt=Math.max(30, performance.now()-p0.t);
    if(mode==="bowl" && BW.ph==="aim"){ if(dy>40){ const sp=dy/dt*1000/innerHeight; throwBall(BW.bx, dx/Math.max(dy,1)*3.2, 6+sp*7); }
      else { const p=lanePt(e); if(p && p.z<-2){ const dist=-p.z; throwBall(BW.bx, (p.x-BW.bx)/dist*9, 9); } } }
    if(mode==="dart") dartUp(e); pd=null; guide.visible=false; });

  /* ══ 🎯 다트 ══ */
  const DT={n:0, darts:[], sum:0, rnd:[], aimX:0, aimY:0, hold:false, fly:null, wob:0};
  const DN=9;
  function dartStart(){ mode="dart"; BOWL.visible=false; DART.visible=true; SC.style.display=""; BTN.style.display="none"; DT.darts.forEach(d=>DART.remove(d.m)); Object.assign(DT,{n:0, darts:[], sum:0, rnd:[], aimX:0, aimY:-.2, fly:null, hold:false}); AIM.style.display="block"; dsheet(); chPaint(); say("손가락으로 조준점을 옮기고, 떼면 던져요 🎯"); }
  function dsheet(){ const R3=[0,1,2].map(r=>DT.rnd.slice(r*3,r*3+3)); SC.innerHTML=R3.map((x,i)=>'<div class="'+(Math.floor(DT.n/3)===i?"cur":"")+'" style="width:84px"><small>'+(i+1)+'라운드</small><div class="m">'+x.map(q=>'<span>'+q.s+'</span>').join(" ")+'</div><div class="t">'+(x.length?x.reduce((s,q)=>s+q.s,0):"")+'</div></div>').join("")+'<div class="tot"><small>합계</small><div class="m"></div><div class="t">'+DT.sum+'</div></div>'; }
  const toBoard=(px,py)=>{ /* 화면 → 판 (반지름 1 = 판 끝) */ const v=new THREE.Vector3(0,DB.y,DB.z).project(cam), e=new THREE.Vector3(DB.R,DB.y,DB.z).project(cam), W=innerWidth, H=innerHeight; const cx=(v.x+1)/2*W, cy=(1-v.y)/2*H, rr=((e.x+1)/2*W)-cx; return [(px-cx)/rr, -(py-cy)/rr, cx, cy, rr]; };
  const toScr=(bx,by)=>{ const t=toBoard(0,0); return [t[2]+bx*t[4], t[3]-by*t[4]]; };
  function dartDown(e){ if(DT.fly || DT.n>=DN) return; DT.hold=true; const b=toBoard(e.clientX, e.clientY-70); DT.aimX=b[0]; DT.aimY=b[1]; }
  function dartMove(e){ if(!DT.hold) return; const b=toBoard(e.clientX, e.clientY-70); DT.aimX=Math.max(-1.4,Math.min(1.4,b[0])); DT.aimY=Math.max(-1.4,Math.min(1.4,b[1])); }
  function dartUp(){ if(!DT.hold) return; DT.hold=false; const w=wob(); dart(DT.aimX+w[0], DT.aimY+w[1]); }
  function wob(){ const t=DT.wob; return [Math.sin(t*1.7)*.07+Math.sin(t*4.1)*.025, Math.sin(t*2.3+1)*.07+Math.cos(t*3.7)*.025]; }
  function scoreAt(x,y){ const r=Math.hypot(x,y); if(r<=.037) return {s:50, t:"BULL'S-EYE!", w:"fifty", k:"bull"}; if(r<=.094) return {s:25, t:"BULL!", w:"twenty-five", k:"bull"}; if(r>1) return {s:0, t:"MISS", w:"", k:"miss"};
    let a=Math.atan2(x,y); if(a<0) a+=Math.PI*2; const i=Math.round(a/(Math.PI/10))%20, n=SEG[i];
    if(r>=.582 && r<=.629) return {s:n*3, t:"TRIPLE "+NUMW[n].toUpperCase()+"!", w:"triple "+NUMW[n], k:"t", n}; if(r>=.953) return {s:n*2, t:"DOUBLE "+NUMW[n].toUpperCase()+"!", w:"double "+NUMW[n], k:"d", n}; return {s:n, t:NUMW[n].toUpperCase()+"!", w:NUMW[n], k:"s", n}; }
  function dart(x, y){ if(mode!=="dart" || DT.fly || DT.n>=DN) return null; const m=dartMesh([0xff4d5e,0x3fc46a,0x3ea2ff][Math.floor(DT.n/3)]); m.position.copy(hand.position); DART.add(m); hand.visible=false;
    const to=new THREE.Vector3(x*DB.R, DB.y+y*DB.R, DB.z+.3); DT.fly={m, from:m.position.clone(), to, t:0, x, y}; try{ SFX.noise(.18,.04,1800,.6,900); }catch(e){} return scoreAt(x,y); }
  function dartLand(){ const f=DT.fly; DT.fly=null; const sc=scoreAt(f.x,f.y); DT.darts.push({m:f.m, x:f.x, y:f.y}); DT.rnd.push(sc); DT.sum+=sc.s; DT.n++; try{ SFX.tone(sc.s?1200:200,.06,"square",.04); }catch(e){}
    big(sc.t, sc.s?(sc.s+"점"):"괜찮아요!", 1.2); if(sc.w && sc.k!=="miss") sayW(sc.w); if(sc.k==="bull"){ const r=REC(); r.bulls++; st("hyeng_proto_spr", r); }
    dsheet(); chPaint(); if(DT.n>=DN){ later(fast?.05:1.6, dartEnd); return; } if(DT.n%3===0) later(fast?.05:1.4, ()=>{ DT.darts.forEach(d=>DART.remove(d.m)); DT.darts=[]; say((DT.n/3+1)+"라운드!"); }); }
  function dartEnd(){ const s=DT.sum, r=REC(), best=s>r.dt; r.dt=Math.max(r.dt,s); st("hyeng_proto_spr", r); AIM.style.display="none"; const coins=s>=300?9:s>=180?7:s>=90?5:3;
    api.end({title:(best?"🎉 내 최고! ":"🎯 ")+s+"점", sub:"다트 9개 · 가장 큰 한 방 "+Math.max(...DT.rnd.map(q=>q.s))+"점", rows:null, coins, again:{go:"dart"},
      extra:'<div class="sub" style="margin-top:6px">'+DT.rnd.filter(q=>q.w).map(q=>'<b style="font-family:var(--en)">'+q.w+'</b>').join(" · ")+'</div>', upd:(b,t)=>{ b.dt=Math.max(b.dt|0,s); }}); }
  function dartStep(dt){ DT.wob+=dt; if(DT.fly){ const f=DT.fly; f.t=Math.min(1,f.t+dt*(fast?20:3.2)); const p=f.from.clone().lerp(f.to,f.t); p.y+=Math.sin(f.t*Math.PI)*.35; f.m.position.copy(p); f.m.lookAt(f.to.x, f.to.y, f.to.z-1); f.m.rotateY(Math.PI); if(f.t>=1){ f.m.position.copy(f.to); f.m.rotation.set(-.22+Math.random()*.1,(Math.random()-.5)*.35,0); dartLand(); } }
    if(mode==="dart" && !DT.fly && DT.n<DN){ hand.visible=true; const w=wob(); const ax=(DT.aimX+w[0])*DB.R, ay=DB.y+(DT.aimY+w[1])*DB.R; hand.position.set(cam.position.x+.34, cam.position.y-.42, cam.position.z-1.1); hand.lookAt(ax, ay, DB.z); hand.rotateY(Math.PI); } else hand.visible=false;
    if(mode==="dart" && !DT.fly && DT.n<DN){ const w=wob(), s=toScr(DT.aimX+w[0], DT.aimY+w[1]); AIM.style.left=s[0]+"px"; AIM.style.top=s[1]+"px"; AIM.style.display="block"; } else AIM.style.display="none"; }
  /* ══ 카메라 ══ */
  let camP=null, camT=null;
  function fitCam(){ const w=innerWidth, h=innerHeight, asp=w/h; cam.aspect=asp;
    if(mode==="dart"){ const need=DB.R*2.9, t=Math.tan(cam.fov*Math.PI/360), d=Math.max(need/2/t, need/2/t/asp); cam.position.set(0, DB.y, DB.z+d); cam.lookAt(0, DB.y-.05, DB.z); }
    else { const b=ball.position, portrait=asp<.9; cam.fov=portrait?62:50; const pinCam=(BW.ph==="roll"||BW.ph==="count") && (b.z<HZ+3.4 || !ball.visible) && !BW.gutter;
      const z=BW.ph==="roll"||BW.ph==="count"?Math.max(-6.2, Math.min(BW.camZ, b.z+3.4)):BW.camZ; BW.camZ=z;
      const des=pinCam?new THREE.Vector3(.9, .95, HZ+2.6):new THREE.Vector3(0, portrait?2.05:1.6, z+(portrait?.9:.3)), tgt=pinCam?new THREE.Vector3(-.1,.3,HZ-.6):new THREE.Vector3(0,.1,z-8);
      if(!camP || fast || BW.ph==="aim"){ camP=des.clone(); camT=tgt.clone(); } else { camP.lerp(des, pinCam?.08:.25); camT.lerp(tgt, pinCam?.08:.25); } cam.position.copy(camP); cam.lookAt(camT); }
    cam.updateProjectionMatrix(); }
  /* ══ 틀 ══ */
  function tick(dt){ if(gone || paused) return; if(fast) dt=Math.min(.1, dt*4);
    for(let i=TM.length-1;i>=0;i--){ TM[i].t-=dt; if(TM[i].t<=0){ const f=TM[i].fn; TM.splice(i,1); try{ f(); }catch(e){ console.warn("SP", e); } } }
    if(mode==="bowl"){ const slow=!fast && BW.ph==="roll" && ball.visible && !BW.gutter && ball.position.z<HZ+2.4 && ball.position.z>LZ+.3; bowlStep(dt*(slow?.42:1)); avStep(dt); } if(mode==="dart") dartStep(dt); confStep(dt); }
  function render(){ fitCam(); MG.draw(scene, cam); }
  function dispose(){ gone=true; TM.length=0; try{ R.remove(); }catch(e){} disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); }
  fitCam(); const O=api.opt||{}; if(O.go==="bowl"||O.go==="dart") menuGo(O.go); else menuShow(); ready=true;
  return {scene, cam, tick, render, dispose, pause:v=>{ paused=!!v; },
    get mode(){ return mode; }, get bw(){ return BW; }, get dt(){ return DT; }, get ready(){ return ready; }, get pins(){ return PINS; }, set fast(v){ fast=v?1:0; },
    menuGo, menuShow, throwBall, dart:(x,y)=>dart(x,y), scoreAt, bowlScore, bowlDone, rollsInFrame, get SET(){ return SET; }, fitCam };
}
MG.reg("bowl", {ic:"🎳", nm:"볼링 · 다트", tag:"🎳 볼링 5프레임 · 🎯 다트 9개", bg:"linear-gradient(135deg,#5b3aff,#ff5ce1 55%,#ffd23f)", big:"🎳🎯", menu:true,
  how:[["🎳","레인을 위로 쓱 밀어 굴려요"],["🎯","조준점을 옮기고 떼면 던져요"]], payTxt:"점수 따라 🪙 3~9",
  bestTxt:(b,t)=>'🎳 '+(b.bw|0)+'점 · 🎯 '+(b.dt|0)+'점', ui:{look:false, btns:[]}, start});
})();
