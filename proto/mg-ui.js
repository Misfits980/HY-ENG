/* ═════════ 🎡 놀이 섬 게임 공통 화면 (window.PUI)
   (v643) 사용자: 「너무 부족해 — 인터페이스부터 다 부족해 보여」 → 시안 2개 → 「섞기 (메뉴·결과 = B 게임쇼, 게임 중 = A 섬 스티커)」
   · B 게임쇼 (메뉴 · 결과): 밤하늘 남색 · 금테 · 반짝이 · 금빛 큰 제목 · 내 캐릭터가 빛나는 무대 위 · 별 3개 결과 · 보상 칸
   · A 섬 스티커 (게임 중): 크림 판 · 굵은 갈색 테두리 · 흰 바깥선 · 아래 그림자 단추 · 리본 「내 차례!」 · 말풍선
   · 아이콘 = 본 게임 그림 (assets/ui/hud-icons · menu-icons · result-badges)
   · 캐릭터 그림 = buildAvatar 를 작은 렌더러로 한 번 찍어 PNG 로 (모양별 저장)
   PUI.menu(host, o) · PUI.result(host, o) · PUI.count(host, cb, fast) · PUI.ic(name, px) · PUI.av(av, kind) · PUI.css() */
(function(){
"use strict";
const HUD=["heart","heart0","pause","gear","clock","star","flag","fire"], MEN=["play","retry","book","trophy","plus","question","swords"], BAD=["bronze","silver","gold","crown"];
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function ic(n, px){ px=px||28; let f="hud-icons", i=HUD.indexOf(n), cols=8; if(i<0){ i=MEN.indexOf(n); f="menu-icons"; cols=7; } if(i<0){ i=BAD.indexOf(n); f="result-badges"; cols=4; } if(i<0) return "";
  return '<i class="puI" style="width:'+px+'px;height:'+px+'px;background-image:url(../assets/ui/'+f+'.webp);background-size:'+(px*cols)+'px '+px+'px;background-position:'+(-px*i)+'px 0"></i>'; }
/* ── 캐릭터 사진 (PNG) ── */
let RR=null; const AVC={};
const SV={coin:'<svg class="puSv" viewBox="0 0 32 32" aria-hidden="true"><ellipse cx="16" cy="18" rx="13" ry="12.4" fill="#c98412"/><circle cx="16" cy="15.4" r="13" fill="#ffc93d" stroke="#4b3527" stroke-width="2.4"/><circle cx="16" cy="15.4" r="8.8" fill="#ffe08a" stroke="#e0a21c" stroke-width="1.6"/><path d="M16 9.6l1.8 3.7 4 .5-2.9 2.8.7 4-3.6-1.9-3.6 1.9.7-4-2.9-2.8 4-.5z" fill="#ffb21c" stroke="#d98a0c" stroke-width=".8" stroke-linejoin="round"/><path d="M7.4 10.6c1.6-3 4.2-4.8 7.4-5.2" stroke="#fff" stroke-width="2.1" fill="none" stroke-linecap="round" opacity=".85"/></svg>'};
const coinTx=t=>String(t==null?"":t).replace(/🪙/g, SV.coin);
function av(a, kind){ kind=kind||"bust"; const key=kind+"|"+JSON.stringify(a||{}); if(AVC[key]) return AVC[key];
  try{ if(!RR){ RR=new THREE.WebGLRenderer({alpha:true, antialias:true, preserveDrawingBuffer:true}); RR.setPixelRatio(1); RR.outputEncoding=THREE.sRGBEncoding; }
    const full=kind!=="bust", w=full?360:256, h=full?440:256; RR.setSize(w,h,false); RR.setClearColor(0x000000,0);
    const sc=new THREE.Scene(); sc.add(new THREE.HemisphereLight(0xffffff,0x667788,.95)); const l=new THREE.DirectionalLight(0xffffff,.6); l.position.set(1,2,2); sc.add(l);
    const P=buildAvatar(a||{}); sc.add(P.g);
    if(kind==="cheer"){ P.setExpr("grin"); P.armL.rotation.set(-2.7,0,.4); P.armR.rotation.set(-2.7,0,-.4); }
    else if(kind==="sad"){ P.setExpr("wow"); P.head.rotation.x=.25; }
    else if(kind==="wave"){ P.setExpr("smile"); P.armR.rotation.set(-2.5,0,-.3); }
    else P.setExpr(kind==="bust"?"grin":"smile");
    const c=new THREE.PerspectiveCamera(full?30:24, w/h, .1, 20); if(full){ c.position.set(.4,1.0,3.4); c.lookAt(0,.95,0); } else { c.position.set(.05,1.12,2.9); c.lookAt(0,1.08,0); }
    RR.render(sc,c); const url=RR.domElement.toDataURL("image/png"); AVC[key]=url;
    sc.remove(P.g); return url; }catch(e){ console.warn("PUI av", e); return ""; } }
function css(){ if(document.getElementById("puCss")) return; const s=document.createElement("style"); s.id="puCss"; s.textContent=`
#mgUI .puI{display:inline-block;background-repeat:no-repeat;vertical-align:middle;flex:none}
/* ═ B 게임쇼 (메뉴 · 결과) ═ */
#mgUI .puM,#mgUI .puR{--nv:#1E2160;--nv2:#262a78;--deep:#0D0F33;--gold:#FFC94A;--pink:#FF4FA8;--mint:#2FD49A;--sky:#3FD8FF;font-family:var(--kr);color:#fff}
#mgUI .puM{position:absolute;inset:0;z-index:20;display:flex;flex-direction:column;align-items:center;gap:10px;pointer-events:auto;overflow:hidden;
  padding:calc(58px + env(safe-area-inset-top)) max(14px,env(safe-area-inset-right)) calc(14px + env(safe-area-inset-bottom)) max(14px,env(safe-area-inset-left));
  background:radial-gradient(circle at 50% 44%,rgba(63,216,255,.42) 0 60px,transparent 190px),radial-gradient(circle at 20% 15%,#fff 0 1.4px,transparent 2px) 0 0/62px 62px,radial-gradient(circle at 70% 60%,#ffe 0 1px,transparent 1.5px) 0 0/45px 45px,linear-gradient(#2a1d6e,#0e1240)}
#mgUI .puM *{box-sizing:border-box}
#mgUI .puM .stats{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
#mgUI .puChip{display:inline-flex;align-items:center;gap:6px;background:var(--nv);border:2px solid var(--gold);border-radius:999px;padding:3px 12px 3px 5px;font-size:16px;color:#fff;box-shadow:0 3px 0 var(--deep);white-space:nowrap}
#mgUI .puChip b{font-family:var(--en);font-weight:900}
#mgUI .puTtl{text-align:center;line-height:1}
#mgUI .puTtl h2{margin:0;font-weight:400;font-size:clamp(40px,12vw,62px);color:#ffd860;-webkit-text-stroke:9px var(--deep);paint-order:stroke fill;filter:drop-shadow(0 6px 0 var(--deep)) drop-shadow(0 0 16px rgba(255,201,74,.55));transform:rotate(-4deg);display:inline-block}
#mgUI .puTtl p{margin:10px 0 0;display:inline-block;font-size:16px;background:rgba(255,255,255,.13);border-radius:999px;padding:5px 16px}
#mgUI .puHero{position:relative;flex:1;min-height:120px;width:100%;display:flex;align-items:flex-end;justify-content:center}
#mgUI .puHero img{position:relative;z-index:1;height:min(100%,250px);max-height:250px;margin-bottom:22px;filter:drop-shadow(0 6px 0 rgba(0,0,0,.25))}
#mgUI .puHero .stage{position:absolute;bottom:0;left:50%;width:210px;height:52px;margin-left:-105px;border-radius:50%;background:radial-gradient(#7fe9ff 30%,#3a4ad0 70%);border:3px solid var(--gold);box-shadow:0 0 40px #3fd8ff}
#mgUI .puHero .tag{position:absolute;z-index:2;left:calc(50% + 46px);top:18%;transform:rotate(8deg)}
#mgUI .puHero .deco{position:absolute;z-index:0;font-size:40px;filter:drop-shadow(0 4px 0 rgba(0,0,0,.3))}
#mgUI .puPanel{width:min(100%,480px);background:linear-gradient(#262a78,#171a52);border:3px solid var(--gold);border-radius:22px;box-shadow:0 0 0 3px var(--deep),inset 0 0 0 2px rgba(255,201,74,.22),0 0 30px rgba(63,216,255,.22);padding:12px;display:flex;flex-direction:column;gap:10px;flex:none}
#mgUI .puTiles{display:grid;grid-template-columns:repeat(var(--n,3),1fr);gap:8px}
#mgUI .puTile{font:inherit;position:relative;border:2px solid var(--gold);border-radius:18px;background:var(--nv2);color:#fff;padding:8px 4px 8px;display:flex;flex-direction:column;align-items:center;gap:2px;box-shadow:0 5px 0 var(--deep);min-height:104px;justify-content:center;cursor:pointer}
#mgUI .puTile:active{transform:translateY(4px);box-shadow:0 1px 0 var(--deep)}
#mgUI .puTile .pic{width:60px;height:60px;border-radius:50%;border:3px solid var(--deep);background:#bfe6ff center/cover;display:flex;align-items:center;justify-content:center;font-size:34px}
#mgUI .puTile b{font-weight:400;font-size:18px} #mgUI .puTile small{font-size:12.5px;opacity:.75}
#mgUI .puTile .bd{position:absolute;top:-10px;right:-6px;background:var(--gold);color:var(--deep);border:2px solid var(--deep);border-radius:10px;font-size:12px;padding:1px 6px}
#mgUI .puTile.on{background:#3a3fa8;box-shadow:0 0 0 3px var(--sky),0 5px 0 var(--deep)}
#mgUI .puBtn{font:inherit;display:flex;align-items:center;justify-content:center;gap:8px;border:3px solid var(--deep);border-radius:18px;color:#fff;font-size:23px;padding:10px 16px;min-height:52px;cursor:pointer;
  box-shadow:inset 0 -7px 0 rgba(0,0,0,.2),inset 0 4px 0 rgba(255,255,255,.3),0 5px 0 var(--deep);text-shadow:0 2px 0 rgba(0,0,0,.25);background:var(--nv2)}
#mgUI .puBtn:active{transform:translateY(4px);box-shadow:inset 0 -4px 0 rgba(0,0,0,.2),0 1px 0 var(--deep)}
#mgUI .puBtn.pk{background:var(--pink)} #mgUI .puBtn.two span{display:flex;flex-direction:column;align-items:flex-start;line-height:1.15;text-align:left} #mgUI .puBtn.two b{font-weight:400} #mgUI .puBtn.two small{font-size:13px;opacity:.92} #mgUI .puBtn.mt{background:var(--mint)} #mgUI .puBtn.sm{font-size:17px;min-height:42px;padding:6px 14px;border-radius:14px}
#mgUI .puRow{display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap}
#mgUI .puRow .pay{font-size:15px;opacity:.9}
#mgUI .puSeg{display:flex;gap:6px;justify-content:center} #mgUI .puSeg button{font:inherit;border:2px solid rgba(255,201,74,.5);background:transparent;color:#fff;border-radius:12px;padding:6px 12px;min-height:40px;font-size:15px;cursor:pointer} #mgUI .puSeg button.on{background:var(--gold);color:var(--deep);border-color:var(--gold)}
#mgUI .puExtra{width:min(100%,480px)}
@media (orientation:landscape) and (max-height:620px){
  #mgUI .puM{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);grid-template-rows:auto auto 1fr auto;grid-template-areas:"hero stats" "hero ttl" "hero extra" "hero panel";column-gap:18px;row-gap:6px;padding-top:calc(48px + env(safe-area-inset-top))}
  #mgUI .puM .stats{grid-area:stats} #mgUI .puTtl{grid-area:ttl} #mgUI .puTtl h2{font-size:40px} #mgUI .puHero{grid-area:hero;height:100%} #mgUI .puPanel{grid-area:panel;align-self:end;justify-self:center} #mgUI .puExtra{grid-area:extra;align-self:end;justify-self:center} #mgUI .puM:has(.puExtra) .stats{display:none} #mgUI .puM:has(.puExtra) .puTtl h2{font-size:34px}
  #mgUI .puTile{min-height:72px;padding:4px} #mgUI .puBtn.two small{display:none} #mgUI .puM:has(.puBtn.two) .stats{display:none} #mgUI .puM:has(.puSeg):has(.puBtn.pk) .stats{display:none} #mgUI .puSeg button{min-height:36px;padding:4px 10px} #mgUI .puTile .pic{width:40px;height:40px;font-size:24px} #mgUI .puTile b{font-size:16px} #mgUI .puTtl p{display:none} #mgUI .puM{row-gap:4px}
  #mgUI .puHero{min-height:0} #mgUI .puHero img{height:auto;max-height:calc(100vh - 110px);max-height:calc(100dvh - 110px);margin-bottom:18px} #mgUI .puHero .stage{width:170px;margin-left:-85px;height:42px} #mgUI .puPanel{gap:7px;padding:9px} #mgUI .puBtn{min-height:44px;font-size:20px;padding:6px 12px}
}
/* 결과 */
#mgUI .puR{position:absolute;inset:0;z-index:40;display:flex;align-items:center;justify-content:center;pointer-events:auto;background:rgba(13,15,51,.72);padding:calc(30px + env(safe-area-inset-top)) 14px calc(14px + env(safe-area-inset-bottom));animation:puFade .3s}
@keyframes puFade{from{opacity:0}}
#mgUI .puR .rays{position:absolute;top:50%;left:50%;width:640px;height:640px;margin:-430px 0 0 -320px;background:repeating-conic-gradient(rgba(255,215,90,.28) 0 12deg,transparent 12deg 24deg);border-radius:50%;-webkit-mask:radial-gradient(circle,#000 25%,transparent 68%);mask:radial-gradient(circle,#000 25%,transparent 68%);animation:puSpin 18s linear infinite;pointer-events:none}
@keyframes puSpin{to{transform:rotate(360deg)}}
#mgUI .puR .box{position:relative;width:min(100%,420px);background:linear-gradient(#262a78,#171a52);border:3px solid var(--gold);border-radius:24px;box-shadow:0 0 0 3px var(--deep),0 0 40px rgba(63,216,255,.3);padding:58px 14px 14px;text-align:center;margin-top:96px;animation:puPop .45s cubic-bezier(.3,1.6,.6,1)}
@keyframes puPop{from{transform:scale(.6);opacity:0}}
#mgUI .puR .stars{position:absolute;left:0;right:0;top:-104px;display:flex;justify-content:center;align-items:flex-end;gap:0}
#mgUI .puR .stars .puI{filter:drop-shadow(0 5px 0 var(--deep));animation:puStar .5s backwards} #mgUI .puR .stars .puI:nth-child(2){margin-bottom:16px;animation-delay:.15s} #mgUI .puR .stars .puI:nth-child(3){animation-delay:.3s}
#mgUI .puR .stars .puI.off{filter:grayscale(1) brightness(.6) drop-shadow(0 5px 0 var(--deep))}
@keyframes puStar{from{transform:scale(0) rotate(-90deg)}}
#mgUI .puR .who{position:absolute;left:-8px;top:-150px;width:110px;transform:rotate(-8deg);filter:drop-shadow(0 5px 0 rgba(0,0,0,.3))}
#mgUI .puR .rib{position:absolute;top:-28px;left:50%;transform:translateX(-50%);border:3px solid var(--deep);border-radius:14px;padding:5px 26px;font-size:32px;white-space:nowrap;box-shadow:0 6px 0 var(--deep);text-shadow:0 3px 0 rgba(0,0,0,.25);background:var(--mint)}
#mgUI .puR .rib.lose{background:#6a72d8} #mgUI .puR .rib.draw{background:#ff9a3d}
#mgUI .puR .sub{font-size:16.5px;opacity:.88;margin:2px 0 10px}
#mgUI .puR .rw{display:flex;justify-content:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}
#mgUI .puR .rw .it{width:92px;background:var(--nv2);border:2px solid var(--gold);border-radius:16px;padding:6px 4px 8px;box-shadow:0 4px 0 var(--deep);position:relative}
#mgUI .puR .rw .it .e{font-size:32px;line-height:40px;display:block} #mgUI .puR .rw .it b{display:block;font-family:var(--en);font-weight:900;font-size:21px} #mgUI .puR .rw .it small{font-size:12.5px;opacity:.75}
#mgUI .puR .rw .it .nw{position:absolute;top:-10px;right:-6px;background:var(--pink);border:2px solid var(--deep);border-radius:9px;font-size:12px;padding:1px 6px;transform:rotate(8deg)}
#mgUI .puR .extra{margin:-4px 0 10px;font-size:14.5px}
#mgUI .puRank{display:flex;flex-direction:column;gap:3px;text-align:left} #mgUI .puRank div{display:flex;justify-content:space-between;background:rgba(255,255,255,.08);border-radius:10px;padding:4px 10px} #mgUI .puRank div.me{background:rgba(255,201,74,.25)} #mgUI .puRank b{font-family:var(--en);font-weight:900}
#mgUI .puR .prog{text-align:left;font-size:14.5px;margin:0 4px 12px} #mgUI .puR .prog .b{height:16px;border:2px solid var(--gold);border-radius:10px;background:var(--deep);overflow:hidden;margin-top:4px} #mgUI .puR .prog .b i{display:block;height:100%;background:repeating-linear-gradient(-45deg,var(--gold) 0 10px,#ffd76b 10px 20px)}
#mgUI .puR .bt{display:grid;grid-template-columns:1fr 1fr;gap:8px} #mgUI .puR .bt .big{grid-column:1/-1;font-size:26px;padding:12px}
@media (max-height:640px){ #mgUI .puR .box{margin-top:60px;padding-top:46px} #mgUI .puR .stars{top:-78px} #mgUI .puR .stars .puI{transform:scale(.75)} #mgUI .puR .who{display:none} }
@media (orientation:landscape) and (max-height:620px){
  #mgUI .puR{align-items:flex-start;padding-top:calc(8px + env(safe-area-inset-top));overflow:auto} #mgUI .puR .box{margin-top:42px;padding:40px 12px 10px;width:min(100%,560px)} #mgUI .puR .stars{top:-66px} #mgUI .puR .stars .puI{transform:scale(.62)} #mgUI .puR .who{display:none} #mgUI .puR .rib{font-size:24px;top:-22px}
  #mgUI .puR .rw .it{width:84px;padding:3px} #mgUI .puR .rw .it .e{font-size:24px;line-height:28px} #mgUI .puR .rw .it b{font-size:17px} #mgUI .puR .prog{display:none} #mgUI .puR .sub{margin-bottom:6px} #mgUI .puR .bt{grid-template-columns:2fr 1fr 1fr} #mgUI .puR .bt .big{grid-column:auto;font-size:21px;padding:6px} #mgUI .puR .extra{margin:-2px 0 6px} #mgUI .puR .puRank div:nth-child(n+4):not(.me){display:none} #mgUI .puR .puRank div{padding:2px 10px} #mgUI .puR .rw{margin-bottom:8px}
}
@media (min-width:700px) and (min-height:900px), (min-width:1000px) and (min-height:700px){ #mgUI .puPanel,#mgUI .puExtra{zoom:1.25} #mgUI .puM .stats,#mgUI .puTtl{zoom:1.2} #mgUI .puHero img{max-height:360px;height:min(100%,360px)} #mgUI .puHero .stage{transform:scale(1.3)} #mgUI .puR .box{zoom:1.3} }
@media (min-width:1000px) and (min-height:700px) and (max-height:899px){ #mgUI .puR .box{zoom:1.08} #mgUI .puPanel,#mgUI .puExtra{zoom:1.05} #mgUI .puM .stats,#mgUI .puTtl{zoom:1} #mgUI .puHero img{max-height:240px} }
/* ═ A 섬 스티커 (게임 중) ═ */
#mgUI .paPill{--paper:#FFF6E3;--cocoa:#4A2E1F;display:flex;align-items:center;gap:8px;background:var(--paper);color:var(--cocoa);border:3px solid var(--cocoa);border-radius:999px;box-shadow:0 0 0 3px #fff,0 5px 0 3px rgba(74,46,31,.35);font-family:var(--kr)}
#mgUI .paBtn{--cocoa:#4A2E1F;font:inherit;font-family:var(--kr);display:flex;align-items:center;justify-content:center;gap:6px;border:3px solid var(--cocoa);border-radius:16px;background:#fff;color:var(--cocoa);box-shadow:inset 0 -5px 0 rgba(0,0,0,.08),0 4px 0 var(--cocoa);cursor:pointer}
#mgUI .paBtn:active{transform:translateY(3px);box-shadow:0 1px 0 var(--cocoa)}
#mgUI .paBan{--cocoa:#4A2E1F;position:absolute;left:50%;transform:translateX(-50%) rotate(-3deg);background:#FF5A4E;color:#fff;border:3px solid var(--cocoa);padding:4px 22px;font-size:23px;border-radius:12px;box-shadow:0 4px 0 var(--cocoa);white-space:nowrap;font-family:var(--kr);pointer-events:none;text-shadow:0 2px 0 rgba(0,0,0,.2);z-index:2}
#mgUI .paBan::before,#mgUI .paBan::after{content:"";position:absolute;top:9px;width:18px;height:26px;background:#d9443a;border:3px solid var(--cocoa);z-index:-1}
#mgUI .paBan::before{left:-16px;border-right:0} #mgUI .paBan::after{right:-16px;border-left:0}
#mgUI .paBan.g{background:#3CC46B} #mgUI .paBan.g::before,#mgUI .paBan.g::after{background:#2a9a52} #mgUI .paBan.y{background:#FFC53D;color:#4A2E1F;text-shadow:none} #mgUI .paBan.y::before,#mgUI .paBan.y::after{background:#e0a21c}
#mgUI .paBan.pop{animation:paBan .4s cubic-bezier(.3,1.6,.6,1)} @keyframes paBan{from{transform:translateX(-50%) rotate(-3deg) scale(.4)}}
/* 카운트다운 */
#mgUI .puCnt{position:absolute;inset:0;z-index:30;display:flex;align-items:center;justify-content:center;pointer-events:none}
#mgUI .puCnt b{font-family:var(--kr);font-weight:400;font-size:120px;color:#ffd860;-webkit-text-stroke:12px #0D0F33;paint-order:stroke fill;filter:drop-shadow(0 8px 0 #0D0F33);animation:puCnt .7s cubic-bezier(.3,1.6,.6,1) both}
#mgUI .puCnt b.go{font-size:92px;color:#2FD49A}
@keyframes puCnt{0%{transform:scale(2.2);opacity:0}30%{transform:scale(1);opacity:1}80%{opacity:1}100%{transform:scale(.8);opacity:0}}
/* (v659) 사용자: 「UI 퀄리티도 올리고」 → 화면이 살아 있게: 캐릭터 둥실 · 무대 빛 · 장식 떠다님 · 제목/판 등장 · 큰 단추 반짝 · 보상 칸 차례로 · 숫자 올라감 · 꽃가루 · 그린 코인 */
#mgUI .puSv{display:inline-block;width:1.15em;height:1.15em;vertical-align:-.22em}
#mgUI .puR .rw .it .e .puSv{width:38px;height:38px;vertical-align:middle}
#mgUI .puBtn.pk{position:relative;overflow:hidden}
#mgUI .puR .cf{position:absolute;top:-24px;width:10px;height:16px;border-radius:3px;pointer-events:none;z-index:1;animation:puCf linear forwards} @keyframes puCf{to{transform:translateY(112vh) rotate(700deg)}}
@media (prefers-reduced-motion:no-preference){
#mgUI .puM .puHero img{animation:puBob 2.4s ease-in-out infinite;transform-origin:50% 100%} @keyframes puBob{50%{transform:translateY(-7px) rotate(1.4deg) scale(1.015)}}
#mgUI .puM .puHero .stage{animation:puGlow 2.4s ease-in-out infinite} @keyframes puGlow{50%{box-shadow:0 0 64px #7fe9ff;scale:1.05}}
#mgUI .puM .puHero .deco{animation:puFloat 3.2s ease-in-out infinite} #mgUI .puM .puHero .deco:nth-of-type(odd){animation-duration:2.5s;animation-delay:-1.1s} @keyframes puFloat{50%{translate:0 -11px;rotate:9deg}}
#mgUI .puM .puHero .tag{animation:puFloat 2.8s ease-in-out infinite -.6s}
#mgUI .puBtn.pk::after{content:"";position:absolute;top:0;bottom:0;width:50px;left:-70px;background:linear-gradient(100deg,transparent,rgba(255,255,255,.5),transparent);animation:puShine 2.8s infinite;pointer-events:none} @keyframes puShine{0%,58%{left:-70px}100%{left:calc(100% + 20px)}}
#mgUI .puM.puIn .puTtl h2{animation:puTtl .6s cubic-bezier(.3,1.7,.5,1) backwards} @keyframes puTtl{from{transform:rotate(-14deg) scale(.3);opacity:0}}
#mgUI .puM.puIn .puPanel,#mgUI .puM.puIn .puExtra{animation:puUp .5s cubic-bezier(.3,1.35,.6,1) backwards .12s} @keyframes puUp{from{translate:0 70px;opacity:0}}
#mgUI .puM.puIn .stats .puChip{animation:puUp .4s cubic-bezier(.3,1.35,.6,1) backwards} #mgUI .puM.puIn .stats .puChip:nth-child(2){animation-delay:.08s} #mgUI .puM.puIn .stats .puChip:nth-child(3){animation-delay:.16s}
#mgUI .puM.puIn .puHero img{animation:puHeroIn .55s cubic-bezier(.3,1.5,.6,1) backwards .05s, puBob 2.4s ease-in-out infinite .6s} @keyframes puHeroIn{from{transform:translateY(40px) scale(.5);opacity:0}}
#mgUI .puR .rw .it{animation:puPop .4s cubic-bezier(.3,1.6,.6,1) backwards .35s} #mgUI .puR .rw .it:nth-child(2){animation-delay:.5s} #mgUI .puR .rw .it:nth-child(3){animation-delay:.65s} #mgUI .puR .rw .it:nth-child(4){animation-delay:.8s}
#mgUI .puR .rib{animation:puRib .55s cubic-bezier(.3,1.7,.5,1) backwards .15s} @keyframes puRib{from{transform:translateX(-50%) scale(.3) rotate(-14deg);opacity:0}}
#mgUI .puR .who{animation:puWho 1s ease-in-out infinite alternate} @keyframes puWho{to{transform:rotate(-3deg) translateY(-8px)}}
#mgUI .puR .prog .b i{animation:puBar .8s ease-out backwards .7s} @keyframes puBar{from{width:0}}
#mgUI .puR .bt .again{animation:puPulse 1.5s ease-in-out infinite 1.2s} @keyframes puPulse{50%{scale:1.03}}
}
`; document.head.appendChild(s); }

/* ── 메뉴 (B) ── o={title, sub, av, stats:[[icon|emoji, num, label]], tiles:[{k, pic|emoji, nm, sub, bd}], n, primary:{k,label,ic}, seg:{title, items:[[k,label]], on, pick}, pay, more:html, onPick, onOut, cls} */
function pbtn(p){ return '<button class="puBtn pk'+(p.sub?' two':'')+'" data-m="'+esc(p.k)+'" style="font-size:25px">'+(p.ic?ic(p.ic,36):'')+(p.sub?'<span><b>'+esc(p.label)+'</b><small>'+esc(p.sub)+'</small></span>':esc(p.label))+'</button>'; }
function menu(host, o){ css(); let el=host.querySelector(".puM"); if(!el){ el=document.createElement("div"); el.className="puM puIn"; host.appendChild(el); setTimeout(()=>el.classList.remove("puIn"), 1100); } if(o.cls) el.classList.add(o.cls);
  const st=(o.stats||[]).map(([i,n,l])=>'<span class="puChip">'+(ic(i,26)||'<span style="font-size:20px">'+i+'</span>')+'<b>'+esc(n)+'</b>'+esc(l)+'</span>').join("");
  const url=o.av===false?"":av(o.av||{}, "wave");
  el.innerHTML='<div class="stats">'+st+'</div><div class="puTtl"><h2>'+esc(o.title)+'</h2><br><p>'+esc(o.sub||"")+'</p></div>'+
    '<div class="puHero"><div class="stage"></div>'+(url?'<img alt="" src="'+url+'">':'')+(o.deco||[]).map(d=>'<span class="deco" style="'+d[1]+'">'+d[0]+'</span>').join("")+(o.nick?'<span class="puChip tag">'+esc(o.nick)+'</span>':'')+'</div>'+
    (o.more||"")+
    '<div class="puPanel">'+(o.primary&&o.primaryTop?pbtn(o.primary):'')+(o.seg?'<div class="puSeg">'+o.seg.items.map(([k,l])=>'<button data-sg="'+esc(k)+'" class="'+(String(o.seg.on)===String(k)?"on":"")+'">'+l+'</button>').join("")+'</div>':'')+
      ((o.tiles&&o.tiles.length)?'<div class="puTiles" style="--n:'+(o.n||Math.min(3,o.tiles.length))+'">'+o.tiles.map(t=>'<button class="puTile" data-m="'+esc(t.k)+'">'+(t.bd?'<span class="bd">'+t.bd+'</span>':'')+'<span class="pic" style="'+(t.pic?'background-image:url('+t.pic+');':'')+(t.bg?'background-color:'+t.bg+';':'')+'">'+(t.pic?'':(t.emoji||""))+'</span><b>'+esc(t.nm)+'</b>'+(t.sub?'<small>'+t.sub+'</small>':'')+'</button>').join("")+'</div>':'')+
      (o.primary&&!o.primaryTop?pbtn(o.primary):'')+
      '<div class="puRow"><span class="pay">오늘 '+SV.coin+' 상 '+(o.pay>0?'<b>'+o.pay+'</b>판 남음':'다 받았어요 (연습은 계속!)')+'</span><button class="puBtn sm out">🏝 섬으로</button></div></div>';
  el.style.display="";
  el.onclick=e=>{ const b=e.target.closest("button"); if(!b) return; try{ MG.SFX.tone(660,.06,"triangle",.04); }catch(_){} if(b.classList.contains("out")){ (o.onOut||MG.exit)(); return; } if(b.dataset.sg!=null){ o.seg.pick(b.dataset.sg); return; } if(b.dataset.m) o.onPick(b.dataset.m); };
  return el; }
function menuHide(host){ const el=host.querySelector(".puM"); if(el) el.style.display="none"; }

/* ── 결과 (B) ── o={res:"win"|"lose"|"draw", stars, title, sub, av, rewards:[[icon|emoji, value, label, isNew]], extra, prog:{t, v}, onAgain, onMenu, onOut} */
function result(host, o){ css(); let el=host.querySelector(".puR"); if(el) el.remove(); el=document.createElement("div"); el.className="puR"; host.appendChild(el);
  const s=Math.max(0,Math.min(3,o.stars|0)), who=av(o.av||{}, o.res==="lose"?"sad":"cheer");
  el.innerHTML='<div class="rays"></div><div class="box">'+'<div class="stars">'+[0,1,2].map(i=>ic("star", i===1?104:82).replace('class="puI"','class="puI'+(i<s?'':' off')+'"')).join("")+'</div>'+
    (who?'<img class="who" alt="" src="'+who+'">':'')+'<div class="rib '+(o.res||"win")+'">'+esc(o.title)+'</div><div class="sub">'+(o.sub||"")+'</div>'+
    '<div class="rw">'+(o.rewards||[]).map(([i,v,l,nw])=>'<div class="it">'+(nw?'<span class="nw">새 기록</span>':'')+'<span class="e">'+(ic(i,38)||(i==="🪙"?SV.coin:i))+'</span><b>'+esc(v)+'</b><small>'+esc(l)+'</small></div>').join("")+'</div>'+
    (o.extra?'<div class="extra">'+o.extra+'</div>':'')+
    (o.prog?'<div class="prog">'+coinTx(o.prog.t)+'<div class="b"><i style="width:'+Math.round(Math.max(0,Math.min(1,o.prog.v))*100)+'%"></i></div></div>':'')+
    '<div class="bt"><button class="puBtn mt big again">'+ic("retry",34)+'한 판 더</button><button class="puBtn menu">☰ 메뉴</button><button class="puBtn out">🏝 섬으로</button></div></div>';
  el.querySelector(".again").onclick=()=>{ el.remove(); o.onAgain && o.onAgain(); };
  el.querySelector(".menu").onclick=()=>{ el.remove(); o.onMenu && o.onMenu(); };
  el.querySelector(".out").onclick=()=>{ el.remove(); (o.onOut||MG.exit)(); };
  try{ if(s>=2) MG.SFX.win(); }catch(e){}
  if(!navigator.webdriver){ try{
    /* 숫자가 0 에서 올라감 */
    el.querySelectorAll(".rw .it b").forEach((b,i)=>{ const m=String(b.textContent).match(/^([+×]?)([\d,]+)$/); if(!m) return; const n=+m[2].replace(/,/g,""); if(!(n>1)) return; const t0=performance.now()+350+i*150, D=650; b.textContent=m[1]+"0";
      const f=()=>{ if(!b.isConnected) return; const k=Math.max(0, Math.min(1, (performance.now()-t0)/D)), e=1-Math.pow(1-k,3); b.textContent=m[1]+Math.round(n*e).toLocaleString(); if(k<1) requestAnimationFrame(f); else b.textContent=m[1]+m[2]; }; requestAnimationFrame(f); });
    /* 꽃가루 (별 2개부터) */
    if(s>=2 && (o.res||"win")==="win"){ const C=["#FFC94A","#FF4FA8","#2FD49A","#3FD8FF","#fff","#b28dff"]; for(let i=0;i<34;i++){ const c=document.createElement("i"); c.className="cf"; c.style.left=(Math.random()*100)+"%"; c.style.background=C[i%C.length]; c.style.animationDuration=(1.8+Math.random()*1.6)+"s"; c.style.animationDelay=(Math.random()*.9)+"s"; c.style.width=(7+Math.random()*7)+"px"; el.appendChild(c); setTimeout(()=>c.remove(), 4600); } } }catch(e){} }
  return el; }
/* MG 공통 결과(코인·하루 판 수)는 그대로 쓰고 창만 우리 것으로 */
function award(api, r){ const got=api.end(r)|0; const el=document.getElementById("mgRes"); if(el) el.classList.remove("on"); return got; }
/* ── 3 · 2 · 1 · 시작! ── */
function count(host, cb, fast){ css(); if(fast || navigator.webdriver){ cb && cb(); return; } const el=document.createElement("div"); el.className="puCnt"; host.appendChild(el); let n=3;
  const st=()=>{ if(!el.isConnected) return; if(n>0){ el.innerHTML='<b>'+n+'</b>'; try{ MG.SFX.tick(); }catch(e){} n--; setTimeout(st,650); } else { el.innerHTML='<b class="go">시작!</b>'; try{ MG.SFX.up(); }catch(e){} setTimeout(()=>{ el.remove(); cb && cb(); }, 600); } }; st(); return el; }
window.PUI={ic, av, css, menu, menuHide, result, award, count};
})();
