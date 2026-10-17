"""(v322) 진짜 서비스워커 업데이트 길 — 깃허브 페이지처럼 Cache-Control: max-age=600 을 붙여 저장소를 http://127.0.0.1 로 연다.
   어제 버전이 깔린 기기에서 새 버전(GAME_VER·sw.js VERSION·data/talk.json 이 바뀜)을 올렸을 때
   - 새 버전 캐시에 옛 data/*.json 이 들어가지 않는지 (예전엔 HTTP 캐시를 그대로 타서 옛 자료가 남았다)
   - 그림(assets/)을 다시 받지 않는지 (그림 캐시 hyeng-art-* 는 남는다)
   파일은 복사하지 않고, 올린 뒤의 세 파일만 메모리에서 바꿔 준다."""
import asyncio, os, re, sys, threading, http.server, functools, json, socket
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.abspath(os.path.join(HERE, "..", ".."))
VER = re.search(r'const GAME_VER = "(v\d+)"', open(SITE + "/index.html", encoding="utf-8").read()).group(1)
NEW = "v" + str(int(VER[1:]) + 1)
ST = {"bumped": False, "art": 0}
def patched(path):
    if not ST["bumped"]: return None
    if path == "/index.html": return open(SITE + path, encoding="utf-8").read().replace('const GAME_VER = "%s"' % VER, 'const GAME_VER = "%s"' % NEW).encode()
    if path == "/sw.js": return open(SITE + path, encoding="utf-8").read().replace('"hyeng-%s"' % VER, '"hyeng-%s"' % NEW).encode()
    if path == "/data/talk.json": j = json.load(open(SITE + path, encoding="utf-8")); j["__marker"] = NEW; return json.dumps(j, ensure_ascii=False).encode()
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self): self.send_header("Cache-Control", "max-age=600"); super().end_headers()
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/" : p = "/index.html"
        if "/assets/" in p and ST["bumped"]: ST["art"] += 1
        if p == "/three.min.js": p = "/tools/tests/fake_three.js"
        body = patched(p)
        if body is None and p.startswith("/tools/tests/fake_three.js"): body = open(SITE + p, "rb").read()
        if body is not None:
            self.send_response(200); self.send_header("Content-Type", "application/json" if p.endswith(".json") else ("text/javascript" if p.endswith(".js") else "text/html; charset=utf-8"))
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        self.path = p; return super().do_GET()
s = socket.socket(); s.bind(("127.0.0.1", 0)); PORT = s.getsockname()[1]; s.close()
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(H, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
U = "http://127.0.0.1:%d/index.html" % PORT
STATE = """async()=>{ const r=await fetch('data/talk.json'); const j=await r.json(); const ks=await caches.keys();
  let cached=null; try{ const c=await caches.open(ks.find(k=>k==='hyeng-%s')||'none'); const m=await c.match('data/talk.json'); if(m) cached=(await m.json()).__marker||'old'; }catch(e){}
  return {ver:GAME_VER, caches:ks, talkSeen:j.__marker||'old', talkInNewCache:cached} }""" % NEW
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(U, wait_until="domcontentloaded"); await pg.wait_for_function("document.readyState==='complete'", timeout=90000)
        await pg.evaluate("()=>navigator.serviceWorker.ready"); await pg.wait_for_timeout(1500)
        await pg.reload(wait_until="domcontentloaded"); await pg.wait_for_timeout(2500)
        print("day1", await pg.evaluate(STATE.replace("hyeng-" + NEW, "hyeng-" + VER)))
        ST["bumped"] = True
        await pg.goto(U, wait_until="domcontentloaded")
        for k in range(40):
            await pg.wait_for_timeout(500)
            try:
                if await pg.evaluate("async()=>(await caches.keys()).indexOf('hyeng-%s')>=0 && (await caches.keys()).indexOf('hyeng-%s')<0" % (NEW, VER)): break
            except Exception: pass
        await pg.wait_for_timeout(1500)
        st = await pg.evaluate(STATE); print("after update", st, "art refetched", ST["art"])
        if st["talkInNewCache"] != NEW: print("BAD new cache holds old data/talk.json:", st["talkInNewCache"])
        if st["talkSeen"] != NEW: print("BAD page still reads old data/talk.json:", st["talkSeen"])
        if not any(k.startswith("hyeng-art-") for k in st["caches"]): print("BAD art cache was deleted:", st["caches"])
        if ST["art"] > 0: print("BAD update downloaded art again:", ST["art"])
        print("errs", [e for e in errs if "Failed to load" not in e][:3])
        await br.close()
asyncio.run(main())
