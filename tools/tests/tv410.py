"""(v410) 📺 TV 실시간 중계 — 사용자: "실시간 중계치고는 너무 수수해 내 TV 화면이"
  LIVE 자막 바 · 입장 · 시작 · 역전(큰 알림+소리, 몰리면 한 줄) · 번개 · 1분 · 10초 카운트다운 · 우승 · 나가면 사라짐 · 아이 기기엔 없음 · 레이드 TV 도"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1280, "height": 720}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        E = T.evaluate
        room = await E("()=>Battle.host({set:'elem', from:0, to:3, words:[], dur:300, mode:'score', qt:['mean'], lvl:'exam', lbl:'G3-4'})")
        await T.wait_for_timeout(700)
        ok(await E("()=>!!document.querySelector('#tvCast .tcLive') && document.body.classList.contains('tcOn')"), "선생님 TV: ● LIVE 중계 바")
        await E(f"()=>FB.update('/battle/{room}/p', {{k1:{{n:'민준', c:'hero', sc:0}}, k2:{{n:'서연', c:'cat', sc:0}}}})"); await T.wait_for_timeout(3500)
        ok(await E("()=>/입장/.test(TvCast.cur||'') || TvCast.q.some(x=>/입장/.test(x.t))") or await E("()=>/입장/.test(document.getElementById('tcMsg').innerText)"), "아이가 들어오면 '입장!'")
        ok(await E("()=>document.querySelectorAll('#scRaid .rdPeople.tcLine .btChr').length")==2, "기다리는 TV: 들어온 아이 캐릭터")
        await E("()=>Battle.hostAct('start')")
        for _ in range(60):
            if await E("()=>Battle.st().s==='run'"): break
            await T.wait_for_timeout(200)
        await T.wait_for_timeout(500)
        ok(await E("()=>/시작/.test(document.getElementById('tcFlash').innerText)"), "시작 → 큰 알림 🏁 시작!")
        await E("()=>{ TvCast.said.go=0; }")
        await E(f"()=>FB.update('/battle/{room}/p/k1', {{sc:30}})"); await T.wait_for_timeout(700)
        await E("()=>{ TvCast.said.lead=0; }")
        await E(f"()=>FB.update('/battle/{room}/p/k2', {{sc:90}})"); await T.wait_for_timeout(700)
        r = await E("()=>[document.getElementById('tcFlash').innerText, document.getElementById('tcFlash').className]")
        ok("역전" in r[0] and "서연" in r[0] and "lead" in r[1], f"역전 → 큰 알림 {r}")
        ok(await E("()=>[TvCast.cur||''].concat(TvCast.q.map(x=>x.t)).some(t=>/번개/.test(t))"), "+60점 → ⚡ 번개 한 방")
        n = await E("()=>{ for(let i=0;i<4;i++) TvCast.say('👑 역전 '+i, 1, 'lead'); return TvCast.q.filter(x=>x.k==='lead').length; }")
        ok(n == 1, f"역전이 몰려도 한 줄 {n}")
        # 남은 시간: 1분 · 10초 카운트다운
        await E("()=>{ const st=Battle.st(); Battle._last.st.t0 = Battle.now() - (300-59)*1000; if(Battle._poll && Battle._poll.st) Battle._poll.st.t0=Battle._last.st.t0; }"); await T.wait_for_timeout(700)
        ok(await E("()=>TvCast.said.m1===1"), "1분 남음 알림")
        await E("()=>{ Battle._last.st.t0 = Battle.now() - (300-8)*1000; if(Battle._poll && Battle._poll.st) Battle._poll.st.t0=Battle._last.st.t0; }"); await T.wait_for_timeout(500)
        r = await E("()=>[document.getElementById('tcFlash').className, document.getElementById('tcFlash').innerText.trim()]")
        ok("cd" in r[0] and r[1].isdigit() and int(r[1]) <= 8, f"10초 카운트다운 {r}")
        await E("()=>Battle.hostAct('end')")
        for _ in range(60):
            if await E("()=>Battle.st().s==='end'"): break
            await T.wait_for_timeout(200)
        await T.wait_for_timeout(500)
        r = await E("()=>[document.getElementById('tcFlash').innerText, TvCast.lastS, TvCast.cur, Battle.st().s]"); ok("우승" in r[0], f"끝 → 🏆 우승 알림 {r}")
        # 아이 기기에는 중계 없음
        K = await ctx.new_page(); await boot(K)
        await K.evaluate(f"()=>Battle.join('{room}', {{id:'k3', n:'지호', t:'all'}})"); await K.wait_for_timeout(800)
        ok(not await K.evaluate("()=>!!document.getElementById('tvCast')"), "아이 기기엔 중계 층 없음")
        await E("()=>{ window.confirm=()=>true; Battle.leave(); }"); await T.wait_for_timeout(300)
        ok(await E("()=>!document.getElementById('tvCast') && !document.body.classList.contains('tcOn')"), "나가면 중계 층 사라짐")
        # 레이드 TV
        rd = await E("()=>{ Raid.MIN=1000; return Raid.host('g34',['vest','cap','glove','beard','belt'], 0, null, 250); }"); await T.wait_for_timeout(800)
        ok(await E("()=>!!document.querySelector('#tvCast .tcLive')"), "레이드 TV 에도 중계 바")
        await E("()=>{ window.confirm=()=>true; Raid.leave(); }"); await T.wait_for_timeout(300)
        ok(await E("()=>!document.getElementById('tvCast')"), "레이드 닫으면 사라짐")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
