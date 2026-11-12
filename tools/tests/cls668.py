# v668 교실 게임 손보기 — ① 배틀 아이 화면: 긴 글 문제(대화·문장·뜻풀이)가 보기 단추에 안 가림 ② 선생님이 나가면 관리 화면으로 ③ 워드 게이트 레이스 TV: 점수만큼 앞으로 ④ 🎣 낚싯바늘
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
SETQ = """(o)=>{ const q=Battle.q; if(!q) return 'noq'; const T={
   talk:{t:'talk', exq:1, ab:'C', opic:1, w:{en:'band', ko:'밴드', emoji:'🎸'}, tk:{sit:'학교 축제 무대', lines:['Who is playing music on the stage?','The school band. Tom plays the guitar and Mina sings.'], k:1, pre:'The school ', post:'. Tom plays the guitar and Mina sings.'}, opts:[{en:'rock',ko:''},{en:'bank',ko:''},{en:'band',ko:''},{en:'board',ko:''}]},
   sent:{t:'sent', exq:1, ab:'B', opic:1, w:{en:'library', ko:'도서관', emoji:'📚'}, st:{pre:'We borrowed three interesting books from the school ', post:' after lunch yesterday afternoon.', ko:'우리는 어제 오후 점심을 먹고 학교 도서관에서 재미있는 책 세 권을 빌렸다.'}, opts:[{en:'library',ko:''},{en:'laundry',ko:''},{en:'lottery',ko:''},{en:'liberty',ko:''}]},
   sent2:{t:'sent2', exq:1, ab:'C', w:{en:'light', ko:'빛; 가벼운'}, sts:[{pre:'Please turn on the ', post:' because the room is too dark to read.'},{pre:'This bag is very ', post:', so even my little sister can carry it.'}], opts:[{en:'light',ko:''},{en:'right',ko:''},{en:'night',ko:''},{en:'might',ko:''}]},
   def:{t:'def', exq:1, ab:'B', w:{en:'umbrella', ko:'우산'}, d:'a thing that you hold over your head to keep yourself dry when it is raining outside', opts:[{en:'umbrella',ko:''},{en:'raincoat',ko:''},{en:'sunglasses',ko:''},{en:'backpack',ko:''}]},
   e2k:{t:'e2k', exq:0, w:{en:'umbrella', ko:'우산'}, opts:[{en:'umbrella',ko:'우산'},{en:'raincoat',ko:'비옷'},{en:'sunglasses',ko:'선글라스'},{en:'backpack',ko:'배낭'}]} };
  Battle.q=Object.assign({}, q, {done:false, ans:null, lab:null, zap:false, tk:null, st:null, sts:null, d:null, opic:0}, T[o]); Battle.streak=2; document.getElementById('rdB')._pf=null; Battle.draw(); return 'ok'; }"""
MEAS = """()=>{ const S=document.getElementById('scRaid'), Q=S.querySelector('.rdQ'), pr=S.querySelector('.rdPr'), op=S.querySelector('.rdOpts'); if(!pr||!op) return null; const a=pr.getBoundingClientRect(), q=Q.getBoundingClientRect(), pb=parseFloat(getComputedStyle(Q).paddingBottom)||0;
  let top=1e9, bot=-1e9, minF=99; pr.querySelectorAll('*').forEach(e=>{ const r=e.getBoundingClientRect(); if(r.height>0 && getComputedStyle(e).display!=='none'){ top=Math.min(top, r.top); bot=Math.max(bot, r.bottom); } });
  pr.querySelectorAll('.stTalk p span, .stSent, .stDef').forEach(e=>{ let z=1, n=e; while(n && n!==pr.parentNode){ z*=parseFloat(getComputedStyle(n).zoom)||1; n=n.parentNode; } minF=Math.min(minF, parseFloat(getComputedStyle(e).fontSize)*z); });
  const O=[...op.querySelectorAll('.stOpt')].map(x=>x.getBoundingClientRect()), land=innerWidth>innerHeight, pad=S.classList.contains('btPad') && innerWidth>=700 && innerHeight>=700;
  const side = pad && land;   // 가로 패드 = 글 왼쪽 · 보기 오른쪽
  const lap = side ? (bot>q.bottom-pb+2 || top<a.top-2 || O.some(r=>r.left<a.right-2)) : (bot>Math.min(...O.map(r=>r.top))+1);
  return {pad, side, lap, cut:Math.max(...O.map(r=>r.bottom))>q.bottom+1 || bot>q.bottom+1, optH:Math.round(Math.min(...O.map(r=>r.height))), f:Math.round(minF*10)/10, over:S.scrollHeight-S.clientHeight, tight:S.classList.contains('btTight'), txt:Q.classList.contains('txt')}; }"""
async def join(ctx, room, nm, vp, i):
    k = await ctx.new_page(); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
    await k.evaluate(f"()=>{{ const k0=Kid.k.bind(Kid); Kid.k=b=>k0(b)+'@t{i}'; RaidJoin.open(); }}"); await k.wait_for_timeout(100)
    await k.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='{nm}'; document.querySelector('[data-rj=go]').click(); }}"); await k.wait_for_timeout(450); return k
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 1920, "height": 1080}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e)[:200])); await boot(H)
        await H.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }"); await H.reload(); await H.wait_for_timeout(1500)
        await H.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Online.on=()=>false; window.confirm=()=>true; }")
        ok(await H.evaluate("()=>Admin.isOn()") is True, "선생님 기기(관리 화면 열쇠 있음)")
        # ① 배틀 아이 화면 — 긴 글 문제
        room = await H.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:300, team:false, lbl:'유치원 단모음 Stage 1-1~7-1'})")
        VP = [("가로 패드", (1180, 820)), ("가로 아이패드", (1024, 768)), ("가로 아이패드(주소창)", (1080, 730)), ("세로 패드", (820, 1180)), ("세로 아이패드", (768, 1024)), ("세로 아이패드(주소창)", (810, 1010)), ("휴대폰", (390, 844)), ("작은 휴대폰", (375, 667)), ("가로 휴대폰", (915, 412))]
        K = [await join(ctx, room, "아이%d" % i, vp, i) for i, (nm, vp) in enumerate(VP)]
        for k in K: k.on("pageerror", lambda e: errs.append("K " + str(e)[:200]))
        await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_function("()=>Battle.st().s==='run' && Battle.left()>0", timeout=12000); await H.wait_for_timeout(900)
        for (nm, vp), k in zip(VP, K):
            await k.wait_for_function("()=>Battle.q && !Battle.q.done", timeout=9000)
            for t in ("talk", "sent", "sent2", "def"):
                await k.evaluate(SETQ, t); await k.wait_for_timeout(350); m = await k.evaluate(MEAS)
                ok(m and m["txt"] and not m["lap"] and not m["cut"] and m["over"] <= 1 and m["optH"] >= 52 and m["f"] >= 13.5, f"① {nm} {t}: 글이 보기에 안 가리고 칸 안 · 스크롤 없음 · 글자 {m and m['f']}px · 보기 {m and m['optH']}px {m}")
            await k.evaluate(SETQ, "e2k"); await k.wait_for_timeout(300); m = await k.evaluate(MEAS)
            ok(m and not m["txt"] and not m["tight"] and m["over"] <= 1, f"① {nm}: 낱말 문제는 그대로 (띠 안 줄임) {m}")
            if nm in ("가로 패드", "세로 아이패드"): await k.evaluate(SETQ, "talk"); await k.wait_for_timeout(300); await k.screenshot(path=OUT + "cls668_talk_%s.png" % ("land" if nm == "가로 패드" else "port"))
        # ② 나가기 — 아이는 오늘의 30 · 선생님은 관리 화면
        await K[6].evaluate("()=>{ window.confirm=()=>true; Battle.leave(); }"); await K[6].wait_for_timeout(500)
        r = await K[6].evaluate("()=>[document.getElementById('scStudy').classList.contains('on') || !!document.getElementById('kidPick') || !!document.querySelector('.kidAsk, #kidAsk'), document.getElementById('shAdmin').classList.contains('on')]")
        ok(r[1] is False, f"② 아이가 나가면 관리 화면 아님 (오늘의 30 쪽) {r}")
        await H.evaluate("()=>Battle.hostAct('end')"); await H.wait_for_timeout(1200); await H.evaluate("()=>Battle.leave()"); await H.wait_for_timeout(700)
        r = await H.evaluate("()=>[document.getElementById('shAdmin').classList.contains('on'), document.getElementById('scStart').classList.contains('on'), document.getElementById('scStudy').classList.contains('on'), document.getElementById('scRaid').classList.contains('on')]")
        ok(r == [True, True, False, False], f"② 선생님이 배틀에서 나가면 관리 화면 (오늘의 30·이름 고르기 아님) {r}")
        await H.evaluate("()=>{ document.getElementById('shAdmin').classList.remove('on'); }")
        await H.evaluate("()=>Raid.host('g34', [], 0, null, 900, 'all')"); await H.wait_for_timeout(1500)
        hosted = await H.evaluate("()=>Raid.role")
        await H.evaluate("()=>Raid.leave()"); await H.wait_for_timeout(700)
        r = await H.evaluate("()=>[document.getElementById('shAdmin').classList.contains('on'), document.getElementById('scStudy').classList.contains('on')]")
        ok(hosted == "host" and r == [True, False], f"② 선생님이 레이드에서 나가도 관리 화면 {hosted} {r}")
        await ctx.close()
        # ③ 워드 게이트 레이스 TV — 점수만큼 앞으로 (시간 없는 판 · 긴 판 · 짧은 판)
        SEED = """([room,S])=>{ const N=['경훈','라언','주호','단우'], CH=['mage','ghost','knight','knight'], P={}; S.forEach((sc,i)=>{ P['k'+i]={n:N[i], c:CH[i], sc, ok:0, ng:0, at:Date.now()}; }); return FB.update('/battle/'+room+'/p', JSON.parse(JSON.stringify(P))); }"""
        for nm, dur in (("끝낼 때까지", 3600), ("10분", 600), ("2분", 120)):
            c2 = await br.new_context(viewport={"width": 1920, "height": 1080}, service_workers="block"); await c2.add_init_script("window.HY_FB_LOCAL=true;")
            T = await c2.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e)[:200])); await boot(T)
            room = await T.evaluate("(d)=>Battle.host({kind:'run', rset:'elem', diff:'normal', dur:d, mode:'score', set:'elem', words:[], lbl:'달리기'})", dur)
            await T.wait_for_timeout(500); await T.evaluate(SEED, [room, [0, 0, 0, 0]]); await T.wait_for_timeout(600)
            await T.evaluate("()=>Battle.hostAct('start')")
            try: await T.wait_for_function("()=>!!document.getElementById('frun') && Battle.st().s==='run'", timeout=25000)
            except Exception: pass
            await T.wait_for_timeout(1200)
            await T.evaluate(SEED, [room, [528, 528, 363, 187]])
            try: await T.wait_for_function("()=>FlagRun.o && FlagRun.o.L.length===4 && Math.max(...FlagRun.o.L.map(t=>t.p))>5.4", timeout=25000)   # 다른 검사와 같이 돌 때도 (느린 기기) 자리가 잡힐 때까지
            except Exception: pass
            await T.wait_for_timeout(1500)
            r = await T.evaluate("()=>{ const L=FlagRun.o.L, by=n=>L.find(t=>t.n===n).p; const S=document.getElementById('frStage').getBoundingClientRect(), x=n=>{ const t=L.find(t=>t.n===n), e=document.getElementById('frR'+t.k).getBoundingClientRect(); return Math.round((e.left-S.left)/S.width*100); }; return {p:['경훈','라언','주호','단우'].map(n=>Math.round(by(n)*10)/10), x:['경훈','단우'].map(x), tm:document.getElementById('frTime').textContent}; }")
            lead = 8.5 if dur >= 3600 else 6.0
            ok(abs(r["p"][0] - lead) < 0.6 and abs(r["p"][1] - lead) < 0.6 and r["p"][0] > r["p"][2] > r["p"][3] > 1.5 and r["x"][0] - r["x"][1] >= 25, f"③ {nm}: 528·528·363·187점 → 자리 {r['p']} (전에는 모두 0.2 = 출발선) · 화면 {r['x']}%")
            ok(("끝낼 때까지" in r["tm"]) if dur >= 3600 else ("⏱" in r["tm"]), f"③ {nm}: 시계 「{r['tm']}」")
            if dur >= 3600: await T.screenshot(path=OUT + "cls668_race.png")
            await c2.close()
        # ④ 🎣 단어 낚시 — 바늘이 물고기를 낚음
        pg = await br.new_page(viewport={"width": 1180, "height": 820}); pg.on("pageerror", lambda e: errs.append("F " + str(e)[:200])); await boot(pg)
        await pg.evaluate("""()=>{ const c={set:'elem',from:0,to:3,words:[],qt:['mean']}, x=Object.create(Battle); x._ws=null; x.cfg=()=>c; const P=[{n:'루아',ch:0},{n:'주호',ch:3}].map((p,i)=>Object.assign(p,{i,col:Board.COL[i]})); MG.open({title:MiniG.L.fish[0], sub:MiniG.L.fish[1], P, ctx:x, kind:'fish', sec:30}, sc=>window._r=sc); }""")
        await pg.wait_for_function("()=>!document.querySelector('.mgIntro') && MG.o && MG.o.inst && MG.o.inst.length===2", timeout=15000); await pg.wait_for_timeout(1200)
        HK = "()=>{ const g=MG.o.inst[0], h=g.Hk, F=g.F.getBoundingClientRect(), r=h.getBoundingClientRect(); return {cls:h.className, left:h.style.left, hgt:h.style.height, h:Math.round(r.height), bg:getComputedStyle(h.querySelector('b')).backgroundImage.includes('fi_hook'), before:getComputedStyle(g.F, '::before').content, an:getComputedStyle(h).animationName, sc:g.sc, hooked:g.F.querySelectorAll('.mgFi.hooked').length}; }"
        a = await pg.evaluate(HK)
        ok("idle" in a["cls"] and a["bg"] and a["an"] == "hkBob" and a["h"] >= 80 and a["before"] in ("none", "normal"), f"④ 바늘: 줄에 매달려 까딱까딱 (구석에 박힌 그림 없음) {a}")
        await pg.evaluate("()=>MG.o.inst[0].auto()"); await pg.wait_for_timeout(90); b = await pg.evaluate(HK)
        ok("idle" not in b["cls"] and b["left"] and b["hgt"] and b["sc"] == a["sc"] + 1, f"④ 맞는 물고기를 누르면 바늘이 그 자리로 · 점수 +1 {b}")
        await pg.wait_for_timeout(240); c = await pg.evaluate(HK); ok("reel" in c["cls"] and c["hgt"] == "0%" and c["hooked"] == 1, f"④ 물고기를 낚아 올림 {c}")
        await pg.wait_for_timeout(900); d = await pg.evaluate(HK); ok("idle" in d["cls"] and d["hooked"] == 0, f"④ 다시 제자리에서 까딱 {d}")
        await pg.evaluate("()=>MG.o.inst[0].wrong()"); await pg.wait_for_timeout(260); e = await pg.evaluate(HK)
        ok("miss" in e["cls"] and e["sc"] == d["sc"] and e["hooked"] == 0, f"④ 틀린 물고기 = 헛챔질 (점수 그대로) {e}")
        await pg.screenshot(path=OUT + "cls668_fish.png"); await pg.close()
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await br.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
