"""(v379) 아이폰 측정: 영어 읽기를 끄면 0.3초 멈춤이 사라짐 → 아이폰·아이패드는 달리는 동안 읽기 기본 끔
  · 설정 「달리는 중에도 발음 듣기」로 켤 수 있음 · 공부 화면·결과창은 그대로 읽음 · 갤럭시·컴퓨터는 그대로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

IPH = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
GAL = "Mozilla/5.0 (Linux; Android 14; SM-S921N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36"
SPY = "()=>{ window._said=[]; const f=Voice.speak.bind(Voice); Voice.speak=function(t){ window._said.push(String(t)); return f.apply(this, arguments); }; Voice.broken=false; Voice.on=true; }"
RUN = """()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; G.dir='e2k'; startGame();
  return new Promise(r=>setTimeout(()=>{ const s=G.sets.find(s=>!s.judged); G.lane=s.q.answer; P.x=laneX(s.q.answer, G.lanes); judge(s);
    setTimeout(()=>r([window._said.slice(), document.getElementById('plabel').innerHTML.indexOf('다시 듣기')>=0 || !!document.getElementById('prompt').__word]), 500); }, 900)); }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for name, ua in (("아이폰", IPH), ("갤럭시", GAL)):
            ctx = await br.new_context(viewport={"width": 390, "height": 844}, user_agent=ua)
            await ctx.add_init_script("window.HY_FB_LOCAL=true;")
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
            await pg.evaluate(SPY)
            r = await pg.evaluate(RUN)
            print(name, r)
            if name == "아이폰":
                ok(r[0] == [] and not r[1], f"아이폰: 달리는 동안 읽지 않음 · 다시 듣기 없음 {r}")
                await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(300)
                await pg.evaluate("()=>{ window._said=[]; Voice.say('apple'); }")
                ok(await pg.evaluate("()=>window._said") == ["apple"], "판 밖(결과창·공부)에서는 그대로 읽음")
                # 설정에서 켜기
                await pg.evaluate("()=>{ syncSettings(); }")
                ok(await pg.evaluate("()=>!document.getElementById('setRunVoice').classList.contains('sel')"), "설정: 기본 꺼짐 표시")
                await pg.evaluate("()=>document.getElementById('setRunVoice').click()")
                ok(await pg.evaluate("()=>[document.getElementById('setRunVoice').classList.contains('sel'), localStorage.getItem('hyeng_runvoice')]") == [True, "1"], "설정에서 켜면 기억")
                await pg.evaluate("()=>{ window._said=[]; }")
                r = await pg.evaluate(RUN)
                ok(len(r[0]) >= 1, f"켜면 달리는 동안에도 읽음 {r}")
                await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); Voice.on=false; syncSettings(); }")
                ok(await pg.evaluate("()=>document.getElementById('setRunVoice').classList.contains('off')"), "발음 듣기를 끄면 흐리게")
            else:
                ok(len(r[0]) >= 1, f"갤럭시: 그대로 읽음 {r}")
            await ctx.close()
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
