/* (v694) 🐾 단어 손님 — claude/hy-eng-plan-town-study.md 2번 · 사용자 「그래 너가 한번 해 봐라」
   Daily 30 에서 (오늘·어제) 처음 본 동물 단어 = 광장에 놀러 옴 ✨ · 며칠 뒤에도 맞힌 단어(기억 칸 3 이상) = 이사 옴 🏡 (모으기 n/17)
   이름표는 영어 · 누르면 그 동물이 영어로 한 줄(사실) + 🔊 · 🤚 쓰다듬기 · 🥕 간식(풀 먹는 동물) — 보석·코인 보상 없음(하트만)
   모형: Quaternius 움직이는 동물(isle-ani.js, CC0) · 고양이·토끼·병아리·판다 = 펫 가게 모형(TFAC.petMesh) */
const GUEST=(()=>{
  const D={
    cow:{a:"cow", h:1.35, f:["Cows give us milk.","소는 우리에게 우유를 줘요."], eat:1},
    ox:{a:"bull", h:1.4, f:["An ox can pull a heavy cart.","황소는 무거운 수레를 끌 수 있어요."], eat:1},
    bull:{a:"bull", h:1.45, f:["A bull has two big horns.","황소는 큰 뿔이 두 개 있어요."], eat:1, ko:"황소", e:"🐂"},
    horse:{a:"horse", h:1.65, f:["Horses can run very fast.","말은 아주 빨리 달려요."], eat:1},
    pony:{a:"pony", h:1.2, f:["A pony is a small horse.","조랑말은 작은 말이에요."], eat:1, ko:"조랑말", e:"🐴"},
    donkey:{a:"donkey", h:1.25, f:["Donkeys have long ears.","당나귀는 귀가 길어요."], eat:1},
    chick:{p:"chick", s:1.25, f:["A chick is a baby chicken.","병아리는 아기 닭이에요."], eat:1},
    dog:{a:"shiba", h:.82, f:["Dogs say, “Woof woof!”","개는 「멍멍!」 하고 짖어요."]},
    puppy:{a:"shiba", h:.62, f:["A puppy is a baby dog.","강아지는 아기 개예요."]},
    pup:{a:"shiba", h:.58, f:["A pup is a baby dog, too.","pup 도 아기 개예요."]},
    cat:{p:"cat", s:1.35, f:["Cats sleep a lot.","고양이는 잠을 많이 자요."]},
    kitten:{p:"cat", s:1, f:["A kitten is a baby cat.","새끼 고양이는 아기 고양이예요."]},
    rabbit:{p:"bunny", s:1.3, f:["Rabbits love carrots.","토끼는 당근을 좋아해요."], eat:1},
    deer:{a:"deer", h:1.4, f:["Deer eat leaves and grass.","사슴은 나뭇잎과 풀을 먹어요."], eat:1},
    fox:{a:"fox", h:.85, f:["A fox has a fluffy tail.","여우는 꼬리가 복슬복슬해요."]},
    wolf:{a:"wolf", h:1.05, f:["A wolf can howl. Awoooo!","늑대는 「아우~」 하고 울어요."]},
    panda:{p:"panda", s:1.9, f:["Pandas eat bamboo.","판다는 대나무를 먹어요."], eat:1},
  };
  const LIST=Object.keys(D), MAXG=4, FOOD=["carrot","apple","wheat","corn","strawberry","potato","tomato","watermelon","pumpkin"];
  const W_=()=>typeof ISLE_WORDS!=="undefined" ? ISLE_WORDS : [];
  const info=w=>{ const r=W_().find(x=>x[0]===w)||[]; return {e:D[w].e||r[2]||"🐾", ko:D[w].ko||r[1]||""}; };
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const day=()=>{ try{ return dayKey(); }catch(e){ return new Date().toISOString().slice(0,10); } };
  const dn=()=>Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5);
  let S=null; function st(){ if(!S){ S=store("hyeng_proto_guest")||{}; S.home=S.home||{}; S.seen=S.seen||{}; S.f=S.f||{}; } if(!S.td || S.td.d!==day()) S.td={d:day(), pet:{}, fed:{}}; return S; }
  function sv(){ store("hyeng_proto_guest", S); }
  function study(){ let o={}; try{ o=JSON.parse(localStorage.getItem("hyeng_study_v1")||"{}")||{}; }catch(e){} return {sd:o.sd||{}, srs:o.srs||{}}; }
  /* 누가 오나 — 이사(기억 칸 3+, 한 번 오면 계속) · 놀러(오늘·어제 처음 본 단어) */
  function who(){ const {sd, srs}=study(), t=dn(), s=st(); let ch=false; const vis=[], res=[];
    LIST.forEach(w=>{ const b=srs[w] ? (srs[w][0]|0) : 0; if(b>=3 && !s.home[w]){ s.home[w]=day(); ch=true; } if(s.home[w]) res.push(w); else if(sd[w]!=null && sd[w]>=t-1) vis.push(w); });
    if(ch) sv(); return {vis, res, sd, srs}; }
  function hs(a, b){ try{ return hashf(a)-hashf(b); }catch(e){ return 0; } }
  function maxG(){ try{ return PLV()>=2 ? 2 : MAXG; }catch(e){ return MAXG; } }   /* 렉 줄이기 2단계면 2마리 */
  function picks(){ const {vis, res}=who(), d=day(), M=maxG(), L=vis.slice(0,Math.min(2,M)).map(w=>[w,"v"]);
    res.slice().sort((a,b)=>hs("gq|"+d+"|"+a, "gq|"+d+"|"+b)).forEach(w=>{ if(L.length<M) L.push([w,"r"]); });
    return L; }
  function count(){ return Object.keys(st().home).filter(w=>D[w]).length; }

  /* ── 몸 만들기 ── */
  let C=null; const A=[]; let FC=null, built=false;
  /* 옛 기기: 뼈 그림(float 꼭짓점 텍스처)이 없고 uniform 도 모자라면 움직이는 동물은 빼고 펫 모형만 */
  function aniOk(){ try{ const c=renderer.capabilities; return !!c.floatVertexTextures || Math.floor((c.maxVertexUniforms-20)/4)>=56; }catch(e){ return true; } }
  function body(w){ const d=D[w];
    if(d.a){ if(!aniOk()) return null; const m=window.ANI && ANI.make(d.a, {h:d.h}); if(!m) return null; return {kind:"a", m, g:m.g, hy:d.h}; }
    let g=null; try{ g=TFAC.petMesh(d.p); }catch(e){} if(!g) return null; const root=new THREE.Group(); g.scale.setScalar(d.s||1); root.add(g); return {kind:"p", g:root, B:g.userData.body||g, hy:(d.p==="chick"?.66:.9)*(d.s||1)}; }
  function bad(x, z){ try{ return ISLE.blocked(Math.floor(x), Math.floor(z)) || ISLE.busyAt(x, z, .7); }catch(e){ return false; } }   /* 막힌 칸 + 화분·의자 같은 장식 둘레 */
  function free(x, z){ if(bad(x,z)) return false; return !A.some(G=>G.g && Math.hypot(G.g.position.x-x, G.g.position.z-z)<1.6); }
  function lineFree(x0,z0,x1,z1){ for(let k=1;k<=6;k++){ const t=k/6; if(bad(x0+(x1-x0)*t, z0+(z1-z0)*t)) return false; } return true; }
  function spot(i, n){ for(let k=0;k<24;k++){ const an=(i/Math.max(1,n))*Math.PI*2+.4+k*.53, r=4.2+((k*1.7+i)%4); const x=FC[0]+Math.cos(an)*r, z=FC[1]+Math.sin(an)*r; if(free(x,z)) return [x,z]; } return [FC[0]+4.5, FC[1]+4.5]; }
  function add(w, kind, i, n){ const b=body(w); if(!b) return; const p=spot(i, n); b.g.position.set(p[0], 0, p[1]); b.g.rotation.y=Math.random()*6.28; b.g.traverse(o=>{ o.userData.guest=w; if(o.isMesh){ o.castShadow=true; } });
    C.G.add(b.g); try{ TOON.scan(b.g); }catch(e){}
    const c={g:b.g, n:{id:"g_"+w, nm:w}, face:b.g.rotation.y, talking:false, emo:null};
    const G=Object.assign(b, {w, kind0:kind, c, L:[p[0], b.hy+.55, p[1]], tgt:null, wait:1+Math.random()*3, st:"idle", t:0, hop:0});
    try{ if(typeof VOICE!=="undefined") VOICE[c.n.id]=Math.round(820-Math.min(1.6,b.hy)*380); }catch(e){}
    A.push(G); }
  function build(ctx){ C=ctx; A.length=0; FC=[C.OX, C.OZ]; built=true; const L=picks(); if(!L.length) return;
    const need=[...new Set(L.map(([w])=>D[w].a).filter(Boolean))];
    Promise.all(need.map(k=>window.ANI ? ANI.load(k) : null)).then(()=>{ L.forEach(([w,k],i)=>{ try{ add(w,k,i,L.length); }catch(e){ console.warn("GUEST", w, e); } }); try{ dirty=true; }catch(e){} try{ if(place===PL.isle) drawLabels(); }catch(e){} }); }   /* 다 읽은 뒤 이름표 다시 */

  /* ── 움직임 ── */
  function setSt(G, s, dur){ G.st=s; G.t=0; G.dur=dur||0; if(G.kind!=="a") return; const m=G.m;
    if(s==="walk") m.play("Walk", .25); else if(s==="eat"){ if(m.has("Eating")) m.play("Eating", .25); else m.play("Idle", .25); } else if(s==="happy"){ if(m.has("Jump_ToIdle")) m.play("Jump_ToIdle", .12, true); else m.play("Idle", .2); } else m.play("Idle", .3); }
  function pickTgt(G){ const p=G.g.position; for(let k=0;k<8;k++){ const an=Math.random()*Math.PI*2, r=3.8+Math.random()*4.8, x=FC[0]+Math.cos(an)*r, z=FC[1]+Math.sin(an)*r;
      if(Math.hypot(x-p.x, z-p.z)<1.5 || Math.hypot(x-p.x, z-p.z)>6) continue; if(free(x,z) && lineFree(p.x,p.z,x,z)) return [x,z]; } return null; }
  function tick(dt){ if(!built || !A.length || !C || !C.G.visible) return false; let a=false; const hp=hero.g.position, near=Math.hypot(hp.x-FC[0], hp.z-FC[1])<46;
    A.forEach(G=>{ if(G.g.visible!==near){ G.g.visible=near; a=true; } }); if(!near) return a;
    A.forEach(G=>{ const p=G.g.position, c=G.c; G.t+=dt;
      if(G.st==="eat" || G.st==="happy"){ const jd=G.st==="happy" && G.kind==="a" && G.m.has("Jump_ToIdle"); if(G.t>=(G.dur||1.2) && (!jd || G.m.done())){ setSt(G,"idle"); G.wait=2+Math.random()*3; } }
      if(c.talking || G.hold>0){ if(G.hold>0) G.hold-=dt; G.tgt=null; if(G.st==="walk") setSt(G,"idle"); c.face=Math.atan2(hp.x-p.x, hp.z-p.z); }
      else if(G.st==="idle"){ G.wait-=dt; if(G.wait<=0){ if(D[G.w].eat && Math.random()<.35) setSt(G,"eat", G.kind==="a"?3.2:2.2); else { G.tgt=pickTgt(G); if(G.tgt) setSt(G,"walk"); else G.wait=2; } } }
      else if(G.st==="walk"){ if(!G.tgt){ setSt(G,"idle"); G.wait=2; } else { const dx=G.tgt[0]-p.x, dz=G.tgt[1]-p.z, d=Math.hypot(dx,dz), sp=Math.max(.45, Math.min(1.1, G.hy*.75))*dt; c.face=Math.atan2(dx,dz);
        if(d<sp){ p.x=G.tgt[0]; p.z=G.tgt[1]; G.tgt=null; setSt(G,"idle"); G.wait=3+Math.random()*5; } else { p.x+=dx/d*sp; p.z+=dz/d*sp; } } }
      /* 몸 돌리기 · 애니 */
      let dy=c.face-G.g.rotation.y; dy=Math.atan2(Math.sin(dy), Math.cos(dy)); G.g.rotation.y+=dy*Math.min(1, dt*6);
      if(G.kind==="a"){ G.m.tick(dt); const bb=G.m.body; if(G.st==="happy" && !G.m.has("Jump_ToIdle")) bb.position.y=Math.abs(Math.sin(G.t*9))*.18*Math.max(0, 1-G.t/1.2); else if(bb.position.y) bb.position.y=0; }
      else { const B=G.B; if(G.st==="walk"){ G.hop+=dt*11; B.position.y=Math.abs(Math.sin(G.hop))*.07; B.rotation.z=0; B.rotation.x=0; } else if(G.st==="eat"){ B.position.y=0; B.rotation.x=Math.max(0, Math.sin(G.t*7))*.22; } else if(G.st==="happy"){ B.position.y=Math.abs(Math.sin(G.t*10))*.22*Math.max(0,1-G.t/1.2); B.rotation.x=0; } else { B.position.y=0; B.rotation.x=0; B.rotation.z=Math.sin(G.t*1.7)*.05; } }
      if(c.emo && c.emo.s) c.emo.s.position.y=G.hy+.5;
      G.L[0]=p.x; G.L[1]=G.hy+.55; G.L[2]=p.z; a=true; });
    return a; }

  /* ── 이름표 · 말 걸기 ── */
  function tag(G){ const s=st(); return G.kind0==="v" ? " ✨" : (!s.seen[G.w] ? " 🆕" : ""); }
  function labels(L){ A.forEach(G=>{ const nw=G.kind0==="r" && !st().seen[G.w]; L.push({k:"g_"+G.w, ic:info(G.w).e, t:G.w+tag(G), p:G.L, r:nw?9:5.5, act:()=>talk(G)}); }); }
  function walkNear(p, then){ const x=Math.floor(p[0]), z=Math.floor(p[2]); let best=null; for(let r=1;r<4 && !best;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){ if(Math.max(Math.abs(dx),Math.abs(dz))!==r) continue; try{ if(!ISLE.blocked(x+dx,z+dz)){ best=[x+dx,z+dz]; break; } }catch(e){} }
    const hp=hero.g.position; if(Math.hypot(hp.x-p[0],hp.z-p[2])<2.6 || !best){ then(); return; } try{ walkTo(best[0],best[1],then); }catch(e){ then(); } }
  function talk(G){ G.tgt=null; G.hold=8; if(G.st==="walk") setSt(G,"idle");   /* 걸어가는 동안 멈춰서 기다림 (8초) */
    walkNear([G.g.position.x,0,G.g.position.z], ()=>{ G.hold=0; G.c.prov=prov(G); try{ talkTo(G.c); }catch(e){ G.c.talking=false; } }); }
  const NL=(en,ko,emo)=>({en,ko,emo,who:"npc"}), ML=(en,ko,emo)=>({en,ko,emo,who:"me",say:false});
  function food(){ try{ return FOOD.find(k=>(mats[k]|0)>0)||""; }catch(e){ return ""; } }
  function hearts(w){ const f=Math.min(5, st().f[w]|0); return "♥".repeat(f)+"♡".repeat(5-f); }
  function prov(G){ const w=G.w, d=D[w], I=info(w);
    return {
      nameHtml:()=>I.e+" "+esc(w)+'<i>'+hearts(w)+'</i>',
      start(){ const s=st(), L=[], home=!!s.home[w]; try{ say(w); }catch(e){} setSt(G,"happy",1.2);
        if(!s.seen[w]){ s.seen[w]=1; sv(); L.push(home ? NL("Hi! I live here now!","안녕! 나 이제 여기 살아! 🏡 (단어 손님 "+count()+"/"+LIST.length+")","🏡") : NL("Hi! You learned my name today!","안녕! 오늘 내 이름 배웠지? 「"+w+"」 = "+I.ko,"✨")); }
        else L.push(NL(["Hello, friend!","Hi again!","Nice to see you!"][Math.floor(Math.random()*3)], "안녕, 친구!","🎵"));
        L.push(NL(d.f[0], d.f[1], "💡")); speakLines(L); },
      choices(){ const s=st(), C=[["say","🔊 "+w, I.ko]]; if(!s.td.pet[w]) C.push(["pet","🤚 Pat, pat!","쓰다듬기"]);
        const fd=food(); if(d.eat && !s.td.fed[w] && fd) C.push(["treat",(MAT[fd]||{}).e+" Here's a treat!","간식 주기"]);
        C.push(["book","📖 단어 손님 "+count()+"/"+LIST.length,"모은 동물 보기"]); C.push(["bye","👋 Bye!","잘 있어!"]); return C; },
      choose(k, me){ const s=st();
        if(k==="say"){ try{ say(w); }catch(e){} setSt(G,"happy",1); showChoices(); return; }
        if(k==="pet"){ s.td.pet[w]=1; s.f[w]=(s.f[w]|0)+1; sv(); setSt(G,"happy",1.2); try{ emote(G.c,"❤️"); }catch(e){} try{ SND.big(); }catch(e){}
          speakLines([ML(me[1].replace(/^\S+\s/,""), me[2]), NL(["Yay! I like you!","Hee hee! That tickles!","Thank you!"][Math.floor(Math.random()*3)],"좋아! ❤️","💖")]); return; }
        if(k==="treat"){ const fd=food(); if(!fd){ showChoices(); return; } try{ addMat(fd,-1); saveBag(); updBagBtn(); }catch(e){} s.td.fed[w]=1; s.f[w]=(s.f[w]|0)+2; sv(); setSt(G,"eat", 3); try{ emote(G.c,(MAT[fd]||{}).e||"😋"); }catch(e){}
          speakLines([ML("Here's a treat! "+((MAT[fd]||{}).e||""),"간식이야!"), NL("Yum yum! Thank you!","냠냠! 고마워!","😋")]); return; }
        if(k==="book"){ try{ closeTalk(); }catch(e){} openBook(); return; }
        if(k==="bye"){ speakLines([ML("Bye!","잘 있어!"), NL("Bye! See you!","안녕! 또 봐!","👋")], ()=>setTimeout(()=>{ try{ closeTalk(); }catch(e){} }, 400)); return; } } }; }

  /* ── 📖 단어 손님 모음 ── */
  let el=null;
  function sheet(){ if(el) return el; const css=document.createElement("style"); css.textContent=`
#gbP{left:50%;right:auto;width:min(720px,100vw);transform:translate(-50%,105%);padding:0;display:flex;flex-direction:column;max-height:min(80vh,760px);overflow:hidden;background:#fffaf0}
#gbP.on{transform:translate(-50%,0)} #gbP::before{display:none}
#gbP .gHd{flex:none;display:flex;align-items:center;gap:10px;padding:12px 12px 4px} #gbP .gHd .t{flex:1;min-width:0} #gbP .gHd b{display:block;font-size:18px} #gbP .gHd small{display:block;font-size:12.5px;color:var(--sub);line-height:1.35}
#gbP .gX{flex:none;width:38px;height:38px;border-radius:50%;border:2.5px solid var(--line2);background:#fff;font-size:16px}
#gbP .gBar{flex:none;margin:4px 12px 8px;height:10px;border-radius:6px;background:#efe4d2;overflow:hidden} #gbP .gBar s{display:block;height:100%;background:linear-gradient(90deg,#ffb84d,#ff8a3d)}
#gbP .gB{flex:1;min-height:0;overflow-y:auto;padding:2px 12px calc(14px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:8px}
#gbP .gC{display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 4px 7px;border-radius:16px;border:2.5px solid var(--line);background:#fff;font:inherit;color:var(--ink);min-height:118px}
#gbP .gC i{font-style:normal;font-size:38px;line-height:1.15} #gbP .gC b{font:800 15px/1.2 var(--en)} #gbP .gC small{font-size:11.5px;color:var(--sub)} #gbP .gC em{font-style:normal;font-size:11px;font-weight:800;border-radius:99px;padding:1px 7px;margin-top:2px}
#gbP .gC.home{border-color:#ffb84d;background:#fff7e6} #gbP .gC.home em{background:#ffe1a8;color:#8a5a00}
#gbP .gC.vis{border-color:#7fc8f8;background:#f0f8ff} #gbP .gC.vis em{background:#d4ecff;color:#1f5f8b}
#gbP .gC.lrn em{background:#eef6e6;color:#4f7a2a}
#gbP .gC.lock i{filter:grayscale(1) brightness(.25);opacity:.55} #gbP .gC.lock b{color:#b9ad9c} #gbP .gC.lock em{background:#f1ece4;color:#9b8f80}`; document.head.appendChild(css);
    el=document.createElement("div"); el.id="gbP"; el.className="sheet"; document.body.appendChild(el); try{ SHEETS.push("gbP"); }catch(e){}
    el.addEventListener("click", e=>{ if(e.target.closest("[data-gx]")){ el.classList.remove("on"); return; } const c=e.target.closest("[data-gw]"); if(c){ try{ say(c.dataset.gw); }catch(er){} } }); return el; }
  function drawBook(){ const s=st(), {vis, sd, srs}=who(), n=count();
    let h='<div class="gHd"><span style="font-size:32px">🐾</span><span class="t"><b>단어 손님 '+n+' / '+LIST.length+'</b><small>📚 Daily 30 에서 배운 동물이 놀러 와요 ✨<br>며칠 뒤에도 맞히면 이사 와요 🏡</small></span><button class="gX" data-gx aria-label="닫기">✕</button></div>';
    h+='<div class="gBar"><s style="width:'+Math.round(n/LIST.length*100)+'%"></s></div><div class="gB">';
    h+=LIST.map(w=>{ const I=info(w), home=!!s.home[w], v=vis.indexOf(w)>=0, b=srs[w]?(srs[w][0]|0):0, lrn=sd[w]!=null;
      const cl=home?"home":v?"vis":lrn?"lrn":"lock", st2=home?"🏡 "+hearts(w):v?"✨ 놀러 왔어요":lrn?"📚 기억 "+Math.min(b,3)+"/3":"🔒 아직";
      return '<button class="gC '+cl+'"'+(cl!=="lock"?' data-gw="'+esc(w)+'"':'')+'><i>'+I.e+'</i><b>'+(cl==="lock"?"???":esc(w))+'</b><small>'+(cl==="lock"?"&nbsp;":esc(I.ko))+'</small><em>'+st2+'</em></button>'; }).join("");
    el.innerHTML=h+'</div>'; }
  function openBook(){ sheet(); drawBook(); el.classList.add("on"); }
  return {build, tick, labels, openBook, who, picks, count, LIST, D, A:()=>A, C:()=>A.map(G=>G.c), st, talk:w=>{ const G=A.find(x=>x.w===w); if(G) talk(G); }};
})();
window.GUEST=GUEST;
