"""(v416) 사용자 QA 「분신술」 — 랭킹 단어 수집에 같은 아이가 두 줄 (스트로베리 856 · 👤스트로베리 856 / 김지후 211 · 👤김지후 210 / SEOWON#0010 782 · 👤SEOWON 1) + 선생님 3,508 이 1등
  ① 화면: 👤 뗀 이름이 같으면 한 줄(큰 값) · 태그가 서로 다르면 다른 아이 · 선생님 줄 빼기 · 결과 화면 '내 순위'도 👤 없이 찾음
  ② 공용 패드는 도감(단어 수)을 안 보냄 (여러 아이가 모은 단어라)
  ③ 서버 Code.gs v5 (node rank416_srv.js)"""
import asyncio, sys, os, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

SHOT = [{"nick":"영어선생님","score":3508,"me":True},{"nick":"스트로베리","score":856,"title":"t-daily"},{"nick":"👤스트로베리","score":856},{"nick":"SEOWON","tag":"0010","score":782},
        {"nick":"👤김지환","tag":"0008","score":735},{"nick":"김지후","score":211},{"nick":"👤김지후","score":210},{"nick":"👤패트와 매트(패트)","score":207},{"nick":"👤빈","tag":"0009","score":51},
        {"nick":"👤이무이무시완","score":17},{"nick":"👤박유범","score":6},{"nick":"👤SEOWON","score":1},{"nick":"하준","tag":"0020","score":5},{"nick":"하준","tag":"0021","score":4}]

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        r = await pg.evaluate("(L)=>rankMerge(L).map(x=>x.nick+(x.tag?'#'+x.tag:'')+'='+x.score)", SHOT)
        print(r)
        ok(r[:3] == ["스트로베리=856", "SEOWON#0010=782", "김지환#0008=735"], f"선생님 빠짐 · 스트로베리 한 줄 · SEOWON 한 줄(782) {r[:3]}")
        ok(r.count("김지후=211") == 1 and not any(x.startswith("김지후=210") for x in r), "김지후 한 줄 (큰 값 211)")
        ok(not any("👤" in x for x in r), "👤 없이 이름만")
        ok(not any(x.startswith("SEOWON=1") for x in r), "공용 패드의 👤SEOWON 1 은 SEOWON 에 합쳐짐")
        ok("하준#0020=5" in r and "하준#0021=4" in r, "태그가 다른 같은 이름은 다른 아이")
        h = await pg.evaluate("(L)=>{ const d=document.createElement('div'); d.innerHTML=onlineRows(L, true); return [d.querySelectorAll('.rrow').length, d.textContent.includes('영어선생님'), d.querySelectorAll('.meTag').length]; }", SHOT)
        ok(h[0] == 10 and not h[1], f"랭킹 화면 14줄 → 10줄 (선생님·분신 3) {h}")
        # ② 공용 패드는 도감을 안 보냄
        sent = await pg.evaluate("""async()=>{ const S=[]; const p0=Online.post; Online.post=b=>{ S.push(JSON.parse(JSON.stringify(b))); return Promise.resolve({ok:true}); };
            localStorage.setItem('hyeng_nick','한양패드'); await Online.submit({nick:'한양패드', score:10, diff:'normal', rule:'normal', dex:900});
            localStorage.setItem('hyeng_nick','김지후'); await Online.submit({nick:'김지후', score:10, diff:'normal', rule:'normal', dex:211});
            Online.post=p0; return S.map(b=>[b.nick, b.dex]); }""")
        ok(sent[0][1] == "" and sent[1][1] == 211, f"공용 패드 = 단어 수 안 보냄 · 내 기기 = 보냄 {sent}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "rank416_srv.js")], capture_output=True, text=True)
    print(r.stdout.strip().split("\n")[-11:] and "\n".join(l for l in r.stdout.split("\n") if l.startswith(("OK", "FAIL"))))
    ok(r.returncode == 0, "서버 Code.gs v5 랭킹 (rank416_srv.js)")
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
