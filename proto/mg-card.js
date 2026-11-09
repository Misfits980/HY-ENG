/* ═════════ (v633) 🃏 컬러팡 — 🎡 놀이 섬 가운데 카드 카페
   사용자(11-09): 「우노 이런 거 못 만드나?」 → 「그림 바꾸는 게 좋지 않을까? 우노인데?」 → 「영어 굳이 안 넣어도 되니까 개선판」
                → 「스타2 · 테이블탑 시뮬레이터도 참고」 → 「오 좋은데 조금만 더」 → 「만들어 주고 더 개선할 게 없는지 생각해 봐」
   · 이름 · 그림은 우리 것 (우노 이름 · 모양 안 씀) — 색마다 그림: 빨강 하트 · 노랑 별 · 초록 클로버 · 파랑 물방울 · 아래 점 = 숫자만큼
   · 규칙: 같은 색이나 같은 숫자(기능) · ⊘ 건너뛰기 · ⇄ 방향 바꾸기 · +2 · 🌈 무지개(색 고르기) · 🌈+4 · 1장 남으면 「☝️ 한 장!」(깜빡하면 +2)
   · 3D 카드 카페: 봇 3명(아바타)이 의자에 앉아 카드를 쥠 · 카드는 두께 있는 물건 · 날아가 떨어지며 「팡!」 · 탁자 테두리 = 지금 색
   · 화면(스타2 느낌): 차례 줄 · 머리 위 이름표 · 아래 내 얼굴 액자(+리그) · 큰 버튼 4개 · 내 차례 띠 · 끝나면 승리 화면 + 남은 카드 그래프
   · 상: MG 공통(하루 3판 🪙) — 1등 🪙10 · 2등 🪙6 · 3등 🪙5 · 4등 🪙4
   시험 손잡이: MG.run.G(상태) · MG.run.auto(내 차례 자동) · MG.run.fast(빨리 감기) */
(function(){
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
function cardSVG(c,v,w){ const W=w||150, H=Math.round(W*216/150), hd='<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+H+'" viewBox="0 0 150 216">';
  if(v==="back") return hd+frameSVG("#4a2f5f",["r","y","g","b"].map((k,i)=>'<g opacity=".2">'+icon(k,35+(i%2)*80,45+Math.floor(i/2)*126,40,"#fff",0)+'</g>').join("")
      +'<g transform="rotate(-14 75 108)"><rect x="18" y="80" width="114" height="56" rx="16" fill="'+CREAM+'" stroke="'+INK+'" stroke-width="5"/><text x="75" y="120" text-anchor="middle" font-family="Jua,\'Apple SD Gothic Neo\',\'Noto Sans KR\',sans-serif" font-weight="900" font-size="31" stroke="'+INK+'" stroke-width="6" paint-order="stroke" stroke-linejoin="round"><tspan fill="#ff5a5f">컬</tspan><tspan fill="#ffc83d">러</tspan><tspan fill="#3fc46a">팡</tspan><tspan fill="#3ea2ff">!</tspan></text></g>')+'</svg>';
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

/* ══ 게임 ══ */
function start(api){
  const SFX=api.sfx, LOW=!!api.low || (window.GUARD && GUARD.lv>=2), EASY=api.opt.df==="easy";
  api.menu=true;   /* 조이스틱 없음 — 화면은 그냥 누르기 */
  api.ui.classList.add("cpOn");
  let gone=false, paused=false, fast=0;
  const disp=[];
  /* ── 시간 (멈춤 지킴) ── */
  const TM=[]; const later=(s,fn)=>TM.push({t:s,fn}); const wait=s=>new Promise(r=>later(fast?Math.min(s,.02):s, r));
  /* ── 3D 장면 ── */
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x3a2630); scene.fog=new THREE.Fog(0x3a2630, 8, 17);
  const cam=new THREE.PerspectiveCamera(50, 1, .05, 40);
  scene.add(new THREE.HemisphereLight(0xfff0e0, 0x6a4450, .62));
  { const rim=new THREE.DirectionalLight(0xc8dcff,.45); rim.position.set(0,3.5,-6); scene.add(rim); }
  const sun=new THREE.DirectionalLight(0xffe2c0,.78); sun.position.set(2.5,6,3); scene.add(sun); scene.add(sun.target);
  if(!LOW){ sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); Object.assign(sun.shadow.camera,{left:-3.2,right:3.2,top:3.2,bottom:-3.2,near:1,far:14}); sun.shadow.bias=-.0008; }
  { const lp=new THREE.PointLight(0xffc98a,1.1,6,1.6); lp.position.set(0,2.8,0); scene.add(lp); }
  const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const MS=(c,o)=>{ const m=toon(new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.85},o||{}))); disp.push(m); return m; };
  const G3=g=>{ disp.push(g); return g; };
  function tex(w,h,draw){ const c=document.createElement("canvas"); c.width=w; c.height=h; draw(c.getContext("2d"),w,h); const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding; t.anisotropy=4; disp.push(t); return t; }
  /* 바닥 · 깔개 · 벽 · 간판 · 깃발 · 전구 */
  { const ft=tex(256,256,(g,w)=>{ for(let i=0;i<4;i++){ g.fillStyle=["#a8714a","#9c6842","#b07a50","#a06c45"][i]; g.fillRect(0,i*64,w,64); g.fillStyle="rgba(60,30,20,.35)"; g.fillRect(0,i*64,w,3); for(let k=0;k<2;k++) g.fillRect((i*97+k*131)%w,i*64,3,64); } }); ft.wrapS=ft.wrapT=THREE.RepeatWrapping; ft.repeat.set(12,12);
    const fl=new THREE.Mesh(G3(new THREE.PlaneGeometry(30,30)), MS(0xffffff,{map:ft})); fl.rotation.x=-Math.PI/2; fl.receiveShadow=true; scene.add(fl);
    const rug=new THREE.Mesh(G3(new THREE.CircleGeometry(2.9,40)), MS(0x5b3a7a,{roughness:.95})); rug.rotation.x=-Math.PI/2; rug.position.y=.005; rug.receiveShadow=true; scene.add(rug);
    const r2=new THREE.Mesh(G3(new THREE.RingGeometry(2.55,2.7,40)), MS(0xe0a84a)); r2.rotation.x=-Math.PI/2; r2.position.y=.007; scene.add(r2);
    const wm=MS(0x8d5a6b), wg=G3(new THREE.PlaneGeometry(14,5)), win=new THREE.MeshBasicMaterial({color:0xffd99a}); disp.push(win); const wing=G3(new THREE.PlaneGeometry(1.3,1.5));
    [[0,-6.5,0],[-6.5,0,Math.PI/2],[6.5,0,-Math.PI/2]].forEach(([x,z,r])=>{ const w=new THREE.Mesh(wg,wm); w.position.set(x,2.5,z); w.rotation.y=r; scene.add(w);
      for(let i=-1;i<=1;i++){ const q=new THREE.Mesh(wing,win); q.position.set(x+(r?(x<0?.01:-.01):i*3.6),2.4,z+(r?i*3.6:.01)); q.rotation.y=r; scene.add(q); } });
    const sg=tex(512,160,(g,w,h)=>{ g.fillStyle=INK; g.fillRect(0,0,w,h); g.strokeStyle="#ffd36b"; g.lineWidth=8; g.strokeRect(4,4,w-8,h-8); g.font="900 76px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; ["컬","러","팡","!"].forEach((t,i)=>{ g.shadowColor=COL[CS[i]]; g.shadowBlur=16; g.fillStyle=COL[CS[i]]; g.fillText(t,w/2+(i-1.5)*76,h/2-8); }); g.shadowBlur=0; g.font="800 24px Jua,sans-serif"; g.fillStyle=CREAM; g.fillText("🃏 카드 카페",w/2,h-22); });
    const sgm=new THREE.MeshBasicMaterial({map:sg}); disp.push(sgm); const sign=new THREE.Mesh(G3(new THREE.PlaneGeometry(3.2,1)), sgm); sign.position.set(0,2.05,-6.45); scene.add(sign); scene.userData.sign=sign;
    const fg=G3(new THREE.BufferGeometry()); fg.setAttribute("position", new THREE.Float32BufferAttribute([-.14,0,0,.14,0,0,0,-.3,0],3)); const fm=CS.map(c=>{ const m=new THREE.MeshBasicMaterial({color:COL[c],side:THREE.DoubleSide}); disp.push(m); return m; });
    for(let i=0;i<=26;i++){ const t=i/26, m=new THREE.Mesh(fg,fm[i%4]); m.position.set(-6+t*12,3.35-Math.sin(t*Math.PI)*.5,-6.4); scene.add(m); }
    const bg=G3(new THREE.SphereGeometry(.05,6,4)), bm=new THREE.MeshBasicMaterial({color:0xfff0b0}); disp.push(bm); for(let i=0;i<30;i++){ const t=i/29, b=new THREE.Mesh(bg,bm); b.position.set(-6+t*12,4.2-Math.sin(t*Math.PI)*.35,-6.38); scene.add(b); }
    const sh=new THREE.Mesh(G3(new THREE.ConeGeometry(.42,.32,20,1,true)), MS(0xffd36b,{side:THREE.DoubleSide,emissive:0x5a3a00})); sh.position.set(0,3.9,0); scene.add(sh); }
  /* 탁자 */
  const TY=.66, TR=1.32, table=new THREE.Group(); scene.add(table);
  { const rim=new THREE.Mesh(G3(new THREE.CylinderGeometry(TR,TR-.04,.1,48)), MS(0x8a5a3c,{roughness:.55})); rim.position.y=TY-.05; rim.castShadow=rim.receiveShadow=true; table.add(rim);
    const ftx=tex(512,512,(g,w,h)=>{ const gr=g.createRadialGradient(w/2,h/2,10,w/2,h/2,w/2); gr.addColorStop(0,"#6fd0a0"); gr.addColorStop(1,"#3a9c70"); g.fillStyle=gr; g.fillRect(0,0,w,h); for(let i=0;i<5000;i++){ g.fillStyle="rgba(255,255,255,"+(Math.random()*.05)+")"; g.fillRect(Math.random()*w,Math.random()*h,1.5,1.5); }
      g.strokeStyle="rgba(255,255,255,.28)"; g.lineWidth=6; g.setLineDash([22,16]); g.beginPath(); g.arc(w/2,h/2,w*.36,0,7); g.stroke(); g.setLineDash([]); g.globalAlpha=.1; g.fillStyle="#fff"; g.font="900 64px Jua,sans-serif"; g.textAlign="center"; g.fillText("컬러팡!",w/2,h/2+22); });
    const felt=new THREE.Mesh(G3(new THREE.CircleGeometry(TR-.1,48)), MS(0xffffff,{map:ftx,roughness:.95})); felt.rotation.x=-Math.PI/2; felt.position.y=TY+.002; felt.receiveShadow=true; table.add(felt);
    const leg=new THREE.Mesh(G3(new THREE.CylinderGeometry(.16,.22,TY-.1,16)), MS(0x6e4430)); leg.position.y=(TY-.1)/2; table.add(leg);
    const base=new THREE.Mesh(G3(new THREE.CylinderGeometry(.6,.7,.08,24)), MS(0x6e4430)); base.position.y=.04; table.add(base); }
  const glowM=new THREE.MeshBasicMaterial({color:0x3ea2ff}); disp.push(glowM);
  { const gl=new THREE.Mesh(G3(new THREE.TorusGeometry(TR-.06,.022,6,72)), glowM); gl.rotation.x=Math.PI/2; gl.position.y=TY+.012; table.add(gl); }
  const haloM=new THREE.MeshBasicMaterial({map:tex(128,128,(g,w,h)=>{ const gr=g.createRadialGradient(w/2,h/2,w*.36,w/2,h/2,w*.5); gr.addColorStop(0,"rgba(255,255,255,0)"); gr.addColorStop(.25,"rgba(255,255,255,.9)"); gr.addColorStop(1,"rgba(255,255,255,0)"); g.fillStyle=gr; g.fillRect(0,0,w,h); }),color:0x3ea2ff,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,opacity:.3}); disp.push(haloM);
  { const h=new THREE.Mesh(G3(new THREE.PlaneGeometry(TR*2.5,TR*2.5)), haloM); h.rotation.x=-Math.PI/2; h.position.y=TY+.008; table.add(h); }
  const glowCol=new THREE.Color(0x3ea2ff), glowTo=new THREE.Color(0x3ea2ff);
  /* 내 차례 = 내 쪽 가장자리 금빛 */
  const myArc=new THREE.Group(); table.add(myArc);
  { const a=new THREE.Mesh(G3(new THREE.TorusGeometry(TR-.02,.045,6,40,Math.PI*.42)), new THREE.MeshBasicMaterial({color:0xffe14d})); disp.push(a.material); a.rotation.x=Math.PI/2; a.rotation.z=Math.PI/2-Math.PI*.21; a.position.y=TY+.03; myArc.add(a);
    const hm=new THREE.MeshBasicMaterial({map:tex(64,32,(g,w,hh)=>{ const gr=g.createLinearGradient(0,0,0,hh); gr.addColorStop(0,"rgba(255,225,77,0)"); gr.addColorStop(1,"rgba(255,225,77,.45)"); g.fillStyle=gr; g.fillRect(0,0,w,hh); }),transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}); disp.push(hm);
    const h=new THREE.Mesh(G3(new THREE.PlaneGeometry(TR*1.2,.7)), hm); h.rotation.x=-Math.PI/2; h.position.set(0,TY+.01,TR-.42); myArc.add(h); }
  myArc.visible=false;
  /* ── 카드 물건 (둥근 모서리 · 두께) ── */
  const CW=.36, CH=.52, CT=.007;
  const cardGeo=(()=>{ const s=new THREE.Shape(), w=CW/2, h=CH/2, r=.035; s.moveTo(-w+r,-h); s.lineTo(w-r,-h); s.quadraticCurveTo(w,-h,w,-h+r); s.lineTo(w,h-r); s.quadraticCurveTo(w,h,w-r,h); s.lineTo(-w+r,h); s.quadraticCurveTo(-w,h,-w,h-r); s.lineTo(-w,-h+r); s.quadraticCurveTo(-w,-h,-w+r,-h);
    let g=new THREE.ExtrudeGeometry(s,{depth:CT,bevelEnabled:false,curveSegments:3}); g.rotateX(-Math.PI/2); if(g.index) g=g.toNonIndexed();
    const p=g.attributes.position, uv=g.attributes.uv, n=g.attributes.normal, cnt=p.count, tri=[];
    for(let i=0;i<cnt;i+=3){ const ny=n.getY(i); tri.push(ny>.9?1:ny<-.9?2:0); if(Math.abs(ny)>.9) for(let j=0;j<3;j++) uv.setXY(i+j,(p.getX(i+j)+w)/CW,(-p.getZ(i+j)+h)/CH); }
    const ord=tri.map((m,i)=>[m,i]).sort((a,b)=>a[0]-b[0]), idx=new Uint16Array(cnt); ord.forEach(([m,t],k)=>{ for(let j=0;j<3;j++) idx[k*3+j]=t*3+j; }); g.setIndex(new THREE.BufferAttribute(idx,1));
    let st=0; [0,1,2].forEach(m=>{ const c=tri.filter(x=>x===m).length*3; g.addGroup(st,c,m); st+=c; }); return G3(g); })();
  const sideM=MS(0xfff8ea,{roughness:.6});
  /* 카드 그림 → 이미지(미리) → 텍스처(쓸 때 · 24장까지) */
  const IMG={}, TEX=new Map(); const key=k=>k?(k.c||"x")+"|"+k.v:"x|back";
  function loadImgs(){ const L=[[null,"back"],[null,"wild"],[null,"wild4"]]; CS.forEach(c=>{ for(let n=0;n<=9;n++) L.push([c,n]); ["skip","rev","d2"].forEach(v=>L.push([c,v])); });
    return Promise.all(L.map(([c,v])=>new Promise(res=>{ const im=new Image(); im.onload=()=>res(); im.onerror=()=>res(); im.src="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(cardSVG(c,v)); IMG[(c||"x")+"|"+v]=im; }))); }
  function faceMat(k){ const kk=key(k); let e=TEX.get(kk); if(e){ e.used=performance.now(); return e.m; }
    const t=tex(192,276,(g)=>{ const im=IMG[kk]; try{ if(im && im.complete) g.drawImage(im,0,0,192,276); }catch(_){} }); t.anisotropy=8; const m=new THREE.MeshStandardMaterial({map:t,roughness:.55}); disp.push(m);
    e={m,t,used:performance.now()}; TEX.set(kk,e);
    if(TEX.size>26){ let old=null; for(const [q,v] of TEX) if(q!=="x|back" && (!old || v.used<old[1].used) && !v.keep) old=[q,v]; if(old && !inUse(old[0])){ old[1].t.dispose(); old[1].m.dispose(); TEX.delete(old[0]); } }
    return m; }
  const inUse=kk=>pileM.some(m=>m.userData.kk===kk) || FLY.some(f=>f.m.userData.kk===kk);
  function cardMesh(k, faceUp){ const f=faceMat(k), b=faceMat(null); const m=new THREE.Mesh(cardGeo, faceUp===false?[sideM,b,f]:[sideM,f,b]); m.castShadow=!LOW; m.receiveShadow=!LOW; m.userData.kk=key(k); return m; }
  /* 뽑기 더미 · 버린 더미 */
  const drawPile=new THREE.Group(); drawPile.position.set(-.48,TY,.28); drawPile.rotation.y=.12; table.add(drawPile);
  { const edge=tex(32,32,(g,w,h)=>{ g.fillStyle=CREAM; g.fillRect(0,0,w,h); g.fillStyle="#d8c7a8"; for(let i=0;i<h;i+=4) g.fillRect(0,i,w,1.5); }); const em=MS(0xffffff,{map:edge});
    const st=new THREE.Mesh(G3(new THREE.BoxGeometry(CW-.01,.1,CH-.01)), [em,em,faceMat(null),em,em,em]); st.position.y=.05; st.castShadow=!LOW; st.receiveShadow=true; drawPile.add(st); drawPile.userData.st=st;
    const t1=cardMesh(null,true); t1.position.set(.015,.102,.012); t1.rotation.y=-.08; drawPile.add(t1); }
  const disc=new THREE.Group(); disc.position.set(.36,TY,.3); table.add(disc);
  const pileM=[];
  function pileAdd(k){ const m=cardMesh(k); const n=pileM.length; m.position.set((Math.random()-.5)*.08, .001+n*(CT+.0015), (Math.random()-.5)*.08); m.rotation.y=(Math.random()-.5)*(n?1.4:.2); disc.add(m); pileM.push(m);
    if(pileM.length>7){ const o=pileM.shift(); disc.remove(o); pileM.forEach((q,i)=>q.position.y=.001+i*(CT+.0015)); } }
  /* ── 사람 (봇 3명 · 아바타 그대로) ── */
  const chairM=MS(0xa66a42), chairD=MS(0x7a4a2c);
  function chair(G){ const c=new THREE.Group(); const B=(w,h,d,x,y,z,m)=>{ const q=new THREE.Mesh(G3(new THREE.BoxGeometry(w,h,d)), m); q.position.set(x,y,z); q.castShadow=!LOW; c.add(q); };
    B(.56,.07,.52,0,.42,0,chairM); B(.56,.5,.07,0,.7,-.24,chairM); B(.48,.08,.05,0,.82,-.25,chairD); [[-.23,-.21],[.23,-.21],[-.23,.21],[.23,.21]].forEach(([x,z])=>B(.06,.42,.06,x,.21,z,chairD)); G.add(c); return c; }
  const SEATS=[];
  function mkSeat(i, ang, bot){ const d=TR+.5, x=Math.sin(ang)*d, z=-Math.cos(ang)*d, G=new THREE.Group(); G.position.set(x,0,z); G.rotation.y=Math.atan2(-x,-z); scene.add(G); chair(G);
    let P=null; try{ P=buildAvatar(bot.av); P.g.scale.setScalar(1.08); P.g.position.set(0,.25,-.02); G.add(P.g); P.legL.rotation.x=P.legR.rotation.x=-1.45; arms(P,"hold"); }catch(e){ console.warn("CP av", e); }
    const hand=new THREE.Group(); hand.position.set(0,.8,.42); hand.rotation.x=-.5; G.add(hand);
    const s={i, G, P, hand, n:-1, ang, t:Math.random()*6, act:"", actT:0}; SEATS[i]=s; return s; }
  function arms(P, k){ if(!P) return; if(k==="yay"){ P.armL.rotation.set(-2.7,0,.4); P.armR.rotation.set(-2.7,0,-.4); } else if(k==="clap"){ P.armL.rotation.set(-1.3,0,-.35); P.armR.rotation.set(-1.3,0,.35); } else { P.armL.rotation.set(-1.05,0,.25); P.armR.rotation.set(-1.05,0,-.25); } }
  const backPG=G3(new THREE.PlaneGeometry(CW*.62,CH*.62)), backFM=new THREE.MeshStandardMaterial({map:faceMat(null).map,roughness:.6}), backBM=MS(0xfff8ea,{side:THREE.BackSide}); disp.push(backFM);
  function fan(s, n){ n=Math.min(n,8); if(s.n===n) return; s.n=n; while(s.hand.children.length) s.hand.remove(s.hand.children[0]);
    for(let i=0;i<n;i++){ const a=(i-(n-1)/2)*.17; const m=new THREE.Mesh(backPG,backFM), m2=new THREE.Mesh(backPG,backBM); m.position.set(Math.sin(a)*.12, Math.cos(a)*.12-.12, i*.004); m.rotation.z=-a; m2.position.copy(m.position); m2.rotation.copy(m.rotation); s.hand.add(m); s.hand.add(m2); } }
  /* ── 내 얼굴 (액자 안 — 따로 그림) ── */
  const PS=new THREE.Scene(); PS.background=new THREE.Color(0x2b3a5a); PS.add(new THREE.HemisphereLight(0xffffff,0x445566,.85)); { const l=new THREE.DirectionalLight(0xffffff,.55); l.position.set(.6,1.4,1.4); PS.add(l); }
  const PC=new THREE.PerspectiveCamera(26,1,.1,10); PC.position.set(.05,1.0,1.75); PC.lookAt(0,.88,0);
  let ME=null; try{ ME=buildAvatar(api.av||{}); PS.add(ME.g); ME.setExpr("grin"); }catch(e){}
  /* ── 날아가는 카드 · 팡! · 색종이 ── */
  const FLY=[];
  function fly(k, faceUp, from, to, dur, o){ o=o||{}; const m=cardMesh(k, faceUp); m.position.copy(from); scene.add(m); return new Promise(res=>FLY.push({m, from:from.clone(), to:to.clone(), t:0, dur:fast?.01:dur, arc:o.arc==null?.45:o.arc, r0:o.r0||new THREE.Euler(-.5,0,.2), r1:o.r1||new THREE.Euler(0,(Math.random()-.5)*.6,0), flip:!!o.flip, res, keep:!!o.keep})); }
  const popTex=tex(256,256,(g,w,h)=>{ g.translate(w/2,h/2); g.beginPath(); for(let i=0;i<24;i++){ const a=i/24*Math.PI*2, r=i%2?w*.27:w*.46; g.lineTo(Math.cos(a)*r,Math.sin(a)*r); } g.closePath(); g.fillStyle="#ffe14d"; g.fill(); g.lineWidth=8; g.strokeStyle=INK; g.lineJoin="round"; g.stroke();
    g.rotate(-.18); g.font="900 62px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.lineWidth=14; g.strokeStyle=INK; g.strokeText("팡!",0,4); g.fillStyle="#ff5a5f"; g.fillText("팡!",0,4); });
  const popM=new THREE.SpriteMaterial({map:popTex,depthTest:false,transparent:true}); disp.push(popM); const popS=new THREE.Sprite(popM); popS.renderOrder=9; popS.visible=false; scene.add(popS); let popT=9;
  function pop(){ const w=new THREE.Vector3(); disc.getWorldPosition(w); popS.position.set(w.x+.3,w.y+.34,w.z-.1); popT=0; popS.visible=true; }
  const CONF=[]; function confetti(n){ const g=G3(new THREE.PlaneGeometry(.08,.13)); for(let i=0;i<n;i++){ const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:[0xff5a5f,0xffc83d,0x3fc46a,0x3ea2ff,0xffffff][i%5],side:THREE.DoubleSide})); disp.push(m.material);
      m.position.set((Math.random()-.5)*4, 2.6+Math.random()*2, (Math.random()-.5)*3.4); m.rotation.set(Math.random()*6,Math.random()*6,0); m.userData.v=.5+Math.random()*.7; m.userData.s=(Math.random()-.5)*4; scene.add(m); CONF.push(m); } }

  /* ══ 화면 (HUD) ══ */
  css();
  const U=api.ui, HUD=document.createElement("div"); HUD.id="cpHud"; U.appendChild(HUD);
  HUD.innerHTML='<div class="cpVig"></div><div class="cpPlates"></div><div class="cpFeed"></div><div class="cpBan"><div><span class="t">⭐ 내 차례! ⭐</span><small></small></div></div>'
    +'<div class="cpHand"><div class="in"></div></div>'
    +'<div class="cpCon"><div class="cpPor"><canvas></canvas><div class="who"></div><div class="emo"></div></div><div class="cpMid"><div class="cpHint"></div><div class="cpBar"><i></i></div></div>'
    +'<div class="cpCmd"><button data-c="draw"><span>🃏</span><b>뽑기</b></button><button data-c="one" class="one"><span>☝️</span><b>한 장!</b></button><button data-c="emo"><span>😊</span><b>표정</b></button><button data-c="sort"><span>🔀</span><b>정렬</b></button></div></div>'
    +'<div class="cpEmo"></div><div class="cpPick"></div><div class="cpEnd"></div><div class="cpLoad">🃏 카드 섞는 중…</div>';
  const $=s=>HUD.querySelector(s);
  api.topR.innerHTML='<div class="cpTop"><div class="cpOrd"></div><div class="cpCoin"></div></div>';
  const ORD=api.topR.querySelector(".cpOrd");
  const porCv=$(".cpPor canvas"), porG=porCv.getContext("2d");

  /* ══ 상태 ══ */
  const rec=MG.rec(), T0=(rec.t.card)||{}, B0=(rec.b.card)||{};
  const LG=league(T0.win);
  const names=shuffle(BOTS.slice()).slice(0,3);
  const G={P:[], dir:1, turn:0, cur:"b", top:null, pile:[], draw:[], over:false, busy:true, drew:false, tleft:0, hist:[], st:{play:0, atk:0, rev:0, wild:0, drawn:0}, sort:"c", one:{need:false, t:0}, feed:[], myTurn:false};
  G.P.push({nm:api.nick||"나", me:true, h:[], col:"#ffc83d", av:api.av});
  names.forEach((b,i)=>G.P.push({nm:b.nm, bot:true, h:[], col:COL[["r","b","g"][i]], av:b.av, called:false}));
  [-.6,0,.6].forEach((a,i)=>mkSeat(i+1, a, names[i]));
  /* 카메라 — 화면 모양에 맞춰 (폰 세로 · 패드 세로 · 가로) */
  let lastA=0;
  function fitCam(){ const a=cam.aspect||1; if(Math.abs(a-lastA)<.01) return; lastA=a; let fov, p, l;
    if(a<1){ const t=Math.max(0,Math.min(1,(a-.46)/(.72-.46))); fov=52-8*t; p=[0,4.15-.25*t,5.35-.75*t]; l=[0,.6,-.15-.1*t]; }
    else { const t=Math.max(0,Math.min(1,(a-1.3)/(2.16-1.3))); fov=40-6*t; p=[0,3.35-.25*t,3.9-.25*t]; l=[0,.62,-.2]; }
    cam.fov=fov; cam.position.set(...p); cam.lookAt(...l); cam.updateProjectionMatrix(); HUD.classList.toggle("land", a>=1); HUD.classList.toggle("pad", a>=.6 && a<1); layoutHand(); }

  /* ── 소식 · 띠 · 힌트 ── */
  function feed(h, c){ G.feed.unshift({h, c}); G.feed=G.feed.slice(0,3); $(".cpFeed").innerHTML=G.feed.map(f=>'<div style="--c:'+(f.c?COL[f.c]:"#fff")+'">'+(f.c?icSVG(f.c,13):"")+'<span>'+f.h+'</span></div>').join(""); }
  let banT=0; function banner(t, sub){ const b=$(".cpBan"); b.querySelector(".t").textContent=t; b.querySelector("small").textContent=sub||""; b.classList.add("on"); banT=1.3; }
  function hint(){ const h=$(".cpHint"); if(G.over){ h.innerHTML="🏁 끝!"; return; } if(!G.myTurn){ const p=G.P[G.turn]; h.innerHTML='⏳ <b>'+esc(p.nm)+'</b> 차례'; h.classList.remove("my"); return; }
    h.classList.add("my"); const pl=G.P[0].h.some(k=>okCard(k,G.top,G.cur));
    h.innerHTML=pl ? icSVG(G.cur,16)+' <b>'+KO[G.cur]+'</b>'+(isW(G.top)?'':' 또는 <b>'+(typeof G.top.v==="number"?G.top.v:ACTC[G.top.v])+'</b>')+'!' : (G.drew?'낼 카드가 없어요 → 넘겨요':'낼 카드가 없어요 → <b>🃏 뽑기</b>'); }
  function setCur(c){ G.cur=c; glowTo.set(COL[c]); }

  /* ── 차례 줄 · 이름표 ── */
  function drawTop(){ const L=[0,1,2,3].map(i=>(i+0)%4); ORD.innerHTML=L.map((i,j)=>(j?'<b>'+(G.dir>0?'›':'‹')+'</b>':'')+'<i class="'+(G.turn===i&&!G.over?"on":"")+'" style="background:'+G.P[i].col+'">'+esc(G.P[i].nm.slice(0,1))+'</i>').join("")+'<b class="d">'+(G.dir>0?'↻':'↺')+'</b>';
    const left=MG.payLeft("card"); api.topR.querySelector(".cpCoin").textContent=left>0?'🪙 '+left+'판':'🪙 끝'; }
  const PL=$(".cpPlates");
  PL.innerHTML=[1,2,3].map(i=>'<div class="cpPlate" data-i="'+i+'"><div class="emo"></div><div class="one1">☝️ 한 장!</div><div class="nm"><span class="dot" style="background:'+G.P[i].col+'"></span><span class="n"></span>🤖<u></u></div><div class="think"><i></i><i></i><i></i></div></div>').join("");
  function plates(){ [1,2,3].forEach(i=>{ const el=PL.querySelector('[data-i="'+i+'"]'), p=G.P[i]; el.querySelector(".n").textContent=p.nm; const u=el.querySelector("u"); u.textContent="🂠 "+p.h.length; u.classList.toggle("one", p.h.length===1); el.classList.toggle("turn", G.turn===i && !G.over); el.classList.toggle("o1", p.h.length===1 && !G.over); }); }
  const v3=new THREE.Vector3();
  function platePos(){ const W=innerWidth, H=innerHeight; [1,2,3].forEach(i=>{ const s=SEATS[i]; if(!s || !s.P) return; s.P.head.getWorldPosition(v3); v3.y+=.42; v3.project(cam); const el=PL.querySelector('[data-i="'+i+'"]'); el.style.left=((v3.x+1)/2*W)+"px"; el.style.top=((1-v3.y)/2*H)+"px"; }); }
  const EMT={}; function emote(i, e){ const el=i===0?$(".cpPor .emo"):PL.querySelector('[data-i="'+i+'"] .emo'); if(!el) return; el.textContent=e; el.classList.add("on"); clearTimeout(EMT[i]); EMT[i]=setTimeout(()=>el.classList.remove("on"), 1800);
    const s=i===0?{P:ME}:SEATS[i]; if(s && s.P && EMO_X[e]) { s.P.setExpr(EMO_X[e]); s.actT=1.8; } }
  function react(i, ex, t){ const s=SEATS[i]; if(!s || !s.P) return; s.P.setExpr(ex); s.actT=t||1.6; }

  /* ── 내 패 ── */
  const HAND=$(".cpHand .in");
  function sorted(){ const h=G.P[0].h.slice(); const co=c=>c?CS.indexOf(c):9; return G.sort==="c" ? h.sort((a,b)=>co(a.c)-co(b.c) || ORDV(a.v)-ORDV(b.v)) : h.sort((a,b)=>ORDV(a.v)-ORDV(b.v) || co(a.c)-co(b.c)); }
  let handSig="", newIds={};
  function layoutHand(){ handSig=""; drawHand(); }
  function drawHand(){ const h=sorted(), W=innerWidth, H=innerHeight, land=W>H, n=Math.max(1,h.length);
    const cw=Math.round(Math.max(48, Math.min(land?H*.2:118, H*(land?.2:.15), (W*(land?.62:.94))/(1+(n-1)*.64)))), ov=Math.round(cw*.36), rot=Math.min(4.2, 30/n);
    const sig=h.map(k=>k.id).join(",")+"|"+cw+"|"+G.myTurn+"|"+G.cur+"|"+(G.top&&G.top.id)+"|"+G.busy+"|"+G.over;
    if(sig===handSig) return; handSig=sig; const mid=(n-1)/2;
    HAND.innerHTML=h.map((k,i)=>{ const can=G.myTurn && !G.busy && !G.over && okCard(k,G.top,G.cur); const d=i-mid;
      return '<div class="cpC '+(G.myTurn&&!G.over?(can?"ok":"no"):"")+(newIds[k.id]?" new":"")+'" data-id="'+k.id+'" style="margin-left:'+(i?-ov:0)+'px;--r:'+(d*rot).toFixed(1)+'deg;--y:'+(d*d*1.3).toFixed(1)+'px">'+cardSVG(k.c,k.v,cw)+'</div>'; }).join("");
    newIds={}; }
  HAND.addEventListener("pointerdown", e=>{ const c=e.target.closest(".cpC"); if(!c) return; e.preventDefault(); tapCard(+c.dataset.id, c); });
  function shake(el){ if(!el) return; el.classList.remove("shk"); void el.offsetWidth; el.classList.add("shk"); }
  function tapCard(id, el){ try{ SFX.ctx(); }catch(e){} if(G.over) return; const k=G.P[0].h.find(q=>q.id===id); if(!k) return;
    if(!G.myTurn || G.busy){ shake(el); return; }
    if(!okCard(k,G.top,G.cur)){ shake(el); try{ SFX.tone(220,.12,"square",.03); }catch(e){} toast(icSVG(G.cur,15)+' '+KO[G.cur]+(isW(G.top)?'':' 또는 '+(typeof G.top.v==="number"?G.top.v:ACTC[G.top.v]))+' 만 낼 수 있어요'); return; }
    if(isW(k)){ pickColor(k); return; }
    myPlay(k); }
  let toastT=0; function toast(h){ const t=$(".cpHint"); t.innerHTML=h; t.classList.add("warn"); toastT=1.6; }
  /* 🌈 색 고르기 */
  function pickColor(k){ const cnt={}; G.P[0].h.forEach(q=>{ if(q.c && q.id!==k.id) cnt[q.c]=(cnt[q.c]|0)+1; }); let best=null; CS.forEach(c=>{ if((cnt[c]|0)>0 && (!best || cnt[c]>cnt[best])) best=c; });
    const C=["y","g","b","r"]; let svg='<svg viewBox="0 0 300 300">'; C.forEach((c,i)=>{ const a0=(i*90-135)*Math.PI/180, a1=a0+Math.PI/2, r=140, ri=58, P=(a,rr)=>(150+Math.cos(a)*rr).toFixed(1)+" "+(150+Math.sin(a)*rr).toFixed(1);
      svg+='<path data-c="'+c+'" d="M'+P(a0,ri)+'L'+P(a0,r)+'A'+r+' '+r+' 0 0 1 '+P(a1,r)+'L'+P(a1,ri)+'A'+ri+' '+ri+' 0 0 0 '+P(a0,ri)+'Z" fill="'+COL[c]+'" stroke="'+INK+'" stroke-width="6" stroke-linejoin="round"/>'; });
    svg+='</svg>'; const lab=C.map((c,i)=>{ const a=(i*90-90)*Math.PI/180; return '<div class="lb'+(c===best?" rec":"")+'" data-c="'+c+'" style="left:'+(50+Math.cos(a)*33.3)+'%;top:'+(50+Math.sin(a)*33.3)+'%">'+icSVG(c,40)+KO[c]+(c===best?'<small>내 카드에 '+cnt[c]+'장</small>':'')+'</div>'; }).join("");
    const P=$(".cpPick"); P.innerHTML='<h3>🌈 무슨 색으로 할까?</h3><div class="wh">'+svg+lab+'<div class="mid">'+cardSVG(null,k.v,62)+'</div></div><p>👆 누르면 탁자 색이 바뀌어요</p><button class="no">↩ 다른 카드</button>'; P.classList.add("on");
    P.querySelectorAll("[data-c]").forEach(el=>el.onclick=()=>{ P.classList.remove("on"); myPlay(k, el.dataset.c); });
    P.querySelector(".no").onclick=()=>P.classList.remove("on"); }
  /* 버튼 */
  HUD.querySelector(".cpCmd").addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b) return; try{ SFX.ctx(); }catch(_){} const c=b.dataset.c;
    if(c==="draw") myDraw(); else if(c==="one") callOne(); else if(c==="sort"){ G.sort=G.sort==="c"?"n":"c"; b.querySelector("b").textContent=G.sort==="c"?"색 순서":"숫자 순서"; layoutHand(); try{ SFX.tone(660,.06,"triangle",.03); }catch(_){} }
    else if(c==="emo"){ const E=$(".cpEmo"); E.innerHTML=EMOS.map(x=>'<button>'+x+'</button>').join(""); E.classList.toggle("on"); E.querySelectorAll("button").forEach(bb=>bb.onclick=()=>{ E.classList.remove("on"); emote(0, bb.textContent); botReply(); }); } });
  let replyT=0; function botReply(){ if(replyT>0) return; replyT=4; if(Math.random()<.6){ const i=1+Math.floor(Math.random()*3); later(.7+Math.random()*.6, ()=>emote(i, EMOS[Math.floor(Math.random()*EMOS.length)])); } }
  function cmd(){ const C=$(".cpCmd"), dr=C.querySelector('[data-c="draw"]'), on=C.querySelector('[data-c="one"]'), me=G.P[0];
    const can=G.myTurn && !G.busy && !G.over; const pl=me.h.some(k=>okCard(k,G.top,G.cur));
    dr.classList.toggle("off", !can); dr.classList.toggle("glow", can && !pl && !G.drew);
    dr.querySelector("span").textContent=G.drew?"⏭":"🃏"; dr.querySelector("b").textContent=G.drew?"넘기기":"뽑기";
    const oneOn=!G.over && ((G.myTurn && me.h.length===2 && pl && !me.called) || G.one.need); on.classList.toggle("off", !oneOn && !me.called); on.classList.toggle("glow", oneOn); on.querySelector("b").textContent=me.called?"외쳤어요!":"한 장!"; }

  /* ══ 흐름 ══ */
  const nextI=(i,st)=>(i+G.dir*(st||1)+40)%4;
  function refill(){ if(G.draw.length) return; const top=G.pile.pop(); G.draw=shuffle(G.pile); G.pile=[top]; feed("🔄 카드를 다시 섞었어요"); }
  function seatPos(i){ const v=new THREE.Vector3(); if(i===0){ const p=new THREE.Vector3(0,-.82,.5).unproject(cam); return p; } SEATS[i].hand.getWorldPosition(v); return v; }
  function myCardPos(id){ const el=HAND.querySelector('[data-id="'+id+'"]'); let x=innerWidth/2, y=innerHeight*.85; if(el){ const r=el.getBoundingClientRect(); x=r.left+r.width/2; y=r.top+r.height/2; }
    const v=new THREE.Vector3(x/innerWidth*2-1, -(y/innerHeight)*2+1, .5).unproject(cam), d=v.sub(cam.position).normalize(); return cam.position.clone().add(d.multiplyScalar(1.6)); }
  const pileTop=()=>{ const w=new THREE.Vector3(); disc.getWorldPosition(w); w.y+=.02+pileM.length*(CT+.0015); return w; };
  async function drawCards(i, n, why){ const p=G.P[i]; for(let j=0;j<n;j++){ if(gone) return; refill(); const k=G.draw.pop(); if(!k) break; const from=new THREE.Vector3(); drawPile.getWorldPosition(from); from.y+=.12;
      try{ SFX.noise(.08,.03,1800); }catch(e){} if(i===0) G.st.drawn++;
      await fly(k, i===0 && false ? true : false, from, seatPos(i), .26, {arc:.3, r0:new THREE.Euler(0,.12,0), r1:new THREE.Euler(i===0?-1.1:-.3,0,0)});
      p.h.push(k); if(i===0){ newIds[k.id]=1; drawHand(); } else fan(SEATS[i], p.h.length); plates(); }
    if(p.h.length>1) p.called=false; }
  async function play(i, k, col){ const p=G.P[i]; p.h=p.h.filter(q=>q.id!==k.id); G.busy=true; cmd();
    const from=i===0?myCardPos(k.id):seatPos(i); if(i===0) drawHand(); else fan(SEATS[i], p.h.length); plates();
    try{ SFX.noise(.12,.05,2600,.6,900); }catch(e){}
    await fly(k, true, from, pileTop(), i===0?.34:.42, {arc:i===0?.35:.5, r0:new THREE.Euler(i===0?-1.1:-.6,0,.3), r1:new THREE.Euler(0,(Math.random()-.5)*.7,0)});
    if(gone) return; G.pile.push(k); G.top=k; pileAdd(k); setCur(isW(k)?col:k.c); pop();
    try{ SFX.tone(isW(k)?520:440,.1,"triangle",.05,isW(k)?1040:880); if(isW(k)) [523,659,784,988].forEach((f,j)=>SFX.tone(f,.12,"triangle",.035,0,j*.05)); }catch(e){}
    const nm=i===0?"내가":esc(p.nm)+"(이)가"; feed((i===0?"🙋 ":"")+nm+' <b>'+kname(k)+'</b>'+(isW(k)?' → '+KO[col]:''), isW(k)?col:k.c);
    if(i===0){ G.st.play++; if(k.v==="d2"||k.v==="wild4") G.st.atk++; if(k.v==="rev") G.st.rev++; if(isW(k)) G.st.wild++; }
    else react(i, "grin", 1.2);
    if(!p.h.length){ return endGame(i); }
    if(p.h.length===1) await oneRule(i);
    if(gone || G.over) return;
    let skip=false; const t=nextI(i);
    if(k.v==="skip"){ skip=true; react(t,"wow"); feed('⊘ '+esc(G.P[t].nm)+' 건너뛰어요', k.c); if(t===0) banner("⊘ 건너뛰기!", "이번엔 쉬어요"); }
    else if(k.v==="rev"){ G.dir*=-1; feed('⇄ 방향이 바뀌었어요', k.c); drawTop(); }
    else if(k.v==="d2"||k.v==="wild4"){ skip=true; const n=k.v==="d2"?2:4; react(t,"wow",2.2); if(t!==0 && Math.random()<.6) later(.3,()=>emote(t,"😱")); if(t===0) banner("😮 +"+n+"!", n+"장 받고 한 번 쉬어요"); await wait(.25); await drawCards(t, n); feed('😱 '+esc(G.P[t].nm)+' +'+n+'장', isW(k)?col:k.c); }
    G.busy=false; await wait(.25); advance(skip); }
  /* ☝️ 한 장! — 나: 2초 안에 누르기(미리 눌러도 됨) · 봇: 가끔 깜빡 */
  async function oneRule(i){ const p=G.P[i];
    if(i===0){ if(!p.called){ G.one.need=true; G.one.t=fast?.01:2.2; cmd(); while(G.one.need && G.one.t>0 && !gone){ await wait(.05); } G.one.need=false; }
      if(!p.called){ feed('😅 「한 장!」을 깜빡했어요 → 2장'); banner("😅 깜빡!", "「☝️ 한 장!」을 안 눌러서 2장 받아요"); await wait(.5); await drawCards(0,2); } else feed('☝️ 내가 「한 장!」', null); cmd(); return; }
    if(Math.random()<(EASY?.72:.88)){ p.called=true; feed('☝️ '+esc(p.nm)+' 「한 장!」'); emote(i,"😝"); try{ SFX.tone(880,.12,"square",.03); }catch(e){} }
    else { await wait(.6); feed('😅 '+esc(p.nm)+' 「한 장!」 깜빡 → 2장'); react(i,"wow",1.8); await drawCards(i,2); } }
  function callOne(){ const me=G.P[0]; if(G.over) return; if(G.one.need){ me.called=true; G.one.need=false; } else if(G.myTurn && me.h.length===2) me.called=true; else return; emote(0,"☝️"); try{ SFX.tone(880,.12,"square",.04); SFX.tone(1320,.12,"square",.03,0,.08); }catch(e){} cmd(); }
  async function myPlay(k, col){ if(!G.myTurn || G.busy || G.over) return; G.myTurn=false; myArc.visible=false; $(".cpPick").classList.remove("on"); await play(0, k, col); }
  async function myDraw(){ if(!G.myTurn || G.busy || G.over) return; if(G.drew){ G.myTurn=false; myArc.visible=false; feed('⏭ 내가 넘겼어요'); advance(false); return; }
    G.busy=true; cmd(); G.drew=true; await drawCards(0,1); G.busy=false; handSig=""; drawHand(); hint(); cmd();
    if(!G.P[0].h.some(k=>okCard(k,G.top,G.cur))){ await wait(.7); if(G.myTurn && !G.over){ G.myTurn=false; myArc.visible=false; feed('⏭ 낼 카드가 없어서 넘겨요'); advance(false); } } }
  const TURN_T=30;
  function advance(skip){ if(G.over || gone) return; G.turn=nextI(G.turn, skip?2:1); G.hist.push(G.P.map(p=>p.h.length)); beginTurn(); }
  function beginTurn(){ const i=G.turn, p=G.P[i]; G.drew=false; drawTop(); plates();
    if(p.me){ G.myTurn=true; G.busy=false; G.tleft=TURN_T; myArc.visible=true; banner("⭐ 내 차례! ⭐", (G.P[0].h.some(k=>okCard(k,G.top,G.cur))?KO[G.cur]+(isW(G.top)?'':'이나 '+(typeof G.top.v==="number"?G.top.v:ACTC[G.top.v]))+' 를 내요':'낼 카드가 없어요 → 🃏 뽑기')); try{ SFX.tone(660,.1,"triangle",.04); SFX.tone(990,.14,"triangle",.04,0,.09); }catch(e){} if(auto) later(.3, autoMove); }
    else { G.myTurn=false; myArc.visible=false; later((fast?.01:.75+Math.random()*.6), ()=>botMove(i)); }
    handSig=""; drawHand(); hint(); cmd(); }
  /* 🤖 봇 */
  function choose(i, pl){ if(EASY) return pl[Math.floor(Math.random()*pl.length)];
    const p=G.P[i], nx=G.P[nextI(i)], cnt={}; p.h.forEach(k=>{ if(k.c) cnt[k.c]=(cnt[k.c]|0)+1; }); const danger=nx.h.length<=2 && !nx.me ? 1 : nx.h.length<=2 ? .8 : 0;
    let best=null, bs=-1e9; pl.forEach(k=>{ let s=Math.random()*1.2; if(k.c) s+=(cnt[k.c]|0)*.6; if(typeof k.v==="number") s+=1.5+k.v*.05;
      if(k.v==="skip"||k.v==="d2") s+=danger?5:.5; if(k.v==="rev") s+=danger?2:.3; if(k.v==="wild") s+=danger?1:-4; if(k.v==="wild4") s+=danger?6:-7; if(p.h.length<=2 && isW(k)) s+=3;
      if(s>bs){ bs=s; best=k; } }); return best; }
  function bestCol(i, k){ const cnt={}; G.P[i].h.forEach(q=>{ if(q.c && q.id!==k.id) cnt[q.c]=(cnt[q.c]|0)+1; }); let b=null; CS.forEach(c=>{ if(!b || (cnt[c]|0)>(cnt[b]|0)) b=c; }); return (cnt[b]|0)>0?b:CS[Math.floor(Math.random()*4)]; }
  async function botMove(i){ if(G.over || gone || G.turn!==i) return; const p=G.P[i]; let pl=p.h.filter(k=>okCard(k,G.top,G.cur));
    if(!pl.length){ await drawCards(i,1); pl=p.h.filter(k=>okCard(k,G.top,G.cur)); if(!pl.length){ feed('⏭ '+esc(p.nm)+' 넘겨요'); await wait(.3); return advance(false); } await wait(.45); }
    const k=choose(i,pl); await play(i, k, isW(k)?bestCol(i,k):null); }
  /* 시험용 자동 (내 차례도 봇처럼) */
  let auto=false;
  async function autoMove(){ if(!G.myTurn || G.over) return; const me=G.P[0], pl=me.h.filter(k=>okCard(k,G.top,G.cur));
    if(me.h.length===2 && pl.length) callOne();
    if(!pl.length){ await myDraw(); const p2=me.h.filter(k=>okCard(k,G.top,G.cur)); if(p2.length && G.myTurn){ const k=p2[0]; if(isW(k)) await myPlay(k, bestCol(0,k)); else await myPlay(k); } return; }
    const k=choose(0,pl); if(isW(k)) await myPlay(k, bestCol(0,k)); else await myPlay(k); }

  /* ══ 끝 ══ */
  async function endGame(w){ G.over=true; G.busy=true; G.myTurn=false; myArc.visible=false; G.hist.push(G.P.map(p=>p.h.length)); drawTop(); plates(); cmd(); hint(); handSig=""; drawHand();
    const order=[0,1,2,3].sort((a,b)=>(a===w?-1:b===w?1:G.P[a].h.length-G.P[b].h.length)); const rank=order.indexOf(0)+1;
    [1,2,3].forEach(i=>{ const s=SEATS[i]; if(!s || !s.P) return; if(i===w){ arms(s.P,"yay"); s.P.setExpr("grin"); s.hand.visible=false; } else { arms(s.P,w===0?"clap":"hold"); s.P.setExpr(w===0?"wow":"smile"); } s.actT=99; });
    if(w===0){ confetti(LOW?70:150); banner("🎉 다 냈다!", ""); try{ SFX.win(); }catch(e){} } else { banner("🏁 "+esc(G.P[w].nm)+" 다 냈어요!", ""); try{ SFX.tone(392,.25,"triangle",.05); SFX.tone(330,.35,"triangle",.05,0,.2); }catch(e){} }
    await wait(fast?.01:1.6); if(gone) return;
    const COINS=[10,6,5,4][rank-1]; const streak=w===0?((B0.cs|0)+1):0;
    const got=api.end({title:rank===1?"🏆 1등!":rank+"등", sub:"컬러팡", rows:order.map(i=>[G.P[i].nm, i===w?"다 냈어요":G.P[i].h.length+"장", i===0]), coins:COINS,
      upd:(b,t)=>{ t.win=(t.win|0)+(w===0?1:0); t.cards=(t.cards|0)+G.st.play; t.atk=(t.atk|0)+G.st.atk; b.cs=streak; b.bs=Math.max(b.bs|0, streak); b.top=Math.min(b.top||9, rank); }});
    try{ const r=document.getElementById("mgRes"); if(r) r.classList.remove("on"); }catch(e){}
    endUI(order, w, rank, got, streak); }
  function graph(){ const H=G.hist, n=H.length, w=300, h=86, mx=Math.max(7,...H.map(r=>Math.max(...r))), X=i=>8+i*(w-16)/Math.max(1,n-1), Y=v=>8+(mx-v)/mx*(h-16);
    let s='<svg viewBox="0 0 '+w+' '+h+'" width="100%" height="'+h+'" preserveAspectRatio="none" style="display:block;background:#f6ecd6;border-radius:10px">';
    for(let k=1;k<4;k++) s+='<line x1="8" x2="'+(w-8)+'" y1="'+(8+k*(h-16)/4)+'" y2="'+(8+k*(h-16)/4)+'" stroke="#e2d2b4" stroke-width="1"/>';
    [3,2,1,0].forEach(j=>{ const pts=H.map((r,i)=>X(i).toFixed(1)+','+Y(r[j]).toFixed(1)).join(" "); s+='<polyline fill="none" stroke="'+INK+'" stroke-width="'+(j?4.5:6.5)+'" stroke-linejoin="round" points="'+pts+'"/><polyline fill="none" stroke="'+G.P[j].col+'" stroke-width="'+(j?2.4:3.8)+'" stroke-linejoin="round" points="'+pts+'"/>'; });
    return s+'</svg>'; }
  function endUI(order, w, rank, got, streak){ const E=$(".cpEnd"), r2=MG.rec(), lg=league(((r2.t.card)||{}).win);
    const emb=rank===1?"승리!":rank===2?"2등!":rank===3?"3등!":"4등"; const sub=rank===1?"카드를 제일 먼저 다 냈어요":"아깝다! 카드가 "+G.P[0].h.length+"장 남았어요";
    E.innerHTML='<div class="dim"></div>'+(rank===1?'<div class="rays"></div>':'')+'<div class="box"><div class="emb r'+rank+'">'+emb+'</div>'+(streak>=2?'<div class="rib">🔥 '+streak+'연승!</div>':'')+'<div class="sub">'+sub+'</div>'
      +'<div class="card"><div class="rk">'+order.map((i,j)=>'<i>'+(["🥇","🥈","🥉","4"][j])+'</i><span class="'+(i===0?"me":"")+'"><b class="dt" style="background:'+G.P[i].col+'"></b>'+esc(G.P[i].nm)+(G.P[i].bot?' 🤖':'')+'</span><em>'+(i===w?"다 냈어요!":G.P[i].h.length+"장")+'</em>').join("")+'</div>'
      +'<div class="gr"><div class="t">📈 남은 카드<em>판이 어떻게 흘렀나</em></div>'+graph()+'</div>'
      +'<div class="rew">'+(got>0?'<span>🪙 +'+got+'</span>':'<span class="off">🪙 오늘 상 끝</span>')+(G.st.atk?'<span>⚔️ 공격 '+G.st.atk+'번</span>':'')+'<span>🃏 낸 카드 '+G.st.play+'</span></div>'
      +'<div class="lv">'+lg.ic+' '+lg.nm+'<div class="bar"><i style="width:'+Math.round(lg.p*100)+'%"></i></div>'+(lg.next?lg.next+' <small>'+lg.left+'번 더 이기면</small>':'최고!')+'</div>'
      +'<div class="bt"><button class="out">🏝 나가기</button><button class="go">🔄 한 판 더</button></div></div></div>';
    E.classList.add("on"); E.querySelector(".out").onclick=()=>MG.exit(); E.querySelector(".go").onclick=()=>api.restart(Object.assign({}, api.opt)); }

  /* ══ 시작 ══ */
  $(".cpPor .who").textContent=(G.P[0].nm)+" · "+LG.ic+" "+LG.nm;
  let ready=false;
  loadImgs().then(()=>{ if(gone) return; TEX.forEach(e=>{ try{ e.t.dispose(); e.m.dispose(); }catch(_){} }); TEX.clear();   /* 그림이 다 온 뒤 다시 */
    backFM.map=faceMat(null).map; backFM.needsUpdate=true; drawPile.userData.st.material[2]=faceMat(null); drawPile.children[1].material=[sideM,faceMat(null),faceMat(null)];
    $(".cpLoad").remove(); deal(); });
  async function deal(){ G.draw=shuffle(mkDeck()); ready=true; drawTop(); plates(); [1,2,3].forEach(i=>fan(SEATS[i],0));
    for(let r=0;r<7;r++) for(let i=0;i<4;i++){ const k=G.draw.pop(); G.P[i].h.push(k); if(i>0) fan(SEATS[i], G.P[i].h.length); }
    let k; do{ k=G.draw.pop(); if(typeof k.v!=="number"){ G.draw.unshift(k); k=null; } }while(!k); G.pile=[k]; G.top=k; pileAdd(k); setCur(k.c); glowCol.copy(glowTo);
    feed('🃏 첫 카드: <b>'+kname(k)+'</b>', k.c); G.turn=Math.floor(Math.random()*4); G.hist.push(G.P.map(p=>p.h.length)); try{ SFX.noise(.4,.04,2200,.5,800); }catch(e){}
    handSig=""; drawHand(); await wait(.6); beginTurn(); }

  /* ══ 매 프레임 ══ */
  let fr=0, tAll=0; const e0=new THREE.Euler(), q0=new THREE.Quaternion(), q1=new THREE.Quaternion();
  function tick(dt){ if(paused || gone) return; const steps=fast?20:1;
    for(let s=0;s<steps;s++){ const d=fast?.05:dt; tAll+=d;
      for(let i=TM.length-1;i>=0;i--){ TM[i].t-=d; if(TM[i].t<=0){ const f=TM[i].fn; TM.splice(i,1); try{ f(); }catch(e){ console.warn("CP", e); } } }
      for(let i=FLY.length-1;i>=0;i--){ const f=FLY[i]; f.t+=d/f.dur; const t=Math.min(1,f.t), e=t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
        f.m.position.lerpVectors(f.from,f.to,e); f.m.position.y+=Math.sin(t*Math.PI)*f.arc; q0.setFromEuler(f.r0); q1.setFromEuler(f.r1); f.m.quaternion.copy(q0).slerp(q1,e);
        if(t>=1){ FLY.splice(i,1); scene.remove(f.m); f.res(); } }
      if(G.myTurn && !G.busy && !G.over && ready){ G.tleft-=d; if(G.tleft<=0){ G.tleft=TURN_T; if(!G.drew) myDraw(); else { G.myTurn=false; myArc.visible=false; feed('⏰ 시간이 다 돼서 넘겨요'); advance(false); } } }
      if(G.one.need) G.one.t-=d; }
    if(banT>0){ banT-=dt; if(banT<=0) $(".cpBan").classList.remove("on"); }
    if(toastT>0){ toastT-=dt; if(toastT<=0){ $(".cpHint").classList.remove("warn"); hint(); } }
    if(replyT>0) replyT-=dt;
    glowCol.lerp(glowTo, Math.min(1,dt*6)); glowM.color.copy(glowCol); haloM.color.copy(glowCol);
    if(popS.visible){ popT+=dt; const k=popT<.15?popT/.15:1; popS.scale.setScalar(.65*(.6+.4*k)*(1+.08*Math.sin(popT*20))); popM.opacity=popT>.55?Math.max(0,1-(popT-.55)/.25):1; if(popT>.8) popS.visible=false; }
    SEATS.forEach(s=>{ if(!s || !s.P) return; s.t+=dt; const th=G.turn===s.i && !G.over; s.P.g.position.y=.25+(th?Math.abs(Math.sin(s.t*5))*.025:Math.sin(s.t*1.6)*.006); s.P.head.rotation.y=th?Math.sin(s.t*2)*.15:Math.sin(s.t*.7)*.08;
      if(s.actT>0 && s.actT<90){ s.actT-=dt; if(s.actT<=0) s.P.setExpr(s.P.expr0||"smile"); } });
    for(const m of CONF){ m.position.y-=m.userData.v*dt; m.rotation.x+=m.userData.s*dt; m.rotation.y+=dt*2; if(m.position.y<TY+.02) m.position.y=TY+.02; }
    const bar=$(".cpBar i"); if(bar) bar.style.width=(G.myTurn&&!G.over?Math.max(0,G.tleft/TURN_T*100):0)+"%";
    fitCam(); platePos(); }
  /* 그리기: 내 얼굴(8프레임마다 작은 그림으로 옮김) → 탁자 */
  function render(rn){ fr++; const box=$(".cpPor"); if(ME && box && (fr%8===1 || porCv.width<4)){ const r=box.getBoundingClientRect(), pr=rn.getPixelRatio(), sz=Math.max(8,Math.round(r.width-8));
      if(porCv.width!==Math.round(sz*pr)){ porCv.width=porCv.height=Math.round(sz*pr); }
      try{ const H=rn.domElement.height/pr; rn.setScissorTest(true); rn.setScissor(0,0,sz,sz); rn.setViewport(0,0,sz,sz); rn.render(PS,PC); porG.clearRect(0,0,porCv.width,porCv.height); porG.drawImage(rn.domElement,0,rn.domElement.height-porCv.height,porCv.width,porCv.height,0,0,porCv.width,porCv.height); }catch(e){}
      rn.setScissorTest(false); const c=rn.domElement; rn.setViewport(0,0,c.width/rn.getPixelRatio(),c.height/rn.getPixelRatio()); }
    MG.draw(scene, cam); }
  function dispose(){ gone=true; TM.length=0; FLY.length=0; try{ U.classList.remove("cpOn"); HUD.remove(); }catch(e){} disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); TEX.forEach(e=>{ try{ e.t.dispose(); e.m.dispose(); }catch(_){} }); TEX.clear(); }
  return {scene, cam, tick, render, dispose, pause:(v)=>{ paused=!!v; }, G, SEATS, okCard, get auto(){ return auto; }, set auto(v){ auto=!!v; if(auto && G.myTurn) later(.1, autoMove); }, set fast(v){ fast=v?1:0; }, get fast(){ return !!fast; }, get ready(){ return ready; }, callOne, myDraw, tapCard, pileM, TEX, FLY, cmd, drawHand}; }

/* ══ 화면 꾸밈 ══ */
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
.cpHand{position:absolute;left:0;right:0;bottom:calc(112px + env(safe-area-inset-bottom));display:flex;justify-content:center;perspective:700px;pointer-events:auto}
.cpHand .in{display:flex;transform:rotateX(16deg);transform-origin:50% 100%}
.cpC{position:relative;flex:none;transform:translateY(calc(var(--y,0px) + var(--l,0px))) rotate(var(--r,0deg));transform-origin:50% 140%;filter:drop-shadow(0 6px 4px rgba(0,0,0,.35));transition:transform .15s}
.cpC svg{display:block}
.cpC.no{--l:8px;filter:grayscale(.75) brightness(.9) drop-shadow(0 4px 3px rgba(0,0,0,.3));opacity:.82}
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
.cpEnd .dim{position:fixed;inset:0;background:radial-gradient(ellipse at 50% 30%,rgba(30,20,28,.25),rgba(20,12,20,.8) 70%)}
.cpEnd .rays{position:fixed;left:50%;top:-80px;width:560px;height:560px;transform:translateX(-50%);border-radius:50%;background:repeating-conic-gradient(rgba(255,225,77,.22) 0 9deg,transparent 9deg 22deg);-webkit-mask:radial-gradient(circle,#000 20%,transparent 68%);mask:radial-gradient(circle,#000 20%,transparent 68%);animation:cpSpin 14s linear infinite}
@keyframes cpSpin{to{transform:translateX(-50%) rotate(360deg)}}
.cpEnd .box{position:relative;display:flex;flex-direction:column;align-items:center;padding:calc(64px + env(safe-area-inset-top)) 14px 24px}
.cpEnd .emb{font-size:60px;line-height:1;letter-spacing:6px;color:#ffe14d;-webkit-text-stroke:8px var(--ink);paint-order:stroke fill;filter:drop-shadow(0 0 18px rgba(255,211,107,.85));animation:cpEmb .5s cubic-bezier(.2,1.6,.4,1)}
.cpEnd .emb.r2{color:#dfe8f5}.cpEnd .emb.r3{color:#f0b37a}.cpEnd .emb.r4{color:#cdbfd8;filter:none}
@keyframes cpEmb{from{transform:scale(2.2);opacity:0}}
.cpEnd .rib{margin-top:4px;background:#ff5a5f;color:#fff;border:3px solid var(--ink);border-radius:8px;padding:2px 16px;font-size:15px;box-shadow:0 3px 0 var(--ink);transform:rotate(-2deg)}
.cpEnd .sub{font-size:16px;color:#fff;margin-top:4px;text-shadow:0 2px 0 rgba(0,0,0,.4)}
.cpEnd .card{width:min(360px,100%);margin-top:16px;background:var(--cream);border:4px solid var(--ink);border-radius:22px;box-shadow:0 5px 0 var(--ink);padding:12px;animation:cpUp .4s .15s both}
@keyframes cpUp{from{transform:translateY(30px);opacity:0}}
.cpEnd .rk{display:grid;grid-template-columns:28px 1fr auto;gap:4px 8px;align-items:center;font-size:16px}
.cpEnd .rk i{font-style:normal;font-size:18px;text-align:center}.cpEnd .rk span{display:flex;align-items:center;gap:6px;padding:1px 4px}.cpEnd .rk em{font-style:normal;font-size:13px;color:#7a6a5e}
.cpEnd .rk .me{background:#fff3b0;border-radius:8px}
.cpEnd .dt{width:12px;height:12px;border-radius:50%;border:2px solid var(--ink)}
.cpEnd .gr{margin-top:8px}.cpEnd .gr .t{font-size:14px;display:flex;justify-content:space-between;margin-bottom:3px}.cpEnd .gr .t em{font-style:normal;color:#7a6a5e;font-size:12px}
.cpEnd .rew{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-top:10px}.cpEnd .rew span{background:#fff;border:3px solid var(--ink);border-radius:13px;padding:3px 10px;font-size:15px;box-shadow:0 3px 0 var(--ink);white-space:nowrap}.cpEnd .rew .off{opacity:.6}
.cpEnd .lv{display:flex;align-items:center;gap:8px;margin-top:10px;font-size:14px;white-space:nowrap}.cpEnd .lv small{font-size:11px;color:#7a6a5e}.cpEnd .bar{flex:1;height:14px;border-radius:99px;background:#e9dcc2;border:2px solid var(--ink);overflow:hidden}.cpEnd .bar i{display:block;height:100%;background:linear-gradient(90deg,#c58a4a,#e6b06e)}
.cpEnd .bt{display:flex;gap:9px;margin-top:12px}.cpEnd .bt button{flex:1;height:52px;border-radius:15px;border:3px solid var(--ink);box-shadow:0 4px 0 var(--ink);font-size:18px;background:var(--cream);color:var(--ink)}.cpEnd .bt .go{background:#7bd389}
#cpHud.pad .cpPor{width:118px;height:118px}
#cpHud.pad .cpCmd button{width:70px;height:66px;font-size:13px}#cpHud.pad .cpCmd button span{font-size:26px}
#cpHud.pad .cpHand{bottom:calc(150px + env(safe-area-inset-bottom))}
#cpHud.pad .cpBan{top:calc(110px + env(safe-area-inset-top))}
#cpHud.land .cpCon{background:none;padding-bottom:calc(6px + env(safe-area-inset-bottom))}
#cpHud.land .cpPor{width:70px;height:70px}
#cpHud.land .cpMid{position:absolute;left:50%;bottom:calc(4px + env(safe-area-inset-bottom));width:min(300px,40vw);transform:translateX(-50%)}
#cpHud.land .cpHint{font-size:14px;padding:2px 8px}
#cpHud.land .cpCmd{margin-left:auto;grid-template-columns:repeat(2,1fr)}
#cpHud.land .cpCmd button{width:54px;height:50px}
#cpHud.land .cpHand{bottom:calc(54px + env(safe-area-inset-bottom))}
#cpHud.land .cpBan{top:calc(52px + env(safe-area-inset-top))}
#cpHud.land .cpBan .t{font-size:22px}
#cpHud.land .cpEmo{bottom:calc(120px + env(safe-area-inset-bottom))}
`; document.head.appendChild(st); }

MG.reg("card", {ic:"🃏", nm:"컬러팡", tag:"색깔 카드 게임 · 봇 3명과 · 같은 색이나 같은 숫자를 내요", bg:"linear-gradient(135deg,#ff5a5f,#ffc83d 35%,#3fc46a 65%,#3ea2ff)", big:"🃏🌈",
  how:[["🎨","<b>같은 색</b>이나 <b>같은 숫자</b> 카드를 내요 · 빛나는 카드만 낼 수 있어요"],["⊘","<b>건너뛰기</b> · ⇄ <b>방향 바꾸기</b> · <b>+2</b> 다음 사람이 2장 받아요"],["🌈","<b>무지개</b> = 색을 골라요 · <b>🌈+4</b> 다음 사람이 4장"],["☝️","1장 남으면 <b>「한 장!」</b> 버튼 — 깜빡하면 2장 더!"],["🏆","카드를 <b>먼저 다 내면</b> 이겨요"]],
  opts:[{k:"df", t:"봇 실력", d:"normal", v:[["easy","🐣 쉬움"],["normal","🙂 보통"]]}],
  payTxt:"1등 🪙10 · 2등 🪙6 · 3등 🪙5 · 4등 🪙4",
  bestTxt:(b,t)=>{ const L=league(t.win); return '🏆 이긴 판 '+(t.win|0)+' · 🔥 최고 '+(b.bs|0)+'연승 · '+L.ic+' '+L.nm; },
  ui:{look:false, btns:[]},
  start});
window.CPF={cardSVG, mkDeck, okCard, league, isW};
})();
