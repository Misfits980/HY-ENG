/* ═════════ (v634) 🃏 컬러팡 그림 · 데이터 · 꾸밈 (mg-card.js 가 씀) — 카드 SVG · 뒷면 9가지 · 오늘의 미션 · CSS ═════════ */
window.CPA=(function(){
"use strict";
const INK="#3b2433", CREAM="#fff8ea";
const COL={r:"#ff5a5f",y:"#ffc83d",g:"#3fc46a",b:"#3ea2ff"}, KO={r:"빨강",y:"노랑",g:"초록",b:"파랑"}, CS=["r","y","g","b"];
const NUMF="Nunito,'Arial Rounded MT Bold','Helvetica Neue',Arial,sans-serif";
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* ══ 카드 그림 (SVG 150×216) ══ */
const SH={
 r:[['p','M50 90C18 70 6 46 14 28c9-18 30-18 36 0 6-18 27-18 36 0 8 18-4 42-36 62z']],
 y:[['p','M50 6c4 0 6 3 8 7l9 19 21 3c8 1 10 7 4 12L77 62l4 21c1 8-4 11-11 7L50 80 31 90c-7 4-12 1-11-7l4-21L9 47c-6-5-4-11 4-12l21-3 9-19c2-4 4-7 7-7z']],
 g:[['c',50,30,21],['c',28,56,21],['c',72,56,21],['c',50,60,20],['p','M45 70L41 95Q50 99 59 95L55 70z']],
 b:[['p','M50 5C40 26 18 44 18 64a32 32 0 0 0 64 0C82 44 60 26 50 5z']]};
function shp(c,fill,sw){ const one=(p,f,st)=>p[0]==='p'?'<path d="'+p[1]+'" fill="'+f+'"'+st+'/>':'<circle cx="'+p[1]+'" cy="'+p[2]+'" r="'+p[3]+'" fill="'+f+'"'+st+'/>';
  const P=SH[c]; if(!sw) return P.map(p=>one(p,fill,'')).join("");
  return P.map(p=>one(p,INK,' stroke="'+INK+'" stroke-width="'+sw+'" stroke-linejoin="round"')).join("")+P.map(p=>one(p,fill,'')).join(""); }
const icon=(c,x,y,sz,fill,sw)=>'<g transform="translate('+(x-sz/2)+' '+(y-sz/2)+') scale('+(sz/100)+')">'+shp(c,fill||"#fff",sw==null?10:sw)+'</g>';
const TX=(x,y,t,sz,fill,sw)=>'<text x="'+x+'" y="'+y+'" text-anchor="middle" font-family="'+NUMF+'" font-weight="900" font-size="'+sz+'" fill="'+fill+'" stroke="'+INK+'" stroke-width="'+sw+'" stroke-linejoin="round" paint-order="stroke">'+t+'</text>';
let UID=0;
function frameSVG(base,inner){ const id="cp"+(UID++);
  return '<defs><linearGradient id="'+id+'g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".10"/></linearGradient><clipPath id="'+id+'k"><rect x="11" y="11" width="128" height="194" rx="14"/></clipPath></defs>'
   +'<rect x="3" y="7" width="144" height="206" rx="20" fill="'+INK+'"/><rect x="3" y="3" width="144" height="206" rx="20" fill="'+CREAM+'" stroke="'+INK+'" stroke-width="4"/>'
   +'<g clip-path="url(#'+id+'k)"><rect x="11" y="11" width="128" height="194" fill="'+base+'"/>'+inner+'<rect x="11" y="11" width="128" height="194" fill="url(#'+id+'g)"/></g>'
   +'<rect x="11" y="11" width="128" height="194" rx="14" fill="none" stroke="'+INK+'" stroke-width="3"/>'; }
const WALL={}; function wall(c){ if(WALL[c]) return WALL[c]; let s='<g opacity=".16">'; for(let j=0;j<7;j++) for(let i=0;i<5;i++){ const x=8+i*34+(j%2)*17, y=14+j*32; s+='<g transform="rotate(-18 '+x+' '+y+')">'+icon(c,x,y,15,"#fff",0)+'</g>'; } return WALL[c]=s+'</g>'; }
function pips(n,y){ if(!n) return ""; const r1=Math.min(n,5), r2=n-r1; let s=""; const row=(k,yy)=>{ for(let i=0;i<k;i++) s+='<circle cx="'+(75+(i-(k-1)/2)*13)+'" cy="'+yy+'" r="4.6" fill="#fff" stroke="'+INK+'" stroke-width="2.4"/>'; }; if(r2){ row(r1,y-7); row(r2,y+7); } else row(r1,y); return s; }
const ACTG={
 skip:c=>'<circle cx="75" cy="100" r="40" fill="#fff" stroke="'+INK+'" stroke-width="7"/><path d="M50 125L100 75" stroke="'+INK+'" stroke-width="15" stroke-linecap="round"/><path d="M50 125L100 75" stroke="'+COL[c]+'" stroke-width="7" stroke-linecap="round"/>',
 rev:()=>'<g fill="#fff" stroke="'+INK+'" stroke-width="6" stroke-linejoin="round"><path d="M42 96a33 33 0 0 1 55-21l7-9 4 33-32-3 8-9a19 19 0 0 0-31 12z"/><path d="M108 104a33 33 0 0 1-55 21l-7 9-4-33 32 3-8 9a19 19 0 0 0 31-12z"/></g>',
 d2:()=>'<g stroke="'+INK+'" stroke-width="5.5"><rect x="38" y="62" width="44" height="60" rx="8" fill="#fff" transform="rotate(-14 60 92)"/><rect x="66" y="70" width="44" height="60" rx="8" fill="'+CREAM+'" transform="rotate(12 88 100)"/></g>'+TX(75,160,"+2",40,"#fff",7)};
const ACTC={skip:"⊘",rev:"⇄",d2:"+2"};
function cardSVG(c,v,w,bk){ const W=w||150, H=Math.round(W*216/150), hd='<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+H+'" viewBox="0 0 150 216">';
  if(v==="back") return hd+backSVG(bk)+'</svg>';
  if(v==="wild"||v==="wild4") return hd+frameSVG("#fff",'<path d="M11 11H75V108H11z" fill="#ff5a5f"/><path d="M75 11H139V108H75z" fill="#ffc83d"/><path d="M11 108H75V205H11z" fill="#3ea2ff"/><path d="M75 108H139V205H75z" fill="#3fc46a"/>'
      +'<g opacity=".22">'+icon("r",36,40,30,"#fff",0)+icon("y",114,40,30,"#fff",0)+icon("b",36,178,30,"#fff",0)+icon("g",114,178,30,"#fff",0)+'</g><circle cx="75" cy="108" r="44" fill="'+CREAM+'" stroke="'+INK+'" stroke-width="6"/>'
      +(v==="wild"? icon("r",58,92,30,COL.r)+icon("y",92,92,30,COL.y)+icon("b",58,125,30,COL.b)+icon("g",92,125,30,COL.g)
        : icon("r",47,82,20,COL.r)+icon("y",103,82,20,COL.y)+icon("b",47,136,20,COL.b)+icon("g",103,136,20,COL.g)+TX(75,126,"+4",46,"#fff",8)))
      +(v==="wild4"?TX(27,37,"+4",20,"#fff",4.5)+'<g transform="rotate(180 75 108)">'+TX(27,37,"+4",20,"#fff",4.5)+'</g>':'')+'</svg>';
  const num=typeof v==="number", lab=num?v:ACTC[v], cn='<g>'+TX(27,37,lab,22,"#fff",4.5)+icon(c,27,51,15,"#fff",9)+'</g>';
  return hd+frameSVG(COL[c], wall(c)+(num? icon(c,75,100,118,"#fff",9)+TX(75,126,v,66,COL[c],8)+pips(v,180) : ACTG[v](c)))+cn+'<g transform="rotate(180 75 108)">'+cn+'</g></svg>'; }
const icSVG=(c,sz)=>'<svg width="'+sz+'" height="'+sz+'" viewBox="0 0 100 100">'+shp(c,"#fff",10)+'</svg>';

/* ══ 규칙 ══ */
function mkDeck(){ const d=[]; let id=0; CS.forEach(c=>{ d.push({c,v:0,id:id++}); for(let n=1;n<=9;n++){ d.push({c,v:n,id:id++}); d.push({c,v:n,id:id++}); } ["skip","rev","d2"].forEach(v=>{ d.push({c,v,id:id++}); d.push({c,v,id:id++}); }); });
  for(let i=0;i<4;i++){ d.push({c:null,v:"wild",id:id++}); d.push({c:null,v:"wild4",id:id++}); } return d; }
const isW=k=>k.v==="wild"||k.v==="wild4";
const okCard=(k,top,cur)=>isW(k) || k.c===cur || (!isW(top) && k.v===top.v);
const shuffle=a=>{ for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; };
const josa=(w,a,b)=>{ const c=String(w||"").charCodeAt(String(w||"").length-1); return w+((c>=0xAC00 && c<=0xD7A3 && (c-0xAC00)%28)?a:b); };
const kname=k=>k.v==="wild"?"🌈 무지개":k.v==="wild4"?"🌈 +4":k.v==="skip"?KO[k.c]+" 건너뛰기":k.v==="rev"?KO[k.c]+" 방향 바꾸기":k.v==="d2"?KO[k.c]+" +2":KO[k.c]+" "+k.v;
const ORDV=v=>typeof v==="number"?v:{skip:10,rev:11,d2:12,wild:13,wild4:14}[v];
const LEAGUE=[["🥉","브론즈",0],["🥈","실버",5],["🥇","골드",15],["💎","다이아",30],["👑","챔피언",60]];
function league(w){ w=w|0; let i=0; while(i<LEAGUE.length-1 && w>=LEAGUE[i+1][2]) i++; const L=LEAGUE[i], N=LEAGUE[i+1]; return {ic:L[0], nm:L[1], next:N?N[0]:"", p:N?(w-L[2])/(N[2]-L[2]):1, left:N?N[2]-w:0}; }
const BOTS=[
 {nm:"토리",av:{skin:1,hair:"long",hc:2,style:"dress",top:6,pc:0,sc:1,hat:"none",acc:"ribbon",expr:"smile"}},
 {nm:"모모",av:{skin:0,hair:"spiky",hc:0,style:"hoodie",top:3,pc:1,sc:3,hat:"cap",acc:"none",expr:"grin"}},
 {nm:"별이",av:{skin:2,hair:"pigtails",hc:4,style:"overalls",top:2,pc:2,sc:4,hat:"beanie",acc:"glasses",expr:"cat"}},
 {nm:"하루",av:{skin:3,hair:"bun",hc:5,style:"tee",top:4,pc:3,sc:5,hat:"none",acc:"flower",expr:"wink"}},
 {nm:"콩이",av:{skin:0,hair:"short",hc:3,style:"overalls",top:0,pc:4,sc:2,hat:"straw",acc:"backpack",expr:"cool"}}];
const EMOS=["😆","😮","😱","😝","👍","🎉"], EMO_X={"😆":"grin","😮":"wow","😱":"wow","😝":"wink","👍":"wink","🎉":"grin"};

/* ══ (v634) 🎴 카드 뒷면 모으기 — 이기기·판 수·미션·연승·같이 하기로 열림 · 고른 뒷면 = 내 뽑기 더미 · 같이 하기면 친구 화면의 내 손 카드 ══ */
function pat(c, op, sz, fill, gap, rot){ gap=gap||34; let s='<g opacity="'+op+'">'; for(let j=0;j<8;j++) for(let i=0;i<6;i++){ const x=6+i*gap+(j%2)*gap/2, y=10+j*gap*.92; s+='<g transform="rotate('+(rot||-18)+' '+x+' '+y+')">'+icon(c,x,y,sz,fill||"#fff",0)+'</g>'; } return s+'</g>'; }
const LOGO=(plate)=>'<g transform="rotate(-14 75 108)"><rect x="18" y="80" width="114" height="56" rx="16" fill="'+(plate||CREAM)+'" stroke="'+INK+'" stroke-width="5"/><text x="75" y="120" text-anchor="middle" font-family="Jua,\'Apple SD Gothic Neo\',\'Noto Sans KR\',sans-serif" font-weight="900" font-size="31" stroke="'+INK+'" stroke-width="6" paint-order="stroke" stroke-linejoin="round"><tspan fill="#ff5a5f">컬</tspan><tspan fill="#ffc83d">러</tspan><tspan fill="#3fc46a">팡</tspan><tspan fill="#3ea2ff">!</tspan></text></g>';
const STAR='M0 -10l3 7 8 1-6 5 2 8-7-4-7 4 2-8-6-5 8-1z';
const BACKS=[
 {k:"base",   nm:"컬러팡",   bg:"#4a2f5f", art:()=>["r","y","g","b"].map((k,i)=>'<g opacity=".2">'+icon(k,35+(i%2)*80,45+Math.floor(i/2)*126,40,"#fff",0)+'</g>').join("")},
 {k:"night",  nm:"별밤",     bg:"#1d2a5c", need:["win",1,"1번 이기기"], art:()=>{ let s='<circle cx="112" cy="40" r="17" fill="#ffe9a8"/><circle cx="119" cy="34" r="15" fill="#1d2a5c"/>'; [[30,30,1],[60,52,.7],[40,170,.9],[118,175,.8],[95,150,.6],[24,95,.6],[128,100,.7],[70,190,.5],[55,20,.5]].forEach(([x,y,k])=>s+='<path d="'+STAR+'" transform="translate('+x+' '+y+') scale('+k+')" fill="#fff6c4"/>'); return s; }},
 {k:"candy",  nm:"사탕",     bg:"#ff8fb8", need:["play",5,"5판 하기"], art:()=>{ let s='<g opacity=".38">'; for(let i=-6;i<12;i++) s+='<rect x="'+(i*22)+'" y="-20" width="10" height="280" fill="#fff" transform="rotate(30 75 108)"/>'; s+='</g>'; [[36,40,"#7ee0ff"],[112,58,"#ffe14d"],[40,168,"#8be38b"],[110,176,"#b98cff"]].forEach(([x,y,c])=>s+='<circle cx="'+x+'" cy="'+y+'" r="11" fill="'+c+'" stroke="'+INK+'" stroke-width="3"/>'); return s; }},
 {k:"sea",    nm:"바다",     bg:"#2f8fd8", need:["win",3,"3번 이기기"], art:()=>{ let s=''; for(let j=0;j<7;j++){ const y=22+j*30; s+='<path d="M0 '+y+' q12 -9 24 0 t24 0 t24 0 t24 0 t24 0 t24 0 t24 0" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="4" stroke-linecap="round"/>'; } return s+pat("b",.18,16,"#fff",44,0); }},
 {k:"clover", nm:"클로버 숲", bg:"#2fa860", need:["ms",5,"미션 5개 깨기"], art:()=>pat("g",.24,20,"#fff",36)},
 {k:"fire",   nm:"불꽃",     bg:"#ff5a3d", need:["bs",3,"3연승"], art:()=>{ let s='<rect x="0" y="120" width="150" height="100" fill="#ffb02e" opacity=".55"/>'; [[25,200,1],[60,205,1.3],[100,200,1.1],[130,205,.9],[45,60,.6],[110,50,.7]].forEach(([x,y,k])=>s+='<path d="M0 0c-14-14-10-30 0-44 2 10 8 14 12 6 8 14 6 30-12 38z" transform="translate('+x+' '+y+') scale('+k+')" fill="#ffe14d" stroke="'+INK+'" stroke-width="3"/>'); return s; }},
 {k:"rainbow",nm:"무지개",   bg:"#fff", need:["win",10,"10번 이기기"], art:()=>{ const C=["#ff5a5f","#ff9f43","#ffc83d","#3fc46a","#3ea2ff","#7b5ea7"]; return '<g transform="rotate(-30 75 108)">'+C.map((c,i)=>'<rect x="-60" y="'+(-40+i*50)+'" width="280" height="50" fill="'+c+'"/>').join("")+'</g>'; }},
 {k:"friend", nm:"우정",     bg:"#ffb0a0", need:["co",3,"친구랑 3판"], art:()=>pat("r",.32,20,"#fff",36,10)},
 {k:"gold",   nm:"황금 왕관", bg:"#e0a520", need:["win",30,"30번 이기기"], art:()=>{ let s='<rect x="0" y="0" width="150" height="216" fill="#ffd36b" opacity=".35"/>'; [[30,34],[118,40],[30,182],[120,178]].forEach(([x,y])=>s+='<path d="M'+(x-16)+' '+(y+8)+'l4-18 8 9 4-13 4 13 8-9 4 18z" fill="#fff6c4" stroke="'+INK+'" stroke-width="3" stroke-linejoin="round"/>'); [[75,30],[20,108],[130,108],[75,196]].forEach(([x,y])=>s+='<path d="'+STAR+'" transform="translate('+x+' '+y+') scale(.8)" fill="#fff"/>'); return s; }}];
const BACK={}; BACKS.forEach(b=>BACK[b.k]=b);
function backSVG(bk){ const B=BACK[bk]||BACK.base; return frameSVG(B.bg, B.art()+LOGO()); }
function backVal(k, R){ const t=(R&&R.t&&R.t.card)||{}, b=(R&&R.b&&R.b.card)||{}; return k==="bs"?(b.bs|0):(t[k]|0); }
function backOpen(B, R){ return !B.need || backVal(B.need[0],R)>=B.need[1]; }

/* ══ (v634) 🎯 오늘의 카드 미션 — 하루 3개(날짜로 고름 · 모두 같은 미션) · 깨면 🪙 · 셋 다면 🎁 +🪙20 ══ */
const MISS=[
 {k:"games", t:"한 판 끝까지 하기",       n:1,  c:10},
 {k:"d2",    t:"+2 카드 2번 내기",        n:2,  c:15},
 {k:"wild",  t:"🌈 무지개 카드 2번 내기",  n:2,  c:15},
 {k:"skip",  t:"⊘ 건너뛰기 2번 내기",     n:2,  c:15},
 {k:"rev",   t:"⇄ 방향 바꾸기 2번",       n:2,  c:15},
 {k:"swap",  t:"같은 숫자로 색 바꾸기 3번", n:3,  c:15},
 {k:"win",   t:"🏆 1등 하기",             n:1,  c:25},
 {k:"one",   t:"☝️ 「한 장!」 2번 외치기", n:2,  c:15},
 {k:"cards", t:"카드 20장 내기",           n:20, c:15},
 {k:"w4",    t:"🌈+4 카드 내기",          n:1,  c:15},
 {k:"top2",  t:"2등 안에 들기",           n:1,  c:20}];
function missToday(day){ let h=0; for(const ch of String(day)) h=(h*31+ch.charCodeAt(0))>>>0; const L=MISS.slice(), out=[]; while(out.length<3){ h=(h*1103515245+12345)>>>0; const i=h%L.length; out.push(L.splice(i,1)[0]); } if(!out.some(m=>m.k==="games")) out[0]=MISS[0]; return out; }

function css(){ if(document.getElementById("cpCss")) return; const st=document.createElement("style"); st.id="cpCss"; st.textContent=`
#mgUI.cpOn .mgJoyH,#mgUI.cpOn .mgJoy{display:none!important}
#mgUI.cpOn .mgTop{z-index:6}
#mgUI.cpOn .mgX{background:rgba(42,30,40,.8);border:2px solid rgba(255,211,107,.7)}
#cpHud{position:absolute;inset:0;font-family:var(--kr);color:#3b2433;--ink:#3b2433;--cream:#fff8ea;--gold:#ffd36b;pointer-events:none}
#cpHud *{box-sizing:border-box}
#cpHud button{font-family:inherit;pointer-events:auto;cursor:pointer;-webkit-tap-highlight-color:transparent}
.cpTop{display:flex;align-items:center;justify-content:center;gap:8px;pointer-events:none}
.cpOrd{display:flex;align-items:center;gap:3px;background:rgba(42,30,40,.8);border:2px solid rgba(255,211,107,.7);border-radius:99px;padding:3px 8px;margin:0 auto}
.cpOrd i{width:24px;height:24px;border-radius:50%;border:2px solid #fff;font:15px/20px var(--kr);color:#fff;text-align:center;font-style:normal;text-shadow:0 1px 0 rgba(0,0,0,.4)}
.cpOrd i.on{outline:3px solid #ffe14d;outline-offset:1px;transform:scale(1.12)}
.cpOrd b{color:#ffe14d;font-size:13px}.cpOrd b.d{margin-left:4px;font-size:15px}
.cpCoin{background:rgba(42,30,40,.8);border:2px solid rgba(255,211,107,.7);border-radius:99px;color:#fff;font-size:14px;padding:5px 10px;white-space:nowrap}
.cpVig{position:absolute;inset:0;background:radial-gradient(ellipse 80% 70% at 50% 42%,transparent 55%,rgba(20,10,20,.42))}
.cpPlate{position:absolute;transform:translate(-50%,-100%);display:flex;flex-direction:column;align-items:center;gap:3px}
.cpPlate .nm{display:flex;align-items:center;gap:4px;background:rgba(42,30,40,.86);color:#fff;border:2px solid rgba(255,255,255,.5);border-radius:12px;padding:2px 7px 2px 5px;font-size:14px;white-space:nowrap}
.cpPlate .dot{width:10px;height:10px;border-radius:50%;border:2px solid #fff}
.cpPlate u{text-decoration:none;background:#fff;color:var(--ink);border-radius:8px;padding:0 5px;font-size:14px;margin-left:2px}
.cpPlate u.one{background:#ff5a5f;color:#fff}
.cpPlate.turn .nm{border-color:#ffe14d;box-shadow:0 0 0 2px #ffe14d,0 0 14px 4px rgba(255,225,77,.7)}
.cpPlate .think{display:none;gap:3px}.cpPlate.turn .think{display:flex}.cpPlate .think i{width:7px;height:7px;border-radius:50%;background:#ffe14d;animation:cpDot 1s infinite}.cpPlate .think i:nth-child(2){animation-delay:.15s}.cpPlate .think i:nth-child(3){animation-delay:.3s}
@keyframes cpDot{50%{transform:translateY(-4px);opacity:.5}}
.cpPlate .emo,.cpPor .emo{position:absolute;right:-30px;top:-32px;background:#fff;border:3px solid var(--ink);border-radius:16px 16px 16px 4px;font-size:22px;padding:0 5px;box-shadow:0 3px 0 var(--ink);opacity:0;transform:scale(.5);transition:all .18s}
.cpPor .emo{right:-26px;top:-22px}
.cpPlate .emo.on,.cpPor .emo.on{opacity:1;transform:scale(1)}
.cpPlate .one1{display:none;position:absolute;left:50%;top:-26px;transform:translateX(-50%) rotate(-6deg);background:#ff5a5f;color:#fff;border:3px solid var(--ink);border-radius:9px;font-size:13px;padding:0 6px;white-space:nowrap}
.cpPlate.o1 .one1{display:block}
.cpFeed{position:absolute;left:max(10px,env(safe-area-inset-left));top:calc(56px + env(safe-area-inset-top));display:flex;flex-direction:column;gap:4px;max-width:62%}
.cpFeed div{background:rgba(42,30,40,.82);color:#fff;border-left:4px solid var(--c);border-radius:8px;padding:3px 9px;font-size:14px;display:flex;align-items:center;gap:6px;animation:cpIn .25s}
.cpFeed div:nth-child(n+2){opacity:.72}.cpFeed div:nth-child(3){opacity:.5}
.cpFeed b{color:#ffe14d;font-weight:400}
#cpHud:not(.pad):not(.land) .cpFeed div:nth-child(n+2){display:none}
@keyframes cpIn{from{transform:translateX(-12px);opacity:0}}
.cpBan{position:absolute;left:0;right:0;top:calc(96px + env(safe-area-inset-top));display:flex;justify-content:center;opacity:0;transform:scale(.85);transition:all .2s}
.cpBan.on{opacity:1;transform:scale(1)}
.cpBan div{position:relative;background:linear-gradient(90deg,transparent,rgba(42,30,40,.92) 18%,rgba(42,30,40,.92) 82%,transparent);text-align:center;padding:6px 64px}
.cpBan .t{display:block;color:#ffe14d;font-size:28px;letter-spacing:2px;-webkit-text-stroke:5px var(--ink);paint-order:stroke fill;text-shadow:0 0 16px rgba(255,225,77,.7)}
.cpBan small{display:block;color:#fff;font-size:14px}
.cpBan div:before,.cpBan div:after{content:"";position:absolute;left:12%;right:12%;height:2px;background:linear-gradient(90deg,transparent,#ffd36b,transparent)}.cpBan div:before{top:0}.cpBan div:after{bottom:0}
.cpHand{position:absolute;left:0;right:0;bottom:calc(128px + env(safe-area-inset-bottom));display:flex;justify-content:center;perspective:700px;pointer-events:auto}
.cpHand .in{display:flex;transform:rotateX(16deg);transform-origin:50% 100%}
.cpC{position:relative;flex:none;transform:translateY(calc(var(--y,0px) + var(--l,0px))) rotate(var(--r,0deg));transform-origin:50% 140%;filter:drop-shadow(0 6px 4px rgba(0,0,0,.35));transition:transform .15s}
.cpC svg{display:block}
.cpC.no{--l:8px;filter:saturate(.5) brightness(.86) drop-shadow(0 4px 3px rgba(0,0,0,.3))}
.cpC.ok{--l:-18px}.cpC.ok:before{content:"";position:absolute;inset:-4px -3px -2px;border-radius:16px;box-shadow:0 0 0 4px #ffe14d,0 0 18px 6px rgba(255,225,77,.85)}
.cpC.ok:active{--l:-40px}
.cpC.new{animation:cpNew .5s}
@keyframes cpNew{from{transform:translateY(-60px) scale(.8);opacity:0}}
.cpC.shk{animation:cpShk .3s}
@keyframes cpShk{25%{transform:translateX(-6px) rotate(var(--r))}75%{transform:translateX(6px) rotate(var(--r))}}
.cpCon{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:flex-end;gap:10px;padding:0 max(10px,env(safe-area-inset-right)) calc(10px + env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));background:linear-gradient(transparent,rgba(30,20,28,.92) 38%);pointer-events:none}
.cpPor{position:relative;flex:none;width:86px;height:86px;border-radius:18px;border:4px solid var(--gold);box-shadow:0 0 0 3px var(--ink),0 0 18px rgba(255,211,107,.5);background:#2b3a5a}
.cpPor canvas{width:100%;height:100%;border-radius:13px;display:block}
.cpPor .who{position:absolute;left:50%;bottom:-12px;transform:translateX(-50%);background:var(--ink);color:#fff;border:2px solid var(--gold);border-radius:99px;font-size:12px;padding:0 8px;white-space:nowrap;max-width:140px;overflow:hidden;text-overflow:ellipsis}
.cpMid{flex:1;min-width:0;display:flex;flex-direction:column;gap:6px;padding-bottom:4px}
.cpHint{background:#fff8ea;border:3px solid var(--ink);border-radius:13px;box-shadow:0 3px 0 var(--ink);font-size:16px;padding:4px 10px;display:flex;gap:5px;align-items:center;justify-content:center;white-space:nowrap;overflow:hidden}
.cpHint.my{background:#ffe14d}.cpHint.warn{background:#ff8a8e;color:#fff}
.cpHint b{font-weight:400;color:#c2410c}.cpHint.warn b{color:#fff}
.cpBar{height:13px;border-radius:99px;background:rgba(255,255,255,.18);border:2px solid rgba(255,255,255,.4);overflow:hidden}.cpBar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#ffe14d,#ffb02e);transition:width .25s linear}
.cpCmd{flex:none;display:grid;grid-template-columns:repeat(2,1fr);gap:6px}
.cpCmd button{width:60px;height:58px;border-radius:14px;border:3px solid var(--ink);background:linear-gradient(#fffaf0,#f1e2c4);box-shadow:0 3px 0 var(--ink);display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:12px;gap:1px;color:var(--ink);padding:0}
.cpCmd button span{font-size:22px;line-height:1}.cpCmd button b{font-weight:400;white-space:nowrap}
.cpCmd button:active{transform:translateY(3px);box-shadow:0 0 0 var(--ink)}
.cpCmd .one{background:linear-gradient(#ff8a8e,#ff4a50);color:#fff}
.cpCmd .off{background:#cdbfa8;color:#7a6a5e;filter:grayscale(.6)}
.cpCmd .glow{animation:cpGlow .8s infinite;box-shadow:0 3px 0 var(--ink),0 0 0 4px #ffe14d,0 0 18px 6px rgba(255,225,77,.7)}
@keyframes cpGlow{50%{transform:scale(1.07)}}
.cpEmo{position:absolute;right:max(12px,env(safe-area-inset-right));bottom:calc(150px + env(safe-area-inset-bottom));display:none;grid-template-columns:repeat(3,1fr);gap:6px;background:rgba(42,30,40,.9);border:2px solid var(--gold);border-radius:18px;padding:8px;pointer-events:auto}
.cpEmo.on{display:grid}.cpEmo button{width:48px;height:48px;border-radius:12px;border:0;background:#fff8ea;font-size:26px}
.cpPick{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 46%,rgba(30,18,40,.35),rgba(20,12,20,.8) 60%);pointer-events:auto}
.cpPick.on{display:flex}
.cpPick h3{margin:0 0 10px;font-size:26px;font-weight:400;color:#fff;-webkit-text-stroke:5px var(--ink);paint-order:stroke fill}
.cpPick p{margin:12px 0 0;font-size:15px;color:#fff;background:rgba(42,30,40,.8);border-radius:99px;padding:4px 12px}
.cpPick .no{margin-top:10px;border:3px solid var(--ink);border-radius:14px;background:#fff8ea;font-size:16px;padding:8px 16px;box-shadow:0 3px 0 var(--ink)}
.cpPick .wh{position:relative;width:min(300px,72vw,52vh);aspect-ratio:1}
.cpPick .wh>svg{position:absolute;inset:0;width:100%;height:100%;filter:drop-shadow(0 6px 0 #3b2433)}
.cpPick path{cursor:pointer}
.cpPick .lb{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;font-size:20px;color:#fff;-webkit-text-stroke:5px var(--ink);paint-order:stroke fill;cursor:pointer}
.cpPick .lb svg{display:block}
.cpPick .lb small{-webkit-text-stroke:0;font-size:11px;color:var(--ink);background:#ffe14d;border:2px solid var(--ink);border-radius:99px;padding:0 6px;margin-top:2px}
.cpPick .mid{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(-6deg);pointer-events:none}
.cpLoad{position:absolute;left:50%;top:45%;transform:translate(-50%,-50%);background:rgba(42,30,40,.88);color:#fff;border-radius:16px;padding:10px 18px;font-size:18px}
.cpEnd{position:absolute;inset:0;display:none;pointer-events:auto;overflow:auto}
.cpEnd.on{display:block}
.cpEnd .ed{position:fixed;inset:0;background:radial-gradient(ellipse at 50% 30%,rgba(30,20,28,.25),rgba(20,12,20,.8) 70%)}
.cpEnd .rays{position:fixed;left:50%;top:-80px;width:560px;height:560px;transform:translateX(-50%);border-radius:50%;background:repeating-conic-gradient(rgba(255,225,77,.22) 0 9deg,transparent 9deg 22deg);-webkit-mask:radial-gradient(circle,#000 20%,transparent 68%);mask:radial-gradient(circle,#000 20%,transparent 68%);animation:cpSpin 14s linear infinite}
@keyframes cpSpin{to{transform:translateX(-50%) rotate(360deg)}}
.cpEnd .eb{position:relative;display:flex;flex-direction:column;align-items:center;padding:calc(64px + env(safe-area-inset-top)) 14px 24px}
.cpEnd .emb{font-size:60px;line-height:1;letter-spacing:6px;color:#ffe14d;-webkit-text-stroke:8px var(--ink);paint-order:stroke fill;filter:drop-shadow(0 0 18px rgba(255,211,107,.85));animation:cpEmb .5s cubic-bezier(.2,1.6,.4,1)}
.cpEnd .emb.r2{color:#dfe8f5}.cpEnd .emb.r3{color:#f0b37a}.cpEnd .emb.r4{color:#cdbfd8;filter:none}
@keyframes cpEmb{from{transform:scale(2.2);opacity:0}}
.cpEnd .rib{margin-top:4px;background:#ff5a5f;color:#fff;border:3px solid var(--ink);border-radius:8px;padding:2px 16px;font-size:15px;box-shadow:0 3px 0 var(--ink);transform:rotate(-2deg)}
.cpEnd .sub{font-size:16px;color:#fff;margin-top:4px;text-shadow:0 2px 0 rgba(0,0,0,.4)}
.cpEnd .ec{width:min(360px,100%);margin-top:16px;background:var(--cream);border:4px solid var(--ink);border-radius:22px;box-shadow:0 5px 0 var(--ink);padding:12px;animation:cpUp .4s .15s both}
@keyframes cpUp{from{transform:translateY(30px);opacity:0}}
.cpEnd .rk{display:grid;grid-template-columns:28px 1fr auto;gap:4px 8px;align-items:center;font-size:16px}
.cpEnd .rk i{font-style:normal;font-size:18px;text-align:center}.cpEnd .rk span{display:flex;align-items:center;gap:6px;padding:1px 4px}.cpEnd .rk em{font-style:normal;font-size:13px;color:#7a6a5e}
.cpEnd .rk .me{background:#fff3b0;border-radius:8px}
.cpEnd .dt{width:12px;height:12px;border-radius:50%;border:2px solid var(--ink)}
.cpEnd .gr{margin-top:8px}.cpEnd .gr .t{font-size:14px;display:flex;justify-content:space-between;margin-bottom:3px}.cpEnd .gr .t em{font-style:normal;color:#7a6a5e;font-size:12px}
.cpEnd .rew{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-top:10px}.cpEnd .rew span{background:#fff;border:3px solid var(--ink);border-radius:13px;padding:3px 10px;font-size:15px;box-shadow:0 3px 0 var(--ink);white-space:nowrap}.cpEnd .rew .off{opacity:.6}
.cpEnd .lv{display:flex;align-items:center;gap:8px;margin-top:10px;font-size:14px;white-space:nowrap}.cpEnd .lv small{font-size:11px;color:#7a6a5e}.cpEnd .lvb{flex:1;height:14px;border-radius:99px;background:#e9dcc2;border:2px solid var(--ink);overflow:hidden}.cpEnd .lvb i{display:block;height:100%;background:linear-gradient(90deg,#c58a4a,#e6b06e)}
.cpEnd .bt{display:flex;gap:9px;margin-top:12px}.cpEnd .bt button{flex:1;height:52px;white-space:nowrap;padding:0 10px;border-radius:15px;border:3px solid var(--ink);box-shadow:0 4px 0 var(--ink);font-size:18px;background:var(--cream);color:var(--ink)}.cpEnd .bt .go{background:#7bd389}
#cpHud.pad .cpPor{width:118px;height:118px}
#cpHud.pad .cpCmd button{width:70px;height:66px;font-size:13px}#cpHud.pad .cpCmd button span{font-size:26px}
#cpHud.pad .cpHand{bottom:calc(166px + env(safe-area-inset-bottom))}
#cpHud.pad .cpBan{top:calc(110px + env(safe-area-inset-top))}
#cpHud.land .cpCon{background:none;padding-bottom:calc(6px + env(safe-area-inset-bottom))}
#cpHud.land .cpPor{width:70px;height:70px;margin-left:6px}
#cpHud.land .cpMid{position:absolute;left:calc(92px + env(safe-area-inset-left));bottom:calc(8px + env(safe-area-inset-bottom));width:min(190px,24vw)}
#cpHud.land .cpHint{white-space:normal;line-height:1.15}
#cpHud.land .cpHint{font-size:14px;padding:2px 8px}
#cpHud.land .cpCmd{margin-left:auto;grid-template-columns:repeat(2,1fr)}
#cpHud.land .cpCmd button{width:54px;height:50px}
#cpHud.land .cpHand{bottom:calc(2px + env(safe-area-inset-bottom));left:calc(min(190px,24vw) + 100px);right:130px}
#cpHud.land .cpBan{top:calc(40% - 30px)}
#cpHud.land .cpBan .t{font-size:22px}#cpHud.land .cpBan{top:calc(30% - 30px)}
#cpHud.land .cpEmo{bottom:calc(120px + env(safe-area-inset-bottom))}

/* (v634) 메뉴 · 미션 · 뒷면 · 규칙 · 따라 하기 · 쌓기 */
.cpMenu{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:calc(56px + env(safe-area-inset-top)) max(12px,env(safe-area-inset-right)) calc(12px + env(safe-area-inset-bottom)) max(12px,env(safe-area-inset-left));background:radial-gradient(ellipse at 50% 40%,rgba(30,18,40,.25),rgba(20,12,20,.72) 70%);pointer-events:auto;overflow:auto}
.cpMenu .pn{width:min(420px,100%);background:linear-gradient(rgba(52,34,58,.96),rgba(34,22,40,.96));border:3px solid var(--gold);box-shadow:0 0 0 3px var(--ink),0 0 26px rgba(255,211,107,.35);border-radius:24px;padding:14px;color:#fff;max-height:100%;overflow:auto}
.cpMenu .lg{font-size:44px;line-height:1;text-align:center;-webkit-text-stroke:7px var(--ink);paint-order:stroke fill;transform:rotate(-3deg);margin:2px 0 4px}
.cpMenu .lg span:nth-child(1){color:#ff5a5f}.cpMenu .lg span:nth-child(2){color:#ffc83d}.cpMenu .lg span:nth-child(3){color:#3fc46a}.cpMenu .lg span:nth-child(4){color:#3ea2ff}
.cpMenu .me{display:flex;justify-content:center;gap:6px;flex-wrap:wrap;font-size:14px;margin-bottom:10px}.cpMenu .me span{background:rgba(255,255,255,.12);border-radius:99px;padding:2px 10px}
.cpMenu .bb{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.cpMenu .bb button,.cpMenu .bk{border:3px solid var(--ink);border-radius:16px;box-shadow:0 4px 0 var(--ink);background:linear-gradient(#fffaf0,#f1e2c4);color:var(--ink);font-size:17px;padding:10px 8px;display:flex;flex-direction:column;align-items:center;gap:2px;line-height:1.15;position:relative}
.cpMenu .bb button small{font-size:12px;color:#7a6a5e}
.cpMenu .bb button:active{transform:translateY(3px);box-shadow:0 1px 0 var(--ink)}
.cpMenu .bb .big{grid-column:1/-1;background:linear-gradient(#8ff0a3,#4fcf6c);font-size:22px;padding:12px}
.cpMenu .bb .co{background:linear-gradient(#9fd8ff,#56b0ff)}
.cpMenu .bb .new:after{content:"처음이면 여기!";position:absolute;top:-10px;right:-6px;background:#ff5a5f;color:#fff;border:2px solid var(--ink);border-radius:9px;font-size:11px;padding:0 6px;transform:rotate(6deg);animation:cpGlow 1s infinite}
.cpMenu .df{display:flex;justify-content:center;gap:6px;margin:8px 0 2px}.cpMenu .df button{border:2px solid rgba(255,255,255,.5);background:rgba(255,255,255,.1);color:#fff;border-radius:99px;padding:5px 12px;font-size:14px}.cpMenu .df button.on{background:#ffe14d;color:var(--ink);border-color:var(--ink)}
.cpMenu .bt2{display:flex;gap:8px;margin-top:10px}.cpMenu .bt2 button{flex:1;border:2px solid rgba(255,255,255,.4);background:rgba(255,255,255,.1);color:#fff;border-radius:14px;padding:8px;font-size:15px}
.cpMenu h4{margin:0 0 8px;font-size:22px;font-weight:400;text-align:center}
.cpMenu .ml{display:flex;flex-direction:column;gap:7px}
.cpMenu .mi{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.1);border-radius:14px;padding:8px 10px;font-size:15px}
.cpMenu .mi .t{flex:1;min-width:0}.cpMenu .mi .b{height:8px;border-radius:9px;background:rgba(255,255,255,.18);margin-top:4px;overflow:hidden}.cpMenu .mi .b i{display:block;height:100%;background:#ffe14d}
.cpMenu .mi .c{white-space:nowrap;font-size:14px}.cpMenu .mi.ok{background:rgba(79,207,108,.28)}.cpMenu .mi.ok .c{color:#9ff0b0}
.cpMenu .bg2{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.cpMenu .bk{padding:6px 4px;font-size:13px;color:var(--ink)}.cpMenu .bk svg{display:block}.cpMenu .bk.on{outline:4px solid #ffe14d;outline-offset:2px}
.cpMenu .bk.lock svg{filter:grayscale(.85) brightness(.75)}.cpMenu .bk.lock:before{content:"🔒";position:absolute;top:40%;left:50%;transform:translate(-50%,-50%);font-size:28px;z-index:1}
.cpMenu .bk small{font-size:11px;color:#7a6a5e}
.cpMenu .rr{display:flex;flex-direction:column;gap:10px}.cpMenu .rr .r{background:rgba(255,255,255,.1);border-radius:14px;padding:10px}.cpMenu .rr .r b{font-weight:400;display:block;margin-bottom:6px}.cpMenu .rr .r small{display:block;font-size:12.5px;opacity:.8;margin-top:6px}
.cpMenu .rr .op{display:flex;gap:6px}.cpMenu .rr .op button{flex:1;border:2px solid rgba(255,255,255,.5);background:rgba(255,255,255,.1);color:#fff;border-radius:12px;padding:8px;font-size:15px}.cpMenu .rr .op button.on{background:#ffe14d;color:var(--ink);border-color:var(--ink)}
.cpOrd:empty{display:none}
#cpHud.pad .cpMenu .pn{width:min(540px,100%);padding:20px}#cpHud.pad .cpMenu .lg{font-size:58px}#cpHud.pad .cpMenu .bb button{font-size:20px;padding:14px 8px}#cpHud.pad .cpMenu .bb .big{font-size:26px}#cpHud.pad .cpMenu .me{font-size:16px}#cpHud.pad .cpMenu .bk{font-size:15px}
#cpHud.land .cpMenu{padding-top:calc(48px + env(safe-area-inset-top))}#cpHud.land .cpMenu .pn{width:min(760px,100%);padding:10px 14px}#cpHud.land .cpMenu .lg{font-size:30px}#cpHud.land .cpMenu .me{margin-bottom:6px}
#cpHud.land .cpMenu .bb{grid-template-columns:repeat(3,1fr);gap:6px}#cpHud.land .cpMenu .bb .big{font-size:20px;padding:6px}#cpHud.land .cpMenu .bb button{padding:6px;font-size:15px}#cpHud.land .cpMenu .bb [data-m=rule]{grid-column:auto!important}#cpHud.land .cpMenu .df{margin:2px 0}#cpHud.land .cpMenu .df button{padding:3px 12px}#cpHud.land .cpMenu .bt2{margin-top:6px}#cpHud.land .cpMenu .bt2 button{padding:5px}#cpHud.land .cpMenu .bg2{grid-template-columns:repeat(5,1fr)}
#cpHud.inMenu .cpCon,#cpHud.inMenu .cpHand,#cpHud.inMenu .cpFeed,#cpHud.inMenu .cpPlates{display:none}
.cpRule{display:inline-flex;gap:4px;font-size:12px;opacity:.85}
.cpCoach{position:absolute;max-width:min(300px,80vw);background:#fff8ea;color:var(--ink);border:3px solid var(--ink);border-radius:16px;box-shadow:0 4px 0 var(--ink);padding:8px 12px;font-size:16px;line-height:1.35;pointer-events:auto;z-index:8;animation:cpUp .3s}
.cpCoach b{color:#c2410c;font-weight:400}.cpCoach small{display:block;font-size:12px;color:#7a6a5e;margin-top:3px}
.cpFinger{position:absolute;font-size:40px;pointer-events:none;z-index:9;filter:drop-shadow(0 3px 0 #3b2433);animation:cpFing .8s infinite;transform:translate(-50%,0)}
@keyframes cpFing{50%{margin-top:10px}}
.cpPend{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%) rotate(-8deg);font-size:40px;color:#ff5a5f;-webkit-text-stroke:7px var(--ink);paint-order:stroke fill;display:none;animation:cpGlow .7s infinite}
.cpPend.on{display:block}
.cpMT{position:absolute;left:50%;top:calc(130px + env(safe-area-inset-top));transform:translateX(-50%);background:linear-gradient(#ffe14d,#ffb02e);color:var(--ink);border:3px solid var(--ink);border-radius:16px;box-shadow:0 4px 0 var(--ink);padding:6px 14px;font-size:16px;white-space:nowrap;display:none;z-index:7}
.cpMT.on{display:block;animation:cpEmb .4s cubic-bezier(.2,1.6,.4,1)}
.cpEnd .ms{display:flex;flex-direction:column;gap:4px;margin-top:8px}.cpEnd .ms div{display:flex;justify-content:space-between;font-size:13px;background:#f6ecd6;border-radius:9px;padding:3px 8px}.cpEnd .ms div.ok{background:#d6f5dc}
.cpEnd .nb{margin-top:8px;background:#fff3b0;border:2px dashed var(--ink);border-radius:12px;padding:5px 8px;font-size:14px;text-align:center}
`; document.head.appendChild(st); }


return {INK, CREAM, COL, KO, CS, NUMF, esc, shp, icon, cardSVG, backSVG, icSVG, mkDeck, isW, shuffle, josa, kname, ORDV, ACTC, LEAGUE, league, BOTS, EMOS, EMO_X, BACKS, BACK, backVal, backOpen, MISS, missToday, css};
})();
