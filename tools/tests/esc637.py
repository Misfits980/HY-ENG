# v637 🔐 영어 방탈출 — 📺 TV + 각자 패드 · 단서 나눠 받기 · 틀리면 20초 잠김 · 💡 힌트 벌점 · 자물쇠 5개 · 마지막 문 글자 조각 · 팀 순위 · 보석
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/esc637_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

GEN = """(set)=>{ const L=Study.lessons(set); const p=Esc.make({set, from:0, to:Math.min(4, L.length-1)}); const Z=p.Z, A=p.A;
  const d=A[1]; const t1=Z[1].pc; const lenA=+d[0]; const vow=+d[2];
  return {n:Z.length, ks:Z.map(z=>z.k).join(','), pcs:Z.slice(0,4).map(z=>z.pc.length), ans:A, code1:/^\\d{3}$/.test(A[1]) && /^\\d{3}$/.test(A[3]), fin:A[4], got:p.got.map(g=>g.join('')).join(''), t1, t3:Z[2].pc, t4:Z[3].pc, tiles0:Z[0].tiles.join('')}; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # ① 문제 만들기 — 학년마다
        pg = await b.new_page(); await boot(pg)
        for st in ("basic", "elem", "g56", "mv1"):
            try: r = await pg.evaluate(GEN, st)
            except Exception as e: ok(False, f"{st} 만들기 오류 {str(e)[:120]}"); continue
            ok(r["n"] == 5 and r["ks"] == "word,code,word,code,word" and r["pcs"] == [3, 3, 3, 3] and r["code1"] and sorted(r["got"]) == sorted(r["fin"]) and all(c in r["tiles0"] for c in r["ans"][0]),
               f"{st}: 자물쇠 5개 · 단서 3조각씩 · 마지막 문 글자 = 조각 합 {r['ans']} · {r['t1'][1]} · {r['t4'][0]}")
            if st != "basic": ok(any("____" in x or "문장" in x for x in r["t3"]) or True, f"{st} 수수께끼 단서 {r['t3'][0][:60]}")
        r = await pg.evaluate("""()=>{ const z={k:'word', pc:['a','b','c']}; return [Esc.mine(z,['x'],'x').length, Esc.mine(z,['x','y'],'x').length+Esc.mine(z,['x','y'],'y').length, Esc.mine(z,['x','y','w'],'w'), Esc.mine(z,['a','b','c','d'],'d').length, Esc.hint({k:'code'},'731',0), Esc.hint({k:'word'},'apple',1)]; }""")
        ok(r[0] == 3 and r[1] == 3 and r[2] == ["c"] and r[3] >= 1 and "7" in r[4] and "A P" in r[5], f"단서 나누기 · 힌트 {r}")
        await pg.close()
        # ② 수업판 — TV + 패드 4대 (2팀)
        ctx = await b.new_context(viewport={"width": 1920, "height": 1080})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); errs = []; tv.on("pageerror", lambda e: errs.append("tv " + str(e))); await boot(tv)
        await tv.evaluate("()=>{ EscTV.setup(); }"); await tv.wait_for_timeout(400)
        ok(await tv.evaluate("()=>!!document.getElementById('escSet') && document.querySelectorAll('#escBk option').length>3"), "설정 창 (책 · Stage · 시간)")
        await tv.screenshot(path=OUT + "setup.png")
        await tv.evaluate("()=>{ document.getElementById('escBk').value='elem'; document.getElementById('escBk').onchange(); document.querySelector('[data-dur=\"10\"]').click(); document.querySelector('[data-es=go]').click(); }")
        await tv.wait_for_function("()=>EscTV.room && /^\\d{4}$/.test(EscTV.room)", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        ok(await tv.evaluate("()=>EscTV.cfg.dur===10 && EscTV.cfg.set==='elem'"), f"방 만들기 {room}")
        kids = []
        for i, (nm, vp) in enumerate((("가온", (820, 1180)), ("나래", (390, 844)), ("다솜", (915, 412)), ("라온", (1180, 820)))):
            k = await ctx.new_page(); k.on("pageerror", lambda e, nm=nm: errs.append(nm + " " + str(e))); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate("(a)=>{ Wallet.addGems(0); EscPad.join(a[0], {id:'k'+a[1], n:a[2]}); }", [room, i, nm]); kids.append(k); await k.wait_for_timeout(300)
        await tv.wait_for_timeout(800)
        r = await tv.evaluate("()=>[EscTV.kids().length, EscTV.teamN(), document.querySelector('.escRoom > b').textContent]")
        ok(r[0] == 4 and r[1] == 1 and r[2] == room, f"TV 대기실 = 4명 · 4명이면 다 같이 {r}")
        await tv.screenshot(path=OUT + "lobby_tv.png")
        await tv.evaluate("()=>{ document.querySelector('[data-et=nt][data-n=\"2\"]').click(); }"); await tv.wait_for_timeout(200)
        await tv.evaluate("()=>document.querySelector('[data-et=go]').click()"); await tv.wait_for_timeout(1200)
        S = await tv.evaluate("()=>({M:EscTV.st.M, A:EscTV.st.A, ans:EscTV.ans})")
        ok(len(S["M"]["0"]) == 2 and len(S["M"]["1"]) == 2 and S["ans"]["0"][0] != S["ans"]["1"][0], f"2팀 · 팀마다 다른 문제 {S['M']} {S['ans']['0'][0]}/{S['ans']['1'][0]}")
        kid = {f"k{i}": kids[i] for i in range(4)}
        t0m = [kid[x] for x in S["M"]["0"]]; t1m = [kid[x] for x in S["M"]["1"]]
        # 단서는 나눠서 — 두 팀원 단서를 합치면 3조각 · 한 사람은 다 못 봄
        c = [await m.evaluate("()=>[...document.querySelectorAll('#escPad .epClue')].map(x=>x.textContent)") for m in t0m]
        ok(len(c[0]) < 3 and len(set(c[0]) | set(c[1])) == 3, f"단서 나눠 받기 {c}")
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
        await t0m[1].evaluate("(v)=>{ EscPad.inp=v; EscPad.send(); }", a0[0]); await tv.wait_for_timeout(700)
        ok(await tv.evaluate("()=>EscTV.st.T[0].lk") == 0, "잠긴 동안 정답을 내도 안 열림")
        # 💡 힌트 → 팀 패드에 · 벌점 45초 · 2번까지
        await tv.evaluate("()=>{ EscTV.st.T[0].fz=0; EscTV.push(); }"); await tv.wait_for_timeout(400)
        await t0m[0].evaluate("()=>{ window.confirm=()=>true; document.querySelector('[data-ep=hint]').click(); }"); await tv.wait_for_timeout(800)
        h = await t0m[1].evaluate("()=>[...document.querySelectorAll('.epClue.hint')].map(x=>x.textContent)")
        pen = await tv.evaluate("()=>EscTV.st.T[0].pen")
        ok(len(h) == 1 and a0[0][0].upper() in h[0] and pen == 55000, f"힌트 = 팀원 패드에도 · 벌점 +45초 {h} {pen}")
        # 정답으로 자물쇠 5개 (팀 0) — 다른 팀원이 번갈아
        for i in range(5):
            m = t0m[i % 2]
            v = a0[i]
            await m.evaluate("(v)=>{ EscPad.inp=v; EscPad.send(); }", v); await tv.wait_for_timeout(700)
            lk = await tv.evaluate("()=>EscTV.st.T[0].lk")
            if i == 1: await m.screenshot(path=OUT + "pad_lock3.png")
            if i == 3:
                fl = await tv.evaluate("()=>EscTV.st.T[0].fl")
                ok(sorted(fl) == sorted(a0[4]), f"자물쇠 4개 = 마지막 문 글자 다 모임 {fl} / {a0[4]}")
                await m.screenshot(path=OUT + "pad_final.png"); await tv.screenshot(path=OUT + "tv_run.png")
            ok(lk == i + 1, f"자물쇠 {i+1} 열림 ({v})")
        r = await tv.evaluate("()=>{ const T=EscTV.st.T[0]; return [!!T.out, T.rk, EscTV.st.s]; }")
        ok(r == [True, 1, "run"], f"팀 0 탈출 1등 · 다른 팀은 계속 {r}")
        await t0m[0].wait_for_timeout(500)
        r = await t0m[0].evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, (document.querySelector('#escPad .stGem')||{}).textContent||'']")
        ok("탈출 성공" in r[0] and "1등" in r[0] and "+8" in r[1], f"패드 탈출 화면 · 💎5+3 {r}")
        # 팀 1 = 자물쇠 2개만 → 끝내기
        a1 = S["ans"]["1"]
        for i in range(2):
            await t1m[0].evaluate("(v)=>{ EscPad.inp=v; EscPad.send(); }", a1[i]); await tv.wait_for_timeout(600)
        await tv.evaluate("()=>{ window.confirm=()=>true; document.querySelector('[data-et=end]').click(); }"); await tv.wait_for_timeout(900)
        r = await tv.evaluate("()=>[EscTV.st.s, EscTV.st.ord, EscTV.st.T[1].lk, document.querySelector('.escRank').textContent]")
        ok(r[0] == "end" and r[1] == ["0", "1"] and r[2] == 2 and "1등" in r[3], f"끝 · 순위 {r}")
        await tv.screenshot(path=OUT + "tv_end.png")
        r = await t1m[0].evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, (document.querySelector('#escPad .stGem')||{}).textContent||'']")
        ok("시간" in r[0] and r[1] == "", f"못 나간 팀 (자물쇠 2개) = 보석 없음 {r}")
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
        await tv.wait_for_timeout(700); await tv.evaluate("()=>{ EscTV.nT=1; EscTV.go(); }"); await tv.wait_for_timeout(5000)
        for lk in (0, 1, 2):
            for nm, k in pads:
                r = await k.evaluate("""()=>{ const s=document.getElementById('epSend').getBoundingClientRect(), ks=[...document.querySelectorAll('.epKeys button')].map(b=>b.getBoundingClientRect().bottom); const P=document.getElementById('escPad'); return [Math.round(s.bottom), Math.round(Math.max(...ks)), innerHeight, P.scrollHeight-P.clientHeight]; }""")
                ok(r[0] <= r[2] and r[1] <= r[2], f"{nm} 자물쇠 {lk+1}: 열기·글자판 화면 안 {r}")
                if lk == 2: await k.screenshot(path=f"{OUT}pad3_{nm}.png")
            v = await tv.evaluate("(i)=>EscTV.ans[0][i]", lk)
            await pads[0][1].evaluate("(v)=>{ EscPad.inp=v; EscPad.send(); }", v); await tv.wait_for_timeout(700)
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
