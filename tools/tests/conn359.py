"""(v359) 사용자 사진: 선생님 TV 점수가 멈추고(흐림) · 아이 화면에 다른 아이가 안 보이고 0등 — 실시간 연결이 조용히 끊김
  ① 배틀: 실시간 소식이 6초 넘게 없으면 서버에서 방을 직접 읽어 씀 (🔄 연결 다시 잡는 중) ② 내가 목록에 없어도 0등 없음 (내 점수로 자리)
  ③ FB 감시: 닫혔거나 45초 소식 없는 연결은 다시 연결"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await T.evaluate("""()=>FB.set('/battle/3939', {cfg:{set:'elem', from:0, to:2, words:[], dur:300, qt:['mean'], lvl:'easy', made:Date.now()}, st:{s:'run', t0:Date.now()-5000},
            p:{a1:{n:'서연', sc:40, ok:4, at:Date.now()}}})""")
        await K.evaluate("()=>{ Battle.join('3939', {id:'k1', n:'민준', t:'a'}); }"); await K.wait_for_timeout(1200)
        # 실시간이 끊긴 것처럼: 이 기기의 듣기를 멈춘 사본으로 바꿈
        await K.evaluate("()=>{ const t=JSON.parse(JSON.stringify(Battle.h.get())); Battle.h.close(); Battle.h={get:()=>t, up:()=>false, close(){}}; Battle._evAt=Date.now()-10000; }")
        await T.evaluate("()=>FB.update('/battle/3939/p/a2', {n:'하준', sc:90, ok:9, at:Date.now()})"); await K.wait_for_timeout(3800)
        r = await K.evaluate("()=>[Object.keys(Battle.T().p||{}).sort(), !!Battle._poll, Battle.rank()[0]]")
        ok(r[0] == ["a1", "a2", "k1"] and r[1] and r[2] == "a2", f"연결이 끊겨도 직접 읽어 다른 아이가 보임 {r}")
        r = await K.evaluate("()=>[...document.querySelectorAll('#rdC .btLvR b')].map(b=>b.textContent)")
        ok("하준" in r, f"문제 아래 순위에도 {r}")
        # 0등 없음 — 서버 목록에 내가 없어도
        r = await K.evaluate("()=>{ Battle._poll={st:{s:'run', t0:Date.now()-5000}, cfg:Battle.cfg(), p:{a1:{n:'서연', sc:40}}}; Battle._pollAt=Date.now()+1; Battle.sc=50; return Battle.rank().indexOf('k1')+1; }")
        ok(r == 1, f"목록에 내가 없어도 내 점수로 자리 (0등 아님) {r}")
        await K.evaluate("()=>{ Battle.ended=false; Battle._finish(['a1']); }"); await K.wait_for_timeout(200)
        r = await K.evaluate("()=>document.querySelector('.rdEndT') && document.querySelector('.rdEndT').innerText")
        ok(r and "0등" not in r and "1등" in r, f"끝 화면 0등 없음 {r}")
        await K.evaluate("()=>{ Battle.role=null; clearInterval(Battle.t); }")
        # 선생님 TV: 끊기면 안내
        await T.evaluate("()=>{ Battle.reopen('3939'); }"); await T.wait_for_timeout(600)
        await T.evaluate("()=>{ const t=JSON.parse(JSON.stringify(Battle.h.get())); Battle.h.close(); Battle.h={get:()=>t, up:()=>false, close(){}}; Battle._evAt=Date.now()-10000; }")
        await T.evaluate("()=>FB.update('/battle/3939/p/a3', {n:'지우', sc:10, at:Date.now()})"); await T.wait_for_timeout(3800)
        r = await T.evaluate("()=>[!!document.querySelector('.btLag'), [...document.querySelectorAll('.btRow b')].map(b=>b.textContent)]")
        ok(r[0] and "지우" in r[1], f"TV: 「연결 다시 잡는 중」 + 새 아이 보임 {r}")
        await T.evaluate("()=>{ Battle.role=null; clearInterval(Battle.t); }")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
