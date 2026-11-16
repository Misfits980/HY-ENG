/* (v535) 🏝 우리 마을 새 화면 (HUD 1안 · 로블록스식) — 사용자: "1번 나쁘지 않네 · 도구를 점프를 감싸듯 대각선으로 · 채팅도"
   왼쪽 위 = 내 얼굴·이름·지금 있는 곳 · 오른쪽 위 = ☰ (빨간 숫자) + 💎🪱 · 왼쪽 = 오늘 할 일 카드(막대)
   왼쪽 아래 = 조이스틱 + 💬 말하기 · 오른쪽 아래 = 큰 점프 + 보라 「도구」 (가방·꾸미기·나·표정이 점프를 감싸며 펼침)
   할 수 있는 일 = 가까이 가면 초록 말풍선 + 바닥 빛 고리 · 멀리는 작은 흐린 아이콘 · 잡으면 보상 카드 · ☰ = 색 칸 6개 */
const IHUD=(()=>{
  if(!window.ISLE) return null;
  const inIsle=()=>place===PL.isle;
  const st=document.createElement("style"); st.textContent=`
#ih{display:none} body.isleOn #ih{display:block}
body.isleOn .bar.top .ttl, body.isleOn .bar.top .tools, body.isleOn #hud, body.isleOn .bar.bot, body.isleOn #bEmo{display:none!important}
#ih button{font-family:var(--kr);color:#3b2433;-webkit-tap-highlight-color:transparent}
#ihMe{position:fixed;left:calc(64px + env(safe-area-inset-left));top:calc(10px + env(safe-area-inset-top));z-index:4;display:flex;align-items:center;gap:7px;height:50px;padding:0 14px 0 4px;border-radius:999px;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;max-width:56vw}
#ihMe svg{width:40px;height:40px;flex:none}
#ihMe b{display:block;font-weight:400;font-size:16px;line-height:1.05;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left}
#ihMe small{display:block;font-size:11.5px;color:#8a6a4a;white-space:nowrap;text-align:left}
#ihMenu{position:fixed;right:calc(12px + env(safe-area-inset-right));top:calc(10px + env(safe-area-inset-top));z-index:4;width:50px;height:50px;border-radius:16px;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font-size:24px;line-height:1;padding:0}
#ihMenu u,#ihChat u{position:absolute;right:-6px;top:-6px;min-width:22px;height:22px;padding:0 5px;border-radius:999px;background:#ff4d5e;color:#fff;border:2.5px solid #fff;font:800 12px/17px var(--en);text-decoration:none;box-sizing:border-box}
#ihRes{position:fixed;right:calc(12px + env(safe-area-inset-right));top:calc(68px + env(safe-area-inset-top));z-index:4;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;max-width:min(230px,58vw)}
#ihRes span{display:flex;align-items:center;gap:4px;height:32px;padding:0 10px 0 6px;border-radius:999px;border:2.5px solid #3b2433;background:#fffdf7;box-shadow:0 2px 0 #3b2433;font:800 15px var(--en);color:#3b2433}
#ihCoinP{position:relative;cursor:pointer}#ihCoinP::after{content:"";position:absolute;inset:-7px -4px}   /* (v563 QA) 누르는 자리 넓게 (보이는 칸은 그대로) */
#ihRes img{width:20px;height:20px} #ihRes i{font-style:normal;font-size:17px}
#ihQ{position:fixed;left:calc(10px + env(safe-area-inset-left));top:calc(70px + env(safe-area-inset-top));z-index:3;width:148px;padding:6px 8px 7px;border-radius:16px;border:3px solid #3b2433;background:rgba(255,253,247,.94);box-shadow:0 3px 0 #3b2433;text-align:left}
#ihQ h4{margin:0 0 4px;font-weight:400;font-size:13px;display:flex;justify-content:space-between}#ihQ h4 em{font-style:normal;color:#4caf50}
#ihQ .r{display:flex;align-items:center;gap:5px;height:20px}#ihQ .r i{font-style:normal;font-size:14px;width:18px;text-align:center}
#ihQ .r s{flex:1;height:8px;border-radius:5px;background:#eadfcb;overflow:hidden;text-decoration:none;border:1.5px solid #3b2433}#ihQ .r s b{display:block;height:100%;background:#5cc46a}
#ihQ .r small{font:800 10.5px var(--en);min-width:22px;text-align:right}
#ihQ .r.ok s b{background:#ffd23f}#ihQ .r.got{opacity:.45}
#ihQ.hot{animation:ihHop 1s ease-in-out infinite}
@keyframes ihHop{50%{transform:translateY(-3px)}}
body.ihMin #ihQ{display:none}

body.isleOn #ijoy{bottom:calc(26px + env(safe-area-inset-bottom))} body.isleOn #ijump{bottom:calc(30px + env(safe-area-inset-bottom))}
body.isleOn #ipBan{top:calc(110px + env(safe-area-inset-top))} body.isleOn #emoBar{bottom:calc(150px + env(safe-area-inset-bottom));right:auto;left:50%;transform:translateX(-50%)}
#ihChat{position:fixed;left:calc(28px + env(safe-area-inset-left));bottom:calc(176px + env(safe-area-inset-bottom));z-index:3;width:56px;height:56px;border-radius:50%;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font-size:26px;line-height:1;padding:0}
#ihChat span{position:absolute;left:50%;bottom:-17px;transform:translateX(-50%);font-size:11.5px;color:#fff;text-shadow:0 1px 2px #3b2433,0 0 3px #3b2433;white-space:nowrap}
#ihTool{position:fixed;right:calc(124px + env(safe-area-inset-right));bottom:calc(30px + env(safe-area-inset-bottom));z-index:4;width:62px;height:62px;border-radius:50%;border:3px solid #3b2433;padding:0;
  background:linear-gradient(180deg,#c7a6ff,#8f63ef);box-shadow:inset 0 -5px 0 rgba(70,30,150,.35),inset 0 4px 0 rgba(255,255,255,.45),0 4px 0 #3b2433;color:#fff!important;display:flex;flex-direction:column;align-items:center;justify-content:center;transition:transform .2s}
#ihTool b{font-size:24px;line-height:1;transition:transform .25s}#ihTool span{font-size:12px;text-shadow:0 1px 0 rgba(60,20,120,.5)}
#ihTool.open{background:linear-gradient(180deg,#b89cff,#7a4fe0)}
#ihTool u{position:absolute;right:-4px;top:-4px;width:16px;height:16px;border-radius:50%;background:#ff4d5e;border:2.5px solid #fff}
.ihF{position:fixed;z-index:4;width:54px;height:54px;margin:-27px 0 0 -27px;border-radius:50%;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;padding:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
  opacity:0;transform:translate(0,0) scale(.3);pointer-events:none;transition:transform .28s cubic-bezier(.2,.9,.3,1.35),opacity .18s}
.ihF i{font-style:normal;font-size:24px;line-height:1}.ihF span{font-size:11px;line-height:1.1}
#ih.fan .ihF{opacity:1;pointer-events:auto}
#ihM{position:fixed;inset:0;z-index:20;display:none;background:rgba(30,18,40,.42);align-items:flex-start;justify-content:flex-end;padding:calc(66px + env(safe-area-inset-top)) calc(10px + env(safe-area-inset-right)) 0 0}
#ihM.on{display:flex}
/* (v561) 🗺 마을 지도 — QA: 섬에서 지도를 열면 예전 세계 지도(예전 마을로 감)가 나오던 것 */
#ihMap{position:fixed;inset:0;z-index:21;display:none;background:rgba(30,18,40,.45);align-items:center;justify-content:center;padding:16px}
#ihMap.on{display:flex}
#ihMap .mb{width:min(520px,94vw);background:#fff8ea;border:3px solid #3b2433;border-radius:24px;box-shadow:0 5px 0 #3b2433;padding:10px 10px 12px;animation:pop .3s cubic-bezier(.2,.9,.3,1.3)}
#ihMap .mh{display:flex;align-items:center;justify-content:space-between;font-weight:800;font-size:17px;padding:2px 4px 6px}
#ihMap .mh button{width:40px;height:40px;border-radius:50%;border:3px solid #3b2433;background:#fff;font-size:18px}
#ihMap svg{width:100%;height:auto;display:block;border-radius:16px;background:#8fd3f0}
#ihMap svg [data-z]{cursor:pointer}
#ihMap svg text{font:800 7.6px system-ui,sans-serif;fill:#3b2433;paint-order:stroke;stroke:#fff;stroke-width:2.4px;pointer-events:none} #ihMap svg text.hm{font-size:7.5px;fill:#8a5a00}
#ihMap .mt{font-size:13px;color:#6b5a4e;text-align:center;margin-top:6px}
#ihMap.v5{padding:max(8px,env(safe-area-inset-top)) max(6px,env(safe-area-inset-right)) max(8px,env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left))}
#ihMap.v5 .mb{width:min(680px,100%);max-height:100%;display:flex;flex-direction:column;padding:8px 6px 10px}
#ihMap.v5 svg{flex:1 1 auto;min-height:0;max-height:calc(100vh - 150px);width:100%;background:radial-gradient(ellipse at 50% 45%,#9fdcf4,#7cc8ea)}
#ihMap.v5 svg text.ic{font:9px system-ui,sans-serif;text-anchor:middle;stroke:none;fill:#000;paint-order:normal}
#ihMap.v5 svg text.nm{font:800 7px system-ui,sans-serif;text-anchor:middle;fill:#fff;stroke:none;paint-order:normal}
#ihMap.v5 svg text.lk{font:9px system-ui;text-anchor:middle;stroke:none}
#ihMap.v5 svg .pin:active circle{fill:#ffd23f}
#ihMap.v5 .mt{font-size:12.5px;line-height:1.45;padding:0 4px}
#ihM .bx{width:min(300px,86vw);background:#fff8ea;border:3px solid #3b2433;border-radius:24px;box-shadow:0 5px 0 #3b2433;padding:12px;display:grid;grid-template-columns:repeat(3,1fr);gap:9px;animation:pop .3s cubic-bezier(.2,.9,.3,1.3)}
#ihM .bx button{position:relative;height:84px;border-radius:18px;border:3px solid #3b2433;box-shadow:inset 0 -5px 0 rgba(0,0,0,.12),0 3px 0 #3b2433;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:14px;padding:0}
#ihM .bx button i{font-style:normal;font-size:30px;line-height:1}
#ihM .bx button u{position:absolute;right:-6px;top:-6px;min-width:22px;height:22px;padding:0 5px;border-radius:999px;background:#ff4d5e;color:#fff;border:2.5px solid #fff;font:800 12px/17px var(--en);text-decoration:none}
/* (v696) 📱 화면 정리 — claude/hy-eng-plan-town-study.md 4번 (시안 ①②): 시각·날씨 알약 · 돈 알약 하나 · 접힌 「📋 오늘」 · ☰+🧰 → 📱 HY폰 · 상황 단추 */
#ihMe b{font:800 16px var(--en)} #ihMe b em{font-style:normal;font-size:15px;margin-left:3px}
#ihMenu{background:linear-gradient(180deg,#c7a6ff,#8f63ef);box-shadow:inset 0 -4px 0 rgba(70,30,150,.35),inset 0 3px 0 rgba(255,255,255,.45),0 3px 0 #3b2433;font-size:25px}
#ihRes{gap:0;flex-wrap:nowrap;max-width:none;align-items:center;height:38px;padding:0 3px;border:2.5px solid #3b2433;border-radius:999px;background:#fffdf7;box-shadow:0 2px 0 #3b2433}
#ihRes>span{height:32px;padding:0 7px 0 5px;border:0;box-shadow:none;background:none;border-radius:0}
#ihRes>span+span{border-left:2px solid #eadfcb}
#ihQ{width:auto;height:38px;padding:0 12px 0 9px;border-radius:999px;display:flex;align-items:center;gap:5px;font-size:14px;white-space:nowrap}
#ihQ>i{font-style:normal;font-size:17px} #ihQ>em{font:800 14px var(--en);font-style:normal;color:#4caf50} #ihQ>s{text-decoration:none;color:#8a6a4a;font-size:12px}
#ihQ.all{background:#e9f8e4}
#ihAct{position:fixed;right:calc(124px + env(safe-area-inset-right));bottom:calc(30px + env(safe-area-inset-bottom));z-index:4;width:78px;height:78px;border-radius:50%;border:3px solid #3b2433;padding:0;
  background:linear-gradient(180deg,#8fe07f,#3fa64a);box-shadow:inset 0 -5px 0 rgba(20,80,30,.3),inset 0 4px 0 rgba(255,255,255,.45),0 4px 0 #3b2433;color:#fff!important;display:none;flex-direction:column;align-items:center;justify-content:center;gap:1px}
#ihAct.on{display:flex;animation:pop .25s cubic-bezier(.2,.9,.3,1.3)}
#ihAct i{font-style:normal;font-size:29px;line-height:1} #ihAct span{font-size:12.5px;line-height:1.1;max-width:72px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 1px 0 rgba(0,60,10,.55)}
#ihM{align-items:center;justify-content:center;padding:14px}
#ihM .ph{position:relative;width:min(360px,92vw);max-height:calc(100% - 8px);overflow-y:auto;border-radius:34px;border:4px solid #3b2433;background:#fffaf0;box-shadow:0 6px 0 #3b2433;padding:12px 14px 16px;animation:pop .28s cubic-bezier(.2,.9,.3,1.3)}
#ihM .pt{display:flex;justify-content:space-between;align-items:center;font:800 14px var(--en);color:#3b2433;padding:0 6px 8px}
#ihM .pt b{font-weight:800} #ihM .pt small{font-size:12.5px;color:#8a6a4a}
#ihM .nw{display:flex;gap:9px;align-items:center;width:100%;padding:9px 12px;margin:0 0 12px;border-radius:18px;border:2.5px solid #3b2433;background:#fff4d6;text-align:left;font:inherit;color:#3b2433}
#ihM .nw>i{font-style:normal;font-size:24px} #ihM .nw span{flex:1;min-width:0} #ihM .nw b{display:block;font:800 14.5px/1.25 var(--en)} #ihM .nw small{display:block;font-size:12px;color:#8a6a4a}
#ihM .ph .bx{width:auto;background:none;border:0;box-shadow:none;padding:0;animation:none;gap:10px 8px}
#ihM .ph .bx button{height:auto;aspect-ratio:auto;padding:10px 2px 8px;font-size:12.5px;gap:4px}
#ihM .ph .bx button i{font-size:30px}
#ihM .pc{display:block;margin:14px auto 0;width:52px;height:52px;border-radius:50%;border:3px solid #3b2433;background:#fff;font-size:20px;box-shadow:0 3px 0 #3b2433}
@media (max-height:520px){ #ihM .ph{width:min(640px,94vw);padding:10px 12px 12px} #ihM .ph .bx{grid-template-columns:repeat(6,1fr);gap:8px 6px} #ihM .ph .bx button{padding:6px 2px 5px;font-size:11.5px} #ihM .ph .bx button i{font-size:24px} #ihM .nw{margin-bottom:8px;padding:6px 10px} #ihM .pt{padding-bottom:4px} #ihM .pc{margin-top:8px;width:44px;height:44px} }
/* 패드: 단추·글자 1.35배 (시안 2 ①) */
@media (min-width:700px) and (min-height:700px){
  #ihMe{transform:scale(1.32);transform-origin:left top}
  #ihMenu{transform:scale(1.32);transform-origin:right top}
  #ihRes{transform:scale(1.32);transform-origin:right top;top:calc(86px + env(safe-area-inset-top))}
  #ihQ{transform:scale(1.32);transform-origin:left top;top:calc(86px + env(safe-area-inset-top))}
  #ihChat{transform:scale(1.25);transform-origin:left bottom}
  #ihAct{transform:scale(1.3);transform-origin:right bottom;right:calc(150px + env(safe-area-inset-right))}
  body.isleOn #tls .tl{font-size:18px} #ihM .ph{width:min(470px,86vw);padding:16px 20px 20px} #ihM .ph .bx button i{font-size:40px} #ihM .ph .bx button{font-size:15px} #ihM .nw b{font-size:17px} #ihM .nw small{font-size:14px} #ihM .pt{font-size:16px}
}
/* 할 수 있는 일 = 초록 말풍선 · 멀리 = 작은 흐린 아이콘 */
body.isleOn .tl{border:3px solid #3b2433;box-shadow:0 3px 0 #3b2433;font-size:14.5px}
body.isleOn .tl:not(.far){background:linear-gradient(180deg,#8fe07f,#4caf50);color:#fff;text-shadow:0 1px 0 rgba(20,70,20,.5);padding:4px 13px 4px 4px}
body.isleOn .tl:not(.far) i{background:#fffdf7;border-radius:50%}
body.isleOn .tl:not(.far)::after{content:"";position:absolute;left:50%;bottom:-9px;width:12px;height:12px;background:#4caf50;border-right:3px solid #3b2433;border-bottom:3px solid #3b2433;transform:translateX(-50%) rotate(45deg)}
body.isleOn .tl.far{opacity:.78;scale:.78;pointer-events:auto;font-size:0;gap:0;padding:3px;background:rgba(255,253,247,.9)}
body.isleOn .tl.far i{font-size:17px}
body.isleOn .tl.far::after{display:none}
/* (v687) 화면 밖 안내(.edge): 위 꼬리 규칙이 「➜」 화살표 규칙을 이겨서 화살표 대신 초록 꼬리가 이름표 글자(「같이 낚시」의 「같」) 위에 그려졌음 → 이름표 바깥에 동그란 화살표 · 👇 손가락은 숨김 (가리킬 곳이 화면 밖) */
body.isleOn .tl.edge:not(.far)::after{content:"➜";left:50%;top:50%;bottom:auto;width:26px;height:26px;margin:-16px 0 0 -16px;display:grid;place-items:center;background:#fffdf7;border:3px solid #3b2433;border-radius:50%;color:#2f8a2a;font-size:19px;font-weight:900;line-height:1;text-shadow:none;box-shadow:0 2px 0 #3b2433;transform:rotate(var(--ea)) translateX(var(--er,46px));pointer-events:none}
body.isleOn .tl.edge::before{display:none}
body.isleOn .tl.far.sg:not(.hot),body.isleOn .tl.far.dc:not(.hot),body.isleOn .tl.hudx{display:none}
/* 잡았다! 보상 카드 */
body.isleOn #quiz .box{border:3px solid #3b2433;box-shadow:0 6px 0 #3b2433;border-radius:26px;padding-top:30px}
body.isleOn #quiz .box::before{content:"🎉 잡았다!";top:-22px;padding:7px 22px;border:3px solid #3b2433;border-radius:16px;background:linear-gradient(180deg,#ff8a8a,#ff5d6c);font:400 19px var(--kr);box-shadow:0 3px 0 #3b2433;transform:translateX(-50%) rotate(-2deg)}
body.isleOn #quiz.rec .box::before{content:"🏆 최고 기록!";background:linear-gradient(180deg,#ffe58f,#ffbf33);color:#5a3000}
body.isleOn #quiz .fishBig{width:128px;height:128px;margin:2px auto 4px;border-radius:50%;background:radial-gradient(circle at 50% 40%,#e3f6ff,#bfe6ff);border:3px solid #3b2433;display:flex;align-items:center;justify-content:center;font-size:76px}
body.isleOn #quiz .opts .btn{border:3px solid #3b2433;box-shadow:0 3px 0 #3b2433}
body.isleOn #quiz #qOk{background:linear-gradient(180deg,#8fe07f,#4caf50);color:#fff}
@media (max-height:520px){ #ihQ{top:auto;bottom:calc(170px + env(safe-area-inset-bottom));transform:scale(.86);transform-origin:left bottom} #ihChat{left:calc(166px + env(safe-area-inset-left));bottom:calc(30px + env(safe-area-inset-bottom))} body.isleOn #ipBan{top:calc(66px + env(safe-area-inset-top))} }
@media (max-height:430px){ #ihQ{display:none} }
`; document.head.appendChild(st);
  const d=document.createElement("div"); d.id="ih";
  d.innerHTML='<button id="ihMe" aria-label="나"></button><button id="ihMenu" aria-label="HY폰">📱<u hidden></u></button><div id="ihRes"><span><img src="../assets/ui/ic-gem.webp" alt=""><b id="ihGem">0</b></span><span id="ihCoinP" role="button" aria-label="코인 · 마을 은행"><i>🪙</i><b id="ihCoin">0</b></span><span><i>🪱</i><b id="ihBait">0</b></span></div>'
    +'<button id="ihQ" aria-label="오늘 할 일"></button><button id="ihChat" aria-label="말하기">💬<span>말하기</span></button>'
    +'<button id="ihAct" aria-label="지금 할 수 있는 것"><i></i><span></span></button>';   /* (v696) 🧰 도구 펼침 → 📱 HY폰 안으로 · 그 자리 = 상황 단추 */
  document.body.appendChild(d);
  const m=document.createElement("div"); m.id="ihM";
  /* (v696) 📱 HY폰 — ☰ 메뉴 · 🧰 도구(가방·꾸미기·나·표정) · 이웃 · 단어 손님을 한 화면에 (시안 ②) · 맨 위 오늘 소식 한 줄 (창이 뜨지 않음) */
  const TILES=[["map","🗺️","지도","#c4e6ff"],["q","📋","할 일","#fff0a8"],["dex","🐟","도감","#c9f0c0"],["bag","🎒","가방","#ffd9a8"],["me","👕","나 꾸미기","#ffe0ec"],["nb","🐻","이웃","#e9d6ff"],
    ["guest","🐾","단어 손님","#ffe7c2"],["fr","👫","친구","#ffc4d6"],["home","🏠","내 집","#fde6b0"],["deco","🎨","집 꾸미기","#d8f3ec"],["lot","🏡","우리 땅","#e0d0ff"],["emo","😊","표정","#fff3b0"]];
  m.innerHTML='<div class="ph"><div class="pt"><b id="ihPT"></b><small id="ihPD"></small></div><button class="nw" id="ihNw" data-m="news"></button><div class="bx">'+TILES.map(([k,i,t,c])=>'<button data-m="'+k+'" style="background:'+c+'"><i>'+i+'</i>'+t+'<u hidden></u></button>').join("")+'</div><button class="pc" data-m="x" aria-label="닫기">✕</button></div>'; document.body.appendChild(m);
  const stop=e=>e.stopPropagation(); [d,m].forEach(el=>["pointerdown","pointerup","click","wheel"].forEach(ev=>el.addEventListener(ev, e=>{ if(e.target!==el || el===m) stop(e); })));
  try{ SHEETS.push("ihM"); }catch(e){}
  const click=id=>{ const b=$(id); if(b) b.click(); };
  /* ── 얼굴 ── */
  function face(){ const A=AV_OPT, sk=A.skin[av.skin]||A.skin[0], hc=A.hc[av.hc]||A.hc[0], tp=A.top[av.top]||A.top[0];
    return '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="19" fill="#bfe6ff" stroke="#3b2433" stroke-width="2.5"/><path d="M6 38c2-7 8-10 14-10s12 3 14 10" fill="'+tp+'" stroke="#3b2433" stroke-width="2"/>'
      +'<circle cx="20" cy="19" r="10.5" fill="'+sk+'" stroke="#3b2433" stroke-width="2"/><path d="M9.6 18.5c0-7 4.6-10 10.4-10s10.4 3 10.4 10c-3-3.6-7-4.6-10.4-4.6S12.6 15 9.6 18.5z" fill="'+hc+'" stroke="#3b2433" stroke-width="1.6"/>'
      +'<circle cx="16.2" cy="20.5" r="1.6" fill="#3b2433"/><circle cx="23.8" cy="20.5" r="1.6" fill="#3b2433"/><path d="M17 24.4q3 2.6 6 0" fill="none" stroke="#3b2433" stroke-width="1.6" stroke-linecap="round"/><circle cx="13.6" cy="23.6" r="1.6" fill="#ff9ab0" opacity=".7"/><circle cx="26.4" cy="23.6" r="1.6" fill="#ff9ab0" opacity=".7"/></svg>'; }
  function where(){ const h=hero && hero.g.position; if(!h) return "🏝 우리 마을"; const x=h.x-ISLE.OX, z=h.z-ISLE.OZ;   /* (v536) 이름 있는 길 */
    if(x*x+z*z<64) return "⛲ 광장"; let best=null, bd=36; (ISLE.lots||[]).forEach(L=>{ const d=(L.x-x)**2+(L.z-z)**2; if(d<bd){ bd=d; best=L; } });
    if(best){ const hi=(window.ISLE_MAP && ISLE_MAP.hoods.find(q=>q.id===best.hood)); if(hi) return hi.ic+" "+hi.nm; }
    const S=window.ISLE_MAP && ISLE_MAP.spots; if(S){ const near=(p,r)=>(p[0]-x)**2+(p[1]-z)**2<r*r; if(near(S.farm,8)) return "🌾 농장"; if(near([S.park.x,S.park.z],S.park.r+1)) return "🎡 놀이 공원"; if(near([S.lake.x,S.lake.z],10)) return "🎣 호수"; if(near(S.tower,7)) return "🗼 타워"; if(near(S.mine,8)) return "⛏ 광산"; }
    try{ const Z=ISLE_MAP.zoneAt(x,z); if(Z && !Z.free) return Z.nm; }catch(_){}   /* (v561) QA: 곳마다 이름이 달랐음(시장 거리/상점가 · 학교/배움 언덕 · 풍차 밭/농장·캠핑) → 구역 이름판과 같게 */
    return "🏝 우리 마을"; }
  let meKey="";
  /* (v696) 왼쪽 위 = 얼굴 + 지금 시각·날씨 (이름 대신 · 이름은 나 꾸미기·친구에서) */
  function clock(){ let t; try{ t=new Date(srvNow()); }catch(e){ t=new Date(); } const h=t.getHours(), m=t.getMinutes(); return {t:(h<12?"오전 ":"오후 ")+((h%12)||12)+":"+String(m).padStart(2,"0"), d:(t.getMonth()+1)+"월 "+t.getDate()+"일 ("+"일월화수목금토"[t.getDay()]+")", h}; }
  function wx(){ let r=false, k="d"; try{ r=rainy(); }catch(e){} try{ k=tod(); }catch(e){} return r?"🌧":k==="n"?"🌙":k==="e"?"🌇":"☀️"; }
  function drawMe(){ const w=where(), c=clock(), k=c.t+"|"+w+"|"+wx()+"|"+JSON.stringify(av);
    if(k===meKey) return; meKey=k; $("ihMe").innerHTML=face()+'<div><b>'+c.t+'<em>'+wx()+'</em></b><small>'+w+'</small></div>'; }
  /* ── 할 일 카드 ── */
  let qKey="";
  function drawQ(){ let L=[]; try{ L=qList().filter(q=>q.sec==="d"); }catch(e){} const done=L.filter(q=>q.got||q.c>=q.n).length, ok=L.some(q=>!q.got && q.c>=q.n);
    const k=L.map(q=>q.k+q.c+q.got).join("|"); if(k===qKey) return; qKey=k;
    $("ihQ").innerHTML='<i>📋</i>오늘 <em>'+done+'/'+L.length+'</em><s>'+(ok?'받기!':'▸')+'</s>';   /* (v696) 접힌 칩 — 누르면 할 일 창 */
    $("ihQ").classList.toggle("hot", ok); $("ihQ").classList.toggle("all", !!L.length && done>=L.length); }
  /* ── 숫자 (💎 🪱 · ☰ 빨간 숫자) ── */
  function nbBang(){ try{ return VIL.nbList().filter(x=>x.bang).length; }catch(e){ return 0; } }
  function gNew(){ try{ const s=GUEST.st(); return GUEST.A().filter(G=>G.kind0==="r" && !s.seen[G.w]).length; }catch(e){ return 0; } }
  function badge(){ let n=0, fr=0; try{ n=qList().filter(q=>!q.got && q.c>=q.n).length; }catch(e){} try{ fr=Object.keys(SOC.req||{}).length; }catch(e){} const nb=nbBang(), gn=gNew();
    const set=(el,v)=>{ el.hidden=!v; el.textContent=v; }; set($("ihMenu").querySelector("u"), n+fr+nb+gn);
    set(m.querySelector('[data-m="q"] u'), n); set(m.querySelector('[data-m="fr"] u'), fr); set(m.querySelector('[data-m="nb"] u'), nb); set(m.querySelector('[data-m="guest"] u'), gn);
    $("ihGem").textContent=gems; $("ihBait").textContent=bait; try{ $("ihCoin").textContent=TECO.coins().toLocaleString("ko-KR"); }catch(_){} }
  /* (v696) 🧰 도구 펼침은 📱 HY폰 안으로 — fan() 은 예전 부르는 곳을 위해 빈 함수 */
  function fan(){}
  $("ihChat").onclick=e=>{ e.stopPropagation(); fan(false); try{ vcOpen(); }catch(_){ click("bIChat"); } };
  $("ihCoinP").onclick=e=>{ e.stopPropagation(); try{ TECO.openBank(); }catch(_){} };
  function news(){ const c=clock(); let n=null;
    try{ if(DAYR.night()) n=DAYR.news(); }catch(e){}
    try{ const L=VIL.nbList().filter(x=>x.bang); if(L.length) n=["🐻", L[0].nm+(L.length>1?" and friends need":" needs")+" your help!", "이웃 "+L.map(x=>x.nm).join("·")+" 에게 오늘 ❗ 부탁이 있어요", "nb"]; }catch(e){}
    if(!n){ try{ const s=GUEST.st(), G=GUEST.A().find(G=>G.kind0==="r" && !s.seen[G.w]) || GUEST.A().find(G=>G.kind0==="v"); if(G) n=G.kind0==="r" ? ["🏡", "A "+G.w+" moved to our town!", "「"+G.w+"」 가 마을로 이사 왔어요 · 광장에 있어요", "guest"] : ["✨", "A "+G.w+" is visiting today!", "오늘 배운 「"+G.w+"」 가 광장에 놀러 왔어요", "guest"]; }catch(e){} }
    if(!n){ let q=0; try{ q=qList().filter(x=>!x.got && x.c>=x.n).length; }catch(e){} if(q) n=["📋", "You can get a reward!", "할 일 보상 "+q+"개를 받을 수 있어요", "q"]; }
    if(!n){ try{ n=DAYR.news(); }catch(e){} }
    if(!n) n=c.h<12 ? ["🌅","Good morning!","좋은 아침! 오늘도 즐거운 하루", ""] : c.h<18 ? ["🌤","Good afternoon!","오늘도 마을은 평화로워요", ""] : ["🌙","Good evening!","오늘 하루도 수고했어요", ""];
    return n; }
  function phone(){ const c=clock(), n=news(); $("ihPT").textContent=c.t+" "+wx(); $("ihPD").textContent=c.d; const nw=$("ihNw"); nw.dataset.go=n[3]; nw.innerHTML='<i>'+n[0]+'</i><span><b>'+esc(n[1])+'</b><small>'+esc(n[2])+'</small></span>'; badge(); m.classList.add("on"); }
  $("ihMenu").onclick=e=>{ e.stopPropagation(); phone(); try{ SND.pop && SND.pop(); }catch(_){} };
  $("ihQ").onclick=e=>{ e.stopPropagation(); try{ openQ(); }catch(_){} };
  $("ihMe").onclick=e=>{ e.stopPropagation(); click("bIAv"); };
  m.addEventListener("click", e=>{ const b=e.target.closest("[data-m]"); if(!b && e.target!==m) return; m.classList.remove("on"); if(!b) return; let k=b.dataset.m; if(k==="news") k=b.dataset.go||"";
    if(k==="home") click("bIHome"); else if(k==="fr") click("bFr"); else if(k==="map") openMap(); else if(k==="dex") click("bDex"); else if(k==="q") openQ(); else if(k==="lot") ISLE.openLots();
    else if(k==="bag") click("bIBag"); else if(k==="me") click("bIAv"); else if(k==="deco") ISLE.openHouse(); else if(k==="emo"){ const eb=$("emoBar"); if(eb) eb.classList.toggle("on"); }
    else if(k==="nb"){ try{ VIL.openList(); }catch(_){} } else if(k==="guest"){ try{ GUEST.openBook(); }catch(_){} } });
  /* (v561) 🗺 마을 지도 — 구역을 누르면 그 입구까지 걸어감 · ⭐ 내 집 · 🔴 나 */
  function openMap(){ const M=window.ISLE_MAP; if(!M || !M.zones){ click("bMap"); return; }
    let el=$("ihMap"); if(!el){ el=document.createElement("div"); el.id="ihMap"; document.body.appendChild(el);
      el.addEventListener("click", e=>{ const z=e.target.closest("[data-z]"); if(z){ el.classList.remove("on"); goZone(z.dataset.z); return; } if(e.target===el || e.target.closest(".mx")) el.classList.remove("on"); }); }
    if(M.v5){ mapV5(M, el); return; }
    const I=M.island, f=n=>Math.round(n*10)/10; let x0=I.cx-I.ax-5, z0=I.cz-I.az-5, w=I.ax*2+10, h=I.az*2+10;
    if(M.isles){ let a0=-75,b0=-68,a1=73,b1=62; M.isles.forEach(q=>{ a0=Math.min(a0,q.cx-q.R); b0=Math.min(b0,q.cz-q.R); a1=Math.max(a1,q.cx+q.R); b1=Math.max(b1,q.cz+q.R); }); x0=a0-6; z0=b0-6; w=a1-a0+12; h=b1-b0+12; }   /* (v607~) 새 섬 5판 = 둘레 섬까지 */   /* (v568) ax·az 는 반지름 — 예전엔 지름으로 써서 섬 절반만 보이고 이름이 겹침 */
    const cen=P=>{ let x=0,z=0; P.forEach(q=>{ x+=q[0]; z+=q[1]; }); return [x/P.length, z/P.length]; };
    const hex=c=>"#"+("00000"+(c>>>0).toString(16)).slice(-6);
    let g; try{ const pts=[]; for(let k=0;k<72;k++){ const a=k/72*Math.PI*2, r=M.edge(a); pts.push(f(I.cx+Math.cos(a)*r)+","+f(I.cz+Math.sin(a)*r)); } g='<polygon points="'+pts.join(" ")+'" fill="#9ed67a" stroke="#f1e2a8" stroke-width="3"/>'; }
      catch(_){ g='<ellipse cx="'+f(I.cx)+'" cy="'+f(I.cz)+'" rx="'+f(I.ax)+'" ry="'+f(I.az)+'" fill="#9ed67a" stroke="#f1e2a8" stroke-width="3"/>'; }
    if(M.isles){ M.isles.forEach(q=>{ const pts=[]; for(let k=0;k<48;k++){ const a=k/48*Math.PI*2, r=q.R*(1+.035*Math.sin(3*a+q.s)+.025*Math.sin(5*a+q.s*2)); pts.push(f(q.cx+Math.cos(a)*r)+","+f(q.cz+Math.sin(a)*r)); } g+='<polygon points="'+pts.join(" ")+'" fill="'+(q.lock?"#c9d6c0":"#9ed67a")+'" stroke="#f1e2a8" stroke-width="3"/>'; if(q.lake){ const L=M.spots.lake; g+='<ellipse cx="'+f(L.x)+'" cy="'+f(L.z)+'" rx="'+f(L.rx)+'" ry="'+f(L.rz)+'" fill="#58c2e6"/>'; } });
      (M.links||[]).forEach(b=>{ g+='<line x1="'+b[0]+'" y1="'+b[1]+'" x2="'+b[2]+'" y2="'+b[3]+'" stroke="#a8743c" stroke-width="'+f((b[4]||1.5)*.9)+'"/>'; });
      Object.values(M.roads).forEach(r=>{ if(!r.asph) return; g+='<polyline points="'+r.p.map(q=>f(q[0])+","+f(q[1])).join(" ")+'" fill="none" stroke="#7a808c" stroke-width="'+f(r.w*.8)+'" stroke-linecap="round" stroke-linejoin="round"/>'; }); }
    M.zones.forEach(Z=>{ if(Z.free) return; const c=cen(Z.poly); g+='<g data-z="'+Z.k+'"><polygon points="'+Z.poly.map(q=>f(q[0])+","+f(q[1])).join(" ")+'" fill="'+hex(Z.c||0xcccccc)+'" fill-opacity=".75" stroke="#3b2433" stroke-width=".9"/></g><text x="'+f(c[0])+'" y="'+f(c[1])+'" text-anchor="middle">'+Z.nm+'</text>'; });
    try{ const fd=ISLE.myFd && ISLE.myFd(), f2=fd!=null && ISLE.SLOTS().find(x=>x.id===fd); if(f2) g+='<g data-z="myfield"><rect x="'+f(f2.c[0]-ISLE.OX-3)+'" y="'+f(f2.c[1]-ISLE.OZ-2.5)+'" width="6" height="5" rx="1.2" fill="#8bd16a" stroke="#3b2433" stroke-width="1"/></g><text class="hm" x="'+f(f2.c[0]-ISLE.OX)+'" y="'+f(f2.c[1]+9-ISLE.OZ)+'" text-anchor="middle">🌱 내 밭</text>'; }catch(_){}
    try{ const d=ISLE.doorCell(); if(d && tut.s>=1) g+='<g data-z="myhome"><circle cx="'+f(d[0]+.5-ISLE.OX)+'" cy="'+f(d[1]+.5-ISLE.OZ)+'" r="4.4" fill="#ffd23f" stroke="#3b2433" stroke-width="1"/></g><text class="hm" x="'+f(d[0]+.5-ISLE.OX)+'" y="'+f(d[1]+11-ISLE.OZ)+'" text-anchor="middle">⭐ 내 집</text>'; }catch(_){}
    try{ const s=ISLE.SPOT.mine; if(s) g+='<g data-z="mine"><circle cx="'+f(s[0]-ISLE.OX)+'" cy="'+f(s[2]-ISLE.OZ)+'" r="4.4" fill="#b8a2e0" stroke="#3b2433" stroke-width="1"/></g><text class="hm" x="'+f(s[0]-ISLE.OX)+'" y="'+f(s[2]+11-ISLE.OZ)+'" text-anchor="middle">⛏ 광산</text>'; }catch(_){}   /* (v580) ⛏ 광산 = 바로 가기 되는 곳 */
    try{ const p=hero.g.position; g+='<circle cx="'+f(p.x-ISLE.OX)+'" cy="'+f(p.z-ISLE.OZ)+'" r="3.4" fill="#ff4d5e" stroke="#fff" stroke-width="1.2"><animate attributeName="r" values="3.4;4.6;3.4" dur="1.2s" repeatCount="indefinite"/></circle>'; }catch(_){}
    el.innerHTML='<div class="mb"><div class="mh"><span>🗺 우리 마을 지도</span><button class="mx" aria-label="닫기">✕</button></div><svg viewBox="'+f(x0)+' '+f(z0)+' '+f(w)+' '+f(h)+'">'+g+'</svg><div class="mt">🔴 = 나 · 누르면 걸어가요 · ⭐ 집·⛏ 광산은 🚀 바로 · 먼 곳은 🚉 기차</div></div>';
    el.classList.add("on"); }
  /* (v618) 🗺 새 섬 지도 — 사용자: 「지도 너무 불편해」(구역 네모가 겹치고 · 이름이 작고 · 아래 글이 잘림)
     → 섬 모양 + 큰길·다리·시내 블록·텃밭만 그리고, 갈 곳 = 큰 동그라미 핀(그림 + 이름표) 11곳 · 🔴 나 · ⭐ 내 집 · 🌱 내 밭 · 화면 크게 */
  function mapV5(M, el){ const f=n=>Math.round(n*10)/10, OX=ISLE.OX, OZ=ISLE.OZ;
    let a0=1e9,b0=1e9,a1=-1e9,b1=-1e9; M.isles.forEach(q=>{ a0=Math.min(a0,q.cx-q.R); b0=Math.min(b0,q.cz-q.R); a1=Math.max(a1,q.cx+q.R); b1=Math.max(b1,q.cz+q.R); }); a0=Math.min(a0,-80); a1=Math.max(a1,78); b0=Math.min(b0,-72); b1=Math.max(b1,66);
    const x0=a0-3, z0=b0-5, w=a1-a0+6, h=b1-b0+14;
    const isl=(pts,c)=>'<polygon points="'+pts.join(" ")+'" fill="'+c+'" stroke="#f3e2a6" stroke-width="3.2" stroke-linejoin="round"/>';
    let g='';
    { const pts=[]; for(let k=0;k<96;k++){ const a=k/96*Math.PI*2, r=M.edge(a); pts.push(f(M.island.cx+Math.cos(a)*r)+","+f(M.island.cz+Math.sin(a)*r)); } g+=isl(pts,"#a6db7f"); }
    M.isles.forEach(q=>{ const pts=[]; for(let k=0;k<48;k++){ const a=k/48*Math.PI*2, r=q.R*(1+.035*Math.sin(3*a+q.s)+.025*Math.sin(5*a+q.s*2)); pts.push(f(q.cx+Math.cos(a)*r)+","+f(q.cz+Math.sin(a)*r)); } g+=isl(pts, q.lock?"#cfd8c6":"#a6db7f"); if(q.lock) g+='<text class="lk" x="'+f(q.cx)+'" y="'+f(q.cz+3)+'">🔒</text>'; });
    { const L=M.spots.lake; g+='<ellipse cx="'+f(L.x)+'" cy="'+f(L.z)+'" rx="'+f(L.rx)+'" ry="'+f(L.rz)+'" fill="#6cc8ea"/>'; }
    (M.links||[]).forEach(b=>{ g+='<line x1="'+b[0]+'" y1="'+b[1]+'" x2="'+b[2]+'" y2="'+b[3]+'" stroke="#b07a40" stroke-width="'+f((b[4]||1.5)*1.1)+'" stroke-linecap="round"/>'; });
    if(M.city) M.city.blocks.forEach(B=>{ g+='<rect x="'+f(B.x0)+'" y="'+f(B.z0)+'" width="'+f(B.x1-B.x0)+'" height="'+f(B.z1-B.z0)+'" rx="1.5" fill="#e9e1f2" stroke="#c9bfd8" stroke-width=".6"/>'; });
    if(M.fields) M.fields.slots.forEach(F=>{ g+='<rect x="'+f(F.x-2.8)+'" y="'+f(F.z-2.3)+'" width="5.6" height="4.6" rx=".8" fill="#c8a066" opacity=".75"/>'; });
    Object.values(M.roads).forEach(r=>{ g+='<polyline points="'+r.p.map(q=>f(q[0])+","+f(q[1])).join(" ")+'" fill="none" stroke="'+(r.asph?"#8a8f9a":"#e8d3a0")+'" stroke-width="'+f(r.asph?r.w*.85:r.w*.7)+'" stroke-linecap="round" stroke-linejoin="round"/>'; });
    M.hoods.forEach(H=>{ g+='<polyline points="'+H.p.map(q=>f(q[0])+","+f(q[1])).join(" ")+'" fill="none" stroke="#e8d3a0" stroke-width="1.3" stroke-linecap="round"/>'; });
    g+='<circle cx="0" cy="0" r="'+f(M.plaza.r)+'" fill="#f3e6c4" stroke="#e0c98e" stroke-width=".8"/>';
    /* 갈 곳 핀 */
    const S=M.spots, P=[["center","🏙","도심",14,-30],["campus","🎓","배움 언덕",-34,-40],["home","🏘","1~3동",-46,18],["home2","🏘","4~6동",46,18],["farm","🌾","텃밭 섬",-108,16],["vil","🍄","버섯 마을",S.vil[0],S.vil[1]],["adv","⛏","광산 섬",0,-94],["lake","🎣","호수 섬",S.lake.x,S.lake.z],["park","🎡","놀이 섬",S.park.x,S.park.z],["beach","🏖","등대 섬",0,74]];
    const K=Math.max(1, Math.min(1.6, 560/Math.max(320, Math.min(innerWidth, 680))));   /* 휴대폰 = 핀·글자 크게 */
    const pin=(k,ic,t,x,z,col,small)=>{ const r=(small?5.4:6.6)*K, tw=(t.length*5.6+7)*K, th=9*K; return '<g data-z="'+k+'" class="pin"><circle cx="'+f(x)+'" cy="'+f(z)+'" r="'+f(r+4)+'" fill="transparent"/><circle cx="'+f(x)+'" cy="'+f(z)+'" r="'+f(r)+'" fill="'+(col||"#fffdf7")+'" stroke="#3b2433" stroke-width="'+f(1.4*K)+'"/><text class="ic" style="font-size:'+f(9*K)+'px" x="'+f(x)+'" y="'+f(z+2.8*K)+'">'+ic+'</text>'
      +'<rect x="'+f(x-tw/2)+'" y="'+f(z+r+1.2)+'" width="'+f(tw)+'" height="'+f(th)+'" rx="'+f(th/2)+'" fill="#3b2433"/><text class="nm" style="font-size:'+f(7*K)+'px" x="'+f(x)+'" y="'+f(z+r+1.2+th*.74)+'">'+t+'</text></g>'; };
    P.forEach(p=>{ if(p[0]==="home") return; g+=pin(p[0],p[1],p[2],p[3],p[4]); });   /* 1~3동 = ⭐ 내 집 핀이 대신 (겹치던 것) */
    try{ const fd=ISLE.myFd && ISLE.myFd(), f2=fd!=null && ISLE.SLOTS().find(x=>x.id===fd); if(f2) g+=pin("myfield","🌱","내 밭",f2.c[0]-OX,f2.c[1]-OZ-6,"#c9f2a6",1); }catch(_){}
    try{ const d=ISLE.doorCell(); if(d && tut.s>=1) g+=pin("myhome","⭐","내 집",d[0]+.5-OX,d[1]+.5-OZ,"#ffe27a",1); }catch(_){}
    try{ const p=hero.g.position; g+='<circle cx="'+f(p.x-OX)+'" cy="'+f(p.z-OZ)+'" r="3.2" fill="#ff4d5e" stroke="#fff" stroke-width="1.4"><animate attributeName="r" values="3.2;4.6;3.2" dur="1.2s" repeatCount="indefinite"/></circle>'; }catch(_){}
    el.classList.add("v5");
    el.innerHTML='<div class="mb"><div class="mh"><span>🗺 우리 마을 지도</span><button class="mx" aria-label="닫기">✕</button></div><svg viewBox="'+f(x0)+' '+f(z0)+' '+f(w)+' '+f(h)+'" preserveAspectRatio="xMidYMid meet">'+g+'</svg><div class="mt">📍 가고 싶은 곳을 눌러요 · <b style="color:#e63946">●</b> 나 · ⭐ 내 집은 🚀 바로 · 먼 곳은 🚉 기차</div></div>';
    el.classList.add("on"); }
  /* (v580) 사용자: 「기차가 있는데 지도로 텔포하면 기차의 의미가 있을까? · 집 가는 거랑 광산은 하게 해 줘」
     → 🚀 바로 가기는 ⭐ 내 집(무료)·⛏ 광산(🪙)만 · 다른 곳은 🚶 걸어가기 또는 🚉 기차역으로 (빨리 가려면 기차) */
  const near=(x,z)=>{ const bx=Math.floor(x), bz=Math.floor(z); for(let r=0;r<10;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){ if(Math.max(Math.abs(dx),Math.abs(dz))!==r) continue; if(!ISLE.blocked(bx+dx,bz+dz)) return [bx+dx,bz+dz]; } return null; };
  function pick2(title, opts){ const A=$("ask"), ok=$("askOk");
    try{ ask(title+'<div class="hxPick">'+opts.map((o,i)=>'<button class="btn on" data-gz="'+i+'">'+o[0]+'</button>').join("")+'</div>', null); ok.hidden=true;
      const h=e=>{ const b=e.target.closest("[data-gz]"); if(!b && !e.target.closest("#askNo") && e.target!==A) return; A.removeEventListener("click", h, true); ok.hidden=false; if(!b) return; A.classList.remove("on"); opts[+b.dataset.gz][1](); };
      A.addEventListener("click", h, true); }catch(_){ opts[0][1](); } }
  function homeNow(){ const d=ISLE.doorCell(); if(!d) return; const p=hero.g.position; if(Math.hypot(p.x-d[0]-.5, p.z-d[1]-.5)>6){ try{ TFAC.warp(d[0]+.5, d[1]+.5); }catch(_){} }
    try{ ISLE.enterHome(); }catch(_){ walkTo(d[0],d[1],()=>ISLE.enterHome()); } }
  function goZone(k){ const fee=(()=>{ try{ return TECO.FEE.warp; }catch(_){ return 5; } })();
    if(k==="myfield"){ pick2("🌱 <b>내 밭</b> (텃밭 섬)", [["🚶 걸어가기 (무료)", ()=>{ toast("🌱 내 밭 — 걸어가요", 1400); ISLE.goField(); }]]); return; }
    if(k==="myhome"){ const d=ISLE.doorCell(); if(!d) return; pick2("⭐ <b>내 집</b>", [["🚶 걸어가기", ()=>{ toast("⭐ 내 집 — 걸어가요", 1400); walkTo(d[0],d[1],()=>ISLE.enterHome()); }], ["🚀 바로 집으로 (무료)", homeNow]]); return; }
    if(k==="mine"){ const s=ISLE.SPOT.mine; if(!s) return; const c=near(s[0], s[2]);
      pick2("⛏ <b>광산</b>", [["🚶 걸어가기 (무료)", ()=>{ toast("⛏ 광산 — 걸어가요", 1400); if(c) walkTo(c[0],c[1]); }], ["🚀 바로 광산으로 🪙"+fee, ()=>{ if(!TECO.pay2({g:0,c:fee})) return; try{ ISLE.tripTo("mine"); }catch(_){} }]]); return; }
    const Z=(ISLE_MAP.zones||[]).find(z=>z.k===k); if(!Z) return;
    const t=Z.gate || (()=>{ let x=0,z=0; Z.poly.forEach(q=>{ x+=q[0]; z+=q[1]; }); return [x/Z.poly.length, z/Z.poly.length]; })();
    const c=near(t[0]+ISLE.OX, t[1]+ISLE.OZ); if(!c) return;
    const walk=()=>{ toast("🗺 "+Z.nm+" — 걸어가요", 1400); try{ walkTo(c[0], c[1]); }catch(_){} };
    const st=ISLE_MAP.spots.station, sc=st ? near(st[0]+ISLE.OX, st[1]+ISLE.OZ) : null, here=hero.g.position, far=Math.hypot(here.x-c[0], here.z-c[1])>28;
    const tf=(()=>{ try{ return TECO.trainFee(); }catch(_){ return 10; } })();
    if(!sc || !far){ walk(); return; }
    pick2("🗺 <b>"+Z.nm+"</b><br><small>멀어요! 빨리 가려면 🚉 기차 (🎫 🪙"+tf+" · 안내 방송을 맞히면 다음 표 반값)</small>", [["🚶 걸어가기 (무료)", walk], ["🚉 기차역으로", ()=>{ toast("🚉 기차역으로 걸어가요", 1400); try{ walkTo(sc[0], sc[1]); }catch(_){} }]]); }
  /* ── 바닥 빛 고리 (가장 가까운 할 수 있는 일) ── */
  let ring=null, ringT=0;
  function mkRing(){ const g=new THREE.RingGeometry(.62,.8,40); g.rotateX(-Math.PI/2); ring=new THREE.Mesh(g, new THREE.MeshBasicMaterial({color:0x7dff7a, transparent:true, opacity:.75, depthWrite:false})); ring.position.y=.03; ring.renderOrder=3; ring.visible=false; ISLE.G.add(ring); }
  ISLE.onBuild(()=>{ mkRing(); });
  let slowT=0, actK="";
  /* (v696) 상황 단추 — 엄지 자리 · 가까운 것에 따라 💬 말 걸기 · 🚪 들어가기 · 🎣 낚시 … (작은 이름표를 정확히 누르는 대신) */
  function verb(d){ const k=String(d.k||""), t=String(d.t||"").replace(/<[^>]+>/g,"").replace(/ [❗✨🆕✅]+$/u,"");
    if(/^(v_(tom|lily|sam|joe)|g_)/.test(k)) return ["💬","말 걸기"];
    if(k==="lake") return ["🎣","낚시"];
    return [d.ic||"👉", t.split(/ · | \(/)[0]]; }
  function act(best){ const b=$("ihAct"); if(!b) return; const busy=!!((typeof talkN!=="undefined" && talkN) || document.querySelector("#dlg.on") || document.querySelector(".sheet.on") || (m.classList.contains("on")));
    const L=(!busy && best && best.near) ? best : null; const k=L ? L.d.k+"|"+L.d.t : "";
    if(k!==actK){ actK=k; if(L){ const [i,s]=verb(L.d); b.querySelector("i").textContent=i; b.querySelector("span").textContent=s; b.onclick=e=>{ e.stopPropagation(); try{ if(F.st!=="idle" || trip.busy) return; }catch(_){} try{ L.d.act(); }catch(_){} }; } b.classList.toggle("on", !!L); } }
  function tick(dt){ if(!inIsle()){ if(d.classList.contains("fan")) fan(false); return false; } let anim=false;
    if(!ring || !ring.parent) mkRing();
    let best=null, bd=1e9; try{ LBL.forEach(L=>{ if(!L.near || !L.d.p || L.el.style.display==="none") return; const dd=Math.hypot(hero.g.position.x-L.d.p[0], hero.g.position.z-L.d.p[2]); if(dd<bd){ bd=dd; best=L; } }); }catch(e){}
    act(best);
    if(best){ ringT+=dt; const s=1+Math.sin(ringT*4)*.12, rad=Math.min(1.6, Math.max(.8,(best.d.r||2.4)*.33)); ring.position.set(best.d.p[0], .03, best.d.p[2]); ring.scale.setScalar(s*rad); ring.material.opacity=.55+Math.sin(ringT*4)*.2; if(!ring.visible) ring.visible=true; anim=true; }
    else if(ring.visible){ ring.visible=false; anim=true; }
    const t=performance.now(); if(t-slowT>400){ slowT=t; drawMe(); drawQ(); badge(); const bn=$("ipBan"); document.body.classList.toggle("ihMin", !!(bn && bn.classList.contains("on"))); }
    return anim; }
  /* 잡았다! 카드 — 📖 도감 단추 더하기 */
  function onCatch(){ if(!inIsle()) return; setTimeout(()=>{ const o=$("qOpts"); if(!o || o.querySelector("#qDexB")) return; const b=document.createElement("button"); b.className="btn"; b.id="qDexB"; b.textContent="📖 도감";
    b.onclick=()=>{ const ok=$("qOk"); if(ok) ok.click(); setTimeout(()=>click("bDex"), 250); }; o.appendChild(b); }, 0); }
  addEventListener("resize", ()=>{ if(d.classList.contains("fan")) fan(true); });
  return {tick, fan, onCatch, drawQ, badge, ring:()=>ring, openMap, goZone};
})();
window.IHUD=IHUD;
