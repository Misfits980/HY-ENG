/* (v723) 🔐 아이 계정 1단계 — 로그인 화면 · 내 기록 저장(/kacct) · 선생님 계정 관리
   사용자: 「아이디(영어 소문자) + 비밀번호(생일 6자리) · 넷플릭스처럼 누가 할까요 · 처음 쓰는 기기는 선생님 승인 · 우리 로고 포털이 열림 · 같은 반 같은 이름 막기 · 출입증 A」
   · 서버 v27 (Code.gs acct_ · acctT_) 이 비밀번호를 확인하고 출입증(Firebase 옛 방식 토큰 · 7일)을 줌 → /kacct/<uid>/main 에 내 기록
   · 1단계는 내 기기만 (공용 패드·선생님 기기는 지금처럼) · 예전 이름 고르기는 그대로 두되 로그인하면 명단 아이로 묶여서 저절로 안 물음
   · 계정을 켜기 전(선생님 「계정 켜기」)에는 아이 화면에 아무것도 안 보임 */
(function(){
"use strict";
const CSS=`#acctUI{position:fixed;inset:0;z-index:9000;display:none;color:#f4efff;font-family:var(--font,"Pretendard","Apple SD Gothic Neo","Malgun Gothic",sans-serif);user-select:none;-webkit-user-select:none;background:#120f2b;overflow:hidden}
#acctUI.on{display:block}
body.acOpen{overflow:hidden}
#acctUI button{font-family:inherit;cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
#acctUI .acBg{position:absolute;inset:-14px;background:radial-gradient(90% 55% at 50% 30%,rgba(120,70,220,.3),rgba(18,15,43,0) 70%),linear-gradient(180deg,rgba(18,15,43,.5),rgba(18,15,43,.72) 45%,rgba(12,10,30,.96)),url(assets/world/world-night.webp) 50% 40%/cover;filter:blur(3px)}
#acctUI .acSpk i{position:absolute;width:12px;height:12px;background:#fff;clip-path:polygon(50% 0,62% 38%,100% 50%,62% 62%,50% 100%,38% 62%,0 50%,38% 38%);filter:drop-shadow(0 0 4px #e6d4ff);animation:acTw 3s ease-in-out infinite;animation-delay:var(--d,0s)}
@keyframes acTw{0%,100%{transform:scale(.45);opacity:.25}50%{transform:scale(1);opacity:1}}
#acctUI .acIn{position:absolute;inset:0;max-width:480px;margin:0 auto}
#acctUI .acS{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;gap:10px;padding:calc(env(safe-area-inset-top,0px) + 14px) 16px calc(env(safe-area-inset-bottom,0px) + 16px);opacity:0;visibility:hidden;transform:translateX(var(--dx,24px));transition:opacity .28s,transform .28s,visibility 0s .28s}
#acctUI .acS.on{opacity:1;visibility:visible;transform:none;transition:opacity .28s,transform .28s}
#acctUI .grow{flex:1;min-height:6px}
#acctUI .acTop{width:100%;display:flex;align-items:center;justify-content:space-between;gap:6px;min-height:34px}
#acctUI .acTop.end{justify-content:flex-end}
#acctUI .sp{width:34px}
#acctUI .acGold{width:100%;border:3px solid #2a1650;border-radius:18px;padding:13px 0 10px;background:linear-gradient(180deg,#fff4a8 0%,#ffcf3d 45%,#e39700 100%);color:#2a1650;font-weight:900;font-size:21px;line-height:1.15;box-shadow:inset 0 3px 0 rgba(255,255,255,.75),inset 0 -5px 0 rgba(150,80,0,.35),0 5px 0 #2a1650,0 10px 18px rgba(0,0,0,.45)}
#acctUI .acGold small,#acctUI .acSlab small{display:block;font-size:11.5px;font-weight:800;margin-top:3px;opacity:.85}
#acctUI .acGold:active{transform:translateY(3px);box-shadow:inset 0 3px 0 rgba(255,255,255,.75),0 2px 0 #2a1650}
#acctUI .acGold:disabled{filter:grayscale(.9) brightness(.65);cursor:default;transform:none}
#acctUI .acSlab{position:relative;border:2px solid transparent;border-radius:12px;padding:11px 18px 9px;background:linear-gradient(180deg,#4a3889,#2c2062) padding-box,linear-gradient(180deg,#ffe58a,#c58a14) border-box;color:#fff3c4;font-weight:900;font-size:15px;box-shadow:0 4px 0 #1a1238,0 8px 14px rgba(0,0,0,.35);white-space:nowrap}
#acctUI .acSlab.sm{font-size:12.5px;padding:7px 11px 6px;border-radius:10px}
#acctUI .acSlab:active{transform:translateY(2px);box-shadow:0 2px 0 #1a1238}
#acctUI button:focus-visible{outline:3px solid #ffe07a;outline-offset:2px}
#acctUI .acGt{background:linear-gradient(180deg,#fff7c2 0%,#ffd54a 50%,#e59a00 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(1.5px 0 0 #2a1650) drop-shadow(-1.5px 0 0 #2a1650) drop-shadow(0 1.5px 0 #2a1650) drop-shadow(0 -1.5px 0 #2a1650) drop-shadow(0 4px 4px rgba(0,0,0,.45))}
#acctUI .acBig{font-family:"Jua",var(--font,sans-serif);font-size:30px;line-height:1.2;text-align:center}
#acctUI .acFloat{width:100%;animation:acBob 3.2s ease-in-out infinite}
@keyframes acBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
#acctUI .acFloat.sm{width:56%}#acctUI .acFloat.big{width:100%;margin-top:6px}
#acctUI .acSmall{width:100%;display:block;max-width:none;filter:drop-shadow(0 6px 10px rgba(0,0,0,.4))}
#acctUI .acLogo{position:relative;width:100%;aspect-ratio:1024/679;--p:1;transform-origin:48.8% 42.5%;transition:transform 1s cubic-bezier(.6,0,.8,.4);filter:drop-shadow(0 8px 14px rgba(0,0,0,.45))}
#acctUI .acLogo img{position:absolute;inset:0;width:100%;height:100%;max-width:none}
#acctUI .acPg{position:absolute;left:48.8%;top:42.5%;width:30%;height:66%;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(ellipse,rgba(255,255,255,.95),rgba(214,170,255,.85) 30%,rgba(150,80,255,.5) 55%,rgba(120,60,255,0) 72%);opacity:calc(.08 + var(--p) * .16);mix-blend-mode:screen;transition:opacity .25s}
#acctUI .acPs{position:absolute;left:48.8%;top:42.5%;width:26%;height:56%;transform:translate(-50%,-50%);border-radius:50%;background:conic-gradient(from 0deg,rgba(255,255,255,0),rgba(230,200,255,.9) 12%,rgba(255,255,255,0) 25%,rgba(200,150,255,.8) 40%,rgba(255,255,255,0) 52%,rgba(240,220,255,.9) 66%,rgba(255,255,255,0) 78%,rgba(190,140,255,.8) 90%,rgba(255,255,255,0));-webkit-mask:radial-gradient(ellipse,#000 30%,transparent 70%);mask:radial-gradient(ellipse,#000 30%,transparent 70%);mix-blend-mode:screen;opacity:calc(var(--p) * .13);animation:acSpin calc(6s - var(--p) * .7s) linear infinite}
@keyframes acSpin{to{transform:translate(-50%,-50%) rotate(360deg)}}
#acctUI .acFloat.dim .acLogo{--p:0}
#acctUI .acLogo.bad{animation:acShake .45s}
@keyframes acShake{20%{transform:translateX(-10px)}40%{transform:translateX(9px)}60%{transform:translateX(-6px)}80%{transform:translateX(4px)}}
#acctUI .acLogo.go{transform:scale(9)}#acctUI .acLogo.go .acPg,#acctUI .acLogo.go .acPs{opacity:1}
#acctUI .acStep{display:flex;align-items:center;gap:5px;font-size:11.5px;font-weight:900;color:#9e93c6}
#acctUI .acStep b.cur{color:#ffe07a}#acctUI .acStep i{width:16px;height:2px;background:#6a5aa8;border-radius:1px}
#acctUI .acPlate{width:calc(100% - 24px);position:relative;padding:8px 18px 10px;border-radius:14px;border:3px solid transparent;background:linear-gradient(180deg,#3d2e78,#231a4c) padding-box,linear-gradient(180deg,#fff0a0,#d09a1c 50%,#8a5a00) border-box;box-shadow:0 5px 0 #1a1238,0 12px 20px rgba(0,0,0,.4);margin-top:4px}
#acctUI .acPlate::before,#acctUI .acPlate::after{content:"";position:absolute;top:50%;width:18px;height:18px;transform:translateY(-50%) rotate(45deg);background:radial-gradient(circle,#c49bff 0 28%,#5a24c0 30% 40%,transparent 42%),linear-gradient(135deg,#fff1a0,#c98a14);border:2px solid #2a1650}
#acctUI .acPlate::before{left:-12px}#acctUI .acPlate::after{right:-12px}
#acctUI .acPlate .lab{display:block;font-size:11px;font-weight:900;color:#d9c9ff;text-align:center;letter-spacing:.04em}
#acctUI .acTyped{font-family:"Lilita One",var(--font,sans-serif);font-size:40px;letter-spacing:3px;line-height:1.1;min-height:46px;display:flex;justify-content:center;align-items:center}
#acctUI .acTyped .ph{color:rgba(255,255,255,.16)}
#acctUI .acTyped .nw{animation:acPop .25s}
@keyframes acPop{50%{transform:scale(1.35)}}
#acctUI .caret{display:inline-block;width:3px;height:32px;background:#ffd54a;margin-left:4px;border-radius:2px;animation:acBlink 1s steps(1) infinite}
@keyframes acBlink{50%{opacity:0}}
#acctUI .acHint{font-size:12.5px;color:#cfc4f0;font-weight:700;text-align:center;line-height:1.45}#acctUI .acHint b{color:#ffe07a}
#acctUI .acKb{width:100%;display:flex;flex-direction:column;gap:6px}
#acctUI .acKb div{display:flex;gap:5px;justify-content:center}
#acctUI .acKb button{flex:1;max-width:44px;height:50px;border:none;border-radius:10px;background:linear-gradient(180deg,#5a47a3,#3a2b78);box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 3px 0 #1a1238;color:#ffd65a;font-family:"Lilita One",var(--font,sans-serif);font-size:23px;padding:0 0 2px;text-shadow:0 1px 0 #2a1650}
#acctUI .acKb button.w{max-width:93px;font-size:13px;color:#fff3c4;font-family:inherit;font-weight:900}
#acctUI .acKb button:active{transform:translateY(2px);box-shadow:0 1px 0 #1a1238,0 0 12px rgba(190,140,255,.9);background:linear-gradient(180deg,#7a62d0,#4e3a9c)}
#acctUI .acWho{display:flex;align-items:center;gap:6px;font-weight:900;font-size:14px;color:#fff3c4}
#acctUI .acWho i{width:30px;height:30px;border-radius:50%;background-color:#3d6db3;border:2px solid #ffd54a;box-shadow:0 0 0 2px #2a1650}
#acctUI .acGems{display:flex;gap:5px;padding:6px 14px;border-radius:14px;border:2px solid transparent;background:linear-gradient(180deg,#36296c,#1f1745) padding-box,linear-gradient(180deg,#ffe58a,#b47a10) border-box;box-shadow:0 4px 0 #1a1238}
#acctUI .acDm{width:35px;height:47px;overflow:visible;display:block}
#acctUI .acDm .o{fill:url(#acGold);stroke:#2a1650;stroke-width:3}
#acctUI .acDm .b{fill:#2a1650}#acctUI .acDm .cr{fill:url(#acOff)}#acctUI .acDm .hi{fill:rgba(255,255,255,.12)}#acctUI .acDm .sh{fill:rgba(0,0,0,.25)}
#acctUI .acDm.on .cr{fill:url(#acOn)}#acctUI .acDm.on .hi{fill:rgba(255,255,255,.45)}#acctUI .acDm.on{filter:drop-shadow(0 0 6px rgba(180,120,255,.95))}
#acctUI .acDm.pop{animation:acPop .3s}
#acctUI .acGems.au .acDm .cr{fill:url(#acAu)}#acctUI .acGems.au .acDm{filter:drop-shadow(0 0 8px rgba(255,230,140,1))}
#acctUI .acGems.bad .acDm .cr{fill:url(#acBad)}#acctUI .acGems.bad .acDm{filter:drop-shadow(0 0 6px rgba(255,90,80,.95))}
#acctUI .acMsg{min-height:20px;font-size:13.5px;font-weight:900;color:#f4efff;text-align:center;text-shadow:0 2px 0 #2a1650}#acctUI .acMsg.bad{color:#ffb4a8}#acctUI .acMsg.ok{color:#ffe07a}#acctUI .acMsg b{color:#ffe07a}
#acctUI .acKeys{display:grid;grid-template-columns:repeat(3,1fr);gap:8px 12px;width:100%;align-items:center}
#acctUI .acKeys button{height:62px;border:none;background:url(assets/ui/stone-p0.webp) center/100% 100% no-repeat;padding:0 0 9px;filter:drop-shadow(0 4px 4px rgba(0,0,0,.45))}
#acctUI .acKeys button span{font-family:"Lilita One",var(--font,sans-serif);font-weight:900;font-size:32px;line-height:1;background:linear-gradient(180deg,#fff7c2 0%,#ffd54a 50%,#e59a00 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(1.5px 0 0 #2a1650) drop-shadow(-1.5px 0 0 #2a1650) drop-shadow(0 1.5px 0 #2a1650) drop-shadow(0 -1.5px 0 #2a1650)}
#acctUI .acKeys button.g{height:42px;border:2px solid transparent;border-radius:30px;background:linear-gradient(180deg,#4a3889,#2c2062) padding-box,linear-gradient(180deg,#ffe58a,#c58a14) border-box;color:#fff3c4;font-weight:900;font-size:12.5px;padding:0;filter:none;box-shadow:0 3px 0 #1a1238}
#acAdm .acNote.bad{background:rgba(255,90,90,.14);border:1px solid rgba(255,120,120,.5);color:#ffd7d7}
#acctUI .acKeys .nil{display:block}
#acctUI .acKeys button:active{transform:translateY(3px);filter:brightness(1.25) drop-shadow(0 0 12px rgba(190,140,255,.95))}
#acctUI .acPpl{display:flex;gap:16px;justify-content:center;width:100%;flex-wrap:wrap;margin-top:6px}
#acctUI .acPpl button{display:flex;flex-direction:column;align-items:center;gap:4px;background:none;border:none;color:#fff;padding:6px;border-radius:16px}
#acctUI .acPpl i{width:96px;height:96px;border-radius:50%;background-color:#3d6db3;border:5px solid #ffd54a;box-shadow:0 0 0 3px #2a1650,0 0 22px rgba(170,110,255,.55),0 10px 16px rgba(0,0,0,.45)}
#acctUI .acPpl button:active i{transform:scale(.95)}
#acctUI .acPpl b{font-family:"Jua",var(--font,sans-serif);font-size:20px;color:#fff3c4;text-shadow:0 2px 0 #2a1650}#acctUI .acPpl small{font-size:11px;color:#b9aee0;font-weight:700}
#acctUI .acRow{display:flex;gap:10px;width:100%}#acctUI .acRow .acSlab{flex:1}
#acctUI .acCrew{position:relative;width:100%;flex:1;min-height:120px;max-height:180px}
#acctUI .acCrew i{position:absolute;bottom:20px;width:72px;height:81px;background-repeat:no-repeat;filter:drop-shadow(0 6px 6px rgba(0,0,0,.5));animation:acHop 2.6s ease-in-out infinite}
#acctUI .acCrew .c1{left:2%;bottom:34px;animation-delay:.3s}#acctUI .acCrew .c5{right:2%;bottom:34px;animation-delay:1.1s}
#acctUI .acCrew .c2{left:20%;width:84px;height:94px;bottom:22px;animation-delay:.7s}#acctUI .acCrew .c4{right:20%;width:84px;height:94px;bottom:22px;animation-delay:1.5s}
#acctUI .acCrew .c3{left:50%;margin-left:-50px;width:100px;height:112px;bottom:8px;animation-delay:0s}
#acctUI .acCrew .gr{position:absolute;left:4%;right:4%;bottom:2px;height:40px;border-radius:50%;background:radial-gradient(ellipse,rgba(170,110,255,.55),rgba(120,70,220,.18) 55%,transparent 72%)}
@keyframes acHop{0%,100%{transform:translateY(0)}12%{transform:translateY(-10px)}24%{transform:translateY(0)}}
#acctUI .acSent{font-size:12px;font-weight:800;color:#e6dcff;background:rgba(20,14,48,.55);border:1px solid rgba(220,190,255,.3);border-radius:99px;padding:6px 12px;display:flex;align-items:center;gap:6px}
#acctUI .dots{display:inline-flex;gap:3px}#acctUI .dots i{width:5px;height:5px;border-radius:50%;background:#ffe07a;animation:acDot 1.2s ease-in-out infinite}#acctUI .dots i:nth-child(2){animation-delay:.2s}#acctUI .dots i:nth-child(3){animation-delay:.4s}
@keyframes acDot{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-3px)}}
#acctUI .acCmp{display:grid;grid-template-columns:1fr 1fr;gap:8px;width:100%}#acctUI .acCmp div{background:rgba(20,14,48,.65);border:1px solid rgba(255,214,90,.25);border-radius:14px;padding:10px;font-size:13.5px;line-height:1.6;color:#d9d2ef}#acctUI .acCmp b{display:block;color:#fff3c4;font-size:14px;margin-bottom:2px}
#acctUI .acFlash{position:absolute;inset:0;background:radial-gradient(circle at 50% 30%,#fff,#ecdcff 40%,#a77cff);opacity:0;pointer-events:none;transition:opacity .45s;z-index:5}
#acctUI.go .acFlash{opacity:1;transition-delay:.55s}
#acctUI .acS.wel{z-index:6;justify-content:center;gap:12px;background:radial-gradient(120% 70% at 50% 25%,#3a2a80,#15112e 70%)}
#acctUI .acStats{display:flex;gap:6px;flex-wrap:wrap;justify-content:center}#acctUI .acStats span{font-weight:900;font-size:13px;color:#ffe07a;background:rgba(20,14,48,.6);border:1px solid rgba(255,224,122,.35);border-radius:99px;padding:5px 10px}
#acctUI .acFace{position:relative;width:130px;height:130px;display:grid;place-items:center}
#acctUI .acFace i{position:relative;z-index:1;width:116px;height:116px;border-radius:50%;background-color:#3d6db3;border:6px solid #ffd54a;box-shadow:0 0 0 3px #2a1650,0 0 30px rgba(255,220,120,.6)}
#acctUI .acFace.sm{width:96px;height:96px}#acctUI .acFace.sm i{width:88px;height:88px}
#acctUI .acFace .burst{position:absolute;left:50%;top:50%;width:260px;height:260px;margin:-130px 0 0 -130px;background:repeating-conic-gradient(rgba(255,226,140,.5) 0 7deg,rgba(255,226,140,0) 7deg 20deg);-webkit-mask:radial-gradient(circle,#000 20%,transparent 66%);mask:radial-gradient(circle,#000 20%,transparent 66%);animation:acSpin2 12s linear infinite}
@keyframes acSpin2{to{transform:rotate(360deg)}}
#acctUI .acConf{position:absolute;inset:0;overflow:hidden;pointer-events:none}
#acctUI .acConf b{position:absolute;top:-20px;width:8px;height:13px;border-radius:2px;background:var(--c);transform:rotate(var(--r));opacity:0}
#acctUI .acS.wel.on .acConf b{animation:acFall 2.4s ease-in var(--t) 1 forwards}
@keyframes acFall{0%{opacity:1;transform:translateY(0) rotate(var(--r))}100%{opacity:.9;transform:translateY(110vh) rotate(calc(var(--r) + 540deg))}}
#acctUI .acS.wel.on .acFace{animation:acPopIn .5s cubic-bezier(.3,1.6,.5,1)}
@keyframes acPopIn{0%{transform:scale(.3);opacity:0}100%{transform:scale(1);opacity:1}}
#acctUI .acCard{width:100%;display:flex;flex-direction:column;gap:6px}
#acctUI .acCard div{display:flex;justify-content:space-between;align-items:center;gap:8px;border-radius:12px;padding:10px 12px;border:1.5px solid transparent;background:linear-gradient(180deg,#2e2366,#1d1645) padding-box,linear-gradient(180deg,#ffe58a88,#c58a1466) border-box;font-size:13.5px}
#acctUI .acCard span{color:#cfc4f0}#acctUI .mono{font-family:"Lilita One",monospace;font-size:17px;color:#ffd65a;letter-spacing:1px}
#acctUI .acHold{position:relative;width:100%;display:flex;align-items:center;justify-content:center;gap:6px;padding:14px;border-radius:14px;font-weight:900;font-size:16px;color:#ffe1da;background:linear-gradient(180deg,#7a2a3a,#4a1828) padding-box,linear-gradient(180deg,#ff9a8c,#b0382b) border-box;border:2px solid transparent;overflow:hidden}
#acctUI .acHold small{font-size:11px;font-weight:700;color:#ffc9bf}
#acctUI .acHold .fill{position:absolute;left:0;top:0;bottom:0;width:0;background:rgba(255,160,140,.3)}
#acctUI .acHold.hold .fill{width:100%;transition:width 2s linear}
@media (min-width:700px){#acctUI .acKb button{max-width:52px;height:56px;font-size:26px}#acctUI .acKeys button{height:70px}}
@media (min-width:700px) and (min-height:950px){#acctUI .acIn{max-width:600px}#acctUI .acS[data-s=home]{justify-content:center;gap:16px}#acctUI .acS[data-s=home]>.acTop{position:absolute;top:calc(env(safe-area-inset-top,0px) + 14px);left:16px;right:16px;width:auto}#acctUI .acCrew{max-height:250px}#acctUI .acGold{font-size:25px;padding:17px 0 13px}#acctUI .acGold small,#acctUI .acSlab small{font-size:13.5px}#acctUI .acSlab{font-size:17px}#acctUI .acSlab.sm{font-size:14px}#acctUI .acKeys{gap:14px 26px}#acctUI .acKeys button{height:84px}#acctUI .acKeys button span{font-size:40px}#acctUI .acKeys button.g{height:50px;font-size:15px}#acctUI .acKb button{max-width:64px;height:64px;font-size:28px}}
@media (prefers-reduced-motion:reduce){#acctUI .acFloat,#acctUI .acSpk i,#acctUI .caret,#acctUI .acPs,#acctUI .acCrew i,#acctUI .dots i,#acctUI .acFace .burst,#acctUI .acS.wel.on .acConf b{animation:none!important}#acctUI .acLogo{transition:none}#acctUI .acLogo.go{transform:none}#acctUI .acS{transition:none}}
.acChip{position:absolute;left:50%;transform:translateX(-50%);top:calc(env(safe-area-inset-top,0px) + 12px);z-index:5;display:flex;align-items:center;gap:6px;padding:4px 12px 4px 4px;border-radius:99px;border:1.5px solid transparent;background:linear-gradient(180deg,#4a3889,#2c2062) padding-box,linear-gradient(180deg,#ffe58a,#c58a14) border-box;box-shadow:0 3px 0 #1a1238;font:900 13px var(--font,sans-serif);color:#fff3c4;cursor:pointer}
.acChip i{width:28px;height:28px;border-radius:50%;background-color:#3d6db3;border:2px solid #ffd54a;display:grid;place-items:center;font-style:normal;font-size:14px}
.acChip i.k{background:#2c2062}
.acChip b.g{display:flex;flex-direction:column;align-items:flex-start;line-height:1.05}.acChip b.g small{font:800 10px var(--font,sans-serif);color:#cdbdf5;margin-top:1px;white-space:nowrap}
#btnShop.acLk{position:relative;opacity:.62}#scSetup .acLkC{filter:saturate(.6) brightness(.93)}#scSetup .acLkC .townTag{color:#4b3527;background:#ffe08a}
.acLkB{position:absolute;left:50%;bottom:8px;transform:translateX(-50%);padding:3px 10px;border-radius:99px;background:rgba(20,14,48,.88);border:1.5px solid #ffd54a;color:#ffe9a8;font:900 12px var(--font,sans-serif);white-space:nowrap;pointer-events:none;z-index:2}
#btnShop.acLk .acLkB{left:auto;right:6px;top:4px;bottom:auto;transform:none;padding:1px 6px;font-size:12px}
.acAdm .acPend{border:1.5px solid #ffd54a;background:rgba(255,200,80,.1);border-radius:12px;padding:8px 10px;margin:6px 0;display:flex;flex-direction:column;gap:6px}
.acAdm .acPend .row{display:flex;align-items:center;gap:6px;flex-wrap:wrap}.acAdm .acPend .row span{flex:1;min-width:160px}
.acAdm .acBar,.acAdm .acTabs{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.acAdm .acList{display:flex;flex-direction:column;gap:6px}
.acAdm .acR{border:1px solid rgba(255,214,90,.25);border-radius:12px;overflow:hidden}
.acAdm .acRh{width:100%;display:flex;align-items:center;gap:8px;padding:9px 10px;background:rgba(40,30,90,.5);border:none;color:inherit;font:inherit;text-align:left;cursor:pointer}
.acAdm .acRh b{font-size:15px}.acAdm .mono{font-family:"Lilita One",monospace;color:#ffd65a;letter-spacing:1px}
.acAdm .st{margin-left:auto;font-size:11.5px;font-weight:900;padding:3px 9px;border-radius:99px;white-space:nowrap}
.acAdm .st.ok{background:#1d3b2a;color:#9be8a6}.acAdm .st.lock{background:#4a1f2e;color:#ffb4a8}.acAdm .st.wait{background:#4a3a12;color:#ffe07a}.acAdm .st.none{background:#2c2850;color:#b9aee0}
.acAdm .acD{padding:8px 10px;display:flex;flex-direction:column;gap:7px;background:rgba(20,14,48,.4)}
.acAdm .kv{display:flex;align-items:center;gap:6px;flex-wrap:wrap}.acAdm .kv>span{min-width:120px;font-size:13px;color:#cfc4f0}.acAdm .kv.col{flex-direction:column;align-items:flex-start}
.acAdm .kv input,.acAdm .kv select{flex:1;min-width:90px;max-width:160px;padding:7px 8px;border-radius:8px;border:1px solid rgba(255,255,255,.25);background:rgba(10,8,30,.6);color:#fff;font:inherit;font-size:14px}
.acAdm .dv{display:flex;align-items:center;gap:8px;font-size:13px}
.acAdm .mini.warn{background:#7a2a3a;color:#ffe1da}
.acAdm .acMk{display:flex;flex-direction:column;gap:6px;margin-top:6px}
.acAdm .acNote{font-size:13px;color:#ffe07a;margin:4px 0}
.acAdm .acRes{margin-top:8px;font-size:13px;line-height:1.7}.acAdm .acRes em{font-style:normal;color:#ffd27a}
`;
try{ if(!document.getElementById("acctCss")){ const st=document.createElement("style"); st.id="acctCss"; st.textContent=CSS; document.head.appendChild(st); } }catch(e){}
const AK="hyeng_acct", AL="hyeng_acct_list", AS="hyeng_acct_sync", SKIPK="hyeng_acct_skip";
const $$=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const jget=(k,d)=>{ try{ const v=JSON.parse(localStorage.getItem(k)||"null"); return v==null?d:v; }catch(e){ return d; } };
const jset=(k,v)=>{ try{ if(v==null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); }catch(e){} };
const CH=["hero","explorer","archer","mage","knight","scholar","ghost","cat","wolf"];
const myChar=()=>{ try{ const s=JSON.parse(localStorage.getItem("hyeng_setup_v1")||"null"); const c=s && s.char; return CH.indexOf(c)>=0 ? c : "hero"; }catch(e){ return "hero"; } };
const face=c=>'background-image:url(assets/chars/char-portraits.webp);background-size:900% 100%;background-position:'+(Math.max(0,CH.indexOf(c))*12.5)+'% 0';
const cheer=c=>'background-image:url(assets/chars/char-cheer.webp);background-size:900% 100%;background-position:'+(Math.max(0,CH.indexOf(c))*12.5)+'% 0';
const devName=()=>{ const u=navigator.userAgent||""; const os=/iPad|Macintosh.*Mobile/.test(u)||(/Macintosh/.test(u)&&navigator.maxTouchPoints>1)?"아이패드":/iPhone/.test(u)?"아이폰":/Android/.test(u)?(/Mobile/.test(u)?"안드로이드 폰":"안드로이드 패드"):/CrOS/.test(u)?"크롬북":/Windows/.test(u)?"윈도우 PC":/Mac/.test(u)?"Mac":"기기";
  const br=/SamsungBrowser/.test(u)?"삼성 인터넷":/CriOS|Chrome/.test(u)?"크롬":/Safari/.test(u)?"사파리":/Firefox/.test(u)?"파이어폭스":""; return (os+(br?" · "+br:"")).slice(0,30); };
const tone=(f,d,t,v)=>{ try{ SFX.tone(f,d||.15,t||"triangle",v||.05); }catch(e){} };

/* ───────────── 계정 상태 · 서버 · 내 기록 ───────────── */
const Acct = {
  get(){ const a=jget(AK,null); return a && a.uid && a.ds ? a : null; },
  on(){ try{ if(window.HY_ACCT_OFF) return false; }catch(e){} return !!this.get(); },
  list(){ const L=jget(AL,[]); return Array.isArray(L) ? L.filter(x=>x && x.id).slice(0,4) : []; },
  remember(a){ const L=this.list().filter(x=>x.id!==a.id); L.unshift({id:a.id, n:a.n, c:myChar(), at:Date.now()}); jset(AL, L.slice(0,4)); },
  forget(id){ jset(AL, this.list().filter(x=>x.id!==id)); },
  /* 공용 패드 · 선생님 기기는 1단계에 안 씀 */
  usable(){ try{ if(TEST_STAGE) return false; }catch(e){} try{ const q=new URLSearchParams(location.search); if(q.has("admin") || q.has("vs")) return false; }catch(e){} try{ if(Kid.shared() || Kid.teacher()) return false; }catch(e){ return false; }
    /* (v725) 선생님 휴대폰(관리 화면을 6자리 코드로 연결한 기기 · 이번에 관리 화면을 연 기기)도 아이 로그인 안 띄움 — 사용자 「나도 로그인하라고 뜬다」 */
    try{ if(/^[0-9a-f]{40,}$/.test(localStorage.getItem("hyeng_admin_key")||"")) return false; }catch(e){}
    try{ if(sessionStorage.getItem("hyeng_admin_ok")) return false; }catch(e){}
    return true; },
  call(o){ try{ return Online.submit(o).then(r=>r||{ok:false, err:"net"}).catch(()=>({ok:false, err:"net"})); }catch(e){ return Promise.resolve({ok:false, err:"net"}); } },
  base(){ try{ return FB_URLS[0]; }catch(e){ return ""; } },
  async tok(){ const a=this.get(); if(!a) return ""; let need=false; try{ need=!a.tag && !sessionStorage.getItem("hyeng_acct_tg"); }catch(e){} if(a.tok && Date.now()<a.exp-864e5 && !need) return a.tok;
    try{ sessionStorage.setItem("hyeng_acct_tg","1"); }catch(e){}
    const r=await this.call({type:"acctRenew", uid:a.uid, dev:a.dk, ds:a.ds});
    if(r && r.ok && r.tok){ const b=Object.assign({}, a, {tok:r.tok, exp:r.exp}, r.acct||{}); jset(AK, b); try{ if(/^\d{4}$/.test(b.tag||"")) localStorage.setItem("hyeng_tag", b.tag); }catch(e){} return b.tok; }
    if(r && r.err==="gone"){ this.kicked(); return ""; }
    return a.tok && Date.now()<a.exp ? a.tok : ""; },
  async fb(path, method, val){ const t=await this.tok(), b=this.base(); if(!t || !b) return {ok:false, err:"tok"};
    try{ const r=await fetch(b+path+".json?auth="+encodeURIComponent(t), method==="GET" ? {cache:"no-store"} : {method, headers:{"Content-Type":"application/json"}, body:JSON.stringify(val)});
      if(r.status===401){ return {ok:false, err:"deny"}; } if(!r.ok) return {ok:false, err:"http"+r.status}; return {ok:true, v:await r.json()}; }catch(e){ return {ok:false, err:"net"}; } },
  /* 이 기기 기록 묶음 (예전 ☁️ 백업과 같은 모양) */
  pack(){ try{ return Cloud.pack(); }catch(e){ return {}; } },
  sum(){ try{ return Cloud.sum(); }catch(e){ return {}; } },
  hash(t){ try{ return Cloud.hash(t); }catch(e){ return String(t.length); } },
  empty(){ try{ return Cloud.empty(); }catch(e){ return false; } },
  body(data, rev){ const a=this.get(); return {at:Date.now(), dev:a ? a.dk : "", rev:rev|0, v:(()=>{ try{ return GAME_VER; }catch(e){ return ""; } })(), sm:this.sum(), d:JSON.stringify({hyeng:(()=>{ try{ return GAME_VER; }catch(e){ return ""; } })(), data})}; },
  /* 서버 기록을 이 기기에 넣고 새로 켬 */
  apply(m, why){ const a=this.get(); if(!a || !m || !m.d) return false; let o=null; try{ o=JSON.parse(m.d); }catch(e){} const data=(o && o.data) || {};
    try{ Move.keys().forEach(k=>{ if(!Move.SKIP.test(k) && !/^hyeng_acct/.test(k)) try{ localStorage.removeItem(k); }catch(e){} }); }catch(e){}
    Object.keys(data).forEach(k=>{ if(/^(hyeng|wgr)_/.test(k) && !/^hyeng_acct/.test(k) && typeof data[k]==="string") try{ localStorage.setItem(k, data[k]); }catch(e){} });
    this.bind(a); jset(AS, {uid:a.uid, rev:m.rev|0, h:this.hash(JSON.stringify(this.pack())), at:Date.now()});
    try{ sessionStorage.setItem("hyeng_acct_why", why||""); }catch(e){}
    setTimeout(()=>location.reload(), 500); return true; },
  /* 이 기기를 계정 아이로 — 예전 「나는 누구?」가 저절로 안 묻게 (명단 아이 · 게임 이름) */
  bind(a){ try{ if(a.rid) localStorage.setItem("hyeng_me", JSON.stringify({id:a.rid, at:Date.now(), t:a.t||"", acct:1})); }catch(e){}
    try{ if(a.n) localStorage.setItem("hyeng_nick", a.n); }catch(e){} try{ localStorage.removeItem("hyeng_kid"); }catch(e){}
    /* (v727) 🏷 계정 태그(서버 v28) = 이 기기 태그 — 랭킹·통계·My Town·도전장이 기기가 아니라 아이를 따라감 */
    try{ if(/^\d{4}$/.test(a.tag||"")) localStorage.setItem("hyeng_tag", a.tag); }catch(e){} },
  async park(why){ const a=this.get(); if(!a) return false; const r=await this.fb("/kacct/"+a.uid+"/park/"+a.dk+"_"+Date.now().toString(36), "PUT", Object.assign(this.body(this.pack(), 0), {why})); return r.ok; },
  async put(rev){ const a=this.get(); if(!a) return {ok:false}; const data=this.pack(), t=JSON.stringify(data); if(t.length>3500000) return {ok:false, err:"big"};
    const r=await this.fb("/kacct/"+a.uid+"/main", "PUT", this.body(data, rev)); if(r.ok) jset(AS, {uid:a.uid, rev:rev|0, h:this.hash(t), at:Date.now()}); return r; },
  busy:false,
  /* 저장 — 서버 rev 가 내가 마지막으로 맞춘 것과 같을 때만 (늦게 깬 기기가 새 기록을 덮지 않게) */
  async save(force){ if(this.busy || !this.on()) return false; const a=this.get(), S=jget(AS,{}); if(S.uid!==a.uid) return false;
    const t=JSON.stringify(this.pack()), h=this.hash(t); if(!force && h===S.h) return true;
    this.busy=true; try{ const rv=await this.fb("/kacct/"+a.uid+"/main/rev", "GET"); if(!rv.ok) return false; const sr=rv.v|0;
      if(sr!==(S.rev|0)){ await this.conflict(sr, h!==S.h); return false; }
      const r=await this.put(sr+1); return r.ok; } finally{ this.busy=false; } },
  /* 다른 기기가 그새 저장함 → 여기서 바뀐 게 없으면 받아 오기 · 있으면 여기 것은 선생님께 맡기고 받아 오기 */
  async conflict(sr, changed){ const a=this.get(); const m=await this.fb("/kacct/"+a.uid+"/main", "GET"); if(!m.ok || !m.v) return;
    const home=(()=>{ try{ return $$("scStart").classList.contains("on"); }catch(e){ return true; } })();
    if(!home){ this.pend=1; return; }   // 하는 중이면 첫 화면에 돌아왔을 때
    if(changed) await this.park("conflict");
    this.apply(m.v, changed ? "conflict" : "pull"); },
  /* 켤 때 · 첫 화면에 돌아올 때 */
  async check(){ if(!this.on()) return; const a=this.get(), S=jget(AS,{}); if(S.uid!==a.uid) return this.first();
    const rv=await this.fb("/kacct/"+a.uid+"/main/rev", "GET"); if(!rv.ok) return; if((rv.v|0)!==(S.rev|0)) await this.conflict(rv.v|0, this.hash(JSON.stringify(this.pack()))!==S.h); },
  /* 이 기기에서 이 계정으로 처음 — 「이 기기 기록 맞아요?」 */
  async first(){ const a=this.get(); const m=await this.fb("/kacct/"+a.uid+"/main", "GET"); if(!m.ok) return {err:m.err};
    const srv=m.v && m.v.d ? m.v : null, sm=(srv && srv.sm) || {}, sEmpty=!srv || (!(sm.g|0) && !(sm.e|0) && !(sm.st|0) && !(sm.dx|0)), lEmpty=this.empty();
    if(lEmpty){ if(srv){ this.apply(srv, "load"); return {applied:1}; } const r=await this.put(1); return r.ok ? {ok:1} : {err:r.err}; }
    const pick=await UI.mine(a, this.sum(), srv ? sm : null);
    if(pick==="mine"){
      const L=this.sum(), score=x=>((x.st|0)*1000+(x.dx|0)*10+((x.e|0)>0?1:0)), lw=sEmpty || score(L)>=score(sm);
      if(lw){ if(srv) await this.fb("/kacct/"+a.uid+"/park/srv_"+Date.now().toString(36), "PUT", Object.assign({}, srv, {why:"merge-srv"}));
        const r=await this.put(((srv && srv.rev)|0)+1); return r.ok ? {ok:1, merged:srv?1:0} : {err:r.err}; }
      await this.park("merge"); this.apply(srv, "merge"); return {applied:1}; }
    await this.park("other");   // 동생·친구 것 → 선생님께
    if(srv){ this.apply(srv, "other"); return {applied:1}; }
    try{ Move.keys().forEach(k=>{ if(!Move.SKIP.test(k) && !/^hyeng_acct/.test(k)) try{ localStorage.removeItem(k); }catch(e){} }); }catch(e){}
    this.bind(a); const r=await this.put(1); setTimeout(()=>location.reload(), 400); return r.ok ? {ok:1} : {err:r.err}; },
  /* 로그인 · 승인 기다림 */
  async login(id, pw){ const r=await this.call({type:"acctLogin", id, pw, dev:Online.dev(), n:devName()}); if(r && r.ok && r.tok) this.won(r); return r; },
  won(r){ const a=Object.assign({uid:r.uid, dk:r.dk, ds:r.ds, tok:r.tok, exp:r.exp}, r.acct||{}); jset(AK, a); this.remember(a); try{ if(/^\d{4}$/.test(a.tag||"")) localStorage.setItem("hyeng_tag", a.tag); }catch(e){} try{ sessionStorage.removeItem(SKIPK); }catch(e){} Lock.set(false); },
  wait(id, pid){ return this.call({type:"acctWait", id, pid}); },
  /* 로그아웃 — 서버에 저장된 걸 확인한 뒤에만 · 이 기기 기록은 지움 (다음 아이가 섞이지 않게) */
  async logout(){ if(!this.on()) return {ok:1}; const ok=await this.save(true); if(!ok) return {err:"save"};
    const a=this.get(); this.remember(a);
    try{ Move.keys().forEach(k=>{ if(!Move.SKIP.test(k) && !/^hyeng_acct_list$/.test(k)) try{ localStorage.removeItem(k); }catch(e){} }); }catch(e){}
    ["hyeng_me","hyeng_kid","hyeng_tag",AK,AS].forEach(k=>{ try{ localStorage.removeItem(k); }catch(e){} }); try{ localStorage.setItem("hyeng_nick",""); }catch(e){}   // (v727) 태그도 — 다음 아이 기록이 이 아이 태그로 가지 않게
    setTimeout(()=>location.reload(), 300); return {ok:1}; },
  kicked(){ const a=this.get(); jset(AK, null); jset(AS, null); ["hyeng_me","hyeng_tag"].forEach(k=>{ try{ localStorage.removeItem(k); }catch(e){} }); try{ localStorage.setItem("hyeng_nick",""); }catch(e){}   /* (v727) 선생님이 기기를 뺐으면 이 기기는 그 아이가 아님 — 기록은 두고 이름·명단 아이·태그만 */ try{ hyToast("🔐 이 기기는 로그인이 풀렸어요"+(a?" ("+esc(a.n)+")":"")+" — 다시 로그인해요"); }catch(e){} },
  /* 게임 이름 바꾸기 — 같은 반에 있는 이름은 서버가 막음 */
  async rename(nm){ const a=this.get(); if(!a) return ""; const r=await this.call({type:"acctName", uid:a.uid, dev:a.dk, ds:a.ds, name:nm});
    if(r && r.ok){ jset(AK, Object.assign({}, a, {n:r.n})); return ""; } if(r && r.err==="dup") return "같은 반에 「"+nm+"」 친구가 있어요 — 다른 이름을 골라 줘 (💎 는 그대로예요)";
    if(r && r.err==="bad") return "「선생님 · 관리자」 같은 이름은 쓸 수 없어요"; return "지금은 이름을 못 바꿔요 — 인터넷을 확인해요"; },
  /* 계정을 켰는지 (선생님) — /hy/acon */
  async enabled(){ try{ await FB.ready(); const v=await FB.get("/hy/acon"); return !!(v && v.on); }catch(e){ return false; } },
  async boot(){ if(!this.usable()){ Lock.set(false); return; } if(this.on()){ Lock.set(false); this.check(); return; }
    let skip=false; try{ skip=sessionStorage.getItem(SKIPK)==="1"; }catch(e){}
    const on=await this.enabled(); this.acon=on; Lock.set(on); if(!on) return; Chip.draw(); if(skip) return; UI.open(this.list().length ? "who" : "home"); },
  /* (v726) ①-c 게스트 = 계정 켜짐 · 아이 개인 기기(공용 패드·선생님 기기 아님) · 로그인 안 함 → My Town · 수업 게임 · 상점 잠김 (Adventure · Daily 30 은 그대로) */
  locked(){ return !!this.acon && !this.on() && this.usable(); },
  guestNo(){ let n=""; try{ n=localStorage.getItem("hyeng_acct_gn")||""; if(!/^\d{4}$/.test(n)){ n=String(1000+Math.floor(Math.random()*9000)); localStorage.setItem("hyeng_acct_gn", n); } }catch(e){ n="0000"; } return n; }
};
window.Acct=Acct;

/* ───────────── 첫 화면 칩 (내 얼굴 · 이름 / 🔑 로그인) ───────────── */
const Chip={ draw(){ const sc=$$("scStart"); if(!sc) return; let c=$$("acChip"); if(!Acct.on() && !Acct.usable()){ if(c) c.remove(); return; } if(!c){ c=document.createElement("button"); c.id="acChip"; c.type="button"; sc.appendChild(c); c.addEventListener("click", ()=>{ tone(660,.06); if(Acct.on()) UI.me(); else UI.open(Acct.list().length ? "who" : "id"); }); }
  const a=Acct.get(); c.className=a?"acChip in":"acChip"; c.innerHTML=a ? '<i style="'+face(myChar())+'"></i><b>'+esc(a.n)+'</b><span>▾</span>' : '<i class="k">🔑</i><b class="g">로그인<small>🙋 게스트 '+Acct.guestNo()+'</small></b>'; Lock.paint(); } };
/* (v726) ①-c 게스트 잠금 — 카드·단추에 🔒 · 누르면 로그인 화면 · My Town(house.html)은 hyeng_acct_glock 을 보고 첫 화면으로 */
const Lock={ NM:{town:"🏡 My Town은", join:"🎮 수업 게임은", shop:"💎 상점은"},
  set(on){ try{ if(on && Acct.locked()) localStorage.setItem("hyeng_acct_glock","1"); else localStorage.removeItem("hyeng_acct_glock"); }catch(e){} this.paint(); },
  paint(){ const L=Acct.locked(), sh=$$("btnShop");
    if(sh){ sh.classList.toggle("acLk", L); let b=sh.querySelector(".acLkB"); if(L && !b){ b=document.createElement("span"); b.className="acLkB"; b.textContent="🔒"; sh.appendChild(b); } else if(!L && b) b.remove(); }
    const j=document.querySelector('#selRule [data-v="join"]'); if(j){ if(!j.dataset.h0a) j.dataset.h0a=j.innerHTML; j.classList.toggle("acLkC", L);
      const h=L ? '<span class="townTag">🔒 로그인</span><b>🎮 수업 게임</b><small>로그인하면 열려요</small>' : j.dataset.h0a; if(j.innerHTML!==h) j.innerHTML=h; }
    try{ TownGate.card(); }catch(e){} },   // 🏡 My Town 카드는 TownGate.card 가 그림 (Acct.locked 보고 「🔒 로그인」)
  say(k){ try{ hyToast(k==="pick" ? "🙋 <b>로그인</b>하면 내 이름으로 해요" : "🔒 "+(this.NM[k]||"이건")+" <b>로그인</b>하면 열려요"); }catch(e){} UI.open(Acct.list().length ? "who" : "home"); },
  wrap(){ try{ const o=RaidJoin.open; if(o && !o._acLk){ RaidJoin.open=function(){ if(Acct.locked()) return Lock.say("join"); return o.apply(this, arguments); }; RaidJoin.open._acLk=1; } }catch(e){}
    try{ const o=ShopUI.open; if(o && !o._acLk){ ShopUI.open=function(){ if(Acct.locked()) return Lock.say("shop"); return o.apply(this, arguments); }; ShopUI.open._acLk=1; } }catch(e){}
    /* (v727) 「나는 누구?」 명단 고르기 — 계정이 켜진 개인 기기의 게스트가 명단에서 아무 아이나 골라 그 아이(주간 보스·선물·시험)가 되지 않게 → 로그인 */
    try{ const o=KidPick.open; if(o && !o._acLk){ KidPick.open=function(){ if(Acct.locked()) return Lock.say("pick"); return o.apply(this, arguments); }; KidPick.open._acLk=1; } }catch(e){} } };
window.AcctLock=Lock;

/* ───────────── 로그인 화면 (시안 v16 · 로고 포털) ───────────── */
const DM='<svg class="acDm" viewBox="0 0 60 80" aria-hidden="true"><path class="o" d="M30 2 Q35 33 57 40 Q35 47 30 78 Q25 47 3 40 Q25 33 30 2 Z"/><path class="b" d="M30 15 L45 40 L30 65 L15 40 Z"/><path class="cr" d="M30 18 L42 40 L30 62 L18 40 Z"/><path class="hi" d="M30 18 L42 40 L30 40 Z"/><path class="sh" d="M30 40 L18 40 L30 62 Z"/></svg>';
const LOGO='<div class="acLogo"><img class="lb" src="assets/ui/logo.webp" alt="HY ENG 워드 게이트 러너"><div class="acPg"></div><div class="acPs"></div><img class="lf" src="assets/ui/logo-front.webp" alt="" onerror="this.remove()"></div>';
const UI={
  el:null, cur:"", idv:"", code:"", busy:false, left:5, T:[], who:null, pollT:null,
  build(){ if(this.el) return this.el; const d=document.createElement("div"); d.id="acctUI"; d.setAttribute("role","dialog"); d.setAttribute("aria-label","로그인");
    const kb=["abcdefg","hijklmn","opqrstu","vwxyz"].map(r=>'<div>'+r.split("").map(c=>'<button type="button" data-l="'+c+'">'+c+'</button>').join("")+(r==="vwxyz"?'<button type="button" class="w" data-l="del">⌫ 지우기</button>':'')+'</div>').join("");
    const pk=[1,2,3,4,5,6,7,8,9].map(k=>'<button type="button" data-k="'+k+'"><span>'+k+'</span></button>').join("")+'<i class="nil" aria-hidden="true"></i><button type="button" data-k="0"><span>0</span></button><button type="button" class="g" data-k="del">⌫ 지우기</button>';
    d.innerHTML='<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
      +'<linearGradient id="acGold" x1="0" y1="0" x2=".6" y2="1"><stop offset="0" stop-color="#fff4a8"/><stop offset=".45" stop-color="#ffc93a"/><stop offset="1" stop-color="#b87400"/></linearGradient>'
      +'<linearGradient id="acOff" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a3d74"/><stop offset="1" stop-color="#1e1640"/></linearGradient>'
      +'<linearGradient id="acOn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1e0ff"/><stop offset=".45" stop-color="#a66bff"/><stop offset="1" stop-color="#4f1fb0"/></linearGradient>'
      +'<linearGradient id="acAu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#ffe79a"/><stop offset="1" stop-color="#ffb52e"/></linearGradient>'
      +'<linearGradient id="acBad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd0c8"/><stop offset=".5" stop-color="#ff5a4a"/><stop offset="1" stop-color="#a3161a"/></linearGradient></defs></svg>'
      +'<div class="acBg"></div><div class="acSpk" aria-hidden="true"><i style="left:12%;top:16%"></i><i style="left:84%;top:10%;--d:1.2s"></i><i style="left:76%;top:34%;--d:.6s"></i><i style="left:20%;top:44%;--d:1.8s"></i><i style="left:58%;top:6%;--d:2.4s"></i></div>'
      +'<div class="acIn">'
      /* 첫 화면 */
      +'<div class="acS" data-s="home"><div class="acTop end"><button type="button" class="acSlab sm" data-go="skip">✕ 닫기</button></div><div class="acFloat big">'+LOGO+'</div>'
      +'<div class="acCrew" aria-hidden="true"><div class="gr"></div><i class="c1" style="'+cheer("mage")+'"></i><i class="c5" style="'+cheer("cat")+'"></i><i class="c2" style="'+cheer("archer")+'"></i><i class="c4" style="'+cheer("wolf")+'"></i><i class="c3" style="'+cheer("hero")+'"></i></div>'
      +'<button type="button" class="acGold" data-go="id">🔑 로그인<small>내 기록이 어느 기기에서나 이어져요</small></button><button type="button" class="acSlab" data-go="skip">🙋 로그인 없이 해 보기</button></div>'
      /* 누가 할까요 */
      +'<div class="acS" data-s="who"><div class="acTop end"><button type="button" class="acSlab sm" data-go="skip">✕ 닫기</button></div><div class="acFloat sm"><img class="acSmall" src="assets/ui/logo.webp" alt="HY ENG"></div><div class="acBig acGt">누가 할까요?</div><div class="acPpl" id="acPpl"></div><div class="acHint">얼굴을 누르면 <b>비밀번호만</b> 눌러요</div><div class="grow"></div><div class="acRow"><button type="button" class="acSlab" data-go="id">＋ 다른 친구</button><button type="button" class="acSlab" data-go="skip">🙋 로그인 없이</button></div></div>'
      /* 아이디 */
      +'<div class="acS" data-s="id"><div class="acTop"><button type="button" class="acSlab sm" data-go="back">◀ 처음으로</button><span class="acStep"><b class="cur">아이디</b><i></i><b>비밀번호</b></span><span class="sp"></span></div><div class="acFloat sm"><img class="acSmall" src="assets/ui/logo.webp" alt="HY ENG"></div>'
      +'<div class="acPlate"><span class="lab">아이디</span><div class="acTyped" id="acIdT"></div></div><div class="acHint" id="acIdH">영어 소문자 3~8글자 · 잊었으면 <b>선생님께</b></div><div class="grow"></div><div class="acKb" id="acKb">'+kb+'</div><button type="button" class="acGold" id="acIdNext" disabled>다음 ▶</button></div>'
      /* 비밀번호 */
      +'<div class="acS" data-s="pw"><div class="acTop"><button type="button" class="acSlab sm" id="acPwBack" data-go="idk">◀ 아이디</button><span class="acWho"><i id="acPwFace"></i><b id="acPwName"></b></span><span class="sp"></span></div><div class="acFloat">'+LOGO+'</div>'
      +'<div class="acGems" id="acGems" aria-label="누른 숫자 0개">'+DM.repeat(6)+'</div><div class="acMsg" id="acMsg" aria-live="polite">비밀번호 6자리를 눌러요</div><div class="grow"></div><div class="acKeys" id="acKeys">'+pk+'</div><div class="acHint">잊어버렸어요 → <b>선생님께</b></div></div>'
      /* 승인 기다림 */
      +'<div class="acS" data-s="wait"><div class="acTop"><button type="button" class="acSlab sm" data-go="back">◀ 처음으로</button><span class="sp"></span></div><div class="acFloat dim">'+LOGO+'</div><div class="acBig acGt">선생님이<br>확인하고 있어요</div>'
      +'<div class="acHint">처음 쓰는 기기라서 <b>한 번만</b> 확인해요 · 확인되면 저절로 들어가요</div><div class="acSent">🔔 선생님 화면에 떴어요 · 선생님께 말해 줘요<span class="dots"><i></i><i></i><i></i></span></div><div class="grow"></div><button type="button" class="acGold" data-go="guest">🙋 그동안 게스트로 놀기<small>확인되면 알려 줄게요</small></button></div>'
      /* 이 기기 기록 맞아요? */
      +'<div class="acS" data-s="mine"><div class="acTop"><span class="sp"></span></div><div class="acFloat sm"><img class="acSmall" src="assets/ui/logo.webp" alt=""></div><div class="acBig acGt" style="font-size:24px">📦 이 기기에 있던 기록</div><div class="acHint" id="acMineQ"></div><div class="acCmp" id="acCmp"></div><div class="grow"></div><button type="button" class="acGold" data-mine="mine">✅ 네, 제 기록이에요</button><button type="button" class="acSlab" data-mine="other">🙅 동생 · 친구 거예요<small>지우지 않고 선생님께 맡겨요</small></button></div>'
      /* 어서 와 */
      +'<div class="acS wel" data-s="wel"><div class="acConf" aria-hidden="true">'+[8,18,29,40,52,63,74,85,93,35,68,12].map((x,i)=>'<b style="left:'+x+'%;--t:'+(i*.07).toFixed(2)+'s;--c:'+["#ffd54a","#b98cff","#7fe3ff","#ff8fb3","#9be07a"][i%5]+';--r:'+((i*37)%120-60)+'deg"></b>').join("")+'</div><div class="acFace"><span class="burst"></span><i id="acWelFace"></i></div><div class="acBig acGt" id="acWelT">어서 와!</div><div class="acStats" id="acWelS"></div><div class="acHint" id="acWelH">이 기기는 계속 로그인돼요</div><button type="button" class="acGold" data-go="done" style="width:auto;padding:10px 26px 8px">게임 시작 ▶</button></div>'
      /* 내 계정 (첫 화면 칩) */
      +'<div class="acS" data-s="me"><div class="acTop"><button type="button" class="acSlab sm" data-go="done">◀ 닫기</button><span class="sp"></span></div><div class="acFace sm"><i id="acMeFace"></i></div><div class="acBig acGt" id="acMeN"></div><div class="acCard" id="acMeC"></div><div class="grow"></div><button type="button" class="acHold" id="acOut"><span class="fill"></span>🚪 로그아웃 <small>2초 꾹 눌러요</small></button><div class="acHint" id="acOutH">로그아웃하면 이 기기 기록은 지워지고 서버에 그대로 있어요</div></div>'
      +'</div><div class="acFlash"></div>';
    document.body.appendChild(d); this.el=d; this.wire(); return d; },
  q(s){ return this.el.querySelector(s); },
  show(n){ const d=this.build(); const ORD={home:0,who:.5,id:1,wait:1.5,mine:1.6,pw:2,wel:3,me:0}; const dir=(ORD[n]||0)>=(ORD[this.cur]||0)?1:-1;
    d.querySelectorAll(".acS").forEach(s=>{ const on=s.dataset.s===n; if(on && this.cur!==n){ s.style.setProperty("--dx",(24*dir)+"px"); s.getBoundingClientRect(); } else if(s.classList.contains("on")) s.style.setProperty("--dx",(-24*dir)+"px"); s.classList.toggle("on", on); });
    this.cur=n; if(n==="id") this.drawId(); if(n==="pw") this.resetPw(); if(n==="who") this.drawWho(); },
  open(n){ if(!Acct.on() && !Acct.usable()) return; this.build(); document.body.classList.add("acOpen"); this.el.classList.add("on"); this.show(n||"home"); },
  close(){ if(!this.el) return; this.el.classList.remove("on","go"); document.body.classList.remove("acOpen"); this.T.forEach(clearTimeout); this.T=[]; },
  skip(){ try{ sessionStorage.setItem(SKIPK,"1"); }catch(e){} this.close(); Chip.draw(); },
  drawWho(){ const L=Acct.list(); $$("acPpl").innerHTML=L.map(x=>'<button type="button" data-who="'+esc(x.id)+'"><i style="'+face(x.c)+'"></i><b>'+esc(x.n)+'</b><small>'+esc(x.id)+'</small></button>').join(""); },
  drawId(){ const v=this.idv; $$("acIdT").innerHTML=(v ? v.split("").map((c,i)=>'<span class="acGt'+(i===v.length-1?' nw':'')+'">'+c+'</span>').join("") : '<span class="ph">toto</span>')+'<i class="caret"></i>'; $$("acIdNext").disabled=v.length<3; },
  resetPw(){ this.code=""; this.busy=false; const G=$$("acGems"); G.className="acGems"; this.q('[data-s="pw"] .acLogo').className="acLogo"; const M=$$("acMsg"); M.className="acMsg"; M.textContent="비밀번호 6자리를 눌러요";
    const B=$$("acPwBack"); if(this.fromWho){ B.dataset.go="back"; B.textContent="◀ 누가 할까요"; } else { B.dataset.go="idk"; B.textContent="◀ 아이디"; }
    const w=this.who||{n:this.idv}; $$("acPwName").textContent=w.n||this.idv; $$("acPwFace").setAttribute("style", face(w.c||myChar())); this.drawPw(); },
  drawPw(){ const G=$$("acGems"), n=this.code.length; [...G.children].forEach((g,i)=>g.classList.toggle("on", i<n)); this.q('[data-s="pw"] .acLogo').style.setProperty("--p", n); G.setAttribute("aria-label","누른 숫자 "+n+"개"); },
  msg(t, cls){ const M=$$("acMsg"); M.className="acMsg"+(cls?" "+cls:""); M.innerHTML=t; },
  bad(t){ const G=$$("acGems"), F=this.q('[data-s="pw"] .acLogo'); G.classList.add("bad"); F.classList.add("bad"); this.msg(t, "bad"); tone(220,.22,"square",.04); setTimeout(()=>tone(175,.28,"square",.04),120);
    this.T.push(setTimeout(()=>{ this.code=""; this.busy=false; G.className="acGems"; F.className="acLogo"; this.drawPw(); }, 1100)); },
  async press(k){ if(this.busy) return; if(k==="del"){ this.code=this.code.slice(0,-1); this.drawPw(); tone(330,.06); return; } 
    if(this.code.length>=6) return; this.code+=k; this.drawPw(); const g=$$("acGems").children[this.code.length-1]; g.classList.remove("pop"); void g.getBoundingClientRect(); g.classList.add("pop"); tone([523.25,587.33,659.25,698.46,783.99,880][this.code.length-1],.22);
    if(this.code.length<6) return; this.busy=true; this.msg("확인하는 중…");
    const r=await Acct.login(this.idv, this.code);
    if(r && r.ok && r.tok) return this.good();
    if(r && r.ok && r.wait){ this.pid=r.pid; this.show("wait"); this.poll(); return; }
    const e=r && r.err; this.bad(e==="pw" ? "앗, 다시 해 봐요 · "+(r.left|0)+"번 남았어요" : e==="lock" ? "잠깐 쉬었다가 해요 · "+Math.max(1,Math.ceil(((r.until||0)-Date.now())/60000))+"분 뒤에" : e==="tlock" ? "여러 번 틀려서 잠겼어요 · <b>선생님께</b> 풀어 달라고 해요"
      : e==="nosecret"||e==="fb" ? "지금은 로그인을 할 수 없어요 · <b>선생님께</b> 말해 줘요" : e==="noid" ? "아이디가 없어요 · 다시 확인해요" : e==="closed" ? "지금은 쓰지 않는 계정이에요 · 선생님께" : e==="wait" ? "잠깐 쉬었다가 다시 해요" : "인터넷을 확인하고 다시 해요");
    if(e==="noid") this.T.push(setTimeout(()=>this.show("id"), 1300)); },
  good(){ const G=$$("acGems"), F=this.q('[data-s="pw"] .acLogo'); G.classList.add("au"); this.msg("포털이 열려요!", "ok"); [1046.5,1318.5,1568].forEach((f,i)=>this.T.push(setTimeout(()=>tone(f,.4,"triangle",.06), i*90)));
    this.T.push(setTimeout(()=>{ F.classList.add("go"); this.el.classList.add("go"); }, 300));
    this.T.push(setTimeout(()=>this.enter(), 1450)); },
  async enter(){ const a=Acct.get(); this.el.classList.remove("go"); if(!a){ this.show("home"); return; } Acct.bind(a);
    const r=await Acct.first(); if(r && r.applied) return;   // 새로 켜짐
    $$("acWelFace").setAttribute("style", face(myChar())); $$("acWelT").textContent="어서 와, "+a.n+"!"; const s=Acct.sum();
    $$("acWelS").innerHTML='<span>💎 '+(s.g|0).toLocaleString()+'</span><span>⭐ Stage '+(s.st|0)+'</span><span>📖 '+(s.dx|0)+'</span>';
    $$("acWelH").textContent=r && r.err ? "⚠️ 서버에 아직 저장 못 했어요 — 인터넷이 되면 저절로 해요" : (r && r.merged ? "두 기록 중 더 많이 한 쪽으로 이어요 · 다른 쪽은 선생님께 맡겨 뒀어요" : "이 기기는 계속 로그인돼요");
    this.show("wel"); },
  poll(){ clearTimeout(this.pollT); const go=async()=>{ if(!this.pid) return; const r=await Acct.wait(this.idv, this.pid);
      if(r && r.ok && r.tok){ this.pid=null; Acct.won(r); Chip.draw();
        if(this.el && this.el.classList.contains("on")){ try{ hyToast("✅ 선생님이 확인했어요 — 로그인할게요"); }catch(e){} this.open("pw"); this.good(); }
        else { try{ hyToast("✅ 선생님이 확인했어요! 첫 화면으로 가면 내 기록으로 이어져요"); }catch(e){} Acct.pend=1; try{ if($$("scStart").classList.contains("on")){ Acct.pend=0; Acct.check(); } }catch(e){} }
        return; }
      if(r && r.err==="no"){ this.pid=null; try{ hyToast("🙅 이 기기는 로그인 안 돼요 — 선생님께 물어봐요"); }catch(e){} if(this.el.classList.contains("on")) this.show("home"); return; }
      if(r && r.err==="pid"){ this.pid=null; return; } this.pollT=setTimeout(go, 5000); }; this.pollT=setTimeout(go, 4000); },
  mine(a, L, S){ return new Promise(res=>{ this.open("mine"); $$("acMineQ").innerHTML='이게 <b>'+esc(a.n)+'</b> 기록이 맞아요?';
    const box=(t,x)=>'<div><b>'+t+'</b>'+(x ? '💎 '+(x.g|0).toLocaleString()+'<br>⭐ Stage '+(x.st|0)+'<br>📖 '+(x.dx|0) : '아직 비어 있어요<br>(처음 로그인)')+'</div>';
    $$("acCmp").innerHTML=box("📱 이 기기", L)+box("🔐 "+esc(a.n)+" 계정", S); this._mine=res; }); },
  me(){ const a=Acct.get(); if(!a) return; this.open("me"); $$("acMeFace").setAttribute("style", face(myChar())); $$("acMeN").textContent=a.n;
    const S=jget(AS,{}); $$("acMeC").innerHTML='<div><span>🪪 아이디</span><b class="mono">'+esc(a.id)+'</b></div><div><span>📱 이 기기</span><b>계속 로그인 ✅</b></div><div><span>☁️ 마지막 저장</span><b>'+(S.at ? new Date(S.at).toLocaleTimeString("ko-KR",{hour:"2-digit",minute:"2-digit"}) : "—")+'</b></div>'; },
  wire(){ const d=this.el;
    d.addEventListener("click", e=>{ const t=e.target;
      const go=t.closest("[data-go]"); if(go){ tone(660,.06); const g=go.dataset.go;
        if(g==="skip"||g==="guest"){ this.skip(); return; } if(g==="done"){ this.close(); Chip.draw(); return; }
        if(g==="back"){ this.pid=null; clearTimeout(this.pollT); this.show(Acct.list().length ? "who" : "home"); return; }
        if(g==="idk"){ this.show("id"); return; }
        if(g==="id"){ this.who=null; this.idv=""; } this.show(g); return; }
      const w=t.closest("[data-who]"); if(w){ tone(660,.06); const x=Acct.list().find(y=>y.id===w.dataset.who); this.who=x||null; this.idv=w.dataset.who; this.fromWho=true; this.show("pw"); return; }
      const l=t.closest("#acKb button"); if(l){ const v=l.dataset.l; if(v==="del") this.idv=this.idv.slice(0,-1); else if(this.idv.length<8) this.idv+=v; tone(v==="del"?330:520+this.idv.length*35,.07); this.drawId(); return; }
      if(t.closest("#acIdNext")){ if(this.idv.length>=3){ this.who=Acct.list().find(y=>y.id===this.idv)||null; this.fromWho=false; this.show("pw"); } return; }
      const k=t.closest("#acKeys button"); if(k){ this.press(k.dataset.k); return; }
      const m=t.closest("[data-mine]"); if(m && this._mine){ const f=this._mine; this._mine=null; f(m.dataset.mine); return; } });
    document.addEventListener("keydown", e=>{ if(!this.el || !this.el.classList.contains("on")) return; const tg=e.target; if(tg && /^(INPUT|TEXTAREA|SELECT)$/.test(tg.tagName)) return;
      if(this.cur==="id"){ if(/^[a-z]$/i.test(e.key) && this.idv.length<8){ this.idv+=e.key.toLowerCase(); this.drawId(); } else if(e.key==="Backspace"){ this.idv=this.idv.slice(0,-1); this.drawId(); } else if(e.key==="Enter" && this.idv.length>=3){ this.who=Acct.list().find(y=>y.id===this.idv)||null; this.fromWho=false; this.show("pw"); } }
      else if(this.cur==="pw"){ if(/^[0-9]$/.test(e.key)) this.press(e.key); else if(e.key==="Backspace") this.press("del"); } });
    /* 로그아웃 2초 꾹 */
    const ob=d.querySelector("#acOut"); let hT=null; const stop=()=>{ clearTimeout(hT); ob.classList.remove("hold"); };
    ob.addEventListener("pointerdown", ()=>{ ob.classList.add("hold"); hT=setTimeout(async ()=>{ ob.classList.remove("hold"); $$("acOutH").textContent="서버에 저장하는 중…"; const r=await Acct.logout(); if(r && r.err) $$("acOutH").textContent="⚠️ 서버에 저장이 안 돼서 로그아웃을 멈췄어요 — 인터넷을 확인해요"; }, 2000); });
    ["pointerup","pointerleave","pointercancel"].forEach(ev=>ob.addEventListener(ev, stop)); }
};

/* ───────────── 저장 시계 ───────────── */
function loop(){ setInterval(()=>{ if(Acct.on() && !document.hidden) Acct.save(); }, 60000);
  document.addEventListener("visibilitychange", ()=>{ if(document.hidden && Acct.on()) Acct.save(); else if(!document.hidden && Acct.on() && Acct.pend){ Acct.pend=0; Acct.check(); } });
  addEventListener("pagehide", ()=>{ if(Acct.on()) Acct.save(); });
  /* 첫 화면에 돌아오면 미뤄 둔 받아 오기 */
  try{ const sc=$$("scStart"); new MutationObserver(()=>{ if(sc.classList.contains("on")){ Chip.draw(); if(Acct.pend && Acct.on()){ Acct.pend=0; Acct.check(); } } }).observe(sc, {attributes:true, attributeFilter:["class"]}); }catch(e){} }

/* ───────────── 선생님: 👥 아이들 → 🔐 아이 계정 ───────────── */
const ROM={i:["g","kk","n","d","tt","r","m","b","pp","s","ss","","j","jj","ch","k","t","p","h"], v:["a","ae","ya","yae","eo","e","yeo","ye","o","wa","wae","oe","yo","u","wo","we","wi","yu","eu","ui","i"], f:["","k","k","k","n","n","n","t","l","k","m","l","l","l","p","l","m","p","p","t","t","ng","t","t","k","t","p","t"]};
function roman(s){ let o=""; for(const ch of String(s||"")){ const c=ch.charCodeAt(0)-0xAC00; if(c<0||c>11171){ if(/[a-z]/i.test(ch)) o+=ch.toLowerCase(); continue; } o+=ROM.i[Math.floor(c/588)]+ROM.v[Math.floor((c%588)/28)]+ROM.f[c%28]; } return o.replace(/[^a-z]/g,""); }
const AdmA={
  tk:"", L:null, busy:false, err:"", t:"", open:null, make:false, mk:{}, res:null, sure:"", note:"",
  card(tk){ this.tk=tk||this.tk; if(this.L===null && !this.busy) this.load(); if(!Object.keys(this.kids()).length && !this._rq){ this._rq=1; try{ HyBoss.refresh(true).then(()=>{ this._rq=0; this.paint(); }); }catch(e){ this._rq=0; } } return '<div class="adCard acAdm" id="acAdm">'+this.inner()+'</div>'; },
  load(){ if(this.busy) return; this.busy=true; Acct.call({type:"acctList", tk:this.tk}).then(r=>{ this.busy=false; if(r && r.ok){ this.L=r.list||[]; this.openUntil=r.open||0; this.err=""; this.fb=r.fb||null; if(r.fb && r.fb.code===200) this.onState=!!r.fb.on; } else this.err=(r && r.err)||"net"; this.paint(); }); },
  paint(){ const c=$$("acAdm"); if(c) c.innerHTML=this.inner(); },
  teams(){ let T={}; try{ T=HyBoss.teams()||{}; }catch(e){} return T; }, kids(){ try{ return HyBoss.kids()||{}; }catch(e){ return {}; } },
  tn(t){ try{ return HyBoss.tName(t); }catch(e){ return t||"반 없음"; } },
  inner(){ const T=this.teams(), ts=Object.keys(T), L=this.L||[];
    if(this.err) return '<h3>🔐 아이 계정 <small>로그인 · 비밀번호 · 기기</small></h3><p class="adSmall">'+(this.err==="type"||this.err==="nokey" ? "시트 서버를 v27 로 올려야 써요 (Code.gs 새 버전 배포)" : this.err==="badkey" ? "선생님 열쇠를 확인해요" : "불러오지 못했어요 · 인터넷 확인")+' <button class="mini" data-acx="re">다시</button></p>';
    if(this.L===null) return '<h3>🔐 아이 계정</h3><p class="adSmall">불러오는 중…</p>';
    if(!this.t || !T[this.t]) this.t=ts[0]||"";
    const live=L.filter(a=>a.st!=="closed"), pend=[]; live.forEach(a=>(a.pend||[]).forEach(p=>pend.push([a,p])));
    let h='<h3>🔐 아이 계정 <small>'+live.length+'명 · 로그인 · 비밀번호 · 기기</small>'+(pend.length?'<em class="adTabN">'+pend.length+'</em>':'')+'</h3>';
    if(this.note) h+='<p class="acNote">'+this.note+'</p>';
    const fb=this.fb; if(fb && fb.code!==200) h+='<p class="acNote bad">⚠️ '+AdmA.fbWhy(fb.code)+'</p>';
    if(pend.length) h+='<div class="acPend"><b>🔔 새 기기 승인 '+pend.length+'</b>'+pend.map(([a,p])=>'<div class="row"><span>'+esc(a.n)+' <small>'+esc(a.id)+' · '+esc(p.n)+' · '+new Date(p.at).toLocaleTimeString("ko-KR",{hour:"2-digit",minute:"2-digit"})+' · 지금 게스트로 하는 중</small></span><button class="mini go" data-acx="ap" data-u="'+a.uid+'" data-p="'+p.pid+'">✅ 승인</button><button class="mini" data-acx="no" data-u="'+a.uid+'" data-p="'+p.pid+'">🙅 아니에요</button></div>').join("")+'</div>';
    h+='<div class="acBar"><button class="mini'+(this.onState?' go':'')+'" data-acx="on">'+(this.onState===false?'▶ 계정 켜기 (아이 화면에 로그인이 보임)':this.onState?'🔐 계정 켜짐 · 끄기':'확인 중…')+'</button><button class="mini" data-acx="open">'+(this.openUntil>Date.now()?'⏳ 승인 없이 ~'+new Date(this.openUntil).toLocaleDateString("ko-KR",{month:"numeric",day:"numeric"})+' · 끄기':'🚪 처음 기기 승인 없이 3일')+'</button><button class="mini" data-acx="re">↻</button></div>';
    h+='<div class="acTabs">'+ts.map(t=>'<button class="mini'+(t===this.t?' go':'')+'" data-acx="t" data-t="'+esc(t)+'">'+esc(this.tn(t))+'</button>').join("")+'</div>';
    const mine=live.filter(a=>a.t===this.t);
    h+='<div class="acList">'+(mine.length ? mine.map(a=>this.row(a)).join("") : '<p class="adSmall">이 반은 아직 계정이 없어요 — 아래 「＋ 계정 만들기」</p>')+'</div>';
    h+='<div class="acBar"><button class="mini go" data-acx="mk">'+(this.make?'✕ 닫기':'＋ 계정 만들기 (반 명단에서)')+'</button><button class="mini" data-acx="slip">🖨 부모님께 로그인 쪽지</button></div>';
    if(this.make) h+=this.makeForm(L);
    if(this.res) h+='<div class="acRes">'+this.res+'</div>';
    return h; },
  fbWhy(c){ c=String(c); return c==="nosec" ? "시트 서버에 Firebase 열쇠(FB_SECRET)가 없어서 계정을 켤 수 없어요 — Apps Script ⚙ 프로젝트 설정 → 스크립트 속성에 FB_SECRET 을 넣어 주세요 (값은 아무에게도 보내지 마세요)"
      : c==="401" ? "시트 서버의 Firebase 열쇠(FB_SECRET)가 안 맞아요 — Firebase 콘솔의 데이터베이스 비밀번호를 다시 복사해 스크립트 속성 FB_SECRET 에 넣어 주세요"
      : "시트 서버가 Firebase 에 쓰지 못했어요 ("+c+") — 잠시 뒤 다시"; },
  row(a){ const st=a.tl?'<span class="st lock">🔒 선생님 풀기</span>':a.lock?'<span class="st lock">🔒 '+Math.ceil((a.lock-Date.now())/60000)+'분</span>':(a.pend||[]).length?'<span class="st wait">⏳ 승인</span>':(a.devs||[]).length?'<span class="st ok">✅ '+a.devs.length+'대</span>':'<span class="st none">아직 로그인 안 함</span>';
    const op=this.open===a.uid; let h='<div class="acR'+(op?' op':'')+'"><button class="acRh" data-acx="op" data-u="'+a.uid+'"><b>'+esc(a.n)+'</b><small class="mono">'+esc(a.id)+(a.tag?' · #'+esc(a.tag):'')+'</small>'+st+'</button>';
    if(op){ const tsel=Object.keys(this.teams()).map(t=>'<option value="'+esc(t)+'"'+(t===a.t?' selected':'')+'>'+esc(this.tn(t))+'</option>').join("");
      h+='<div class="acD"><div class="kv"><span>🪪 아이디</span><input id="acE_id" value="'+esc(a.id)+'" maxlength="8" autocapitalize="off" autocomplete="off" spellcheck="false"><button class="mini" data-acx="eid" data-u="'+a.uid+'">바꾸기</button></div>'
        +'<div class="kv"><span>✏️ 게임 이름</span><input id="acE_n" value="'+esc(a.n)+'" maxlength="8"><button class="mini" data-acx="en" data-u="'+a.uid+'">바꾸기</button></div>'
        +'<div class="kv"><span>🏫 반</span><select id="acE_t">'+tsel+'</select><button class="mini" data-acx="et" data-u="'+a.uid+'">옮기기</button></div>'
        +'<div class="kv"><span>🔑 비밀번호 · '+(a.pk==="바꿈"?"바꿈":"처음(생일)")+'</span><input id="acE_pw" inputmode="numeric" maxlength="6" placeholder="새 6자리"><button class="mini" data-acx="pw" data-u="'+a.uid+'">새로</button><button class="mini" data-acx="pwb" data-u="'+a.uid+'">생일로 되돌리기</button></div>'
        +((a.tl||a.lock)?'<div class="kv"><span>🔒 잠김</span><button class="mini go" data-acx="ul" data-u="'+a.uid+'">잠금 풀기</button></div>':'')
        +'<div class="kv col"><span>📱 기기 '+(a.devs||[]).length+'대</span>'+((a.devs||[]).map(x=>'<div class="dv">'+esc(x.n)+' <small>'+new Date(x.u||x.at).toLocaleDateString("ko-KR",{month:"numeric",day:"numeric"})+'</small><button class="mini" data-acx="dd" data-u="'+a.uid+'" data-d="'+esc(x.dk)+'">내보내기</button></div>').join("")||'<small>없음</small>')+'</div>'
        +'<div class="kv"><span>🎓 졸업 · 그만둠</span><button class="mini'+(this.sure===a.uid?' warn':'')+'" data-acx="cl" data-u="'+a.uid+'">'+(this.sure===a.uid?'한 번 더 누르면 닫아요':'계정 닫기')+'</button></div></div>'; }
    return h+'</div>'; },
  makeForm(L){ const K=this.kids(), have={}; L.forEach(a=>{ if(a.rid && a.st!=="closed") have[a.rid]=1; });
    const ks=Object.keys(K).filter(k=>(K[k].t||"")===this.t && !have[k] && !K[k].nw);
    if(!ks.length) return '<p class="adSmall">이 반 명단의 아이는 모두 계정이 있어요 (명단에 없는 아이는 👥 명단에 먼저 넣어요)</p>';
    return '<div class="acMk"><p class="adSmall">아이디 = 영어 소문자 3~8글자(겹치면 철자를 다르게) · 생일 = 6자리(예: 2015년 3월 9일 → 150309) — 생일이 처음 비밀번호예요 · 화면엔 「생일」이라고 안 나와요</p>'
      +ks.map(k=>{ const n=String(HyBoss.plainN ? HyBoss.plainN(K[k].n) : K[k].n), sug=this.mk[k] ? this.mk[k].id : roman(n.length>=3 ? n.slice(1) : n).slice(0,8);
        return '<div class="kv"><span>'+esc(n)+'</span><input data-mki="'+esc(k)+'" value="'+esc(sug)+'" maxlength="8" autocapitalize="off" autocomplete="off" spellcheck="false" placeholder="아이디"><input data-mkb="'+esc(k)+'" value="'+esc(this.mk[k]?this.mk[k].bd:"")+'" inputmode="numeric" maxlength="6" placeholder="생일 6자리" type="password"></div>'; }).join("")
      +'<button class="mini go" data-acx="mkgo">계정 만들기</button></div>'; },
  async act(a, b){ const u=b.dataset.u, P={uid:u, tk:this.tk}; let r=null;
    const done=(rr, ok)=>{ if(rr && rr.ok){ this.note=ok; this.load(); } else { this.note="⚠️ "+({badid:"아이디는 영어 소문자 3~8글자예요",dupid:"이미 있는 아이디예요",dupname:"같은 반에 같은 이름이 있어요",badname:"이 이름은 쓸 수 없어요",badpw:"쉬운 번호(같은 숫자·123456)는 안 돼요",fb:"시트 서버가 Firebase 에 쓰지 못했어요 (FB_SECRET 확인)"}[rr&&rr.err]||"안 됐어요 ("+((rr&&rr.err)||"인터넷")+")"); this.paint(); } };
    if(a==="re"){ this.L=null; this.err=""; this.note=""; this.paint(); this.load(); return; }
    if(a==="t"){ this.t=b.dataset.t; this.open=null; this.res=null; this.paint(); return; }
    if(a==="op"){ this.open=this.open===u?null:u; this.sure=""; this.paint(); return; }
    if(a==="mk"){ this.make=!this.make; this.res=null; this.paint(); return; }
    if(a==="ap"||a==="no"){ r=await Acct.call(Object.assign(P, {type:"acctApprove", pid:b.dataset.p, yes:a==="ap"?1:0})); return done(r, a==="ap"?"✅ 승인했어요 — 아이 화면이 저절로 들어가요":"🙅 그 기기는 막았어요"); }
    if(a==="on"){ const on=this.onState===false; r=await Acct.call({type:"acctOn", tk:this.tk, on:on?1:0}); if(r && r.ok) this.onState=on; else if(r && r.err==="fb"){ this.fb={code:r.why}; this.note="⚠️ 계정을 "+(on?"켜지":"끄지")+" 못했어요"; this.paint(); return; } return done(r, on?"🔐 계정을 켰어요 — 아이들 첫 화면에 로그인이 보여요":"계정을 껐어요 — 아이 화면은 예전처럼"); }
    if(a==="open"){ r=await Acct.call({type:"acctOpen", tk:this.tk, days:this.openUntil>Date.now()?0:3}); return done(r, this.openUntil>Date.now()?"승인 없이 기간을 끝냈어요":"3일 동안 처음 기기도 승인 없이 들어가요 (옮겨 가는 주에)"); }
    if(a==="eid"){ r=await Acct.call(Object.assign(P, {type:"acctEdit", id:($$("acE_id")||{}).value})); return done(r, "아이디를 바꿨어요 — 부모님께 새 쪽지를"); }
    if(a==="en"){ r=await Acct.call(Object.assign(P, {type:"acctEdit", n:($$("acE_n")||{}).value})); return done(r, "게임 이름을 바꿨어요"); }
    if(a==="et"){ r=await Acct.call(Object.assign(P, {type:"acctEdit", t:($$("acE_t")||{}).value})); return done(r, "반을 옮겼어요"); }
    if(a==="pw"){ r=await Acct.call(Object.assign(P, {type:"acctPw", pw:String(($$("acE_pw")||{}).value||"").replace(/\D/g,"")})); return done(r, "새 비밀번호로 바꿨어요"); }
    if(a==="pwb"){ r=await Acct.call(Object.assign(P, {type:"acctPw", birth:1})); return done(r, "처음 비밀번호(생일)로 되돌렸어요"); }
    if(a==="ul"){ r=await Acct.call(Object.assign(P, {type:"acctUnlock"})); return done(r, "잠금을 풀었어요"); }
    if(a==="dd"){ r=await Acct.call(Object.assign(P, {type:"acctDev", dk:b.dataset.d})); return done(r, "그 기기를 내보냈어요 — 늦어도 7일 안에 로그인이 풀려요"); }
    if(a==="cl"){ if(this.sure!==u){ this.sure=u; this.paint(); return; } this.sure=""; r=await Acct.call(Object.assign(P, {type:"acctClose"})); this.open=null; return done(r, "계정을 닫았어요 (기록은 서버에 남아요)"); }
    if(a==="mkgo"){ const list=[]; document.querySelectorAll("#acAdm [data-mki]").forEach(i=>{ const k=i.dataset.mki, bd=(document.querySelector('#acAdm [data-mkb="'+k+'"]')||{}).value||"", K=this.kids()[k]; this.mk[k]={id:i.value, bd};
        if(K && i.value.trim() && bd.trim()) list.push({rid:k, n:HyBoss.plainN ? HyBoss.plainN(K.n) : K.n, t:K.t||"", id:i.value.trim().toLowerCase(), bd:bd.replace(/\D/g,"")}); });
      if(!list.length){ this.note="⚠️ 아이디와 생일을 적은 아이가 없어요"; this.paint(); return; }
      r=await Acct.call({type:"acctMake", tk:this.tk, list}); if(!r || !r.ok){ this.note="⚠️ 만들지 못했어요 ("+((r&&r.err)||"인터넷")+")"; this.paint(); return; }
      const E={badid:"아이디 모양(영어 소문자 3~8)",dupid:"이미 있는 아이디",dupname:"같은 반에 같은 이름",duprid:"이미 계정 있음",badbd:"생일 6자리 확인",badname:"쓸 수 없는 이름"};
      this.res='<b>만든 계정 '+(r.made|0)+'개</b>'+(r.res||[]).map(x=>'<div>'+(x.ok?'✅':'⚠️')+' '+esc(x.n)+' <span class="mono">'+esc(x.id)+'</span> '+(x.ok?((x.sameBirth||[]).length?'<em>같은 반에 생일이 같은 친구('+esc(x.sameBirth.join(", "))+') → 한 명은 🔑 새 6자리로</em>':''):esc(E[x.err]||x.err))+'</div>').join("");
      (r.res||[]).forEach(x=>{ if(x.ok) Object.keys(this.mk).forEach(k=>{ if(this.mk[k].id===x.id) delete this.mk[k]; }); }); this.load(); return; }
    if(a==="slip"){ this.print(); return; } },
  print(){ const L=(this.L||[]).filter(a=>a.st!=="closed" && a.t===this.t); if(!L.length){ this.note="이 반은 계정이 없어요"; this.paint(); return; }
    const w=window.open("", "_blank"); if(!w){ this.note="⚠️ 새 창이 막혔어요 — 팝업을 허용해 주세요"; this.paint(); return; }
    w.document.write('<!doctype html><meta charset="utf-8"><title>HY ENG 로그인 쪽지 · '+esc(this.tn(this.t))+'</title><style>body{font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic",sans-serif;margin:12mm}.g{display:grid;grid-template-columns:1fr 1fr;gap:6mm}.s{border:2px dashed #b8902e;border-radius:4mm;padding:5mm;break-inside:avoid}.s img{width:45mm}.s b.id{display:block;font-size:22pt;letter-spacing:1px;margin:2mm 0;font-family:monospace}.s p{margin:1mm 0;font-size:10.5pt;color:#333}</style><div class="g">'
      +L.map(a=>'<div class="s"><img src="'+location.href.replace(/[^/]*$/,"")+'assets/ui/logo.webp"><p><b>'+esc(a.n)+'</b> · '+esc(this.tn(a.t))+'</p><p>아이디</p><b class="id">'+esc(a.id)+'</b><p>비밀번호: 처음엔 <b>아이 생일 6자리</b> (예: 2015년 3월 9일 → 150309)</p><p>처음 쓰는 기기는 선생님이 한 번 확인해요 · 집 기기는 처음 한 번만 넣어 주세요</p></div>').join("")
      +'</div><script>setTimeout(()=>print(),400)<\/script>'); w.document.close(); }
};
document.addEventListener("click", e=>{ const b=e.target.closest && e.target.closest("#acAdm [data-acx]"); if(!b) return; e.preventDefault(); try{ SFX.click(); }catch(er){} AdmA.act(b.dataset.acx, b); });
window.AcctAdm={ card:tk=>{ if(AdmA.onState===undefined){ AdmA.onState=null; Acct.enabled().then(v=>{ AdmA.onState=v; AdmA.paint(); }); } return AdmA.card(tk); }, roman };

/* ───────────── 켜기 ───────────── */
function start(){ try{ const why=sessionStorage.getItem("hyeng_acct_why"); if(why){ sessionStorage.removeItem("hyeng_acct_why"); const a=Acct.get();
      const t={load:"☁️ "+(a?esc(a.n):"")+" 기록을 받아 왔어요", merge:"두 기록 중 더 많이 한 쪽으로 이어요 · 다른 쪽은 선생님께 맡겨 뒀어요", other:"이 기기에 있던 기록은 선생님께 맡겨 뒀어요", pull:"다른 기기에서 한 기록을 받아 왔어요", conflict:"다른 기기에서 한 기록을 받아 왔어요 · 여기서 한 것은 선생님께 맡겨 뒀어요"}[why];
      if(t) setTimeout(()=>{ try{ hyToast(t); }catch(e){} }, 1200); } }catch(e){}
  Lock.wrap(); if(location.hash==="#acctlock"){ try{ history.replaceState(null, "", location.pathname+location.search); }catch(e){} setTimeout(()=>{ if(Acct.locked()) Lock.say("town"); }, 1400); }
  loop(); setTimeout(()=>{ Acct.boot().catch(e=>console.error(e)); }, 600); }
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
