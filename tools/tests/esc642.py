# v642 🔐 영어 방탈출 2.0 — 방 3개 × (자물쇠 3 + 🚪 문) = 12 · 단서는 방 안 물건 속(팀원마다 다른 곳) · 📝 문장 자물쇠 · 틀리면 20초 잠김 · 💡 힌트 벌점 · 팀 순위 · 보석
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/esc642_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

GEN = """async (set)=>{ await Duel.ready(); const L=Study.lessons(set); const p=Esc.make({set, from:0, to:Math.min(4, L.length-1)}); const Z=p.Z, A=p.A;
  const doors=[0,1,2].map(r=>({door:A[r*4+3], got:p.got.slice(r*4, r*4+3).map(g=>g.join('')).join(''), fin:!!Z[r*4+3].fin, rr:Z.slice(r*4,r*4+4).every(z=>z.r===r)}));
  const bad=[]; Z.forEach((z,i)=>{ const a=A[i]; if(!a) bad.push(i+':빈 답');
    if(z.k==='code' && !new RegExp('^\\\\d{'+z.n+'}$').test(a)) bad.push(i+':번호 '+a);
    if(z.k==='word' && !z.fin && z.tiles && !a.split('').every(c=>z.tiles.indexOf(c)>=0)) bad.push(i+':글자판 '+a);
    if(z.k==='ord' && !a.split(' ').every(w=>z.tiles.indexOf(w)>=0)) bad.push(i+':문장 '+a);
    if(z.k==='first' && a.length!==z.n) bad.push(i+':첫 글자 '+a);
    if(!z.fin && (z.pc||[]).length<3) bad.push(i+':단서 '+z.pc.length); });
  return {n:Z.length, ks:Z.map(z=>z.fin?'fin':z.say?'say':z.kb&&z.k==='word'?'kb':z.k).join(','), ans:A, doors, bad, ord:(Z.find(z=>z.k==='ord')||{}).pc, uniq:new Set(A).size}; }"""

SEND = "(v)=>{ const z=EscPad.z(); if(z && z.k==='ord'){ EscPad.iw=[]; EscPad.iwI=[]; const K=[...document.querySelectorAll('#escPad .epKeys.wd button')]; v.split(' ').forEach(w=>{ const b=K.find(b=>b.dataset.v===w && !b.disabled && EscPad.iwI.indexOf(+b.dataset.i)<0); if(b) b.click(); }); } else EscPad.inp=v; EscPad.send(); }"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # ① 문제 만들기 — 학년마다
        pg = await b.new_page(); await boot(pg)
        for st in ("basic", "elem", "g56", "mv1"):
            try: r = await pg.evaluate(GEN, st)
            except Exception as e: ok(False, f"{st} 만들기 오류 {str(e)[:120]}"); continue
            want = "word,code,first,fin,kb,say,word,fin," + ("first,code,kb,fin" if st == "basic" else "ord,code,kb,fin")
            ok(r["n"] == 12 and (r["ks"] == want or (st != "basic" and r["ks"] == want.replace("ord", "first"))) and not r["bad"] and r["uniq"] == 12, f"{st}: 방 3 × 4 = 12 · 종류 {r['ks']} · 문제 없음 {r['bad']}")
            ok(all(d["fin"] and d["rr"] and sorted(d["got"]) == sorted(d["door"]) for d in r["doors"]), f"{st}: 방마다 자물쇠 3개 글자 = 문 단어 {[(d['door'], d['got']) for d in r['doors']]}")
            if st != "basic": ok(r["ord"] is not None and "뜻 =" in r["ord"][0], f"{st}: 📝 문장 자물쇠 {r['ord']}")
        r = await pg.evaluate("""()=>{ const z={k:'word', pc:['a','b','c']}; return [Esc.mine(z,['x'],'x').length, Esc.mine(z,['x','y'],'x').length+Esc.mine(z,['x','y'],'y').length, Esc.mine(z,['x','y','w'],'w'), Esc.mine(z,['a','b','c','d'],'d').length, Esc.hint({k:'code'},'731',0), Esc.hint({k:'word'},'apple',1), Esc.hint({k:'ord'},'I like red apples',1), Esc.hide(3,'a|1|9').length, JSON.stringify(Esc.hide(3,'a|1|9'))===JSON.stringify(Esc.hide(3,'a|1|9')), JSON.stringify(Esc.hide(3,'a|1|9'))!==JSON.stringify(Esc.hide(3,'b|1|9'))||JSON.stringify(Esc.hide(3,'a|1|9'))!==JSON.stringify(Esc.hide(3,'c|1|9'))]; }""")
        ok(r[0] == 3 and r[1] == 3 and r[2] == ["c"] and r[3] >= 1 and "7" in r[4] and "A P" in r[5] and "I like" in r[6] and r[7] == 3 and r[8] and r[9], f"단서 나누기 · 힌트 · 숨김 자리 {r}")
        await pg.close()
        # ② 수업판 — TV + 패드 4대 (2팀)
        ctx = await b.new_context(viewport={"width": 1920, "height": 1080})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); errs = []; tv.on("pageerror", lambda e: errs.append("tv " + str(e))); await boot(tv)
        await tv.evaluate("()=>{ EscTV.setup(); }"); await tv.wait_for_timeout(400)
        ok(await tv.evaluate("()=>!!document.getElementById('escSet') && document.querySelectorAll('#escBk option').length>3"), "설정 창 (책 · Stage · 시간)")
        await tv.screenshot(path=OUT + "setup.png")
        await tv.evaluate("()=>{ document.getElementById('escBk').value='elem'; document.getElementById('escBk').onchange(); document.querySelector('[data-dur=\"15\"]').click(); document.querySelector('[data-es=go]').click(); }")
        await tv.wait_for_function("()=>EscTV.room && /^\\d{4}$/.test(EscTV.room)", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        ok(await tv.evaluate("()=>EscTV.cfg.dur===15 && EscTV.cfg.set==='elem'"), f"방 만들기 {room}")
        kids = []
        for i, (nm, vp) in enumerate((("가온", (820, 1180)), ("나래", (390, 844)), ("다솜", (915, 412)), ("라온", (1180, 820)))):
            k = await ctx.new_page(); k.on("pageerror", lambda e, nm=nm: errs.append(nm + " " + str(e))); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate("(a)=>{ Wallet.addGems(0); EscPad.join(a[0], {id:'k'+a[1], n:a[2]}); }", [room, i, nm]); kids.append(k); await k.wait_for_timeout(300)
        await tv.wait_for_timeout(800)
        r = await tv.evaluate("()=>[EscTV.kids().length, EscTV.teamN(), document.querySelector('.escRoom > b').textContent]")
        ok(r[0] == 4 and r[1] == 1 and r[2] == room, f"TV 대기실 = 4명 · 4명이면 다 같이 {r}")
        await tv.screenshot(path=OUT + "lobby_tv.png")
        await tv.evaluate("()=>{ document.querySelector('[data-et=nt][data-n=\"2\"]').click(); }"); await tv.wait_for_timeout(200)
        await tv.evaluate("()=>document.querySelector('[data-et=go]').click()"); await tv.wait_for_function("()=>EscTV.st && EscTV.st.s==='run'", timeout=10000); await tv.wait_for_timeout(800)
        S = await tv.evaluate("()=>({M:EscTV.st.M, A:EscTV.st.A, ans:EscTV.ans})")
        ok(len(S["M"]["0"]) == 2 and len(S["M"]["1"]) == 2 and S["ans"]["0"][0] != S["ans"]["1"][0], f"2팀 · 팀마다 다른 문제 {S['M']} {S['ans']['0'][0]}/{S['ans']['1'][0]}")
        kid = {f"k{i}": kids[i] for i in range(4)}
        t0m = [kid[x] for x in S["M"]["0"]]; t1m = [kid[x] for x in S["M"]["1"]]
        # 단서는 물건 속에 — 처음엔 안 보임 · 물건 6개 다 뒤지면 내 단서 · 두 팀원 합치면 3조각
        c0 = await t0m[0].evaluate("()=>[document.querySelectorAll('#escPad .epClue').length, document.querySelectorAll('#escPad .epObj button').length]")
        ok(c0 == [0, 6], f"처음엔 단서 안 보임 · 물건 6개 {c0}")
        await t0m[0].screenshot(path=OUT + "pad_search.png")
        for m in t0m:
            for i in range(6):
                await m.evaluate("(i)=>EscPad.look(i)", i); await m.wait_for_timeout(760)
        c = [await m.evaluate("()=>({c:[...document.querySelectorAll('#escPad .epClue')].map(x=>x.textContent), hit:document.querySelectorAll('#escPad .epObj .hit').length, nil:document.querySelectorAll('#escPad .epObj .nil').length})") for m in t0m]
        ok(len(c[0]["c"]) < 3 and len(set(c[0]["c"]) | set(c[1]["c"])) == 3 and c[0]["hit"] == len(c[0]["c"]) and c[0]["hit"] + c[0]["nil"] == 6, f"물건 뒤져 단서 나눠 받기 {c}")
        await t0m[0].screenshot(path=OUT + "pad_lock1.png")
        # 시작 전 4초 준비 → 기다림
        await tv.wait_for_timeout(4200)
        # 틀림 → 20초 잠김 + 벌점 10초 · 다른 팀원도 잠김
        await t0m[0].evaluate("()=>{ EscPad.inp='zzzz'; EscPad.send(); }"); await tv.wait_for_timeout(900)
        r = await tv.evaluate("()=>{ const T=EscTV.st.T[0]; return [T.lk, T.w, T.pen, T.fz-EscTV.now()]; }")
        ok(r[0] == 0 and r[1] == 1 and r[2] == 10000 and 15000 < r[3] <= 20000, f"틀림 → 20초 잠김 · 벌점 10초 {r}")
        r = await t0m[1].evaluate("()=>{ EscPad.drawFz(); return [!document.getElementById('epFz').hidden, document.getElementById('epSend').disabled]; }")
        ok(r == [True, True], f"팀원 패드도 잠김 {r}")
        await t0m[1].screenshot(path=OUT + "pad_frozen.png")
        # 잠긴 동안 낸 답은 안 받음
        a0 = S["ans"]["0"]
        await t0m[1].evaluate(SEND, a0[0]); await tv.wait_for_timeout(700)
        ok(await tv.evaluate("()=>EscTV.st.T[0].lk") == 0, "잠긴 동안 정답을 내도 안 열림")
        # 💡 힌트 → 팀 패드에 · 벌점 45초 · 2번까지
        await tv.evaluate("()=>{ EscTV.st.T[0].fz=0; EscTV.push(); }"); await tv.wait_for_timeout(400)
        await t0m[0].evaluate("()=>{ window.confirm=()=>true; document.querySelector('[data-ep=hint]').click(); }"); await tv.wait_for_timeout(800)
        h = await t0m[1].evaluate("()=>[...document.querySelectorAll('.epClue.hint')].map(x=>x.textContent)")
        pen = await tv.evaluate("()=>EscTV.st.T[0].pen")
        ok(len(h) == 1 and a0[0][0].upper() in h[0] and pen == 55000, f"힌트 = 팀원 패드에도 · 벌점 +45초 {h} {pen}")
        # 정답으로 자물쇠 12개 (팀 0) — 다른 팀원이 번갈아 · 방마다 문 글자 다 모이면 문
        for i in range(12):
            m = t0m[i % 2]
            v = a0[i]
            if i % 4 == 3:
                fl = await tv.evaluate("()=>EscTV.st.T[0].fl")
                ok(sorted(fl) == sorted(v), f"방 {i//4+1}: 자물쇠 3개 = 문 글자 다 모임 {fl} / {v}")
                if i == 3: await m.screenshot(path=OUT + "pad_door.png"); await tv.screenshot(path=OUT + "tv_run.png")
            await m.evaluate(SEND, v); await tv.wait_for_timeout(700)
            lk = await tv.evaluate("()=>EscTV.st.T[0].lk")
            if i == 4: await m.screenshot(path=OUT + "pad_room2.png")
            if i == 8: await m.screenshot(path=OUT + "pad_ord.png")
            ok(lk == i + 1, f"자물쇠 {i+1} 열림 ({v})")
            if i == 3: ok(await tv.evaluate("()=>EscTV.st.T[0].fl") == "", "문 열면 다음 방 = 글자 처음부터")
        r = await tv.evaluate("()=>{ const T=EscTV.st.T[0]; return [!!T.out, T.rk, EscTV.st.s]; }")
        ok(r == [True, 1, "run"], f"팀 0 탈출 1등 · 다른 팀은 계속 {r}")
        await t0m[0].wait_for_timeout(500)
        r = await t0m[0].evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, (document.querySelector('#escPad .stGem')||{}).textContent||'']")
        ok("탈출 성공" in r[0] and "1등" in r[0] and "+9" in r[1], f"패드 탈출 화면 · 💎6+3 {r}")
        # 팀 1 = 자물쇠 5개(문 하나) → 끝내기
        a1 = S["ans"]["1"]
        for i in range(5):
            await t1m[0].evaluate(SEND, a1[i]); await tv.wait_for_timeout(600)
        await tv.evaluate("()=>{ window.confirm=()=>true; document.querySelector('[data-et=end]').click(); }"); await tv.wait_for_timeout(900)
        r = await tv.evaluate("()=>[EscTV.st.s, EscTV.st.ord, EscTV.st.T[1].lk, document.querySelector('.escRank').textContent]")
        ok(r[0] == "end" and r[1] == ["0", "1"] and r[2] == 5 and "1등" in r[3], f"끝 · 순위 {r}")
        await tv.screenshot(path=OUT + "tv_end.png")
        r = await t1m[0].evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, (document.querySelector('#escPad .stGem')||{}).textContent||'']")
        ok("시간" in r[0] and "+2" in r[1], f"못 나간 팀 (문 하나) = 💎2 {r}")
        # 패드 화면 넘침 · 가로 휴대폰 「열기」 버튼 화면 안
        for nm, m in (("pad", kids[0]), ("ph", kids[1]), ("phL", kids[2]), ("padL", kids[3])):
            w = await m.evaluate("()=>document.documentElement.scrollWidth-innerWidth")
            ok(w <= 0, f"{nm} 가로 넘침 없음 {w}")
        e = [x for x in errs if "favicon" not in x]; ok(not e, f"오류 없음 {e[:3]}")
        await ctx.close()
        # ③ 패드 문제 화면 — 가로 휴대폰에서 「🔑 열기」·글자판이 화면 안 (스크롤 없이)
        ctx = await b.new_context(viewport={"width": 1280, "height": 800}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); await boot(tv)
        await tv.evaluate("()=>EscTV.host({set:'elem', from:0, to:4, dur:15})"); await tv.wait_for_function("()=>EscTV.room", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        pads = []
        for nm, vp in (("phL", (915, 412)), ("ph", (390, 844)), ("pad", (820, 1180))):
            k = await ctx.new_page(); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate("(a)=>EscPad.join(a[0], {id:a[1], n:a[1]})", [room, nm]); pads.append((nm, k))
        await tv.wait_for_timeout(700); await tv.evaluate("async ()=>{ EscTV.nT=1; await EscTV.go(); }"); await tv.wait_for_timeout(5000)
        for lk in range(12):
            for nm, k in pads:
                if lk in (0, 8): await k.evaluate("async ()=>{ for(let i=0;i<6;i++){ EscPad.look(i); await new Promise(z=>setTimeout(z,720)); } }")
                r = await k.evaluate("""()=>{ const s=document.getElementById('epSend').getBoundingClientRect(), ks=[...document.querySelectorAll('.epKeys button')].map(b=>b.getBoundingClientRect().bottom); const P=document.getElementById('escPad'); return [Math.round(s.bottom), Math.round(Math.max(...ks)), innerHeight, P.scrollHeight-P.clientHeight]; }""")
                ok(r[0] <= r[2] and r[1] <= r[2], f"{nm} 자물쇠 {lk+1}: 열기·글자판 화면 안 {r}")
                if lk in (0, 3, 5, 8): await k.screenshot(path=f"{OUT}pad{lk}_{nm}.png")
            v = await tv.evaluate("(i)=>EscTV.ans[0][i]", lk)
            await pads[0][1].evaluate(SEND, v); await tv.wait_for_timeout(700)
        await ctx.close()
        # ③-2 중등 = 긴 문장(12단어까지) 📝 문장 자물쇠도 화면 안
        ctx = await b.new_context(viewport={"width": 1280, "height": 800}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); await boot(tv)
        await tv.evaluate("()=>EscTV.host({set:'mv1', from:0, to:4, dur:20})"); await tv.wait_for_function("()=>EscTV.room", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        pads = []
        for nm, vp in (("phL", (915, 412)), ("ph", (390, 844)), ("pad", (820, 1180)), ("padL", (1180, 820))):
            k = await ctx.new_page(); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate("(a)=>EscPad.join(a[0], {id:a[1], n:a[1]})", [room, nm]); pads.append((nm, k))
        await tv.wait_for_timeout(700); await tv.evaluate("async ()=>{ EscTV.nT=1; await EscTV.go(); }"); await tv.wait_for_timeout(4500)
        L = await tv.evaluate("()=>{ const Z=EscTV.st.Z[0]; const i=Z.findIndex(z=>z.k==='ord'); const n=Z[i].n; EscTV.st.T[0].lk=i; EscTV.push(); return [i, n]; }"); await tv.wait_for_timeout(700)
        for nm, k in pads:
            await k.evaluate("async ()=>{ for(let i=0;i<6;i++){ EscPad.look(i); await new Promise(z=>setTimeout(z,720)); } }")
            await k.evaluate(SEND.replace("EscPad.send();", ""), await tv.evaluate("(i)=>EscTV.ans[0][i]", L[0]))
            await k.evaluate("()=>EscPad.drawIn()")
            r = await k.evaluate("""()=>{ const s=document.getElementById('epSend').getBoundingClientRect(), ks=[...document.querySelectorAll('.epKeys button')].map(b=>b.getBoundingClientRect()), P=document.getElementById('escPad');
                return [Math.round(s.bottom), Math.round(Math.max(...ks.map(r=>r.bottom))), innerHeight, P.scrollHeight-P.clientHeight, Math.round(Math.max(...ks.map(r=>r.right))), innerWidth, document.getElementById('epIn').getBoundingClientRect().bottom<=innerHeight]; }""")
            ok(r[0] <= r[2] and r[1] <= r[2] and r[3] <= 0 and r[4] <= r[5] and r[6], f"{nm} 중등 📝 문장 {L[1]}단어: 화면 안 {r}")
            await k.screenshot(path=f"{OUT}mid_ord_{nm}.png")
        await ctx.close()
        # ④ 🎮 수업 게임 번호로 들어가면 방탈출 패드
        ctx = await b.new_context(viewport={"width": 820, "height": 1180}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); await boot(tv)
        await tv.evaluate("()=>EscTV.host({set:'basic', from:0, to:3, dur:10})"); await tv.wait_for_function("()=>EscTV.room", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        k = await ctx.new_page(); await boot(k)
        await k.evaluate("()=>RaidJoin.open()"); await k.wait_for_timeout(500)
        await k.evaluate("(r)=>{ const ni=document.getElementById('rdNameIn'); if(ni) ni.value='마루'; else RaidJoin.pick={id:'maru', n:'마루', t:''}; document.getElementById('rdRoomIn').value=r; document.querySelector('[data-rj=go]').click(); }", room)
        await k.wait_for_timeout(2000)
        ok(await k.evaluate("()=>!!document.getElementById('escPad')"), "🎮 수업 게임 → 방 번호 → 방탈출 패드")
        await ctx.close()
        # ⑤ 관리자 「지금 수업」 탭에 🔐 방탈출 단추
        pg = await b.new_page(); await boot(pg)
        r = await pg.evaluate("()=>document.querySelector('#scStart') && typeof EscTV.setup")
        ok(r == "function", "EscTV 준비")
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
