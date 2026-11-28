"""(v742) 🔐 아이디 3~12글자 (전 3~8) — 사용자: 「아이디는 길이는 최대 12글자까지 하자 · 이번 주까지 아이디 다 생성해서 애들 분리」
   ① 선생님 「계정 만들기」 칸 12글자까지 · 12글자 아이디로 만들어짐 · 13글자는 칸이 받지 않음 · 안내 글 3~12
   ② 아이 로그인: 자판으로 13글자 → 12글자에서 멈춤 · 12글자가 판 안에 다 보임(360 · 390 · 패드) · 다음 → 비밀번호 → 서버가 아이디를 받음(noid 아님)
   ③ 로그인 쪽지: 12글자 아이디가 한 줄"""
import asyncio, sys, os, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from acct723 import http, db, wire, ui, typeId, pin, PORT, ROSTER
from playwright.async_api import async_playwright
OUTD = OUT + "acct742/"; os.makedirs(OUTD, exist_ok=True)
FITS = """()=>{ const e=document.getElementById('acIdT'), p=e.closest('.acPlate'), r=e.getBoundingClientRect(), q=p.getBoundingClientRect(); const L=[...e.querySelectorAll('.acGt')].map(s=>s.getBoundingClientRect());
  const inside=L.every(s=>s.left>=q.left-1 && s.right<=q.right+1); return {n:L.length, inside, ow:e.scrollWidth-e.clientWidth, fs:getComputedStyle(e).fontSize, pl:Math.round(q.left), pr:Math.round(q.right), W:innerWidth}; }"""
async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    node = subprocess.Popen(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_acct_srv.js"), str(PORT)], stdout=subprocess.PIPE, text=True)
    assert "READY" in node.stdout.readline()
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch()
            tctx = await br.new_context(viewport={"width": 1100, "height": 900}); tp = await tctx.new_page(); tp.on("pageerror", lambda e: errs.append("T " + str(e)))
            await tp.add_init_script("window.HY_FB_LOCAL=1"); await boot(tp); await wire(tp)
            await tp.evaluate("""(R)=>FB.ready().then(()=>FB.set('/hy/roster', R)).then(()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'TK'); localStorage.setItem('hyeng_teacher_dev','1'); })""", ROSTER)
            await tp.reload(); await tp.wait_for_timeout(2000)
            await tp.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); Admin.open(); }"); await tp.wait_for_timeout(800)
            await tp.evaluate("()=>{ const b=document.querySelector('#shAdmin [data-ad=tab][data-t=class]'); if(b) b.click(); }"); await tp.wait_for_timeout(1500)
            await tp.click("#acAdm [data-acx=mk]"); await tp.wait_for_timeout(300)
            r = await tp.evaluate("()=>({ml:[...document.querySelectorAll('#acAdm [data-mki]')].map(i=>i.maxLength), t:(document.querySelector('#acAdm .acMk')||{}).innerText||''})")
            ok(r["ml"] and all(m == 12 for m in r["ml"]) and "3~12글자" in r["t"], "① 만들기 칸 12글자까지 · 안내 「3~12글자」 %s" % r["ml"])
            await tp.fill('#acAdm [data-mki="r1"]', "gureumgureumx")   # 13글자 → 칸이 12에서 자름
            v = await tp.evaluate("()=>document.querySelector('#acAdm [data-mki=\"r1\"]').value")
            ok(v == "gureumgureum", "① 13글자를 넣으면 칸이 12글자에서 멈춤 (%s)" % v)
            await tp.evaluate("""()=>{ const s=(k,id,bd)=>{ document.querySelector('#acAdm [data-mki="'+k+'"]').value=id; document.querySelector('#acAdm [data-mkb="'+k+'"]').value=bd; };
              s('r1','gureumgureum','150309'); s('r2','haneulbyeol','150410'); s('r3','',''); }""")
            await tp.click("#acAdm [data-acx=mkgo]"); await tp.wait_for_timeout(1500)
            t = await tp.evaluate("()=>document.getElementById('acAdm').innerText")
            ok("만든 계정 2개" in t and "gureumgureum" in t and "haneulbyeol" in t, "① 12글자 · 11글자 아이디로 계정 2개 만듦")
            await tp.screenshot(path=OUTD + "admin.png", full_page=False)
            # ③ 로그인 쪽지 (새 창 글)
            pop = []
            tp.on("popup", lambda q: pop.append(q))
            await tp.evaluate("()=>{ window.print=()=>{}; }")
            await tp.click("#acAdm [data-acx=slip]"); await tp.wait_for_timeout(1500)
            if pop:
                q = pop[0]; await q.evaluate("()=>{ window.print=()=>{}; }"); await q.wait_for_timeout(500)
                s = await q.evaluate("()=>[...document.querySelectorAll('b.id')].map(b=>({t:b.textContent, h:Math.round(b.getBoundingClientRect().height), w:b.scrollWidth<=b.parentElement.clientWidth+1}))")
                ok(any(x["t"] == "gureumgureum" and x["h"] < 50 and x["w"] for x in s), "③ 로그인 쪽지에 12글자 아이디가 한 줄 %s" % s)
                await q.screenshot(path=OUTD + "slip.png"); await q.close()
            else:
                ok(False, "③ 로그인 쪽지 창이 안 열림")
            await tp.click("#acAdm [data-acx=on]"); await tp.wait_for_timeout(900)
            ok(db()["db"].get("hy", {}).get("acon", {}).get("on") == 1, "계정 켜기")
            # ② 아이 로그인 · 화면 3가지
            for w, h in ((360, 740), (390, 844), (820, 1180)):
                ctx = await br.new_context(viewport={"width": w, "height": h}); pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append("K " + str(e)))
                await pg.add_init_script("window.HY_FB_LOCAL=1"); await boot(pg); await wire(pg)
                await pg.evaluate("""(R)=>FB.ready().then(()=>Promise.all([FB.set('/hy/roster', R), FB.set('/hy/acon', {on:1})]))""", ROSTER)
                await pg.reload(); await pg.wait_for_timeout(2200)
                if await ui(pg) != "home":
                    ok(False, "② %d×%d 로그인 첫 화면이 안 뜸 (%s)" % (w, h, await ui(pg))); await ctx.close(); continue
                await pg.click('#acctUI [data-s=home] .acGold'); await pg.wait_for_timeout(400)
                hint = await pg.evaluate("()=>document.getElementById('acIdH').innerText")
                await typeId(pg, "gureumgureumz")
                idv = await pg.evaluate("()=>AcctUI ? AcctUI.idv : null") if await pg.evaluate("()=>typeof AcctUI!=='undefined'") else None
                f = await pg.evaluate(FITS)
                ok(f["n"] == 12 and f["inside"] and f["ow"] <= 1 and "3~12" in hint, "② %d×%d 13글자 → 12글자에서 멈춤 · 판 안에 다 보임 · 안내 3~12 %s" % (w, h, f))
                await pg.screenshot(path=OUTD + "id_%dx%d.png" % (w, h))
                await pg.click("#acIdNext"); await pg.wait_for_timeout(400)
                if await ui(pg) == "pw":
                    await pin(pg, "150309")
                    s = ""
                    for _ in range(20):
                        s = await ui(pg)
                        if s in ("wait", "mine", "wel"): break
                        await pg.wait_for_timeout(400)
                    msg = await pg.evaluate("()=>{ const e=document.querySelector('#acctUI .acS.on'); return e ? e.innerText.slice(0,80) : ''; }")
                    ok(s in ("wait", "mine", "wel"), "② %d×%d 12글자 아이디 + 생일 → 서버가 받음 (%s) %s" % (w, h, s, msg.replace("\n", " ")))
                else:
                    ok(False, "② %d×%d 다음 → 비밀번호 화면이 아님 (%s)" % (w, h, await ui(pg)))
                await ctx.close()
            ok(not errs, "오류 없음 %s" % errs[:3])
            await br.close()
    finally:
        node.terminate()
    print("== 문제 %d" % len(bad))
    sys.exit(1 if bad else 0)
if __name__ == "__main__":
    asyncio.run(main())
