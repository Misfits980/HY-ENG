"""(v419) 🔐 Firebase 로그인 준비 — 웹 API 키가 있으면 익명 로그인 → 모든 요청에 ?auth=토큰 · 토큰이 끝나 가면 새로 · 선생님 기기 등록(시트) · My Town 도 같은 토큰
  키가 없으면(지금) 예전과 똑같이 토큰 없이 (이건 다른 모든 테스트가 확인)"""
import asyncio, sys, os, json
from urllib.parse import urlparse, parse_qs, unquote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
DB = {"hy": {"ok": True, "roster": {"t": {"a1": {"n": "A1"}}, "k": {"k1": {"n": "루아", "t": "a1"}}}}}
TOK = {"cur": "tok1", "n": 0}
LOG = []; SHEET = []
def getp(path):
    o = DB
    for k in [x for x in path.split("/") if x]:
        if not isinstance(o, dict) or k not in o: return None
        o = o[k]
    return o
def setp(path, v, merge=False):
    P = [x for x in path.split("/") if x]; o = DB
    for k in P[:-1]: o = o.setdefault(k, {})
    if v is None: o.pop(P[-1], None)
    elif merge and isinstance(o.get(P[-1]), dict) and isinstance(v, dict): o[P[-1]].update(v)
    else: o[P[-1]] = v
async def fb(r):
    u = urlparse(r.request.url); q = parse_qs(u.query)
    if "identitytoolkit" in u.netloc:
        TOK["n"] += 1; TOK["cur"] = "tok%d" % TOK["n"]
        return await r.fulfill(status=200, content_type="application/json", body=json.dumps({"idToken": TOK["cur"], "refreshToken": "r1", "localId": "uidABCDEFGHIJKL", "expiresIn": "3600"}))
    if "securetoken" in u.netloc:
        TOK["n"] += 1; TOK["cur"] = "tok%d" % TOK["n"]
        return await r.fulfill(status=200, content_type="application/json", body=json.dumps({"id_token": TOK["cur"], "refresh_token": "r2", "user_id": "uidABCDEFGHIJKL", "expires_in": "3600"}))
    if "script.google" in u.netloc:
        b = r.request.post_data or ""; SHEET.append(b)
        try: d = json.loads(b)
        except Exception: d = {}
        return await r.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True} if d.get("type") == "fbTeacher" else {"ok": True, "list": []}))
    if "firebasedatabase" not in u.netloc: return await route(r)
    path = unquote(u.path)[:-5] if u.path.endswith(".json") else unquote(u.path); m = r.request.method; a = (q.get("auth") or [""])[0]
    LOG.append((m, path, a))
    if a != TOK["cur"]: return await r.fulfill(status=401, content_type="application/json", body='{"error":"Permission denied"}')
    if "text/event-stream" in (r.request.headers.get("accept") or ""):
        return await r.fulfill(status=200, content_type="text/event-stream", body="event: put\ndata: " + json.dumps({"path": "/", "data": getp(path)}) + "\n\n")
    if m == "GET": return await r.fulfill(status=200, content_type="application/json", body=json.dumps(getp(path)))
    body = r.request.post_data; val = json.loads(body) if body else None
    if m == "PUT": setp(path, val)
    if m == "PATCH": setp(path, val, True)
    if m == "DELETE": setp(path, None); val = None
    return await r.fulfill(status=200, content_type="application/json", body=json.dumps(val))

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
        await ctx.add_init_script("try{ if(!localStorage.getItem('t0')){ localStorage.clear(); localStorage.setItem('t0','1'); localStorage.setItem('hyeng_fb_key','TESTKEY'); localStorage.setItem('hyeng_nick','영어선생님'); } }catch(e){}")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fb); await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1500)
        E = pg.evaluate
        r = await E("()=>FB.ready().then(m=>[m, FBAuth.on(), FBAuth.uid, FBAuth.tok])")
        ok(r[0] == "fb" and r[1] and r[2] == "uidABCDEFGHIJKL" and r[3] == TOK["cur"], f"키가 있으면 익명 로그인 · 서버 연결 {r}")
        r = await E("()=>FB.get('/hy/roster/k/k1')")
        ok(r and r.get("n") == "루아", f"읽기에 토큰 {r}")
        await E("()=>FB.set('/hy/day/x/k1', {so:3})"); await pg.wait_for_timeout(300)
        ok(getp("/hy/day/x/k1") == {"so": 3}, "쓰기에 토큰")
        await E("()=>FB.update('/hy/day/x/k1', {rr:2})"); await E("()=>FB.push('/hy/cheer/k1/d', {e:'🌟'})"); await pg.wait_for_timeout(300)
        ok(getp("/hy/day/x/k1") == {"so": 3, "rr": 2} and len(getp("/hy/cheer/k1/d") or {}) == 1, "고치기·더하기도 토큰")
        r = await E("()=>FB.once('/hy/roster/pz/p1/k1', {n:'루아'})"); await pg.wait_for_timeout(200)
        ok(r is True and getp("/hy/roster/pz/p1/k1"), "한 번만 쓰기(once)도 토큰")
        no_auth = [x for x in LOG if x[1] != "/hy/ok" and not x[2]]
        ok(not no_auth, f"토큰 없는 요청 없음 (ok 확인 빼고) {no_auth[:3]}")
        # 토큰이 끝나 가면 새로 (refresh)
        old = TOK["cur"]
        await E("()=>{ FBAuth.exp=Date.now()+60000; }")
        r = await E("()=>FB.get('/hy/roster/k/k1').then(v=>[v && v.n, FBAuth.tok])")
        ok(r[0] == "루아" and r[1] == TOK["cur"] and r[1] != old, f"토큰이 끝나 가면 새로 받아서 계속 {r} (전 {old})")
        # 실시간 듣기 URL 에도
        await E("()=>{ window._h=FB.listen('/hy/roster', ()=>{}); }"); await pg.wait_for_timeout(1500)
        es = [x for x in LOG if x[1] == "/hy/roster" and x[0] == "GET"]
        ok(es and es[-1][2] == TOK["cur"], f"실시간 듣기에도 토큰 {es[-1:]}")
        # 선생님 기기 등록 → 시트
        await E("()=>{ Admin.open && Admin.open(); }"); await pg.wait_for_timeout(300)
        r = await E("""()=>new Promise(res=>{ const t0=Date.now(); FBAuth.token().then(()=>{ fetch(Online.URL, {method:'POST', body:JSON.stringify({key:Online.KEY, type:'fbTeacher', uid:FBAuth.uid, tk:'x'})}).then(r=>r.json()).then(res); }); })""")
        ok(r.get("ok") and any('"fbTeacher"' in b and "uidABCDEFGHIJKL" in b for b in SHEET), "선생님 기기 등록 요청 (시트에 uid)")
        # My Town 도 같은 토큰
        LOG.clear(); os.environ["HY_REAL3D"] = "1"
        await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(2500)
        r = await E("()=>(typeof HOUSE!=='undefined') ? HOUSE.loadSocial().then(()=>1) : 0")
        h = [x for x in LOG if x[1].startswith("/hy/life")]
        ok(h and all(x[2] == TOK["cur"] for x in h), f"My Town 요청에도 같은 토큰 {h[:2]}")
        ok(not [e for e in errs if "Failed to load" not in e], "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
