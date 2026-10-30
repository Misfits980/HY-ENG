"""(v453) 🗼 타워 = 잼못타처럼 — 사용자: "타워를 잼못타를 카피해서 · 영어는 넣지 말고 · 애들이 같이 할 수 있게 · 체크포인트가 있으면 안 되더라"
  ① 🔤 단어 다리 없음 (쉬움·어려움 여러 날) · 층 발판에 🚩 깃발 없음
  ② 🚫 체크포인트 없음: 높은 층에서 떨어지면 떨어진 곳에 그대로(⬇️ 횟수) · 로비 바닥에 떨어져도 그대로 · 🔥 용암 = 맨 아래 · 아주 아래로 빠지면 맨 아래
  ③ 층 표시 = 지금 몸 높이 · 👥 친구 수
  ④ 👥 그냥 같이: 가짜 서버(진짜 Firebase 대신 이 시험 안의 저장소)로 두 기기 — 서로 보임 · 이름표 · 따라 움직임 · 나가면 사라짐"""
import asyncio, sys, os, json, re
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

DB = {}
def db_get(path):
    o = DB
    for k in [x for x in path.split("/") if x]:
        if not isinstance(o, dict) or k not in o: return None
        o = o[k]
    return o
def db_put(path, v):
    ks = [x for x in path.split("/") if x]; o = DB
    for k in ks[:-1]: o = o.setdefault(k, {})
    if v is None: o.pop(ks[-1], None)
    else: o[ks[-1]] = v
async def fake(r):
    url = r.request.url
    if "firebasedatabase.app" in url or "firebaseio.com" in url:
        if "text/event-stream" in (r.request.headers.get("accept") or ""): return await r.fulfill(status=503, body="no")   # 스트리밍 없음 → 읽기로
        path = re.sub(r"^https://[^/]+", "", url).split("?")[0]; path = path[:-5] if path.endswith(".json") else path
        m = r.request.method
        if path == "/hy/ok": return await r.fulfill(status=200, body="true", content_type="application/json")
        if m == "GET": return await r.fulfill(status=200, body=json.dumps(db_get(path)), content_type="application/json")
        if m == "PUT": v = json.loads(r.request.post_data or "null"); db_put(path, v); return await r.fulfill(status=200, body=json.dumps(v), content_type="application/json")
        if m == "DELETE": db_put(path, None); return await r.fulfill(status=200, body="null", content_type="application/json")
        return await r.fulfill(status=400, body="x")
    return await route(r)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        async def open_kid(code, name):
            ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(600)
            await pg.evaluate("""([c,n])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1');
                localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); }""", [code, name])
            await pg.reload(); await pg.wait_for_timeout(2200); return pg
        A = await open_kid("AAAAA", "루아"); E = A.evaluate
        async def until(pg, js, n=60):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(200)
            return False
        r = await E("()=>HOUSE.myCode()")
        ok(r == "AAAAA", f"기기 A 집 키 {r}")
        # ① 단어 다리 · 깃발 없음
        r = await E("""()=>{ const T=HOUSE.TW, out=[]; for(const m of ['easy','hard']) for(let d=1; d<=10; d++){ T.seed='2026-09-'+d; HOUSE.twBuild(m); out.push([T.secs.includes('word'), T.S.some(s=>s.kind==='glass'), T.cps.some(c=>c.flag)]); } return out.filter(x=>x.some(Boolean)).length; }""")
        ok(r == 0, f"① 🔤 단어 다리·유리 없음 · 🚩 깃발 없음 (20개 타워) {r}")
        # 타워 안으로 (A)
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until(A, "()=>HOUSE.place()==='village'")
        await E("()=>{ HOUSE.TW.seed='2026-10-07'; HOUSE.twEnterGo('easy'); }")
        ok(await until(A, "()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "🟢 쉬움 → 타워 안")
        r = await E("()=>[document.getElementById('twRe').hidden, document.getElementById('twPeers').textContent, document.getElementById('twFloor').textContent]")
        ok(r[0] and r[1] == "👥 0" and r[2].startswith("1 / 10"), f"🚩 단추 없음 · 👥 0 · 1층 {r}")
        # ② 떨어지면 그 자리 (사람)
        r = await E("""()=>{ const T=HOUSE.TW; T.bot=false; T.cp=3; T.best=3; const c=T.cps[3]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); for(let i=0;i<20;i++) HOUSE.twStep(1/90);
            const hud=(HOUSE.twTick(0.2), document.getElementById('twFloor').textContent), d0=T.dead, f0=T.fall, y0=T.p.y;
            const F=HOUSE.TWC; T.p.set(F+7.5, y0+0.5, F+7.5); T.v.set(0,0,0); for(let i=0;i<900 && !(T.onG && T.p.y<y0-2);i++) HOUSE.twStep(1/90); for(let i=0;i<30;i++) HOUSE.twStep(1/90);
            return [hud, T.dead-d0, T.fall-f0, +(y0-T.p.y).toFixed(1), T.onG, T.cp, Math.hypot(T.p.x-(c.min.x+c.max.x)/2, T.p.z-(c.min.z+c.max.z)/2)>1]; }""")
        ok(r[0].startswith("4 / 10") and r[1] == 0 and r[2] >= 1 and r[3] > 2 and r[4] and r[6], f"② 4층에서 떨어짐 → 떨어진 곳에 그대로 (체크포인트로 안 감) · ⬇️ 횟수 {r}")
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<60 && !T.S.some(s=>s.kind==='kill'); d++){ T.seed='2026-12-'+d; HOUSE.twBuild('easy'); } T.cp=3; T.best=3; const b=T.cps[0]; const lava=T.S.find(s=>s.kind==='kill'); if(!lava) return 'nolava'; T.p.set((lava.min.x+lava.max.x)/2, lava.max.y+0.05, (lava.min.z+lava.max.z)/2); T.v.set(0,-1,0); for(let i=0;i<10;i++) HOUSE.twStep(1/90);
            const atBottom=Math.hypot(T.p.x-(b.min.x+b.max.x)/2, T.p.z-(b.min.z+b.max.z)/2)<0.1 && Math.abs(T.p.y-b.max.y)<0.05; T.p.y=-20; HOUSE.twStep(1/90); const again=Math.abs(T.p.y-b.max.y)<0.05;
            return [atBottom, again, T.cp]; }""")
        ok(r != "nolava" and r[0] and r[1] and r[2] == 3, f"② 🔥 용암 = 맨 아래 · 아래로 빠짐 = 맨 아래 · 최고 층 기록은 그대로 {r}")
        r = await E("""()=>{ const T=HOUSE.TW, fl=T.S.find(s=>s.kind==='floor'); T.p.set(HOUSE.TWC+8, 0.5, HOUSE.TWC+8); T.v.set(0,0,0); const d0=T.dead; for(let i=0;i<120;i++) HOUSE.twStep(1/90); return [T.onG, T.gnd===fl, T.dead-d0, Math.abs(T.p.x-(HOUSE.TWC+8))<0.2]; }""")
        ok(r == [True, True, 0, True], f"② 로비 바닥에 내려도 그 자리 {r}")
        # ④ 두 번째 기기 (B)
        B = await open_kid("BBBBB", "주호")
        await B.evaluate("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until(B, "()=>HOUSE.place()==='village'")
        await B.evaluate("()=>{ HOUSE.TW.seed='2026-10-07'; HOUSE.twEnterGo('easy'); }")
        ok(await until(B, "()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "④ 기기 B 도 같은 타워로")
        r = await E("()=>HOUSE.twNetPath()")
        ok(re.match(r"^/hy/day/tw\d{8}e$", r) is not None, f"④ 같이 쓰는 곳 = /hy/day/tw<날짜>e {r}")
        # A 를 2층 발판 위로 → B 에서 보임
        await E("()=>{ const T=HOUSE.TW, c=T.cps[1]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); }")
        await E("()=>{ HOUSE.TW.seed='2026-10-07'; HOUSE.twBuild('easy'); const T=HOUSE.TW, c=T.cps[1]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); }")   # (위에서 다른 날 타워로 바꿨으니 같은 타워로)
        ok(await until(B, """()=>{ const c=HOUSE.TWN.peers.AAAAA, s=HOUSE.TW.cps[1]; return HOUSE.twNetCount()===1 && c && c.g.position.distanceTo(new THREE.Vector3((s.min.x+s.max.x)/2, s.max.y, (s.min.z+s.max.z)/2))<0.6 && document.getElementById('twPeers').textContent==='👥 1'; }""", 60), "④ B 화면에 A(루아)가 보임")
        r = await B.evaluate("""()=>{ const c=HOUSE.TWN.peers.AAAAA, T=HOUSE.TW, s=T.cps[1]; return c ? [c.nm, c.g.visible, +c.g.position.distanceTo(new THREE.Vector3((s.min.x+s.max.x)/2, s.max.y, (s.min.z+s.max.z)/2)).toFixed(2), !!c.tag, document.getElementById('twPeers').textContent] : null; }""")
        ok(r and r[0] == "루아" and r[1] and r[2] < 0.6 and r[3] and r[4] == "👥 1", f"④ 이름표 루아 · 2층 발판 위에 · 👥 1 {r}")
        ok(await until(A, "()=>HOUSE.twNetCount()===1 && HOUSE.TWN.peers.BBBBB && HOUSE.TWN.peers.BBBBB.nm==='주호'", 60), "④ A 화면에도 B(주호)")
        r = await A.evaluate("()=>{ const d=HOUSE.TWN.tree; return [Object.keys(d).sort(), Array.isArray(d.AAAAA.p) && d.AAAAA.p.length, typeof d.BBBBB.i.av]; }")
        ok(r[0] == ["AAAAA", "BBBBB"] and r[1] == 6 and r[2] == "object", f"④ 저장 모양 i={{n,av}} · p=[x,y,z,방향,동작,시각] {r}")
        # A 움직이면 B 에서 따라감
        await E("()=>{ const T=HOUSE.TW, c=T.cps[2]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); }")
        ok(await until(B, """()=>{ const c=HOUSE.TWN.peers.AAAAA, s=HOUSE.TW.cps[2]; return c && c.g.position.distanceTo(new THREE.Vector3((s.min.x+s.max.x)/2, s.max.y, (s.min.z+s.max.z)/2))<0.6; }""", 60), "④ A 가 3층으로 → B 화면에서도 따라감")
        await B.screenshot(path=OUT + "tower453_peer.png")
        # A 가 나가면 B 에서 사라짐
        await E("()=>HOUSE.twLeave()")
        ok(await until(A, "()=>HOUSE.place()==='village' && !HOUSE.TW.on"), "④ A 마을로")
        ok(await until(B, "()=>HOUSE.twNetCount()===0", 60), "④ A 가 나가면 B 화면에서 사라짐 · 👥 0")
        r = db_get("/hy/day")
        ok(r and all("AAAAA" not in v for k, v in r.items() if k.startswith("tw")), f"④ 나가면 서버(타워 자리)에서 내 자리 지움 — 마을 자리(vl, v473)는 마을에 있으니 남음 {list((r or {}).keys())}")
        await B.evaluate("()=>HOUSE.twLeave()")
        await br.close()
    r = real_errs(errs)
    print("errs", r)
    if bad or r: print("결과: 실패", len(bad)); sys.exit(1)
    print("결과: 통과")
asyncio.run(main())
