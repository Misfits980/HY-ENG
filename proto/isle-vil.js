/* ═════════ (v587) 🍄 버섯 마을 — 사용자: 「새로 마을을 만들어 주고 퀘스트를 줘 · 아이들이 은화 20개 30개씩 퀘스트를 고르게」
   · 「1번(마을 사람 + 의뢰판) 2번(섬 빈 자리에 새 마을 구역) 을 하는데 의뢰도 하면서 마을만의 뭔가가 있으면 좋겠어」
   · 섬 서쪽(주택가 1동 끝에서 이어지는 길) 「🍄 버섯 마을」 — 버섯 집 4채 · 광장 · 📌 의뢰판 · 🍄 큰 버섯(마을 자랑)
   · 마을 사람 4명(Tom 농부 · Lily 빵집 · Sam 어부 · Joe 광부)이 광장을 걸어 다님 — 누르면 영어로 말하고 그 사람 의뢰
   · 📌 의뢰판: 오늘의 의뢰 6개(모든 아이 같음, 날마다 바뀜) 중 3개까지 골라 받기 → 하면 🪙 20 / 30 + ❤️ 그 사람 하트
     가져다주기(당근 3개 …) 는 가진 걸 건네고, 해 오기(물고기 3마리 잡기 …) 는 받은 뒤부터 센 것
   · 마을만의 것 = ❤️ 이웃 하트 — 하트를 모으면 마을에서만 받는 🍄 버섯 가구 선물(버섯 의자 · 버섯 등 · 버섯 집) · 날마다 🍄 큰 버섯에 인사하면 작은 선물
   · 기록: hyeng_proto_vil {d, acc:{key:{c}}, done:{key:1}, h:{tom:n}, g:{gift:1}, w:day} */
const VIL=(()=>{
  if(!window.ISLE) return null;
  const NPC=[
    {id:"tom",  nm:"Tom",  job:"농부",  ic:"🧑‍🌾", cap:0xff5a5a, av:{skin:1, hair:"short", hc:1, style:"overalls", top:3, pc:2, hat:"straw", acc:"none"}, hi:["Hi! My carrots are the best!","안녕! 우리 당근이 최고야!"]},
    {id:"lily", nm:"Lily", job:"빵집",  ic:"👩‍🍳", cap:0xffb84d, av:{skin:0, hair:"bun", hc:6, style:"dress", top:6, pc:5, hat:"none", acc:"ribbon"}, hi:["Welcome! Something smells sweet!","어서 와! 달콤한 냄새가 나지?"]},
    {id:"sam",  nm:"Sam",  job:"어부",  ic:"🧔", cap:0x4f9be8, av:{skin:2, hair:"short", hc:0, style:"hoodie", top:1, pc:1, hat:"beanie", acc:"none"}, hi:["The lake is calm today.","오늘 호수가 잔잔해."]},
    {id:"joe",  nm:"Joe",  job:"광부",  ic:"👴", cap:0xa77be8, av:{skin:1, hair:"spiky", hc:4, style:"tee", top:7, pc:2, hat:"cap", acc:"glasses"}, hi:["Rocks and gems, that's my life!","돌이랑 보석이 내 인생이지!"]}];
  const NB={}; NPC.forEach(n=>NB[n.id]=n);
  /* 의뢰 틀 — kind b = 가져다주기(item·n) · d = 해 오기(ev·n) · r = 🪙 */
  const QT=[
    ["tom","b","carrot",3,20,"Can you bring me 3 carrots?","당근 3개 갖다 줄래?"],
    ["tom","b","wheat",5,20,"I need 5 wheat for my cows.","소한테 줄 밀 5개가 필요해."],
    ["tom","b","potato",3,30,"Bring me 3 potatoes, please!","감자 3개 갖다 줘!"],
    ["tom","d","plant",3,20,"Please plant 3 seeds today!","오늘 씨앗 3개 심어 줘!"],
    ["tom","d","harvest",2,30,"Harvest 2 fields for me!","밭 두 번 거둬 줘!"],
    ["lily","b","apple",3,20,"I want 3 apples for a pie.","파이 만들 사과 3개가 필요해."],
    ["lily","b","strawberry",2,30,"Strawberries! Can I have 2?","딸기 2개 줄 수 있어?"],
    ["lily","b","tomato",2,20,"I need 2 tomatoes for pizza.","피자 만들 토마토 2개!"],
    ["lily","d","cook",1,30,"Cook something yummy!","맛있는 요리 하나 만들어 줘!"],
    ["lily","d","eat",1,20,"Eat a snack with me!","간식 하나 먹어 봐!"],
    ["sam","d","catch",3,20,"Catch 3 fish for me!","물고기 3마리 잡아 줘!"],
    ["sam","d","catch",6,30,"Wow! Can you catch 6 fish?","우와, 6마리 잡을 수 있어?"],
    ["sam","b","fish",2,30,"Bring me 2 fish, please.","물고기 2마리 갖다 줘."],
    ["sam","d","sell",3,20,"Sell 3 things at the fish shop!","생선 가게에서 3번 팔아 봐!"],
    ["joe","b","stone",4,20,"I need 4 stones to fix my wall.","벽 고칠 돌 4개가 필요해."],
    ["joe","b","branch",4,20,"Can you bring me 4 branches?","나뭇가지 4개 갖다 줄래?"],
    ["joe","b","coal",2,30,"Bring me 2 coal from the mine!","광산에서 석탄 2개!"],
    ["joe","d","mine",3,30,"Go to the mine and dig 3 times!","광산에서 3번 캐 봐!"],
    ["joe","d","tree",3,20,"Shake 3 trees for me!","나무 3번 흔들어 줘!"],
    ["joe","d","clear",3,20,"Pull 3 weeds in your yard!","마당 잡초 3개 뽑아 줘!"]
  ].map(([who,k,x,n,r,en,ko],i)=>({id:"q"+i, who, kind:k, x, n, r, en, ko}));
  const EV_KO={plant:"🌱 씨앗 심기", harvest:"🧺 거두기", cook:"🍳 요리", eat:"😋 먹기", catch:"🎣 낚기", sell:"🪙 팔기", mine:"⛏ 캐기", tree:"🌳 흔들기", clear:"🌿 잡초 뽑기"};
  const MAXA=3;
  const GIFT=[[3,"mushstool","🍄 버섯 의자"],[8,"mushlamp","🍄 버섯 등"],[15,"mushhut","🍄 버섯 집"]];
  const day=()=>{ try{ return dayKey(); }catch(e){ return new Date().toISOString().slice(0,10); } };
  let S=null; function st(){ if(!S){ S=store("hyeng_proto_vil")||{}; S.acc=S.acc||{}; S.done=S.done||{}; S.h=S.h||{}; S.g=S.g||{}; } if(S.d!==day()){ S.d=day(); S.acc={}; S.done={}; sv(); } return S; }
  function sv(){ store("hyeng_proto_vil", S); }
  /* 오늘의 의뢰 6개 — 날짜로 섞음 (모든 아이 같음) · 사람마다 1개 이상 */
  function today(){ const d=day(), pick=[]; NPC.forEach(n=>{ const L=QT.filter(q=>q.who===n.id && ok(q)); if(L.length) pick.push(L[Math.floor(hashf("vq|"+d+"|"+n.id)*L.length)]); });
    const rest=QT.filter(q=>pick.indexOf(q)<0 && ok(q)).sort((a,b)=>hashf("vr|"+d+"|"+a.id)-hashf("vr|"+d+"|"+b.id)); return pick.concat(rest).slice(0,6); }
  const ok=q=>q.kind==="d" || q.x==="fish" || !!MAT[q.x];
  const ie=q=>q.kind==="d" ? (EV_KO[q.x]||"✅").split(" ")[0] : q.x==="fish" ? "🐟" : MAT[q.x].e;
  const haveN=q=>q.kind==="d" ? ((st().acc[q.id]||{}).c|0) : q.x==="fish" ? bag.filter(b=>FISH_BY[b.en] && !(SPEC[b.en]||{}).junk).length : (mats[q.x]|0);
  const need=q=>q.kind==="d" ? (EV_KO[q.x]||q.x)+" "+q.n+"번" : ie(q)+" "+q.x+" ×"+q.n;
  /* 일 세기 — 받은 뒤 한 것만 (tEv 를 감쌈) */
  const _tEv=window.tEv; window.tEv=function(name){ try{ ev(name); }catch(e){} return _tEv.apply(this, arguments); };
  function ev(name){ const s=st(); let ch=false; today().forEach(q=>{ if(q.kind==="d" && s.acc[q.id] && !s.done[q.id] && q.x===name){ s.acc[q.id].c=(s.acc[q.id].c|0)+1; ch=true; if(s.acc[q.id].c===q.n){ setTimeout(()=>toast("📌 의뢰 끝! "+NB[q.who].ic+" <b>"+NB[q.who].nm+"</b> 에게 가서 🪙 "+q.r+" 받아요", 2400), 900); } } }); if(ch){ sv(); refresh(); } }
  const canDone=q=>haveN(q)>=q.n;
  function accept(q){ const s=st(); if(s.acc[q.id] || s.done[q.id]) return; if(Object.keys(s.acc).filter(k=>!s.done[k]).length>=MAXA){ toast("📌 의뢰는 한 번에 "+MAXA+"개까지 — 먼저 끝내요", 1800); return; }
    s.acc[q.id]={c:0, at:Date.now()}; sv(); try{ say(q.en); SND.pop(); }catch(e){} toast(NB[q.who].ic+" <b>"+NB[q.who].nm+"</b>: \""+q.en+"\"<br><small>"+q.ko+" · 🪙 "+q.r+"</small>", 2200); try{ _tEv("vquest"); }catch(e){} refresh(); }
  function claim(q){ const s=st(); if(!s.acc[q.id] || s.done[q.id] || !canDone(q)) return false;
    if(q.kind==="b"){ if(q.x==="fish"){ for(let k=0;k<q.n;k++){ let bi=-1, bv=1e9; bag.forEach((it,i)=>{ if(FISH_BY[it.en] && !(SPEC[it.en]||{}).junk){ const v=price(it); if(v<bv){ bv=v; bi=i; } } }); if(bi>=0) bag.splice(bi,1); } saveBag(); try{ updBagBtn(); }catch(e){} }
      else { addMat(q.x,-q.n); saveBag(); } }
    s.done[q.id]=1; s.h[q.who]=(s.h[q.who]|0)+1; sv(); try{ TECO.addCoin(q.r); }catch(e){}
    try{ say("Thank you!"); SND.big(); }catch(e){} const N=NB[q.who]; const npc=W.find(w=>w.n.id===q.who); if(npc){ npc.c.act="yay"; npc.c.t=0; setTimeout(()=>{ if(npc.c.act==="yay") npc.c.act="idle"; }, 1500); try{ emote(npc.c,"💖"); }catch(e){} }
    toast(N.ic+" <b>"+N.nm+"</b>: \"Thank you!\"<br>🪙 +"+q.r+" · ❤️ +1 <small>("+N.nm+" ❤️ "+s.h[q.who]+")</small>", 2400); try{ _tEv("vdone"); }catch(e){} gifts(); refresh(); return true; }
  const hearts=()=>Object.values(st().h).reduce((a,b)=>a+(b|0),0);
  function gifts(){ const s=st(), H=hearts(); GIFT.forEach(([n,id,nm])=>{ if(H>=n && !s.g[id]){ s.g[id]=1; sv(); try{ ystock[id]=(ystock[id]|0)+1; ySave(); }catch(e){} setTimeout(()=>{ try{ SND.win(); }catch(e){} toast("🎁 <b>버섯 마을 선물!</b> "+nm+"<br><small>마을 하트 ❤️ "+n+"개 — ✏️ 마당 꾸미기에서 놓아요</small>", 3200); }, 1600); } }); }
  /* 🍄 큰 버섯 — 하루 한 번 인사하면 작은 선물 */
  function bigShroom(){ const s=st(); try{ say("Hello, big mushroom!"); }catch(e){} if(s.w===day()){ toast("🍄 큰 버섯이 반짝반짝 — 내일 또 인사해요", 1600); return; } s.w=day(); sv();
    const r=hashf("bs|"+day()+"|"+(typeof myCode!=="undefined"?myCode:"")), g=r<0.4?["bait",2,"🪱 미끼 2"]:r<0.75?["coin",10,"🪙 10"]:["seed",1,"🍓 strawberry seeds 1"];
    if(g[0]==="bait"){ try{ setBait(bait+2); }catch(e){} } else if(g[0]==="coin"){ try{ TECO.addCoin(10); }catch(e){} } else { try{ addMat("strawberry seeds",1); saveBag(); }catch(e){} }
    try{ SND.sparkle ? SND.sparkle() : SND.pop(); emote(hero,"✨"); }catch(e){} toast("🍄 <b>큰 버섯</b>에게 인사했어요! 선물 "+g[2]+"<br><small>하루 한 번 · 버섯 마을의 자랑</small>", 2400); }
  /* ── 화면: 📌 의뢰판 (who = 그 사람만) ── */
  let el=null, who=null;
  function sheetEl(){ if(el) return el; const css=document.createElement("style"); css.textContent=`
#vlP{left:50%;right:auto;width:min(720px,100vw);transform:translate(-50%,105%);padding:0;display:flex;flex-direction:column;max-height:min(74vh,700px);overflow:hidden;background:#fffaf0}
#vlP.on{transform:translate(-50%,0)} #vlP::before{display:none}
#vlP .vAw{flex:none;height:14px;background:repeating-linear-gradient(90deg,#e85d5d 0 18px,#fff 18px 30px);border-radius:24px 24px 0 0}
#vlP .vHd{flex:none;display:flex;align-items:center;gap:10px;padding:10px 12px 6px}
#vlP .vHd .t{flex:1;min-width:0} #vlP .vHd b{display:block;font-size:17px} #vlP .vHd small{font-size:12px;color:var(--sub)}
#vlP .vX{width:36px;height:36px;border-radius:50%;border:2.5px solid var(--line2);background:#fff;font-size:16px}
#vlP .vNp{flex:none;display:flex;gap:6px;padding:0 12px 8px;overflow-x:auto;scrollbar-width:none}
#vlP .vNp button{flex:none;display:flex;align-items:center;gap:4px;height:36px;padding:0 10px;border-radius:999px;border:2.5px solid var(--line2);background:#fff;font:800 13px var(--en);color:var(--ink)} #vlP .vNp button.on{background:#ffe9c7}
#vlP .vNp i{font-style:normal;font-size:18px}
#vlP .vGf{flex:none;margin:0 12px 8px;padding:7px 10px;border-radius:14px;background:#fff1f4;font-size:12px;color:#8a3a55;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#vlP .vGf u{text-decoration:none;padding:2px 8px;border-radius:999px;background:#fff;border:2px solid #ffc2d1} #vlP .vGf u.got{background:#ffd6e2;border-color:#ff8fb0}
#vlP .vB{flex:1;min-height:0;overflow-y:auto;padding:2px 12px calc(14px + env(safe-area-inset-bottom) + var(--gapB,0px));display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:9px}
#vlP .vQ{position:relative;display:flex;gap:10px;align-items:center;padding:10px;border-radius:18px;border:2.5px solid var(--line);background:#fff;box-shadow:0 3px 0 rgba(90,60,30,.1)}
#vlP .vQ.acc{border-color:#ffb84d;background:#fffaf0} #vlP .vQ.fin{border-color:#7ed957;background:#f2fbea} #vlP .vQ.dn{opacity:.55}
#vlP .vQ .np{flex:none;width:46px;height:46px;border-radius:50%;display:grid;place-items:center;font-size:26px;border:2.5px solid var(--line2)}
#vlP .vQ .tx{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px} #vlP .vQ .tx b{font:800 14px/1.25 var(--en)} #vlP .vQ .tx small{font-size:12px;color:var(--sub)}
#vlP .vQ .nd{display:flex;align-items:center;gap:6px;font-size:12px;color:#6b5a4e} #vlP .vQ .bar{flex:1;max-width:120px;height:7px;border-radius:4px;background:#efe4d2;overflow:hidden} #vlP .vQ .bar s{display:block;height:100%;background:#7ed957}
#vlP .vQ .rw{flex:none;display:flex;flex-direction:column;align-items:center;gap:4px}
#vlP .vQ .rw em{font-style:normal;font:800 13px var(--en);color:#8a5a00;background:#fff1c9;border-radius:999px;padding:2px 9px}
#vlP .vQ .rw button{min-width:76px;height:38px;border-radius:12px;border:0;font:900 14px var(--kr);color:#fff;background:#ff8a3d;box-shadow:0 3px 0 rgba(0,0,0,.15)} #vlP .vQ .rw button.claim{background:#4caf50;animation:vlPulse 1s infinite} #vlP .vQ .rw button:disabled{background:#cfc6b6;box-shadow:none}
@keyframes vlPulse{50%{transform:scale(1.06)}}`; document.head.appendChild(css);
    el=document.createElement("div"); el.id="vlP"; el.className="sheet"; document.body.appendChild(el); try{ SHEETS.push("vlP"); }catch(e){}
    el.addEventListener("click", e=>{ if(e.target.closest("[data-vx]")){ el.classList.remove("on"); return; } const w=e.target.closest("[data-vw]"); if(w){ who=w.dataset.vw||null; draw(); return; }
      const a=e.target.closest("[data-acc]"), c=e.target.closest("[data-clm]"); const L=today(); if(a){ const q=L.find(x=>x.id===a.dataset.acc); if(q) accept(q); return; } if(c){ const q=L.find(x=>x.id===c.dataset.clm); if(q) claim(q); return; } });
    return el; }
  function draw(){ if(!el) return; const s=st(), L=today().filter(q=>!who || q.who===who), na=Object.keys(s.acc).filter(k=>!s.done[k]).length, H=hearts();
    const N=who?NB[who]:null;
    let h='<div class="vAw"></div><div class="vHd"><span style="font-size:30px">'+(N?N.ic:"📌")+'</span><span class="t"><b>'+(N?N.nm+" · "+N.job+" <small>❤️ "+(s.h[N.id]|0)+"</small>":"🍄 버섯 마을 의뢰판")+'</b><small>'+(N?'"'+N.hi[0]+'" '+N.hi[1]:"골라서 받고 → 하면 🪙 20 · 30 · ❤️ — 한 번에 "+MAXA+"개까지 (받은 것 "+na+"/"+MAXA+")")+'</small></span><button class="vX" data-vx aria-label="닫기">✕</button></div>';
    h+='<div class="vNp"><button data-vw="" class="'+(who?'':'on')+'"><i>📌</i>모두</button>'+NPC.map(n=>'<button data-vw="'+n.id+'" class="'+(who===n.id?'on':'')+'"><i>'+n.ic+'</i>'+n.nm+' ❤️'+(s.h[n.id]|0)+'</button>').join("")+'</div>';
    h+='<div class="vGf">🎁 이웃 하트 ❤️ <b>'+H+'</b> '+GIFT.map(([n,id,nm])=>'<u class="'+(s.g[id]?'got':'')+'">'+(s.g[id]?'✅ ':'❤️'+n+' → ')+nm+'</u>').join("")+'</div>';
    h+='<div class="vB">'+(L.length?L.map(q=>{ const n=NB[q.who], A=s.acc[q.id], D=s.done[q.id], hv=Math.min(haveN(q),q.n), fin=A && !D && canDone(q);
        return '<div class="vQ'+(D?' dn':fin?' fin':A?' acc':'')+'"><span class="np" style="background:#'+n.cap.toString(16).padStart(6,"0")+'33">'+n.ic+'</span><span class="tx"><b>"'+esc(q.en)+'"</b><small>'+n.nm+' · '+esc(q.ko)+'</small>'
          +'<span class="nd">'+need(q)+(A&&!D?' <span class="bar"><s style="width:'+Math.round(hv/q.n*100)+'%"></s></span> '+hv+'/'+q.n:'')+'</span></span>'
          +'<span class="rw"><em>🪙 '+q.r+'</em>'+(D?'<button disabled>✅ 끝</button>':fin?'<button class="claim" data-clm="'+q.id+'">받기!</button>':A?'<button disabled>하는 중</button>':'<button data-acc="'+q.id+'"'+(na>=MAXA?' disabled':'')+'>고르기</button>')+'</span></div>'; }).join("")
      : '<p style="padding:20px;color:var(--sub)">오늘은 의뢰가 없어요</p>')+'</div>';
    el.innerHTML=h; }
  function open(w){ if(typeof F!=="undefined" && F.st!=="idle") return; sheetEl(); who=w||null; draw(); el.classList.add("on"); if(w){ try{ say(NB[w].hi[0]); }catch(e){} } }
  function refresh(){ if(el && el.classList.contains("on")) draw(); }
  /* ── 🏗 짓기 (isle.js 가 TFAC 다음에 부름) ── */
  let C=null; const W=[]; let SP=null;
  function build(ctx){ C=ctx; W.length=0; const s=C.MAP.spots.vil; if(!s) return; SP=s; const OX=C.OX, OZ=C.OZ, G=new THREE.Group(); G.name="vil"; C.G.add(G);
    const M_=col=>C.MC(col), P_=(geo,col,x,y,z,o)=>{ const m=new THREE.Mesh(geo, M_(col)); m.position.set(x,y,z); if(o&&o.s) m.scale.set(o.s[0],o.s[1],o.s[2]); if(o&&o.ry) m.rotation.y=o.ry; m.castShadow=true; m.receiveShadow=true; m.userData.hx=col; return m; };
    /* 한 무리의 보통 색 조각 = 한 덩어리로 (그리는 횟수 ↓ · isle535 예산) — 빛나는 것·그림판은 따로 */
    const GLM=new THREE.MeshStandardMaterial({vertexColors:true, emissive:C.LIN(0xffe9a0), emissiveIntensity:.05, roughness:.6}); G.userData.glm=GLM;
    const GL_=(geo,col,x,y,z,o)=>{ const m=P_(geo,col,x,y,z,o); delete m.userData.hx; m.userData.gl=col; return m; };
    const mergeGL=H=>{ if(!C.vcMerge) return; const L=[]; H.children.slice().forEach(m=>{ if(m.isMesh && m.userData.gl!=null){ m.updateMatrix(); L.push({g:m.geometry, col:m.userData.gl, m:m.matrix.clone()}); H.remove(m); } }); if(L.length){ const mm=C.vcMerge(L, GLM); mm.castShadow=false; H.add(mm); } };
    const mergeG=H=>{ mergeGL(H); if(!C.vcMerge) return; const L=[]; H.children.slice().forEach(m=>{ if(m.isMesh && m.userData.hx!=null){ m.updateMatrix(); L.push({g:m.geometry, col:m.userData.hx, m:m.matrix.clone()}); H.remove(m); } }); if(L.length) H.add(C.vcMerge(L)); };
    C.disc(s[0], s[1], 7.2, 0xe9d8b4, 1); C.disc(s[0], s[1], 5.2, 0xf3e4c4, 2);
    /* 버섯 집 4채 — 광장을 봄 */
    const HS=[[-9.5,-4],[ -9.5,6],[9,7],[1,11]];
    NPC.forEach((n,i)=>{ const [dx,dz]=HS[i], x=s[0]+dx, z=s[1]+dz, ry=Math.atan2(s[0]-x, s[1]-z); const H=new THREE.Group(); H.position.set(x+OX,0,z+OZ); H.rotation.y=ry; H.userData.solo=1; G.add(H);
      H.add(P_(new THREE.CylinderGeometry(1.35,1.6,2.3,18),0xfff3dc,0,1.15,0));
      const cap=P_(new THREE.SphereGeometry(2.55,24,14,0,Math.PI*2,0,Math.PI/2),n.cap,0,2.15,0,{s:[1,.78,1]}); H.add(cap);
      H.add(P_(new THREE.CylinderGeometry(2.55,2.55,.18,24),0xfff8ee,0,2.13,0));
      for(let k=0;k<7;k++){ const a=k/7*Math.PI*2+i, rr=k%2?1.2:1.9, yy=2.15+Math.sqrt(Math.max(0,2.55*2.55-rr*rr))*.78; H.add(P_(new THREE.SphereGeometry(k%2?.26:.34,10,8),0xffffff,Math.cos(a)*rr,yy-.08,Math.sin(a)*rr,{s:[1,.45,1]})); }
      H.add(P_(new THREE.BoxGeometry(.7,1.15,.12),0x8a5a34,0,.58,1.52)); H.add(P_(new THREE.SphereGeometry(.05,8,6),0xffd23f,.22,.6,1.6));
      [[-.8,1.25],[.8,1.25]].forEach(([wx,wy])=>{ const w=GL_(new THREE.CircleGeometry(.24,16),0xbfe8ff,wx,wy,1.47+(Math.abs(wx)>.5?-.08:0)); w.rotation.y=wx*.35; H.add(w); });
      H.add(P_(new THREE.BoxGeometry(1.1,.06,.6),0xb07a4a,0,.03,1.95));
      [-1,1].forEach(sd=>{ for(let k=0;k<3;k++) H.add(P_(new THREE.SphereGeometry(.13,8,6),[0xff7aa8,0xffd23f,0xb28dff][k],sd*(1.0+k*.22),.15,1.75-k*.1)); });
      C.cols.push([x+OX,z+OZ,1.9]); C.busy.push([x,z,2.6]); const fr=[x+Math.sin(ry)*2.4, z+Math.cos(ry)*2.4]; n.door=fr; mergeG(H); try{ TOON.scan(H); }catch(e){} });
    /* 📌 의뢰판 */
    { const bx=s[0]+3.6, bz=s[1]-4.6, ry=Math.atan2(s[0]-bx, s[1]-bz); const B=new THREE.Group(); B.position.set(bx+OX,0,bz+OZ); B.rotation.y=ry; G.add(B);
      [-1.05,1.05].forEach(u=>B.add(P_(new THREE.CylinderGeometry(.08,.09,2.2,8),0x8a5a34,u,1.1,0))); B.add(P_(new THREE.BoxGeometry(2.4,1.4,.12),0xc9925c,0,1.45,0)); B.add(P_(new THREE.ConeGeometry(1.6,.6,4),0xe85d5d,0,2.45,0,{s:[1.05,1,.32],ry:Math.PI/4}));
      const cv=document.createElement("canvas"); cv.width=512; cv.height=300; const g=cv.getContext("2d"); g.fillStyle="#fff7e6"; g.fillRect(0,0,512,300); g.fillStyle="#3b2433"; g.font="bold 64px sans-serif"; g.textAlign="center"; g.fillText("📌 QUESTS",256,90); g.font="bold 46px sans-serif"; g.fillStyle="#8a5a34"; g.fillText("의뢰판",256,160);
      [["#ffd23f",90],["#7fc8f8",210],["#ff9ec0",330],["#b5e48c",440]].forEach(([c,x],i)=>{ g.save(); g.translate(x,235); g.rotate((i%2?.08:-.06)); g.fillStyle=c; g.fillRect(-48,-36,96,72); g.fillStyle="#e85d5d"; g.beginPath(); g.arc(0,-30,7,0,7); g.fill(); g.restore(); });
      const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; const f=new THREE.Mesh(new THREE.PlaneGeometry(2.2,1.28), new THREE.MeshBasicMaterial({map:tx})); f.position.set(0,1.45,.07); B.add(f);
      C.cols.push([bx+OX,bz+OZ,1.0]); C.busy.push([bx,bz,1.6]); SP.board=[bx+OX,2.7,bz+OZ]; mergeG(B); try{ TOON.scan(B); }catch(e){} }
    /* 🍄 큰 버섯 (마을 자랑) — 가운데에서 살짝 북쪽 · 밤엔 빛남 */
    { const bx=s[0]-1.2, bz=s[1]-1.6; const B=new THREE.Group(); B.position.set(bx+OX,0,bz+OZ); B.userData.solo=1; G.add(B);
      B.add(P_(new THREE.CylinderGeometry(.55,.85,3.2,16),0xfff3dc,0,1.6,0));
      const cap=new THREE.Mesh(new THREE.SphereGeometry(2.0,24,14,0,Math.PI*2,0,Math.PI/2), new THREE.MeshStandardMaterial({color:C.LIN(0x9b7be8), emissive:C.LIN(0x7a5af5), emissiveIntensity:.12, roughness:.6})); cap.position.y=3.0; cap.scale.y=.7; cap.castShadow=true; B.add(cap); B.userData.cap=cap;
      for(let k=0;k<8;k++){ const a=k/8*Math.PI*2, rr=k%2?.9:1.5; B.add(GL_(new THREE.SphereGeometry(.2,10,8),0xfff6b0,Math.cos(a)*rr,3.0+Math.sqrt(Math.max(0,4-rr*rr))*.7-.05,Math.sin(a)*rr,{s:[1,.45,1]})); }
      for(let k=0;k<6;k++){ const a=k/6*Math.PI*2+.3; B.add(P_(new THREE.SphereGeometry(.16,8,6),[0xff7aa8,0xffd23f,0xffffff][k%3],Math.cos(a)*1.1,.12,Math.sin(a)*1.1)); }
      C.cols.push([bx+OX,bz+OZ,1.0]); C.busy.push([bx,bz,1.8]); SP.big=[bx+OX,4.2,bz+OZ]; mergeG(B); try{ TOON.scan(B); }catch(e){} }
    /* 작은 버섯 등 (밤에 켜짐) */
    { const LG=new THREE.Group(); LG.position.set(s[0]+OX,0,s[1]+OZ); G.add(LG); for(let k=0;k<6;k++){ const a=k/6*Math.PI*2+.5, lx=Math.cos(a)*6.6, lz=Math.sin(a)*6.6; LG.add(P_(new THREE.CylinderGeometry(.06,.08,.8,8),0xfff3dc,lx,.4,lz)); LG.add(GL_(new THREE.SphereGeometry(.3,14,8,0,Math.PI*2,0,Math.PI/2),[0xff5a8a,0x4f9be8,0xffb020][k%3],lx,.78,lz,{s:[1,.7,1]})); C.busy.push([s[0]+lx,s[1]+lz,.6]); } mergeG(LG); }
    /* 마을 사람 */
    NPC.forEach((n,i)=>{ const c=buildAvatar(n.av);   /* 이름은 가까이 가면 이름표(LBL) — 머리 위 이름판과 두 겹이 되지 않게 */ c.g.traverse(m=>{ m.userData.vnpc=n.id; }); const a=i/NPC.length*Math.PI*2; c.g.position.set(s[0]+Math.cos(a)*3.4+OX,0,s[1]+Math.sin(a)*3.4+OZ); G.add(c.g);
      Object.assign(c, {t:0, act:"idle", face:a+Math.PI, moving:false}); const L=[0,1.95,0]; W.push({n, c, L, tgt:null, wait:1+i*.8}); try{ TOON.scan(c.g); }catch(e){} });
    G.traverse(o=>{ if(o.isSprite){ o.raycast=()=>{}; } });
    C.G.userData.vil=G; }
  /* 걸어 다니기 — 광장 안 (반지름 5) */
  function tick(dt){ if(!C || !W.length || !C.G.visible) return false; let a=false; const s=SP, OX=C.OX, OZ=C.OZ;
    { const S0=st(), hp=hero.g.position; if(!S0.seen && place===PL.isle && Math.hypot(hp.x-s[0]-OX, hp.z-s[1]-OZ)<12){ S0.seen=1; sv(); toast("🍄 <b>버섯 마을</b>에 왔어요!<br><small>📌 의뢰판에서 의뢰를 골라요 — 하면 🪙 20·30 · 마을 사람 ❤️</small>", 3200); try{ say("Welcome to the Mushroom Village!"); }catch(e){} } }
    { const hp=hero.g.position, d=Math.hypot(hp.x-s[0]-OX, hp.z-s[1]-OZ), G=C.G.userData.vil; const near=d<46; if(G && G.visible!==(d<70)){ G.visible=d<70; a=true; } W.forEach(w=>{ if(w.c.g.visible!==near){ w.c.g.visible=near; a=true; } }); if(!near) return a; }   /* 멀면 마을 사람은 안 그림 (그리는 횟수) */
    W.forEach(w=>{ const p=w.c.g.position;
      if(w.talk>0){ w.talk-=dt; w.c.moving=false; const hp=hero.g.position; w.c.face=Math.atan2(hp.x-p.x, hp.z-p.z); }
      else if(!w.tgt){ w.wait-=dt; w.c.moving=false; if(w.wait<=0){ const r=1.5+Math.random()*3.6, an=Math.random()*Math.PI*2; w.tgt=[s[0]+OX+Math.cos(an)*r, s[1]+OZ+Math.sin(an)*r]; } }
      else { const dx=w.tgt[0]-p.x, dz=w.tgt[1]-p.z, d=Math.hypot(dx,dz), sp=1.1*dt; if(d<sp){ p.x=w.tgt[0]; p.z=w.tgt[1]; w.tgt=null; w.wait=2+Math.random()*4; w.c.moving=false; } else { p.x+=dx/d*sp; p.z+=dz/d*sp; w.c.face=Math.atan2(dx,dz); w.c.moving=true; } }
      if(animChar(w.c, dt)) a=true; w.L[0]=p.x; w.L[2]=p.z; });
    return a || W.some(w=>w.c.moving); }
  function night(on){ const G=C && C.G.userData.vil; if(!G) return; if(G.userData.glm) G.userData.glm.emissiveIntensity=on?1.1:.05; G.traverse(o=>{ if(o.userData.cap) o.userData.cap.material.emissiveIntensity=on?.7:.12; }); try{ dirty=true; }catch(e){} }
  function labels(L){ if(!SP) return; const s=st();
    if(SP.board) L.push({k:"v_board", ic:"📌", t:"의뢰판"+(today().some(q=>s.acc[q.id] && !s.done[q.id] && canDone(q))?" ✅":""), p:SP.board, r:3.6, act:()=>walkNear(SP.board, ()=>open())});
    if(SP.big) L.push({k:"v_big", ic:"🍄", t:"큰 버섯", p:SP.big, r:3.4, act:()=>walkNear(SP.big, bigShroom)});
    W.forEach(w=>{ const n=w.n, fin=today().some(q=>q.who===n.id && s.acc[q.id] && !s.done[q.id] && canDone(q)); L.push({k:"v_"+n.id, ic:n.ic, t:n.nm+(fin?" ✅":""), p:w.L, r:3.2, act:()=>talk(w)}); }); }
  function walkNear(p, then){ const x=Math.floor(p[0]), z=Math.floor(p[2]); let best=null; for(let r=1;r<5 && !best;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){ if(Math.max(Math.abs(dx),Math.abs(dz))!==r) continue; if(!ISLE.blocked(x+dx,z+dz)){ best=[x+dx,z+dz]; break; } }
    const hp=hero.g.position; if(Math.hypot(hp.x-p[0],hp.z-p[2])<3.2 || !best){ then(); return; } walkTo(best[0],best[1],then); }
  function talk(w){ w.talk=6; const s=st(); const done=today().filter(q=>q.who===w.n.id && s.acc[q.id] && !s.done[q.id] && canDone(q));
    walkNear([w.c.g.position.x,0,w.c.g.position.z], ()=>{ w.c.act="wave"; w.c.t=0; setTimeout(()=>{ if(w.c.act==="wave") w.c.act="idle"; }, 1200);
      if(done.length){ done.forEach(q=>claim(q)); return; } open(w.n.id); }); }
  return {build, tick, labels, night, open, today, accept, claim, st, NPC, QT, GIFT, hearts, ev, bigShroom, W:()=>W, SP:()=>SP};
})();
window.VIL=VIL;
