/* ═════════ 🎳🎯 볼링 · 다트 — 🎡 놀이 섬 볼링장
   (v638) 사용자: 「5번은 한 번씩 좋다」 = 한 건물에서 🎳 볼링 · 🎯 다트 하나 골라 한 판
   · 🎳 볼링 5프레임: 레인을 위로 쓱 밀면(빠르기 · 방향) 굴러감 · 콕 누르면 그쪽으로 · 🛡 범퍼(도랑 막기) 켜고 끄기
       핀끼리 부딪혀 넘어짐(원 충돌) · 스트라이크 X · 스페어 / · 점수 = 진짜 볼링 셈(5프레임)
   · 🎯 다트 3라운드 × 3개: 손가락으로 조준점을 옮기고 떼면 던짐(조준점이 살짝 흔들림) · 트리플 · 더블 · 불
       맞힌 숫자는 영어로 (triple twenty! → 60) — 숫자 영어 말하기 연습
   · 상: MG 공통 하루 3판 🪙 (볼링 40/70/100 · 다트 90/180/300 넘으면 5/7/9 · 그 밑 3)
   · (v731) 🎳 옆 레인 대결: 🤖 Tom(왼쪽) · Lily(오른쪽)가 같이 굴림(쉬움 · 보통 · 잘함 · 혼자) · 점수판 3줄 · 「Tom 스트라이크!」
       핀 손맛: 맞은 핀이 튀어 오르며 돎 · 핀 정리 막대 · 핀 세우는 판 · 스트라이크 다시 보기(느리게) · 더블 · 터키 · 부딪히는 소리
   시험 손잡이: MG.run.mode · .bw(볼링 상태) · .dt(다트 상태) · .throwBall(x, vx, vz) · .dart(x, y) · .fast · .menuGo(k) · .ready · .score */
(function(){
"use strict";
if(!window.MG) return;
const st=(k,v)=>{ try{ return typeof store==="function" ? store(k,v) : (v===undefined?JSON.parse(localStorage.getItem(k)||"null"):localStorage.setItem(k,JSON.stringify(v))); }catch(e){ return null; } };
const sayW=w=>{ try{ say(w); }catch(e){} };
const NUMW=["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen","twenty"];
const SEG=[20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5];
const NF=5;
const esc=x=>String(x==null?"":x).replace(/[<>&"]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c]));
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
#mgUI .spSc{position:absolute;left:50%;top:calc(56px + env(safe-area-inset-top));transform:translateX(-50%);display:flex;gap:4px;pointer-events:none;background:#FFF6E3;border:3px solid #4A2E1F;border-radius:16px;padding:5px;max-width:96vw;box-shadow:0 0 0 3px #fff,0 5px 0 3px rgba(74,46,31,.35)}
#mgUI .spSc div{width:54px;background:#fff;color:#4A2E1F;border:2px solid #4A2E1F;border-radius:9px;text-align:center;font-family:var(--en);font-weight:900;overflow:hidden}
#mgUI .spSc div.cur{box-shadow:0 0 0 3px #FFC53D;background:#fffbe8}
#mgUI .spSc div small{display:block;background:#4A2E1F;color:#fff;font-size:10px;font-weight:700;padding:1px 0}
#mgUI .spSc div .m{display:flex;justify-content:flex-end;gap:4px;font-size:13px;min-height:18px;padding:1px 3px} #mgUI .spSc div .m span{min-width:12px} #mgUI .spSc div .t{font-size:17px;min-height:22px}
#mgUI .spSc div.tot{width:64px;background:#FFC53D}
#mgUI .spBig{position:absolute;left:50%;top:38%;transform:translate(-50%,-50%) scale(.6);opacity:0;font-family:var(--kr);font-size:62px;color:#FFC53D;-webkit-text-stroke:9px #4A2E1F;paint-order:stroke fill;filter:drop-shadow(0 6px 0 #4A2E1F);transition:all .25s;pointer-events:none;white-space:nowrap;text-align:center}
#mgUI .spBig.on{opacity:1;transform:translate(-50%,-50%) scale(1)} #mgUI .spBig small{display:block;font-size:24px;font-family:var(--kr);color:#fff;-webkit-text-stroke:6px #4A2E1F}
#mgUI .spSay{position:absolute;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translateX(-50%);background:#4A2E1F;color:#fff;border-radius:16px;padding:9px 18px;font-size:16.5px;white-space:nowrap;pointer-events:none;box-shadow:0 0 0 3px #fff}
#mgUI .spBtn{position:absolute;right:calc(14px + env(safe-area-inset-right));bottom:calc(74px + env(safe-area-inset-bottom));pointer-events:auto;font:inherit;font-family:var(--kr);border:3px solid #4A2E1F;border-radius:16px;padding:8px 12px;min-height:46px;background:#fff;color:#4A2E1F;font-size:15px;box-shadow:0 4px 0 #4A2E1F}
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
/* (v731) 점수판 3줄 (나 · Tom · Lily) · 친구 소식 · 다시 보기 표 */
#mgUI .spSc.multi{flex-direction:column;gap:3px;padding:5px 6px}
#mgUI .spSc.multi .rw{display:flex;gap:3px;align-items:stretch}
#mgUI .spSc.multi .nm{width:50px;align-self:center;font-family:var(--kr);font-size:13px;color:#4A2E1F;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;text-align:left;padding-left:2px}
#mgUI .spSc.multi .rw.me .nm{color:#e2553c}
#mgUI .spSc.multi .f{width:40px;background:#fff;color:#4A2E1F;border:2px solid #4A2E1F;border-radius:8px;text-align:center;font-family:var(--en);font-weight:900;display:flex;flex-direction:column;justify-content:center;line-height:1.08;padding:1px 0}
#mgUI .spSc.multi .f i{font-style:normal;font-size:11.5px;min-height:13px;display:block;white-space:nowrap} #mgUI .spSc.multi .f b{font-size:13.5px;min-height:14px;display:block}
#mgUI .spSc.multi .f.cur{box-shadow:0 0 0 2px #FFC53D;background:#fffbe8}
#mgUI .spSc.multi .f.tot{width:42px;background:#fff1c9;font-size:17px}
#mgUI .spSc.multi .rw.lead .f.tot{background:#FFC53D}
#mgUI .spPop{position:absolute;left:50%;top:150px;transform:translate(-50%,-8px) scale(.9);opacity:0;background:#FFC53D;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:999px;padding:5px 16px;font-size:18px;white-space:nowrap;pointer-events:none;box-shadow:0 4px 0 #4A2E1F;transition:opacity .2s,transform .25s cubic-bezier(.34,1.56,.64,1)}
#mgUI .spPop.on{opacity:1;transform:translate(-50%,0) scale(1)}
#mgUI .spRp{position:absolute;left:50%;transform:translateX(-50%);bottom:calc(24px + env(safe-area-inset-bottom));white-space:nowrap;display:none;background:#ff3b5c;color:#fff;border-radius:999px;padding:6px 14px;font-size:15px;pointer-events:none;box-shadow:0 0 0 3px #fff}
#mgUI .spRp.on{display:block}
@media (prefers-reduced-motion:reduce){ #mgUI .spPop{transition:opacity .2s} }
#mgUI .puM.spMenuVs .puSeg{gap:4px} #mgUI .puM.spMenuVs .puSeg button{flex:1 1 0;min-width:0;padding:4px 2px;white-space:nowrap;font-size:14px}   /* 상대 5개가 한 줄 (좁은 휴대폰에서 두 줄로 꺾여 메뉴가 넘쳤음) */
@media (max-width:370px){ #mgUI .puM.spMenuVs .puSeg button{font-size:12.5px} }
@media (orientation:landscape) and (max-height:620px){ #mgUI .spSc{top:calc(8px + env(safe-area-inset-top))} #mgUI .spMenu .g button{min-height:110px}
  #mgUI .spSc.multi{left:auto;right:calc(10px + env(safe-area-inset-right));transform:none} }
@media (min-width:700px) and (min-height:900px), (min-width:1000px) and (min-height:700px){ #mgUI .spSc{zoom:1.3} #mgUI .spSay{zoom:1.25} #mgUI .spBtn{zoom:1.25} #mgUI .spBig{zoom:1.3} #mgUI .spRp{zoom:1.25} #mgUI .spPop{font-size:23px;padding:7px 20px} }`;   /* (v729) 패드 크게 */ document.head.appendChild(s); }

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
  const BOWL=new THREE.Group(); scene.add(BOWL); let RET=null;
  const LW=2.0, LZ=-12.5, HZ=-10.3, BR=.24, PR=.12, BMIN=3.2;
  { const lt=tex(128,1024,(g,w,h)=>{ for(let i=0;i<16;i++){ g.fillStyle=i%2?"#e8b77a":"#dfa968"; g.fillRect(i*8,0,8,h); } g.fillStyle="rgba(255,255,255,.18)"; g.fillRect(0,0,w,h*.6);
      g.fillStyle="#ff4d5e"; [-2,-1,0,1,2].forEach(k=>{ const x=w/2+k*16, y=h*.8; g.beginPath(); g.moveTo(x,y-18); g.lineTo(x-6,y); g.lineTo(x+6,y); g.fill(); }); g.fillStyle="#3ea2ff"; for(let k=-4;k<=4;k++) { g.beginPath(); g.arc(w/2+k*12, h*.93, 3, 0, 7); g.fill(); } g.fillStyle="#2b2233"; g.fillRect(0,h-6,w,6); });
    const lane=new THREE.Mesh(GE(new THREE.PlaneGeometry(LW, -LZ+1)), MS(0xffffff,{map:lt, roughness:.35})); lane.rotation.x=-Math.PI/2; lane.position.set(0,0,LZ/2+.5); lane.receiveShadow=true; BOWL.add(lane);
    const gm=MS(0x3b3366); [-1,1].forEach(s=>{ const gt=new THREE.Mesh(GE(new THREE.BoxGeometry(.32,.04,-LZ+1)), gm); gt.position.set(s*(LW/2+.16),-.06,LZ/2+.5); BOWL.add(gt); const wall=new THREE.Mesh(GE(new THREE.BoxGeometry(.18,.5,-LZ+1)), MS(0x6a4fd0)); wall.position.set(s*(LW/2+.41),.2,LZ/2+.5); wall.castShadow=true; BOWL.add(wall); });
    const pit=new THREE.Mesh(GE(new THREE.BoxGeometry(LW+1.2,2.4,.3)), MS(0x1d1640)); pit.position.set(0,1,LZ-.4); BOWL.add(pit);
    const sign=new THREE.Mesh(GE(new THREE.PlaneGeometry(4,1.1)), new THREE.MeshBasicMaterial({map:tex(512,140,(g,w,h)=>{ g.fillStyle="#1d1640"; g.fillRect(0,0,w,h); g.font="900 84px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; "BOWLING".split("").forEach((ch,i)=>{ g.fillStyle=["#ff4d5e","#ffd23f","#3fc46a","#3ea2ff","#ff5ce1","#ff9a3d","#3dff9a"][i]; g.fillText(ch,46+i*70,h/2+4); }); })})); disp.push(sign.material); sign.position.set(0,1.78,LZ-.2); sign.scale.setScalar(.8); BOWL.add(sign);   /* (v729) 전: y 2.6 = 점수 화면(2.5~3.5)에 가려 「B‿W‿L」 만 보임 */
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
    const rt=new THREE.Group(); rt.position.set(1.85,0,1.5); BOWL.add(rt); RET=rt; { const b=new THREE.Mesh(GE(new THREE.BoxGeometry(.7,.55,1.1)), MS(0x5b3aff)); b.position.y=.28; rt.add(b); const hood=new THREE.Mesh(GE(new THREE.SphereGeometry(.38,16,10,0,Math.PI*2,0,Math.PI/2)), MS(0x9ad8ff,{transparent:true,opacity:.6})); hood.position.set(0,.55,-.2); rt.add(hood);
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
  /* 핀 — (v731) 한 덩어리(빨간 띠 = 꼭짓점 색 · 전엔 핀 하나 = 3개) · 가운데(높이 PC)가 축 = 맞으면 돌며 튀어 오름 */
  const PC=.3, AX=new THREE.Vector3();
  const pinGeo=(()=>{ const pts=[[0,0],[.07,0],[.11,.08],[.12,.22],[.1,.36],[.055,.47],[.05,.52],[.0509,.525],[.0603,.575],[.0613,.58],[.0632,.59],[.0641,.595],[.065,.6],[.0688,.645],[.0692,.65],[.07,.66],[.05,.72],[0,.75]].map(([x,y])=>new THREE.Vector2(x,y));
    const g=new THREE.LatheGeometry(pts,16), P=g.attributes.position, C=new Float32Array(P.count*3), W=new THREE.Color(0xfffaf2), Rd=new THREE.Color(0xff4d5e);
    for(let i=0;i<P.count;i++){ const y=P.getY(i), c=(y>.522&&y<.578)||(y>.592&&y<.648)?Rd:W; C[i*3]=c.r; C[i*3+1]=c.g; C[i*3+2]=c.b; }
    g.setAttribute("color", new THREE.BufferAttribute(C,3)); g.translate(0,-PC,0); return GE(g); })();
  const pinM=MS(0xffffff,{roughness:.3, vertexColors:true});
  const barGeo=GE(new THREE.BoxGeometry(LW+.24,.14,.07)), barM=MS(0xff5ce1,{emissive:0x551144}), deckGeo=GE(new THREE.BoxGeometry(LW-.1,.07,1.75)), deckM=MS(0xa597f2,{emissive:0x2a1866});
  const ballGeo=GE(new THREE.SphereGeometry(BR,28,20));
  /* 레인 하나 = 그룹(옆 레인은 x0 만큼 옆) · 핀 10 · 공 · 핀 정리 막대 · 핀 세우는 판 · (옆 레인) 전광판 */
  function mkLane(x0, bm, side){ const G=new THREE.Group(); G.position.x=x0; BOWL.add(G); const pins=[];
    for(let k=0;k<4;k++) for(let i=0;i<=k;i++){ const g=new THREE.Group(), m=new THREE.Mesh(pinGeo,pinM); m.castShadow=!LOW; g.add(m); G.add(g); pins.push({g, hx:(i-k/2)*.5, hz:HZ-k*.45, x:0,z:0,vx:0,vz:0, down:false, up:true, rot:0, ta:0, y:0, vy:0, spin:0, air:false, lift:0}); }
    bm.castShadow=!LOW; G.add(bm);
    const bar=new THREE.Mesh(barGeo,barM); bar.visible=false; G.add(bar); const deck=new THREE.Mesh(deckGeo,deckM); deck.position.set(0,1.75,HZ-.68); deck.visible=false; G.add(deck);
    const L={x0, G, pins, ball:bm, bar, deck, rolls:[], ph:"idle", bx:0, vx:0, vz:0, t:0, gutter:false, camZ:3.4, hit:false, rec:null, rp:null, sw:null, stk:0, on:false, wait:0, P:null, A:null, tag:null, nm:"", sk:"easy", pk:1, inS:1};
    if(side){ L.mc=document.createElement("canvas"); L.mc.width=512; L.mc.height=160; L.mg=L.mc.getContext("2d"); L.mt=new THREE.CanvasTexture(L.mc); L.mt.encoding=THREE.sRGBEncoding; disp.push(L.mt);
      const mm=new THREE.MeshBasicMaterial({map:L.mt}); disp.push(mm); L.mon=new THREE.Mesh(GE(new THREE.PlaneGeometry(3.2,1.0)), mm); L.mon.position.set(0,3.0,LZ+.2); G.add(L.mon); const fr=new THREE.Mesh(GE(new THREE.BoxGeometry(3.35,1.15,.08)), MS(0x111122)); fr.position.set(0,3.0,LZ+.15); G.add(fr); }
    pins.forEach(p=>{ p.x=p.hx; p.z=p.hz; placePin(p); }); return L; }
  function placePin(p){ const c=Math.abs(Math.cos(p.rot)), s=Math.abs(Math.sin(p.rot)); p.g.position.set(p.x, Math.max(.12, PC*c+.12*s)+p.y+(p.lift||0), p.z); AX.set(Math.cos(p.ta),0,-Math.sin(p.ta)); p.g.quaternion.setFromAxisAngle(AX, p.rot); }
  const ball=new THREE.Mesh(ballGeo, MS(0x5b3aff,{roughness:.2, map:tex(256,128,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,w,h); gr.addColorStop(0,"#ff5ce1"); gr.addColorStop(.5,"#5b3aff"); gr.addColorStop(1,"#3ea2ff"); g.fillStyle=gr; g.fillRect(0,0,w,h); g.fillStyle="#1d1640"; [[100,40],[124,36],[112,62]].forEach(([x,y])=>{ g.beginPath(); g.arc(x,y,7,0,7); g.fill(); }); g.fillStyle="#fff"; g.font="bold 30px sans-serif"; g.fillText("★",30,80); })}));
  const BW=mkLane(0, ball, false), PINS=BW.pins; BW.on=true; ball.position.set(0,BR,.3);
  /* 🤖 옆 레인 친구 (v731) — 왼쪽 Tom · 오른쪽 Lily · 공 색 다름 · pk = 겨냥하는 「포켓」 쪽 · inS = 캐릭터가 서는 쪽(가운데 레인 쪽) */
  const BOTV=[{nm:"Tom", col:"#d9661c", bc:0xff9a3d, av:{skin:1, hair:"short", hc:1, style:"overalls", top:3, pc:2, hat:"straw", acc:"none"}}, {nm:"Lily", col:"#13997a", bc:0x3dd9b0, av:{skin:0, hair:"bun", hc:6, style:"dress", top:6, pc:5, hat:"none", acc:"ribbon"}}];
  const SIDE=[-3.1,3.1].map((x,i)=>{ const v=BOTV[i], m=MS(v.bc,{roughness:.2}), L=mkLane(x, new THREE.Mesh(ballGeo, m), true); L.bv=v; L.nm=v.nm; L.pk=i?-1:1; L.inS=i?-1:1; L.ball.visible=false; return L; });
  const LANES=[BW, ...SIDE];
  /* (개선) 내 캐릭터 (공 오른쪽 · 등이 보이게) · 굴리는 팔 동작 · 겨냥 점선 · 꽃가루 */
  let MEAV=null; try{ MEAV=buildAvatar(api.av||{}); MEAV.g.rotation.y=Math.PI; MEAV.g.scale.setScalar(.7); BOWL.add(MEAV.g); MEAV.armR.rotation.set(.2,0,0); }catch(e){}
  const AV={sw:0, cheer:0, sad:0, t:0};
  const guide=new THREE.Group(); BOWL.add(guide); { const gm=new THREE.MeshBasicMaterial({color:0xff2f8a, transparent:true, opacity:.92}); disp.push(gm); const gg=GE(new THREE.CircleGeometry(.085,14));   /* (v729) 분홍 · 크게 (노란 레인 위 노란 점은 안 보였음) */ for(let i=0;i<14;i++){ const d=new THREE.Mesh(gg,gm); d.rotation.x=-Math.PI/2; guide.add(d); } } guide.visible=false;
  function guideTo(tx, tz){ const n=guide.children.length; guide.children.forEach((d,i)=>{ const t=(i+1)/n; d.position.set(BW.bx+(tx-BW.bx)*t, .02, .3+(tz-.3)*t); }); guide.visible=true; }
  const CONF=[]; function confetti(x,y,z,n){ const g=GE(new THREE.PlaneGeometry(.09,.14)); for(let i=0;i<n;i++){ const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:[0xff5ce1,0xffd23f,0x3dff9a,0x3ea2ff,0xffffff][i%5],side:THREE.DoubleSide})); disp.push(m.material);
      const a=Math.random()*Math.PI*2, sp=1+Math.random()*2.5; m.position.set(x,y,z); m.userData={vx:Math.cos(a)*sp, vy:2+Math.random()*3, vz:Math.sin(a)*sp*.6, s:(Math.random()-.5)*8, life:2.4}; scene.add(m); CONF.push(m); } }
  function confStep(dt){ for(let i=CONF.length-1;i>=0;i--){ const m=CONF[i], u=m.userData; u.vy-=4*dt; u.vx*=1-dt; m.position.x+=u.vx*dt; m.position.y+=u.vy*dt; m.position.z+=u.vz*dt; m.rotation.x+=u.s*dt; m.rotation.y+=dt*3; u.life-=dt; if(u.life<=0 || m.position.y<0){ scene.remove(m); CONF.splice(i,1); } } }
  function avOne(P, A, x, aim, dt){ A.t+=dt; P.g.position.set(x, 0, 1.05);
    if(A.sw>0){ A.sw=Math.max(0,A.sw-dt); const k=A.sw/.55; P.armR.rotation.set(-1.5+2.6*k*k,0,0); P.body.rotation.x=.18*(1-k); }
    else if(A.cheer>0){ A.cheer-=dt; P.armL.rotation.set(-2.7,0,.4); P.armR.rotation.set(-2.7,0,-.4); P.g.position.y=Math.abs(Math.sin(A.t*9))*.12; if(A.cheer<=0){ P.setExpr(P.expr0||"smile"); } }
    else if(A.sad>0){ A.sad-=dt; P.head.rotation.x=.35; P.armL.rotation.set(0,0,.1); P.armR.rotation.set(0,0,-.1); if(A.sad<=0){ P.head.rotation.x=0; P.setExpr(P.expr0||"smile"); } }
    else { P.body.rotation.x=0; P.armL.rotation.set(0,0,.12); P.armR.rotation.set(aim?.25+Math.sin(A.t*2)*.05:0,0,-.12); P.g.position.y=0; } }
  function avStep(dt){ if(MEAV) avOne(MEAV, AV, Math.max(-.4,Math.min(1.1,BW.bx+.7)), BW.ph==="aim", dt);   /* (v729) 조금 더 옆 · 작게 = 세로 휴대폰에서 레인·점선을 덜 가림 */
    SIDE.forEach(L=>{ if(!L.on || !L.P) return; const x=L.x0+(L.inS>0?Math.max(-.4,Math.min(1.1,L.bx+.7)):Math.max(-1.1,Math.min(.4,L.bx-.7))); avOne(L.P, L.A, x, L.ph==="aim", dt); if(L.tag) L.tag.position.set(x, 1.32, 1.05); }); }
  /* 이름표 (캔버스 글자 — 그림 문자 안 씀) */
  function tagSpr(t, col){ const tx=tex(256,76,(g,w,h)=>{ const r=30, x=6, y=6, W=w-12, H=h-12; g.beginPath(); g.moveTo(x+r,y); g.arcTo(x+W,y,x+W,y+H,r); g.arcTo(x+W,y+H,x,y+H,r); g.arcTo(x,y+H,x,y,r); g.arcTo(x,y,x+W,y,r); g.closePath(); g.fillStyle="#FFF6E3"; g.fill(); g.lineWidth=6; g.strokeStyle="#4A2E1F"; g.stroke();
      g.fillStyle=col; g.font="900 42px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText(t, w/2, h/2+2); });
    const m=new THREE.SpriteMaterial({map:tx, depthTest:false, transparent:true}); disp.push(m); const s=new THREE.Sprite(m); s.scale.set(.78,.23,1); s.renderOrder=5; return s; }
  function botAv(L){ const av=L.co?(L.fav||{}):L.bv.av, key=JSON.stringify(av);
    if(L.P && L.avk!==key){ try{ BOWL.remove(L.P.g); }catch(e){} try{ avFree(L.P); }catch(e){} L.P=null; }   /* 친구 = 친구 캐릭터 */
    if(!L.P){ try{ const P=buildAvatar(av); P.g.rotation.y=Math.PI; P.g.scale.setScalar(.7); BOWL.add(P.g); P.armR.rotation.set(.2,0,0); L.P=P; L.avk=key; }catch(e){} }
    L.A={sw:0, cheer:0, sad:0, t:Math.random()*5};
    if(L.tag && L.tagN!==L.nm){ try{ BOWL.remove(L.tag); }catch(e){} L.tag=null; } if(!L.tag){ L.tag=tagSpr(L.nm, L.bv.col); L.tagN=L.nm; BOWL.add(L.tag); } }
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
  R.innerHTML='<div class="spHit"></div><div class="spSc"></div><div class="spAim"></div><div class="spBig"></div><div class="spSay"></div><button class="spBtn"></button><div class="spPop"></div><div class="spRp">🔁 다시 보기 · 느리게</div><div class="spMenu"></div>';
  ["pointerdown","pointermove","pointerup"].forEach(t=>R.addEventListener(t, e=>e.stopPropagation()));
  const $=s=>R.querySelector(s), HIT=$(".spHit"), SC=$(".spSc"), AIM=$(".spAim"), BIG=$(".spBig"), SAY=$(".spSay"), BTN=$(".spBtn"), MENU=$(".spMenu"), POP=$(".spPop"), RP=$(".spRp");
  const say=t=>{ SAY.textContent=t||""; SAY.style.display=t?"":"none"; };
  function big(t, sub, s){ BIG.innerHTML=t+(sub?'<small>'+sub+'</small>':''); BIG.classList.add("on"); clearTimeout(big.h); big.h=setTimeout(()=>BIG.classList.remove("on"), (s||1.2)*1000*(fast?.05:1)); }
  /* ══ 메뉴 ══ */
  function menuShow(){ mode="menu"; TM.length=0; SC.style.display="none"; BTN.style.display="none"; AIM.style.display="none"; say(""); BOWL.visible=true; DART.visible=false; const r=REC();
    PUI.menu(U, {title:"볼링 · 다트", sub:"하나 골라 한 판!", cls:"spMenuVs", av:api.av, nick:api.nick, stats:[["🎳",r.bw,"볼링 최고"],["🎯",r.dt,"다트 최고"],["star",r.strikes,"스트라이크"]],
      deco:[["🎳","left:calc(50% - 132px);top:24%;transform:rotate(-14deg)"],["🎯","left:calc(50% + 70px);top:58%;font-size:34px"]],
      tiles:[{k:"bowl", emoji:"🎳", bg:"#c9b8ff", nm:"볼링", sub:({"0":"5프레임", co:"👫 친구랑"}[vsOf()]||"🤖 대결")+" · 최고 "+r.bw}, {k:"dart", emoji:"🎯", bg:"#ffd1e6", nm:"다트", sub:"9개 · 최고 "+r.dt}], n:2,
      seg:{items:[["0","🙋 혼자"],["easy","🤖 쉬움"],["normal","🤖 보통"],["hard","🤖 잘함"],["co","👫 친구"]], on:vsOf(), pick:v=>{ SET.vs=v; st("hyeng_proto_spset", SET); menuShow(); }},   /* (v731) 볼링 상대 (범퍼는 게임 안 단추) */
      pay:MG.payLeft("bowl"), onPick:k=>menuGo(k)}); }
  function menuGo(k){ TM.length=0; CONF.forEach(m=>scene.remove(m)); CONF.length=0; PUI.menuHide(U); if(k==="bowl"){ if(vsOf()==="co") coRoom(); else { CO=false; bowlStart(); } } else dartStart(); }
  BTN.addEventListener("click", ()=>{ if(mode==="bowl"){ SET.bump=SET.bump?0:1; st("hyeng_proto_spset", SET); BTN.textContent="🛡 범퍼 "+(SET.bump?"켬":"끔"); BUMP.forEach(b=>b.visible=!!SET.bump); } });

  /* ══ 🎳 볼링 ══ (v731) 레인 셋 — 나(가운데) · 🤖 Tom(왼쪽) · 🤖 Lily(오른쪽)가 같이 굴림 · 봇은 내 프레임보다 앞서지 않음 */
  const VSK=["0","easy","normal","hard","co"], vsOf=()=>VSK.indexOf(SET.vs)>=0?SET.vs:"easy";
  /* 봇 실력: sx = 서는 자리 흔들림 · sv = 옆으로 휘는 정도 · v0~v1 = 세기 · w0~w1 = 굴리기 전 기다림(초) */
  const SKILL={easy:{sx:.5, sv:.3, v0:6, v1:10, w0:1.4, w1:2.6}, normal:{sx:.38, sv:.21, v0:7, v1:11.5, w0:1.1, w1:2.2}, hard:{sx:.11, sv:.06, v0:9.5, v1:13, w0:.9, w1:1.8}};
  const gauss=()=>{ let s=0; for(let i=0;i<3;i++) s+=Math.random()*2-1; return s; };   /* 표준편차 1 */
  let endQ=false, shk=0;
  const RDM=(()=>{ try{ return matchMedia("(prefers-reduced-motion: reduce)").matches; }catch(e){ return false; } })();
  const clampX=x=>Math.max(-LW/2+BR, Math.min(LW/2-BR, x));
  function bowlStart(){ mode="bowl"; BOWL.visible=true; DART.visible=false; SC.style.display=""; BTN.style.display=""; BTN.textContent="🛡 범퍼 "+(SET.bump?"켬":"끔"); BUMP.forEach(b=>b.visible=!!SET.bump);
    const vs=CO?"co":(vsOf()==="co"?"easy":vsOf()); endQ=false; shk=0;
    SIDE.forEach((L,i)=>{ const fr=CO?COL[i]:null; L.co=fr?fr.k:null; L.fav=fr?fr.av:null; L.nm=fr?fr.n:L.bv.nm; L.on=CO?!!fr:vs!=="0"; L.sk=vs; L.seen=-1; L.gone=0; L.left=0; L.bump=false; L.cw=0;
      L.rolls=[]; L.stk=0; L.sw=null; L.bar.visible=L.deck.visible=false; L.ph="idle"; setPins(L,true); L.ball.visible=false; if(L.on) botAv(L); if(L.P) L.P.g.visible=L.on; if(L.tag) L.tag.visible=L.on; sidePaint(L); if(L.on) readyLane(L); });
    BW.rolls=[]; BW.mk=[]; BW.th=null; BW.stk=0; BW.sw=null; BW.rp=null; BW.bar.visible=BW.deck.visible=false; if(RET) RET.visible=vs==="0"; setPins(BW,true); readyBall(); sheet(); }   /* 공 돌아오는 기계는 혼자일 때만 (오른쪽 Lily 를 가림) */
  function setPins(L, all){ L.pins.forEach(p=>{ if(all) p.up=true; if(p.up){ Object.assign(p,{down:false, x:p.hx, z:p.hz, vx:0, vz:0, rot:0, ta:0, y:0, vy:0, spin:0, air:false, lift:0}); p.g.visible=true; placePin(p); } else p.g.visible=false; }); }
  function readyBall(){ BW.ph="aim"; BW.bx=0; BW.vx=BW.vz=0; BW.t=0; BW.gutter=false; BW.hit=false; BW.rec=null; ball.position.set(0,BR,.3); ball.rotation.set(0,0,0); guide.visible=false; camP=null; ball.visible=true; arrowM.visible=true; BW.camZ=3.4; const f=rollsInFrame(BW.rolls); say((f.f+1)+"프레임 "+(f.k+1)+"번째 · "+(SIDE.some(L=>L.on)?"다 같이! 위로 쓱 👆":"위로 쓱! 또는 콕 👆")); }
  function readyLane(L){ L.ph="aim"; L.aim=L.co?[0,0,9]:botAim(L); L.bx=L.aim[0]; L.vx=L.vz=0; L.t=0; L.gutter=false; L.hit=false; L.ball.position.set(L.bx,BR,.3); L.ball.visible=true; const S=SKILL[L.sk]||SKILL.easy; L.wait=(S.w0+Math.random()*(S.w1-S.w0))*(fast?.02:1); }
  function sheet(){ const act=LANES.filter(L=>L.on);
    if(act.length<2){ SC.classList.remove("multi"); const s=bowlScore(BW.rolls), f=rollsInFrame(BW.rolls).f; SC.innerHTML=s.marks.map((m,i)=>'<div class="'+(i===f && mode==="bowl"?"cur":"")+'"><small>'+(i+1)+'</small><div class="m">'+m.map(x=>'<span>'+x+'</span>').join("")+'</div><div class="t">'+(s.out[i]==null?"":s.out[i])+'</div></div>').join("")+'<div class="tot"><small>합계</small><div class="m"></div><div class="t">'+s.total+'</div></div>'; }
    else { SC.classList.add("multi"); const T=act.map(L=>bowlScore(L.rolls).total), top=Math.max(...T);
      SC.innerHTML=act.map((L,j)=>{ const s=bowlScore(L.rolls), f=bowlDone(L.rolls)?-1:rollsInFrame(L.rolls).f; return '<span class="rw'+(L===BW?' me':'')+(T[j]===top && top>0?' lead':'')+'"><span class="nm">'+esc(L===BW?(api.nick||"나"):L.nm)+'</span>'+s.marks.map((m,i)=>'<span class="f'+(i===f?' cur':'')+'"><i>'+m.join(" ")+'</i><b>'+(s.out[i]==null?"":s.out[i])+'</b></span>').join("")+'<span class="f tot">'+s.total+'</span></span>'; }).join(""); }
    if(!monBig) monPaint(); }
  let monBig=0;
  function sidePaint(L, big){ if(!L.mg) return; const g=L.mg, w=512, h=160; g.fillStyle="#08061a"; g.fillRect(0,0,w,h); g.fillStyle="rgba(255,255,255,.05)"; for(let y=0;y<h;y+=4) g.fillRect(0,y,w,2); g.textAlign="center"; g.textBaseline="middle";
    if(!L.on){ g.fillStyle="#4a3f80"; g.font="900 64px Jua,sans-serif"; g.fillText("BOWLING", w/2, h/2+4); }
    else if(big){ g.font="900 92px Jua,sans-serif"; g.fillStyle=big==="SPARE!"?"#3dff9a":big==="STRIKE!"?"#ffd23f":"#ff5ce1"; g.shadowColor=g.fillStyle; g.shadowBlur=24; g.fillText(big,w/2,h/2+6); g.shadowBlur=0; }
    else { const sc=bowlScore(L.rolls); g.fillStyle=L.bv.col; g.font="900 44px Jua,sans-serif"; g.textAlign="left"; g.fillText(L.nm, 22, 46); g.textAlign="center"; g.font="bold 24px sans-serif";
      for(let i=0;i<NF;i++){ const x=22+i*74; g.strokeStyle="#3ea2ff"; g.lineWidth=2; g.strokeRect(x,84,68,58); g.fillStyle="#fff"; g.fillText((sc.marks[i]||[]).join(" "),x+34,104); g.fillStyle="#ffd23f"; g.fillText(sc.out[i]==null?"":sc.out[i],x+34,130); }
      g.fillStyle="#ff5ce1"; g.font="900 64px sans-serif"; g.textAlign="right"; g.fillText(sc.total, w-22, 52); }
    L.mt.needsUpdate=true; }
  function throwLane(L, x, vx, vz){ L.bx=clampX(x); L.vx=Math.max(-1.6,Math.min(1.6,vx)); L.vz=-Math.max(5, Math.min(16, vz)); L.ph="roll"; L.t=0; L.hit=false; L.gutter=false; L.ball.position.set(L.bx, BR, .3); L.ball.visible=true; if(L.A) L.A.sw=.55; try{ SFX.noise(1.2, L===BW?.05:.016, 300, .5, 150); }catch(e){} }
  function throwBall(x, vx, vz){ if(mode!=="bowl" || BW.ph!=="aim") return false; throwLane(BW, x, vx, vz); BW.th={i:BW.rolls.length, x:+BW.bx.toFixed(3), vx:+BW.vx.toFixed(3), vz:+(-BW.vz).toFixed(3)}; BW.rec=[]; arrowM.visible=false; guide.visible=false; AV.sw=.55; say(""); return true; }
  /* 봇 겨냥: 처음 공 = 포켓(가운데 살짝 옆) · 두 번째 공 = 남은 핀 가운데 · 실력만큼 흔들림 */
  function botAim(L){ const S=SKILL[L.sk]||SKILL.easy, up=L.pins.filter(p=>p.up && p.g.visible), tx=up.length>=10||!up.length ? L.pk*.16 : up.reduce((s,p)=>s+p.hx,0)/up.length;
    return [clampX(tx+gauss()*S.sx), gauss()*S.sv, S.v0+Math.random()*(S.v1-S.v0)]; }
  function botTick(L, dt){ if(L.ph!=="aim") return; const mf=bowlDone(BW.rolls)?NF:rollsInFrame(BW.rolls).f, lf=rollsInFrame(L.rolls).f; if(lf>mf) return;   /* 내 프레임보다 앞서지 않음 */
    L.wait-=dt*(lf<mf?2.2:1); if(L.wait>0) return; const a=L.aim||botAim(L); throwLane(L, a[0], a[1], a[2]); }
  /* 맞으면 튀어 오르며 돎 (dv = 핀이 받은 빠르기) */
  function pop(p, dv){ if(dv<2) return; const k=Math.min(1,(dv-2)/8); if(!p.air){ p.vy=.8+k*2.5+Math.random()*.5; p.air=true; } else p.vy=Math.max(p.vy, .5+k*1.4); p.spin=(Math.random()<.5?-1:1)*(5+k*10+Math.random()*3); p.down=true; p.ta=Math.atan2(p.vx,p.vz)||p.ta||0; }
  function laneStep(L, dt){ const me=L===BW;
    if(L.ph==="aim"){ if(me){ const t=performance.now()/1000; arrowM.position.set(BW.bx, .03, -1.0+Math.sin(t*4)*.08); } return; }
    if(L.ph!=="roll" && L.ph!=="count" || L.sw) return; const roll=L.ph==="roll", H=1/240, b=L.ball.position, P=L.pins; let n=Math.ceil(dt/H); const h=dt/n;
    while(n--){
      if(roll){ L.t+=h;
        if(L.vz<0 || Math.abs(L.vx)>0){ b.x+=L.vx*h; b.z+=L.vz*h; L.ball.rotation.x+=L.vz*h/BR; }
        if(!L.gutter){ if(me ? SET.bump : L.bump){ if(b.x<-LW/2+BR){ b.x=-LW/2+BR; L.vx=Math.abs(L.vx)*.6; try{ SFX.tone(240,.05,"square",.03); }catch(e){} } if(b.x>LW/2-BR){ b.x=LW/2-BR; L.vx=-Math.abs(L.vx)*.6; try{ SFX.tone(240,.05,"square",.03); }catch(e){} } }
          else if(Math.abs(b.x)>LW/2-BR*.4 && b.z>HZ+.4){ L.gutter=true; L.vx=0; b.x=Math.sign(b.x)*(LW/2+.16); b.y=BR-.12; if(me) big("😅 도랑!", "", 1); } }
        if(b.z<LZ+.1){ L.vz=0; L.vx=0; L.ball.visible=false; }
        else if(L.vz>-BMIN){ L.vz=-BMIN; }   /* (v729) 핀에 부딪혀도 공은 앞으로 (전: 느린 공이 거의 멈춰 5초 · 가끔 거꾸로 굴러와 19초 기다림) */
        /* 공 → 핀 */
        if(!L.gutter && L.ball.visible) P.forEach(p=>{ if(!p.g.visible) return; const dx=p.x-b.x, dz=p.z-b.z, d=Math.hypot(dx,dz), rr=BR+PR; if(d<rr && d>0){ const nx=dx/d, nz=dz/d, ov=rr-d; p.x+=nx*ov; p.z+=nz*ov; const vn=(L.vx-p.vx)*nx+(L.vz-p.vz)*nz;
          if(vn>0){ const j=1.5*vn/(1/6+1/1.5); p.vx+=j*nx/1.5; p.vz+=j*nz/1.5; L.vx-=j*nx/6; L.vz-=j*nz/6; pop(p, j/1.5); if(!L.hit){ L.hit=true; crash(L, vn); } hitSnd(L); } } }); }
      /* 핀 → 핀 */
      for(let i=0;i<P.length;i++){ const a=P[i]; if(!a.g.visible) continue; for(let j=i+1;j<P.length;j++){ const c=P[j]; if(!c.g.visible) continue; const dx=c.x-a.x, dz=c.z-a.z, d=Math.hypot(dx,dz), rr=PR*2*(a.down||c.down?1.15:1); if(d<rr && d>0){ const nx=dx/d, nz=dz/d, ov=rr-d; a.x-=nx*ov/2; a.z-=nz*ov/2; c.x+=nx*ov/2; c.z+=nz*ov/2; const vn=(a.vx-c.vx)*nx+(a.vz-c.vz)*nz; if(vn>0){ const jj=vn*.75; a.vx-=jj*nx; a.vz-=jj*nz; c.vx+=jj*nx; c.vz+=jj*nz; if(jj>2.4){ pop(c, jj*.7); pop(a, jj*.45); } hitSnd(L); } } } }
      P.forEach(p=>{ if(!p.g.visible) return; p.x+=p.vx*h; p.z+=p.vz*h; const sp=Math.hypot(p.vx,p.vz); if(sp>0){ const k=Math.max(0,sp-(p.air?2.4:3.5)*h)/sp; p.vx*=k; p.vz*=k; } if(!p.down && (sp>.9 || Math.hypot(p.x-p.hx,p.z-p.hz)>.16)){ p.down=true; p.ta=Math.atan2(p.vx,p.vz)||0; }
        if(p.air){ p.y+=p.vy*h; p.vy-=9.8*h; p.rot+=p.spin*h; if(p.y<=0){ p.y=0; if(p.vy<-1.2){ p.vy=-p.vy*.3; p.spin*=.45; try{ if(me) SFX.tone(700+Math.random()*300,.04,"triangle",.02); }catch(e){} } else { p.vy=0; p.air=false; } } }
        if(Math.abs(p.x)>LW/2+.3 || p.z<LZ){ p.vx*=.5; p.vz*=.5; } }); }
    P.forEach(p=>{ if(!p.g.visible) return; if(p.down && !p.air){ const tg=Math.PI/2+Math.round((p.rot-Math.PI/2)/Math.PI)*Math.PI, d=tg-p.rot; p.rot+=Math.sign(d)*Math.min(Math.abs(d), dt*7); } placePin(p); });
    if(!roll) return;
    if(me && L.rec && !fast && L.rec.length<480 && (L.hit || b.z<HZ+2.6)) L.rec.push(snap(L));
    const moving=P.some(p=>p.g.visible && (p.air || Math.hypot(p.vx,p.vz)>.05));
    if((b.z<LZ+.2 || L.vz===0) && (!moving || L.t>7) || L.t>9){ L.ph="count"; later(fast?.02:.6, ()=>countPins(L)); } }
  let hitT=0; function hitSnd(L){ const n=performance.now(); if(n-hitT<45) return; hitT=n; const v=L===BW?1:.3; try{ SFX.tone(900+Math.random()*500,.05,"square",.03*v); SFX.noise(.08,.05*v,2200); }catch(e){} }
  function crash(L, sp){ const v=(L===BW?.12:.035)*Math.min(1, sp/11); try{ SFX.noise(.5, v, 1300, .6, 240); SFX.tone(120, .22, "sine", v, 55); }catch(e){} if(L===BW && sp>8 && !RDM) shk=Math.max(shk,.35); }
  function countPins(L){ const me=L===BW; let fgot=null;
    if(L.co){ const p=coP(L), ro=(p && p.ro)||[], i=L.rolls.length; if(ro.length<=i){ if(++L.cw<40 && L.on && !L.left){ later(.25, ()=>countPins(L)); return; } } else { L.cw=0; fgot=ro[i]; coMask(L, (p.mk||[])[i]); } }   /* 친구 결과가 올 때까지 (8초) */
    const before=L.pins.filter(p=>p.up).length; L.pins.forEach(p=>{ if(p.up && p.down) p.up=false; }); const after=L.pins.filter(p=>p.up).length, got=fgot!=null?fgot:before-after; L.rolls.push(got);
    if(me){ let ms=0; L.pins.forEach((p,j)=>{ if(p.up) ms|=1<<j; }); (BW.mk||(BW.mk=[])).push(ms); }
    const strike=got===10 && before===10, spare=!strike && after===0; L.stk=strike?L.stk+1:0;
    if(me){ const r=REC();
      if(strike){ const k=L.stk, T=k>=3?"TURKEY!":k===2?"DOUBLE!":"STRIKE!"; big(T, k>=3?"스트라이크 "+k+"번 연속! 🦃":k===2?"스트라이크 2번 연속 🔥":"스트라이크 🎉", 1.6); r.strikes++; st("hyeng_proto_spr", r); try{ SFX.win(); }catch(e){} fx(T, k>=3?120:k===2?95:70); }
      else if(spare){ big("SPARE!", "스페어 👏", 1.4); try{ SFX.clear(); }catch(e){} fx("SPARE!", 36); }
      else if(got===0){ big("0", "괜찮아요!", 1); AV.sad=1.4; if(MEAV) MEAV.setExpr("wow"); }
      else { big(String(got), got>=7?"좋아요!":"핀 "+got+"개", 1); if(got>=7){ AV.cheer=.8; if(MEAV) MEAV.setExpr("grin"); try{ SFX.tone(660,.12,"triangle",.05); SFX.tone(990,.16,"triangle",.05,0,.09); }catch(e){} } } }
    else botSay(L, strike, spare, got);
    sheet(); if(!me) sidePaint(L, strike?"STRIKE!":spare?"SPARE!":null); if(!me && (strike||spare)) later(1.6, ()=>sidePaint(L));
    const fin=bowlDone(L.rolls), nf=fin?null:rollsInFrame(L.rolls);
    const go=()=>{ if(fin){ laneDone(L); return; } later(fast?.05:.3, ()=>sweep(L, nf.reset, ()=>{ if(me){ readyBall(); sheet(); } else readyLane(L); })); };
    if(me && strike && !fast && BW.rec && BW.rec.length>=8){ later(.95, ()=>{ if(!rpStart(go)) go(); }); return; }   /* STRIKE 글자가 사라질 즈음 다시 보기 */
    go(); }
  function laneDone(L){ L.ph="done"; L.ball.visible=false; if(L===BW){ BW.camZ=3.4; if(SIDE.some(S=>S.on && S.ph!=="done")) say("🎳 친구들이 마지막 프레임을 굴려요…"); } checkEnd(); }
  function checkEnd(){ if(endQ || !LANES.every(L=>!L.on || L.ph==="done")) return; endQ=true; later(fast?.05:1.6, ()=>{ say(""); bowlEnd(); }); }
  function botSay(L, strike, spare, got){ const A=L.A||{}; let t="";
    if(strike){ t=L.stk>=3?L.nm+" 터키! 🦃":L.stk===2?L.nm+" 더블! 🔥":L.nm+" 스트라이크! 🎳"; A.cheer=1.4; if(L.P) L.P.setExpr("grin"); }
    else if(spare){ t=L.nm+" 스페어! 👏"; A.cheer=1; }
    else if(got===0 && !L.co && Math.random()<.6){ t=L.nm+" 앗, 0개 😅"; A.sad=1.2; if(L.P) L.P.setExpr("wow"); }
    if(t) popMsg(t); }
  function popMsg(t){ POP.textContent=t; try{ const r=SC.getBoundingClientRect(), u=U.getBoundingClientRect(), multiR=SC.classList.contains("multi") && innerWidth>innerHeight && innerHeight<=620; POP.style.top=Math.round((multiR?r.top:r.bottom)-u.top+(multiR?0:8))+"px"; POP.style.left=multiR?Math.round(Math.min(u.width/2, r.left-u.left-POP.offsetWidth/2-10))+"px":""; }catch(e){}   /* 가로 = 오른쪽 위 점수판 왼쪽에 */ POP.classList.add("on"); clearTimeout(popMsg.h); popMsg.h=setTimeout(()=>POP.classList.remove("on"), 1800*(fast?.05:1)); }
  /* 핀 정리 (v731) — 판이 내려와 서 있는 핀을 들고 · 막대가 쓰러진 핀을 쓸어 내고 · 핀(새로 10개 또는 남은 핀)을 내려놓음 */
  const SWT=.8, EZ=(t,a,b)=>{ const k=Math.max(0,Math.min(1,(t-a)/(b-a))); return k*k*(3-2*k); };
  function sweep(L, reset, cb){ if(fast){ setPins(L, reset); cb(); return; } L.sw={t:0, reset, cb, set:false}; L.deck.visible=L.bar.visible=true; L.deck.position.y=1.75; L.bar.position.set(0,1.5,HZ+.75); }
  function sweepStep(L, dt){ const S=L.sw; if(!S) return; S.t+=dt/SWT; const t=S.t, P=L.pins;
    const dy=t<.22?1.75-.92*EZ(t,0,.22):t<1?.83+.47*EZ(t,.22,.42):t<1.25?1.3-.47*EZ(t,1,1.25):.83+.92*EZ(t,1.25,1.45); L.deck.position.y=dy;
    if(t>=1 && !S.set){ S.set=true; setPins(L, S.reset); }
    const bar=L.bar.position; if(t<.5){ bar.y=1.5-1.41*EZ(t,.3,.5); bar.z=HZ+.75; } else if(t<.95){ bar.y=.09; bar.z=HZ+.75+(LZ+.15-HZ-.75)*EZ(t,.5,.95); } else { bar.y=.09+1.41*EZ(t,.95,1.1); }
    const lift=t>=.22 && t<1.25 ? dy-.83 : 0;
    P.forEach(p=>{ if(!p.g.visible) return; if(p.up && !p.down){ if(p.lift!==lift){ p.lift=lift; placePin(p); } return; }
      if(t<.95){ if(bar.y<.3 && p.z>bar.z-.15){ p.z=bar.z-.15; placePin(p); } } else if(!S.set) p.g.visible=false; });
    if(t>=.95 && L.ball.visible && L.ph!=="aim") L.ball.visible=false;
    if(t>=1.45){ L.sw=null; L.deck.visible=L.bar.visible=false; P.forEach(p=>{ p.lift=0; if(p.g.visible) placePin(p); }); S.cb(); } }
  /* 🔁 스트라이크 다시 보기 (v731) — 굴리는 동안 핀 쪽 장면을 적어 두었다가 옆에서 느리게 · 누르면 건너뜀 */
  const RPS=.3;
  function snap(L){ const P=L.pins, a=new Float32Array(5+P.length*8), b=L.ball.position; a[0]=b.x; a[1]=b.y; a[2]=b.z; a[3]=L.ball.visible?1:0; a[4]=L.ball.rotation.x;
    P.forEach((p,i)=>{ const o=5+i*8, g=p.g; a[o]=g.position.x; a[o+1]=g.position.y; a[o+2]=g.position.z; a[o+3]=g.quaternion.x; a[o+4]=g.quaternion.y; a[o+5]=g.quaternion.z; a[o+6]=g.quaternion.w; a[o+7]=g.visible?1:0; }); return {t:L.t, a, h:L.hit}; }
  function rpApply(s){ const a=s.a; ball.position.set(a[0],a[1],a[2]); ball.visible=!!a[3]; ball.rotation.x=a[4]; PINS.forEach((p,i)=>{ const o=5+i*8, g=p.g; g.position.set(a[o],a[o+1],a[o+2]); g.quaternion.set(a[o+3],a[o+4],a[o+5],a[o+6]); g.visible=!!a[o+7]; }); }
  function rpStart(cb){ const R=BW.rec; if(fast || !R || R.length<8) return false; const h=R.find(s=>s.h); if(!h) return false; const t0=Math.max(R[0].t, h.t-.12), t1=Math.min(R[R.length-1].t, h.t+1.5);
    BW.rp={t:t0, t0, t1, i:0, cb, b:ball.position.clone(), bv:ball.visible, br:ball.rotation.x, pv:PINS.map(p=>p.g.visible)}; RP.classList.add("on"); camP=null; return true; }
  function rpStep(dt){ const S=BW.rp, R=BW.rec; S.t+=dt*RPS; while(S.i+1<R.length && R[S.i+1].t<=S.t) S.i++; rpApply(R[S.i]); if(S.t>=S.t1) rpEnd(); }
  function rpEnd(){ const S=BW.rp; if(!S) return; BW.rp=null; RP.classList.remove("on"); ball.position.copy(S.b); ball.visible=S.bv; ball.rotation.x=S.br; PINS.forEach((p,i)=>{ p.g.visible=S.pv[i]; placePin(p); }); camP=null; S.cb(); }
  function fx(t, n){ confetti(0,.8,HZ-.6,LOW?Math.round(n/2):n); AV.cheer=1.6; if(MEAV) MEAV.setExpr("grin"); monBig=1; monPaint(t); later(fast?.05:1.6, ()=>{ monBig=0; monPaint(); }); }
  function bowlEnd(){ const s=bowlScore(BW.rolls).total, r=REC(), best=s>r.bw; r.bw=Math.max(r.bw,s); const coins=s>=100?9:s>=70?7:s>=40?5:3, sk=BW.rolls.filter(x=>x===10).length;
    const act=LANES.filter(L=>L.on), vs=act.length>1, tot=act.map(L=>[L, bowlScore(L.rolls).total]).sort((a,b)=>b[1]-a[1]), rank=1+tot.filter(x=>x[1]>s).length;
    if(vs && rank===1) r.vw=(r.vw|0)+1; st("hyeng_proto_spr", r);
    const got=PUI.award(api, {title:s+"점", sub:"볼링", rows:null, coins, again:{go:"bowl"}, upd:(b,t)=>{ b.bw=Math.max(b.bw|0,s); }}), left=MG.payLeft("bowl");
    const who=tot.map(([L,t])=>(L===BW?"나":esc(L.nm))+" "+t).join(" · ");
    PUI.result(U, {res:vs&&rank>1?"draw":"win", stars:s>=100?3:s>=70?2:s>=40?1:0, title:vs?(rank===1?(best?"1등! 내 최고 기록!":"1등! 🏆"):rank+"등 · "+s+"점"):(best?"내 최고 기록!":s+"점!"),
      sub:vs?(CO?"👫 친구랑":"🤖 "+({easy:"쉬움",normal:"보통",hard:"잘함"}[act[1].sk]||""))+" · "+who:"볼링 5프레임 · "+(SET.bump?"🛡 범퍼":"범퍼 없이"), av:api.av,
      rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"],["🎳", s, "점", best],["star", sk, "스트라이크"]], prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3},
      onAgain:()=>api.restart({go:"bowl"}), onMenu:()=>api.restart({}), onOut:()=>MG.exit()}); }
  /* ══ 👫 친구랑 (v731) — 방(MG.room) · 셋까지 · 내 레인은 내 기기가 굴리고, 옆 레인 = 친구가 보낸 「던진 값」을 그대로 굴려 보여 줌 · 핀은 친구가 보낸 결과(남은 핀)로 맞춤 ══ */
  let RM=null, CO=false, COL=[];
  function coRoom(){ mode="bowl"; CO=false; COL=[]; PUI.menuHide(U); SC.style.display="none"; BTN.style.display="none"; say(""); BOWL.visible=true; DART.visible=false; BW.ph="idle"; arrowM.visible=false; ball.position.set(0,BR,.3); ball.visible=true; camP=null;
    SIDE.forEach(L=>{ L.on=false; L.ph="idle"; L.ball.visible=false; if(L.P) L.P.g.visible=false; if(L.tag) L.tag.visible=false; sidePaint(L); });
    if(RM){ try{ RM.dispose(); }catch(e){} RM=null; }
    RM=MG.room(api, {pre:"mgb", title:"볼링 같이 하기", ic:"🎳", max:3, fill:false, wait:6000, send:.25, poll:.3, back:()=>{ coQuit(); menuShow(); }});
    RM.node=()=>({av:api.av||null, ro:BW.rolls.slice(), mk:(BW.mk||[]).slice(), th:BW.th||null, bp:SET.bump?1:0, dn:CO && BW.ph==="done"?1:0});
    { const st0=RM.start; RM.start=async()=>{ const d=RM.d||{}, t=RM.now(); let ro=Object.keys(d.p||{}).filter(k=>k===RM.code || (d.p[k] && t-(d.p[k].t||0)<20000)); if(ro.indexOf(RM.code)<0) ro.push(RM.code); ro=ro.sort().slice(0,3);   /* (v729 컬러팡처럼) 느린 와이파이 친구도 20초 */
      if(ro.length<2){ api.msg("친구가 들어오면 시작할 수 있어요 👫", 1500); return; } try{ await NET.patch(RM.path+"/h", {ro}); }catch(e){} if(RM.d && RM.d.h) RM.d.h.ro=ro; return st0(); }; }
    RM.onStart=(h, Lv)=>coBegin(h, Lv); }
  function coQuit(){ if(RM){ try{ RM.dispose(); }catch(e){} } RM=null; CO=false; COL=[]; }
  function coBegin(h, Lv){ const ro=(h.ro && h.ro.length ? h.ro : Lv.map(p=>p.k)).slice(0,3), PD=(RM.d && RM.d.p)||{};
    if(ro.indexOf(RM.code)<0){ api.msg("🙈 시작할 때 자리에 못 들어갔어요<small>다음 판에 같이 해요</small>", 2200); try{ RM.leave(true); }catch(e){} return; }
    COL=ro.filter(c=>c!==RM.code).map(k=>({k, n:String((PD[k] && PD[k].n)||(Lv.find(q=>q.k===k)||{}).n||"친구").slice(0,8), av:(PD[k] && PD[k].av)||{}}));
    CO=true; bowlStart(); }
  const coP=L=>RM && RM.d && RM.d.p ? RM.d.p[L.co] : null;
  /* 친구 결과(남은 핀 묶음)로 내 화면 핀을 맞춤 — 비트 j = j번 핀이 서 있음 */
  function coMask(L, ms){ if(typeof ms!=="number") return; L.pins.forEach((p,j)=>{ if(!p.up) return; const st=!!((ms>>j)&1); if(!st && !p.down){ p.down=true; p.ta=Math.random()*6.28; } else if(st && p.down){ p.down=false; } }); }
  /* 많이 밀렸거나 다시 붙었을 때: 굴리는 모습 없이 점수 · 핀만 바로 맞춤 */
  function coSync(L, p){ L.rolls=(p.ro||[]).slice(); L.stk=0; for(let i=L.rolls.length-1;i>=0 && L.rolls[i]===10;i--) L.stk++; L.sw=null; L.bar.visible=L.deck.visible=false; L.seen=L.rolls.length-1;
    if(bowlDone(L.rolls)){ sheet(); sidePaint(L); laneDone(L); return; }
    const nf=rollsInFrame(L.rolls), ms=(p.mk||[])[L.rolls.length-1]; if(nf.reset || typeof ms!=="number") setPins(L,true); else { L.pins.forEach((q,j)=>{ q.up=!!((ms>>j)&1); }); setPins(L,false); }
    readyLane(L); sheet(); sidePaint(L); }
  function coTick(dt){ if(!RM) return; try{ RM.tick(dt); }catch(e){} if(!CO || mode!=="bowl") return; const live=RM.live(true).map(p=>p.k);
    SIDE.forEach(L=>{ if(!L.on || !L.co || L.ph==="done") return; const p=coP(L);
      L.gone=(!p || live.indexOf(L.co)<0) ? (L.gone||0)+dt : 0;
      if(L.gone>12){ popMsg(L.nm+" 나갔어요 👋"); L.left=1; laneDone(L); sheet(); return; }
      if(!p) return; const ro=p.ro||[]; L.bump=!!p.bp;
      if(ro.length>L.rolls.length+1 || (L.ph==="aim" && ro.length>L.rolls.length)){ coSync(L, p); return; }
      if(L.ph==="aim" && p.th && p.th.i===L.rolls.length && p.th.i!==L.seen){ L.seen=p.th.i; throwLane(L, p.th.x, p.th.vx, p.th.vz); } }); }
  /* 볼링 조작: 위로 쓱(빠르기 · 방향) · 콕 = 그쪽으로 */
  const ray=new THREE.Raycaster(), v2=new THREE.Vector2(), pl=new THREE.Plane(new THREE.Vector3(0,1,0),0), hitP=new THREE.Vector3();
  function lanePt(e){ const r=HIT.getBoundingClientRect(); v2.set((e.clientX-r.left)/r.width*2-1, -((e.clientY-r.top)/r.height*2-1)); ray.setFromCamera(v2,cam); return ray.ray.intersectPlane(pl,hitP)?hitP.clone():null; }
  let pd=null, trail=[];
  HIT.addEventListener("pointerdown", e=>{ e.preventDefault(); if(mode==="bowl" && BW.rp){ BW.rp.t=BW.rp.t1; return; }   /* 다시 보기 건너뛰기 */ pd={x:e.clientX, y:e.clientY, t:performance.now()}; trail=[pd]; if(mode==="dart") dartDown(e); });
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
  function dartEnd(){ const s=DT.sum, r=REC(), best=s>r.dt; r.dt=Math.max(r.dt,s); st("hyeng_proto_spr", r); AIM.style.display="none"; const coins=s>=300?9:s>=180?7:s>=90?5:3, top=Math.max(...DT.rnd.map(q=>q.s));
    const got=PUI.award(api, {title:s+"점", sub:"다트", rows:null, coins, again:{go:"dart"}, upd:(b,t)=>{ b.dt=Math.max(b.dt|0,s); }}), left=MG.payLeft("bowl");
    PUI.result(U, {res:"win", stars:s>=250?3:s>=150?2:s>=80?1:0, title:best?"내 최고 기록!":s+"점!", sub:"다트 9개 · 가장 큰 한 방 "+top+"점", av:api.av,
      rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"],["🎯", s, "점", best],["star", DT.rnd.filter(q=>q.k==="bull").length, "불"]],
      extra:DT.rnd.filter(q=>q.w).map(q=>'<b style="font-family:var(--en)">'+q.w+'</b>').join(" · "), prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3},
      onAgain:()=>api.restart({go:"dart"}), onMenu:()=>api.restart({}), onOut:()=>MG.exit()}); }
  function dartStep(dt){ DT.wob+=dt; if(DT.fly){ const f=DT.fly; f.t=Math.min(1,f.t+dt*(fast?20:3.2)); const p=f.from.clone().lerp(f.to,f.t); p.y+=Math.sin(f.t*Math.PI)*.35; f.m.position.copy(p); f.m.lookAt(f.to.x, f.to.y, f.to.z-1); f.m.rotateY(Math.PI); if(f.t>=1){ f.m.position.copy(f.to); f.m.rotation.set(-.22+Math.random()*.1,(Math.random()-.5)*.35,0); dartLand(); } }
    if(mode==="dart" && !DT.fly && DT.n<DN){ hand.visible=true; const w=wob(); const ax=(DT.aimX+w[0])*DB.R, ay=DB.y+(DT.aimY+w[1])*DB.R; hand.position.set(cam.position.x+.34, cam.position.y-.42, cam.position.z-1.1); hand.lookAt(ax, ay, DB.z); hand.rotateY(Math.PI); } else hand.visible=false;
    if(mode==="dart" && !DT.fly && DT.n<DN){ const w=wob(), s=toScr(DT.aimX+w[0], DT.aimY+w[1]); AIM.style.left=s[0]+"px"; AIM.style.top=s[1]+"px"; AIM.style.display="block"; } else AIM.style.display="none"; }
  /* ══ 카메라 ══ */
  let camP=null, camT=null;
  function fitCam(){ const w=innerWidth, h=innerHeight, asp=w/h; cam.aspect=asp;
    if(mode==="dart"){ const need=DB.R*2.9, t=Math.tan(cam.fov*Math.PI/360), d=Math.max(need/2/t, need/2/t/asp); cam.position.set(0, DB.y, DB.z+d); cam.lookAt(0, DB.y-.05, DB.z); }
    else { const b=ball.position, portrait=asp<.9; cam.fov=portrait?62:50;
      if(BW.rp){ const S=BW.rp, k=Math.min(1,(S.t-S.t0)/Math.max(.01,S.t1-S.t0)); cam.position.set(2.45-.45*k, 1.25-.1*k, HZ+2.05-.25*k); cam.lookAt(-.08,.28,HZ-.7); cam.updateProjectionMatrix(); return; }   /* 🔁 다시 보기 = 옆에서 가까이 */
      const pinCam=(BW.ph==="roll"||BW.ph==="count") && (b.z<HZ+3.4 || !ball.visible) && !BW.gutter, vsW=!portrait && SIDE.some(L=>L.on), wait=BW.ph==="done";
      const z=BW.ph==="roll"||BW.ph==="count"?Math.max(-6.2, Math.min(BW.camZ, b.z+3.4)):BW.camZ; BW.camZ=z;
      const des=pinCam?new THREE.Vector3(.9, .95, HZ+2.6):wait?new THREE.Vector3(0, portrait?3.4:2.5, portrait?5.6:5.4):new THREE.Vector3(0, portrait?2.05:(vsW?1.9:1.6), z+(portrait?.9:(vsW?1.3:.3))), tgt=pinCam?new THREE.Vector3(-.1,.3,HZ-.6):wait?new THREE.Vector3(0,.2,-6):new THREE.Vector3(0,.1,z-8);   /* (v731) 옆 레인 친구가 보이게 가로 화면은 한 걸음 뒤 · 다 굴리고 기다릴 땐 넓게 */
      if(!camP || fast || BW.ph==="aim"){ camP=des.clone(); camT=tgt.clone(); } else { camP.lerp(des, pinCam?.08:wait?.05:.25); camT.lerp(tgt, pinCam?.08:wait?.05:.25); } cam.position.copy(camP); cam.lookAt(camT);
      if(shk>0){ cam.position.x+=(Math.random()-.5)*shk*.09; cam.position.y+=(Math.random()-.5)*shk*.06; } }
    cam.updateProjectionMatrix(); }
  /* ══ 틀 ══ */
  function tick(dt){ if(gone || paused) return; if(fast) dt=Math.min(.1, dt*4); if(RM) coTick(dt);
    for(let i=TM.length-1;i>=0;i--){ TM[i].t-=dt; if(TM[i].t<=0){ const f=TM[i].fn; TM.splice(i,1); try{ f(); }catch(e){ console.warn("SP", e); } } }
    if(mode==="bowl"){ const slow=!fast && BW.ph==="roll" && ball.visible && !BW.gutter && ball.position.z<HZ+2.4 && ball.position.z>LZ+.3;
      if(BW.rp) rpStep(dt); else laneStep(BW, dt*(slow?.42:1));
      SIDE.forEach(L=>{ if(!L.on) return; if(!L.co) botTick(L, dt); laneStep(L, dt); }); LANES.forEach(L=>sweepStep(L, dt)); avStep(dt); if(shk>0) shk=Math.max(0, shk-dt*2.4); } if(mode==="dart") dartStep(dt); confStep(dt); }
  function render(){ fitCam(); MG.draw(scene, cam); }
  function dispose(){ gone=true; TM.length=0; coQuit(); try{ R.remove(); }catch(e){} disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); }
  fitCam(); const O=api.opt||{}; if(O.go==="bowl"||O.go==="dart") menuGo(O.go); else menuShow(); ready=true;
  return {scene, cam, tick, render, dispose, pause:v=>{ paused=!!v; },
    get mode(){ return mode; }, get bw(){ return BW; }, get dt(){ return DT; }, get ready(){ return ready; }, get pins(){ return PINS; }, set fast(v){ fast=v?1:0; },
    menuGo, menuShow, throwBall, dart:(x,y)=>dart(x,y), scoreAt, bowlScore, bowlDone, rollsInFrame, get SET(){ return SET; }, fitCam,
    lanes:LANES, SKILL, botAim, laneThrow:(i,x,vx,vz)=>throwLane(LANES[i],x,vx,vz), get rp(){ return BW.rp; }, get shk(){ return shk; }, get endQ(){ return endQ; }, get RM(){ return RM; }, get CO(){ return CO; } };
}
MG.reg("bowl", {ic:"🎳", nm:"볼링 · 다트", tag:"🎳 볼링 5프레임 · 🎯 다트 9개", bg:"linear-gradient(135deg,#5b3aff,#ff5ce1 55%,#ffd23f)", big:"🎳🎯", menu:true,
  how:[["🎳","레인을 위로 쓱 밀어 굴려요"],["🎯","조준점을 옮기고 떼면 던져요"]], payTxt:"점수 따라 🪙 3~9",
  bestTxt:(b,t)=>'🎳 '+(b.bw|0)+'점 · 🎯 '+(b.dt|0)+'점', ui:{look:false, btns:[]}, start});
})();
