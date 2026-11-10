/* ═════════ 🎨 그림 맞히기 — 🎡 놀이 섬 그림 공방
   (v635) 사용자: 「1번 응 다 좋은데 글자를 직접 써야 한다고 봐」
   · ▶ 혼자 「그림 퍼즐」: 물감 칸이 하나씩 떨어지며 그림이 드러남 → 영어 단어를 직접 쳐서 맞힘 (8문제)
       💡 글자 힌트(점수 조금 깎임) · 🤔 모르겠어요 = 정답 보고 그 단어는 뒤에 한 번 더 나옴(다시 풀기)
   · 👫 같이 「그리고 맞히기」(2~6명): 차례로 그리는 사람 → 3단어 중 하나 고름 → 60초 그림 → 나머지는 영어로 쳐서 맞힘
       친 글자는 다른 친구에게 안 보임 — 친구 화면엔 ❌ / 🔥(거의) / ✅ 만 · 시간이 지나면 글자 힌트
   · 🖍️ 그려 보기: 단어 골라 그리고 🖼️ 그림첩에 저장 (같이 하기에서 내가 그린 그림도 저장)
   · 상: MG 공통 하루 3판 🪙 (혼자 = 맞힌 수 · 같이 = 1등 10 · 2등 6 · 3등 5 · 그 밖 4)
   방 데이터 /hy/day/mgd<날짜>/<방>/ { h, p, e, fd, g(방장 상태), s/<라운드>/k<n>(그림 줄) }
   시험 손잡이: MG.run.mode · .S · .G · .ready · .menuGo(k) · .key(ch) · .typeWord(s) · .submit() · .giveUp() · .hint() · .pick(i) · .demo() · .fast · .ans() */
(function(){
"use strict";
if(!window.MG) return;
/* ── 단어 (그리기 쉬운 이름씨만 · 아이 단어장 1단계) [영어, 뜻, 그림] ── */
const W=[["cat","고양이","🐱"],["dog","개","🐶"],["bird","새","🐦"],["fish","물고기","🐟"],["cow","소","🐮"],["pig","돼지","🐷"],["duck","오리","🦆"],["lion","사자","🦁"],["bear","곰","🐻"],["frog","개구리","🐸"],["ant","개미","🐜"],["bee","벌","🐝"],["fox","여우","🦊"],["crab","게","🦀"],["worm","지렁이","🪱"],
  ["horse","말","🐴"],["sheep","양","🐑"],["mouse","쥐","🐭"],["tiger","호랑이","🐯"],["zebra","얼룩말","🦓"],["snake","뱀","🐍"],["whale","고래","🐋"],["shark","상어","🦈"],["panda","판다","🐼"],["camel","낙타","🐫"],["hippo","하마","🦛"],["rabbit","토끼","🐰"],["monkey","원숭이","🐵"],["turtle","거북이","🐢"],["spider","거미","🕷️"],["parrot","앵무새","🦜"],
  ["chicken","닭","🐔"],["elephant","코끼리","🐘"],["giraffe","기린","🦒"],["butterfly","나비","🦋"],["dolphin","돌고래","🐬"],["penguin","펭귄","🐧"],["crocodile","악어","🐊"],
  ["pear","배","🍐"],["corn","옥수수","🌽"],["cake","케이크","🍰"],["milk","우유","🥛"],["egg","달걀","🥚"],["pie","파이","🥧"],
  ["apple","사과","🍎"],["grape","포도","🍇"],["lemon","레몬","🍋"],["bread","빵","🍞"],["candy","사탕","🍬"],["pizza","피자","🍕"],["banana","바나나","🍌"],["cheese","치즈","🧀"],["carrot","당근","🥕"],["tomato","토마토","🍅"],["cookie","쿠키","🍪"],
  ["popcorn","팝콘","🍿"],["pumpkin","호박","🎃"],["hamburger","햄버거","🍔"],["strawberry","딸기","🍓"],["watermelon","수박","🍉"],
  ["bag","가방","🎒"],["bed","침대","🛏️"],["box","상자","📦"],["key","열쇠","🔑"],["cup","컵","🥤"],["ball","공","⚽"],["kite","연","🪁"],["hat","모자","🎩"],["cap","야구모자","🧢"],["shoe","신발","👟"],["sock","양말","🧦"],["ring","반지","💍"],["bell","종","🔔"],["lamp","램프","💡"],["door","문","🚪"],["book","책","📕"],["drum","북","🥁"],["gift","선물","🎁"],["fork","포크","🍴"],
  ["chair","의자","🪑"],["ruler","자","📏"],["clock","시계","🕐"],["spoon","숟가락","🥄"],["robot","로봇","🤖"],["piano","피아노","🎹"],["shirt","셔츠","👕"],["pants","바지","👖"],["dress","원피스","👗"],["glove","장갑","🧤"],["broom","빗자루","🧹"],["bottle","병","🍼"],["mirror","거울","🪞"],["guitar","기타","🎸"],["pencil","연필","✏️"],["basket","바구니","🧺"],["crayon","크레용","🖍️"],
  ["balloon","풍선","🎈"],["glasses","안경","👓"],["umbrella","우산","☂️"],["scissors","가위","✂️"],["computer","컴퓨터","💻"],["snowman","눈사람","⛄"],["monster","괴물","👾"],
  ["sun","태양","☀️"],["moon","달","🌙"],["star","별","⭐"],["rain","비","🌧️"],["snow","눈","❄️"],["tree","나무","🌳"],["leaf","나뭇잎","🍃"],["fire","불","🔥"],
  ["cloud","구름","☁️"],["heart","하트","❤️"],["flower","꽃","🌷"],["island","섬","🏝️"],["rainbow","무지개","🌈"],["mountain","산","⛰️"],
  ["eye","눈","👁️"],["ear","귀","👂"],["nose","코","👃"],["hand","손","✋"],["foot","발","🦶"],["mouth","입","👄"],["tooth","이빨","🦷"],
  ["car","자동차","🚗"],["bus","버스","🚌"],["bike","자전거","🚲"],["ship","배","🚢"],["boat","보트","⛵"],["king","왕","🤴"],["baby","아기","👶"],
  ["train","기차","🚂"],["truck","트럭","🚚"],["plane","비행기","✈️"],["house","집","🏠"],["queen","여왕","👸"],["rocket","로켓","🚀"],["school","학교","🏫"],["bridge","다리","🌉"]];
const tier=i=>{ const n=W[i][0].length; return n<=4?1:n<=6?2:3; };
const TIERS=[[],[],[],[]]; W.forEach((w,i)=>TIERS[tier(i)].push(i));
const LV=[null,{nm:"쉬움",ic:"⭐",t:[1]},{nm:"보통",ic:"⭐⭐",t:[1,2]},{nm:"어려움",ic:"⭐⭐⭐",t:[2,3]}];
const COLS=["#2b2233","#ff5a5f","#ff9a3d","#ffd23f","#3fc46a","#3ea2ff","#9a6bff","#8a5a3c","#ffffff"], SIZES=[7,16,34], PW=1000, PH=750;
const B36="0123456789abcdefghijklmnopqrstuvwxyz";
const PTL={d:2,g:2,b:3,c:3,m:3,p:3,f:4,h:4,v:4,w:4,y:4,k:5,j:8,x:8,q:10,z:10};
const e2=n=>{ n=Math.max(0,Math.min(1295,Math.round(n))); return B36[(n/36)|0]+B36[n%36]; };
const enc=S=>{ let o=B36[S.c]+B36[S.s]; for(let i=0;i<S.p.length;i++) o+=e2(S.p[i]); return o; };
const dec=str=>{ if(typeof str!=="string" || str.length<2) return null; const S={c:B36.indexOf(str[0]), s:B36.indexOf(str[1]), p:[]}; for(let i=2;i+1<str.length;i+=2) S.p.push(B36.indexOf(str[i])*36+B36.indexOf(str[i+1])); return S; };
const norm=s=>String(s||"").toLowerCase().replace(/[^a-z]/g,"");
function lev(a,b){ const m=a.length, n=b.length; if(Math.abs(m-n)>2) return 9; let p=Array.from({length:n+1},(_,j)=>j); for(let i=1;i<=m;i++){ const c=[i]; for(let j=1;j<=n;j++) c[j]=Math.min(p[j]+1,c[j-1]+1,p[j-1]+(a[i-1]===b[j-1]?0:1)); p=c; } return p[n]; }
const near=(g,w)=>g.length>=2 && lev(g,w)<=(w.length>=7?2:1);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const st=(k,v)=>{ try{ return typeof store==="function" ? store(k,v) : (v===undefined?JSON.parse(localStorage.getItem(k)||"null"):localStorage.setItem(k,JSON.stringify(v))); }catch(e){ return null; } };
const sayW=w=>{ try{ say(w); }catch(e){ try{ const u=new SpeechSynthesisUtterance(w); u.lang="en-US"; u.rate=.9; speechSynthesis.speak(u); }catch(_){} } };
const encW=(i,rd)=>(i+37*rd)*3+1, decW=(v,rd)=>((v|0)-1)/3-37*rd;
const shuffle=(a,r)=>{ r=r||Math.random; for(let i=a.length-1;i>0;i--){ const j=Math.floor(r()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; };

function css(){ if(document.getElementById("dwCss")) return; const s=document.createElement("style"); s.id="dwCss"; s.textContent=`
#mgUI .dwR{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;gap:7px;pointer-events:auto;color:#3b2433;font-family:var(--kr);
  padding:calc(56px + env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) calc(8px + env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));
  background:radial-gradient(circle at 12% 18%,rgba(255,90,95,.18) 0 46px,transparent 47px),radial-gradient(circle at 88% 12%,rgba(62,162,255,.2) 0 38px,transparent 39px),radial-gradient(circle at 92% 78%,rgba(255,210,63,.25) 0 54px,transparent 55px),radial-gradient(circle at 6% 86%,rgba(63,196,106,.2) 0 40px,transparent 41px),
  repeating-linear-gradient(90deg,#fff3dd 0 26px,#ffeccc 26px 52px)}
#mgUI .dwR *{box-sizing:border-box}
#mgUI .dwBar{display:flex;align-items:center;gap:8px;width:min(100%,640px);flex:none}
#mgUI .dwMe{width:46px;height:46px;border-radius:50%;flex:none;border:3px solid #fff;box-shadow:0 2px 0 #d9bfa0,0 0 0 2px #5b3a7a;background:#2b3a5a;transition:transform .2s}
#mgUI .dwMe.hop{animation:dwHop .5s}
@keyframes dwHop{30%{transform:translateY(-10px) scale(1.12)}60%{transform:translateY(0) scale(.95)}}
#mgUI .dwPl span canvas{width:26px;height:26px;border-radius:50%;vertical-align:middle;margin:-4px 4px -4px -4px;background:#2b3a5a}
#mgUI .dwLine{position:relative;width:min(100%,640px);height:58px;flex:none;display:flex;justify-content:space-around;align-items:flex-start}
#mgUI .dwLine::before{content:"";position:absolute;left:-2%;right:-2%;top:8px;height:16px;border-top:2px solid #8a5a3c;border-radius:50%}
#mgUI .dwLine figure{margin:10px 0 0;width:58px;height:44px;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.18);transform:rotate(var(--r,0deg));position:relative;display:flex;align-items:center;justify-content:center;font-size:24px}
#mgUI .dwLine figure img{width:100%;height:100%;object-fit:cover}
#mgUI .dwLine figure::before{content:"";position:absolute;left:50%;top:-8px;width:8px;height:16px;margin-left:-4px;background:var(--pc,#ff8466);border-radius:2px}
@media (max-height:760px){ #mgUI .dwLine{display:none} }
#mgUI .dwCf{position:absolute;top:-20px;width:10px;height:14px;pointer-events:none;animation:dwFall 1.6s ease-in forwards;z-index:9}
@keyframes dwFall{to{transform:translateY(110vh) rotate(720deg)}}
#mgUI .dwBar b{background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;box-shadow:0 3px 0 #4A2E1F;border-radius:999px;padding:3px 11px;font-weight:400;font-size:16px;white-space:nowrap}
#mgUI .dwTm{flex:1;height:16px;border-radius:9px;background:#fff;overflow:hidden;border:3px solid #4A2E1F}
#mgUI .dwTm i{display:block;height:100%;width:100%;background:linear-gradient(90deg,#3fc46a,#ffd23f);transform-origin:left;transition:transform .2s linear}
#mgUI .dwTm.low i{background:#ff5a5f}
#mgUI .dwPl{display:flex;flex-wrap:wrap;gap:5px;justify-content:center;width:min(100%,640px);flex:none}
#mgUI .dwPl span{background:#fff;border:2px solid #e4cfb0;border-radius:12px;padding:3px 8px;font-size:13.5px;position:relative;transition:transform .15s}
#mgUI .dwPl span.me{border-color:#ff8466} #mgUI .dwPl span.dr{background:#ffe9a8;border-color:#ffb02e} #mgUI .dwPl span.ok{background:#d6f7de;border-color:#3fc46a}
#mgUI .dwPl span em{position:absolute;right:-6px;top:-12px;font-style:normal;font-size:18px;animation:dwPop .9s forwards}
@keyframes dwPop{0%{transform:scale(.3)}25%{transform:scale(1.3)}70%{opacity:1}100%{opacity:0;transform:translateY(-8px)}}
#mgUI .dwBd{position:relative;flex:none;margin-top:auto;margin-bottom:20px;width:min(100%,640px,calc((100vh - 410px)*4/3));width:min(100%,640px,calc((100dvh - 410px)*4/3));aspect-ratio:4/3;max-width:100%}
#mgUI .dwBd.dwT{width:min(100%,640px,calc((100vh - 330px)*4/3));width:min(100%,640px,calc((100dvh - 330px)*4/3))}
#mgUI .dwBd canvas{position:absolute;inset:0;width:100%;height:100%;border-radius:6px;background:#fff;touch-action:none;box-shadow:0 0 0 7px #c48a58,0 0 0 10px #8a5a3c,0 14px 24px rgba(91,58,122,.25)}
#mgUI .dwBd .ledge{position:absolute;left:-14px;right:-14px;bottom:-24px;height:14px;background:linear-gradient(#b07a50,#8a5a3c);border-radius:4px;box-shadow:0 3px 0 rgba(0,0,0,.15);pointer-events:none}
#mgUI .dwBd .ledge i{position:absolute;bottom:10px;width:7px;height:34px;border-radius:3px 3px 1px 1px;transform:rotate(var(--r));transform-origin:bottom}
#mgUI .dwBd::before,#mgUI .dwBd::after{content:"";position:absolute;width:70px;height:20px;top:-8px;background:rgba(255,132,102,.7);border-radius:3px;z-index:2;pointer-events:none}
#mgUI .dwBd::before{left:14px;transform:rotate(-8deg)} #mgUI .dwBd::after{right:14px;transform:rotate(7deg);background:rgba(62,162,255,.6)}
#mgUI .dwCov{position:absolute;inset:0;display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,1fr);border-radius:14px;overflow:hidden;pointer-events:none}
#mgUI .dwCov i{display:flex;align-items:center;justify-content:center;font-style:normal;font-size:min(7vw,34px);color:rgba(255,255,255,.75);font-family:var(--en);font-weight:900;transition:transform .55s cubic-bezier(.5,-0.4,.8,.6),opacity .55s;box-shadow:inset 0 0 0 2px rgba(255,255,255,.5)}
#mgUI .dwCov i.off{transform:translateY(130%) rotate(24deg) scale(.6);opacity:0}
#mgUI .dwOv{position:absolute;inset:0;border-radius:14px;display:none;flex-direction:column;align-items:center;justify-content:center;gap:8px;background:rgba(255,248,234,.94);z-index:3;text-align:center;padding:10px}
#mgUI .dwOv.on{display:flex}
#mgUI .dwVote{position:absolute;inset:0;z-index:30;display:none;flex-direction:column;align-items:center;gap:8px;overflow:auto;color:#fff;font-family:var(--kr);
  padding:calc(56px + env(safe-area-inset-top)) max(12px,env(safe-area-inset-right)) calc(12px + env(safe-area-inset-bottom)) max(12px,env(safe-area-inset-left));
  background:radial-gradient(circle at 50% 30%,rgba(255,201,74,.25),transparent 60%),radial-gradient(circle at 20% 15%,#fff 0 1.3px,transparent 2px) 0 0/58px 58px,linear-gradient(#2a1d6e,#0e1240)}
#mgUI .dwVote.on{display:flex}
#mgUI .dwVote h3{margin:0;font-weight:400;font-size:clamp(28px,8vw,40px);color:#ffd860;-webkit-text-stroke:7px #0D0F33;paint-order:stroke fill;transform:rotate(-3deg);text-align:center;line-height:1.15}
#mgUI .dwVote .sub{font-size:16px;background:rgba(255,255,255,.13);border-radius:999px;padding:4px 14px;text-align:center}
#mgUI .dwVote .tm{width:min(100%,520px);height:12px;border:2px solid #FFC94A;border-radius:8px;background:#0D0F33;overflow:hidden;flex:none} #mgUI .dwVote .tm i{display:block;height:100%;background:#FFC94A;transform-origin:left;transition:transform .3s linear}
#mgUI .dwVote .gr{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;width:min(100%,560px);padding:6px 2px 10px}
@media (min-width:640px){ #mgUI .dwVote .gr{grid-template-columns:repeat(3,1fr)} }
#mgUI .dwVote figure{margin:0;position:relative;background:#FFF6E3;border:3px solid #4A2E1F;border-radius:14px;padding:6px 6px 4px;box-shadow:0 0 0 3px #FFC94A,0 6px 0 3px #0D0F33;color:#4A2E1F;cursor:pointer;transform:rotate(var(--r,0deg));transition:transform .15s}
#mgUI .dwVote figure:nth-child(odd){--r:-1.5deg} #mgUI .dwVote figure:nth-child(even){--r:1.5deg}
#mgUI .dwVote figure:active{transform:scale(.96)}
#mgUI .dwVote figure .im{width:100%;aspect-ratio:4/3;border-radius:8px;background:#fff center/cover;display:flex;align-items:center;justify-content:center;font-size:48px;border:2px solid rgba(74,46,31,.25)}
#mgUI .dwVote figcaption{display:flex;justify-content:space-between;align-items:center;gap:4px;padding:4px 2px 0;font-size:14px;white-space:nowrap;overflow:hidden}
#mgUI .dwVote figcaption b{font-family:var(--en);font-weight:900;font-size:15px;overflow:hidden;text-overflow:ellipsis}
#mgUI .dwVote figure.mine{cursor:default;opacity:.62} #mgUI .dwVote figure.mine::after{content:"내 그림";position:absolute;top:-10px;left:-6px;background:#3ea2ff;color:#fff;border:2px solid #4A2E1F;border-radius:9px;font-size:12px;padding:1px 7px;transform:rotate(-8deg)}
#mgUI .dwVote figure.pick{box-shadow:0 0 0 4px #FF4FA8,0 6px 0 4px #0D0F33;transform:scale(1.04) rotate(0deg)} #mgUI .dwVote figure.pick::after{content:"❤️ 내 투표";position:absolute;top:-12px;right:-6px;background:#FF4FA8;color:#fff;border:2px solid #4A2E1F;border-radius:9px;font-size:13px;padding:1px 8px;transform:rotate(8deg)}
#mgUI .dwVote.done figure:not(.pick){opacity:.5}
#mgUI .dwVote .vc{position:absolute;bottom:34px;right:4px;background:#FF4FA8;color:#fff;border:2px solid #4A2E1F;border-radius:999px;font-size:15px;padding:0 9px;font-family:var(--en);font-weight:900}
#mgUI .dwVote .aw{display:flex;flex-direction:column;align-items:center;gap:6px;width:min(100%,420px)}
#mgUI .dwVote .aw figure{width:100%;cursor:default;--r:-2deg} #mgUI .dwVote .aw .rb{background:#2FD49A;border:3px solid #0D0F33;border-radius:14px;padding:4px 20px;font-size:24px;box-shadow:0 5px 0 #0D0F33;margin-bottom:-4px;z-index:1}
#mgUI .puR .dwAw{display:flex;align-items:center;gap:8px;justify-content:center;margin:0 0 8px;font-size:15px} #mgUI .puR .dwAw img{width:64px;height:48px;object-fit:cover;border-radius:8px;border:2px solid #FFC94A;background:#fff}
#mgUI .dwOv .big{font-size:min(20vw,110px);line-height:1}
#mgUI .dwOv .en{font-family:var(--en);font-weight:900;font-size:min(10vw,46px);color:#5b3a7a;letter-spacing:.04em}
#mgUI .dwOv .ko{font-size:18px;opacity:.8}
#mgUI .dwOv .ch{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
#mgUI .dwOv .ch button{font:inherit;border:0;border-radius:16px;background:#fff;box-shadow:0 4px 0 #d9bfa0;padding:8px 10px;min-width:96px;min-height:96px;display:flex;flex-direction:column;align-items:center;gap:2px;color:#3b2433}
#mgUI .dwOv .ch button .e{font-size:34px} #mgUI .dwOv .ch button .w{font-family:var(--en);font-weight:900;font-size:19px} #mgUI .dwOv .ch button small{font-size:12px;opacity:.75}
#mgUI .dwOv .ch button:active{transform:translateY(3px);box-shadow:0 1px 0 #d9bfa0}
#mgUI .dwBx{display:flex;gap:4px;justify-content:center;flex:none;min-height:46px;transition:transform .1s}
#mgUI .dwBx i{width:var(--bw,36px);height:46px;border-radius:10px;background:#fff;border:3px solid #5b3a7a;display:flex;align-items:center;justify-content:center;font-style:normal;font-family:var(--en);font-weight:900;font-size:24px;color:#3b2433}
#mgUI .dwBx i.h{color:#c9b6e0} #mgUI .dwBx i.cur{border-color:#ff8466;box-shadow:0 0 0 3px rgba(255,132,102,.35)} #mgUI .dwBx.ok i{background:#d6f7de;border-color:#3fc46a} #mgUI .dwBx.no{animation:dwShake .35s}
@keyframes dwShake{25%{transform:translateX(-9px)}50%{transform:translateX(8px)}75%{transform:translateX(-5px)}}
#mgUI .dwFb{min-height:24px;font-size:17px;flex:none;text-align:center;margin-bottom:auto}
#mgUI .dwKb{margin-top:auto;width:min(100%,640px);display:flex;flex-direction:column;gap:6px;flex:none}
#mgUI .dwKb div{display:flex;gap:5px;justify-content:center}
#mgUI .dwKb button{font:inherit;flex:1;max-width:58px;min-height:48px;border:0;border-radius:8px;background:linear-gradient(#fff8e6,#f1dcb2);box-shadow:0 4px 0 #b88a55,inset 0 -2px 0 rgba(120,80,30,.12);position:relative;font-family:var(--en);font-weight:900;font-size:21px;color:#6a4022;padding:0;touch-action:manipulation}
#mgUI .dwKb button.dn{transform:translateY(3px);box-shadow:none;background:#ffe9a8}
#mgUI .dwKb button.w{max-width:none;flex:1.6;font-family:var(--kr);font-weight:400;font-size:15px;white-space:nowrap;letter-spacing:-.02em} #mgUI .dwKb button.go{background:#3fc46a;color:#fff;box-shadow:0 3px 0 #2a8a4a} #mgUI .dwKb button.gv{background:#efe3ff;box-shadow:0 3px 0 #c9b6e0}
#mgUI .dwKb.off{opacity:.45;pointer-events:none}
#mgUI .dwTl{margin-top:auto;width:min(100%,640px);display:flex;flex-direction:column;gap:6px;flex:none}
#mgUI .dwTl .wd{text-align:center;font-size:16px} #mgUI .dwTl .wd b{font-family:var(--en);font-weight:900;font-size:21px;color:#5b3a7a}
#mgUI .dwTl div.r{display:flex;gap:6px;justify-content:center;flex-wrap:wrap}
#mgUI .dwTl button{font:inherit;border:0;border-radius:50%;width:44px;height:44px;box-shadow:0 3px 0 rgba(0,0,0,.18);padding:0;font-size:20px;background:#fff;touch-action:manipulation}
#mgUI .dwTl button.c.on{outline:4px solid #5b3a7a;outline-offset:2px} #mgUI .dwTl button.s{display:flex;align-items:center;justify-content:center} #mgUI .dwTl button.s i{display:block;background:#3b2433;border-radius:50%}
#mgUI .dwTl button.s.on{outline:4px solid #ff8466;outline-offset:1px} #mgUI .dwTl button.tx{border-radius:14px;width:auto;padding:0 14px;font-size:16px} #mgUI .dwTl button.go{background:#3fc46a;color:#fff}
#mgUI .dwMenu{position:absolute;inset:0;background:inherit;display:none;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:calc(58px + env(safe-area-inset-top)) 16px calc(16px + env(safe-area-inset-bottom));z-index:4}
#mgUI .dwMenu.on{display:flex}
#mgUI .dwMenu h2{margin:0;font-weight:400;font-size:34px;color:#5b3a7a;text-shadow:0 3px 0 #fff} #mgUI .dwMenu .sub{font-size:14px;opacity:.8;text-align:center}
#mgUI .dwMenu .g{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:min(100%,520px)}
#mgUI .dwMenu .g button{font:inherit;border:0;border-radius:20px;padding:12px 8px;min-height:104px;background:#fff;box-shadow:0 5px 0 #d9bfa0;color:#3b2433;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font-size:18px}
#mgUI .dwMenu .g button .e{font-size:36px} #mgUI .dwMenu .g button small{font-size:12.5px;opacity:.75} #mgUI .dwMenu .g button.big{grid-column:1/-1;background:linear-gradient(135deg,#ff8466,#ffb02e);color:#fff;box-shadow:0 5px 0 #c8642e;min-height:92px}
#mgUI .dwMenu .g button:active{transform:translateY(4px);box-shadow:0 1px 0 #d9bfa0}
#mgUI .dwMenu .lv{display:flex;gap:6px} #mgUI .dwMenu .lv button{font:inherit;border:0;border-radius:14px;padding:8px 12px;min-height:44px;background:rgba(255,255,255,.7);color:#3b2433;font-size:15px} #mgUI .dwMenu .lv button.on{background:#5b3a7a;color:#fff}
#mgUI .dwMenu .out{font:inherit;border:0;border-radius:14px;padding:10px 18px;min-height:46px;background:rgba(91,58,122,.15);color:#3b2433;font-size:16px}
#mgUI .dwMenu .bst{font-size:13.5px;opacity:.85;text-align:center}
#mgUI .dwGal{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;gap:10px;padding:calc(60px + env(safe-area-inset-top)) 14px calc(14px + env(safe-area-inset-bottom));z-index:5;background:rgba(255,243,221,.97);overflow:auto}
#mgUI .dwGal.on{display:flex} #mgUI .dwGal h3{margin:0;font-weight:400;font-size:24px;color:#5b3a7a}
#mgUI .dwGal .gr{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;width:min(100%,720px)}
#mgUI .dwGal figure{margin:0;background:#fff;border-radius:12px;padding:6px;box-shadow:0 4px 0 #e0c39a;text-align:center;font-size:13px}
#mgUI .dwGal figure img{width:100%;border-radius:8px;display:block;aspect-ratio:4/3;object-fit:cover} #mgUI .dwGal figure b{font-family:var(--en);font-weight:900;font-size:16px;color:#5b3a7a}
#mgUI .dwGal .none{opacity:.7;margin:30px 0} #mgUI .dwGal button{font:inherit;border:0;border-radius:14px;padding:10px 18px;min-height:46px;background:#5b3a7a;color:#fff;font-size:16px}
@media (orientation:landscape) and (max-height:620px){
  #mgUI .dwR{display:grid;grid-template-columns:auto minmax(0,1fr);grid-template-rows:auto auto auto auto 1fr;grid-template-areas:"bd bar" "bd pl" "bd bx" "bd fb" "bd kb";column-gap:14px;row-gap:5px;align-items:start;justify-items:center;padding-top:calc(52px + env(safe-area-inset-top))}
  #mgUI .dwBd,#mgUI .dwBd.dwT{grid-area:bd;width:auto;height:calc(100vh - 62px - env(safe-area-inset-top) - env(safe-area-inset-bottom));height:calc(100dvh - 62px - env(safe-area-inset-top) - env(safe-area-inset-bottom));max-width:58vw}
  #mgUI .dwBar{grid-area:bar} #mgUI .dwPl{grid-area:pl} #mgUI .dwBx{grid-area:bx} #mgUI .dwFb{grid-area:fb} #mgUI .dwKb,#mgUI .dwTl{grid-area:kb;align-self:end}
  #mgUI .dwKb button{min-height:36px;font-size:17px} #mgUI .dwBx i{height:38px;font-size:20px} #mgUI .dwMe{width:34px;height:34px;border-width:2px} #mgUI .dwBd,#mgUI .dwBd.dwT{margin-bottom:0} #mgUI .dwKb{gap:4px}
  #mgUI .dwMenu .g{grid-template-columns:repeat(4,1fr);width:min(100%,760px)} #mgUI .dwMenu .g button.big{grid-column:auto}
}`; document.head.appendChild(s); }

function start(api){
  const SFX=api.sfx, O=api.opt||{};
  api.menu=true; css();
  let gone=false, paused=false, fast=0, mode="menu", ready=false;
  const SET=Object.assign({lv:2}, st("hyeng_proto_dwset")||{});
  const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  const TM=[]; const later=(s,fn)=>TM.push({t:fast?Math.min(s,.05):s, fn});
  const scene=new THREE.Scene(), cam=new THREE.PerspectiveCamera(50,1,.1,10);
  /* ── 화면 ── */
  const U=api.ui, R=document.createElement("div"); R.className="dwR"; U.insertBefore(R, U.querySelector(".mgTop"));
  R.innerHTML='<div class="dwBar"><canvas class="dwMe dwPor" data-k="me"></canvas><b class="rd"></b><div class="dwTm"><i></i></div><b class="sc"></b></div><div class="dwPl"></div>'+
    '<div class="dwLine"></div><div class="dwBd"><div class="ledge"><i style="left:18px;--r:-12deg;background:#ff5a5f"></i><i style="left:30px;--r:-4deg;background:#3ea2ff"></i><i style="left:42px;--r:8deg;background:#ffd23f"></i><i style="right:30px;--r:10deg;background:#3fc46a"></i></div><canvas width="'+PW+'" height="'+PH+'"></canvas><div class="dwCov"></div><div class="dwOv"></div></div>'+
    '<div class="dwBx"></div><div class="dwFb"></div><div class="dwKb"></div><div class="dwTl"></div>'+
    '<div class="dwMenu"></div><div class="dwGal"></div><div class="dwVote"></div>';
  ["pointerdown","pointermove","pointerup"].forEach(t=>R.addEventListener(t, e=>e.stopPropagation()));
  const $=s=>R.querySelector(s);
  /* (개선) 얼굴 사진 (나 · 친구) — 캐릭터를 작은 장면에 세워 찍어 둠 */
  const PSc=new THREE.Scene(); PSc.background=new THREE.Color(0x2b3a5a); PSc.add(new THREE.HemisphereLight(0xffffff,0x445566,.85)); { const l=new THREE.DirectionalLight(0xffffff,.55); l.position.set(.6,1.4,1.4); PSc.add(l); }
  const AVS={}, PCACHE={}; let porDirty=1, frN=0;
  function avFor(k, av){ if(AVS[k]) return AVS[k]; try{ const A=buildAvatar(av||{}); const i=Object.keys(AVS).length; A.g.position.x=i*4; PSc.add(A.g); const cm=new THREE.PerspectiveCamera(26,1,.1,10); cm.position.set(i*4+.05,1.0,1.75); cm.lookAt(i*4,.88,0); AVS[k]={A, cm}; porDirty=1; return AVS[k]; }catch(e){ return null; } }
  avFor("me", api.av);
  function react(k, ex, s){ const o=AVS[k]; if(!o) return; o.A.setExpr(ex); o.t=s||1.4; porDirty=1; if(k==="me"){ const m=$(".dwMe"); if(m){ m.classList.remove("hop"); void m.offsetWidth; if(ex==="grin") m.classList.add("hop"); } } }
  function porRender(rn){ frN++; Object.keys(AVS).forEach(k=>{ const o=AVS[k]; if(o.t>0){ o.t-=1/60; if(o.t<=0){ o.A.setExpr(o.A.expr0||"smile"); porDirty=1; } } });
    if(!porDirty && frN%30) return; porDirty=0; const sz=64; Object.keys(AVS).forEach(k=>{ const o=AVS[k]; let c=PCACHE[k]; if(!c){ c=PCACHE[k]=document.createElement("canvas"); c.width=c.height=sz*2; }
      try{ rn.setScissorTest(true); rn.setScissor(0,0,sz,sz); rn.setViewport(0,0,sz,sz); rn.render(PSc,o.cm); const pr=rn.getPixelRatio(), q=Math.round(sz*pr); c.getContext("2d").clearRect(0,0,c.width,c.height); c.getContext("2d").drawImage(rn.domElement,0,rn.domElement.height-q,q,q,0,0,c.width,c.height); }catch(e){} });
    rn.setScissorTest(false); const cv0=rn.domElement; rn.setViewport(0,0,cv0.width/rn.getPixelRatio(),cv0.height/rn.getPixelRatio()); porCopy(); }
  function porCopy(){ R.querySelectorAll("canvas.dwPor").forEach(el=>{ const c=PCACHE[el.dataset.k]; if(!c) return; if(el.width!==c.width){ el.width=c.width; el.height=c.height; } const q=el.getContext("2d"); q.clearRect(0,0,el.width,el.height); q.drawImage(c,0,0); }); }
  function confetti(n){ const C=["#ff5a5f","#ffd23f","#3fc46a","#3ea2ff","#9a6bff","#ff8466"]; for(let i=0;i<n;i++){ const d=document.createElement("i"); d.className="dwCf"; d.style.left=(Math.random()*100)+"%"; d.style.background=C[i%6]; d.style.animationDelay=(Math.random()*.4)+"s"; d.style.animationDuration=(1.2+Math.random()*.8)+"s"; R.appendChild(d); setTimeout(()=>d.remove(), 2600); } }
  function lineGal(){ const L=(st("hyeng_proto_dwg")||[]).slice(0,5), el=$(".dwLine"); if(!el) return; const PC=["#ff8466","#3ea2ff","#3fc46a","#ffd23f","#9a6bff"]; const n=Math.max(4, L.length);
    el.innerHTML=Array.from({length:n},(_,i)=>{ const x=L[i]; return '<figure style="--r:'+((i%2?1:-1)*(3+i*2))+'deg;--pc:'+PC[i%5]+'">'+(x?'<img src="'+x.d+'" alt="">':["🎨","🖌️","🌈","⭐","🖍️"][i%5])+'</figure>'; }).join(""); }
  const cv=$(".dwBd canvas"), g=cv.getContext("2d"), BD=$(".dwBd"), COV=$(".dwCov"), OV=$(".dwOv"), BX=$(".dwBx"), FB=$(".dwFb"), KB=$(".dwKb"), TL=$(".dwTl"), PL=$(".dwPl"), MENU=$(".dwMenu"), GAL=$(".dwGal"), VT=$(".dwVote");
  const show=(el,v)=>{ el.style.display=v?"":"none"; };
  function clearBoard(){ g.globalCompositeOperation="source-over"; g.fillStyle="#fff"; g.fillRect(0,0,PW,PH); }
  function paint(S){ const p=S.p; if(!p || !p.length) return; const c=COLS[S.c]||COLS[0], w=SIZES[S.s]||SIZES[1]; g.strokeStyle=g.fillStyle=c; g.lineWidth=w; g.lineCap=g.lineJoin="round";
    if(p.length<=2){ g.beginPath(); g.arc(p[0],p[1],w/2,0,7); g.fill(); return; }
    g.beginPath(); g.moveTo(p[0],p[1]); for(let i=2;i<p.length-2;i+=2){ g.quadraticCurveTo(p[i],p[i+1],(p[i]+p[i+2])/2,(p[i+1]+p[i+3])/2); } g.lineTo(p[p.length-2],p[p.length-1]); g.stroke(); }
  function redraw(list){ clearBoard(); list.forEach(paint); }
  function emojiPic(e){ clearBoard(); g.save(); g.textAlign="center"; g.textBaseline="middle"; g.font='520px "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif'; g.fillText(e, PW/2, PH/2+30); g.restore(); }
  function thumb(){ try{ const c=document.createElement("canvas"); c.width=200; c.height=150; c.getContext("2d").drawImage(cv,0,0,200,150); return c.toDataURL("image/jpeg",.7); }catch(e){ return ""; } }
  function galAdd(i){ const L=st("hyeng_proto_dwg")||[]; const d=thumb(); if(!d) return; L.unshift({w:W[i][0], ko:W[i][1], d, at:Date.now()}); st("hyeng_proto_dwg", L.slice(0,12)); }
  /* ── 내 기록 ── */
  const REC=()=>{ const r=st("hyeng_proto_dwr")||{}; r.best=r.best|0; r.ok=r.ok|0; r.drawn=r.drawn|0; r.recent=r.recent||[]; return r; };
  const saveRec=r=>st("hyeng_proto_dwr", r);
  /* ── 글자 칸 · 자판 ── */
  let typed="", wordLen=0, hintMap={}, kbOn=false, onSubmit=null;
  function boxes(okWord){ const n=wordLen; if(!n){ BX.innerHTML=""; return; } const bw=Math.max(22,Math.min(38, Math.floor((Math.min(BD.clientWidth||360, 640)-4*n)/n))); BX.style.setProperty("--bw", bw+"px");
    let h=""; for(let i=0;i<n;i++){ const t=okWord?okWord[i]:typed[i]; h+='<i class="'+(t?"":(hintMap[i]?"h":""))+(!okWord && i===typed.length?" cur":"")+'">'+esc(t||hintMap[i]||"")+'</i>'; } BX.innerHTML=h; BX.classList.toggle("ok", !!okWord); }
  function kb(on){ kbOn=on; KB.classList.toggle("off", !on); }
  function kbBuild(extra, noHint){ const rows=["qwertyuiop","asdfghjkl","zxcvbnm"]; KB.innerHTML=rows.map((r,i)=>'<div>'+r.split("").map(c=>'<button data-k="'+c+'">'+c+'<sub style="position:absolute;right:4px;bottom:2px;font-size:9px;opacity:.6">'+(PTL[c]||1)+'</sub></button>').join("")+(i===2?'<button class="w" data-k="bs">⌫</button>':'')+'</div>').join("")+
      '<div>'+(noHint?'':'<button class="w gv" data-k="hint">💡 힌트</button>')+(extra||'')+'<button class="w go" data-k="ok" style="flex:2.4">✔ 확인</button></div>'; }
  KB.addEventListener("pointerdown", e=>{ const b=e.target.closest("button"); if(!b) return; e.preventDefault(); b.classList.add("dn"); setTimeout(()=>b.classList.remove("dn"),110); key(b.dataset.k); });
  function key(k){ if(!kbOn || gone) return; if(k==="bs"){ typed=typed.slice(0,-1); boxes(); return; } if(k==="ok"){ if(onSubmit) onSubmit(); return; } if(k==="hint"){ if(mode==="solo") soloHint(); return; } if(k==="give"){ if(mode==="solo") giveUp(); return; }
    if(/^[a-z]$/.test(k) && typed.length<wordLen){ typed+=k; try{ SFX.tone(700+typed.length*40,.05,"triangle",.03); }catch(e){} boxes(); if(typed.length===wordLen) setTimeout(()=>{ if(typed.length===wordLen && onSubmit) onSubmit(); }, 160); } }
  const onKey=e=>{ if(gone || !kbOn) return; if(e.key==="Backspace"){ key("bs"); e.preventDefault(); } else if(e.key==="Enter") key("ok"); else if(/^[a-zA-Z]$/.test(e.key)) key(e.key.toLowerCase()); };
  window.addEventListener("keydown", onKey);
  const fb=(t)=>{ FB.textContent=t||""; };
  const shake=()=>{ BX.classList.remove("no"); void BX.offsetWidth; BX.classList.add("no"); };
  /* ── 위 막대 ── */
  const TMB=$(".dwTm i"), TMW=$(".dwTm");
  function bar(rd, sc, frac){ $(".dwBar .rd").textContent=rd; $(".dwBar .sc").textContent=sc; TMB.style.transform="scaleX("+Math.max(0,Math.min(1,frac))+")"; TMW.classList.toggle("low", frac<.2); }

  /* ══ 메뉴 ══ */
  function menuShow(){ mode="menu"; kb(false); show(KB,0); show(TL,0); GAL.classList.remove("on"); const r=REC(), G0=st("hyeng_proto_dwg")||[];
    PUI.menu(U, {title:"그림 맞히기", sub:"친구 그림을 보고 영어로 직접 써서 맞혀요", av:api.av, nick:api.nick, stats:[["trophy",r.best,"최고 점수"],["✅",r.ok,"맞힌 단어"],["🖍️",r.drawn,"그린 그림"]],
      deco:[["🎨","left:calc(50% - 132px);top:20%;transform:rotate(-14deg)"],["✏️","left:calc(50% + 72px);top:58%;font-size:34px"]],
      tiles:[{k:"solo", emoji:"🧩", bg:"#ffd36b", nm:"혼자 연습", sub:"그림 퍼즐 · 8문제"},{k:"sketch", emoji:"🖍️", bg:"#bfe6ff", nm:"그려 보기", sub:"그림첩에 쏙"},{k:"gal", emoji:"🖼️", bg:"#ffd1e6", nm:"그림첩", sub:G0.length+"장"}],
      seg:{items:[1,2,3].map(i=>[String(i), LV[i].ic+" "+LV[i].nm]), on:SET.lv, pick:v=>{ SET.lv=+v; st("hyeng_proto_dwset", SET); menuShow(); }},
      primary:{k:"co", label:"친구랑 그리고 맞히기", sub:"2~6명 · 그리고, 영어로 맞히고, 작품 투표!", ic:"swords"}, primaryTop:true, pay:MG.payLeft("draw"), onPick:k=>menuGo(k)});
    bar("","",1); }
  function menuGo(m){ PUI.menuHide(U); if(m==="solo") startSolo(); else if(m==="co") startCo(); else if(m==="sketch") startSketch(); else if(m==="gal") galShow(); }
  function galShow(){ mode="gal"; GAL.classList.add("on"); const L=st("hyeng_proto_dwg")||[];
    GAL.innerHTML='<h3>🖼️ 내 그림첩</h3>'+(L.length?'<div class="gr">'+L.map(x=>'<figure><img src="'+x.d+'" alt=""><b>'+esc(x.w)+'</b> · '+esc(x.ko)+'</figure>').join("")+'</div>':'<div class="none">아직 그림이 없어요 — 「🖍️ 그려 보기」나 「👫 같이」에서 그려 봐요!</div>')+'<button>☰ 메뉴</button>';
    GAL.querySelector("button").onclick=()=>{ GAL.classList.remove("on"); menuShow(); }; }

  /* ══ 🧩 혼자: 그림 퍼즐 ══ */
  const TILE_T=1.15, NQ=8, TCOL=["#ff5a5f","#ff9a3d","#ffd23f","#3fc46a","#3ea2ff","#9a6bff","#ff7eb6","#2fc4c4"];
  let S=null;
  function startSolo(){ mode="solo"; lineGal(); const r=REC(), lv=LV[SET.lv]||LV[2]; let pool=[]; lv.t.forEach(t=>pool=pool.concat(TIERS[t])); pool=shuffle(pool.filter(i=>r.recent.indexOf(W[i][0])<0)); if(pool.length<NQ){ pool=shuffle([].concat(...lv.t.map(t=>TIERS[t]))); }
    S={q:pool.slice(0,NQ), n:NQ, done:0, sc:0, ok:0, streak:0, res:[], again:{}, cur:-1, t:0, pop:0, hint:0, miss:0, wait:false};
    r.recent=r.recent.concat(S.q.map(i=>W[i][0])).slice(-40); saveRec(r);
    show(KB,1); show(TL,0); show(PL,0); BD.classList.remove("dwT"); kbBuild('<button class="w gv" data-k="give">🤔 모르겠어요</button>'); onSubmit=soloSubmit; nextQ(); }
  function nextQ(){ if(!S.q.length){ soloEnd(); return; } S.cur=S.q.shift(); S.t=0; S.pop=0; S.hint=0; S.miss=0; S.wait=false; typed=""; hintMap={}; wordLen=W[S.cur][0].length; OV.classList.remove("on");
    emojiPic(W[S.cur][2]); COV.style.display=""; const ord=shuffle([...Array(12).keys()]); S.ord=ord; COV.innerHTML=ord.map((_,i)=>{ const q=k=>30+((i*37+k*53+S.done*11)%35); return '<i style="margin:-7px;border-radius:'+q(1)+'% '+q(2)+'% '+q(3)+'% '+q(4)+'% / '+q(5)+'% '+q(6)+'% '+q(7)+'% '+q(8)+'%;background:radial-gradient(circle at 30% 28%,rgba(255,255,255,.45) 0 16%,transparent 17%),'+TCOL[(i*5+S.done)%8]+'">?</i>'; }).join("");
    boxes(); fb("그림이 보이면 영어로 써 봐요 ✏️"); kb(true); bar((S.done+1)+" / "+S.n, "⭐ "+S.sc, 1); }
  function popTile(){ if(S.pop>=12) return; const i=S.ord[S.pop++]; const el=COV.children[i]; if(el) el.classList.add("off"); try{ SFX.tone(300+S.pop*35,.08,"sine",.03); }catch(e){} if(S.pop===12 && !S.hint) addHint(); }
  function addHint(){ const w=W[S.cur][0]; const free=[...Array(w.length).keys()].filter(i=>!hintMap[i] && i>=typed.length); if(!free.length) return false; const i=S.hint===0?free[0]:free[Math.floor(Math.random()*free.length)]; hintMap[i]=w[i]; S.hint++; boxes(); return true; }
  function soloHint(){ if(!S || S.wait) return; if(S.hint>=Math.ceil(W[S.cur][0].length/2)){ fb("힌트는 여기까지! 🤔 모르겠어요를 눌러도 돼요"); return; } if(addHint()){ fb("💡 글자 하나 보여 줬어요 (−10점)"); try{ SFX.tone(880,.1,"triangle",.04); }catch(e){} } }
  function soloSubmit(){ if(!S || S.wait) return; const w=W[S.cur][0], v=norm(typed); if(!v){ fb("자판으로 영어를 써 봐요 ⌨️"); return; }
    if(v===w){ S.wait=true; kb(false); const pts=Math.max(10, 20+(12-S.pop)*6-S.hint*10-S.miss*3); S.streak=(S.hint||S.miss)?0:S.streak+1; const bon=S.streak>=2?10:0; S.sc+=pts+bon; S.ok++; S.done++; S.res.push([S.cur,1]);
      boxes(w); fb("✅ 정답! +"+pts+(bon?" · 🔥 "+S.streak+"연속 +"+bon:"")); try{ SFX.clear(); }catch(e){} sayW(w); react("me","grin",1.6); confetti(S.streak>=2?40:24); for(let k=S.pop;k<12;k++) COV.children[S.ord[k]] && COV.children[S.ord[k]].classList.add("off"); S.pop=12;
      later(1.7, nextQ); return; }
    S.miss++; typed=""; shake(); try{ SFX.bad(); }catch(e){} react("me","wow",1);
    if(near(v,w)) fb("🔥 거의 맞았어요! 철자를 다시 봐요"); else fb("❌ 아니에요 — 다시 써 봐요"); if(S.miss%3===0) addHint(); boxes(); }
  function giveUp(){ if(!S || S.wait) return; S.wait=true; kb(false); const w=W[S.cur][0]; S.streak=0; boxes(w); for(let k=S.pop;k<12;k++) COV.children[S.ord[k]] && COV.children[S.ord[k]].classList.add("off"); S.pop=12; sayW(w);
    if(!S.again[S.cur]){ S.again[S.cur]=1; S.q.splice(Math.min(S.q.length, 2), 0, S.cur); fb("정답은 「"+w+"」 ("+W[S.cur][1]+") — 조금 뒤에 다시 나와요!"); } else { S.done++; S.res.push([S.cur,0]); fb("정답은 「"+w+"」 ("+W[S.cur][1]+")"); }
    later(2.4, nextQ); }
  function soloEnd(){ mode="solo-end"; kb(false); const r=REC(), isBest=S.sc>r.best; r.best=Math.max(r.best, S.sc); r.ok+=S.ok; saveRec(r);
    const coins=S.ok>=7?8:S.ok>=5?6:S.ok>=3?5:3, lv=LV[SET.lv]||LV[2];
    const got=PUI.award(api, {title:S.ok+" / "+S.n, sub:"그림 퍼즐", rows:null, coins, again:{go:"solo"}, upd:(b,t)=>{ b.best=Math.max(b.best|0, S.sc); t.ok=(t.ok|0)+S.ok; }}), left=MG.payLeft("draw");
    PUI.result(U, {res:"win", stars:S.ok>=7?3:S.ok>=5?2:S.ok>=3?1:0, title:S.ok+" / "+S.n+" 맞혔어요!", sub:"그림 퍼즐 · "+lv.ic+" "+lv.nm, av:api.av,
      rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"],["star", S.sc, "점", isBest],["✅", r.ok, "모은 단어"]],
      extra:'<div style="display:flex;flex-wrap:wrap;gap:5px;justify-content:center">'+S.res.map(([i,o])=>'<span style="background:'+(o?"#2FD49A":"#6a72d8")+';border-radius:10px;padding:2px 8px;font-size:13.5px">'+W[i][2]+' <b style="font-family:var(--en)">'+W[i][0]+'</b></span>').join("")+'</div>',
      prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3}, onAgain:()=>api.restart({go:"solo"}), onMenu:()=>api.restart({}), onOut:()=>MG.exit()}); }

  /* ══ 🖍️ 그리기 도구 (같이 · 그려 보기) ══ */
  const TOOL={c:0, s:1};
  let MY=[], cur=null, drawOK=false, onStroke=null, myKey=0;
  function toolsBuild(word, extra){ TL.innerHTML='<div class="wd">'+word+'</div><div class="r">'+COLS.slice(0,8).map((c,i)=>'<button class="c'+(TOOL.c===i?" on":"")+'" data-c="'+i+'" style="background:'+c+'" aria-label="색"></button>').join("")+'<button class="c'+(TOOL.c===8?" on":"")+'" data-c="8" aria-label="지우개">🧽</button></div>'+
      '<div class="r">'+SIZES.map((s,i)=>'<button class="s'+(TOOL.s===i?" on":"")+'" data-s="'+i+'"><i style="width:'+(6+i*7)+'px;height:'+(6+i*7)+'px"></i></button>').join("")+'<button data-t="undo">↩️</button><button data-t="clr">🗑️</button>'+(extra||'')+'</div>'; }
  TL.addEventListener("pointerdown", e=>{ const b=e.target.closest("button"); if(!b) return; e.preventDefault();
    if(b.dataset.c){ TOOL.c=+b.dataset.c; TL.querySelectorAll(".c").forEach(x=>x.classList.toggle("on", x===b)); }
    else if(b.dataset.s){ TOOL.s=+b.dataset.s; TL.querySelectorAll(".s").forEach(x=>x.classList.toggle("on", x===b)); }
    else if(b.dataset.t==="undo"){ const s=MY.pop(); if(s){ redraw(MY.map(x=>x.S)); onStroke && onStroke("undo", s); } }
    else if(b.dataset.t==="clr"){ if(!MY.length) return; MY=[]; clearBoard(); onStroke && onStroke("clr"); }
    else if(b.dataset.t==="done"){ sketchDone(); } });
  const toPt=e=>{ const r=cv.getBoundingClientRect(); return [Math.round((e.clientX-r.left)/r.width*PW), Math.round((e.clientY-r.top)/r.height*PH)]; };
  cv.addEventListener("pointerdown", e=>{ if(!drawOK) return; e.preventDefault(); try{ cv.setPointerCapture(e.pointerId); }catch(_){} const p=toPt(e); cur={S:{c:TOOL.c, s:TOOL.s, p:[p[0],p[1]]}, k:"k"+(myKey++), sent:0}; MY.push(cur); paint(cur.S); });
  cv.addEventListener("pointermove", e=>{ if(!cur || !drawOK) return; const p=toPt(e), q=cur.S.p, lx=q[q.length-2], ly=q[q.length-1]; if(Math.hypot(p[0]-lx,p[1]-ly)<4) return; q.push(p[0],p[1]);
    g.strokeStyle=COLS[cur.S.c]; g.lineWidth=SIZES[cur.S.s]; g.lineCap=g.lineJoin="round"; g.beginPath(); g.moveTo(lx,ly); g.lineTo(p[0],p[1]); g.stroke(); if(q.length>1200) endStroke(); });
  function endStroke(){ if(!cur) return; const c=cur; cur=null; redraw(MY.map(x=>x.S)); onStroke && onStroke("end", c); }
  cv.addEventListener("pointerup", endStroke); cv.addEventListener("pointercancel", endStroke);
  function demo(n){ /* 시험: 동그라미 · 줄 몇 개 */ n=n||3; for(let j=0;j<n;j++){ const S0={c:(j%7), s:1, p:[]}; for(let a=0;a<=24;a++){ const t=a/24*Math.PI*2; S0.p.push(Math.round(500+Math.cos(t)*(120+j*60)), Math.round(375+Math.sin(t)*(90+j*40))); } const c={S:S0, k:"k"+(myKey++), sent:0}; MY.push(c); onStroke && onStroke("end", c); } redraw(MY.map(x=>x.S)); }

  /* ══ 🖍️ 그려 보기 (혼자) ══ */
  let SK=null;
  function startSketch(){ mode="sketch"; show(PL,0); show(KB,0); show(TL,0); BD.classList.add("dwT"); COV.style.display="none"; clearBoard(); wordLen=0; boxes(); fb(""); MY=[]; drawOK=false; onStroke=null;
    const ch=[1,2,3].map(t=>TIERS[t][Math.floor(Math.random()*TIERS[t].length)]); SK={ch, i:-1, t:0};
    OV.innerHTML='<div style="font-size:19px">무엇을 그릴까요?</div><div class="ch">'+ch.map((i,k)=>'<button data-p="'+k+'"><span class="e">'+W[i][2]+'</span><span class="w">'+W[i][0]+'</span><small>'+W[i][1]+' · '+"⭐".repeat(tier(i))+'</small></button>').join("")+'</div>'; OV.classList.add("on");
    OV.querySelectorAll("[data-p]").forEach(b=>b.onclick=()=>sketchPick(+b.dataset.p)); bar("🖍️ 그려 보기","",1); }
  function sketchPick(k){ if(!SK || SK.i>=0) return; SK.i=SK.ch[k]; OV.classList.remove("on"); drawOK=true; show(TL,1); toolsBuild('<b>'+W[SK.i][0]+'</b> '+W[SK.i][1]+' 을(를) 그려요 🖍️', '<button class="tx go" data-t="done">✔ 다 그렸어요</button>'); sayW(W[SK.i][0]); }
  function sketchDone(){ if(mode!=="sketch" || !SK || SK.i<0) return; if(!MY.length){ api.msg("조금이라도 그려 봐요 🖍️", 1100); return; } drawOK=false; galAdd(SK.i); const r=REC(); r.drawn++; saveRec(r);
    OV.innerHTML='<div class="big">🖼️</div><div class="en">'+W[SK.i][0]+'</div><div class="ko">그림첩에 넣었어요!</div><div class="ch"><button data-a="again" style="min-height:56px"><span class="w">🖍️ 또 그리기</span></button><button data-a="menu" style="min-height:56px"><span class="w">☰ 메뉴</span></button></div>'; OV.classList.add("on"); try{ SFX.clear(); }catch(e){}
    OV.querySelector('[data-a="again"]').onclick=()=>startSketch(); OV.querySelector('[data-a="menu"]').onclick=()=>{ OV.classList.remove("on"); show(TL,0); BD.classList.remove("dwT"); menuShow(); }; }

  /* ══ 👫 같이: 그리고 맞히기 (MG.room · 2~6명 · 방장이 판을 돌림) ══ */
  const LOC={}, ART={}; let RM=null, G={}, hostC="", hostMiss=0, lastSq=-1, strokeSig="", seenOk={}, myRd=0, lowT=0, drGone=0, alone=0;
  const T=()=>fast?{pick:2500, draw:9000, show:1500, vote:30000, award:1500}:{pick:12000, draw:60000, show:5000, vote:25000, award:6500};
  const live=()=>RM?RM.live(true).map(p=>p.k):[];
  const hostCode=()=>{ if(!RM || !RM.d) return hostC; const L=live(), h=RM.d.h||{}; return L.indexOf(h.c)>=0?h.c:(L[0]||h.c); };
  const amHost=()=>!!RM && hostC===RM.code;
  const nmOf=c=>(G.nm&&G.nm[c])||"친구";
  function startCo(){ mode="co"; Object.keys(ART).forEach(k=>delete ART[k]); myVote=null; vtKey=""; awFx=false; VT.classList.remove("on"); lineGal(); KB.innerHTML=""; show(KB,0); show(TL,0); show(PL,0); COV.style.display="none"; clearBoard(); wordLen=0; boxes(); fb(""); OV.classList.remove("on"); bar("👫","",1);
    RM=MG.room(api, {pre:"mgd", title:"그림 맞히기 같이", ic:"🎨", max:6, fill:false, wait:6000, send:.5, poll:.3, back:()=>{ try{ RM.dispose(); }catch(e){} RM=null; menuShow(); }}); RM.node=()=>({av:api.av||null});
    { const st0=RM.start; RM.start=async()=>{ const L=live(); if(L.length<2){ api.msg("친구가 1명 더 들어오면 시작할 수 있어요 👫", 1600); return; } const ro=L.slice(0,6); try{ await NET.patch(RM.path+"/h", {ro}); }catch(e){} if(RM.d && RM.d.h) RM.d.h.ro=ro; return st0(); }; }
    RM.onEv=e=>{ if(e && amHost()) hostEv(e.s, e); };
    RM.onFeed=f=>{ if(f && (f.t==="x"||f.t==="nr") && f.s!==RM.code){ chipPop(f.s, f.t==="x"?"❌":"🔥"); react(f.s, "wow", 1); } };
    RM.onStart=(h, L)=>{ const ro=(h.ro && h.ro.length? h.ro : L.map(p=>p.k)).slice(0,6); hostC=h.c; mode="co-play"; const PD=(RM.d&&RM.d.p)||{}, nm={}; ro.forEach(c=>{ const p=Object.assign({}, PD[c]||{}, L.find(q=>q.k===c)||{}); nm[c]=String(p.n||"친구").slice(0,8); });
      show(PL,1); if(amHost()) hostInit(ro, nm); else { G={ph:"wait", ro, nm, sc:{}, ok:{}}; render(); } };
  }
  function toHost(o){ if(!RM) return; if(amHost()) hostEv(RM.code, o); else RM.ev(hostC||hostCode(), Object.assign({s:RM.code}, o)); }
  /* 방장 */
  function pubG(){ G.sq=(G.sq|0)+1; RM.put("g", G); render(); }
  function hostInit(ro, nm){ G={ph:"pick", rd:0, nr:ro.length<=3?ro.length*2:ro.length, ro, nm, sc:{}, ok:{}, used:[], sq:0}; ro.forEach(c=>G.sc[c]=0); nextRound(); }
  function nextRound(){ const L=live(); if(G.rd>0) G.hist=(G.hist||[]).concat([Object.keys(G.ok||{}).length]); G.rd++; if(G.rd>G.nr || L.length<2){ if(L.length>=2 && Object.keys(G.drs||{}).length>=2){ voteStart(); return; } G.ph="end"; pubG(); return; }
    let dr=null; for(let k=0;k<G.ro.length;k++){ const c=G.ro[(G.rd-1+k)%G.ro.length]; if(L.indexOf(c)>=0){ dr=c; break; } } if(!dr){ G.ph="end"; pubG(); return; }
    if(G.rd>1) RM.put("s/"+(G.rd-1), null);
    const ch=[1,2,3].map(t=>{ const c=TIERS[t].filter(i=>G.used.indexOf(i)<0); const i=c[Math.floor(Math.random()*c.length)]; return i==null?TIERS[t][0]:i; });
    Object.assign(G, {dr, ch, w:0, wl:0, hi:{}, ok:{}, ph:"pick", t0:now(), tot:T().pick, dl:now()+T().pick, ans:-1}); drGone=0; pubG(); }
  function hostPick(k){ if(G.ph!=="pick") return; const i=G.ch[k]; if(i==null) return; G.used.push(i); Object.assign(G, {w:encW(i,G.rd), wl:W[i][0].length, ph:"draw", t0:now(), tot:T().draw, dl:now()+T().draw}); pubG(); }
  function hostEv(s, e){ if(!e || !s) return;
    if(e.t==="pk" && s===G.dr) hostPick(e.k|0);
    else if(e.t==="vt" && G.ph==="vote" && G.vt && G.vt[s]==null && G.drs && G.drs["r"+(e.r|0)]!=null && G.drs["r"+(e.r|0)]!==s){ G.vt[s]=e.r|0; pubG(); }
    else if(e.t==="ok" && G.ph==="draw" && s!==G.dr && G.ok[s]==null && decW(G.w,G.rd)===e.i){ const left=Math.max(0,(G.dl-now())/G.tot), first=!Object.keys(G.ok).length, tr=tier(e.i);
      const pts=Math.round((30+60*left)*(1+.25*(tr-1)))+(first?15:0); G.ok[s]=pts; G.sc[s]=(G.sc[s]||0)+pts; G.sc[G.dr]=(G.sc[G.dr]||0)+10+5*tr; pubG(); } }
  /* (작품 투표) 마지막 판 뒤 — 오늘 그린 그림 중 마음에 드는 것 하나 (내 그림 빼고) */
  function voteStart(){ if(G.rd>1) RM.put("s/"+(G.rd-1), null); Object.assign(G, {ph:"vote", vt:{}, t0:now(), tot:T().vote, dl:now()+T().vote}); pubG(); }
  function voteDone(){ const vc={}, vp={}; Object.keys(G.vt||{}).forEach(c=>{ const k="r"+G.vt[c], d=G.drs[k]; if(d==null) return; vc[k]=(vc[k]|0)+1; vp[d]=(vp[d]|0)+1; G.sc[d]=(G.sc[d]|0)+10; });
    const best=Math.max(0, ...Object.values(vc)); G.vc=vc; G.vp=vp; G.aw=best>0?Object.keys(vc).filter(k=>vc[k]===best):[]; Object.assign(G, {ph:"award", t0:now(), tot:T().award, dl:now()+T().award}); pubG(); }
  function hostReveal(){ G.ans=decW(G.w,G.rd); G.drs=Object.assign({}, G.drs||{}); G.drs["r"+G.rd]=G.dr; G.wds=Object.assign({}, G.wds||{}); G.wds["r"+G.rd]=G.ans; Object.assign(G, {ph:"show", t0:now(), tot:T().show, dl:now()+T().show}); pubG(); }
  function hostTick(dt){ const t=now(), L=live();
    alone=L.length<2?alone+dt:0; if(alone>8 && G.ph!=="end"){ G.ph="end"; pubG(); return; }
    if(G.ph==="pick"){ if(L.indexOf(G.dr)<0) drGone+=dt; else drGone=0; if(drGone>3){ nextRound(); return; } if(t>G.dl) hostPick(1); }
    else if(G.ph==="draw"){ const f=(t-G.t0)/G.tot, i=decW(G.w,G.rd), w=W[i]?W[i][0]:""; const want=Math.min(Math.floor(w.length/3), f>.7?2:f>.4?1:0);
      if(Object.keys(G.hi).length<want){ const free=[...Array(w.length).keys()].filter(k=>!G.hi[k]); if(free.length){ const k=free[Math.floor(Math.random()*free.length)]; G.hi[k]=w[k]; pubG(); } }
      const guess=L.filter(c=>c!==G.dr && G.ro.indexOf(c)>=0); if(L.indexOf(G.dr)<0) drGone+=dt; else drGone=0;
      if(t>G.dl || drGone>4 || (guess.length && guess.every(c=>G.ok[c]!=null))) hostReveal(); }
    else if(G.ph==="show"){ if(t>G.dl) nextRound(); }
    else if(G.ph==="vote"){ const can=c=>Object.keys(G.drs||{}).some(k=>G.drs[k]!==c), V=L.filter(c=>G.ro.indexOf(c)>=0 && can(c)); if(t>G.dl || (V.length && V.every(c=>G.vt[c]!=null))) voteDone(); }
    else if(G.ph==="award"){ if(t>G.dl){ G.ph="end"; pubG(); } } }
  /* 모두 */
  function chipPop(c, e){ const el=PL.querySelector('[data-c="'+c+'"]'); if(!el) return; const m=document.createElement("em"); m.textContent=e; el.appendChild(m); setTimeout(()=>m.remove(), 950); }
  function render(){ if(mode!=="co-play" || !RM) return; const me=RM.code, iDraw=G.dr===me, t=now();
    (G.ro||[]).forEach(c=>{ if(!AVS[c]) avFor(c, c===me?api.av:(((RM.d&&RM.d.p)||{})[c]||{}).av); });
    PL.innerHTML=(G.ro||[]).map(c=>'<span data-c="'+esc(c)+'" class="'+(c===me?"me ":"")+(c===G.dr?"dr ":"")+(G.ok&&G.ok[c]!=null?"ok":"")+'"><canvas class="dwPor" data-k="'+esc(c)+'"></canvas>'+(c===G.dr?"🖍️ ":G.ok&&G.ok[c]!=null?"✅ ":"")+esc(nmOf(c))+' <b style="font-family:var(--en)">'+((G.sc&&G.sc[c])|0)+'</b></span>').join("");
    if(G.rd!==myRd || G.ph==="vote") artSnap();
    if(G.ph!=="vote" && G.ph!=="award") VT.classList.remove("on");
    if(G.ph==="vote" || G.ph==="award"){ myRd=G.rd; voteRender(); return; }
    if(G.rd!==myRd){ myRd=G.rd; MY=[]; myKey=0; cur=null; strokeSig=""; clearBoard(); typed=""; seenOk={}; }
    Object.keys(G.ok||{}).forEach(c=>{ if(!seenOk[c]){ seenOk[c]=1; if(c!==me){ fbFeed("✅ "+nmOf(c)+" 맞혔어요!"); chipPop(c,"✅"); react(c,"grin",1.6); try{ SFX.tone(1046,.12,"triangle",.04); }catch(e){} } } });
    if(G.ph==="wait"){ OV.innerHTML='<div class="big">🎨</div><div class="ko">곧 시작해요…</div>'; OV.classList.add("on"); show(KB,0); show(TL,0); return; }
    if(G.ph==="end"){ coEnd(); return; }
    const rdT=G.rd+" / "+G.nr+" 판", myS="⭐ "+((G.sc&&G.sc[me])|0);
    if(G.ph==="pick"){ drawOK=false; wordLen=0; boxes(); show(KB,0); show(TL,0); fb("");
      if(iDraw){ OV.innerHTML='<div style="font-size:19px">🖍️ <b>내 차례!</b> 무엇을 그릴까요?</div><div class="ch">'+G.ch.map((i,k)=>'<button data-p="'+k+'"><span class="e">'+W[i][2]+'</span><span class="w">'+W[i][0]+'</span><small>'+W[i][1]+' · '+"⭐".repeat(tier(i))+'</small></button>').join("")+'</div><div class="ko" style="font-size:13.5px">⭐ 많을수록 점수도 많아요 · 글자는 쓰면 안 돼요!</div>';
        OV.querySelectorAll("[data-p]").forEach(b=>b.onclick=()=>{ OV.querySelectorAll("[data-p]").forEach(x=>x.disabled=true); toHost({t:"pk", k:+b.dataset.p}); }); }
      else OV.innerHTML='<div class="big">🤔</div><div class="ko"><b>'+esc(nmOf(G.dr))+'</b> 친구가 그릴 단어를 고르는 중…</div>';
      OV.classList.add("on"); return; }
    if(G.ph==="draw"){ OV.classList.remove("on"); const i=iDraw?decW(G.w,G.rd):-1;
      if(iDraw){ show(KB,0); show(TL,1); BD.classList.add("dwT"); wordLen=0; boxes(); if(!drawOK){ drawOK=true; onStroke=coStroke; toolsBuild('그릴 단어: '+W[i][2]+' <b>'+W[i][0]+'</b> '+W[i][1]); } fb("글자 말고 그림으로! 친구들이 맞히면 나도 점수 ⭐"); }
      else { drawOK=false; show(TL,0); show(KB,1); BD.classList.remove("dwT"); const done=G.ok&&G.ok[me]!=null; if(!KB.children.length) kbBuild('', true); wordLen=G.wl|0; hintMap=Object.assign({}, G.hi||{}); onSubmit=coSubmit; kb(!done);
        if(done){ boxes(myAns||""); fb("✅ 정답! 친구들을 기다려요"); } else { boxes(); if(!FB.textContent) fb("영어로 써서 맞혀요 ✏️"); } }
      return; }
    if(G.ph==="show"){ drawOK=false; kb(false); const i=G.ans; if(iDraw && MY.length && i>=0 && !LOC["gal"+G.rd]){ LOC["gal"+G.rd]=1; galAdd(i); const r=REC(); r.drawn++; saveRec(r); }
      const n=Object.keys(G.ok||{}).length; OV.innerHTML='<div class="big">'+(W[i]?W[i][2]:"🎨")+'</div><div class="en">'+(W[i]?W[i][0]:"")+'</div><div class="ko">'+(W[i]?W[i][1]:"")+'</div><div class="ko" style="font-size:15px">'+(n?'✅ '+n+'명이 맞혔어요!':'아무도 못 맞혔어요 — 다음엔 맞힐 수 있어요!')+'</div>';
      OV.classList.add("on"); if(W[i] && !LOC["say"+G.rd]){ LOC["say"+G.rd]=1; sayW(W[i][0]); } myAns=""; return; } }
  let myAns="";
  /* 판마다 그림을 내 기기에만 찍어 둠 (서버에 그림을 안 올림) */
  function artSnap(){ const rd=myRd, k="r"+rd; if(!rd || ART[k] || !G.drs || G.drs[k]==null) return; const mine=G.drs[k]===RM.code; if(mine? !MY.length : !strokeSig) return;
    try{ const c=document.createElement("canvas"); c.width=320; c.height=240; c.getContext("2d").drawImage(cv,0,0,320,240); ART[k]=c.toDataURL("image/jpeg",.75); }catch(e){} }
  function artCard(k, extra){ const i=(G.wds||{})[k], w=W[i]||["?","","🎨"], d=G.drs[k]; return '<figure data-v="'+k.slice(1)+'" class="'+(extra||"")+'"><div class="im" style="'+(ART[k]?'background-image:url('+ART[k]+')':'')+'">'+(ART[k]?'':w[2])+'</div><figcaption><b>'+w[2]+' '+w[0]+'</b><span>'+esc(nmOf(d))+'</span></figcaption></figure>'; }
  let vtKey="", awFx=false;
  function voteRender(){ const me=RM.code, ks=Object.keys(G.drs||{}).sort((a,b)=>(+a.slice(1))-(+b.slice(1))); drawOK=false; kb(false); show(TL,0); show(KB,0); OV.classList.remove("on"); VT.classList.add("on");
    if(G.ph==="vote"){ const my=G.vt&&G.vt[me]!=null?G.vt[me]:myVote, n=Object.keys(G.vt||{}).length, key="v"+ks.join(",")+"|"+my+"|"+n;
      if(key===vtKey) return; vtKey=key;
      VT.classList.toggle("done", my!=null);
      VT.innerHTML='<h3>🗳️ 최고의 작품은?</h3><div class="sub">'+(my!=null?'❤️ 투표했어요! 친구들을 기다려요 ('+n+'명 투표)':'내 그림 말고 마음에 드는 그림을 하나 콕!')+'</div><div class="tm"><i></i></div><div class="gr">'+
        ks.map(k=>artCard(k, (G.drs[k]===me?"mine ":"")+(my!=null && "r"+my===k?"pick":""))).join("")+'</div>';
      VT.querySelectorAll("figure").forEach(f=>f.onclick=()=>vote(+f.dataset.v)); return; }
    const key="a"+(G.aw||[]).join(","); if(key===vtKey) return; vtKey=key; VT.classList.remove("done");
    const aw=G.aw||[], vc=G.vc||{};
    VT.innerHTML=aw.length? '<h3>🏅 인기 작품상!</h3><div class="aw">'+aw.map(k=>'<div class="rb">❤️ '+(vc[k]|0)+'표</div>'+artCard(k)).join("")+'</div><div class="sub">받은 표마다 ⭐ +10점</div>'+
      '<div class="gr">'+ks.filter(k=>aw.indexOf(k)<0).map(k=>artCard(k).replace("</figure>", (vc[k]?'<span class="vc">❤️ '+vc[k]+'</span>':'')+"</figure>")).join("")+'</div>'
      : '<h3>🎨 모두 멋진 작품!</h3><div class="gr">'+ks.map(k=>artCard(k)).join("")+'</div>';
    if(aw.length && !awFx){ awFx=true; confetti(50); try{ SFX.win(); }catch(e){} if(aw.some(k=>G.drs[k]===me)) react("me","grin",2); } }
  let myVote=null;
  function vote(r){ if(G.ph!=="vote" || myVote!=null || (G.vt&&G.vt[RM.code]!=null)) return; const k="r"+r; if(!G.drs || G.drs[k]==null) return;
    if(G.drs[k]===RM.code){ api.msg("내 그림 말고 친구 그림에 투표해요 😉", 1300); return; } myVote=r; try{ SFX.tone(880,.1,"triangle",.05); }catch(e){} toHost({t:"vt", r}); vtKey=""; voteRender(); }
  function fbFeed(t){ fb(t); clearTimeout(fbFeed.h); fbFeed.h=setTimeout(()=>{ if(FB.textContent===t) fb(""); }, 1800); }
  function coSubmit(){ if(G.ph!=="draw" || !RM || (G.ok&&G.ok[RM.code]!=null)) return; const i=decW(G.w,G.rd), w=W[i]?W[i][0]:"", v=norm(typed); if(!v) return;
    if(v===w){ myAns=w; kb(false); boxes(w); react("me","grin",1.6); confetti(26); fb("✅ 정답! 「"+w+"」 "+W[i][1]); try{ SFX.clear(); }catch(e){} toHost({t:"ok", i}); return; }
    typed=""; shake(); try{ SFX.bad(); }catch(e){} const nr=near(v,w); fb(nr?"🔥 거의 맞았어요! 철자를 다시 봐요":"❌ 아니에요 — 다시!"); RM.feed({t:nr?"nr":"x", s:RM.code}); boxes(); }
  /* 그리는 사람 → 방에 줄 올리기 */
  let upT=0;
  function coStroke(k, c){ if(!RM || G.ph!=="draw") return; const base="s/"+G.rd+"/";
    if(k==="end"){ c.sent=c.S.p.length; RM.put(base+c.k, enc(c.S)); } else if(k==="undo"){ RM.put(base+c.k, null); } else if(k==="clr"){ RM.put("s/"+G.rd, null); } }
  function liveUpload(dt){ if(!cur || !RM || G.ph!=="draw") return; upT+=dt; if(upT<.2) return; upT=0; if(cur.S.p.length!==cur.sent){ cur.sent=cur.S.p.length; RM.put("s/"+G.rd+"/"+cur.k, enc(cur.S)); } }
  function remoteStrokes(){ if(!RM || !RM.d || G.dr===RM.code || (G.ph!=="draw" && G.ph!=="show")) return; const s=(RM.d.s||{})[G.rd]||{}; const ks=Object.keys(s).filter(k=>typeof s[k]==="string").sort((a,b)=>(+a.slice(1))-(+b.slice(1)));
    const sig=ks.map(k=>k+":"+s[k].length).join(","); if(sig===strokeSig) return; strokeSig=sig; redraw(ks.map(k=>dec(s[k])).filter(Boolean)); }
  function coTick(dt){ if(!RM) return; try{ RM.tick(dt); }catch(e){} if(mode!=="co-play") return;
    const hc=hostCode(); hostMiss=(hc!==hostC)?hostMiss+dt:0; if(hc!==hostC && hostMiss>7){ hostC=hc; if(amHost() && RM.d && RM.d.g) G=Object.assign({}, RM.d.g); }
    if(amHost()){ if(G.ph && G.ph!=="end" && G.ph!=="wait"){ hostTick(dt); lowT+=dt; if(lowT>1.5){ lowT=0; RM.put("g", G); } } }
    else { const gg=RM.d && RM.d.g; if(gg && gg.sq!==lastSq && gg.ph){ lastSq=gg.sq; G=Object.assign({}, gg); render(); } }
    remoteStrokes(); liveUpload(dt);
    if(G.ph==="vote"){ const f=G.tot?Math.max(0,(G.dl-now())/G.tot):1, b=VT.querySelector(".tm i"); if(b) b.style.transform="scaleX("+f+")"; }
    if(G.ph==="draw"||G.ph==="pick"||G.ph==="show"){ const left=Math.max(0,(G.dl-now())/1000), frac=G.tot?Math.max(0,(G.dl-now())/G.tot):1; bar(G.rd+" / "+G.nr, "⭐ "+((G.sc&&G.sc[RM.code])|0), frac);
      if(G.ph==="draw" && left<=5 && left>0 && Math.ceil(left)!==coTick.lc){ coTick.lc=Math.ceil(left); try{ SFX.tick(); }catch(e){} } } }
  let ended=false;
  function coEnd(){ if(ended) return; ended=true; VT.classList.remove("on"); drawOK=false; kb(false); show(TL,0); show(KB,0); const me=RM.code, ord=(G.ro||[]).slice().sort((a,b)=>((G.sc[b]|0)-(G.sc[a]|0))), rank=ord.indexOf(me)+1;
    OV.innerHTML='<div class="big">🏆</div><div class="ko">'+esc(nmOf(ord[0]))+' 1등!</div>'; OV.classList.add("on");
    later(1.2, ()=>{ const got=PUI.award(api, {title:rank+"등", sub:"그림 맞히기 같이", rows:ord.map(c=>[nmOf(c), (G.sc[c]|0)+"점", c===me]), coins:[0,10,6,5][rank]||4, upd:(b,t)=>{ t.co=(t.co|0)+1; if(rank===1) t.win=(t.win|0)+1; }}), left=MG.payLeft("draw");
      PUI.result(U, {res:rank===1?"win":"draw", stars:rank===1?3:rank===2?2:1, title:rank===1?"1등!":rank+"등!", sub:"그림 맞히기 · 같이 "+ord.length+"명", av:api.av,
        rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"],["star", (G.sc[me]|0), "점"],["trophy", rank+"등", "순위"]],
        extra:((G.aw||[]).length?'<div class="dwAw">🏅 인기 작품상 '+G.aw.map(k=>(ART[k]?'<img alt="" src="'+ART[k]+'">':'')+'<b>'+esc(nmOf(G.drs[k]))+'</b>').join(" · ")+' ❤️ '+((G.vc||{})[G.aw[0]]|0)+'표</div>':'')+'<div class="puRank">'+ord.map((c,i)=>'<div class="'+(c===me?"me":"")+'"><span>'+(i<3?["🥇","🥈","🥉"][i]:(i+1)+".")+' '+esc(nmOf(c))+'</span><b>'+(G.sc[c]|0)+'점</b></div>').join("")+'</div>',
        prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3}, onAgain:()=>api.restart({}), onMenu:()=>api.restart({}), onOut:()=>MG.exit()});
      try{ RM.dispose(); }catch(e){} RM=null; }); }

  /* ══ 틀 ══ */
  function tick(dt){ if(gone || paused) return;
    for(let i=TM.length-1;i>=0;i--){ TM[i].t-=dt; if(TM[i].t<=0){ const f=TM[i].fn; TM.splice(i,1); try{ f(); }catch(e){ console.warn("DW", e); } } }
    if(mode==="solo" && S && !S.wait){ S.t+=dt; const step=fast?.05:TILE_T; while(S.t>=step*(S.pop+1) && S.pop<12) popTile(); bar((S.done+1)+" / "+S.n, "⭐ "+S.sc, 1-S.pop/12); }
    if(RM) coTick(dt); }
  function dispose(){ gone=true; TM.length=0; window.removeEventListener("keydown", onKey); try{ if(RM) RM.dispose(); }catch(e){} RM=null; try{ R.remove(); }catch(e){} }
  if(O.go==="solo") startSolo(); else menuShow();
  ready=true;
  return {scene, cam, tick, render:rn=>{ try{ porRender(rn); }catch(e){} }, dispose, pause:v=>{ paused=!!v; },
    get mode(){ return mode; }, get S(){ return S; }, get G(){ return G; }, get RM(){ return RM; }, get ready(){ return ready; }, get MY(){ return MY; }, W,
    set fast(v){ fast=v?1:0; }, get fast(){ return fast; }, menuGo, menuShow, key, typeWord:s=>{ String(s).split("").forEach(c=>key(c)); }, submit:()=>key("ok"), giveUp, hint:soloHint, demo,
    pick:k=>{ if(mode==="sketch") sketchPick(k); else if(mode==="co-play") toHost({t:"pk", k}); }, sketchDone, ans:()=>mode==="solo"&&S?W[S.cur][0]:(G.w?W[decW(G.w,G.rd)][0]:""), get typed(){ return typed; }, get sig(){ return strokeSig; }, get wl(){ return wordLen; }, get hints(){ return Object.assign({}, hintMap); }, get amHost(){ return amHost(); }, get fb(){ return FB.textContent; }, vote, get ART(){ return ART; } };
}

MG.reg("draw", {ic:"🎨", nm:"그림 맞히기", tag:"그림 보고 영어로 써서 맞히기 · 친구랑 그리고 맞히기", bg:"linear-gradient(135deg,#ff8466,#ffd23f 50%,#3ea2ff)", big:"🎨✏️", menu:true,
  how:[["🧩","그림이 보이면 <b>영어 단어를 직접 써서</b> 맞혀요"],["👫","친구가 그린 그림을 맞혀요"]], payTxt:"맞힌 만큼 🪙 3~10",
  bestTxt:(b,t)=>'🏆 최고 '+(b.best|0)+'점 · ✅ '+(t.ok|0)+'단어', ui:{look:false, btns:[]}, start});
})();
