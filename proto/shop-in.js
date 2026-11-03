/* ═════════ (v572) 🏪 가게 안 — 사용자: 「파는 곳인데 괴리감 · 가게를 들어가서 하는 게 아니더라 · 가게도 안을 꾸며서 만들어 줘」
   · 상점가 8곳(🐟 👕 🛒 💇 🍦 🛋 🐶 📸) 문 → 페이드 → 가게 안(7×7 방) · 주인(아바타)이 카운터 뒤에서 인사 (영어 + 한국어 · say)
   · 들어가면 카운터까지 걸어가서 원래 가게 창이 열림 (값·경제 코드는 그대로) · 창을 닫으면 가게 안을 걸어 다니며 물건을 누르면 영어 이름
   · 🚪 나가기(문·이름표·아래 단추) → 섬의 그 가게 문 앞 · 방 껍데기(바닥·벽 2·문)는 한 번만 만들고 가게마다 그림·장식만 바꿈
   · 장식 = 도형 → 재료마다 한 덩어리로 합침 (그리는 횟수 ↓) · 나갈 때 버림 · TOON.scan 으로 섬·집과 같은 툰
   · house.html 은 장소 PL.shop 과 go() · walkTo · leaveBy · 이름표(LBL_DEF) 를 그대로 씀 */
const SHOPIN=(()=>{
  if(!window.ISLE) return null;
  const N=7, H=2.6, T=0.18, DOOR=[0,N-1], SPOTC=[3,2];   /* 문 = 왼쪽 벽 맨 앞 칸 · 손님 자리 = 카운터 앞 */
  const G=new THREE.Group(); G.name="shopIn"; G.visible=false; scene.add(G);
  const occ=new Uint8Array(N*N);
  PL.shop={key:"shop", N, g:G, h:H, name:"🏪 가게", blocked:(x,z)=>!!occ[z*N+x], start:[1,N-1], pitch:0.6, sky:0xf6e6cf};
  Object.defineProperty(PL.shop, "pitch", {get:()=>VH()>innerWidth*1.5 ? 0.86 : VH()>innerWidth ? 0.7 : 0.6});   /* 세로 휴대폰 = 더 위에서 (방이 화면을 더 채움) */
  let cur=null, deco=null, keeper=null, bub=null, words=[], anims=[], own=[], tA=0, run=false, lastT=0;

  /* ── 도형 도우미 (OWN = 나만 쓰는 모양 → 합친 뒤 버림 · rbox/M 은 집 것과 같이 씀) ── */
  const OWN=g=>{ g.userData.own=1; return g; };
  const bx=(w,h,d)=>OWN(new THREE.BoxGeometry(w,h,d)), cy=(a,b,h,s)=>OWN(new THREE.CylinderGeometry(a,b,h,s||12)),
        bl=(r,w,h)=>OWN(new THREE.SphereGeometry(r,w||12,h||9)), cn=(r,h,s)=>OWN(new THREE.ConeGeometry(r,h,s||12)), to=(r,t,a)=>OWN(new THREE.TorusGeometry(r,t,8,22,a||Math.PI*2));
  const rb=(w,h,d,r)=>rbox(w,h,d,r==null?Math.min(.05,w/3,h/3,d/3):r);
  function p(g,geo,col,x,y,z,o){ o=o||{}; const m=new THREE.Mesh(geo, o.mat||M(col,o.opt)); m.position.set(x,y,z); m.rotation.set(o.rx||0,o.ry||0,o.rz||0); if(o.s) m.scale.set(o.s[0],o.s[1],o.s[2]); m.castShadow=!o.nocast; m.receiveShadow=true; g.add(m); return m; }
  const GL=()=>M(0xcdeeff,{transparent:true, opacity:.32, roughness:.08}), LT=c=>M(c||0xfff4c4,{emissive:c||0xffe9a0, emissiveIntensity:.7});
  function tex(w,h,draw,rep){ const t=canvasTex(w,h,draw,rep); own.push(t); return t; }
  function pic(g,w,h,draw,x,y,z,ry,px){ const m=new THREE.MeshStandardMaterial({map:tex(px||Math.round(256*w/Math.max(w,h)),px?Math.round(px*h/w):Math.round(256*h/Math.max(w,h)),draw), roughness:.8}); own.push(m);
    const pl=new THREE.Mesh(OWN(new THREE.PlaneGeometry(w,h)), m); pl.position.set(x,y,z); pl.rotation.y=ry||0; pl.receiveShadow=true; g.add(pl); return pl; }
  function rug(g,x,z,w,h,draw){ const m=new THREE.MeshStandardMaterial({map:tex(256,Math.round(256*h/w),draw), roughness:1, transparent:true, alphaTest:.5}); own.push(m);
    const pl=new THREE.Mesh(OWN(new THREE.PlaneGeometry(w,h)), m); pl.rotation.x=-Math.PI/2; pl.position.set(x,.014,z); pl.receiveShadow=true; g.add(pl); return pl; }
  const roundRug=(c1,c2,fx)=>(c,w,h)=>{ c.fillStyle="#3b2433"; c.beginPath(); c.ellipse(w/2,h/2,w/2-2,h/2-2,0,0,7); c.fill(); c.fillStyle=c1; c.beginPath(); c.ellipse(w/2,h/2,w/2-8,h/2-8,0,0,7); c.fill(); c.strokeStyle=c2; c.lineWidth=10; c.beginPath(); c.ellipse(w/2,h/2,w/2-26,h/2-26,0,0,7); c.stroke(); if(fx) fx(c,w,h); };
  function grp(par,x,z,ry,y){ const g=new THREE.Group(); g.position.set(x,y||0,z); g.rotation.y=ry||0; par.add(g); return g; }
  const blk=(...L)=>L.forEach(([x,z])=>{ if(x>=0&&z>=0&&x<N&&z<N) occ[z*N+x]=1; });
  function W(o,en,ko,ic){ words.push({o,en,ko,ic,box:null}); return o; }   /* 누르면 영어 이름 */
  const rr=(g,x,y,w,h,r)=>{ g.beginPath(); g.moveTo(x+r,y); g.arcTo(x+w,y,x+w,y+h,r); g.arcTo(x+w,y+h,x,y+h,r); g.arcTo(x,y+h,x,y,r); g.arcTo(x,y,x+w,y,r); g.closePath(); };

  /* ── 작은 물건 ── */
  function fish(g,x,y,z,col,ry,s){ const f=grp(g,x,z,ry||0,y); s=s||1; p(f,bl(.1*s,10,8),col,0,0,0,{s:[1.6,.75,.65]}); p(f,cn(.07*s,.12*s,6),col,-.2*s,0,0,{rz:-Math.PI/2}); p(f,bl(.018*s,6,5),0x1a1a24,.1*s,.025*s,.045*s); return f; }
  function shirt(g,x,y,z,col,ry){ const s=grp(g,x,z,ry||0,y); p(s,rb(.34,.4,.07,.03),col,0,-.2,0); [-1,1].forEach(k=>p(s,rb(.13,.2,.07,.03),col,k*.2,-.08,0,{rz:k*.7})); p(s,to(.05,.012,Math.PI),0x8a8f99,0,.04,0,{nocast:1}); p(s,bx(.36,.012,.012),0x8a8f99,0,0,0,{nocast:1}); return s; }
  function crate(g,x,y,z,fill,col,n){ const c=grp(g,x,z,0,y); p(c,rb(.5,.2,.36,.02),0x9a6a40,0,.1,0); for(let i=0;i<(n||6);i++){ const a=i%3, b=Math.floor(i/3); fill(c,-.15+a*.15,.24,-.08+b*.16,col,i); } return c; }
  const apple=(c,x,y,z,col)=>p(c,bl(.085,9,7),col,x,y+.02,z), carrot=(c,x,y,z)=>{ p(c,cn(.05,.24,6),0xff8a2a,x,y+.02,z,{rz:Math.PI/2}); p(c,cn(.03,.08,4),0x4fb85e,x+.15,y+.02,z,{rz:-Math.PI/2}); }, cabbage=(c,x,y,z)=>p(c,bl(.1,9,7),0x7fd05a,x,y+.03,z);
  function stool(g,x,z,col){ const s=grp(g,x,z); p(s,cy(.18,.18,.07,14),col,0,.5,0); p(s,cy(.03,.03,.48,6),0xb8bcc6,0,.25,0); p(s,cy(.14,.14,.03,12),0xb8bcc6,0,.015,0); return s; }
  function plant(g,x,z,s){ const q=grp(g,x,z); s=s||1; p(q,cy(.17*s,.13*s,.3*s,10),0xd8794a,0,.15*s,0); [[0,.55,0,.2],[.12,.44,.06,.14],[-.12,.46,-.04,.15]].forEach(([a,b,c,r])=>p(q,bl(r*s,9,7),0x5dbb63,a*s,b*s,c*s)); return q; }
  function ball(g,x,y,z,c1,c2,r){ const b=grp(g,x,z,0,y); p(b,bl(r,12,9),c1,0,r,0); p(b,to(r*.99,r*.18),c2,0,r,0,{rx:Math.PI/2,nocast:1}); return b; }
  function puppy(g,x,y,z,col,ry,cat){ const a=grp(g,x,z,ry||0,y); p(a,bl(.15,10,8),col,0,.14,0,{s:[1,.85,1.25]}); p(a,bl(.12,10,8),col,0,.3,.14);
    if(cat) [-1,1].forEach(k=>p(a,cn(.045,.09,5),col,k*.07,.42,.13)); else [-1,1].forEach(k=>p(a,bl(.05,7,6),0x6b4a30,k*.11,.31,.12,{s:[.6,1.3,.8]}));
    [-1,1].forEach(k=>p(a,bl(.017,6,5),0x1a1a24,k*.045,.32,.25)); p(a,bl(.022,6,5),0x3b2433,0,.29,.26); p(a,cy(.02,.012,.16,5),col,0,.2,-.2,{rx:-.8}); return a; }

  /* ── 공통: 카운터 · 간판 · 주인 ── */
  function counter(g,k,TH){ const c=grp(g,3.5,1.45); p(c,rb(2.9,.72,.6,.05),TH.ctr||0xc98f5a,0,.36,0); p(c,rb(3.02,.07,.7,.03),TH.top||0xfff3dd,0,.75,0); p(c,rb(2.7,.12,.02,.01),TH.col,0,.5,.31);
    blk([2,1],[3,1],[4,1],[2,0],[3,0],[4,0]); return c; }
  function sign(g,TH){ return pic(g,2.6,.78,(c,w,h)=>{ const col="#"+new THREE.Color(TH.col).getHexString(); c.fillStyle="#3b2433"; rr(c,0,0,w,h,30); c.fill(); c.fillStyle=col; rr(c,8,8,w-16,h-16,24); c.fill();
      c.fillStyle="rgba(255,255,255,.28)"; rr(c,16,14,w-32,h*.32,18); c.fill(); c.textAlign="center"; c.textBaseline="middle"; c.fillStyle="#fff"; c.strokeStyle="#3b2433"; c.lineWidth=10; c.font='900 74px "Jua","Arial Rounded MT Bold",sans-serif';
      c.strokeText(TH.en,w/2,h*.42); c.fillText(TH.en,w/2,h*.42); c.font='800 36px "Jua",sans-serif'; c.lineWidth=7; c.strokeText(TH.ko,w/2,h*.78); c.fillText(TH.ko,w/2,h*.78); }, 3.5,2.12,.03,0,768); }
  function mkKeeper(TH){ const k=Object.assign(buildAvatar(TH.av), {face:0, t:0, moving:false, act:"idle", blinkT:1.5}); k.g.position.set(3.5,0,.62); k.g.rotation.y=0; k.g.userData.noFade=1; G.add(k.g); return k; }
  function bubble(txt){ if(bub){ G.remove(bub.s); bub.s.material.map.dispose(); bub.s.material.dispose(); bub=null; }
    const cv=document.createElement("canvas"); cv.width=512; cv.height=256; const g=cv.getContext("2d"); g.fillStyle="#3b2433"; rr(g,4,4,504,200,44); g.fill(); g.fillStyle="#fffdf7"; rr(g,12,12,488,184,38); g.fill();
    g.fillStyle="#3b2433"; g.beginPath(); g.moveTo(228,200); g.lineTo(256,252); g.lineTo(286,200); g.fill(); g.fillStyle="#fffdf7"; g.beginPath(); g.moveTo(238,190); g.lineTo(256,232); g.lineTo(276,190); g.fill();
    g.fillStyle="#3b2433"; g.textAlign="center"; g.textBaseline="middle"; const ws=txt.split(" "), L=[""]; g.font='800 52px "Jua",sans-serif'; ws.forEach(w=>{ const t=(L[L.length-1]+" "+w).trim(); if(g.measureText(t).width>440 && L[L.length-1]) L.push(w); else L[L.length-1]=t; });
    let fs=52; while(fs>26 && L.some(l=>g.measureText(l).width>460)){ fs-=2; g.font='800 '+fs+'px "Jua",sans-serif'; } L.slice(0,3).forEach((l,i,A)=>g.fillText(l,256,104+(i-(A.length-1)/2)*(fs+8)));
    const t=new THREE.CanvasTexture(cv); t.encoding=THREE.sRGBEncoding; const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t, depthTest:false})); s.renderOrder=12; s.userData.noFade=1; s.position.set(3.5,2.5,.75); s.scale.set(.01,.01,1); G.add(s); bub={s, t:0}; dirty=true; }

  /* ── 가게 8곳 — 바닥·벽 그림 · 주인 · 장식 (로컬 좌표 = 방 칸: x 오른쪽 위 · z 왼쪽 아래 · 뒤 벽 z=0 · 왼 벽 x=0 · 문 = 왼 벽 앞) ── */
  const tiles=(a,b,n,gr)=>(c,w,h)=>{ const s=w/n; for(let y=0;y<n;y++) for(let x=0;x<n;x++){ c.fillStyle=(x+y)%2?a:b; c.fillRect(x*s,y*s,s,s); } if(gr){ c.fillStyle=gr; for(let i=0;i<=n;i++){ c.fillRect(i*s-1,0,2,h); c.fillRect(0,i*s-1,w,2); } } };
  const planks=(cols,line)=>(c,w,h)=>{ const n=8, ph=h/n; for(let i=0;i<n;i++){ c.fillStyle=cols[i%cols.length]; c.fillRect(0,i*ph,w,ph); c.fillStyle=line; c.fillRect(0,i*ph,w,3); c.fillRect((i*97)%w,i*ph,3,ph); } };
  const wallOf=(top,bot,band,fx)=>(c,w,h)=>{ c.fillStyle=top; c.fillRect(0,0,w,h); if(fx) fx(c,w,h*.62); c.fillStyle=bot; c.fillRect(0,h*.62,w,h*.38); c.fillStyle="rgba(0,0,0,.08)"; for(let x=0;x<w;x+=32) c.fillRect(x,h*.62,2,h*.38); c.fillStyle=band; c.fillRect(0,h*.6,w,14); };
  const dots=(col,r,st)=>(c,w,h)=>{ c.fillStyle=col; for(let y=st/2;y<h;y+=st) for(let x=((y/st)%2)*st/2+st/4;x<w;x+=st){ c.beginPath(); c.arc(x,y,r,0,7); c.fill(); } };
  const stripes=(col,sw)=>(c,w,h)=>{ c.fillStyle=col; for(let x=0;x<w;x+=sw*2) c.fillRect(x,0,sw,h); };
  const TH={
    fish:{en:"FISH SHOP", ko:"생선 가게", col:0x3f8fe0, sky:0xcfe9f7, ctr:0x5a8fc0, top:0xf4fbff, act:"팔기",
      floor:tiles("#e4f4ff","#bfe2f7",8,"rgba(80,130,170,.35)"), wall:wallOf("#7cc4ec","#c98f5a","#ffffff",(c,w,h)=>{ c.strokeStyle="rgba(255,255,255,.55)"; c.lineWidth=6; for(let y=40;y<h;y+=70){ c.beginPath(); for(let x=0;x<=w;x+=8) c.lineTo(x,y+Math.sin(x/w*Math.PI*4)*10); c.stroke(); } }),
      av:{skin:2, hair:"short", hc:0, style:"overalls", top:1, pc:0, sc:3, hat:"cap", acc:"none", expr:"grin"}, nm:"Finn", hi:["Welcome! Do you have fish to sell?","어서 와요! 팔 물고기 있어요?"]},
    clothes:{en:"CLOTHES", ko:"옷 가게", col:0xff6b8a, sky:0xfde3ea, ctr:0xffffff, top:0xffd6e0, act:"옷 사기",
      floor:planks(["#f1d2a8","#e8c597","#f6dcb6"],"rgba(150,95,45,.25)"), wall:wallOf("#ffe9ef","#ffb3c6","#ffffff",stripes("rgba(255,170,195,.45)",22)),
      av:{skin:0, hair:"long", hc:6, style:"dress", top:6, sc:2, hat:"none", acc:"ribbon", expr:"smile"}, nm:"Coco", hi:["Hello! Try on some clothes!","안녕하세요! 옷을 입어 봐요!"]},
    mart:{en:"MART", ko:"마트", col:0x4fb85e, sky:0xe3f5df, ctr:0x4fb85e, top:0xf4f4f4, act:"장보기",
      floor:tiles("#ffffff","#d4efd0",8,"rgba(90,150,90,.25)"), wall:wallOf("#fff8e6","#8fd47a","#ffffff",dots("rgba(120,190,110,.25)",6,46)),
      av:{skin:1, hair:"short", hc:1, style:"tee", top:2, pc:1, sc:0, hat:"cap", acc:"none", expr:"grin"}, nm:"Ben", hi:["Welcome! We have fresh food.","어서 와요! 신선한 음식이 있어요."]},
    hair:{en:"HAIR SALON", ko:"미용실", col:0xff8fc8, sky:0xf6e1f0, ctr:0x3b3b48, top:0xffffff, act:"머리 하기",
      floor:tiles("#2f2f3a","#f4f0ea",8), wall:wallOf("#ffe0f0","#e9b6d6","#ffffff",dots("rgba(255,255,255,.7)",5,40)),
      av:{skin:0, hair:"bun", hc:5, style:"tee", top:5, pc:1, sc:3, hat:"none", acc:"flower", expr:"smile"}, nm:"Rosie", hi:["Hi! Do you want a new hairstyle?","안녕! 새 머리 모양 해 볼래요?"]},
    snack:{en:"SNACK BAR", ko:"간식 가게", col:0xff9ec0, sky:0xfde8f0, ctr:0xffffff, top:0xff9ec0, act:"주문하기",
      floor:tiles("#fff3c4","#ffd6e4",8,"rgba(255,255,255,.6)"), wall:wallOf("#d8f6ec","#ff9ec0","#ffffff",dots("rgba(255,255,255,.8)",7,44)),
      av:{skin:1, hair:"pigtails", hc:2, style:"dress", top:3, sc:1, hat:"none", acc:"ribbon", expr:"grin"}, nm:"Sunny", hi:["Hi! What snack do you want?","안녕! 어떤 간식 줄까요?"]},
    furn:{en:"FURNITURE", ko:"가구점", col:0xf2b632, sky:0xf6ead6, ctr:0xb07a4a, top:0xe8c79a, act:"가구 사기",
      floor:(c,w,h)=>{ c.fillStyle="#b9824e"; c.fillRect(0,0,w,h); const L=64,T2=21; for(let y=-L;y<h+L;y+=T2*2) for(let x=-L;x<w+L;x+=L) [0,1].forEach(a=>{ c.save(); c.translate(x+(a?T2:0),y+(a?T2:0)); c.rotate(a?-Math.PI/4:Math.PI/4); c.fillStyle=["#d4a06c","#c99460","#ddb07e"][Math.abs((x+y+a*7)/3|0)%3]; c.fillRect(0,0,L*.7,T2*.9); c.restore(); }); },
      wall:wallOf("#fbf1dc","#c99a6a","#9c6d40",null), av:{skin:3, hair:"spiky", hc:4, style:"overalls", top:3, pc:2, sc:0, hat:"beanie", acc:"glasses", expr:"grin"}, nm:"Max", hi:["Welcome! Look at our sofas and lamps.","어서 와요! 소파랑 램프 구경해요."]},
    pet:{en:"PET SHOP", ko:"펫 가게", col:0x6cc45a, sky:0xe6f4d8, ctr:0xffd23f, top:0xfff3dd, act:"펫 보기",
      floor:planks(["#e7c08e","#ddb37f","#ecc99a"],"rgba(150,95,45,.22)"), wall:wallOf("#fff6cc","#9fd884","#ffffff",(c,w,h)=>{ c.fillStyle="rgba(210,160,90,.35)"; for(let y=30;y<h;y+=64) for(let x=((y/64)%2)*32+16;x<w;x+=64){ c.beginPath(); c.ellipse(x,y+6,10,8,0,0,7); c.fill(); [[-11,-8],[-4,-13],[4,-13],[11,-8]].forEach(([a,b])=>{ c.beginPath(); c.arc(x+a,y+b,4,0,7); c.fill(); }); } }),
      av:{skin:2, hair:"pigtails", hc:1, style:"overalls", top:5, pc:4, sc:0, hat:"none", acc:"flower", expr:"grin"}, nm:"Penny", hi:["Hello! Do you want a pet friend?","안녕! 펫 친구 데려갈래요?"]},
    photo:{en:"PHOTO STUDIO", ko:"사진관", col:0x8f6ae8, sky:0xe9e2fb, ctr:0x3d3550, top:0xd8ccff, act:"사진 찍기",
      floor:planks(["#6e4a33","#7a5238","#664430"],"rgba(30,15,5,.35)"), wall:wallOf("#e4dbff","#7d68b8","#ffd23f",(c,w,h)=>{ c.fillStyle="rgba(255,255,255,.6)"; for(let i=0;i<26;i++){ const x=(i*73)%w, y=(i*41)%h; c.beginPath(); for(let k=0;k<10;k++){ const a=k*Math.PI/5-Math.PI/2, r=k%2?3:8; c.lineTo(x+Math.cos(a)*r,y+Math.sin(a)*r); } c.fill(); } }),
      av:{skin:1, hair:"spiky", hc:0, style:"hoodie", top:4, pc:1, sc:3, hat:"none", acc:"glasses", expr:"cool"}, nm:"Kai", hi:["Hi! Smile for the camera!","안녕! 카메라 보고 웃어요!"]}
  };
  /* 가게마다 장식 */
  const DECO={
    fish(g){ /* 얼음 진열대 + 생선 */ const ice=grp(g,3.5,1.45,0,.79); p(ice,rb(2.6,.08,.5,.03),0xeaf8ff,0,0,0); for(let i=0;i<9;i++) p(ice,bl(.05,6,5),0xffffff,-1.15+i*.29,.04,(i%2?.12:-.14),{nocast:1});
        [[0xff8a3d,-.95],[0x5cc8ff,-.5],[0xffd23f,-.05],[0xff6f91,.4],[0x9a8cff,.85],[0x7ad08a,1.15]].forEach(([c,x],i)=>fish(ice,x,.08,(i%2?.06:-.06),c,i%2?.25:-.2,1.3));
      /* 수족관 */ const tk=grp(g,.48,2.0,Math.PI/2); p(tk,rb(1.9,.52,.62),0x8a5a34,0,.26,0); p(tk,rb(1.84,.06,.56),0xf0dca8,0,.55,0); p(tk,bx(1.86,.7,.56),0,0,.92,0,{mat:M(0x4fb6e8,{transparent:true, opacity:.38, roughness:.1}),nocast:1}); p(tk,bx(1.9,.82,.6),0,0,.95,0,{mat:GL(),nocast:1}); [-1,1].forEach(k=>{ p(tk,bx(1.92,.05,.04),0x3b4b5a,0,1.37,k*.3); p(tk,bx(.04,.05,.62),0x3b4b5a,k*.95,1.37,0); [-1,1].forEach(q=>p(tk,bx(.04,.82,.04),0x3b4b5a,k*.95,.95,q*.3)); });
        [[-.6,.1],[.2,-.12],[.7,.14]].forEach(([x,z],i)=>{ p(tk,cn(.07,.4+i*.08,5),0x3fbf6a,x,.78+i*.04,z); p(tk,cn(.05,.3,5),0x6fd88a,x+.1,.72,z+.05); }); p(tk,bl(.1,7,6),0x9aa3ad,-.2,.62,.1); p(tk,bl(.07,7,6),0xb5a08a,.45,.6,-.12);
        const sw=grp(tk,0,0,0,0); sw.userData.anim=1; const F=[[0xff8a3d,.95,.1],[0xffd23f,1.15,-.1],[0x5cc8ff,.85,-.05],[0xff6f91,1.05,.12]].map(([c,y,z],i)=>({f:fish(sw,0,y,z,c,0,.9), y, z, ph:i*1.7, sp:.5+i*.12})); anims.push(dt=>{ F.forEach(o=>{ o.ph+=dt*o.sp; const x=Math.sin(o.ph)*.75; o.f.position.set(x,o.y+Math.sin(o.ph*2.3)*.04,o.z); o.f.rotation.y=Math.cos(o.ph)>0?0:Math.PI; }); });
        W(tk,"fish tank","수족관","🐠"); blk([0,1],[0,2]);
      /* 그물 (뒤 벽 왼쪽) */ const nt=grp(g,1.0,.05); for(let i=-4;i<=4;i++){ p(nt,bx(.025,1.25,.02),0xd9c48f,i*.17,1.75,0,{rz:.62,nocast:1}); p(nt,bx(.025,1.25,.02),0xd9c48f,i*.17,1.75,0,{rz:-.62,nocast:1}); } p(nt,bx(1.5,.05,.04),0x8a5a34,0,2.35,0); [[-.45,1.4],[.2,1.6],[.5,1.9]].forEach(([x,y])=>p(nt,bl(.07,8,6),0xff8a3d,x,y,.04)); W(nt,"net","그물","🕸");
      /* 구명 튜브 (뒤 벽 오른쪽) */ const lr=grp(g,5.6,.08); p(lr,to(.27,.075),0xff4d5e,0,1.75,0); [0,1,2,3].forEach(i=>p(lr,bx(.16,.13,.2),0xffffff,Math.cos(i*Math.PI/2+.78)*.27,1.75+Math.sin(i*Math.PI/2+.78)*.27,0,{rz:i*Math.PI/2+.78,nocast:1})); W(lr,"life ring","구명 튜브","🛟");
      /* 통 · 생선 상자 (오른쪽) */ [[6.35,.75],[6.3,1.55]].forEach(([x,z])=>{ const b=grp(g,x,z); p(b,cy(.28,.25,.62,14),0xa8703f,0,.31,0); [.1,.52].forEach(y=>p(b,to(.275,.025),0x5a4030,0,y,0,{rx:Math.PI/2,nocast:1})); p(b,cy(.25,.25,.02,14),0x7a5030,0,.62,0); W(b,"barrel","통","🛢"); });
        { const c=crate(g,6.3,0,2.6,(c,x,y,z,col,i)=>fish(c,x,y,z,[0xff8a3d,0x5cc8ff,0xffd23f][i%3],.3),0,6); W(c,"fish","물고기","🐟"); }
        blk([6,0],[6,1],[6,2]);
      /* 낚싯대 · 트로피 (왼 벽 앞쪽) */ const rd=grp(g,.12,4.3); [0,.18,.36].forEach((z,i)=>{ p(rd,cy(.016,.022,1.9,6),[0x8a5a34,0x3b4b5a,0xff7a3a][i],.12,.95,z,{rz:-.12}); p(rd,cy(.04,.04,.05,8),0x8a8f99,.15,.5,z,{rz:Math.PI/2}); }); W(rd,"fishing rod","낚싯대","🎣"); blk([0,4]);
        const tp_=grp(g,.04,3.4,Math.PI/2); p(tp_,rb(.9,.5,.05),0x8a5a34,0,1.95,0); fish(tp_,0,1.95,.08,0x5cc8ff,0,3.2); W(tp_,"big fish","큰 물고기","🏆");
        rug(g,3.9,4.5,2.3,2.3,roundRug("#4f9fe0","#bfe6fb",(c,w,h)=>{ c.fillStyle="#ffd23f"; c.beginPath(); c.ellipse(w*.52,h/2,w*.17,h*.1,0,0,7); c.fill(); c.beginPath(); c.moveTo(w*.36,h/2); c.lineTo(w*.26,h*.4); c.lineTo(w*.26,h*.6); c.fill(); c.fillStyle="#3b2433"; c.beginPath(); c.arc(w*.62,h*.48,6,0,7); c.fill(); }));
      /* 앞쪽 — 칠판 · 양동이 · 상자 더미 · 닻 */ const eb=grp(g,4.6,5.7,.7); [-1,1].forEach(k=>p(eb,bx(.05,1.0,.05),0x8a5a34,k*.3,.48,-.12,{rx:-.2})); p(eb,bx(.05,.95,.05),0x8a5a34,0,.46,.14,{rx:.3});
        pic(eb,.62,.5,(c,w,h)=>{ c.fillStyle="#8a5a34"; c.fillRect(0,0,w,h); c.fillStyle="#2f4a3a"; c.fillRect(10,10,w-20,h-20); c.fillStyle="#fff"; c.textAlign="center"; c.textBaseline="middle"; c.font='900 34px "Jua",sans-serif'; c.fillText("FRESH",w/2,h*.36); c.fillStyle="#ffd23f"; c.fillText("FISH!",w/2,h*.68); }, 0,.78,-.08,0,256).rotation.x=-.2; W(eb,"board","칠판","📋"); blk([4,5]);
        { const bk=grp(g,6.3,4.3); p(bk,cy(.24,.19,.36,14),0x6ec3ff,0,.18,0); p(bk,to(.24,.02),0x3b4b5a,0,.36,0,{rx:Math.PI/2,nocast:1}); p(bk,cy(.22,.22,.02,14),0x9fe0ff,0,.33,0,{nocast:1}); fish(bk,-.05,.38,0,0xff8a3d,.6); fish(bk,.06,.39,.06,0x9a8cff,2.4); W(bk,"bucket","양동이","🪣"); blk([6,4]); }
        { const cs=grp(g,6.25,5.55,.2); [[0,0,0],[0,.32,.08]].forEach(([x,y,r],i)=>p(cs,rb(.6,.3,.45,.03),i?0xc98f5a:0xb07a4a,x,y+.15,0,{ry:r})); W(cs,"box","상자","📦"); blk([6,5]); }
        { const an=grp(g,.12,5.2,Math.PI/2); p(an,cy(.035,.035,.9,8),0x5a6470,0,1.2,0); p(an,to(.28,.035,Math.PI),0x5a6470,0,.8,0,{rz:Math.PI}); p(an,to(.07,.025),0x5a6470,0,1.7,0); p(an,bx(.42,.05,.05),0x5a6470,0,1.5,0); W(an,"anchor","닻","⚓"); } },
    clothes(g){ /* 옷걸이 (왼쪽) — 셔츠 */ const r1=grp(g,.62,2.1,Math.PI/2); [-1,1].forEach(k=>p(r1,cy(.03,.03,1.55,6),0xb8bcc6,k*.95,.78,0)); p(r1,cy(.025,.025,2.0,6),0xb8bcc6,0,1.52,0,{rz:Math.PI/2}); [-1,1].forEach(k=>p(r1,rb(.12,.04,.5),0xb8bcc6,k*.95,.02,0));
        [0xff7a7a,0x6ec3ff,0x7be39a,0xffd23f,0xb28dff,0xff9ed2].forEach((c,i)=>shirt(r1,-.8+i*.32,1.5,0,c,0)); W(r1,"shirt","셔츠","👕"); blk([0,1],[0,2],[0,3]);
      /* 원피스 걸이 (오른쪽) */ const r2=grp(g,6.4,1.9,Math.PI/2); [-1,1].forEach(k=>p(r2,cy(.03,.03,1.55,6),0xd6b14a,k*.8,.78,0)); p(r2,cy(.025,.025,1.7,6),0xd6b14a,0,1.52,0,{rz:Math.PI/2});
        [0xff9ed2,0xffd23f,0x6ec3ff,0xb28dff].forEach((c,i)=>{ const d=grp(r2,-.6+i*.4,0); p(d,cn(.2,.62,10),c,0,1.08,0); p(d,rb(.2,.16,.1,.04),c,0,1.42,0); p(d,to(.04,.01,Math.PI),0x8a8f99,0,1.52,0,{nocast:1}); }); W(r2,"dress","원피스","👗"); blk([6,1],[6,2]);
      /* 거울 (뒤 벽 왼쪽) */ const mr=grp(g,1.15,.1); p(mr,rb(.78,1.78,.08,.04),0xe0b040,0,.95,0); p(mr,bx(.64,1.6,.02),0,0,.95,.045,{mat:M(0xe8f6ff,{roughness:.05, metalness:.35}),nocast:1}); [[-.12,1.2],[.08,.85]].forEach(([x,y])=>p(mr,bx(.05,.5,.01),0xffffff,x,y,.06,{rz:.6,nocast:1})); W(mr,"mirror","거울","🪞"); blk([1,0]);
      /* 마네킹 2 */ [[5.4,3.5,0xff7a7a,"cap"],[5.5,4.9,0x6ec3ff,"hat"]].forEach(([x,z,c,h],i)=>{ const m=grp(g,x,z,-.5); p(m,cy(.2,.24,.05,14),0x3b3b48,0,.025,0); p(m,cy(.025,.025,.6,6),0xb8bcc6,0,.33,0); p(m,cy(.19,.15,.5,12),c,0,.86,0); p(m,cy(.15,.19,.2,12),0x3d4f7a,0,.54,0); [-1,1].forEach(k=>p(m,cy(.05,.045,.42,8),c,k*.22,.86,0,{rz:k*.18})); p(m,bl(.13,10,8),0xf3e6d6,0,1.25,0);
        if(i) { p(m,cy(.2,.2,.02,14),0xf2d27a,0,1.35,0); p(m,cy(.11,.12,.1,12),0xf2d27a,0,1.4,0); } else { p(m,bl(.12,10,6),0xff4d5e,0,1.31,0,{s:[1,.6,1]}); p(m,rb(.12,.02,.12),0xff4d5e,0,1.3,.12); } W(m,i?"hat":"cap",i?"모자":"모자","👒"); blk([Math.floor(x),Math.floor(z)]); });
      /* 신발 받침 (왼 벽 앞) */ const sb=grp(g,.32,4.4,Math.PI/2); p(sb,rb(.9,.3,.45),0xffffff,0,.15,0); [[0xff4d5e,-.3],[0x3b3b48,0],[0xffd23f,.3]].forEach(([c,x])=>{ p(sb,rb(.12,.08,.22,.04),c,x-.06,.34,0); p(sb,rb(.12,.08,.22,.04),c,x+.07,.34,0); }); W(sb,"shoes","신발","👟"); blk([0,4]);
      { const ht=grp(g,3.7,5.55); p(ht,cy(.42,.42,.06,20),0xffffff,0,.62,0); p(ht,cy(.36,.3,.6,16),0xffb3c6,0,.3,0); p(ht,cy(.16,.17,.08,12),0xf2d27a,-.15,.7,0); p(ht,cy(.24,.24,.015,14),0xf2d27a,-.15,.66,0); p(ht,bl(.12,10,6),0x6ec3ff,.17,.66,.05,{s:[1,.65,1]}); p(ht,rb(.12,.02,.12),0x6ec3ff,.17,.66,.18); W(ht,"hat","모자","👒"); blk([3,5]); }
      rug(g,3.3,4.2,1.8,1.8,roundRug("#ff9ec0","#ffe6ee"));
      plant(g,.45,5.3,1.1); blk([0,5]);
      /* 카운터 위 옷 더미 · 쇼핑백 */ [[2.5,0xff9ed2],[2.5,0x6ec3ff],[2.5,0xffd23f]].forEach(([x,c],i)=>p(g,rb(.42,.07,.32,.02),c,x,.83+i*.075,1.4)); { const b=grp(g,4.55,1.4,0,.79); p(b,rb(.34,.38,.14,.02),0xff6b8a,0,.19,0); p(b,to(.08,.012,Math.PI),0x3b2433,0,.38,0,{nocast:1}); } },
    mart(g){ /* 선반 (왼 벽) */ const sh=grp(g,.42,2.05,Math.PI/2); p(sh,rb(2.4,1.7,.06),0xb07a4a,0,.85,-.25); [-1.2,1.2].forEach(x=>p(sh,rb(.06,1.7,.56),0x9a6a40,x,.85,0)); [.08,.62,1.16].forEach(y=>p(sh,rb(2.4,.05,.56),0xc98f5a,0,y,0));
        const F=[[apple,0xff4d4d,"apple","사과","🍎"],[apple,0xffa53d,"orange","오렌지","🍊"],[carrot,0,"carrot","당근","🥕"],[cabbage,0,"cabbage","양배추","🥬"],[apple,0xffe14d,"lemon","레몬","🍋"],[apple,0xb055d6,"grape","포도","🍇"]];
        F.forEach(([f,c,en,ko,ic],i)=>{ const cr=crate(sh,(i%3-1)*.75,[.1,.64][Math.floor(i/3)],.0,f,c,6); W(cr,en,ko,ic); });
        for(let i=0;i<8;i++){ const b=grp(sh,-1.0+i*.28,0,0,1.18); p(b,rb(.2,.34,.12,.02),[0xff5a5a,0x4f8fe0,0xffc93d,0x5cc46a,0xff9a3d,0xb070e0,0xff5a5a,0x4f8fe0][i],0,.17,.05); p(b,bx(.12,.1,.005),0xffffff,0,.2,.112,{nocast:1}); } W(sh,"shelf","선반","🗄"); blk([0,1],[0,2],[0,3]);
      /* 냉장고 (뒤 벽 오른쪽) */ const fr=grp(g,5.8,.36); p(fr,bx(1.5,1.95,.06),0xdfe6ee,0,.98,-.28); [-1,1].forEach(k=>p(fr,rb(.1,1.95,.62,.03),0xe9eef4,k*.7,.98,0)); p(fr,rb(1.5,.2,.62,.03),0xe9eef4,0,.1,0); p(fr,rb(1.5,.22,.62,.03),0x4fb85e,0,1.86,0); p(fr,bx(1.34,1.55,.02),0,0,1.0,.31,{mat:GL(),nocast:1}); p(fr,bx(1.3,.06,.02),0,0,1.74,.25,{mat:LT(0xd8f4ff),nocast:1});
        [.42,.86,1.3].forEach(y=>{ p(fr,bx(1.3,.03,.5),0xc6d0da,0,y,.02); for(let i=0;i<7;i++) p(fr,cy(.05,.05,.26,8),[0xffffff,0x6ec3ff,0xff7a7a,0x7be39a,0xffd23f,0xffffff,0xffa53d][(i+y*10|0)%7],-.54+i*.18,y+.14,.05); });
        p(fr,cy(.02,.02,1.2,6),0x9aa3ad,-.05,1.0,.36); p(fr,cy(.02,.02,1.2,6),0x9aa3ad,.05,1.0,.36); W(fr,"fridge","냉장고","🧊"); blk([5,0],[6,0]);
      /* 카트 */ const ct=grp(g,5.5,3.3,-.6); p(ct,bx(.62,.36,.44),0,0,.62,0,{mat:M(0xb8c6d4,{transparent:true,opacity:.55, roughness:.3}),nocast:1}); [[-.31,0],[.31,0]].forEach(([x])=>p(ct,bx(.02,.38,.46),0x8a97a6,x,.62,0)); p(ct,bx(.64,.02,.46),0x8a97a6,0,.8,0); p(ct,bx(.64,.02,.46),0x8a97a6,0,.44,0);
        [[-.25,-.17],[.25,-.17],[-.25,.17],[.25,.17]].forEach(([x,z])=>{ p(ct,cy(.012,.012,.36,5),0x8a97a6,x,.26,z); p(ct,cy(.05,.05,.04,10),0x3b3b48,x,.05,z,{rz:Math.PI/2}); }); p(ct,cy(.02,.02,.6,6),0xff4d5e,-.42,.98,0,{rx:Math.PI/2}); p(ct,bx(.12,.02,.02),0x8a97a6,-.36,.92,.2); p(ct,bx(.12,.02,.02),0x8a97a6,-.36,.92,-.2);
        apple(ct,-.1,.72,.05,0xff4d4d); apple(ct,.05,.74,-.08,0xffa53d); p(ct,rb(.2,.24,.12,.02),0xffe08a,.15,.78,.08); W(ct,"cart","카트","🛒"); blk([5,3]);
      /* 수박 매대 */ const wm=grp(g,5.6,5.0); p(wm,rb(1.0,.5,.7),0xc98f5a,0,.25,0); [[-.25,-.1],[.2,.12],[.0,-.05],[.28,-.18]].forEach(([x,z],i)=>p(wm,bl(.17,12,9),0x3fa34d,x,.6+(i===2?.18:0),z,{s:[1,.9,1.15]})); W(wm,"watermelon","수박","🍉"); blk([5,4],[5,5],[6,4],[6,5]);
      /* 계산대 · 빵 */ const rg=grp(g,4.35,1.42,-.3,.79); p(rg,rb(.42,.22,.32),0x3b3b48,0,.11,0); p(rg,rb(.3,.16,.03),0x9fe0ff,0,.32,-.08,{rx:-.4}); W(rg,"cash register","계산대","💵");
        { const br=grp(g,2.6,1.4,0,.79); [[0,0],[.18,.08]].forEach(([x,z])=>p(br,bl(.11,10,7),0xd9a35a,x,.07,z,{s:[1.6,.7,.9]})); }
        { const bs=grp(g,.45,5.25,.3); [0,1,2].forEach(i=>{ p(bs,rb(.48,.2,.34,.03),0xff4d5e,0,.1+i*.16,0); p(bs,to(.12,.015,Math.PI),0x3b2433,0,.22+i*.16,0,{nocast:1}); }); W(bs,"basket","장바구니","🧺"); blk([0,5]); }
        { const lo=grp(g,4.0,5.55); p(lo,rb(1.7,.5,.55),0xd9e8d4,0,.25,0); [0,1,2,3,4,5].forEach(i=>{ p(lo,rb(.2,.26,.09,.02),[0xffc93d,0xff7a7a,0x6ec3ff,0xffc93d,0x7be39a,0xff9ec0][i],-.65+i*.26,.63,.08); p(lo,rb(.2,.26,.09,.02),[0x7be39a,0xff9ec0,0xffc93d,0x6ec3ff,0xff7a7a,0xffc93d][i],-.65+i*.26,.63,-.1); }); W(lo,"snack","과자","🍪"); blk([3,5],[4,5]); }
        pic(g,1.3,.5,(c,w,h)=>{ c.fillStyle="#ff4d5e"; rr(c,0,0,w,h,20); c.fill(); c.fillStyle="#fff"; c.font='900 '+(h*.62)+'px "Jua",sans-serif'; c.textAlign="center"; c.textBaseline="middle"; c.fillText("SALE",w/2,h*.55); }, 1.0,1.95,.03,0,256); },
    hair(g){ /* 미용 의자 2 + 거울 (왼 벽) */ [1.45,3.35].forEach((z,i)=>{ const ch=grp(g,.95,z,Math.PI/2); p(ch,cy(.22,.26,.06,14),0xc0c6d0,0,.03,0); p(ch,cy(.06,.06,.32,8),0xc0c6d0,0,.2,0); p(ch,rb(.56,.14,.52,.06),0xff4d6d,0,.42,0); p(ch,rb(.56,.62,.12,.06),0xff4d6d,0,.78,-.24); [-1,1].forEach(k=>p(ch,rb(.08,.08,.44,.03),0xc0c6d0,k*.3,.58,0)); p(ch,rb(.4,.04,.16),0xc0c6d0,0,.14,.36); W(ch,"chair","의자","💺");
        const mr=grp(g,.03,z,Math.PI/2); p(mr,rb(.86,1.05,.05,.04),0xffffff,0,1.45,0); p(mr,bx(.72,.9,.02),0,0,1.45,.03,{mat:M(0xe8f6ff,{roughness:.05, metalness:.35}),nocast:1}); for(let k=0;k<5;k++){ p(mr,bl(.04,8,6),0,-.36+k*.18,1.98,.05,{mat:LT(),nocast:1}); } p(mr,bx(.05,.45,.01),0xffffff,-.15,1.55,.05,{rz:.6,nocast:1}); W(mr,"mirror","거울","🪞"); blk([0,Math.floor(z)]); });
      /* 이발소 기둥 (뒤 벽 오른쪽 · 돌아감) */ { const pl=grp(g,6.55,.25); const t=tex(64,128,(c,w,h)=>{ c.fillStyle="#fff"; c.fillRect(0,0,w,h); [["#ff4d5e",0],["#3f6fe0",42]].forEach(([col,o])=>{ c.fillStyle=col; for(let y=-h;y<h*2;y+=84){ c.beginPath(); c.moveTo(0,y+o); c.lineTo(w,y+o-32); c.lineTo(w,y+o-12); c.lineTo(0,y+o+20); c.fill(); } }); }, [1,2]); const mt=new THREE.MeshStandardMaterial({map:t, roughness:.5}); own.push(mt);
        p(pl,cy(.08,.1,.1,12),0xc0c6d0,0,1.0,0); p(pl,cy(.09,.09,.75,16),0,0,1.45,0,{mat:mt}); p(pl,bl(.1,12,8),0xc0c6d0,0,1.86,0); p(pl,cy(.03,.03,1.0,6),0xc0c6d0,0,.5,0); anims.push(dt=>{ t.offset.y-=dt*.35; }); W(pl,"barber pole","이발소 기둥","💈"); blk([6,0]); }
      /* 샴푸 선반 (뒤 벽 왼쪽) */ const sp=grp(g,1.25,.14); [1.25,1.7].forEach(y=>{ p(sp,rb(1.1,.05,.26),0xffffff,0,y,0); for(let i=0;i<5;i++){ const c=[0xff9ec0,0x7fd3ea,0xffd23f,0xb28dff,0x7be39a][(i+y*10|0)%5]; p(sp,cy(.06,.07,.22,10),c,-.4+i*.2,y+.14,0); p(sp,cy(.025,.03,.06,8),0xffffff,-.4+i*.2,y+.28,0); } }); W(sp,"shampoo","샴푸","🧴"); blk([1,0]);
      /* 드라이어 의자 (오른쪽) */ const dr=grp(g,6.15,3.0,-Math.PI/2); p(dr,rb(.56,.14,.52,.06),0x8fd3ff,0,.42,0); p(dr,rb(.56,.62,.12,.06),0x8fd3ff,0,.78,-.24); p(dr,cy(.2,.24,.36,8),0xc0c6d0,0,.18,0); p(dr,cy(.03,.03,1.1,6),0xc0c6d0,0,.95,-.3); p(dr,bl(.3,14,10,0),0xffd6ea,0,1.38,-.12,{s:[1,.8,1]}); p(dr,cy(.31,.31,.06,16),0xff8fc8,0,1.32,-.12); W(dr,"hair dryer","드라이기","💨"); blk([6,3],[5,3]);
      /* 가발 머리 (오른쪽 앞) */ const wg=grp(g,6.3,1.5,-Math.PI/2); p(wg,rb(1.1,.7,.4),0xffffff,0,.35,0); [[0x9b7be8,-.32],[0xe8c26b,0],[0xff9ec0,.32]].forEach(([c,x])=>{ p(wg,bl(.12,10,8),0xf3e6d6,x,.85,0); p(wg,bl(.135,10,8),c,x,.9,-.03,{s:[1,.9,1]}); }); W(wg,"hair","머리카락","💇"); blk([6,1],[6,2]);
      /* 카운터 위 가위 · 빗 */ { const sc=grp(g,2.55,1.42,.4,.8); [-1,1].forEach(k=>p(sc,bx(.03,.012,.3),0xc0c6d0,0,0,0,{ry:k*.3})); [-1,1].forEach(k=>p(sc,to(.045,.012),0xff4d6d,k*.06,0,.17,{rx:Math.PI/2})); p(g,rb(.36,.03,.08,.01),0x3b3b48,4.5,.8,1.45); }
      rug(g,3.8,4.5,2.2,2.2,roundRug("#ff8fc8","#ffe0f0",(c,w,h)=>{ c.strokeStyle="#fff"; c.lineWidth=9; [-1,1].forEach(k=>{ c.beginPath(); c.arc(w/2+k*22,h*.62,16,0,7); c.stroke(); c.beginPath(); c.moveTo(w/2+k*12,h*.54); c.lineTo(w/2-k*30,h*.28); c.stroke(); }); }));
      /* 기다리는 소파 · 잡지 탁자 · 화분 */ { const sf=grp(g,6.25,5.3,-Math.PI/2); p(sf,rb(1.3,.36,.6,.08),0x8fd3ff,0,.3,0); p(sf,rb(1.3,.5,.16,.08),0x8fd3ff,0,.62,-.24); [-1,1].forEach(k=>p(sf,rb(.14,.46,.6,.06),0x7fc0ea,k*.62,.4,0)); [-1,1].forEach(k=>p(sf,cy(.03,.03,.12,6),0xc0c6d0,k*.5,.06,0)); W(sf,"sofa","소파","🛋"); blk([6,4],[6,5],[6,6]); }
        { const mt=grp(g,5.2,5.6); p(mt,cy(.3,.3,.04,16),0xffffff,0,.42,0); p(mt,cy(.03,.03,.4,6),0xc0c6d0,0,.2,0); p(mt,rb(.26,.02,.2,.01),0xff8fc8,-.05,.45,0,{ry:.3}); p(mt,rb(.26,.02,.2,.01),0x6ec3ff,.05,.47,.03,{ry:-.2}); W(mt,"magazine","잡지","📖"); blk([5,5]); }
        plant(g,.45,5.25,1.1); blk([0,5]); },
    snack(g){ /* 아이스크림 냉동고 (왼 벽) */ const fz=grp(g,.5,2.05,Math.PI/2); p(fz,rb(2.1,.5,.72),0xffffff,0,.25,0); [-1,1].forEach(k=>{ p(fz,rb(2.1,.36,.06,.02),0xffffff,0,.66,k*.33); p(fz,rb(.06,.36,.72,.02),0xffffff,k*1.02,.66,0); }); p(fz,rb(2.12,.1,.74),0xff9ec0,0,.12,0); p(fz,bx(2.0,.03,.62),0,0,.84,0,{mat:GL(),nocast:1});
        [0xffb6d1,0x8a5a3c,0xfff3c4,0x9fe8c8,0xffd23f,0xd6b0ff].forEach((c,i)=>{ p(fz,cy(.15,.13,.2,12),0xffffff,-.82+i*.33,.6,0); p(fz,bl(.14,10,6),c,-.82+i*.33,.7,0,{s:[1,.6,1]}); }); W(fz,"ice cream","아이스크림","🍦"); blk([0,1],[0,2],[0,3]);
      /* 메뉴판 (뒤 벽 왼쪽) */ const mn=pic(g,1.55,1.05,(c,w,h)=>{ c.fillStyle="#3b2433"; rr(c,0,0,w,h,24); c.fill(); c.fillStyle="#2f4a3a"; rr(c,10,10,w-20,h-20,18); c.fill(); c.fillStyle="#fff"; c.textAlign="left"; c.textBaseline="middle"; c.font='900 40px "Jua",sans-serif'; c.fillText("MENU",w/2-56,46);
          [["#ffd6a0","cookie"],["#ff9ec0","donut"],["#fff","ice cream"],["#ffe14d","lemonade"]].forEach(([col,t],i)=>{ const y=100+i*44; c.fillStyle=col; c.beginPath(); c.arc(40,y,13,0,7); c.fill(); c.fillStyle="#fff"; c.font='700 30px "Jua",sans-serif'; c.fillText(t,64,y); }); }, 1.2,1.75,.03,0,384); W(mn,"menu","메뉴판","📋");
      /* 탁자 2 + 의자 */ [[5.5,3.5],[5.5,5.4]].forEach(([x,z],i)=>{ const tb=grp(g,x,z); p(tb,cy(.42,.42,.05,20),0xffffff,0,.66,0); p(tb,cy(.04,.04,.62,8),0xc0c6d0,0,.33,0); p(tb,cy(.22,.24,.04,14),0xc0c6d0,0,.02,0);
          if(i){ p(tb,to(.07,.035),0xff9ec0,.1,.72,0,{rx:Math.PI/2}); p(tb,to(.07,.035),0xd9a35a,-.12,.72,.1,{rx:Math.PI/2}); W(tb,"donut","도넛","🍩"); } else { p(tb,cn(.06,.18,8),0xe0b070,.05,.78,0,{rx:Math.PI}); p(tb,bl(.07,9,7),0xffb6d1,.05,.9,0); p(tb,cy(.07,.06,.18,10),0xffe14d,-.15,.78,.1); W(tb,"table","탁자","🍽"); }
          stool(g,x-.72,z,[0xff9ec0,0x7fd3ea][i]); stool(g,x+.72,z,[0xffd23f,0xb28dff][i]); blk([Math.floor(x),Math.floor(z)],[Math.floor(x-.72),Math.floor(z)],[Math.floor(x+.72),Math.floor(z)]); });
      /* 큰 아이스크림 (뒤 오른쪽 구석) */ const ic=grp(g,6.4,.6); p(ic,cy(.3,.34,.12,14),0xffffff,0,.06,0); p(ic,cn(.26,.9,10),0xe0b070,0,.62,0,{rx:Math.PI}); [[0xffb6d1,1.15],[0x9fe8c8,1.4],[0x8a5a3c,1.64]].forEach(([c,y])=>p(ic,bl(.26,12,9),c,0,y,0)); p(ic,bl(.07,8,6),0xff4d5e,0,1.92,0); W(ic,"ice cream cone","아이스크림 콘","🍦"); blk([6,0]);
      /* 깃발 줄 (뒤 벽 위) */ for(let i=0;i<9;i++) p(g,cn(.12,.22,3),[0xff9ec0,0xffd23f,0x7fd3ea,0x9fe8c8][i%4],2.2+i*.48,2.35,.06,{rx:Math.PI,nocast:1});
      { const gb=grp(g,.45,5.25); p(gb,rb(.36,.5,.36,.05),0xff4d5e,0,.25,0); p(gb,cy(.05,.05,.1,8),0xc0c6d0,0,.5,0); p(gb,bl(.26,14,10),0,0,.8,0,{mat:GL(),nocast:1}); for(let i=0;i<14;i++){ const a=i*2.4, r=.08+(i%3)*.05; p(gb,bl(.05,8,6),[0xff4d5e,0xffd23f,0x6ec3ff,0x7be39a,0xb28dff][i%5],Math.cos(a)*r,.66+Math.floor(i/5)*.08,Math.sin(a)*r); } p(gb,cy(.27,.27,.06,16),0xff4d5e,0,1.05,0); p(gb,cy(.04,.04,.03,8),0xffd23f,0,.3,.19,{rx:Math.PI/2}); W(gb,"gumball","껌볼","🍬"); blk([0,5]); }
      rug(g,3.4,4.6,1.9,1.9,roundRug("#ffe58a","#fffaf0"));
      /* 카운터 위 도넛 받침 · 컵케이크 */ { const st=grp(g,2.6,1.42,0,.79); p(st,cy(.24,.24,.03,16),0xffffff,0,.12,0); p(st,cy(.03,.05,.12,8),0xffffff,0,.06,0); [0xff9ec0,0xd9a35a,0xffd23f].forEach((c,i)=>p(st,to(.06,.03),c,Math.cos(i*2.1)*.12,.16,Math.sin(i*2.1)*.12,{rx:Math.PI/2})); }
        [4.4,4.65].forEach((x,i)=>{ p(g,cy(.07,.055,.08,10),0xffffff,x,.83,1.42); p(g,bl(.075,10,7),[0xffb6d1,0x9fe8c8][i],x,.9,1.42,{s:[1,.8,1]}); }); },
    furn(g){ const put=(id,x,z,ry,c,en,ko,ic)=>{ const I=ITEMS[id]; if(!I) return null; const w=grp(g,x,z,ry); try{ w.add(I.build(c||0)); }catch(e){ return null; } if(en) W(w,en,ko,ic); return w; };
      put("sofa",.55,2.1,Math.PI/2,0,"sofa","소파","🛋"); blk([0,1],[0,2]);
      put("floorlamp",.5,3.35,0,0,"lamp","램프","💡"); blk([0,3]);
      put("coffeetable",1.6,2.1,Math.PI/2,0,"table","탁자","☕"); blk([1,2]);
      put("shelf",1.15,.45,0,0,"bookshelf","책장","📚"); put("shelf",.42,1.0,Math.PI/2,0); blk([0,0],[1,0]);
      put("armchair",6.2,2.8,-Math.PI/2,0,"armchair","안락의자","🪑") || put("chair",6.2,2.8,-Math.PI/2,1,"chair","의자","🪑"); blk([6,2],[6,3]);
      put("plant",6.45,.55,0,0,"plant","화분","🪴"); put("monstera",.5,4.45,0,0,"plant","화분","🌿") || plant(g,.5,4.45,1.2); blk([6,0],[0,4]);
      put("table",5.5,4.9,0,0,"table","식탁","🍽"); put("chair",4.75,4.9,Math.PI/2,0) ; put("chair",6.25,4.9,-Math.PI/2,1); blk([5,4],[5,5],[4,4],[4,5],[6,4],[6,5]);
      put("lamp",5.55,1.6,0,1,"lamp","램프","💡"); blk([5,1]);
      /* 러그 · 가격표 · 그림 */ pic(g,1.7,1.7,(c,w,h)=>{ c.fillStyle="#e86a6a"; rr(c,0,0,w,h,40); c.fill(); c.strokeStyle="#fff3dd"; c.lineWidth=12; rr(c,22,22,w-44,h-44,30); c.stroke(); c.fillStyle="#ffd23f"; c.beginPath(); c.arc(w/2,h/2,40,0,7); c.fill(); }, 1.2,.013,2.1,0).rotation.x=-Math.PI/2;
        [[1.4,2.55],[.9,3.6],[6.0,2.2]].forEach(([x,z])=>{ const t=grp(g,x,z); p(t,cy(.012,.012,.5,5),0x8a8f99,0,.25,0); p(t,rb(.22,.14,.02,.01),0xffffff,0,.55,0); p(t,bl(.03,6,5),0x6ec3ff,0,.55,.015); });
        pic(g,1.0,.75,(c,w,h)=>{ c.fillStyle="#c98f5a"; c.fillRect(0,0,w,h); c.fillStyle="#bfe4ff"; c.fillRect(14,14,w-28,h-28); c.fillStyle="#7bcf6a"; c.beginPath(); c.moveTo(14,h-14); c.lineTo(w*.4,h*.4); c.lineTo(w*.7,h-14); c.fill(); c.fillStyle="#ffd23f"; c.beginPath(); c.arc(w*.75,h*.3,16,0,7); c.fill(); }, .03,1.75,2.1,Math.PI/2); },
    pet(g){ /* 우리 2층 (왼 벽) */ const cg=grp(g,.48,2.0,Math.PI/2); [0,1].forEach(r=>{ const y=r*.72; p(cg,rb(2.1,.06,.7),0xffd23f,0,y+.03,0); p(cg,rb(2.1,.06,.7),0xffd23f,0,y+.69,0); for(let i=0;i<=12;i++) p(cg,cy(.012,.012,.64,4),0xc0c6d0,-1.02+i*.17,y+.36,.33,{nocast:1});
          [-1.02,0,1.02].forEach(x=>p(cg,rb(.05,.66,.7),0xf2b632,x,y+.36,0)); });
        puppy(cg,-.55,.06,0,0xe8b878,.0); puppy(cg,.5,.06,-.05,0xffffff,.3); puppy(cg,-.5,.78,0,0xffa94d,.2,true); { const bn=grp(cg,.5,0,0,.78); p(bn,bl(.15,10,8),0xf4f0ea,0,.14,0,{s:[1.2,.9,1]}); p(bn,bl(.11,10,8),0xf4f0ea,0,.24,.13); [-1,1].forEach(k=>p(bn,cy(.03,.035,.22,6),0xf4f0ea,k*.05,.42,.11,{rz:k*.15})); [-1,1].forEach(k=>p(bn,bl(.015,6,5),0x1a1a24,k*.045,.27,.23)); }
        W(cg,"puppy","강아지","🐶"); blk([0,1],[0,2]);
      /* 캣타워 (오른쪽) */ const ct=grp(g,6.35,1.4); p(ct,rb(.7,.08,.7),0xd9a35a,0,.04,0); p(ct,cy(.08,.08,1.4,10),0xe8d2a8,0,.75,0); [[.55,.6],[1.05,.5],[1.45,.62]].forEach(([y,s])=>p(ct,rb(s,.07,s),0xd9a35a,0,y,0)); puppy(ct,0,1.49,0,0x8a8f99,-1.2,true); W(ct,"cat","고양이","🐱"); blk([6,1]);
      /* 어항 (뒤 오른쪽) */ const fb=grp(g,6.3,.42); p(fb,rb(.5,.62,.5),0xffffff,0,.31,0); p(fb,bl(.25,14,10),0,0,.86,0,{mat:GL(),nocast:1}); p(fb,cy(.2,.2,.04,14),0xf0dca8,0,.66,0); fish(fb,0,.86,0,0xffa53d,.4,1.1); W(fb,"goldfish","금붕어","🐠"); blk([6,0]);
      /* 펫 침대 · 그릇 · 장난감 */ const bd=grp(g,5.5,3.6); p(bd,to(.42,.13),0x7fd3ea,0,.13,0,{rx:Math.PI/2}); p(bd,cy(.4,.4,.06,18),0xfff3dd,0,.06,0); const sl=puppy(bd,0,.04,0,0xb07a4a,2.4); sl.userData.anim=1; anims.push((dt,t)=>{ sl.scale.y=1+Math.sin(t*2.2)*.035; }); W(bd,"pet bed","펫 침대","🛏"); blk([5,3]);
        [[4.65,4.6,0xff7a7a,0x8a5a3c],[5.05,4.75,0x6ec3ff,0x7fd3ea]].forEach(([x,z,c,f],i)=>{ const b=grp(g,x,z); p(b,cy(.15,.12,.1,14),c,0,.05,0); p(b,cy(.12,.12,.02,14),f,0,.095,0); if(!i) [[0,0],[.05,.04],[-.05,.03]].forEach(([a,q])=>p(b,bl(.03,6,5),0x8a5a3c,a,.11,q)); W(b,"bowl","그릇","🥣"); });
        W(ball(g,3.4,0,4.9,0xff4d5e,0xffffff,.12),"ball","공","⚽"); { const bn=grp(g,2.3,5.4,.6); p(bn,cy(.03,.03,.22,6),0xfff3dd,0,.05,0,{rz:Math.PI/2}); [-1,1].forEach(k=>{ p(bn,bl(.045,7,6),0xfff3dd,k*.12,.05,.03); p(bn,bl(.045,7,6),0xfff3dd,k*.12,.05,-.03); }); W(bn,"bone","뼈다귀","🦴"); }
      { const kh=grp(g,5.9,5.45,.45); p(kh,rb(.8,.6,.8,.04),0xff8a65,0,.3,0); [-1,1].forEach(k=>p(kh,rb(.56,.07,.92,.03),0xc0503a,k*.2,.78,0,{rz:-k*.7})); p(kh,bx(.34,.42,.02),0x3b2433,0,.24,.405,{nocast:1}); pic(kh,.4,.14,(c,w,h)=>{ c.fillStyle="#fff3dd"; c.fillRect(0,0,w,h); c.fillStyle="#c0503a"; c.font='900 '+(h*.7)+'px "Jua",sans-serif'; c.textAlign="center"; c.textBaseline="middle"; c.fillText("DOG",w/2,h*.55); },0,.56,.41,0,256); W(kh,"dog house","개집","🏠"); blk([5,5],[6,5],[6,6]); }
      rug(g,3.6,4.5,2.0,2.0,roundRug("#9fd884","#e6f6d0",(c,w,h)=>{ c.fillStyle="rgba(255,255,255,.85)"; c.beginPath(); c.ellipse(w/2,h*.56,30,24,0,0,7); c.fill(); [[-34,-24],[-12,-42],[12,-42],[34,-24]].forEach(([a,b])=>{ c.beginPath(); c.arc(w/2+a,h*.56+b,11,0,7); c.fill(); }); }));
      plant(g,.45,5.25,1.1); blk([0,5]);
      /* 펫 밥 자루 (카운터 옆) */ [[5.3,.5,0xff9a5c],[5.62,.62,0x6cc45a]].forEach(([x,z,c])=>{ const s=grp(g,x,z); p(s,rb(.32,.48,.2,.06),c,0,.24,0); p(s,bl(.05,6,5),0xffffff,0,.3,.1); W(s,"pet food","펫 밥","🦴"); }); blk([5,0]);
        pic(g,.9,.6,(c,w,h)=>{ c.fillStyle="#fff"; rr(c,0,0,w,h,20); c.fill(); c.fillStyle="#6cc45a"; c.font='900 54px "Jua",sans-serif'; c.textAlign="center"; c.textBaseline="middle"; c.fillText("I ♥ PETS",w/2,h/2); }, 1.25,1.9,.03,0,256); },
    photo(g){ /* 배경지 (왼 벽) */ const bt=tex(256,256,(c,w,h)=>{ const gr=c.createLinearGradient(0,0,0,h); gr.addColorStop(0,"#9fd8ff"); gr.addColorStop(1,"#ffd6ea"); c.fillStyle=gr; c.fillRect(0,0,w,h); c.fillStyle="rgba(255,255,255,.75)"; [[60,60],[180,90],[110,170],[210,200]].forEach(([x,y])=>{ c.beginPath(); for(let k=0;k<10;k++){ const a=k*Math.PI/5-Math.PI/2, r=k%2?6:15; c.lineTo(x+Math.cos(a)*r,y+Math.sin(a)*r); } c.fill(); }); }); const bm=new THREE.MeshStandardMaterial({map:bt, roughness:.9, side:THREE.DoubleSide}); own.push(bm);
        const bd=grp(g,.06,2.05,Math.PI/2); p(bd,bx(2.3,2.1,.01),0,0,1.07,.0,{mat:bm,nocast:1}); const fl=p(bd,OWN(new THREE.PlaneGeometry(2.3,1.3)),0,0,.012,.65,{mat:bm,nocast:1,rx:-Math.PI/2}); fl.receiveShadow=true; p(bd,cy(.06,.06,2.5,10),0x3b3b48,0,2.18,0,{rz:Math.PI/2}); [-1.25,1.25].forEach(x=>p(bd,cy(.025,.025,2.2,6),0x3b3b48,x,1.1,0));
        stool(g,.85,2.05,0xff9ec0); W(bd,"background","배경","🌈"); blk([0,2]);
      /* 삼각대 카메라 */ const cm=grp(g,2.55,2.8,-Math.PI/2-.25); [0,1,2].forEach(i=>{ const a=i*2.094; p(cm,cy(.015,.015,1.15,5),0x3b3b48,Math.cos(a)*.2,.55,Math.sin(a)*.2,{rx:Math.sin(a)*.18,rz:-Math.cos(a)*.18}); }); p(cm,rb(.36,.24,.2,.04),0x2c2c3a,0,1.2,0); p(cm,cy(.08,.09,.18,14),0x2c2c3a,0,1.2,.17,{rx:Math.PI/2}); p(cm,cy(.06,.06,.01,14),0,0,1.2,.265,{rx:Math.PI/2,mat:M(0x6ec3ff,{roughness:.1, metalness:.4}),nocast:1}); p(cm,rb(.1,.06,.06,.02),0,0,1.36,0,{mat:LT(0xffffff)}); p(cm,bx(.06,.04,.04),0xff4d5e,.12,1.34,0);
        W(cm,"camera","카메라","📷"); blk([2,2]);
      /* 조명 2 */ [[1.6,.45,.6],[.6,4.2,2.2]].forEach(([x,z,ry])=>{ const L=grp(g,x,z,ry); p(L,cy(.02,.02,1.6,6),0x3b3b48,0,.8,0); [0,1,2].forEach(i=>p(L,cy(.012,.012,.4,4),0x3b3b48,Math.cos(i*2.1)*.12,.16,Math.sin(i*2.1)*.12,{rz:Math.cos(i*2.1)*.6,rx:-Math.sin(i*2.1)*.6})); p(L,rb(.5,.4,.24,.03),0x2c2c3a,0,1.7,0); p(L,bx(.44,.34,.02),0,0,1.7,.12,{mat:LT(0xffffff),nocast:1}); W(L,"light","조명","💡"); blk([Math.floor(x),Math.floor(z)]); });
      /* 우산 조명 (오른쪽) */ const um=grp(g,6.3,2.6,-2.2); p(um,cy(.02,.02,1.7,6),0x3b3b48,0,.85,0); p(um,cn(.5,.3,10),0xffffff,0,1.75,.1,{rx:-1.9}); p(um,cy(.02,.02,.5,4),0x3b3b48,0,1.72,0,{rx:-1.9}); W(um,"umbrella","우산","☂️"); blk([6,2]);
      /* 액자 사진 */ const PH=[["#bfe4ff",(c,w,h)=>{ c.fillStyle="#7bcf6a"; c.beginPath(); c.moveTo(0,h); c.lineTo(w*.45,h*.35); c.lineTo(w,h); c.fill(); c.fillStyle="#ffd23f"; c.beginPath(); c.arc(w*.78,h*.25,h*.12,0,7); c.fill(); }],["#ffe6ee",(c,w,h)=>{ c.fillStyle="#ff6f91"; c.beginPath(); c.arc(w*.4,h*.42,h*.16,0,7); c.arc(w*.6,h*.42,h*.16,0,7); c.fill(); c.beginPath(); c.moveTo(w*.26,h*.5); c.lineTo(w*.5,h*.82); c.lineTo(w*.74,h*.5); c.fill(); }],
          ["#fff3c4",(c,w,h)=>{ c.fillStyle="#ffd27a"; c.beginPath(); c.arc(w/2,h*.48,h*.28,0,7); c.fill(); c.fillStyle="#3b2433"; [-1,1].forEach(k=>{ c.beginPath(); c.arc(w/2+k*h*.1,h*.42,h*.04,0,7); c.fill(); }); c.lineWidth=5; c.strokeStyle="#3b2433"; c.beginPath(); c.arc(w/2,h*.52,h*.12,.2,Math.PI-.2); c.stroke(); }],["#d8f6ec",(c,w,h)=>{ c.fillStyle="#8a8f99"; c.beginPath(); c.arc(w/2,h*.58,h*.24,0,7); c.fill(); [-1,1].forEach(k=>{ c.beginPath(); c.moveTo(w/2+k*h*.22,h*.45); c.lineTo(w/2+k*h*.12,h*.2); c.lineTo(w/2+k*h*.02,h*.4); c.fill(); }); }]];
        const frame=(i,x,y,z,ry,s)=>pic(g,.62*s,.5*s,(c,w,h)=>{ c.fillStyle="#3b2433"; c.fillRect(0,0,w,h); c.fillStyle="#f2d27a"; c.fillRect(6,6,w-12,h-12); c.fillStyle=PH[i][0]; c.fillRect(20,20,w-40,h-40); c.save(); c.translate(20,20); PH[i][1](c,w-40,h-40); c.restore(); }, x,y,z,ry,256);
        W(frame(0,5.0,1.75,.03,0,1),"photo","사진","🖼"); frame(1,5.85,1.95,.03,0,.9); frame(2,6.55,1.55,.03,0,.8); frame(3,.03,1.75,3.75,Math.PI/2,.9);
      { const pb=grp(g,6.25,4.3,-Math.PI/2); p(pb,rb(.8,.42,.5,.04),0xd9a35a,0,.21,0); p(pb,rb(.84,.06,.54,.02),0xb07a4a,0,.44,0); p(pb,cy(.12,.14,.14,12),0xff4d5e,-.2,.54,0); p(pb,cy(.18,.18,.02,14),0xff4d5e,-.2,.48,0); p(pb,cn(.1,.26,10),0xffd23f,.18,.6,.02); p(pb,bl(.03,6,5),0xff9ec0,.18,.74,.02); W(pb,"hat","모자","🎩"); blk([6,4]); }
        { const ez=grp(g,4.7,5.6,.7); [-1,1].forEach(k=>p(ez,bx(.05,1.5,.05),0x8a5a34,k*.35,.72,-.1,{rx:-.15})); p(ez,bx(.05,1.4,.05),0x8a5a34,0,.66,.2,{rx:.35}); p(ez,bx(.8,.05,.12),0x8a5a34,0,.62,-.05);
          pic(ez,.82,.66,(c,w,h)=>{ c.fillStyle="#f2d27a"; c.fillRect(0,0,w,h); c.fillStyle="#9fd8ff"; c.fillRect(14,14,w-28,h-28); c.fillStyle="#ffd27a"; c.beginPath(); c.arc(w*.38,h*.55,h*.2,0,7); c.fill(); c.beginPath(); c.arc(w*.64,h*.58,h*.17,0,7); c.fill(); c.fillStyle="#3b2433"; [[.33,.5],[.43,.5],[.6,.54],[.68,.54]].forEach(([a,b])=>{ c.beginPath(); c.arc(w*a,h*b,4,0,7); c.fill(); }); }, 0,1.0,-.03,0,256).rotation.x=-.15; W(ez,"picture","그림","🖼"); blk([4,5]); }
      rug(g,3.6,4.4,2.0,2.0,roundRug("#b9a2e0","#e6dcff"));
      plant(g,.45,5.25,1.1); blk([0,5]);
      /* 카운터 위 앨범 */ p(g,rb(.5,.06,.36,.02),0x8f6ae8,2.6,.82,1.42); p(g,rb(.46,.02,.32,.01),0xffffff,2.6,.86,1.42); }
  };

  /* ── 방 껍데기 (한 번만) ── */
  const floorM=new THREE.MeshStandardMaterial({roughness:.85}), wallM=new THREE.MeshStandardMaterial({roughness:.95});
  let shell=null, door=null;
  function mkShell(){ if(shell) return; shell=new THREE.Group(); G.add(shell);
    const sl=new THREE.Mesh(new THREE.BoxGeometry(N,.25,N), [M(0xd9b48a), M(0xd9b48a), floorM, M(0xd9b48a), M(0xc49a6c), M(0xc49a6c)]); sl.position.set(N/2,-.125,N/2); sl.receiveShadow=true; shell.add(sl);
    [[N/2,0,-T/2,0],[-T/2,0,N/2,Math.PI/2]].forEach(([x,y,z,r])=>{ const g=new THREE.Group(); g.position.set(x,y,z); g.rotation.y=r; const w=new THREE.Mesh(new THREE.BoxGeometry(N+T,H,T), wallM); w.position.y=H/2; w.receiveShadow=true; w.castShadow=true; g.add(w);
      part(g, new THREE.BoxGeometry(N+T,.18,T+.06), trimMat, 0,.09,0); part(g, new THREE.BoxGeometry(N+T+.04,.12,T+.1), trimMat, 0,H,0); shell.add(g); if(r) shell.userData.left=g; });
    door=makeDoor(.84,1.95,0x9a6a40,true); shell.userData.left.add(door); door.position.set(N/2-(N-1+.5),0,T/2+.01);
    const mat=new THREE.Mesh(rbox(.66,.02,.82,.01), M(0xd9a35a)); mat.position.set(.42,.012,N-.5); mat.receiveShadow=true; shell.add(mat);
    shell.traverse(o=>{ o.userData.noFade=1; }); }

  /* ── 합치기 — 같은 재료(그림 없는 것)를 한 덩어리로 (움직이는 것 · 자식 있는 것은 그대로) ── */
  function bake(root){ root.updateMatrixWorld(true); const inv=new THREE.Matrix4().copy(root.matrixWorld).invert(), bk=new Map(), kill=[];
    root.traverse(o=>{ if(!o.isMesh || o.children.length) return; for(let q=o.parent;q&&q!==root;q=q.parent) if(q.userData.anim) return; const m=o.material, gm=o.geometry;
      if(Array.isArray(m) || !m.isMeshStandardMaterial || m.map || !gm.attributes.normal) return; const k=m.uuid+(o.castShadow?"c":"");
      if(!bk.has(k)) bk.set(k,{m, cast:o.castShadow, L:[]}); bk.get(k).L.push({g:gm, M:new THREE.Matrix4().multiplyMatrices(inv,o.matrixWorld)}); kill.push(o); });
    bk.forEach(b=>{ let nv=0, ni=0; b.L.forEach(e=>{ nv+=e.g.attributes.position.count; ni+=e.g.index?e.g.index.count:e.g.attributes.position.count; });
      const P=new Float32Array(nv*3), Nn=new Float32Array(nv*3), I=new Uint32Array(ni), v=new THREE.Vector3(), nm=new THREE.Matrix3(); let ov=0, oi=0;
      b.L.forEach(e=>{ const pa=e.g.attributes.position, na=e.g.attributes.normal, ix=e.g.index; nm.getNormalMatrix(e.M);
        for(let i=0;i<pa.count;i++){ v.fromBufferAttribute(pa,i).applyMatrix4(e.M); P[(ov+i)*3]=v.x; P[(ov+i)*3+1]=v.y; P[(ov+i)*3+2]=v.z; v.fromBufferAttribute(na,i).applyMatrix3(nm).normalize(); Nn[(ov+i)*3]=v.x; Nn[(ov+i)*3+1]=v.y; Nn[(ov+i)*3+2]=v.z; }
        const n=ix?ix.count:pa.count; for(let i=0;i<n;i++) I[oi+i]=(ix?ix.getX(i):i)+ov; ov+=pa.count; oi+=n; });
      const geo=OWN(new THREE.BufferGeometry()); geo.setAttribute("position", new THREE.BufferAttribute(P,3)); geo.setAttribute("normal", new THREE.BufferAttribute(Nn,3)); geo.setIndex(new THREE.BufferAttribute(I,1)); geo.computeBoundingSphere();
      const mm=new THREE.Mesh(geo,b.m); mm.castShadow=b.cast; mm.receiveShadow=true; mm.userData.baked=1; root.add(mm); });
    kill.forEach(o=>{ o.parent.remove(o); if(o.geometry.userData.own) o.geometry.dispose(); }); return bk.size; }

  function build(k){ mkShell(); clear(); const D=TH[k]; occ.fill(0); words=[]; anims=[];
    if(floorM.map) floorM.map.dispose(); floorM.map=canvasTex(256,256,D.floor,[N/2,N/2]); floorM.needsUpdate=true;
    if(wallM.map) wallM.map.dispose(); wallM.map=canvasTex(256,256,D.wall,[N/2,1]); wallM.needsUpdate=true;
    deco=new THREE.Group(); deco.name="shopDeco:"+k; G.add(deco); counter(deco,k,D); const sg=sign(deco,D);
    try{ DECO[k](deco); }catch(e){ console.warn("shopDeco", k, e); }
    deco.updateMatrixWorld(true); words.forEach(w=>{ w.box=new THREE.Box3().setFromObject(w.o); });
    deco.userData.n=bake(deco); deco.traverse(o=>{ o.userData.noFade=1; }); sg.userData.sign=1;
    keeper=mkKeeper(D); try{ TOON.scan(G); }catch(e){} dirty=true; }
  function clear(){ if(deco){ G.remove(deco); deco.traverse(o=>{ if(o.geometry && o.geometry.userData.own) o.geometry.dispose(); }); deco=null; }
    if(keeper){ G.remove(keeper.g); keeper=null; } if(bub){ G.remove(bub.s); bub.s.material.map.dispose(); bub.s.material.dispose(); bub=null; }
    own.splice(0).forEach(r=>{ try{ r.dispose(); }catch(e){} }); words=[]; anims=[]; }

  /* ── 들어가기 · 나가기 ── */
  function has(k){ return !!TH[k]; }
  function is(){ return place===PL.shop; }
  function enter(S, open){ if(!S || !TH[S.k] || F.st!=="idle" || trip.busy) return false; const D=TH[S.k];
    cur={S, open:open||(()=>{}), yaw0:yaw, auto:true, greet:false, at:performance.now()}; PL.shop.name=S.ic+" "+S.t; PL.shop.sky=D.sky;
    go("shop", PL.shop.start, ()=>{ build(S.k); G.visible=true; yaw=yawTo=Math.PI/4; ui(true); }, {from:[-.3,N-.5], door});
    if(!run){ run=true; lastT=performance.now(); requestAnimationFrame(frame); } return true; }
  function greet(){ if(!cur || !keeper) return; const D=TH[cur.S.k]; cur.greet=true; keeper.act="wave"; keeper.t=0; setTimeout(()=>{ if(keeper) keeper.act="idle"; }, 1600);
    bubble(D.hi[0]); try{ say(D.hi[0]); }catch(e){} toast("🧑 <b>"+D.nm+"</b> · "+D.hi[0]+"<br><small>"+D.hi[1]+"</small>", 2600); }
  function openSheet(){ if(!cur || !is()) return; cur.auto=false; hero.face=Math.PI; dirty=true; try{ cur.open(); }catch(e){ console.warn(e); } }
  function goCounter(){ if(!cur || !is() || trip.busy) return; cur.auto=false; if(keeper){ keeper.act="wave"; keeper.t=0; setTimeout(()=>{ if(keeper) keeper.act="idle"; }, 900); }
    if(hero.cx===SPOTC[0] && hero.cz===SPOTC[1] && !hero.moving) openSheet(); else walkTo(SPOTC[0], SPOTC[1], openSheet); }
  function exit(){ if(!cur || !is() || trip.busy) return; cur.auto=false; try{ closeAv(); }catch(e){} try{ SHEETS.forEach(id=>{ const el=$(id); if(el) el.classList.remove("on"); }); }catch(e){}
    leaveBy(DOOR, [-.3,N-.5], out, door); }
  function doorAt(S){ const B=ISLE.blocked; let at=[Math.floor(S.door[0]), Math.floor(S.door[1])];
    if(B(at[0],at[1])){ let best=null, bd=1e9; for(let r=1;r<6 && !best;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){ const x=at[0]+dx, z=at[1]+dz; if(B(x,z)) continue; const d=dx*dx+dz*dz; if(d<bd){ bd=d; best=[x,z]; } } if(best) at=best; } return at; }
  function out(){ const S=cur && cur.S; if(!S){ try{ ISLE.back("market"); }catch(e){} return; } const at=doorAt(S);
    let nx=S.p[0]-S.door[0], nz=S.p[2]-S.door[1]; const L=Math.hypot(nx,nz)||1; nx/=L; nz/=L; const y0=cur.yaw0;
    go("isle", at, ()=>{ cleanup(); yaw=yawTo=y0; }, {from:[at[0]+.5+nx*.9, at[1]+.5+nz*.9]}); }
  function cleanup(){ ui(false); clear(); G.visible=false; cur=null; run=false; dirty=true; }

  /* ── 누르기 (house.html 바닥 누르기에서 부름) ── */
  const rc=new THREE.Raycaster(), v2=new THREE.Vector2();
  function tap(e){ if(!cur || trip.busy) return; cur.ao=false; v2.set(e.clientX/innerWidth*2-1, -(e.clientY/VH())*2+1); rc.setFromCamera(v2, camera);
    if(door && rc.intersectObject(door,true).length){ exit(); return; }
    if(keeper && rc.intersectObject(keeper.g,true).length){ goCounter(); return; }
    const cHit=deco ? rc.intersectObject(deco,true).find(h=>h.object.userData.sign) : null; if(cHit){ goCounter(); return; }
    { const hit=new THREE.Vector3(), H=[]; words.forEach(w=>{ if(w.box && rc.ray.intersectBox(w.box, hit)) H.push([w, hit.distanceTo(rc.ray.origin), w.box.getSize(new THREE.Vector3()).toArray().reduce((a,b)=>a*b,1)]); });
      const d0=Math.min(1e9, ...H.map(h=>h[1])), C=H.filter(h=>h[1]<d0+.7).sort((a,b)=>a[2]-b[2]), best=C.length?C[0][0]:null, bd=C.length?C[0][1]:1e9;   /* 선반 안 과일처럼 겹치면 작은 것 */
      const fl=floorPt(e); const fd=fl ? fl.distanceTo(rc.ray.origin) : 1e9;
      if(best && bd<fd+.05){ cur.auto=false; try{ say(best.en); }catch(er){} toast(best.ic+" <b>"+best.en+"</b> · "+best.ko, 1600); emote(hero, best.ic); hero.face=Math.atan2(best.box.getCenter(hit).x-hero.g.position.x, hit.z-hero.g.position.z); dirty=true; try{ tEv("shopword"); }catch(er){} return; } }
    const c=cellAt(e); if(!c) return; cur.auto=false;
    if(c[0]===DOOR[0] && c[1]===DOOR[1]){ exit(); return; }
    if(c[1]<=1 && c[0]>=2 && c[0]<=4){ goCounter(); return; }   /* 카운터·주인 칸 */
    walkTo(c[0], c[1]); }

  /* ── 이름표 · 아래 단추 ── */
  function labels(){ if(!cur) return []; const D=TH[cur.S.k];
    return [{k:"door", ic:"🚪", t:"나가기", p:[.1,2.25,N-.5], act:exit}, {k:cur.S.k, ic:cur.S.ic, t:D.nm+" · "+D.act, p:[3.5,1.36,.62], act:goCounter}]; }
  function ui(on){ let g=$("gShop"); if(!g){ g=document.createElement("div"); g.className="grp"; g.id="gShop";
      g.innerHTML='<button class="dk go" id="bSOut"><i>'+ic("door")+'</i><span>나가기</span></button><b class="sep"></b><button class="dk" id="bSBuy"><i>'+ic("shop")+'</i><span id="bSBuyT">가게</span></button><button class="dk" id="bSBag"><i>'+ic("bag")+'</i><span>가방</span></button>';
      const bar=document.querySelector(".bar.bot"); if(bar) bar.appendChild(g); $("bSOut").onclick=exit; $("bSBuy").onclick=goCounter; $("bSBag").onclick=()=>{ try{ openBag(); }catch(e){} }; }
    if(on && cur) $("bSBuyT").textContent=TH[cur.S.k].act; g.classList.toggle("on", !!on); }

  /* ── 움직임 (가게 안에 있을 때만 돎) — 주인 숨쉬기·손 흔들기 · 말풍선 · 수족관 물고기 · 이발소 기둥 ── */
  function frame(now){ if(!run) return; requestAnimationFrame(frame); const dt=Math.min(.05,(now-lastT)/1000); lastT=now;
    if(!cur){ return; }
    if(place!==PL.shop){ if(!trip.busy){ const S=cur.S, y0=cur.yaw0;   /* 지도·친구 집 등 다른 길로 나감 → 정리 · 친구 집에서 돌아올 곳 = 가게 문 앞 */
        try{ if(visitFrom && visitFrom.key==="shop") visitFrom={key:"isle", at:doorAt(S)}; }catch(e){} cleanup(); if(place===PL.isle){ yaw=yawTo=y0; } } return; }
    let a=false; if(keeper && animChar(keeper, dt)) a=true; if(keeper && keeper.act==="wave") a=true;
    if(cur.auto && !trip.busy && !hero.slide && F.st==="idle"){ if(!cur.greet) greet(); cur.auto=false; cur.ao=true; walkTo(SPOTC[0], SPOTC[1], ()=>{ hero.face=Math.PI; setTimeout(()=>{ if(cur && cur.ao && is() && !sheetOpen() && !avOpen && hero.cx===SPOTC[0] && hero.cz===SPOTC[1]) openSheet(); }, 380); }); }
    if(bub){ const B=bub; B.t+=dt; const k=B.t<.2?B.t/.2*1.1:B.t<.32?1.1-(B.t-.2)/.12*.1:1; B.s.scale.set(2.3*k,1.15*k,1); if(B.t>3.4){ B.s.material.opacity=Math.max(0,1-(B.t-3.4)/.4); if(B.t>3.8){ G.remove(B.s); B.s.material.map.dispose(); B.s.material.dispose(); bub=null; } } a=true; }
    tA+=dt; if(tA>.066){ anims.forEach(f=>{ try{ f(tA, now/1000); }catch(e){} }); tA=0; if(anims.length) a=true; }
    if(a) dirty=true; }

  try{ LBL_DEF.shop=labels; }catch(e){}
  return {G, N, TH, has, is, enter, exit, tap, labels, goCounter, cur:()=>cur && cur.S.k, words:()=>words, keeper:()=>keeper, deco:()=>deco, occ, DOOR, SPOTC};
})();
window.SHOPIN=SHOPIN;
