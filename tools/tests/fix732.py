"""(v732) ChatGPT 코드 QA 55건 고치기 — 마을 쪽 (사용자: 「한번 싹 다 고치자」)
   #19 펫 이름 고른 뒤 💎 · #20 박물관 서버에 남은 뒤 물건 빼기 · #31 박물관 안내 · #21 사진 찍은 뒤 🪙 · #30 액자 사진 그대로 · #27 친구 집 액자
   #16 간식 가방 칸 · #15 안 읽은 편지 먼저 · #28 답장 하루 한 번 · #33 퀴즈 타이머 · #37 도서관 문장
   #1 공용 패드 받기 실패 · #8 덜 받음 · #3 은행 저장 실패 · #5 두 탭 🪙 · #11 기기 시계 · #24 두 탭 복습 보상
   #12 OX 같은 그림 · #6 낚시 대회 밀린 정산 · #14 시세 겹침 · #17 보물 카드 · #36 의뢰 문장
   #26 마당 청소 · #29 요리 칸 · #25 요리 실패 실적 · #46 타워 시간 · #44 자랑방 · #45 색종이 · #38 우물 · #32 요리 듣기 보기 · #18 가게 가로 화면"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from draw635 import boot
from playwright.async_api import async_playwright
OUTD=OUT+"fix732/"; os.makedirs(OUTD, exist_ok=True)

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","FX732", isle=True)
        E=pg.evaluate
        W=lambda ms: pg.wait_for_timeout(ms)
        await E("()=>{ try{ HOUSE.setWx(false); }catch(e){} document.querySelectorAll('.hlP.on,#info.on,#ask.on').forEach(x=>x.classList.remove('on')); }")

        # ── #19 펫 ──
        r=await E("""async ()=>{ store('hyeng_proto_pet', null); gems=300; saveBag(); TFAC.openPet(); await new Promise(r=>setTimeout(r,200));
            const b=document.querySelector('#tfPt [data-buy]'); const p=TFAC.PETS.find(x=>x.k===b.dataset.buy); b.click(); await new Promise(r=>setTimeout(r,100));
            const f=askFn; document.getElementById('ask').classList.remove('on'); askFn=null; f(); await new Promise(r=>setTimeout(r,150));
            const g1=gems, nameWin=!!document.querySelector('#tfPt.on [data-nm]');
            document.querySelector('#tfPt .x').click(); await new Promise(r=>setTimeout(r,100)); const g2=gems, pet2=!!TFAC.PET();
            TFAC.openPet(); await new Promise(r=>setTimeout(r,150)); document.querySelector('#tfPt [data-buy="'+p.k+'"]').click(); await new Promise(r=>setTimeout(r,100));
            const f2=askFn; document.getElementById('ask').classList.remove('on'); askFn=null; f2(); await new Promise(r=>setTimeout(r,150));
            document.querySelector('#tfPt [data-nm]').click(); await new Promise(r=>setTimeout(r,150));
            return [p.p, g1, nameWin, g2, pet2, gems, (TFAC.PET()||{}).n||'']; }""")
        ok(r[1]==300 and r[2] and r[3]==300 and not r[4] and r[5]==300-r[0] and r[6], f"#19 펫: 이름 창에서 닫으면 💎 그대로 · 펫 없음 · 이름을 고르면 그때 💎 {r}")
        await E("()=>document.querySelectorAll('.hlP.on').forEach(x=>x.classList.remove('on'))")

        # ── #20 박물관 · #31 안내 ──
        r=await E("""async ()=>{ const S=ms=>new Promise(r=>setTimeout(r,ms)); delete mats.wheat; addMat('wheat',1); saveBag(); const P=NET.put;
            const go=async()=>{ TFAC.openMuseum(); await S(500); document.querySelector('#tfMu [data-mt="crop"]').click(); await S(100); const txt=document.querySelector('#tfMu .lb p').textContent; const b=document.querySelector('#tfMu [data-dn="wheat"]'); if(!b) return ['no btn', txt]; b.click(); await S(200);
              const a=document.querySelector('#hqP.on [data-w="wheat"]'); if(!a) return ['no quiz', txt]; a.click(); await S(1800); return ['ok', txt]; };
            NET.put=()=>Promise.reject('off'); const r1=await go(); const w1=mats.wheat|0; NET.put=P;
            const r2=await go(); for(let i=0;i<30 && (mats.wheat|0);i++) await S(150); const w2=mats.wheat|0; let srv=null; try{ srv=await NET.get('/hy/isle/museum/wheat'); }catch(e){}
            return [r1, w1, r2, w2, srv && srv.c===myCode]; }""")
        ok(r[0][0]=="ok" and r[1]==1, f"#20 박물관: 서버에 못 보내면 물건 그대로 {r[:2]}")
        ok(r[2][0]=="ok" and r[3]==0 and r[4], f"#20 박물관: 서버에 내 이름이 남은 뒤에만 물건을 뺌 {r[2:]}")
        ok("🪙25 (오늘 2번 더)" in r[0][1], f"#31 박물관 안내 = 🪙 · 오늘 남은 횟수 {r[0][1][:60]!r}")
        await E("()=>document.querySelectorAll('.hlP.on').forEach(x=>x.classList.remove('on'))")

        # ── #21 사진관 · #30 액자 · #27 친구 집 · #35 ──
        r=await E("""async ()=>{ const S=ms=>new Promise(r=>setTimeout(r,ms)); store('hyeng_proto_album', []); TECO.setCoin(50);
            const R=renderer.readRenderTargetPixels; renderer.readRenderTargetPixels=()=>{ throw new Error('x'); };
            TFAC.openPhoto(); await S(150); document.querySelector('#tfPh [data-shoot]').click(); await S(150); const c1=TECO.coins(); renderer.readRenderTargetPixels=R;
            TFAC.openPhoto(); await S(150); document.querySelector('#tfPh [data-shoot]').click(); await S(300); const c2=TECO.coins();
            const m1=ITEMS.photo.build(0).children[1].material.map;
            TFAC.openPhoto(); await S(150); document.querySelector('#tfPh [data-shoot]').click(); await S(300); const c3=TECO.coins();
            const m2=ITEMS.photo.build(0).children[1].material.map, m3=ITEMS.photo.build(1).children[1].material.map;
            visiting={n:'친구', code:'ZZZZZ'}; let mv=null; try{ mv=ITEMS.photo.build(0).children[1].material.map; }finally{ visiting=null; }
            const A=JSON.parse(localStorage.getItem(skey('hyeng_proto_album'))||'[]');
            return [c1, c2, c3, !!m1 && m1===m2, !!m3 && m3!==m1, !!mv && !!mv.isCanvasTexture && mv!==m1, A.map(a=>a.s).join(',')]; }""")
        ok(r[0]==50 and r[1]==40 and r[2]==30, f"#21 사진관: 못 찍으면 🪙 그대로 · 찍으면 🪙10 {r[:3]}")
        ok(r[3] and r[4] and r[6]=="0,1", f"#30 새 사진을 찍어도 걸어 둔 액자(0번) 사진 그대로 · 1번 = 새 사진 · 칸 {r[6]!r}")
        ok(r[5], "#27 친구 집 액자 = 내 사진 아니고 「친구 사진」 그림")
        await E("()=>document.querySelectorAll('.hlP.on').forEach(x=>x.classList.remove('on'))")

        # ── #16 간식 가방 칸 ──
        r=await E("""async ()=>{ const S=ms=>new Promise(r=>setTimeout(r,ms)); delete mats.cookie; saveBag(); TECO.setCoin(100); const cap=bagCap; bagCap=slots().length;
            try{ TFAC.openSnack(); await S(300); SHOPUI.pick('cookie', 1); await S(100); SHOPUI.go(); await S(300);
              return [!!document.querySelector('#hqP.on'), document.getElementById('suP').classList.contains('on'), mats.cookie|0, TECO.coins(), (document.querySelector('#suP .suSay')||{}).textContent||'']; }
            finally{ bagCap=cap; try{ SHOPUI.close(); }catch(e){} document.getElementById('hqP') && document.getElementById('hqP').classList.remove('on'); } }""")
        ok(r[0] is False and r[2]==0 and r[3]==100 and ("bag" in r[4].lower() or "가방" in r[4]), f"#16 간식: 가방이 꽉 차면 주문 전에 알려 줌 {r}")

        # ── #15 · #28 우체국 ──
        await E("""async ()=>{ const t=Date.now(), L={}; for(let i=0;i<35;i++) L['m'+(t-i*60000)+'_ABCDE']={f:'ABCDE', n:'친구', s:i%12, st:0, t:t-i*60000};
            await NET.put('/hy/isle/mail/'+myCode, L); const ids=Object.keys(L).sort((a,b)=>L[b].t-L[a].t); window._oldId=ids[34]; await TFAC.loadMail(); localStorage.setItem(skey('hyeng_proto_mailr'), JSON.stringify(TFAC.MAIL.list.map(m=>m.id).filter(id=>id!==window._oldId)));
            store('hyeng_proto_mails', {d:dayKey(), to:['ABCDE']}); }""")
        r=await E("""async ()=>{ const S=ms=>new Promise(r=>setTimeout(r,ms)); TFAC.openPost('in'); await S(700); const first=(document.querySelector('#tfPoB [data-m]')||{}).dataset; const more=!!document.querySelector('#tfPoB [data-more]');
            document.querySelector('#tfPoB [data-m]').click(); await S(200); const rep=document.querySelector('#tfPoB [data-reply]'); if(rep) rep.click(); await S(300);
            return [first && first.m===window._oldId, more, (document.getElementById('tfPoB')||{}).textContent||'']; }""")
        ok(r[0] and r[1], f"#15 안 읽은 편지가 맨 위 · 30통 넘으면 「더 보기」 {r[:2]}")
        ok("오늘 벌써 보냈어요" in r[2], f"#28 오늘 보낸 친구에게 답장 = 막음 {r[2][:50]!r}")
        await E("()=>document.querySelectorAll('.hlP.on').forEach(x=>x.classList.remove('on'))")

        # ── #33 퀴즈 타이머 ──
        r=await E("""async ()=>{ const S=ms=>new Promise(r=>setTimeout(r,ms)); const W1=HLIFE.pickWords(1), W2=HLIFE.pickWords(2); let d1=0, d2=0;
            HLIFE.quiz('A', W1, ()=>{ d1++; }); await S(100); document.querySelector('#hqP .b [data-w]').click(); await S(200);
            document.querySelector('#hqP .hqX').click(); HLIFE.quiz('B', W2, ()=>{ d2++; }); await S(1500);
            const on=document.getElementById('hqP').classList.contains('on'), t=document.querySelector('#hqP .t').textContent; document.querySelector('#hqP .hqX').click(); return [on, t, d1, d2]; }""")
        ok(r[0] and r[1].startswith("B") and r[2]==0, f"#33 앞 문제를 닫고 새 문제를 열면 앞 타이머가 새 문제를 넘기지 않음 · 닫은 문제는 보상 없음 {r}")

        # ── #37 · #36 문장 ──
        r=await E("""()=>{ const B=TFAC.BOOKS, park=B.find(b=>b.id==='park'), rain=B.find(b=>b.id==='rain'); return [park.p.map(x=>x[1]).join('|'), rain.p.map(x=>x[1]).join('|'), park.p[0][0]!==park.p[1][0]]; }""")
        ok("red ball" not in r[0] and "yellow umbrella" not in r[1] and r[2], f"#37 도서관: 색이 없는 그림에 색 문장 없음 · 공원/나무 그림 다름 {r[0][:60]}")
        src=open(os.path.join(SITE,"proto","isle-vil.js"),encoding="utf-8").read()
        ok("5 bundles of wheat" in src and "2 pieces of coal" in src and "I need 5 wheat" not in src, "#36 의뢰: wheat · coal 에 세는 말")

        # ── #3 은행 · #11 기기 시계 ──
        r=await E("""()=>{ TECO.setCoin(100); const o=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(String(k).indexOf('hyeng_proto_bank')>=0) throw new Error('full'); return o.call(this,k,v); };
            let a; try{ a=TECO.deposit('sv', 50); }finally{ Storage.prototype.setItem=o; } const c1=TECO.coins(), s1=TECO.BK().sv|0;
            const b=TECO.deposit('sv', 50); const c2=TECO.coins(), s2=TECO.BK().sv|0; const w=TECO.withdraw('sv'); return [a, c1, s1, b, c2, s2, w, TECO.coins()]; }""")
        ok(r[0] is False and r[1]==100 and r[2]==0, f"#3 은행: 저장이 안 되면 🪙 안 빠짐 {r[:3]}")
        ok(r[3] and r[4]==50 and r[5]==50 and r[7]==100, f"#3 은행: 보통 넣기·빼기는 그대로 {r[3:]}")
        r=await E("""()=>{ const a0=TWN8.auto, o0=TWN8.ok; TWN8.auto=false; TWN8.off=0; TWN8.base=Date.now(); TWN8.pa=performance.now(); TWN8.ok=true;
            const real=Date.now; let v; Date.now=()=>real()+86400e3; try{ v=srvNow(); }finally{ Date.now=real; } const okAfter=TWN8.ok; TWN8.auto=a0; TWN8.pa=null; TWN8.ok=o0; return [Math.round((v-real())/1000), okAfter]; }""")
        ok(abs(r[0])<5 and r[1] is False, f"#11 서버 시계를 맞춘 뒤 기기 시계를 하루 앞으로 → 은행 시각은 그대로 · 다시 맞춤 {r}")

        # ── #1 · #8 공용 패드 ──
        r=await E("""async ()=>{ const P0={kid:PAD.kid, id:PAD.id, ns:PAD.ns, pulled:PAD.pulled, bad:PAD.bad}; const G=NET.get;
            PAD.kid={id:'T732', n:'시험'}; PAD.id='T732'; PAD.ns='@T732_'; PAD.pulled=false; PAD.bad=false;
            try{ NET.get=()=>Promise.reject('off'); const a=await padPull(); NET.get=G; const b=await padPush();
              await NET.put('/hy/life/sv/T732', {at:Date.now()+5000, n:'시험', d:JSON.stringify({coin:'5', big:'"x"'})});
              const o=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(String(k).endsWith('@T732_big')) throw new Error('full'); return o.call(this,k,v); };
              let c; try{ c=await padPull(); }finally{ Storage.prototype.setItem=o; }
              const mt=localStorage.getItem('hyeng_proto_@T732__mt'); PAD.pulled=true; const d=await padPush(); return [a, b, c, PAD.bad, mt, d]; }
            finally{ NET.get=G; Object.assign(PAD, P0); for(let i=localStorage.length-1;i>=0;i--){ const k=localStorage.key(i); if(k && k.indexOf('@T732_')>=0) localStorage.removeItem(k); } } }""")
        ok(r[0]==-1 and r[1] is False, f"#1 공용 패드: 서버 기록을 못 읽으면 「받았음」으로 안 침 · 이 패드 것을 안 올림 {r[:2]}")
        ok(r[2]==0 and r[3] is True and r[4] is None and r[5] is False, f"#8 덜 받으면 「최신」 표시 안 함 · 서버에 안 올림 {r[2:]}")

        # ── #12 OX · #14 시세 · #17 보물 카드 ──
        r=await E("""()=>{ let n=0, bad=0, ex=null; for(let i=0;i<4000;i++){ const Q=IPLAY.oxQ(i); if(Q.yes) continue; n++; if(Q.shown[2]===Q.w[2] || Q.shown[1]===Q.w[1] || Q.shown[0]===Q.w[0]){ bad++; ex=ex||[Q.w[0],Q.shown[0],Q.w[2]]; } } return [n, bad, ex]; }""")
        ok(r[0]>1500 and r[1]==0, f"#12 OX 「아니에요」 문제에 같은 그림·같은 뜻 단어 없음 {r}")
        r=await E("""async ()=>{ const G=NET.get; let n=0; NET.get=(p)=>{ if(String(p).indexOf('/hy/isle/mkt/')===0){ n++; return new Promise(r=>setTimeout(()=>r({}), 300)); } return G(p); };
            try{ await TECO.mkLoad(true); for(let i=0;i<60;i++) TECO.mkF('carrot'); const k1=n; await new Promise(r=>setTimeout(r,400)); for(let i=0;i<60;i++) TECO.mkF('carrot'); return [k1, n]; }finally{ NET.get=G; } }""")
        ok(r[0]<=1 and r[1]<=1, f"#14 시세: 가게 그림 한 번에 물건마다 불러도 서버 요청은 하나 {r}")
        r=await E("""()=>{ const T=THREE.Texture.prototype, d0=T.dispose; let n=0; T.dispose=function(){ n++; return d0.call(this); }; try{ IPLAY.trBuild(); const k=IPLAY.S.tr.objs.length; IPLAY.trBuild(); return [k, n]; }finally{ T.dispose=d0; } }""")
        ok(r[0]==0 or r[1]>=r[0], f"#17 보물 카드를 다시 만들 때 그림을 버림 (카드 {r[0]} · 버림 {r[1]})")

        # ── #2·#7 서버 규칙(남의 땅 덮어쓰기 거부) 흉내 → 「먼저 골랐어요」 ──
        r=await E("""async ()=>{ const L0=ISLE.recLot(); if(!L0) return 'no empty lot'; const id=L0.id; await NET.put('/hy/isle/lot2/'+id, {k:'OTHERKID', n:'친구', at:1}); const G=NET.get, P=NET.put; let first=true;
            NET.get=p=>{ if(String(p)==='/hy/isle/lot2/'+id && first){ first=false; return Promise.resolve(null); } return G(p); };   /* 처음 볼 땐 비어 있었음 (거의 같이 고름) */
            NET.put=(p,v)=>String(p).indexOf('/hy/isle/lot2/')===0 ? Promise.reject(401) : P(p,v);   /* 규칙이 거부 */
            let r; try{ r=await ISLE.claim(id); }finally{ NET.get=G; NET.put=P; } await NET.del('/hy/isle/lot2/'+id); return r; }""")
        ok(r=="taken", f"#2·#7 친구가 먼저 고른 땅을 덮으려다 서버가 거부하면 「먼저 골랐어요」(taken) {r!r}")

        # ── #6 낚시 대회 밀린 정산 ──
        r=await E("""async ()=>{ const S=ms=>new Promise(r=>setTimeout(r,ms)); const K=TECO.kk('hyeng_isle_ftq'), me=ISLE.myKey(), t=IPLAY.T();
            const ids=['t'+(t-3*3600e3), 't'+(t-2*3600e3)]; for(const id of ids){ localStorage.removeItem(TECO.kk('hyeng_isle_ftp_'+id)); await NET.put('/hy/isle/ft/'+id, {[me]:{n:'루아', s:50, fee:1}, OTHER1:{n:'친구', s:30, fee:1}}); }
            localStorage.setItem(K, JSON.stringify(ids.map((id,i)=>({id, en:t-(3-i)*3600e3+600000}))));
            TECO.setCoin(0); const G=NET.get; NET.get=p=>String(p).indexOf('/hy/isle/ft/')===0 ? Promise.reject('off') : G(p);
            IPLAY.ftCatchUp(t, true); await S(500); const q1=IPLAY.ftQ().length, c1=TECO.coins(); NET.get=G;
            IPLAY.ftCatchUp(t, true); for(let i=0;i<30 && IPLAY.ftQ().length;i++) await S(150); await S(300);
            const c2=TECO.coins(), q2=IPLAY.ftQ().length; document.getElementById('info').classList.remove('on'); return [q1, c1, q2, c2]; }""")
        ok(r[0]==2 and r[1]==0, f"#6 대회 순위를 못 받으면 대기 목록 그대로 · 상금 그대로 {r[:2]}")
        ok(r[2]==0 and r[3]==40, f"#6 밀린 대회 둘 다 정산 (1등 × 2 = 🪙 20+20) {r[2:]}")

        # ── #26 마당 청소 ──
        await E("()=>HOUSE.goYard ? HOUSE.goYard() : null")
        r=await E("""()=>{ const R=Math.random, cap=bagCap; const k='9,9', old=yd.db[k]; ['wheat seeds','carrot seeds','strawberry seeds','tomato seeds'].forEach(n=>delete mats[n]); saveBag();
            bagCap=slots().length+1; yd.db[k]='weed2'; Math.random=()=>0; try{ yClear(k); }finally{ Math.random=R; bagCap=cap; }
            const r=[!!yd.db[k], ['wheat seeds','carrot seeds','strawberry seeds','tomato seeds'].map(n=>mats[n]|0).join(',')];
            bagCap=slots().length+4; Math.random=()=>0; try{ yClear(k); }finally{ Math.random=R; bagCap=cap; } r.push(!yd.db[k], ['wheat seeds','carrot seeds','strawberry seeds','tomato seeds'].map(n=>mats[n]|0).join(','));
            if(old) yd.db[k]=old; return r; }""")
        ok(r[0] and r[1]=="0,0,0,0", f"#26 다 안 들어가면 하나도 안 주고 잡초도 그대로 (예전: 첫 씨앗만 받고 잡초는 남음) {r[:2]}")
        ok(r[2] and r[3]=="1,1,1,1", f"#26 칸이 있으면 다 받고 치움 {r[2:]}")

        # ── #29 요리 칸 · #25 실패면 실적 안 셈 ──
        r=await E("""()=>{ const F=FISH.find(f=>!f.noRot && !f.noCook); const bag0=bag.slice(), m0=Object.assign({}, mats), cap=bagCap;
            bag.length=0; Object.keys(mats).forEach(k=>delete mats[k]); bag.push({en:F.en, cm:20, t:now(), at:now()}); mats.tomato=3; bagCap=slots().length;
            const o=tEv; let n=0; tEv=function(a){ if(a==='cook') n++; return o.apply(this, arguments); };
            let a, b, c; try{ a=make('cook','fish stew'); const s=mats['fish stew']|0;
              bag.length=0; Object.keys(mats).forEach(k=>delete mats[k]); mats.tomato=3; mats.wheat=2; mats.pumpkin=5; bagCap=slots().length; const n0=n; b=make('cook','pasta'); c=[s, n0, n]; }
            finally{ tEv=o; bag.length=0; bag0.forEach(x=>bag.push(x)); Object.keys(mats).forEach(k=>delete mats[k]); Object.assign(mats, m0); bagCap=cap; saveBag(); }
            return [a, c[0], b, c[1], c[2]]; }""")
        ok(r[0] is True and r[1]==1, f"#29 물고기를 쓰면 칸이 비어 🍲 fish stew 를 만들 수 있음 {r[:2]}")
        ok(r[2] is False and r[3]==r[4], f"#25 가방이 꽉 차 못 만들면 할 일·의뢰 실적 안 셈 {r[2:]}")

        # ── #46 · #44 · #45 타워 ──
        r=await E("()=>[twTime(59.98), twTime(9.97), twTime(65.04), twTime(0)]")
        ok(r==["1:00.0","0:10.0","1:05.0","0:00.0"], f"#46 타워 시간 표시 {r}")
        r=await E("""()=>{ const R=TW.rec, a=store('hyeng_proto_twtot'), b=store('hyeng_proto_twbest'); TW.rec={[dayKey()]:{sky:{best:95.5, n:3}}}; store('hyeng_proto_twtot', null); store('hyeng_proto_twbest', null);
            try{ const x=HLIFE.brag(); return [x.tw, x.twBest]; }finally{ TW.rec=R; store('hyeng_proto_twtot', a); store('hyeng_proto_twbest', b); } }""")
        ok(r[0]==3, f"#44 자랑방 40층 = 완주 횟수 (같은 날 3번 = 3) {r}")
        r=await E("""()=>{ const t0=TW.top; TW.top={mesh:{position:new THREE.Vector3(0,0,0)}, max:{y:1}}; const n0=towerG.children.length; try{ twConfetti(); twConfetti(); const M=towerG.children.slice(n0); const g=new Set(M.map(m=>m.geometry)), mt=new Set(M.map(m=>m.material)); M.forEach(m=>towerG.remove(m)); return [M.length, g.size, mt.size]; }finally{ TW.top=t0; } }""")
        ok(r[0]==80 and r[1]==1 and r[2]<=10, f"#45 색종이 = 판 1개 · 색 재질 10개를 돌려씀 {r}")

        # ── #38 우물 ──
        r=await E("""()=>{ if(!yd) return ['no yd']; const RO=yReachOK; yReachOK=()=>true;   /* 길 막힘 검사는 이 시험과 상관없음 (섬에 있을 땐 마당 길 계산이 달라서) */ try{ const d0=JSON.parse(JSON.stringify(yData())); const st=ystock.well|0; ystock.well=0;
            let cell=null; for(let x=1;x<YN-1 && !cell;x++) for(let z=1;z<YN-1 && !cell;z++){ if(yFits('well',x,z,0)===1) cell=[x,z]; }
            if(!cell){ ystock.well=st; return ['no cell']; } const d=JSON.parse(JSON.stringify(d0)); d.p=(d.p||[]).filter(q=>q[0]!=='well' && q[0]!=='kk_well'); d.p.push(['well',cell[0],cell[1],0,0]); d.ws=cell.slice();
            const io=ISLE_MODE; let got; try{ yLoad(d); got=yplaced.some(q=>q.id==='well' && q.x===cell[0] && q.z===cell[1]); }finally{ ystock.well=st; yLoad(d0); } return [got, cell, io]; }finally{ yReachOK=RO; } }""")
        ok(r[0] is True, f"#38 우물 자리에 지은 우물이 다시 불러와도 그대로 {r}")

        # ── #32 요리 듣기 보기 ──
        r=await E("""async ()=>{ let dup=0, food=0; for(let k=0;k<30;k++){ HLIFE.cookGame({id:'pumpkin pie', need:{pumpkin:1}}, ()=>{}); await null; const E=[...document.querySelectorAll('#hqP .o [data-w]')]; const em=E.map(b=>b.textContent); if(new Set(em).size<em.length) dup++; if(E.some(b=>MAT[b.dataset.w] && MAT[b.dataset.w].food)) food++; }
            document.querySelector('#hqP .hqX').click(); return [dup, food]; }""")
        ok(r==[0,0], f"#32 요리 듣기: 보기 그림이 겹치지 않음 · 보기 = 재료 {r}")

        # ── #24 두 탭 복습 · #5 두 탭 🪙 ──
        pg2=await ctx.new_page(); await pg2.route("**/*", fake); await pg2.goto(ORIGIN+"proto/house.html?isle=1"); await pg2.wait_for_timeout(3500)
        await E("()=>TECO.setCoin(100)"); await pg2.wait_for_timeout(300)
        await pg2.evaluate("()=>TECO.addCoin(20)"); await W(300)
        r=await E("()=>{ TECO.pay2({g:0, c:10}); return [TECO.coins(), store('hyeng_proto_coin')]; }")
        r2=await pg2.evaluate("()=>[TECO.coins(), store('hyeng_proto_coin')]")
        ok(r==[110,110] and r2[1]==110, f"#5 두 탭: 한쪽에서 벌고 다른 쪽에서 써도 서로 안 덮음 {r} {r2}")
        r=await E("""async ()=>{ const S=ms=>new Promise(r=>setTimeout(r,ms)); store('hyeng_proto_rev', ''); gems=50; saveBag(); HLIFE.openBooks(); await S(200); const b=document.querySelector('#hlBk [data-rev]'); if(!b || b.disabled) return ['no rev']; b.click(); await S(200);
            store('hyeng_proto_rev', dayKey());   /* 다른 탭에서 먼저 끝냄 */
            for(let i=0;i<8 && document.getElementById('hqP').classList.contains('on');i++){ const w=document.querySelector('#hqP .b [data-w]'); if(w) w.click(); await S(1250); }
            return [gems, document.getElementById('hqP').classList.contains('on')]; }""")
        ok(r[0]==50, f"#24 다른 탭에서 오늘 복습을 끝냈으면 이 탭은 💎 안 줌 {r}")
        await pg2.close()

        # ── #18 가게 가로 화면 ──
        await pg.set_viewport_size({"width":844, "height":390}); await W(600)
        r=await E("""async ()=>{ try{ HOUSE.openShop ? HOUSE.openShop('fish') : null; }catch(e){} if(!document.querySelector('#suP.on')){ try{ TFAC.openSnack(); }catch(e){} } await new Promise(r=>setTimeout(r,500));
            const B=document.querySelector('#suP .suBody'), P=document.getElementById('suP'); const c=document.querySelector('#suP .suC'); return [B?Math.round(B.getBoundingClientRect().height):0, P?Math.round(P.getBoundingClientRect().height):0, c?Math.round(c.getBoundingClientRect().height):0]; }""")
        await pg.screenshot(path=OUTD+"shop_land.png")
        ok(r[0]>=r[2]*1.3 and r[0]>=110, f"#18 휴대폰 가로: 물건 칸이 한 줄 반 넘게 보임 (칸 높이 {r[0]} · 창 {r[1]} · 카드 {r[2]})")
        await E("()=>{ try{ SHOPUI.close(); }catch(e){} }")
        await pg.set_viewport_size({"width":390, "height":844}); await W(300)

        ok(not [e for e in real_errs(errs) if "Error" in e or "error" in e], f"오류 0 {real_errs(errs)[:4]}")
        await ctx.close()

        # ── #4 점검 모드 끝내기 = 점검 탭이 바꾼 칸만 되돌림 ──
        c2=await br.new_context(); A=await c2.new_page(); await A.route("**/*", route)
        await A.goto(ORIGIN+"index.html"); await A.wait_for_timeout(800)
        await A.evaluate("()=>{ localStorage.setItem('hyeng_t732c','0'); }")
        await A.goto(ORIGIN+"index.html?qa=1"); await A.wait_for_timeout(1500)
        B=await c2.new_page(); await B.route("**/*", route); await B.goto(ORIGIN+"index.html"); await B.wait_for_timeout(1500)
        await B.evaluate("()=>localStorage.setItem('hyeng_t732b','B')")
        await A.evaluate("()=>{ localStorage.setItem('hyeng_t732a','A'); localStorage.setItem('hyeng_t732c','1'); }")
        await A.goto(ORIGIN+"index.html?qa=0", wait_until="commit"); await A.wait_for_timeout(2500)
        r=await B.evaluate("()=>[localStorage.getItem('hyeng_t732a'), localStorage.getItem('hyeng_t732b'), localStorage.getItem('hyeng_t732c'), localStorage.getItem('hyeng_qa_bak'), localStorage.getItem('hyeng_qa_bakk')]")
        ok(r==[None,"B","0",None,None], f"#4 점검 끝내기: 점검 탭이 쓴 칸만 되돌리고 다른 탭(보통 모드) 기록은 그대로 {r}")
        await c2.close()
        await br.close()
    print("FAIL" if bad else "PASS", len(bad))
    sys.exit(1 if bad else 0)

asyncio.run(main())
