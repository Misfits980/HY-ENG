"""(v355) 사용자: 숙제를 냈는데 나갔다 들어오면 사라져 끌 수 없음 (서버에는 있었다)
  ① 진짜 서버처럼(REST) 저장되면 「냈어요」 · 다시 들어와도 카드·끝내기
  ② 서버를 못 읽으면(멈춤·오류) 숙제를 지우지 않고 「⚠️ 못 읽었어요 · 🔄 다시 불러오기」 · 다시 불러오면 카드
  ③ 서버가 저장을 거절(401)하면 「⚠️ 저장되지 않았어요 (오류 401)」 · 카드 없음"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

DB = {}
FLAG = {"deny": False, "rdfail": False}

def getp(path):
    o = DB
    for k in [x for x in path.split('/') if x]:
        if not isinstance(o, dict) or k not in o: return None
        o = o[k]
    return o

def setp(path, v, merge):
    P = [x for x in path.split('/') if x]; o = DB
    for k in P[:-1]: o = o.setdefault(k, {})
    if merge and isinstance(v, dict):
        cur = o.setdefault(P[-1], {})
        for k, x in v.items(): cur[k] = x
    elif v is None: o.pop(P[-1], None)
    else: o[P[-1]] = v

async def fb(r):
    u = r.request.url; m = r.request.method; path = u.split('.app')[1].split('.json')[0]
    if m == 'GET':
        if 'text/event-stream' in (r.request.headers.get('accept') or ''): return await r.abort()
        if FLAG["rdfail"] and '/hy/hw' in path: return await r.abort()
        return await r.fulfill(status=200, content_type='application/json', body=json.dumps(getp(path)))
    if FLAG["deny"] and '/hy/hw' in path: return await r.fulfill(status=401, content_type='application/json', body='{"error":"Permission denied"}')
    v = json.loads(r.request.post_data or 'null'); setp(path, v, m == 'PATCH')
    return await r.fulfill(status=200, content_type='application/json', body=json.dumps(v))

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 820, "height": 1180})
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e)))
        await T.route("**/*", lambda r: fb(r) if ('firebasedatabase.app' in r.request.url or 'firebaseio.com' in r.request.url) else route(r))
        await T.goto(ORIGIN + "index.html"); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }")
        async def open_exam():
            await T.reload(); await T.wait_for_timeout(1800)
            await T.evaluate("()=>{ window.confirm=()=>true; Admin.open(); }"); await T.wait_for_timeout(500)
            await T.evaluate("()=>document.querySelector('#adTabs [data-t=\"exam\"]').click()"); await T.wait_for_timeout(1500)
        async def cnt(): return await T.evaluate("()=>document.querySelectorAll('[data-ad=\"hwEnd\"]').length")
        async def toast(): return await T.evaluate("()=>{ const m=document.getElementById('adToast'); return m ? m.textContent : ''; }")
        await open_exam()
        ok(await T.evaluate("()=>FB.mode()") == "fb", "진짜 서버 모드")
        await T.evaluate("()=>document.querySelector('[data-ad=\"hwOpen\"]').click()"); await T.wait_for_timeout(1500)
        t = await toast()
        ok(await cnt() == 1 and "냈어요" in t and DB.get('hy', {}).get('hw', {}).get('cur'), f"저장되면 냈어요 · 카드 {t}")
        await open_exam()
        ok(await cnt() == 1, "나갔다 들어와도 카드·끝내기 있음")
        # 서버를 못 읽음 → 들어와도 숙제가 지워지지 않고 안내
        FLAG["rdfail"] = True
        await open_exam()
        r = await T.evaluate("()=>[HyHW.rdErr, !!document.querySelector('[data-ad=\"hwReload\"]')]")
        ok(r == [1, True], f"못 읽으면 「못 읽었어요 · 다시 불러오기」 {r}")
        FLAG["rdfail"] = False
        await T.evaluate("()=>document.querySelector('[data-ad=\"hwReload\"]').click()"); await T.wait_for_timeout(1200)
        ok(await cnt() == 1 and not await T.evaluate("()=>!!document.querySelector('[data-ad=\"hwReload\"]')"), "다시 불러오면 카드·끝내기")
        # 끝내기
        await T.evaluate("()=>document.querySelector('[data-ad=\"hwEnd\"]').click()"); await T.wait_for_timeout(1500)
        t = await toast()
        ok(await cnt() == 0 and "끝냈어요" in t and not DB.get('hy', {}).get('hw', {}).get('cur'), f"끝내기 → 서버에서도 꺼짐 {t}")
        # 서버가 거절
        FLAG["deny"] = True
        await T.evaluate("()=>document.querySelector('[data-ad=\"hwOpen\"]').click()"); await T.wait_for_timeout(1800)
        t = await toast()
        ok(await cnt() == 0 and "저장되지 않았어요" in t and "401" in t, f"거절되면 알림 · 카드 없음 {t}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
