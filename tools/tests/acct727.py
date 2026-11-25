"""(v727) 🔐 로그인과 얽힌 곳 — 계정 태그(서버 v28) · 형제가 한 기기 · 한 아이 두 기기 · 로그아웃 뒤 게스트 · 이름표 · 주간 보스 아이 · 수업 게임 이름 · 점수 줄 태그
   진짜 Code.gs(가짜 시트) + 규칙 흉내 Firebase (fake_acct_srv.js)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acct723 as A
from harness import *
from playwright.async_api import async_playwright

R = {"k": {"r1": {"n": "토토", "t": "t1"}, "r2": {"n": "별사탕", "t": "t1"}, "r3": {"n": "콩콩", "t": "t1"}}, "t": {"t1": {"n": "돌고래반", "e": "🐬"}}}

async def wire(pg, log):
    async def gs(r):
        body = r.request.post_data or "{}"
        try: log.append(json.loads(body))
        except Exception: pass
        st, out = A.http("POST", "/gs", body); await r.fulfill(status=200, body=out, content_type="application/json")
    async def fbr(r):
        u = r.request.url; p = u[len(A.FBH):]
        if not (p.startswith("/kacct") or p.startswith("/kdev")): return await r.fallback()
        path, _, q = p.partition("?"); st, out = A.http(r.request.method, "/fb" + path + ("?" + q if q else ""), r.request.post_data)
        await r.fulfill(status=st, body=out, content_type="application/json")
    await pg.route("https://script.google.com/**", gs); await pg.route(A.FBH + "/**", fbr)

async def dev(br, errs, tag, log, init="", seed=None):
    ctx = await br.new_context(viewport={"width": 390, "height": 844}); pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(tag + " " + str(e)))
    await pg.add_init_script("window.HY_FB_LOCAL=1;" + init); await boot(pg); await wire(pg, log)
    await pg.evaluate("""(R)=>FB.ready().then(()=>Promise.all([FB.set('/hy/roster', R), FB.set('/hy/acon', {on:1})]))""", R)
    if seed: await pg.evaluate(seed)   # 한 번만 (init 은 새로 켤 때마다 다시 돎)
    await pg.reload(); await pg.wait_for_timeout(2400)
    return ctx, pg

async def login(pg, idv, pw):
    s = await A.ui(pg)
    if s in ("", "who"):
        await pg.evaluate("()=>{ const c=document.getElementById('acChip'); if(c) c.click(); }"); await pg.wait_for_timeout(400)
    if await A.ui(pg) == "who": await pg.click('#acctUI .acS.on [data-go=id]'); await pg.wait_for_timeout(300)
    if await A.ui(pg) == "home": await pg.click('#acctUI [data-s=home] .acGold'); await pg.wait_for_timeout(300)
    await A.typeId(pg, idv); await pg.click("#acIdNext"); await pg.wait_for_timeout(300); await A.pin(pg, pw)
    for _ in range(25):
        try:
            s = await A.ui(pg)
            if s == "mine": await pg.click("#acctUI [data-mine=mine]")
            if s == "wel": break
        except Exception: pass
        await pg.wait_for_timeout(400)
    await pg.wait_for_timeout(900)
    try: await pg.click('#acctUI [data-go=done]', timeout=3000)
    except Exception: pass
    await pg.wait_for_timeout(500)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    node = A.subprocess.Popen(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_acct_srv.js"), str(A.PORT)], stdout=A.subprocess.PIPE, text=True)
    assert "READY" in node.stdout.readline()
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch(); log = []
            # 선생님: 계정 둘 + 처음 기기 승인 없이(시험이 승인 단계를 건너뛰게)
            tctx = await br.new_context(); tp = await tctx.new_page(); await tp.add_init_script("window.HY_FB_LOCAL=1"); await boot(tp); await wire(tp, [])
            r = await tp.evaluate("()=>Online.submit({type:'acctMake', tk:'TK', list:[{rid:'r1', n:'토토', t:'t1', id:'toto', bd:'150309'}, {rid:'r2', n:'별사탕', t:'t1', id:'byul', bd:'150410'}]})")
            ok(r and r.get("made") == 2, "계정 2개 (토토 · 별사탕 — 형제라고 침)")
            ok((await tp.evaluate("()=>Online.submit({type:'acctOpen', tk:'TK', days:3})")).get("ok"), "처음 기기 승인 없이 3일")
            # 예전부터 토토가 쓰던 집 태블릿 X (기기 태그 #0006 = 토토)
            ctx, X = await dev(br, errs, "X", log, "try{ sessionStorage.setItem('hyeng_acct_skip','1'); }catch(e){}", "()=>{ localStorage.setItem('hyeng_nick','토토'); return Tag.sync(); }")
            t0 = await X.evaluate("()=>Tag.get()"); ok(len(t0) == 4, "로그인 전: 이 기기 태그 #" + t0 + " (토토)")
            # 1) 토토 로그인 → 계정 태그 = 그 태그
            await login(X, "toto", "150309")
            a = await X.evaluate("()=>({on:Acct.on(), tag:(Acct.get()||{}).tag, dev:Tag.get(), me:JSON.parse(localStorage.getItem('hyeng_me')||'{}'), nick:localStorage.getItem('hyeng_nick')})")
            ok(a["on"] and a["tag"] == t0 and a["dev"] == t0, "토토 로그인 = 계정 태그 #" + str(a["tag"]) + " (원래 기기 태그 그대로 — 랭킹 한 줄)")
            ok(a["me"].get("id") == "r1" and a["nick"] == "토토", "명단 아이 r1 · 이름 토토")
            n0 = len(log); await X.evaluate("()=>{ Tag._busy=null; return Tag.sync(); }"); await X.wait_for_timeout(600)
            ok(not any(x.get("type") == "tag" for x in log[n0:]), "로그인 중엔 기기 태그를 서버에 다시 묻지 않음 (이름으로 태그 줄을 바꾸지 않게)")
            km = await X.evaluate("()=>{ try{ const m=Kid.me(); return m && m.id; }catch(e){ return 'ERR '+e.message; } }"); ok(km == "r1", "주간 보스·선물이 보는 아이 = r1 (" + str(km) + ")")
            # 점수 줄에 계정 태그
            n0 = len(log); await X.evaluate("()=>Online.submit({nick:Online.nick?Online.nick():'토토', score:10, diff:'easy', rule:'normal'})"); await X.wait_for_timeout(500)
            sub = [x for x in log[n0:] if "score" in x]
            ok(sub and str(sub[-1].get("tag", "")).replace("#", "") == t0, "점수 줄 tag = 계정 태그 " + str(sub[-1].get("tag") if sub else None))
            # 수업 게임 창 이름
            await X.evaluate("()=>RaidJoin.open()"); await X.wait_for_timeout(700)
            nm = await X.evaluate("()=>{ const e=document.getElementById('rdJoin'); return e ? e.innerText : ''; }")
            ok("토토" in nm, "🎮 수업 게임 창 = 토토로 들어감")
            await X.evaluate("()=>{ try{ RaidJoin.close(); }catch(e){} }")
            # 2) 로그아웃 → 기기 태그 지움
            await X.evaluate("()=>Acct.logout()"); await X.wait_for_timeout(3000)
            st = await X.evaluate("()=>({tag:localStorage.getItem('hyeng_tag'), nick:localStorage.getItem('hyeng_nick'), me:localStorage.getItem('hyeng_me'), on:Acct.on(), lock:Acct.locked()})")
            ok(not st["tag"] and not st["nick"] and not st["me"] and not st["on"], "로그아웃 = 태그·이름·명단 아이 모두 지움 " + str(st))
            # 게스트가 이름을 정해도 토토 태그 줄 이름이 안 바뀜
            n0 = len(log); await X.evaluate("()=>{ localStorage.setItem('hyeng_nick','동생'); Tag._busy=null; return Tag.sync(); }"); await X.wait_for_timeout(800)
            T = json.dumps(A.db()["tags"], ensure_ascii=False)
            ok(not any(x.get("type") == "tag" for x in log[n0:]) and "동생" not in T, "게스트(계정 켜짐)는 태그를 안 물음 → 토토 태그 줄 이름 그대로")
            await X.evaluate("()=>localStorage.setItem('hyeng_nick','')")
            r = await X.evaluate("()=>{ KidPick.open(()=>{}); return {ui:!!(document.getElementById('acctUI')&&document.getElementById('acctUI').classList.contains('on')), kp:!!document.getElementById('kidPick')}; }")
            ok(r["ui"] and not r["kp"], "게스트가 「나는 누구?」 명단 고르기 → 로그인 화면 (명단에서 아무 아이나 못 됨)")
            await X.evaluate("()=>{ const b=document.querySelector('#acctUI [data-go=skip]'); if(b) b.click(); }"); await X.wait_for_timeout(300)
            # 3) 형제: 별사탕이 같은 기기로 로그인 → 다른 태그
            try:
                await X.reload(); await X.wait_for_timeout(2500)
            except Exception: pass
            await login(X, "byul", "150410")
            b = await X.evaluate("()=>({on:Acct.on(), tag:(Acct.get()||{}).tag, dev:Tag.get(), me:JSON.parse(localStorage.getItem('hyeng_me')||'{}')})")
            ok(b["on"] and b["tag"] and b["tag"] != t0 and b["dev"] == b["tag"], "형제 별사탕이 같은 기기 → 자기 태그 #" + str(b["tag"]) + " (토토 #" + t0 + " 와 안 섞임)")
            ok(b["me"].get("id") == "r2", "명단 아이 = r2 (별사탕)")
            TG = A.db()["tags"]; rt = [x for x in TG if str(x[0]) == t0]; rb = [x for x in TG if str(x[0]) == b["tag"]]
            dv = await X.evaluate("()=>Online.dev()")
            ok(rt and rt[0][3] == "토토" and rb and rb[0][3] == "별사탕" and dv in str(rb[0][1]) and dv not in str(rt[0][1]), "태그 탭: #" + t0 + " = 토토 · #" + b["tag"] + " = 별사탕 · 이 기기는 별사탕 줄로")
            await ctx.close()
            # 4) 토토가 새 휴대폰 Y 로 → 같은 태그
            ctx2, Y = await dev(br, errs, "Y", log, "try{ sessionStorage.setItem('hyeng_acct_skip','1'); }catch(e){}")
            nrows = len(A.db()["tags"])
            await login(Y, "toto", "150309")
            y = await Y.evaluate("()=>({on:Acct.on(), tag:(Acct.get()||{}).tag, dev:Tag.get()})")
            ok(y["on"] and y["tag"] == t0 and y["dev"] == t0 and len(A.db()["tags"]) == nrows, "토토 새 휴대폰 → 같은 태그 #" + t0 + " · 태그 줄 안 늘어남")
            # 5) 이름 바꾸기 → 태그 줄 이름도
            await Y.evaluate("()=>Wallet.adjust(200, '시험')")
            msg = await Y.evaluate("()=>Acct.rename('토토로')")
            TG = A.db()["tags"]; rt = [x for x in TG if str(x[0]) == t0]
            ok(msg == "" and rt and rt[0][3] == "토토로", "이름 바꾸기 → 태그 줄 「지금 이름」 토토로")
            await ctx2.close()
            E = real_errs(errs); ok(not E, "페이지 오류 없음 " + str(E[:3]))
    finally:
        node.kill()
    print("FAIL " + str(len(bad)) if bad else "ALL OK"); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
