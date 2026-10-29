"""(v455) 🗼 타워 — 사용자: "타워 안 감정 표현 재밌네(머리 위 말풍선) · 숨은 별 좋다 · 내 최고 높이 선 · 로블록스 타워를 몇 개 더 따라 했으면"
  ① ⭐ 숨은 별: 층마다 하나 · 길 밖 작은 발판 · 잡으면 ⭐ 숫자 · 오늘 처음이면 💎 1 (두 번째는 없음) · 🤖 길 찾기에는 안 들어감
  ② 📏 내 최고 높이 선: 처음엔 없음 → 올라갔다 나가면 저장 → 다시 들어가면 그 높이에 금색 테 + 「내 최고 n층」 · 넘으면 새 최고
  ③ 😀 감정 표현: 😀 단추 → 6개 → 내 머리 위 말풍선 · 친구 화면에도 · 크게 떨어지면 😱 저절로
  ④ 새 장애물: 👀 투명 발판(가까우면 보임) · 🟥 킬브릭(빨간 칸 = 맨 아래) · 🍂 무너지는 발판(밟으면 떨어짐 → 다시) · 🎠 빙글 원판(태워서 돎)
(아래는 v453 시험의 가짜 서버 그대로)
"""
_OLD = """(v453) 🗼 타워 = 잼못타처럼 — 사용자: "타워를 잼못타를 카피해서 · 영어는 넣지 말고 · 애들이 같이 할 수 있게 · 체크포인트가 있으면 안 되더라"
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
        async def until(pg, js, n=60):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(200)
            return False
        A = await open_kid("AAAAA", "루아"); E = A.evaluate
        # ④ 새 장애물이 나오는지 (여러 날)
        r = await E("""()=>{ const T=HOUSE.TW, seen={}; for(const m of ['easy','hard']) for(let d=1; d<=8; d++){ T.seed='2026-11-0'+d; HOUSE.twBuild(m); T.secs.forEach(k=>seen[k]=1); } return Object.keys(seen); }""")
        ok(all(k in r for k in ["ghost", "brick", "crumble", "turn", "wall", "laser", "ice"]), f"④ 새 장애물이 타워에 나옴 {sorted(r)}")
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until(A, "()=>HOUSE.place()==='village'")
        await E("()=>{ HOUSE.TW.seed='2026-11-03'; HOUSE.twEnterGo('hard'); }")
        ok(await until(A, "()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "🔴 어려움 타워 안")
        r = await E("()=>{ const T=HOUSE.TW; return [T.stars.length, T.cps.length-1, T.S.filter(s=>s.starPad).every(s=>s.noWalk), !!T.hiG]; }")
        ok(r == [30, 30, True, False], f"① 별 30개 (층마다 하나) · 별 발판은 길 찾기에서 빠짐 · ② 처음엔 최고 선 없음 {r}")
        # ① 별 잡기
        g0 = await E("()=>HOUSE.gems()")
        r = await E("""()=>{ const T=HOUSE.TW; T.bot=false; const s=T.stars[0], pad=T.S.find(x=>x.starPad); T.p.set((pad.min.x+pad.max.x)/2, pad.max.y+0.01, (pad.min.z+pad.max.z)/2); T.v.set(0,0,0); for(let i=0;i<10;i++) HOUSE.twStep(1/90); HOUSE.twTick(0.05);
            return [s.got, s.sp.visible, T.starN, document.getElementById('twSec').textContent.indexOf('⭐1')>=0]; }""")
        g1 = await E("()=>HOUSE.gems()")
        ok(r[0] and not r[1] and r[2] == 1 and r[3] and g1 == g0 + 1, f"① 별 발판에 올라가 ⭐ 잡음 · HUD ⭐1 · 💎 +1 {r} {g0}→{g1}")
        # ③ 감정 표현 (내 머리 위)
        r = await E("""()=>{ document.getElementById('twEmo').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); const bar=document.getElementById('twEmoBar'); const on=bar.classList.contains('on'), n=bar.querySelectorAll('button').length;
            bar.querySelector('[data-e="💪"]').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); return [on, n, bar.classList.contains('on'), !!HOUSE.hero().emo]; }""")
        ok(r == [True, 6, False, True], f"③ 😀 → 6개 → 💪 고르면 내 머리 위 말풍선 {r}")
        # ④ 투명 발판 · 원판 · 킬브릭 · 무너짐 (몸)
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<60; d++){ T.seed='2026-12-'+d; HOUSE.twBuild('hard'); if(['ghost','turn','brick','crumble'].every(k=>T.secs.includes(k))) break; } T.bot=false; T.cp=5; const out={};
            { const g=T.S.find(s=>s.inv); T.p.set(HOUSE.TWC, 200, HOUSE.TWC); for(let i=0;i<3;i++) HOUSE.twStep(1/90); const far=g.mesh.material.opacity; T.p.set((g.min.x+g.max.x)/2, g.max.y+0.01, (g.min.z+g.max.z)/2); T.v.set(0,0,0); for(let i=0;i<3;i++) HOUSE.twStep(1/90); out.ghost=[+far.toFixed(2), +g.mesh.material.opacity.toFixed(2)]; }
            { const d=T.S.find(s=>s.rot); const c=d.rot.c; T.p.set(c[0]+0.8, d.max.y+0.01, c[1]); T.v.set(0,0,0); const a0=Math.atan2(T.p.z-c[1], T.p.x-c[0]); for(let i=0;i<90;i++) HOUSE.twStep(1/90); const a1=Math.atan2(T.p.z-c[1], T.p.x-c[0]); out.turn=[T.onG, +Math.abs(((a1-a0+Math.PI*3)%(Math.PI*2))-Math.PI).toFixed(2), +Math.hypot(T.p.x-c[0], T.p.z-c[1]).toFixed(2)]; }
            { const k=T.S.find(s=>s.kind==='kill' && s.max.y-s.min.y<0.4), b=T.cps[0]; T.p.set((k.min.x+k.max.x)/2, k.max.y+0.2, (k.min.z+k.max.z)/2); T.v.set(0,0,0); for(let i=0;i<40;i++) HOUSE.twStep(1/90); out.brick=Math.hypot(T.p.x-(b.min.x+b.max.x)/2, T.p.z-(b.min.z+b.max.z)/2)<0.2; }
            { const c=T.S.find(s=>s.crumble); T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); HOUSE.twStep(1/90); const st=c.ft>0; for(let i=0;i<90;i++) HOUSE.twStep(1/90); const gone=!c.on, y=T.p.y<c.max.y-0.5; T.p.set(HOUSE.TWC, 200, HOUSE.TWC); for(let i=0;i<300;i++) HOUSE.twStep(1/90); out.crumble=[st, gone, y, c.on]; }
            return out; }""")
        ok(r["ghost"][0] < 0.1 and r["ghost"][1] > 0.6, f"④ 👀 투명 발판: 멀면 안 보이고 가까우면 보임 {r['ghost']}")
        ok(r["turn"][0] and r["turn"][1] > 0.6 and abs(r["turn"][2] - 0.8) < 0.1, f"④ 🎠 원판에 서 있으면 같이 돎 (같은 거리) {r['turn']}")
        ok(r["brick"], f"④ 🟥 빨간 칸 밟음 → 맨 아래 {r['brick']}")
        ok(r["crumble"] == [True, True, True, True], f"④ 🍂 밟으면 흔들 → 떨어짐 → 몸도 떨어짐 → 3초 뒤 다시 {r['crumble']}")
        # ② 최고 높이 선 — 다시 들어가면 보임
        await E("()=>{ HOUSE.TW.seed='2026-11-03'; HOUSE.twBuild('hard'); const T=HOUSE.TW, c=T.cps[6]; T.maxY=0; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); for(let i=0;i<5;i++) HOUSE.twStep(1/90); HOUSE.twTick(0.05); }")
        await E("()=>HOUSE.twLeave()"); await until(A, "()=>HOUSE.place()==='village' && !HOUSE.TW.on")
        await E("()=>{ HOUSE.TW.seed='2026-11-03'; HOUSE.twEnterGo('hard'); }"); await until(A, "()=>HOUSE.place()==='tower' && HOUSE.TW.on")
        r = await E("()=>{ const T=HOUSE.TW, c=T.cps[6]; return [!!T.hiG, T.hiG && +Math.abs(T.hiG.position.y-c.max.y).toFixed(2), T.hi0>0]; }")
        ok(r[0] and r[1] < 0.2 and r[2], f"② 다시 들어오면 내 최고 높이(7층)에 금색 선 {r}")
        r = await E("()=>{ const T=HOUSE.TW, c=T.cps[8]; T.bot=false; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); for(let i=0;i<5;i++) HOUSE.twStep(1/90); HOUSE.twTick(0.05); return T.hiNew; }")
        ok(r == 1, f"② 넘으면 「새 최고 높이」 {r}")
        await A.screenshot(path=OUT + "tower455_hi.png")
        # ③ 친구에게도 말풍선 · 떨어지면 😱
        B = await open_kid("BBBBB", "주호")
        await B.evaluate("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until(B, "()=>HOUSE.place()==='village'")
        await B.evaluate("()=>{ HOUSE.TW.seed='2026-11-03'; HOUSE.twEnterGo('hard'); }"); await until(B, "()=>HOUSE.place()==='tower' && HOUSE.TW.on")
        await E("()=>{ const T=HOUSE.TW, c=T.cps[1]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); }")
        ok(await until(B, "()=>HOUSE.twNetCount()===1", 60), "③ B 화면에 A")
        await A.wait_for_timeout(800)
        await E("()=>{ HOUSE.TW.emoT=0; HOUSE.twEmote('❤️'); }")
        ok(await until(B, "()=>{ const c=HOUSE.TWN.peers.AAAAA; return c && !!c.emo; }", 40), "③ A 가 ❤️ → B 화면의 A 머리 위에 말풍선")
        r = await E("""()=>{ const T=HOUSE.TW; T.emoT=0; const c=T.cps[4]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); for(let i=0;i<20;i++) HOUSE.twStep(1/90);
            T.p.set(HOUSE.TWC+7.6, T.p.y+0.3, HOUSE.TWC+7.6); T.v.set(0,0,0); for(let i=0;i<900 && !(T.onG && T.p.y<c.max.y-2.5);i++) HOUSE.twStep(1/90); return [T.fall>0, !!HOUSE.hero().emo]; }""")
        ok(r == [True, True], f"③ 크게 떨어지면 😱 저절로 {r}")
        await E("()=>HOUSE.twLeave()"); await B.evaluate("()=>HOUSE.twLeave()")
        await br.close()
    r = real_errs(errs)
    print("errs", r)
    if bad or r: print("결과: 실패", len(bad)); sys.exit(1)
    print("결과: 통과")
asyncio.run(main())
