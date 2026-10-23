"""(v353) 사용자: 문제 푸는 동안 상대 점수·내 점수가 안 보여 긴장감이 없음
  → 문제 아래 실시간 순위 (.btLive, rdC 칸): 1·2·3등 + 내 앞뒤 · 「n등 OO 까지 x점!」 · 앞지르면 「⚠️ OO 이(가) 앞질렀어요!」 · 올라가면 「⬆️」
  · 점수가 바뀌어도 문제 버튼은 다시 그리지 않음 (누르는 중에 버튼이 바뀌지 않게) · 깃발 레이스·끝난 뒤에는 안 보임"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T); await T.evaluate('()=>{ Battle.FR=false; }')
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K); await K.evaluate('()=>{ Battle.FR=false; }')
        await T.evaluate("""()=>FB.set('/battle/5353', {cfg:{set:'elem', from:0, to:2, words:[], dur:300, qt:['mean'], lvl:'easy', made:Date.now()}, st:{s:'run', t0:Date.now()-3000},
            p:{a1:{n:'서연', sc:40, ok:4, ng:0, at:Date.now()}, a2:{n:'하준', sc:20, ok:2, ng:0, at:Date.now()}, a3:{n:'지우', sc:10, ok:1, ng:0, at:Date.now()}, a4:{n:'도윤', sc:0, ok:0, ng:0, at:Date.now()}}})""")
        await K.evaluate("()=>{ Battle.join('5353', {id:'k1', n:'민준', t:'a'}); }"); await K.wait_for_timeout(1500)
        await K.evaluate("()=>FB.update('/battle/5353/p/k1', {sc:25, ok:3})"); await K.evaluate("()=>{ Battle.sc=25; Battle.ok=3; }"); await K.wait_for_timeout(800)
        r = await K.evaluate("()=>{ const b=document.querySelector('#rdC .btLive'); return b ? [b.querySelector('.btLvTip').innerText, [...b.querySelectorAll('.btLvR')].map(x=>x.innerText.replace(/\\s+/g,' ')), !!b.querySelector('.btLvR.me'), b.querySelector('.btLvN').innerText] : null; }")
        print("live", r)
        ok(r and "서연 까지 15점" in r[0] and "1등" in r[0] and r[2] and "5명 중 2등" in r[3], f"문제 아래 실시간 순위 · 1등까지 몇 점 {r and r[0]}")
        ok(r and not any("도윤" in x for x in r[1]), "5등(멀리 있는 아이)은 안 보임 (1·2·3등 + 내 앞뒤)")
        await K.screenshot(path=OUT + "live353.png")
        # 점수가 바뀌어도 문제 버튼은 그대로 (같은 요소)
        await K.evaluate("()=>{ window._b0=document.querySelector('#rdOpts .stOpt'); }")
        await T.evaluate("()=>FB.update('/battle/5353/p/a2', {sc:30, ok:3})"); await K.wait_for_timeout(900)
        r = await K.evaluate("()=>{ const f=document.querySelector('#rdC .btLvFl'); return [!!(window._b0 && window._b0.isConnected), f ? f.innerText : null, f ? f.className : '']; }")
        ok(r[0], "상대 점수가 바뀌어도 문제 버튼은 다시 그리지 않음")
        ok(r[1] and "하준" in r[1] and "앞질렀어요" in r[1] and "dn" in r[2], f"앞지르면 알림 {r[1]}")
        await K.wait_for_timeout(2800)
        r = await K.evaluate("()=>!!document.querySelector('#rdC .btLvFl')")
        ok(not r, "알림은 잠깐만 (2.5초)")
        # 내가 맞혀서 올라감 (서버보다 이 기기 점수가 먼저)
        await K.evaluate("()=>{ Battle.sc=45; }"); await K.wait_for_timeout(500)
        r = await K.evaluate("()=>{ const f=document.querySelector('#rdC .btLvFl'), t=document.querySelector('#rdC .btLvTip'); return [f ? f.innerText : null, t ? t.innerText : null]; }")
        ok(r[0] and "1등으로" in r[0] and "1등" in (r[1] or ""), f"올라가면 알림 · 1등이면 쫓아오는 아이 {r}")
        # 들어올 때 0점끼리 자리만 바뀐 것은 알리지 않음
        await K.wait_for_timeout(2700)
        await T.evaluate("()=>FB.update('/battle/5353/p/a0', {n:'가온', sc:0, ok:0, ng:0, at:Date.now()})"); await K.wait_for_timeout(700)
        r = await K.evaluate("()=>!!document.querySelector('#rdC .btLvFl')")
        ok(not r, "0점 아이가 들어와 자리만 바뀐 것은 알림 없음")
        # 끝나면 없어짐
        await T.evaluate("()=>FB.update('/battle/5353/st', {s:'end', endAt:Date.now()})"); await K.wait_for_timeout(3500)
        r = await K.evaluate("()=>[Battle.ended, !!document.querySelector('#rdC .btLive')]")
        ok(r == [True, False], f"끝나면 실시간 순위 칸 없음 {r}")
        await K.evaluate("()=>{ Battle.role=null; clearInterval(Battle.t); }")
        # 깃발 레이스 — 위 깃발 칸이 있으니 아래 순위는 안 보임
        await T.evaluate("""()=>FB.set('/battle/5354', {cfg:{set:'elem', from:0, to:2, words:[], dur:300, qt:['mean'], lvl:'easy', mode:'flag', team:true, made:Date.now()}, st:{s:'run', t0:Date.now()-3000}, p:{a1:{n:'서연', sc:40, ok:4, t:'b', at:Date.now()}}})""")
        await K.evaluate("()=>{ Battle.join('5354', {id:'k1', n:'민준', t:'a'}); }"); await K.wait_for_timeout(1500)
        r = await K.evaluate("()=>[!!document.querySelector('#rdOpts'), !!document.querySelector('#rdC .btLive')]")
        ok(r == [True, False], f"깃발 레이스: 실시간 순위 칸 없음 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
