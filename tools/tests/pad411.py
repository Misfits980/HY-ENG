"""(v411) 공용 패드 = 아이마다 따로 — 사용자 QA: "공용 패드에서 My Town 집·가방·보석이 섞임 · 캐릭터 3개만 · 레이드 연습은 패드 첫 아이만"
  ① My Town: 공용 패드는 들어오면 👤 나는 누구? → 고른 아이 칸에 저장 (다른 아이와 안 섞임) · 서버 /hy/life/sv/<아이> → 다른 패드에서 이어서 · 내 기기는 예전 그대로
  ② 게임: 공용 패드는 캐릭터 모두 열림 ③ 레이드 연습 = 아이마다 한 번"""
import asyncio, sys, os, json, re
from urllib.parse import urlparse, parse_qs, unquote
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
DB = {"hy": {"roster": {"t": {"a1": {"n": "A1", "e": "🍎"}}, "k": {"k1": {"n": "민준", "t": "a1"}, "k2": {"n": "서연", "t": "a1"}}}}}
def getp(path):
    o = DB
    for k in [x for x in path.split("/") if x]:
        if not isinstance(o, dict) or k not in o: return None
        o = o[k]
    return o
def setp(path, v):
    P = [x for x in path.split("/") if x]; o = DB
    for k in P[:-1]: o = o.setdefault(k, {})
    if v is None: o.pop(P[-1], None)
    else: o[P[-1]] = v
async def fb(r):
    u = urlparse(r.request.url)
    if "firebasedatabase" not in u.netloc: return await route(r)
    path = unquote(u.path)[:-5] if u.path.endswith(".json") else unquote(u.path); m = r.request.method
    if m == "GET": return await r.fulfill(status=200, content_type="application/json", body=json.dumps(getp(path)))
    body = r.request.post_data; val = json.loads(body) if body else None
    if m == "PUT": setp(path, val)
    if m == "DELETE": setp(path, None); val = None
    return await r.fulfill(status=200, content_type="application/json", body=json.dumps(val))

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        async def pad(nick):
            ctx = await br.new_context(viewport={"width": 1024, "height": 768}, has_touch=True)
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(nick + ": " + str(e)))
            await pg.route("**/*", fb); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
            await pg.evaluate("(n)=>{ localStorage.clear(); sessionStorage.clear(); localStorage.setItem('hyeng_nick', n); }", nick)
            await pg.reload(); await pg.wait_for_timeout(2500); return pg
        A = await pad("한양패드")
        async def until(pg, js, n=60):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass   # 다시 여는 중
                await pg.wait_for_timeout(250)
            return False
        ok(await until(A, "()=>document.getElementById('who').classList.contains('on') && document.querySelectorAll('#whoBody [data-wk]').length===2"), "공용 패드: 들어오면 👤 나는 누구? (반 명단 이름)")
        await A.screenshot(path=OUT + "pad411_who.png")
        await A.evaluate("()=>document.querySelector('#whoBody [data-wk=k1]').click()"); await A.wait_for_timeout(3000)
        r = await A.evaluate("()=>[HOUSE.PAD.id, document.getElementById('hWho').innerText.trim(), document.getElementById('who').classList.contains('on'), HOUSE.skey('hyeng_proto_gems')]")
        ok(r[0] == "k1" and "민준" in r[1] and not r[2] and r[3] == "hyeng_proto_@k1_gems", f"민준으로 들어옴 · 저장 칸 = 민준 칸 {r}")
        await A.evaluate("()=>{ HOUSE.setGems(50); HOUSE.setBait(3); }")
        await A.wait_for_timeout(4800)
        sv = getp("/hy/life/sv/k1")
        ok(sv and sv["n"] == "민준" and json.loads(json.loads(sv["d"])["gems"]) == 50, f"4초 뒤 서버에 민준 것 {sv and sv.get('n')}")
        # 서연으로 바꿈 → 따로
        await A.evaluate("()=>{ document.getElementById('whoBody').innerHTML=''; document.getElementById('hWho').click(); }"); await until(A, "()=>document.querySelectorAll('#whoBody [data-wk]').length===2")
        await A.evaluate("()=>document.querySelector('#whoBody [data-wk=k2]').click()"); await until(A, "()=>{ try{ return HOUSE.PAD.id==='k2'; }catch(e){ return false; } }"); await A.wait_for_timeout(1500)
        r = await A.evaluate("()=>[HOUSE.PAD.id, HOUSE.gems(), HOUSE.bait()]")
        ok(r == ["k2", 0, 10], f"서연으로 바꾸면 서연 것 (민준 보석·미끼와 안 섞임) {r}")
        await A.evaluate("()=>HOUSE.setGems(7)"); await A.wait_for_timeout(300)
        await A.evaluate("()=>{ document.getElementById('whoBody').innerHTML=''; document.getElementById('hWho').click(); }"); await until(A, "()=>document.querySelectorAll('#whoBody [data-wk]').length===2")
        await A.evaluate("()=>document.querySelector('#whoBody [data-wk=k1]').click()")
        ok(await until(A, "()=>{ try{ return HOUSE.PAD.id==='k1' && HOUSE.gems()===50 && HOUSE.bait()===3; }catch(e){ return false; } }"), "다시 민준 → 민준 것 그대로")
        ok(getp("/hy/life/sv/k2") is not None and json.loads(json.loads(getp("/hy/life/sv/k2")["d"])["gems"]) == 7, "이름을 바꿀 때 서연 것도 서버에")
        # 다른 공용 패드에서 민준 → 서버에서 이어서
        B = await pad("한양패드2")
        await until(B, "()=>document.querySelectorAll('#whoBody [data-wk]').length===2")
        await B.evaluate("()=>document.querySelector('#whoBody [data-wk=k1]').click()")
        ok(await until(B, "()=>{ try{ return HOUSE.PAD.id==='k1' && HOUSE.gems()===50; }catch(e){ return false; } }", 60), "다른 패드에서 민준 → 서버에서 보석·미끼 이어서")
        ok(await B.evaluate("()=>HOUSE.bait()") == 3, "미끼도 이어서")
        # 내 기기 (공용 아님) — 예전 그대로
        C = await pad("민준")
        r = await C.evaluate("()=>[HOUSE.PAD.shared, document.getElementById('who').classList.contains('on'), HOUSE.skey('hyeng_proto_gems'), document.getElementById('hWho').hidden]")
        ok(r == [False, False, "hyeng_proto_gems", True], f"내 기기: 묻지 않고 예전 칸 {r}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        # ② 게임: 공용 패드 캐릭터 · ③ 레이드 연습 아이마다
        ctx = await br.new_context(viewport={"width": 1194, "height": 834}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        G = await ctx.new_page(); G.on("pageerror", lambda e: errs.append("G " + str(e))); await boot(G)
        r = await G.evaluate("()=>{ localStorage.setItem('hyeng_unlock_v1', JSON.stringify({got:{}, seeded:1})); const a=CHARACTERS.filter(c=>Unlock.has(c.id)).length; localStorage.setItem('hyeng_nick','한양패드'); const b=CHARACTERS.filter(c=>Unlock.has(c.id)).length; return [a, b, CHARACTERS.length]; }")
        ok(r[0] == 3 and r[1] == r[2], f"공용 패드는 캐릭터 모두 열림 (내 기기 새것 3 → 공용 {r[1]}/{r[2]})")
        r = await G.evaluate("()=>{ Raid.pick={id:'k1'}; Raid.me='k1'; const a=RaidTut.key(); localStorage.setItem(a,'1'); Raid.pick={id:'k2'}; Raid.me='k2'; return [a, RaidTut.key(), RaidTut.done()]; }")
        ok(r[0] != r[1] and r[2] is False, f"레이드 연습: 공용 패드는 아이마다 따로 {r}")
        ok(not errs, "오류 없음 (게임) " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
