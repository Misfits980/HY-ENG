"""(v528) 🏝 우리 마을 — 매끈한 섬 · 땅 고르기(서버) · 아이들 놀이 6가지 · 문 앞 길 보장 (가짜 서버 · 아이 3명)
   ① 땅: 처음 나오면 빈 땅 하나가 저절로 내 땅(서버) · 친구 땅에 친구 이름 · 가짜 이름 없음
   ② 땅 고르기: 친구 땅은 「taken」 · 빈 땅으로 이사 = 옛 땅 비움 · ⭐ 좋은 자리는 공부한 날 5일부터
   ③ 🚪 모든 집 문에서 광장까지 걸어갈 수 있음 (48칸 다 차도) · 빈 땅이 4칸 아래면 4동이 열림
   ④ 실시간: 서로 보임 · 💬 말 → 상대 말풍선 · 🎣 잡으면 소식
   ⑤ 🎣 섬 호수 낚시: 물고기 그림자가 섬에 · 던지기 · 🏆 대회 기록 → 다른 아이 순위에 보임 · 대회 끝 상
   ⑥ ⭕❌ OX: 맞는 판 = 연속 +1 · 틀린 판 = 0 + 밖으로 · 오늘 기록 서버
   ⑦ 🧊 얼음땡: 같은 술래 · 술래가 잡으면 얼음(못 움직임) · 친구가 단어 맞히면 풀림
   ⑧ 🎁 보물: 카드 10장 · 주우면 서버 · 합이 목표면 상자 상 한 번
   ⑨ 🏠 친구 집 누르기 → 놀러 가기 · 🗼 타워 이름표 · 카메라 등 뒤 따라가기"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake, DB
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def kid(code,name,extra=""):
            ctx=await br.new_context(viewport={"width":390,"height":700}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e))); pg.on("console", lambda m: print("  ["+name+"] "+m.text[:300]) if m.type in ("warning","error") and "Failed to load" not in m.text and "GL Driver" not in m.text else None)
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1&iplay=test"+extra); await pg.wait_for_timeout(600)
            await pg.evaluate("""([c,n])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')||k.startsWith('hyeng_isle')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); localStorage.setItem('hyeng_isle_cam','1');
                localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); }""", [code,name])
            await pg.reload(); await pg.wait_for_timeout(1800); return pg
        async def until(pg, js, n=120):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        async def enter(pg):
            await pg.evaluate("()=>HOUSE.exitRoom()"); return await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy && !HOUSE.hero().slide")
        A=await kid("AAAAA","루아","&ft=on"); B=await kid("BBBBB","하준","&ft=on")
        ok(await enter(A) and await enter(B), "두 아이 🏝 들어감")
        await A.wait_for_timeout(2500)
        lots=DB["hy"]["isle"]["lot2"]
        r=await B.evaluate("()=>({me:ISLE.myHouse().id, owners:ISLE.lots.filter(l=>l.owner&&!l.me).map(l=>l.owner)})")
        print("①", json.dumps(lots, ensure_ascii=False), r)
        ok(len(lots)==2 and {v["n"] for v in lots.values()}=={"루아","하준"}, "① 처음 나오면 땅 하나씩 서버에")
        ok(r["owners"]==["루아"], f"① 친구 땅에 친구 이름 (가짜 이름 없음) {r['owners']}")
        # ②
        aid=await A.evaluate("()=>ISLE.myHouse().id")
        r=await B.evaluate("(id)=>ISLE.claim(id)", aid)
        ok(r=="taken", f"② 친구 땅은 못 고름 {r}")
        old=await B.evaluate("()=>ISLE.myHouse().id")
        fid=await B.evaluate("()=>ISLE.lots.find(l=>!l.owner && !l.prem && l.hood==='1동').id")
        r=await B.evaluate("(id)=>ISLE.claim(id)", fid)
        ok(r=="ok" and fid in DB["hy"]["isle"]["lot2"] and old not in DB["hy"]["isle"]["lot2"], f"② 이사 = 새 땅 · 옛 땅 비움 {r} {old}→{fid}")
        r=await B.evaluate("()=>{ localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:1,tot:2}})); const L=ISLE.lots.find(l=>l.prem && !l.owner); const a=ISLE.lotState(L); localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:6,tot:6}})); return [a, ISLE.lotState(L)]; }")
        ok(r==["lock","free"], f"② ⭐ 좋은 자리 = 공부한 날 5일부터 {r}")
        await B.evaluate("async ()=>{ await ISLE.loadLots(); ISLE.rebuild(); }")
        r=await B.evaluate("()=>ISLE.lots.filter(l=>l.owner).length")
        ok(r==2, f"② 다시 그려도 땅 2개 {r}")
        # ③ 문 앞 길
        r=await B.evaluate("()=>({stuck:ISLE.stuckDoors(), me:ISLE.myHouse().door, ok:!ISLE.blocked(...ISLE.myHouse().door)})")
        ok(not r["stuck"] and r["ok"], f"③ 문 앞 칸 열림 · 광장까지 감 {r}")
        C=await kid("CCCCC","서아")
        r=await C.evaluate("""async ()=>{ await NET.ready(); const ids=[]; for(let h=1;h<=3;h++) for(let n=1;n<=16;n++) ids.push(h+'-'+n);
            for(const id of ids){ const v=await NET.get('/hy/isle/lot2/'+id); if(!v) await NET.put('/hy/isle/lot2/'+id, {k:'x'+id, c:'ZZZZZ', n:'친구'+id, at:1}); } return ids.length; }""")
        ok(await enter(C), "세 번째 아이 들어감 (땅이 다 차도)")
        r=await C.evaluate("()=>({hoods:ISLE.hoodCount(), stuck:ISLE.stuckDoors(), owned:ISLE.lots.filter(l=>l.owner).length, me:ISLE.myHouse()&&ISLE.myHouse().id, path:(()=>{ const d=ISLE.myHouse().door, P=ISLE.plazaCell(); return !!HOUSE.findPath(d[0],d[1],P[0],P[1]); })()})")
        print("③", r)
        ok(r["hoods"]>=4 and r["me"] and r["me"].startswith("4-"), f"③ 다 차면 4동이 열리고 거기에 내 땅 {r['me']}")
        ok(not r["stuck"] and r["path"], f"③ 집 {r['owned']}채 — 모든 문에서 광장까지 걸어감 {r['stuck']}")
        # ④ 실시간
        await A.wait_for_timeout(4000)
        r=await A.evaluate("()=>Object.keys(VLN.peers)")
        ok("BBBBB" in r and "CCCCC" in r, f"④ 친구가 보임 {r}")
        await A.evaluate("()=>HOUSE.vcSay('Hello!')");
        ok(await until(B, "()=>Object.values(VLN.msgs).some(m=>m.m==='Hello!') && !!VLN.peers['AAAAA'] && !!VLN.peers['AAAAA'].say", 40), "④ 💬 말 → 친구 머리 위 말풍선")
        # ⑤ 낚시
        r=await A.evaluate("""()=>{ const L=ISLE.lake(); return {pg:PG===ISLE.G, wl:WL, water:ISLE.waterCell(Math.floor(L.x),Math.floor(L.z)), shadows:PS.length, inG:PS.every(o=>o.g.parent===ISLE.G)}; }""")
        await A.wait_for_timeout(3000)
        r=await A.evaluate("""()=>{ const L=ISLE.lake(); return {pg:PG===ISLE.G, wl:WL, water:ISLE.waterCell(Math.floor(L.x),Math.floor(L.z)), shadows:PS.length, inG:PS.every(o=>o.g.parent===ISLE.G)}; }""")
        print("⑤", r)
        ok(r["pg"] and r["water"] and r["shadows"]>0 and r["inG"], f"⑤ 섬 호수에 물고기 그림자 {r}")
        await A.evaluate("()=>{ const L=ISLE.SPOT.lake; const h=HOUSE.hero(); h.g.position.set(L[0]-2.2,0,L[2]); h.cx=Math.floor(L[0]-2.2); h.cz=Math.floor(L[2]); const lk=ISLE.lake(); HOUSE.tryFish(Math.floor(lk.x-1), Math.floor(lk.z), lk.x-1, lk.z); }")
        ok(await until(A, "()=>['cast','wait','bite'].includes(HOUSE.F.st) || (HOUSE.hero().moving)", 40), "⑤ 호수를 누르면 던지러 감")
        await A.evaluate("()=>{ try{ HOUSE.F.st='idle'; }catch(e){} }")
        await A.evaluate("()=>IPLAY.onCatch(HOUSE.FISH.find(f=>f.en==='shark')||HOUSE.FISH[0], 88, false, false)")
        await B.wait_for_timeout(500)
        r=await B.evaluate("async ()=>{ const s=IPLAY.ftSlot(); await IPLAY.ftLoad(s.id); return [s.id, IPLAY.S.ft.board]; }")
        ok(r[1] and r[1][0]["n"]=="루아" and r[1][0]["s"]==88, f"⑤ 🏆 대회 기록이 친구 순위에 {r}")
        ok(await until(B, "()=>Object.values(VLN.msgs).some(m=>m.sys && /88cm/.test(m.m))", 30), "⑤ 잡으면 모두에게 소식")
        g0=await A.evaluate("()=>HOUSE.gems()")
        await A.evaluate("(id)=>{ localStorage.removeItem('hyeng_isle_ftp_'+id); return IPLAY.ftEnd(id); }", r[0]); await A.wait_for_timeout(500)
        g1=await A.evaluate("()=>HOUSE.gems()")
        t=await A.evaluate("()=>document.getElementById('infoT').innerText")
        ok(g1-g0==20 and "1등" in t, f"⑤ 대회 끝 = 1등 💎+20 (v559 · 하루 한 번) · 순위 창 {g0}→{g1}")
        await A.evaluate("()=>document.getElementById('info').classList.remove('on')")
        # ⑥ OX
        OXJS="""(right)=>{ const P=12000, J=10000, now=IPLAY.T(), i=Math.floor(now/P)+1, Q=IPLAY.oxQ(i); TWN8.test+= (i*P+J-300)-now; const c=ISLE.SPOT.oxC, h=HOUSE.hero(); const want=right ? (Q.yes?'O':'X') : (Q.yes?'X':'O');
            h.g.position.set(c[0]+(want==='O'?-2:2), 0, c[1]); h.cx=Math.floor(h.g.position.x); h.cz=Math.floor(h.g.position.z); h.path=[]; return [IPLAY.oxIn(), want, i, now]; }"""
        st0=await A.evaluate("()=>IPLAY.S.ox.st")
        r=await A.evaluate(OXJS, True); await until(A, "()=>IPLAY.S.ox.judged===Math.floor(IPLAY.T()/12000) && IPLAY.T()%12000>10000", 40)
        st1=await A.evaluate("()=>IPLAY.S.ox.st")
        ok(r[0]==r[1] and st1==st0+1, f"⑥ 맞는 판 = 연속 +1 {r} {st0}→{st1}")
        r=await A.evaluate(OXJS, False); await until(A, "()=>IPLAY.S.ox.judged===Math.floor(IPLAY.T()/12000) && IPLAY.T()%12000>10000", 40)
        st2=await A.evaluate("()=>[IPLAY.S.ox.st, IPLAY.oxIn()]")
        print("⑥", r, await A.evaluate("()=>{const h=HOUSE.hero(), p=h.g.position, now=IPLAY.T(); return [p.x.toFixed(2),p.z.toFixed(2), Math.floor(now/12000), now%12000, IPLAY.S.ox.judged, IPLAY.S.ox.st, TWN8.test, TWN8.off, F.st, place===PL.isle]; }"))
        ok(st2[0]==0 and st2[1] is None, f"⑥ 틀린 판 = 0 + 마당 밖으로 {st2}")
        ok(DB["hy"]["isle"].get("ox"), "⑥ 오늘 OX 기록 서버")
        await A.evaluate("()=>{ TWN8.test=0; }")
        # ⑦ 얼음땡
        PG_="(k)=>{ const c=ISLE.SPOT.pgC, h=HOUSE.hero(); const o={A:[-1,0],B:[1,0],C:[0,1.5]}[k]; h.g.position.set(c[0]+o[0],0,c[1]+o[1]); h.cx=Math.floor(h.g.position.x); h.cz=Math.floor(h.g.position.z); h.path=[]; }"
        for pg,k in ((A,"A"),(B,"B"),(C,"C")): await pg.evaluate(PG_, k)
        TGJS="()=>{ const L=IPLAY.tagPlayers(), r=Math.floor(IPLAY.T()/60000), t=IPLAY.tagger(L,r); return [L.length, t && (t.me ? myCode : t.k)]; }"
        for _ in range(60):
            tg=[await pg.evaluate(TGJS) for pg in (A,B,C)]
            if all(x[0]==3 for x in tg) and len({x[1] for x in tg})==1: break
            await A.wait_for_timeout(300)
        print("⑦", tg)
        ok(all(x[0]==3 for x in tg) and len({x[1] for x in tg})==1, f"⑦ 세 아이 모두 같은 술래 {tg}")
        T={"AAAAA":A,"BBBBB":B,"CCCCC":C}; tcode=tg[0][1]; tp=T[tcode]; others=[c for c in T if c!=tcode]; victim=others[0]; helper=others[1]
        vp=await T[victim].evaluate("()=>[HOUSE.hero().g.position.x, HOUSE.hero().g.position.z]")
        await tp.evaluate("(p)=>{ const h=HOUSE.hero(); h.g.position.set(p[0]+.3,0,p[1]); }", vp)
        ok(await until(T[victim], "()=>IPLAY.frozen()", 60), f"⑦ 술래 {tcode} 가 잡으면 {victim} 얼음")
        r=await T[victim].evaluate("()=>{ const p=HOUSE.hero().g.position, a=[p.x,p.z]; ISLE.J.x=1; for(let i=0;i<20;i++) ISLE.tick(0.05); ISLE.J.x=0; return Math.hypot(p.x-a[0],p.z-a[1]); }")
        ok(r<0.01, f"⑦ 얼음이면 못 움직임 {r}")
        await tp.evaluate("()=>{ const h=HOUSE.hero(), c=ISLE.SPOT.pgC; h.g.position.set(c[0]+2.6,0,c[1]-1.5); }")
        await T[helper].evaluate("(p)=>{ const h=HOUSE.hero(); h.g.position.set(p[0]-.4,0,p[1]+.3); }", vp)
        ok(await until(T[helper], "()=>document.getElementById('ipQ').classList.contains('on')", 40), "⑦ 얼음 친구 옆 = 단어 문제")
        await T[helper].evaluate("()=>{ const b=document.querySelector('#ipQ .b'), e=b.querySelector('.e').textContent; const w=ISLE_WORDS.find(w=>w[2]===e && [...b.querySelectorAll('[data-w]')].some(x=>x.dataset.w===w[0])); b.querySelector('[data-w=\"'+w[0]+'\"]').click(); }")
        ok(await until(T[victim], "()=>!IPLAY.frozen()", 60), "⑦ 맞히면 얼음 풀림")
        # ⑧ 보물
        r=await A.evaluate("()=>IPLAY.trSpots().length")
        ok(r==10, f"⑧ 오늘 카드 10장 {r}")
        await A.evaluate("()=>{ const o=IPLAY.S.tr.objs[0]; const h=HOUSE.hero(); h.g.position.set(o.x,0,o.z); }")
        ok(await until(A, "()=>Object.keys(IPLAY.S.tr.found).length===1 && document.getElementById('info').classList.contains('on')", 30), "⑧ 카드 줍기 = 단어 카드 창")
        await A.wait_for_timeout(500)
        tr=DB["hy"]["isle"].get("tr",{})
        ok(any(v.get(k)==1 for v in tr.values() for k in v), f"⑧ 주운 수 서버 {tr}")
        await A.evaluate("()=>{ document.getElementById('info').classList.remove('on'); IPLAY.S.tr.goal=1; }")
        g0=await A.evaluate("()=>HOUSE.gems()"); await A.evaluate("()=>{ IPLAY.chestTap(); IPLAY.chestTap(); }"); await until(A, "()=>document.getElementById('info').classList.contains('on')", 40); g1=await A.evaluate("()=>HOUSE.gems()")
        await A.evaluate("()=>{ document.getElementById('info').classList.remove('on'); IPLAY.chestTap(); }"); await until(A, "()=>document.getElementById('info').classList.contains('on')", 40); g2=await A.evaluate("()=>HOUSE.gems()")
        ok(g1-g0==10 and g2==g1, f"⑧ 상자 = 💎+10 한 번만 (두 번 눌러도) {g0}→{g1}→{g2}")
        await A.evaluate("()=>document.getElementById('info').classList.remove('on')")
        # ⑨ 친구 집
        await A.evaluate("()=>HOUSE.publish()"); await A.wait_for_timeout(300)
        await B.evaluate("async ()=>{ await ISLE.loadLots(); ISLE.rebuild(); }")
        r=await B.evaluate("()=>{ const L=ISLE.lots.find(l=>l.owner==='루아'); ISLE.visitLot(L); return !!L; }")
        ok(await until(B, "()=>document.getElementById('ask').classList.contains('on')", 60), "⑨ 친구 집 → 「놀러 갈까요?」")
        await B.evaluate("()=>document.getElementById('askOk').click()")
        ok(await until(B, "()=>['visit','yvisit'].includes(HOUSE.place())", 80), "⑨ 친구 집에 놀러 감")
        await until(B, "()=>!HOUSE.trip().busy", 40)
        await B.evaluate("()=>{ document.getElementById('bVStk').click(); }"); await until(B, "()=>!!document.querySelector('#askT [data-stk]')", 20)
        await B.evaluate("()=>document.querySelector('#askT [data-stk]').click()"); await B.wait_for_timeout(600)
        gb=DB["hy"].get("life",{}).get("gb",{}).get("AAAAA",{})
        ok(len(gb)==1 and list(gb.values())[0]["n"]=="하준", f"⑨ 📮 방명록 스티커 = 친구 집 서버에 {gb}")
        await B.evaluate("()=>document.getElementById('bVLeave').click()")
        ok(await until(B, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 80), "⑨ 나가기 → 다시 🏝 마을")
        r=await B.evaluate("()=>{ const h=HOUSE.hero(), L=ISLE.lots.find(l=>l.owner==='루아'); return [Math.hypot(h.g.position.x-(L.x+ISLE.OX), h.g.position.z-(L.z+ISLE.OZ)), ISLE.blocked(h.cx,h.cz)]; }")
        ok(r[0]<6 and not r[1], f"⑨ 친구 집 앞에서 나옴 {r}")
        r=await A.evaluate("()=>(LBL.find(L=>L.d.k==='tower')||{d:{}}).d.t")
        ok(r is not None, f"⑨ 🗼 타워 이름표 {r}")
        r=await A.evaluate("""()=>{ const h=HOUSE.hero(), run=(jx,jy)=>{ h.g.position.set(ISLE.OX+.5,0,ISLE.OZ+5); yaw=0; yawTo=0; ISLE.CAM.dragAt=0; ISLE.J.x=jx; ISLE.J.y=jy; for(let i=0;i<20;i++) ISLE.tick(0.05); ISLE.J.x=0; ISLE.J.y=0; ISLE.tick(.05); return +yaw.toFixed(3); };
            return [run(.5,-1), run(1,0), run(0,-1)]; }""")
        ok(abs(r[0])>0.15 and r[1]==0 and r[2]==0, f"⑨ 앞+옆 = 카메라가 천천히 따라 돎 · 옆으로만 = 안 돎 (빙글빙글 X) {r}")
        await br.close()
    e=[x for x in real_errs(errs)]
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
