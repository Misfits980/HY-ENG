/* (v563) 💰 경제 2.0 — 사용자 (2026-11-02 밤):
   「환전소를 만드는 게 좋을 것 같아 · 아이들이 환전하면서 시세라는 감각도 늘 수 있어 · 역으로 보석으로 코인을 바꾸는 식도 · 가구에 보석+코인 두 개를 같이 써야 할 때」
   「은행도 만들어 · 적금해서 한 달마다 이자를 주는 복리 · 코인이든 보석이든 · 보석 상품은 적게 슬쩍」
   「아이들이 기본 보석이 좀 있어 · 물가를 조금 더 올려야 · 보석이랑 코인이 둘 다 털 수 있게」 「강화는 인플레 · 그걸 터는 수단 · 기차 같은 건 티켓 사야 이동」
   「경제 2.0 1~7 다 해 두자」
   🪙 코인 = 팔아서 벎(한도 없음) · 💎 보석 = 공부 · 🏦 마을 은행(환전 시세 · 두 방향 · 공부한 만큼 한도 · 적금 3가지 · 서버 시각)
   이용료(🚉 기차표 · 🗺 바로 가기 · 🎣 대회 참가비) · 🛠 강화 3가지(효과 작게 · 값 크게) · 📉 마을 시세(이번 시간 마을에서 많이 팔린 것은 값이 내려감)
   🌙 이달의 한정 가구 · 🏗 다 같이 마을 공사(🚧 빈 자리 3곳 = 🏊 수영장 · 🎡 관람차 · 🏰 성 놀이터) */
const TECO=(()=>{
  const K=10, SPREAD=0.7, BAIT_MAX=20, MON=30*864e5;
  const T=()=>{ try{ return (typeof TWN8!=="undefined" && TWN8.ok) ? srvNow() : now(); }catch(e){ return Date.now(); } };   /* (v563 QA) TWN8 은 const 라 window 에 없음 */
  const srvOK=()=>{ try{ return !!(TWN8.ok || navigator.webdriver); }catch(e){ return false; } };
  const day=()=>{ try{ return dayKey(); }catch(e){ return new Date().toISOString().slice(0,10); } };
  const r5=n=>Math.max(5, Math.round(n/5)*5), r10=n=>Math.max(10, Math.round(n/10)*10), fmt=n=>Number(n||0).toLocaleString("ko-KR");
  const myC=()=>{ try{ return myCode; }catch(e){ return "XXXXX"; } };
  const nick=()=>{ try{ return String(kidInfo().n||"친구").slice(0,10); }catch(e){ return "친구"; } };

  /* ═════════ 값 매기기 — 물가 조율판(v2) 기본값 ═════════
     V = 예전 💎 값(가구점 물가 ECON) · 💎85 넘는 큰 것만 ×1.6
     🪙만 = V × 5 · 💎+🪙 = 💎 V×0.6 + 🪙 V×0.4×10 · 💎만 = V */
  const BIG=85, BM=1.6, CF=0.5, SP=0.6;
  const big=V=>V>BIG ? V*BM : V;
  function cost(V, tier){ const v=big(V); if(tier==="coin") return {g:0, c:r5(v*K*CF)}; if(tier==="gem") return {g:r5(v), c:0}; return {g:r5(v*SP), c:r10(v*(1-SP)*K)}; }
  const tierOf=V=>V<=BIG ? "coin" : "mix";
  const cTxt=o=>{ const a=[]; if(o.g) a.push("💎 "+fmt(o.g)); if(o.c) a.push("🪙 "+fmt(o.c)); return a.join(" + ")||"무료"; };
  const cHtml=o=>{ const a=[]; if(o.g) a.push('<span class="teG">💎'+fmt(o.g)+'</span>'); if(o.c) a.push('<span class="teC">🪙'+fmt(o.c)+'</span>'); return a.join('<i class="teP">+</i>')||"무료"; };

  /* ═════════ 🪙 코인 ═════════ */
  let coin=+store("hyeng_proto_coin")||0;
  const coins=()=>coin;
  function setCoin(v){ coin=Math.max(0, Math.round(v)); store("hyeng_proto_coin", coin); hud(); sum(); }
  function addCoin(n){ if(!(n>0)) return 0; setCoin(coin+n); return n; }
  function can(o){ return gems>=(o.g|0) && coin>=(o.c|0); }
  function lack(o){ const a=[]; if(gems<(o.g|0)) a.push("💎 "+((o.g|0)-gems)); if(coin<(o.c|0)) a.push("🪙 "+((o.c|0)-coin)); return a.join(" · "); }
  /* 💎+🪙 함께 쓰기 — 모자라면 「🏦 은행」 안내 */
  function pay2(o){ if(!can(o)){ toast(lack(o)+" 더 있어야 해요<br><small>"+(gems<(o.g|0)?"💎 는 공부해서 벌어요 · ":"🪙 는 물고기·작물을 팔아요 · ")+"🏦 마을 은행에서 바꿀 수도 있어요</small>", 2600); return false; }
    if(o.g){ gems-=o.g; saveBag(); } if(o.c) setCoin(coin-o.c); return true; }
  /* HUD 🪙 칸 */
  function hud(){ try{ const a=$("hCoin"); if(a) a.querySelector("b").textContent=fmt(coin); const b=$("ihCoin"); if(b) b.textContent=fmt(coin); }catch(e){} }
  /* 게임(관리 화면·시트)이 읽는 요약 — 게임 Kid.k 와 같은 열쇠 */
  const kk=k=>{ try{ if(WAL.on) return k; const id=String((PAD.kid||{}).id||"_guest").replace(/[^\w-]/g,"").slice(0,24); return k+"@"+id; }catch(e){ return k; } };
  let sumT=0;
  function sum(){ clearTimeout(sumT); sumT=setTimeout(()=>{ try{ const b=bankV(); localStorage.setItem(kk("hyeng_town_sum"), JSON.stringify({coin, bait, bank:Math.floor(b.sv+b.lk), gbank:Math.floor(b.gm), tup:upTxt(), at:Date.now()})); }catch(e){} }, 200); }
  /* 공부 보상 받기 — 게임이 넣어 둔 미끼 (Daily 30 한 판 🪱5 · 달리기 15단계 🪱3) */
  function inbox(){ try{ const K2=kk("hyeng_town_inbox"), o=JSON.parse(localStorage.getItem(K2)||"null"); if(!o) return; localStorage.removeItem(K2);
      const b=o.bait|0; if(b>0){ const before=bait; setBait(bait+b); const got=bait-before; toast(got>0 ? "📚 공부 선물! 🪱 미끼 +"+got+(got<b?"<br><small>미끼는 "+BAIT_MAX+"개까지 가질 수 있어요</small>":"") : "📚 공부 선물 🪱 — 미끼가 벌써 가득이에요 ("+BAIT_MAX+"개)<br><small>낚시로 미끼를 쓰고 나서 또 공부해요</small>", 2600); } }catch(e){} }

  /* ═════════ 🏦 마을 은행 — 환전 ═════════ */
  const rate=h=>{ try{ return Math.max(7, Math.min(14, Math.round(K*mkt("💎rate", h)))); }catch(e){ return K; } };   /* 💎1 = 🪙 몇 개 (시간마다) */
  const SELL_MAX=6;   /* (v563 QA) 사는 값(최저 🪙7)보다 늘 낮게 — 싸게 사서 비싸게 되팔기 막기 */
  const sellRate=h=>Math.max(1, Math.min(SELL_MAX, Math.floor(rate(h)*SPREAD)));
  /* 오늘 공부로 번 💎 — 지갑 기록(🏝 마을 · 관리자 · 구매 빼고) */
  function studyToday(){ try{ if(!WAL.on) return 0; const a=JSON.parse(localStorage.getItem(WAL.K)||"{}"), d=day(); let n=0;
      (a.log||[]).forEach(l=>{ if(!(l[1]>0)) return; const w=String(l[2]||""); if(/^🏝|관리자|구매|은행/.test(w)) return; if(new Date(l[0]+9*3600e3).toISOString().slice(0,10)===d) n+=l[1]; }); return n; }catch(e){ return 0; } }
  const LIM_MAX=40;
  const limit=()=>Math.min(LIM_MAX, 10+Math.floor(studyToday()/2));
  function ex(){ let o=store("hyeng_proto_exch")||{}; if(o.d!==day()) o={d:day(), n:0}; return o; }
  const left=()=>Math.max(0, limit()-ex().n);
  const noSrv=()=>{ const e=String((TWN8||{}).err||""), au=/^(401|403)$/.test(e); toast(au ? "🔐 마을 서버가 은행 기록을 막고 있어요<br><small>선생님께 「서버 규칙(hy/day)」을 알려 주세요 · 오류 "+e+"</small>" : "📡 마을 서버에 연결이 안 돼요<br><small>인터넷을 확인하고 잠깐 뒤 다시 눌러요"+(e?" · 오류 "+e:"")+"</small>", 3000); };
  /* (v586) 사용자: 「은행에서 바꾸려는데 왜 안 돼?」 — 서버 시계가 아직이면 그 자리에서 다시 맞춰 보고 되면 바로 이어서 (예전: 10분마다만 다시 → 그동안 막힘) */
  function needSrv(fn){ if(srvOK()) return fn(); toast("📡 마을 서버 시계 맞추는 중…", 1200); let p=null; try{ p=twClock(); }catch(e){} Promise.resolve(p).then(ok=>{ if(ok || srvOK()){ fn(); try{ if($("teBank") && $("teBank").classList.contains("on")) openBank(); }catch(_){} } else noSrv(); }); return 0; }
  function buyGem(n){ if(!srvOK()) return needSrv(()=>buyGem(n)); n=Math.min(n|0, left()); if(n<=0){ toast("🏦 오늘은 더 못 바꿔요<br><small>📚 공부하면 한도가 늘어나요 (최대 💎"+LIM_MAX+")</small>", 2400); return 0; } const c=n*rate(); if(coin<c){ toast("🪙 "+(c-coin)+" 더 있어야 해요", 1800); return 0; }
    setCoin(coin-c); gems+=n; saveBag(); const o=ex(); o.n+=n; store("hyeng_proto_exch", o); tEvS("bank"); try{ SND.big(); }catch(e){} toast("🏦 🪙 "+fmt(c)+" → <b>💎 "+n+"</b>", 1800); return n; }
  function sellGem(n){ n=n|0; if(n<=0 || gems<n){ toast("💎 가 모자라요", 1500); return 0; } const c=n*sellRate(); gems-=n; saveBag(); addCoin(c); tEvS("bank"); try{ SND.pop(); }catch(e){} toast("🏦 💎 "+n+" → <b>🪙 "+fmt(c)+"</b><br><small>되팔면 싸게 쳐 줘요</small>", 2000); return c; }

  /* ═════════ 🏦 적금 (한 달마다 복리 · 서버 시각) ═════════ */
  const PRODUCT={sv:{nm:"🐷 자유 저금", r:0.02, t:"언제든 넣고 빼요"}, lk:{nm:"📅 한 달 적금", r:0.05, t:"한 달 묶여요 · 한 달 지나면 5% · 중간에 빼면 이자 없음"}, gm:{nm:"💎 보석 적금", r:0.01, t:"한 달 묶여요 · 💎200 까지"}};
  const GM_MAX=200;
  let BK=store("hyeng_proto_bank"); if(!BK || typeof BK!=="object") BK={sv:0, st:0, lk:[], gm:[]}; BK.lk=BK.lk||[]; BK.gm=BK.gm||[]; if(BK.svm==null) BK.svm=BK.sv|0;
  const bsave=()=>{ store("hyeng_proto_bank", BK); sum(); };
  const months=t0=>Math.max(0, Math.floor((T()-t0)/MON));
  /* 자유 저금: 한 달 지날 때마다 이자를 원금에 붙임 (서버 시각을 알 때만) */
  /* (v563 QA) 첫 달 이자 = 한 달 내내 들어 있던 돈(svm, 이번 달 가장 적었던 잔액)에만 — 이자 직전에 넣기 막기 */
  function settle(){ if(!srvOK()) return; if(BK.sv>0 && BK.st){ const m=months(BK.st); if(m>0){ const r=PRODUCT.sv.r, i1=Math.floor(Math.min(BK.svm|0, BK.sv)*r); BK.sv=Math.floor((BK.sv+i1)*Math.pow(1+r, m-1)); BK.svm=BK.sv; BK.st+=m*MON; bsave(); } } }
  /* (v563 QA) 📅 한 달 적금 = 한 달 지나면 5% 한 번 (계속 두면 1년에 1.8배 되던 것) · 💎 = 반올림(💎50 → 51) */
  const val=(x, r)=>{ const m=months(x.t); if(m<1) return x.a; return r===PRODUCT.lk.r ? Math.floor(x.a*(1+r)) : Math.round(x.a*Math.pow(1+r, m)); };
  function bankV(){ const lk=BK.lk.reduce((s,x)=>s+val(x,PRODUCT.lk.r),0), gm=BK.gm.reduce((s,x)=>s+val(x,PRODUCT.gm.r),0); return {sv:BK.sv|0, lk, gm}; }
  const nextIn=t0=>{ const ms=MON-((T()-t0)%MON); return Math.max(1, Math.ceil(ms/864e5)); };
  function deposit(k, n){ n=n|0; if(n<=0) return false; if(!srvOK()){ needSrv(()=>deposit(k, n)); return false; } settle();
    if(k==="gm"){ const cur=BK.gm.reduce((s,x)=>s+x.a,0); if(cur+n>GM_MAX){ toast("💎 보석 적금은 💎"+GM_MAX+" 까지예요", 1800); return false; } if(gems<n){ toast("💎 가 모자라요",1500); return false; } gems-=n; saveBag(); BK.gm.push({a:n, t:T()}); }
    else { if(coin<n){ toast("🪙 가 모자라요",1500); return false; } setCoin(coin-n); if(k==="sv"){ if(!BK.sv){ BK.st=T(); BK.svm=n; } BK.sv+=n; } else BK.lk.push({a:n, t:T()}); }
    bsave(); tEvS("bank"); try{ SND.pop(); }catch(e){} toast("🏦 "+PRODUCT[k].nm+" <b>"+(k==="gm"?"💎 ":"🪙 ")+fmt(n)+"</b> 넣었어요", 1800); return true; }
  function withdraw(k, i){ if(k!=="sv" && !srvOK()) return needSrv(()=>withdraw(k, i)); settle();
    if(k==="sv"){ const n=BK.sv|0; if(!n) return 0; BK.sv=0; BK.st=0; BK.svm=0; bsave(); addCoin(n); toast("🐷 🪙 "+fmt(n)+" 찾았어요", 1600); return n; }
    const L=BK[k], x=L[i]; if(!x) return 0; const m=months(x.t), early=m<1, n=early ? x.a : val(x, PRODUCT[k].r); L.splice(i,1); bsave();
    if(k==="gm"){ gems+=n; saveBag(); } else addCoin(n);
    toast((early?"⏳ 한 달이 안 돼서 이자 없이 ":"🎉 이자까지 ")+(k==="gm"?"💎 ":"🪙 ")+fmt(n)+" 찾았어요", 2000); return n; }

  /* ═════════ 🛠 강화 — 효과는 작게(단계마다 조금) · 값은 크게(×2.5) ═════════ */
  const UPS={rod:{ic:"🎣", nm:"낚싯대", eff:["보통","큰 물고기 조금 더","큰 물고기 더","큰 물고기 많이","전설 낚싯대"]},
             bag:{ic:"🎒", nm:"가방", eff:["보통","가방 +5칸","가방 +10칸","가방 +15칸","가방 +20칸"]},
             farm:{ic:"🌱", nm:"밭 도구", eff:["보통","가끔 하나 더 (15%)","가끔 하나 더 (30%)","가끔 하나 더 (45%)","가끔 하나 더 (60%)"]}};
  const UP_COST=[300, 750, 1900, 4700], UP_MAX=4;
  let UP=store("hyeng_proto_tup"); if(!UP || typeof UP!=="object") UP={rod:0, bag:0, farm:0};
  const lv=k=>Math.min(UP_MAX, UP[k]|0);
  const upTxt=()=>Object.keys(UPS).map(k=>UPS[k].nm+lv(k)).join(" ");
  function upgrade(k){ const L=lv(k); if(L>=UP_MAX){ toast(UPS[k].ic+" 최고 단계예요!", 1500); return false; } const c=UP_COST[L]; if(coin<c){ toast("🪙 "+fmt(c-coin)+" 더 있어야 해요", 1800); return false; }
    setCoin(coin-c); UP[k]=L+1; store("hyeng_proto_tup", UP); if(k==="bag"){ try{ bagCap+=5; store("hyeng_proto_cap", bagCap); updBagBtn(); }catch(e){} } sum(); tEvS("upgrade"); try{ SND.big(); emote(hero,"✨"); }catch(e){}
    toast(UPS[k].ic+" <b>"+UPS[k].nm+" "+(L+1)+"단계</b>!<br><small>"+UPS[k].eff[L+1]+"</small>", 2200); return true; }
  /* 낚싯대: 크기 뽑기 지수를 조금 낮춤 (1.7 → 1.25) · 밭 도구: 수확 하나 더 */
  const rodPow=()=>1.7-0.11*lv("rod");
  const farmBonus=()=>Math.random()<0.15*lv("farm") ? 1 : 0;

  /* ═════════ 📉 마을 시세 — 이번 시간 마을에서 많이 팔린 것은 내려감 ═════════
     /hy/isle/mkt/<시간>/<내 코드> = {물건: 판 수} · 다른 아이 것을 합쳐서 · 하나 팔릴 때마다 -4% (최저 ×0.6) */
  let MK={h:-1, at:0, all:{}}, mine=store("hyeng_proto_mkt")||{h:-1, n:{}};
  function mkLoad(force){ const h=hourIx(); if(!force && MK.h===h && Date.now()-MK.at<60e3) return Promise.resolve(MK);
    return NET.get("/hy/isle/mkt/"+h).then(v=>{ const all={}; Object.entries(v||{}).forEach(([c,o])=>{ if(c===myC() || !o || typeof o!=="object") return; Object.entries(o).forEach(([en,n])=>{ all[en]=(all[en]|0)+(n|0); }); }); MK={h, at:Date.now(), all}; return MK; }).catch(()=>MK); }
  function mkF(en, extra){ const h=hourIx(); if(MK.h!==h || Date.now()-MK.at>60e3) mkLoad();   /* (v563 QA) 다른 친구가 판 것 1분마다 다시 */
    const o=(MK.h===h ? MK.all[en]|0 : 0)+(mine.h===h ? mine.n[en]|0 : 0)+(extra|0); return Math.max(0.6, 1-0.03*o); }
  let mkT=0;
  function sold(en, k){ const h=hourIx(); if(mine.h!==h) mine={h, n:{}}; mine.n[en]=(mine.n[en]|0)+(k==null?1:k); store("hyeng_proto_mkt", mine);
    clearTimeout(mkT); mkT=setTimeout(()=>{ try{ NET.put("/hy/isle/mkt/"+mine.h+"/"+myC(), mine.n).catch(()=>{}); }catch(e){} }, 400); }   /* 모두 팔기 = 서버엔 한 번 */

  /* ═════════ 🎫 이용료 ═════════ */
  const FEE={train:10, warp:5, contest:20};
  /* 기차: 안내 방송을 맞히면 다음 표 반값 */
  function trainFee(){ const half=store("hyeng_proto_thalf")===1; return half ? Math.ceil(FEE.train/2) : FEE.train; }
  function payTrain(){ const c=trainFee(); if(coin<c){ toast("🎫 기차표 🪙 "+c+" — 코인이 모자라요<br><small>걸어가면 무료예요 · 🐟 팔아서 코인을 모아요</small>", 2400); return false; } setCoin(coin-c); store("hyeng_proto_thalf", 0); return true; }
  const trainRight=()=>store("hyeng_proto_thalf", 1);

  /* ═════════ 🌙 이달의 한정 가구 (그달에만 · 💎+🪙 ×1.3) ═════════ */
  const LIMITED={1:["snowman","kotatsu","snowglobe"], 2:["kotatsu","heartlamp","snowglobe"], 3:["cherrytree","heartlamp","giftpile"], 4:["cherrytree","giftpile","heartlamp"], 5:["cherrytree","kotatsu","heartlamp"],
    6:["parasol2","seashell","icecart"], 7:["parasol2","seashell","icecart"], 8:["icecart","parasol2","seashell"], 9:["mapletree","pumpkinlamp","kotatsu"], 10:["pumpkinlamp","mapletree","giftpile"],
    11:["mapletree","pumpkinlamp","kotatsu"], 12:["xmastree","snowman","giftpile","snowglobe"]};
  const kmon=()=>new Date(T()+9*3600e3).getUTCMonth()+1;
  const limNow=()=>LIMITED[kmon()]||[];
  const LIM_ALL=[...new Set(Object.values(LIMITED).flat())];
  const isLim=id=>LIM_ALL.indexOf(id)>=0;

  /* ═════════ 🏗 다 같이 마을 공사 — 🚧 빈 자리 3곳 ═════════ */
  const BUILD={free1:{ic:"🏊", nm:"수영장", goal:6000}, free2:{ic:"🎡", nm:"관람차", goal:9000}, free3:{ic:"🏰", nm:"성 놀이터", goal:12000}};
  let BD={at:0, v:{}};
  function bdLoad(force){ if(!force && Date.now()-BD.at<30e3) return Promise.resolve(BD); return NET.get("/hy/isle/build").then(v=>{ BD={at:Date.now(), v:v||{}}; return BD; }).catch(()=>BD); }
  const bdTot=k=>Object.values((BD.v||{})[k]||{}).reduce((s,o)=>s+((o&&o.v)|0),0);
  const bdTop=k=>Object.values((BD.v||{})[k]||{}).filter(o=>o&&o.n).sort((a,b)=>(b.v|0)-(a.v|0)).slice(0,5);
  const done=k=>bdTot(k)>=BUILD[k].goal;
  function donate(k, n){ n=n|0; if(n<=0 || coin<n){ toast("🪙 가 모자라요", 1500); return Promise.resolve(false); } setCoin(coin-n);
    const me=((BD.v||{})[k]||{})[myC()]||{v:0}; const v=(me.v|0)+n, rec={n:nick(), v, at:Date.now()};   /* (v563 QA) 서버에 들어간 뒤에만 내 합계를 올림 */
    return NET.put("/hy/isle/build/"+k+"/"+myC(), rec).then(()=>{ BD.v[k]=BD.v[k]||{}; BD.v[k][myC()]=rec; toast(BUILD[k].ic+" "+BUILD[k].nm+" 공사에 🪙 "+fmt(n)+" 보탰어요! 🏗<br><small>간판에 내 이름이 남아요</small>", 2400); tEvS("build"); try{ SND.big(); }catch(e){} rebuildSites(); return true; })
      .catch(()=>{ toast("📡 서버에 못 보냈어요 — 다시 해 봐요", 1800); setCoin(coin+n); return false; }); }
  let C=null, SITES={};
  function build(ctx){ C=ctx; SITES={}; bdLoad(true).then(()=>rebuildSites()); }
  function rebuildSites(){ if(!C) return; Object.keys(BUILD).forEach(k=>{ try{ site(k); }catch(e){ console.warn("TECO site", k, e); } }); try{ dirty=true; }catch(e){} }
  function zoneC(k){ const Z=(C.MAP.zones||[]).find(z=>z.k===k); if(!Z) return null; let x=0,z=0; Z.poly.forEach(q=>{ x+=q[0]; z+=q[1]; }); return [x/Z.poly.length, z/Z.poly.length]; }
  function site(k){ const c=zoneC(k); if(!c) return; const old=SITES[k]; if(old && old.g){ C.G.remove(old.g); }
    const B=BUILD[k], ok=done(k), g=new THREE.Group(); g.position.set(c[0]+C.OX, 0, c[1]+C.OZ); g.userData.solo=1; C.G.add(g);
    const box=(w,h,d,col,x,y,z)=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d), C.MC(col)); m.position.set(x,y+h/2,z); m.castShadow=true; m.receiveShadow=true; g.add(m); return m; };
    if(!ok){ /* (v576) 점검: 공사장 3곳이 똑같음(울타리+목재+기둥) · 기둥이 글씨를 뚫음 · 「공사 0%」 겹침 → 곳마다 다른 공사 모습 + 울타리(주황·흰 판) + 진행 게이지판 (한 덩어리로 합쳐 그리기 1번) */
      const L=[], GS=new Set(), put=(geo,col,x,y,z,o)=>{ o=o||{}; GS.add(geo); L.push({g:geo, col, m:new THREE.Matrix4().compose(new THREE.Vector3(x,y,z), new THREE.Quaternion().setFromEuler(new THREE.Euler(o.rx||0,o.ry||0,o.rz||0,"YXZ")), new THREE.Vector3(o.sx||1,o.sy||1,o.sz||1))}); };
      const BX=new THREE.BoxGeometry(1,1,1), CY=new THREE.CylinderGeometry(1,1,1,8), CO=new THREE.ConeGeometry(1,1,10), RK=new THREE.DodecahedronGeometry(1,0), HS=new THREE.SphereGeometry(1,10,6,0,Math.PI*2,0,Math.PI/2);
      const bx=(w,h,d,col,x,y,z,o)=>put(BX,col,x,y+h/2,z,Object.assign({sx:w,sy:h,sz:d},o||{}));
      const UP=new THREE.Vector3(0,1,0), rod=(col,a,b,r)=>{ const A=new THREE.Vector3(...a), B2=new THREE.Vector3(...b), d=B2.clone().sub(A), e=new THREE.Euler().setFromQuaternion(new THREE.Quaternion().setFromUnitVectors(UP,d.clone().normalize()),"YXZ"); put(CY,col,(A.x+B2.x)/2,(A.y+B2.y)/2,(A.z+B2.z)/2,{rx:e.x,ry:e.y,rz:e.z,sx:r,sz:r,sy:d.length()}); };
      /* 울타리 — 네모 ±3.25 · 기둥 · 주황/흰 판 · 아래 줄 (막기는 isle.js 가 cols 로) */
      const R=3.25, n=5; for(let s=0;s<4;s++) for(let i=0;i<n;i++){ const t0=-R+i*(2*R/n), t1=t0+2*R/n, tm=(t0+t1)/2, side=[[0,-1],[1,0],[0,1],[-1,0]][s], P=t=>side[0] ? [side[0]*R, t] : [t, side[1]*R];
        const [px,pz]=P(t0), [mx,mz]=P(tm), alongX=!side[0]; put(CY,0xfffdf7,px,.45,pz,{sx:.06,sz:.06,sy:.9}); put(CO,0xff8a3d,px,.95,pz,{sx:.08,sz:.08,sy:.14});
        bx(alongX?2*R/n-.06:.05,.3,alongX?.05:2*R/n-.06,i%2?0xfffdf7:0xff8a3d,mx,.42,mz); bx(alongX?2*R/n:.04,.05,alongX?.04:2*R/n,0xfff1c4,mx,.16,mz); }
      /* 곳마다 다른 공사 */
      if(k==="free1"){ /* 🏊 수영장 — 판 구덩이 · 흙 둔덕 · 파란 덮개 · 타일 더미 · 꼬깔 · 삽 */
        bx(4.4,.03,3.0,0x7a5236,0,.0,0); bx(3.8,.03,2.4,0x5a3d28,0,.02,0); bx(3.0,.03,1.6,0x4a3020,0,.035,0);
        [[-1.9,-1.9,.8],[1.7,-2.0,.65],[2.2,1.9,.55]].forEach(([x,z,r])=>put(HS,0xa3714a,x,0,z,{sx:r*1.3,sy:r*.7,sz:r}));
        bx(1.9,.05,1.5,0x2f7fe0,-.9,.05,.6,{ry:.25, rz:.06}); [[-1.8,.0],[0,1.3],[-1.6,1.3],[0,-.1]].forEach(([x,z])=>put(RK,0x9a9aa6,x-.05,.12,z+.05,{sx:.1,sy:.08,sz:.1}));
        for(let i=0;i<4;i++) bx(.7,.12,.5,i%2?0x9fe0ff:0x6fc6f0,2.2,i*.12,-.4,{ry:i*.15});
        [[1.2,2.4],[-2.4,.9],[2.5,-2.4]].forEach(([x,z])=>{ put(CO,0xff8a3d,x,.25,z,{sx:.17,sz:.17,sy:.5}); put(CY,0xffffff,x,.24,z,{sx:.115,sz:.115,sy:.07}); bx(.36,.04,.36,0xff8a3d,x,0,z); });
        rod(0x8a5a34,[1.55,.35,-1.85],[1.85,1.25,-2.0],.035); bx(.22,.28,.04,0x9a9aa6,1.52,.15,-1.84,{ry:.4, rz:.3}); }
      else if(k==="free2"){ /* 🎡 관람차 — 둥근 받침(콘크리트) · 노란 크레인 · 매달린 바퀴 조각 · 쇠 기둥 더미 */
        put(new THREE.TorusGeometry(2.0,.2,6,28),0xbdbdc6,0,.1,0,{rx:Math.PI/2}); bx(1.4,.3,1.4,0xa9a9b4,0,0,0); bx(.5,1.2,.5,0x8a8a9a,-.6,.3,0); bx(.5,1.2,.5,0x8a8a9a,.6,.3,0);
        const mx=-2.1, mz=-2.1, H=5.4; bx(1.0,.3,1.0,0x8a8a9a,mx,0,mz); bx(.42,H,.42,0xffc21a,mx,.3,mz); for(let y=.9;y<H;y+=.9){ bx(.44,.06,.44,0x3b2433,mx,y,mz); rod(0xe0a800,[mx-.2,y,mz+.22],[mx+.2,y+.85,mz+.22],.02); }
        bx(.6,.5,.55,0xffc21a,mx,H+.3,mz); bx(.4,.25,.05,0x9fd8ff,mx+.1,H+.48,mz+.28); bx(4.6,.22,.28,0xffc21a,mx+2.3,H+.85,mz,{}); bx(1.4,.22,.28,0xffc21a,mx-.8,H+.85,mz); bx(.55,.5,.45,0x8a8a9a,mx-1.25,H+.4,mz);
        rod(0x3b2433,[mx,H+1.6,mz],[mx+3.8,H+.95,mz],.02); rod(0x3b2433,[mx,H+1.6,mz],[mx-1.2,H+.95,mz],.02); bx(.08,.7,.08,0xffc21a,mx,H+.9,mz);
        rod(0x3b2433,[mx+3.6,H+.85,mz],[mx+3.6,2.6,mz],.015); put(CO,0x3b2433,mx+3.6,2.5,mz,{sx:.1,sz:.1,sy:.2,rx:Math.PI});
        put(new THREE.TorusGeometry(.9,.09,6,12,Math.PI*.6),0xff6b9a,mx+3.6,1.55,mz,{rz:Math.PI*.2}); bx(.45,.42,.45,0x5aa7ff,mx+3.0,1.0,mz);
        for(let i=0;i<4;i++) bx(2.4,.16,.16,0xff6b9a,1.5,i<3?0:.16,1.9+(i%3)*.2-(i===3?.1:0)); }
      else { /* 🏰 성 놀이터 — 반쯤 쌓은 돌 벽(ㄱ자) · 비계(쇠 기둥 + 나무 판) · 돌 더미 · 깃발 */
        const ST=[0xd9d2c5,0xcfc6b6,0xe4ddd0]; for(let i=0;i<5;i++) for(let j=0;j<3;j++){ if(j===2 && i%2) continue; bx(.56,.38,.5,ST[(i+j)%3],-1.8+i*.58,j*.4,-1.4); }
        for(let i=1;i<4;i++) for(let j=0;j<(i<3?3:2);j++) bx(.5,.38,.56,ST[(i+j+1)%3],-1.8,j*.4,-1.4+i*.58);
        bx(.9,1.6,.9,0xcfc6b6,-1.8,0,-1.4); bx(1.0,.18,1.0,0x5aa7ff,-1.8,1.6,-1.4);
        [[-2.5,-2.1],[-.9,-2.1],[.7,-2.1],[-2.5,-.7],[-2.5,.7]].forEach(([x,z])=>rod(0x9a9aa6,[x,0,z],[x,2.4,z],.04));
        [1.05,2.05].forEach(y=>{ rod(0x9a9aa6,[-2.5,y,-2.1],[.7,y,-2.1],.03); rod(0x9a9aa6,[-2.5,y,-2.1],[-2.5,y,.7],.03); bx(3.1,.06,.36,0xc48a58,-.9,y,-2.0); bx(.36,.06,2.6,0xc48a58,-2.4,y,-.75); });
        rod(0x9a9aa6,[-2.5,0,-2.1],[-.9,2.4,-2.1],.025); rod(0x9a9aa6,[-.9,0,-2.1],[.7,2.4,-2.1],.025);
        [[1.3,1.1,.42],[1.8,1.5,.36],[1.0,1.7,.32],[1.6,.7,.3],[2.2,1.0,.34],[1.45,1.3,.3]].forEach(([x,z,r],i)=>put(RK,ST[i%3],x,r*.7+(i===5?.45:0),z,{sx:r,sy:r*.8,sz:r,ry:i}));
        for(let i=0;i<3;i++) bx(.5,.36,.46,ST[i%3],2.3-i*.55,0,-.6+i*.1,{ry:i*.2}); rod(0x8a5a34,[-1.8,1.78,-1.4],[-1.8,3.1,-1.4],.03); put(new THREE.ConeGeometry(.3,.5,3),0xff6b6b,-1.62,2.9,-1.4,{rz:-Math.PI/2, sz:.15}); }
      const mm=C.vcMerge(L); g.add(mm); GS.forEach(x=>x.dispose());
      /* 진행 게이지판 — 섬 가운데 쪽 울타리에 (밖을 봄) */
      const dx=-c[0], dz=-c[1], ax=Math.abs(dx)>Math.abs(dz), nx=ax?Math.sign(dx):0, nz=ax?0:Math.sign(dz), along=Math.max(-1.6,Math.min(1.6,(ax?dz:dx)/Math.hypot(dx,dz)*3.4)), bpx=ax?nx*(R+.14):along, bpz=ax?along:nz*(R+.14);
      const bd=new THREE.Group(); bd.position.set(bpx,0,bpz); bd.rotation.y=Math.atan2(nx,nz); g.add(bd);
      const pm=C.MC(0x8a5a34); [-.9,.9].forEach(u=>{ const p=new THREE.Mesh(new THREE.CylinderGeometry(.06,.07,1.75,8), pm); p.position.set(u,.88,-.03); p.castShadow=true; bd.add(p); });
      const back=new THREE.Mesh(new THREE.BoxGeometry(2.0,1.08,.07), C.MC(0xc9925c)); back.position.set(0,1.2,0); back.castShadow=true; bd.add(back);
      const cv=document.createElement("canvas"); cv.width=512; cv.height=272; const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; boardDraw(cv, k); const face=new THREE.Mesh(new THREE.PlaneGeometry(1.9,1.0), new THREE.MeshBasicMaterial({map:tx})); face.position.set(0,1.2,.04); bd.add(face);
      g.userData.board=bd; g.userData.lp=[c[0]+bpx+C.OX, 2.35, c[1]+bpz+C.OZ];
    } else if(k==="free1"){ /* 🏊 수영장 */
      box(7,.3,5,0xe8dcc2,0,0,0); const w=box(6,.12,4,0x4fc3f7,0,.3,0); w.material.transparent=true; w.material.opacity=.85; box(.4,1.2,.15,0xffffff,2.6,.3,-2); box(1,.1,2,0xff6b6b,-4.2,0,1); box(1,.1,2,0xffd23f,-4.2,0,-1.4);
    } else if(k==="free2"){ /* 🎡 관람차 (돎) */
      box(.4,4,.4,0x8a8a9a,-1.2,0,0); box(.4,4,.4,0x8a8a9a,1.2,0,0); const W=new THREE.Group(); W.position.set(0,4.4,0); g.add(W);
      const ring=new THREE.Mesh(new THREE.TorusGeometry(2.6,.12,8,32), C.MC(0xff6b9a)); W.add(ring);
      for(let i=0;i<8;i++){ const a=i/8*Math.PI*2, cab=new THREE.Mesh(new THREE.BoxGeometry(.6,.55,.6), C.MC([0x5aa7ff,0xffd23f,0x7ed957,0xff9a3d][i%4])); cab.position.set(Math.cos(a)*2.6, Math.sin(a)*2.6, 0); W.add(cab); }
      g.userData.wheel=W;
    } else { /* 🏰 성 놀이터 */
      box(4,2.2,3,0xd9d2c5,0,0,0); [[-2,-1.5],[2,-1.5],[-2,1.5],[2,1.5]].forEach(([x,z])=>{ box(.9,3,.9,0xcfc6b6,x,0,z); box(1,.4,1,0x5aa7ff,x,3,z); }); box(1.2,.1,2.5,0xff6b6b,0,1.1,2.6);
    }
    try{ TOON.scan(g); }catch(e){}   /* (v563 QA) 서버에서 늦게 받아 다시 지으니 툰 재질도 다시 */
    SITES[k]={g, c, ok}; }
  /* (v576) 🏗 공사 게이지판 그림 — 이름 · 진행 막대 · 모은 🪙 */
  function boardDraw(cv, k){ const g=cv.getContext("2d"), B=BUILD[k], tot=bdTot(k), pct=Math.min(1, tot/B.goal), W=cv.width, H=cv.height;
    g.fillStyle="#fffdf7"; g.fillRect(0,0,W,H); g.strokeStyle="#3b2433"; g.lineWidth=10; g.strokeRect(5,5,W-10,H-10);
    g.fillStyle="#ffd23f"; g.fillRect(10,10,W-20,62); for(let x=-40;x<W;x+=44){ g.fillStyle="#3b2433"; g.beginPath(); g.moveTo(x,72); g.lineTo(x+22,72); g.lineTo(x+44,10); g.lineTo(x+22,10); g.closePath(); g.fill(); }
    g.fillStyle="#fffdf7"; g.fillRect(70,16,W-140,50); g.fillStyle="#3b2433"; g.font="bold 38px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText("🏗 "+B.ic+" "+B.nm+" 공사", W/2, 42);
    const bx=40, by=104, bw=W-80, bh=58; g.fillStyle="#efe6d6"; g.fillRect(bx,by,bw,bh); g.fillStyle="#7ed957"; g.fillRect(bx,by,bw*pct,bh); g.fillStyle="rgba(255,255,255,.35)"; for(let x=bx; x<bx+bw*pct; x+=28) g.fillRect(x,by,12,bh);
    g.strokeStyle="#3b2433"; g.lineWidth=6; g.strokeRect(bx,by,bw,bh); g.fillStyle="#3b2433"; g.font="bold 40px sans-serif"; g.fillText(Math.floor(pct*100)+"%", W/2, by+bh/2+2);
    g.font="bold 30px sans-serif"; g.fillStyle="#8a5a00"; g.fillText("🪙 "+fmt(Math.min(tot,B.goal))+" / "+fmt(B.goal), W/2, 200); g.font="24px sans-serif"; g.fillStyle="#6b5a4e"; g.fillText("다 같이 🪙 를 모으면 생겨요!", W/2, 240); }
  function tick(dt){ let a=false; Object.values(SITES).forEach(S=>{ if(S.g.userData.wheel){ S.g.userData.wheel.rotation.z+=dt*.25; a=true; } }); return a; }
  function labels(L){ if(!C) return; Object.keys(BUILD).forEach(k=>{ const S=SITES[k]; if(!S) return; const B=BUILD[k], ok=S.ok;
      L.push({k:"b_"+k, ic:ok?B.ic:"🏗", t:ok?B.nm:(B.nm+" 공사 "+Math.min(99,Math.floor(bdTot(k)/B.goal*100))+"%"), p:S.g.userData.lp||[S.c[0]+C.OX, 2.4, S.c[1]+C.OZ], r:4.5, act:()=>openBuild(k)}); }); }

  /* ═════════ 화면 ═════════ */
  function css(){ if($("teCss")) return; const s=document.createElement("style"); s.id="teCss"; s.textContent=`
.teG{color:#2f6fd6;font-weight:800}.teC{color:#b07800;font-weight:800}.teP{font-style:normal;margin:0 3px;color:#9a7e63}
.teTabs{display:flex;gap:6px;margin:2px 0 10px}.teTabs button{flex:1;height:40px;border-radius:14px;border:3px solid #3b2433;background:#fffdf7;font:16px var(--kr);color:#3b2433}.teTabs button.on{background:#3b2433;color:#fff}
.teBal{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}.teBal div{border:3px solid #3b2433;border-radius:16px;background:#fff;padding:6px 10px;box-shadow:0 3px 0 #3b2433}.teBal small{display:block;font-size:12px;color:#8a6a4a}.teBal b{font:800 22px var(--en)}
.teRate{display:flex;align-items:center;justify-content:space-between;gap:8px;border:3px solid #e2b74a;background:#fff3cf;border-radius:16px;padding:8px 10px;margin-bottom:8px}
.teRate b{font:800 20px var(--en)}.teRate .up{color:#d33a3a}.teRate .dn{color:#2f6fd6}.teRate svg{flex:none}
.teLim{border:2px dashed #d8c4a0;border-radius:14px;padding:8px 10px;margin-bottom:8px;font-size:13px;color:#6b5a4e}.teBar{height:12px;border-radius:7px;background:#f2e2b8;overflow:hidden;margin:6px 0}.teBar i{display:block;height:100%;background:#7ed957}
.teBtns{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:8px}.teBtns button{height:58px;border-radius:16px;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font:800 15px var(--en);color:#3b2433;line-height:1.15}.teBtns button small{display:block;font:12px var(--kr);color:#8a6a4a}.teBtns button.go{background:#7ed957}.teBtns button:disabled,.teBtns button.poor{opacity:.45}.teRow button.poor{opacity:.5}.teRow button{white-space:nowrap}
.teH{font-size:14px;color:#8a6a4a;margin:10px 2px 6px}
.teRow{display:flex;align-items:center;gap:8px;border:3px solid #3b2433;border-radius:16px;background:#fffdf7;padding:8px 10px;margin-bottom:6px;box-shadow:0 3px 0 #3b2433}.teRow i{font-style:normal;font-size:26px}.teRow b{display:block;font-size:15px}.teRow small{display:block;font-size:12px;color:#8a6a4a}.teRow .r{margin-left:auto;display:flex;gap:6px}
.teRow button{height:38px;padding:0 10px;border-radius:12px;border:2.5px solid #3b2433;background:#fff;font:14px var(--kr);color:#3b2433}.teRow button.go{background:#7ed957}
.teNote{font-size:12.5px;color:#8a6a4a;line-height:1.5;margin:6px 2px}
.teLv{display:flex;gap:3px;margin-top:2px}.teLv u{width:14px;height:6px;border-radius:3px;background:#e6d6bb}.teLv u.on{background:#ffb02e}
.teBig{font:800 26px var(--en)}`; document.head.appendChild(s); }
  function sheet(id){ css(); let d=$(id); if(d) return d; d=document.createElement("div"); d.id=id; d.className="hlP"; d.innerHTML='<div class="lb"></div>'; document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.closest(".x")) d.classList.remove("on"); }); ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); try{ SHEETS.push(id); }catch(e){} return d; }
  const hd=(t,s)=>'<h3>'+t+'<small>'+(s||"")+'</small><button class="x" aria-label="닫기">✕</button></h3>';
  /* 지난 12시간 환율 그림 (주식창) */
  function spark(){ const h=hourIx(), P=[]; for(let i=11;i>=0;i--) P.push(rate(h-i)); const W=96, H=34, lo=7, hi=14, x=i=>i*(W/11), y=v=>H-3-(v-lo)/(hi-lo)*(H-6);
    return '<svg width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'" aria-label="지난 12시간 환율"><polyline fill="none" stroke="#b07800" stroke-width="2" points="'+P.map((v,i)=>x(i).toFixed(1)+","+y(v).toFixed(1)).join(" ")+'"/><circle cx="'+x(11)+'" cy="'+y(P[11])+'" r="3" fill="#d33a3a"/></svg>'; }
  let bankTab="ex";
  function openBank(tab){ if(tab) bankTab=tab; if(!srvOK()){ try{ twClock(); }catch(e){} } settle(); const d=sheet("teBank"), r=rate(), pr=rate(hourIx()-1), lim=limit(), used=ex().n, lf=Math.max(0,lim-used), st=studyToday();
    const top='<div class="teBal"><div><small>내 코인</small><b class="teC">🪙 '+fmt(coin)+'</b></div><div><small>내 보석</small><b class="teG">💎 '+fmt(gems)+'</b></div></div>'
      +'<div class="teTabs"><button data-tb="ex" class="'+(bankTab==="ex"?"on":"")+'">💱 환전</button><button data-tb="sv" class="'+(bankTab==="sv"?"on":"")+'">🐷 저금·적금</button></div>';
    let body="";
    if(bankTab==="ex"){ const nB=Math.min(lf, Math.floor(coin/r));
      body='<div class="teRate"><div><small>지금 환율</small><br><b>💎1 = 🪙'+r+'</b> <span class="'+(r>pr?"up":r<pr?"dn":"")+'">'+(r>pr?"▲":r<pr?"▼":"–")+'</span><br><small>되팔 때 💎1 → 🪙'+sellRate()+'</small></div>'+spark()+'</div>'
        +'<div class="teLim">오늘 🪙 → 💎 로 바꿀 수 있는 <b>💎 '+lf+'</b> / '+lim+'<div class="teBar"><i style="width:'+Math.round(used/Math.max(1,lim)*100)+'%"></i></div>기본 💎10 + 오늘 공부로 번 💎'+st+' 의 ½ (최대 💎'+LIM_MAX+') · <b>📚 공부하면 더 바꿀 수 있어요</b></div>'
        +'<div class="teH">🪙 → 💎 사기 (환율이 쌀 때 사면 이득!)</div><div class="teBtns">'
        +'<button data-buy="1" class="'+(lf<1||coin<r?"poor":"")+'">💎 1<small>🪙 '+r+'</small></button><button data-buy="5" class="'+(lf<5||coin<r*5?"poor":"")+'">💎 5<small>🪙 '+(r*5)+'</small></button><button class="go'+(nB<1?" poor":"")+'" data-buy="'+Math.max(1,nB)+'">다 바꾸기<small>💎 '+nB+' · 🪙 '+(nB*r)+'</small></button></div>'
        +'<div class="teH">💎 → 🪙 팔기 (한도 없음 · 싸게 쳐 줘요)</div><div class="teBtns"><button data-sell="1" '+(gems<1?"disabled":"")+'>🪙 '+sellRate()+'<small>💎 1</small></button><button data-sell="5" '+(gems<5?"disabled":"")+'>🪙 '+(sellRate()*5)+'<small>💎 5</small></button><button data-sell="10" '+(gems<10?"disabled":"")+'>🪙 '+(sellRate()*10)+'<small>💎 10</small></button></div>'
        +'<div class="teNote">🪙 는 사라지지 않아요 — 오늘 다 못 바꾸면 내일 또 · 환율은 한 시간마다 바뀌어요 (모든 친구 같은 값)</div>';
    } else { const b=bankV();
      body='<div class="teRow"><i>🐷</i><span><b>자유 저금 <span class="teC">🪙 '+fmt(b.sv)+'</span></b><small>한 달마다 2% 이자 (복리 · 한 달 내내 넣어 둔 만큼) · 언제든 넣고 빼요'+(BK.sv?' · 다음 이자까지 '+nextIn(BK.st)+'일':'')+'</small></span><span class="r"><button class="go" data-dep="sv">넣기</button><button data-wd="sv" '+(BK.sv?'':'disabled')+'>찾기</button></span></div>'
        +'<div class="teRow"><i>📅</i><span><b>한 달 적금 · 5%</b><small>넣으면 한 달 묶여요 · 한 달 지나면 <b>5%</b> · 찾아서 다시 넣으면 또 5% · 중간에 찾으면 이자 없음</small></span><span class="r"><button class="go" data-dep="lk">넣기</button></span></div>'
        +BK.lk.map((x,i)=>{ const m=months(x.t); return '<div class="teRow" style="margin-left:24px"><i>📅</i><span><b class="teC">🪙 '+fmt(val(x,PRODUCT.lk.r))+'</b><small>넣은 돈 🪙'+fmt(x.a)+' · '+(m<1?'⏳ '+nextIn(x.t)+'일 뒤 5% 이자':'🎉 이자 받았어요 · 찾아서 다시 넣으면 또 5%')+'</small></span><span class="r"><button data-wd="lk" data-i="'+i+'">찾기</button></span></div>'; }).join("")
        +'<div class="teRow"><i>💎</i><span><b>보석 적금 · 1%</b><small>한 달 묶여요 · 💎'+GM_MAX+' 까지 · 💎100 넣으면 한 달에 💎1</small></span><span class="r"><button class="go" data-dep="gm">넣기</button></span></div>'
        +BK.gm.map((x,i)=>{ const m=months(x.t); return '<div class="teRow" style="margin-left:24px"><i>💎</i><span><b class="teG">💎 '+fmt(val(x,PRODUCT.gm.r))+'</b><small>넣은 💎'+x.a+' · '+(m<1?'⏳ '+nextIn(x.t)+'일 뒤부터 이자':'🎉 '+m+'달째')+'</small></span><span class="r"><button data-wd="gm" data-i="'+i+'">찾기</button></span></div>'; }).join("")
        +'<div class="teNote">이자는 한 달(30일)마다 붙어요 · '+(srvOK()?'시간은 마을 서버 시계로 재요':'📡 서버 시계를 못 받아서 은행이 잠깐 쉬어요 (인터넷 연결 뒤에 다시)')+'</div>';
    }
    d.querySelector(".lb").innerHTML=hd("🏦 마을 은행","환전 · 저금 · 적금")+top+body; d.classList.add("on");
    d.querySelector(".lb").onclick=e=>{ const t=e.target.closest("[data-tb]"); if(t){ openBank(t.dataset.tb); return; }
      const b=e.target.closest("[data-buy]"); if(b){ if(buyGem(+b.dataset.buy)) openBank(); return; }
      const s=e.target.closest("[data-sell]"); if(s && !s.disabled){ ask("💎 "+s.dataset.sell+" 를 🪙 "+(s.dataset.sell*sellRate())+" 로 팔까요?<br><small>되팔면 싸게 쳐 줘요</small>", ()=>{ sellGem(+s.dataset.sell); openBank(); }); return; }
      const dp=e.target.closest("[data-dep]"); if(dp){ askAmt(dp.dataset.dep); return; }
      const w=e.target.closest("[data-wd]"); if(w && !w.disabled){ const k=w.dataset.wd, i=+w.dataset.i||0, early=k!=="sv" && months((BK[k][i]||{}).t||T())<1;
        ask(early ? "⏳ 아직 한 달이 안 됐어요<br>지금 찾으면 <b>이자 없이</b> 넣은 만큼만 돌려받아요. 찾을까요?" : "🏦 찾을까요?", ()=>{ withdraw(k,i); openBank(); }); } }; }
  function askAmt(k){ const isG=k==="gm", have=isG?gems:coin, opts=(isG?[50,100,200]:[50,100,500,1000]).filter(n=>n<=have); if(!opts.length){ toast(isG?"💎 가 모자라요":"🪙 가 모자라요", 1500); return; }
    const d=sheet("teAmt"); d.querySelector(".lb").innerHTML=hd(PRODUCT[k].nm+" 넣기", PRODUCT[k].t)+'<div class="teBtns">'+opts.map(n=>'<button data-n="'+n+'">'+(isG?"💎 ":"🪙 ")+fmt(n)+'</button>').join("")+'</div>'; d.classList.add("on");
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-n]"); if(!b) return; d.classList.remove("on"); deposit(k, +b.dataset.n); openBank("sv"); }; }
  function openUpg(){ const d=sheet("teUpg");
    d.querySelector(".lb").innerHTML=hd("🛠 강화","🪙 로 도구를 키워요 · 단계가 오를수록 비싸요")+'<div class="teBal"><div><small>내 코인</small><b class="teC">🪙 '+fmt(coin)+'</b></div><div><small>내 도구</small><b style="font-size:17px;display:flex;gap:8px">'+Object.keys(UPS).map(k=>'<span>'+UPS[k].ic+'<sup style="font-size:12px">'+lv(k)+'</sup></span>').join("")+'</b></div></div>'
      +Object.keys(UPS).map(k=>{ const L=lv(k), U=UPS[k], c=UP_COST[L]; return '<div class="teRow"><i>'+U.ic+'</i><span><b>'+U.nm+' '+L+'단계</b><span class="teLv">'+[1,2,3,4].map(i=>'<u class="'+(i<=L?'on':'')+'"></u>').join("")+'</span><small>지금: '+U.eff[L]+(L<UP_MAX?' → 다음: '+U.eff[L+1]:'')+'</small></span><span class="r">'+(L<UP_MAX?'<button class="go'+(coin<c?' poor':'')+'" data-up="'+k+'">🪙 '+fmt(c)+'</button>':'<button disabled>최고!</button>')+'</span></div>'; }).join("")
      +'<div class="teNote">강화는 조금씩 더 잘 벌게 해 줘요 — 하지만 🎫 이용료·🌰 씨앗·🪱 미끼(공부)가 필요하니 아껴 써요</div>'; d.classList.add("on");
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-up]"); if(b && !b.disabled){ const k=b.dataset.up; if(coin<UP_COST[lv(k)]){ toast("🪙 "+fmt(UP_COST[lv(k)]-coin)+" 더 있어야 해요<br><small>🐟 물고기·🌾 작물을 팔아 모아요</small>", 2200); return; } ask(UPS[k].ic+" <b>"+UPS[k].nm+" "+(lv(k)+1)+"단계</b>로 올릴까요?<br>🪙 "+fmt(UP_COST[lv(k)]), ()=>{ upgrade(k); openUpg(); }); } }; }
  function openBuild(k){ bdLoad(true).then(()=>{ const B=BUILD[k], tot=bdTot(k), ok=tot>=B.goal, top=bdTop(k), d=sheet("teBld");
      d.querySelector(".lb").innerHTML=hd(B.ic+" "+B.nm+(ok?" — 완성!":" 공사"), ok?"마을 모두가 함께 지었어요":"마을 모두가 🪙 를 모아 지어요")
        +'<div class="teLim"><b class="teBig teC">🪙 '+fmt(Math.min(tot,B.goal))+'</b> / '+fmt(B.goal)+'<div class="teBar"><i style="width:'+Math.min(100,Math.round(tot/B.goal*100))+'%"></i></div>'+(ok?'🎉 다 지었어요! 고마워요':'다 모이면 '+B.ic+' '+B.nm+' 이 생겨요')+'</div>'
        +'<div class="teH">🏅 많이 보탠 친구 (간판에 이름)</div>'+(top.length?top.map((o,i)=>'<div class="teRow"><i>'+["🥇","🥈","🥉","🎖","🎖"][i]+'</i><span><b>'+esc(o.n)+'</b></span><span class="r teC">🪙 '+fmt(o.v)+'</span></div>').join(""):'<div class="teNote">아직 아무도 없어요 — 처음 보태 볼까요?</div>')
        +(ok?'':'<div class="teH">보태기</div><div class="teBtns">'+[50,200,500].map(n=>'<button data-dn="'+n+'" class="'+(coin<n?'poor':'')+'">🪙 '+n+'</button>').join("")+'</div>'); d.classList.add("on");
      d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-dn]"); if(b && !b.disabled){ donate(k, +b.dataset.dn).then(()=>openBuild(k)); } }; }); }
  const tEvS=n=>{ try{ tEv(n); }catch(e){} };
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  /* Mia 「공부 먼저!」 — 오늘 공부를 안 하고 마을에 오면 하루 한 번 (막지는 않음 · 사용자: 에너지 같은 강제는 빼자) */
  function nudge(){ try{ if(store("hyeng_proto_nudge")===day()) return; if(studyToday()>0) return; if(tut.s<TUT.length-1) return; if(!(window.ISLE && place===ISLE.PLC)) return;
      store("hyeng_proto_nudge", day()); toast("🧑‍🌾 <b>Mia</b>: 오늘 📚 <b>Daily 30</b> 한 판 하면<br>🪱 미끼 5개 + 🏦 은행에서 💎 더 바꿀 수 있어요!", 4200); }catch(e){} }
  function init(){ hud(); sum(); inbox(); settle(); mkLoad(); setTimeout(nudge, 5000); setInterval(nudge, 15000); }   /* (v563 QA) 방에서 시작한 아이도 섬에 오면 */
  addEventListener("pageshow", ()=>{ try{ inbox(); }catch(e){} });
  return {K, cost, tierOf, cTxt, cHtml, coins, setCoin, addCoin, can, pay2, lack, hud, sum, inbox, rate, sellRate, limit, left, studyToday, buyGem, sellGem,
    deposit, withdraw, bankV, settle, BK:()=>BK, UPS, UP_COST, lv, upgrade, rodPow, farmBonus, mkLoad, mkF, sold, FEE, trainFee, payTrain, trainRight,
    LIMITED, limNow, isLim, BUILD, bdLoad, bdTot, donate, build, labels, tick, openBank, openUpg, openBuild, init, BAIT_MAX, srvOK, T, MON, kk, big};
})();
setTimeout(()=>{ try{ TECO.init(); }catch(e){ console.warn(e); } }, 300);
window.TECO=TECO;   /* (v563 QA) town-fac 가 window.TECO 로 찾음 — const 는 window 에 안 붙어서 🏗 공사가 안 보였음 */
