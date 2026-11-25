"""(v726) 🔒 ①-c 게스트 잠금 — 계정 켜짐 + 아이 개인 기기 + 로그인 안 함 = My Town · 수업 게임 · 상점 잠김 (Adventure · Daily 30 그대로)
   · 칩 「로그인 · 🙋 게스트 NNNN」(이 기기에서 같은 번호) · 누르면 로그인 화면 · house.html 을 바로 열어도 첫 화면으로
   · 공용 패드 · 선생님 기기 · 계정 꺼짐 = 잠그지 않음 · 로그인하면 풀림
   node tools/tests/fake_acct_srv.js 를 띄워서 씀 (acct723 도우미 그대로)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acct723 as A
from harness import *
from playwright.async_api import async_playwright

SKIP = "()=>{ try{ sessionStorage.setItem('hyeng_acct_skip','1'); }catch(e){} }"
LK = "()=>({town:(()=>{ const t=document.querySelector('#selRule [data-v=town]'); return t.classList.contains('twLock') && /로그인하면 열려요/.test(t.innerText); })(), join:(()=>{ const t=document.querySelector('#selRule [data-v=join]'); return t.classList.contains('acLkC') && /로그인하면 열려요/.test(t.innerText); })(), shop:!!document.querySelector('#btnShop.acLk'), flag:localStorage.getItem('hyeng_acct_glock'), chip:(document.getElementById('acChip')||{}).innerText||''})"

async def page(br, errs, tag, init="", acon=True, vw=(390, 844)):
    ctx = await br.new_context(viewport={"width": vw[0], "height": vw[1]}); pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(tag + " " + str(e)))
    await pg.add_init_script("window.HY_FB_LOCAL=1;" + init); await boot(pg); await A.wire(pg)
    await pg.evaluate("""(o)=>FB.ready().then(()=>Promise.all([FB.set('/hy/roster', o.R), FB.set('/hy/acon', o.on ? {on:1} : null)]))""", {"R": A.ROSTER, "on": acon})
    await pg.reload(); await pg.wait_for_timeout(2400)
    return ctx, pg

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    node = A.subprocess.Popen(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_acct_srv.js"), str(A.PORT)], stdout=A.subprocess.PIPE, text=True)
    assert "READY" in node.stdout.readline()
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch()
            # ── 아이 개인 기기 · 로그인 안 함 (로그인 화면은 「로그인 없이」로 닫은 셈) ──
            ctx, pg = await page(br, errs, "G", "try{ sessionStorage.setItem('hyeng_acct_skip','1'); }catch(e){}")
            L = await pg.evaluate(LK); print("   ", L)
            ok(L["town"] and L["join"] and L["shop"] and L["flag"] == "1", "게스트 = My Town · 수업 게임 · 상점 🔒 · 잠금 표시(hyeng_acct_glock)")
            gn = await pg.evaluate("()=>localStorage.getItem('hyeng_acct_gn')")
            ok(gn and len(gn) == 4 and ("게스트 " + gn) in L["chip"] and "로그인" in L["chip"], "칩 = 로그인 · 🙋 게스트 " + str(gn))
            ok(not await pg.evaluate("()=>/로그인/.test(document.querySelector('#selRule [data-v=normal]').innerText + document.querySelector('#selRule [data-v=daily]').innerText)"), "Adventure · Daily 30 은 그대로")
            await pg.screenshot(path=OUT + "acct726_start.png")
            # 상점 → 로그인 화면 (상점은 안 열림)
            await pg.click("#btnShop"); await pg.wait_for_timeout(500)
            ok(await A.ui(pg) in ("home", "who") and not await pg.evaluate("()=>document.getElementById('shShop').classList.contains('on')"), "상점 누름 → 로그인 화면 (상점 안 열림)")
            await pg.click('#acctUI [data-go=skip] >> nth=0'); await pg.wait_for_timeout(300)
            # 게임 시작 → 무엇을 할까요? → My Town · 수업 게임
            await pg.evaluate("()=>document.getElementById('btnGo').click()"); await pg.wait_for_timeout(700)
            await pg.screenshot(path=OUT + "acct726_setup.png")
            await pg.evaluate("()=>document.querySelector('#selRule [data-v=town]').click()"); await pg.wait_for_timeout(600)
            ok(await A.ui(pg) in ("home", "who") and "house.html" not in pg.url, "🏡 My Town 카드 → 로그인 화면 (마을로 안 감)")
            await pg.click('#acctUI [data-go=skip] >> nth=0'); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>document.querySelector('#selRule [data-v=join]').click()"); await pg.wait_for_timeout(600)
            ok(await A.ui(pg) in ("home", "who") and not await pg.evaluate("()=>{ const e=document.getElementById('rdJoin'); return !!(e && e.classList.contains('on')); }"), "🎮 수업 게임 카드 → 로그인 화면")
            await pg.click('#acctUI [data-go=skip] >> nth=0'); await pg.wait_for_timeout(300)
            r = await pg.evaluate("()=>{ RaidJoin.open(); return !!(document.getElementById('acctUI')||{}).classList && document.getElementById('acctUI').classList.contains('on'); }")
            ok(r, "다른 곳에서 RaidJoin.open() 을 불러도 로그인 화면")
            await pg.click('#acctUI [data-go=skip] >> nth=0'); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>document.querySelector('#selRule [data-v=daily]').click()"); await pg.wait_for_timeout(900)
            ok(await pg.evaluate("()=>document.getElementById('scStudy').classList.contains('on')") and await A.ui(pg) == "", "📚 Daily 30 은 그대로 열림")
            # house.html 을 바로 열면 → 첫 화면 + 로그인 화면
            await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(3500)
            ok("index.html" in pg.url and "house.html" not in pg.url, "house.html 을 바로 열어도 → 첫 화면 " + pg.url[-30:])
            ok(await A.ui(pg) in ("home", "who"), "→ 로그인 화면 (My Town 은 로그인하면 열려요)")
            gn2 = await pg.evaluate("()=>localStorage.getItem('hyeng_acct_gn')"); ok(gn2 == gn, "게스트 번호는 이 기기에서 그대로 " + str(gn2))
            # 로그인하면 풀림 (태그 기기 = 승인 없이)
            tctx = await br.new_context(); tp = await tctx.new_page(); await tp.add_init_script("window.HY_FB_LOCAL=1"); await boot(tp); await A.wire(tp)
            r = await tp.evaluate("()=>Online.submit({type:'acctMake', tk:'TK', list:[{rid:'r3', n:'콩콩', t:'t1', id:'kong', bd:'150512'}]})")
            ok(r and r.get("res") and r["res"][0].get("ok"), "선생님이 계정 만들기 (콩콩 · kong)")
            r = await tp.evaluate("()=>Online.submit({type:'acctOpen', tk:'TK', days:3})"); ok(r and r.get("ok"), "처음 기기 승인 없이 3일 (시험이 승인 단계를 건너뛰게)"); await tctx.close()
            if await A.ui(pg) != "id":
                await pg.click('#acctUI [data-go=id] >> nth=0'); await pg.wait_for_timeout(300)
            await A.typeId(pg, "kong"); await pg.click("#acIdNext"); await A.pin(pg, "150512")
            for _ in range(20):
                s = await A.ui(pg)
                if s in ("mine", "wel"): break
                await pg.wait_for_timeout(400)
            if await A.ui(pg) == "mine": await pg.click("#acctUI [data-mine=mine]")
            for _ in range(20):
                try:
                    if await A.ui(pg) == "wel": break
                except Exception: pass
                await pg.wait_for_timeout(400)
            await pg.wait_for_timeout(800)
            try: await pg.click('#acctUI [data-go=done]')
            except Exception: pass
            await pg.wait_for_timeout(600)
            L = await pg.evaluate(LK); print("   ", L)
            ok(await pg.evaluate("()=>Acct.on()") and not (L["town"] or L["join"] or L["shop"]) and L["flag"] is None and "콩콩" in L["chip"], "로그인하면 잠금 풀림 · 칩 = 콩콩")
            await ctx.close()
            # ── 공용 패드 · 선생님 기기 · 계정 꺼짐 = 잠그지 않음 ──
            for tag, init, acon, why in (("S", "localStorage.setItem('hyeng_nick','한양패드3');", True, "공용 패드"), ("T", "localStorage.setItem('hyeng_teacher_dev','1');", True, "선생님 기기"),
                                         ("K", "localStorage.setItem('hyeng_admin_key','ab'.repeat(24));", True, "연결된 선생님 휴대폰"), ("O", "", False, "계정 꺼짐")):
                c2, p2 = await page(br, errs, tag, init + "try{ sessionStorage.setItem('hyeng_acct_skip','1'); }catch(e){}", acon)
                L = await p2.evaluate(LK)
                ok(not (L["town"] or L["join"] or L["shop"]) and L["flag"] is None and await p2.evaluate("()=>!Acct.locked()"), why + " = 잠그지 않음")
                await c2.close()
            # 작은 휴대폰에서 칩 · 보스 안 겹침
            c3, p3 = await page(br, errs, "N", "try{ sessionStorage.setItem('hyeng_acct_skip','1'); }catch(e){}", True, (360, 640))
            r = await p3.evaluate("()=>{ const c=document.getElementById('acChip').getBoundingClientRect(), b=[...document.querySelectorAll('#scStart .topBtns button, #scStart #btnFull, #scStart #btnSet, #btnSettings')].map(e=>e.getBoundingClientRect()).filter(x=>x.width); return {c:[c.left,c.right], hit:b.filter(x=>x.left<c.right && x.right>c.left && x.top<c.bottom && x.bottom>c.top).length, w:innerWidth}; }")
            ok(r["c"][0] >= 0 and r["c"][1] <= r["w"] and r["hit"] == 0, "360px 휴대폰 = 칩이 화면 안 · 단추와 안 겹침 " + str(r))
            await p3.screenshot(path=OUT + "acct726_360.png"); await c3.close()
            E = real_errs(errs); ok(not E, "페이지 오류 없음 " + str(E[:3]))
    finally:
        node.kill()
    print("FAIL " + str(len(bad)) if bad else "ALL OK"); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
