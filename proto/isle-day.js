/* (v696) 🕰 하루 리듬 — claude/hy-eng-plan-town-study.md 3번 · 사용자 「그래 너가 한번 해 봐라」 (밤 시간은 기본값 · 바꾸기 쉽게)
   ① 🍾 병 편지 하루 1통 (등대 모래섬 바닷가 · 영어 한 문장 + 🔊 + 작은 선물)
   ② ✨ 반짝 땅 하루 3곳 (섬 곳곳 · 파면 돌·철·씨앗·과일)
   ③ 셋 다 하면 「✅ 오늘 섬 한 바퀴」 도장 (보석·코인 없음)
   ④ 밤 HOURS.close 시 ~ 아침 HOURS.open 시: 가게·은행 문 닫음(🌙) · 이웃은 잠듦(💤) — 산책·내 집 꾸미기·낚시·놀이는 그대로
   시험: window.HY_HOUR = 23 처럼 시각을 정하면 그 시각으로 봄 */
const DAYR=(()=>{
  if(!window.ISLE) return null;
  const HOURS={close:22, open:7};   /* ← 바꾸기: 밤 10시 ~ 아침 7시 */
  const CLOSE=new Set(["mart","snack","clothes","hair","photo","pet","furn","fish","f_bank"]);
  const T=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  function hour(){ if(window.HY_HOUR!=null) return +window.HY_HOUR; if(navigator.webdriver) return 12;   /* (v699) 자동 시험은 늘 낮 12시 — 밤(22~7시)에 돌리면 이웃·가게 시험(nb693 …)이 「자고 있어요」로 실패했음 · 밤 시험은 HY_HOUR 로 */ try{ return kstHM(T())[0]; }catch(e){ return new Date().getHours(); } }
  function night(){ const h=hour(); return HOURS.close>HOURS.open ? (h>=HOURS.close || h<HOURS.open) : (h>=HOURS.close && h<HOURS.open); }
  const day=()=>{ try{ return dayKey(); }catch(e){ return new Date().toISOString().slice(0,10); } };
  const hs=s=>{ try{ return hashf(s); }catch(e){ return .5; } };
  const code=()=>{ try{ return typeof myCode!=="undefined" ? myCode : ""; }catch(e){ return ""; } };
  let S=null; function st(){ if(!S) S=store("hyeng_proto_dayr")||{}; if(S.d!==day()){ S={d:day(), bottle:0, dig:{}, done:0}; } return S; }
  function sv(){ store("hyeng_proto_dayr", S); }
  /* 병 편지 — 아이 수준의 짧은 문장 (영어 + 한글) */
  const LET=[["The sea is very blue today.","오늘 바다가 아주 파래요."],["I found a pretty shell on the beach.","바닷가에서 예쁜 조개껍데기를 찾았어요."],["Do you like fish? I love fish!","물고기 좋아해? 나는 정말 좋아해!"],
    ["The sun is warm. Let's play outside!","햇살이 따뜻해요. 밖에서 놀자!"],["I saw a big whale last night.","어젯밤에 큰 고래를 봤어요."],["Have a happy day, friend!","좋은 하루 보내, 친구!"],
    ["My boat is small, but it is fast.","내 배는 작지만 빨라요."],["I can swim like a dolphin.","나는 돌고래처럼 수영할 수 있어요."],["The stars are bright on the sea.","바다 위 별들이 반짝여요."],
    ["Please plant this seed for me.","이 씨앗을 심어 줄래요?"],["The lighthouse helps the ships.","등대는 배들을 도와줘요."],["I am a little crab. Hello!","나는 작은 게예요. 안녕!"],
    ["It is windy today. Hold your hat!","오늘은 바람이 불어요. 모자 꽉 잡아!"],["Let's be friends!","우리 친구 하자!"],["Read a book and smile.","책을 읽고 웃어 봐요."],
    ["The rain makes the flowers happy.","비가 오면 꽃들이 좋아해요."],["I made a sandcastle. It's tall!","모래성을 만들었어요. 높아요!"],["Thank you for reading my letter.","내 편지를 읽어 줘서 고마워요."]];
  const GIFT=[["strawberry seeds",2,"🍓 딸기 씨앗"],["carrot seeds",3,"🥕 당근 씨앗"],["apple",2,"🍎 사과"],["pumpkin seeds",1,"🎃 호박 씨앗"],["corn seeds",2,"🌽 옥수수 씨앗"]];
  const DIG=[["stone",2,"🪨 돌 2개"],["iron",1,"🔩 철 1개"],["coal",1,"⚫ 석탄 1개"],["apple",1,"🍎 사과 1개"],["potato seeds",2,"🥔 감자 씨앗 2개"],["wheat seeds",3,"🌾 밀 씨앗 3개"]];
  /* ── 자리 ── */
  let C=null, B=null, DG=[], built=false; const OX=()=>ISLE.OX, OZ=()=>ISLE.OZ;
  const free=(x,z)=>{ try{ return !ISLE.blocked(Math.floor(x),Math.floor(z)) && !ISLE.busyAt(x,z,.6) && ISLE.inIsle(x,z); }catch(e){ return false; } };
  function bottleAt(){ const d=day(), b=(window.ISLE_MAP && ISLE_MAP.isles || []).find(q=>q.k==="beach"); const cx=b?b.cx:0, cz=b?b.cz:74, R=b?b.R:10;
    for(let k=0;k<24;k++){ const a=hs("bt|"+d+"|"+k)*Math.PI*2, r=R*(.55+hs("br|"+d+"|"+k)*.25), x=cx+Math.cos(a)*r+OX(), z=cz+Math.sin(a)*r+OZ(); if(free(x,z)) return [x,z]; } return null; }
  function digAt(){ const d=day(), c=code(), L=[]; for(let k=0;k<80 && L.length<3;k++){ const a=hs("dg|"+d+"|"+c+"|"+k)*Math.PI*2, r=12+hs("dr|"+d+"|"+c+"|"+k)*34, x=Math.cos(a)*r+OX(), z=Math.sin(a)*r+OZ();
      if(free(x,z) && L.every(p=>Math.hypot(p[0]-x,p[1]-z)>9)) L.push([x,z]); } return L; }
  function mkBottle(){ const g=new THREE.Group(); const gl=new THREE.MeshStandardMaterial({color:0x9fe0c8, transparent:true, opacity:.75, roughness:.2}), ck=new THREE.MeshStandardMaterial({color:0xb07a40, roughness:.8}), pp=new THREE.MeshStandardMaterial({color:0xfff3d0, roughness:.9});
    const b=new THREE.Mesh(new THREE.CylinderGeometry(.16,.16,.5,14), gl); b.rotation.z=Math.PI/2.3; b.position.y=.14; g.add(b);
    const n=new THREE.Mesh(new THREE.CylinderGeometry(.07,.09,.18,10), gl); n.position.set(.3,.25,0); n.rotation.z=Math.PI/2.3; g.add(n);
    const c=new THREE.Mesh(new THREE.CylinderGeometry(.06,.06,.1,10), ck); c.position.set(.39,.29,0); c.rotation.z=Math.PI/2.3; g.add(c);
    const p=new THREE.Mesh(new THREE.CylinderGeometry(.08,.08,.32,10), pp); p.rotation.z=Math.PI/2.3; p.position.y=.14; g.add(p);
    g.add(spark(.7)); g.traverse(o=>{ if(o.isMesh) o.castShadow=true; }); return g; }
  function spark(y){ const s=new THREE.Group(); const m=new THREE.MeshBasicMaterial({color:0xfff27a, transparent:true, opacity:.95, depthWrite:false});
    [0,1].forEach(i=>{ const q=new THREE.Mesh(new THREE.PlaneGeometry(.12,.7), m); q.rotation.z=i*Math.PI/2; s.add(q); }); s.position.y=y; s.userData.spark=1; return s; }
  function mkDig(){ const g=new THREE.Group(); const d=new THREE.Mesh(new THREE.CylinderGeometry(.42,.48,.06,16), new THREE.MeshStandardMaterial({color:0x8a5a34, roughness:1})); d.position.y=.03; g.add(d);
    for(let i=0;i<4;i++){ const pb=new THREE.Mesh(new THREE.SphereGeometry(.07,8,6), new THREE.MeshStandardMaterial({color:0x6b4426})); pb.position.set(Math.cos(i*1.7)*.32,.06,Math.sin(i*1.7)*.32); g.add(pb); }
    g.add(spark(.55)); return g; }
  function build(ctx){ C=ctx; built=true; const s=st();
    if(B){ C.G.remove(B.g); B=null; } DG.forEach(x=>C.G.remove(x.g)); DG=[];
    const bp=bottleAt(); if(bp && !s.bottle){ const g=mkBottle(); g.position.set(bp[0],0,bp[1]); g.rotation.y=hs("bry|"+day())*6.28; C.G.add(g); B={g, p:[bp[0],.6,bp[1]]}; }
    digAt().forEach((p,i)=>{ if(s.dig[i]) return; const g=mkDig(); g.position.set(p[0],0,p[1]); C.G.add(g); DG.push({i, g, p:[p[0],.5,p[1]]}); });
    try{ TOON.scan(C.G); }catch(e){} }
  /* ── 이름표 (밤엔 가게 닫힘) ── */
  function labels(L){ const s=st();
    if(B && !s.bottle) L.push({k:"dy_bottle", ic:"🍾", t:"병 편지", p:B.p, r:7, act:()=>near(B.p, openBottle)});
    DG.forEach(x=>{ if(!s.dig[x.i]) L.push({k:"dy_dig"+x.i, ic:"✨", t:"반짝 땅", p:x.p, r:5, act:()=>near(x.p, ()=>dig(x))}); });
    if(night()) L.forEach(d=>{ if(CLOSE.has(d.k)){ d.t=String(d.t).replace(/ 🌙.*$/,"")+" 🌙"; d.act=()=>toast("🌙 <b>"+d.t.replace(/ 🌙$/,"")+"</b> 문을 닫았어요<br><small>밤 "+(HOURS.close>12?HOURS.close-12:HOURS.close)+"시 ~ 아침 "+HOURS.open+"시는 쉬는 시간 · 아침에 다시 열어요</small>", 2600); } }); }
  function near(p, then){ const x=Math.floor(p[0]), z=Math.floor(p[2]); const hp=hero.g.position; if(Math.hypot(hp.x-p[0],hp.z-p[2])<2.2){ then(); return; }
    let best=null; for(let r=1;r<4 && !best;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){ if(Math.max(Math.abs(dx),Math.abs(dz))!==r) continue; try{ if(!ISLE.blocked(x+dx,z+dz)){ best=[x+dx,z+dz]; break; } }catch(e){} }
    if(!best){ then(); return; } try{ walkTo(best[0],best[1],then); }catch(e){ then(); } }
  function stamp(){ const s=st(); if(s.done || !s.bottle || Object.keys(s.dig).length<3) return; s.done=1; sv();
    setTimeout(()=>{ try{ SND.big(); }catch(e){} toast("✅ <b>오늘 섬 한 바퀴!</b><br><small>병 편지 · 반짝 땅 3곳 다 찾았어요 — 내일 또 새로 생겨요</small>", 3200); }, 900); }
  /* 🍾 병 편지 */
  let el=null;
  function sheet(){ if(el) return el; const css=document.createElement("style"); css.textContent=`
#dyLt{position:fixed;inset:0;z-index:21;display:none;align-items:center;justify-content:center;background:rgba(30,18,40,.45);padding:16px}
#dyLt.on{display:flex}
#dyLt .lp{width:min(420px,92vw);padding:22px 20px 18px;border-radius:22px;border:3px solid #3b2433;box-shadow:0 5px 0 #3b2433;background:repeating-linear-gradient(0deg,#fff8e2 0 30px,#f4e6c2 30px 31px);text-align:center;animation:pop .3s cubic-bezier(.2,.9,.3,1.3)}
#dyLt h3{margin:0 0 10px;font-size:15px;color:#8a6a4a} #dyLt .en{font:800 22px/1.35 var(--en);color:#3b2433;margin:6px 0} #dyLt .ko{font-size:14.5px;color:#8a6a4a;margin:0 0 12px}
#dyLt .gf{display:inline-block;margin:4px 0 12px;padding:6px 14px;border-radius:99px;background:#e9f8e4;border:2px solid #7ed957;font-weight:800}
#dyLt button{min-width:110px;height:46px;margin:0 4px;border-radius:14px;border:3px solid #3b2433;box-shadow:0 3px 0 #3b2433;font:900 16px var(--kr);background:#fff;color:#3b2433} #dyLt button.ok{background:#4caf50;color:#fff}
@media (min-width:700px) and (min-height:700px){ #dyLt .lp{width:min(560px,86vw);padding:30px 28px 24px} #dyLt .en{font-size:30px} #dyLt .ko{font-size:18px} #dyLt h3{font-size:18px} }`; document.head.appendChild(css);
    el=document.createElement("div"); el.id="dyLt"; document.body.appendChild(el);
    el.addEventListener("click", e=>{ const b=e.target.closest("button"); if(e.target===el || (b && b.dataset.x)){ el.classList.remove("on"); return; } if(b && b.dataset.say){ try{ tts(b.dataset.say); }catch(er){} } }); return el; }
  function openBottle(){ const s=st(); if(s.bottle) return; const L=LET[Math.floor(hs("lt|"+day()+"|"+code())*LET.length)], G=GIFT[Math.floor(hs("lg|"+day()+"|"+code())*GIFT.length)];
    s.bottle=1; sv(); try{ addMat(G[0], G[1]); saveBag(); updBagBtn(); }catch(e){} try{ SND.pop && SND.pop(); }catch(e){} try{ tEv("bottle"); }catch(e){}
    if(B){ C.G.remove(B.g); B=null; } try{ drawLabels(); }catch(e){}
    sheet().innerHTML='<div class="lp"><h3>🍾 바다에서 온 편지</h3><p class="en">“'+esc(L[0])+'”</p><p class="ko">'+esc(L[1])+'</p><span class="gf">🎁 '+G[2]+' ×'+G[1]+'</span><div><button data-say="'+esc(L[0])+'">🔊 듣기</button><button class="ok" data-x="1">고마워요!</button></div></div>';
    el.classList.add("on"); setTimeout(()=>{ try{ tts(L[0]); }catch(e){} }, 350); stamp(); }
  /* ✨ 반짝 땅 */
  function dig(x){ const s=st(); if(s.dig[x.i]) return; const R=DIG[Math.floor(hs("dd|"+day()+"|"+code()+"|"+x.i)*DIG.length)];
    s.dig[x.i]=1; sv(); try{ addMat(R[0], R[1]); saveBag(); updBagBtn(); }catch(e){} try{ hero.act="yay"; hero.actT=0; }catch(e){} try{ SND.pop && SND.pop(); }catch(e){}
    C.G.remove(x.g); DG=DG.filter(y=>y!==x); try{ drawLabels(); }catch(e){}
    const n=Object.keys(s.dig).length; toast("✨ 파 보니 <b>"+R[2]+"</b>!<br><small>오늘 반짝 땅 "+n+" / 3</small>", 2200); stamp(); }
  /* ── 시계: 밤/낮이 바뀌면 이름표 다시 · 날이 바뀌면 병·땅 새로 ── */
  let nt=0, lastN=null, lastD="";
  /* (v700) 🌙 밤에 섬에 들어오면 한 번만(밤마다) 알림 줄 — 창이 아니라 잠깐 뜨는 글 (사용자 원칙: 날마다 뜨는 창 없음) */
  function gnCheck(){ try{ if(!night() || place!==PL.isle) return; const k=String(Math.floor((Date.now()+9*3600e3-HOURS.open*3600e3)/864e5)); if(store("hyeng_proto_gn")===k) return; store("hyeng_proto_gn", k);   /* 밤 12시를 넘겨도 같은 밤 = 한 번 */
      toast("🌙 <b>Good night!</b> 가게는 밤 "+(HOURS.close>12?HOURS.close-12:HOURS.close)+"시 ~ 아침 "+HOURS.open+"시에 닫아요<br><small>오늘은 여기까지 하고, 내일 또 와요 · 산책·낚시·내 집은 그대로</small>", 4200); }catch(e){} }
  function tick(dt){ if(!built) return false; nt+=dt; let a=false; const t=performance.now()/1000;
    if(B){ const sp=B.g.children.find(o=>o.userData.spark); if(sp){ sp.rotation.y=t*2; sp.scale.setScalar(.8+Math.sin(t*5)*.25); a=true; } }
    DG.forEach(x=>{ const sp=x.g.children.find(o=>o.userData.spark); if(sp){ sp.rotation.y=t*2+x.i; sp.scale.setScalar(.7+Math.sin(t*4+x.i)*.3); a=true; } });
    if(nt>5){ nt=0; const n=night(), d=day(); if(lastD && d!==lastD){ S=null; build(C); try{ if(place===PL.isle) drawLabels(); }catch(e){} } lastD=d;
      gnCheck();
      if(lastN!==null && n!==lastN){ try{ if(place===PL.isle) drawLabels(); }catch(e){} try{ toast(n ? "🌙 밤이 됐어요 — 가게는 문을 닫고 이웃은 잠들었어요" : "🌅 아침이에요! 가게가 문을 열었어요", 2600); }catch(e){} } lastN=n; }
    return a; }
  function news(){ const s=st(); if(night()) return ["🌙","Good night, town!","밤 "+(HOURS.close>12?HOURS.close-12:HOURS.close)+"시 ~ 아침 "+HOURS.open+"시: 가게 닫힘 · 이웃은 쿨쿨 💤",""];
    if(s.done) return ["✅","You walked around the island!","오늘 섬 한 바퀴 끝 — 내일 또 새로 생겨요",""];
    if(!s.bottle) return ["🍾","A bottle is on the beach!","🏖 등대 모래섬 바닷가에 병 편지가 있어요 · 반짝 땅 "+Object.keys(s.dig).length+"/3",""];
    return ["✨","Find the shiny spots!","반짝 땅 "+Object.keys(s.dig).length+" / 3 — 섬 곳곳을 걸어 봐요",""]; }
  return {build, labels, tick, night, hour, HOURS, CLOSE, st, news, openBottle, B:()=>B, DG:()=>DG, digAt, bottleAt, gn:gnCheck};
})();
window.DAYR=DAYR;
