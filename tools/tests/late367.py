"""(v367) 사용자: 아이들이 안 왔는데 교실 배틀 기록이 생김 — 어제 배틀 끝에 한꺼번에 보내 시트 서버가 바빠(busy) 기기에 쌓였다가 오늘 보내졌다(날짜 = 받은 때)
  ① 모든 기록에 at(실제로 끝난 때) — 쌓였다 늦게 가도 같은 at · 서버 Code.gs 가 그 시각으로 적음
  ② 배틀·레이드 끝 기록은 0~8초 흩어서 보냄 (테스트 모드에선 바로)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        r = await pg.evaluate("""async()=>{ const sent=[]; let busy=true; Online.on=()=>true; Online.post=b=>{ sent.push(JSON.parse(JSON.stringify(b))); return Promise.resolve(busy ? {ok:false, err:'busy'} : {ok:true}); };
            localStorage.removeItem(Online.QK); const t0=Date.now();
            await Online.submit({nick:'민준', score:900, rule:'study-battle', diff:'study'});
            const q=Online.qGet(); busy=false; await new Promise(r=>setTimeout(r, 1200));
            await Online.submit({nick:'민준', score:100, rule:'study', diff:'study'}); await new Promise(r=>setTimeout(r, 300));
            return {n:sent.length, at0:sent[0].at, last:sent.map(b=>[b.score, b.at]), t0, queued:q.length, left:Online.qGet().length}; }""")
        print(r)
        ok(r["at0"] and abs(r["at0"] - r["t0"]) < 2000, "기록에 at(끝난 때)")
        resend = [x for x in r["last"] if x[0] == 900]
        ok(r["queued"] == 1 and len(resend) >= 2 and resend[0][1] == resend[-1][1], f"쌓였다 다시 보내도 같은 at {resend}")
        ok(r["left"] == 0, "쌓인 줄 다 보냄")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    # 서버 코드: at 으로 날짜
    js = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "server", "Code.gs"), encoding="utf-8").read()
    ok('return when;' in js and 'd.at' in js, "Code.gs 가 at 으로 날짜를 적음")
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
