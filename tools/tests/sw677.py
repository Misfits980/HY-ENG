"""(v677) 선생님 PC 크롬: 켤 때마다 첫 화면까지 7초 넘게 — 서비스 워커가 caches.match(…, {ignoreSearch:true}) 로 발음 저장소(3,620개)까지 뒤져 한 번에 4.2초
   진짜 서비스 워커로 http://127.0.0.1 을 열고 발음 저장소에 3,600개를 넣은 뒤
   ① 다시 켜면 index.html 받기 시작(responseStart)이 1초 안 (예전 4초+)
   ② 서버가 오류를 주면(끊김) 기다리지 않고 저장해 둔 화면 (주소 뒤 ?… 가 붙어 있어도)
   ③ 서버가 느리면(4초) 3초 뒤 저장해 둔 화면 먼저
   ④ 그림 문자 글꼴(구글) 링크가 첫 화면을 막지 않음 (media=print → all)"""
import asyncio, os, re, sys, threading, http.server, functools, socket, time
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.abspath(os.path.join(HERE, "..", ".."))
ST = {"down": False, "slow": 0}
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self): self.send_header("Cache-Control", "max-age=600"); super().end_headers()
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path.split("?")[0]
        if ST["down"]: self.send_response(503); self.end_headers(); return
        if p in ("/", "/index.html") and ST["slow"]: time.sleep(ST["slow"])
        if p == "/" : p = "/index.html"
        if p == "/three.min.js": p = "/tools/tests/fake_three.js"
        if p.startswith("/audio/") and p.endswith(".mp3"): self.send_response(404); self.end_headers(); return   # 발음은 시험에서 안 받음
        self.path = p; return super().do_GET()
def serve():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=SITE)); threading.Thread(target=srv.serve_forever, daemon=True).start(); return port
NAV = "()=>{ const n=performance.getEntriesByType('navigation')[0]; return [Math.round(n.responseStart), !!navigator.serviceWorker.controller, typeof GAME_VER!=='undefined' ? GAME_VER : null]; }"
async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    port = serve(); U = f"http://127.0.0.1:{port}/"
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1024, "height": 700})
        await ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())
        pg = await ctx.new_page(); await pg.goto(U + "index.html"); await pg.wait_for_timeout(1500)
        for _ in range(60):
            if await pg.evaluate("()=>!!navigator.serviceWorker.controller"): break
            await pg.reload(); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("()=>!!navigator.serviceWorker.controller"), "서비스 워커가 화면을 맡음")
        n = await pg.evaluate("""async()=>{ const c=await caches.open('hyeng-audio-v1'); const b=new Blob([new Uint8Array(200)]); const L=[]; for(let i=0;i<3600;i++) L.push(c.put(location.origin+'/audio/w'+i+'.mp3', new Response(b))); await Promise.all(L); return (await c.keys()).length; }""")
        t = await pg.evaluate("async()=>{ const t=performance.now(); await caches.match(location.origin+'/index.html', {ignoreSearch:true}); return Math.round(performance.now()-t); }")
        print(f"    (발음 저장소 {n}개 · 예전 방식 찾기 한 번 {t}ms)")
        await pg.goto(U + "index.html"); await pg.wait_for_timeout(800); r = await pg.evaluate(NAV)
        ok(r[1] and r[0] < 1000 and r[2], f"① 다시 켜기: 받기 시작 {r[0]}ms (1초 안) {r}")
        ST["down"] = True
        await pg.goto(U + "index.html?room=1234"); await pg.wait_for_timeout(800); r = await pg.evaluate(NAV)
        ok(r[2] is not None and r[0] < 1500, f"② 서버 오류(끊김) + 주소 뒤 ?… → 저장해 둔 화면 {r}")
        ST["down"] = False; ST["slow"] = 4
        t0 = time.time(); await pg.goto(U + "index.html"); r = await pg.evaluate(NAV); dt = time.time() - t0; ST["slow"] = 0
        ok(r[2] is not None and 2.5 < r[0] / 1000 < 3.8, f"③ 서버가 4초 걸리면 3초 뒤 저장해 둔 화면 먼저 (받기 시작 {r[0]}ms)")
        r = await pg.evaluate("()=>{ const l=[...document.querySelectorAll('link[rel=stylesheet]')].find(x=>/fonts\\.googleapis/.test(x.href)); return l ? [l.media, l.getAttribute('onload')] : null; }")
        ok(r and r[0] in ("print", "all") and "media" in (r[1] or ""), f"④ 구글 글꼴이 첫 화면을 막지 않음 {r}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
