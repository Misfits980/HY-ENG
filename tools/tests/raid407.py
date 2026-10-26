"""(v407) 레이드 — 사용자(수업 레이드를 보며): "문제가 다 가리는데 어떻게 알아 · 모션을 튜토리얼 정도는 있어야" + "신규 아이들은 Daily 30 어떻게 해? 유이홍은 명단에 없어서 못 했다"
  ① 빈칸 문장 = 문제 말풍선 안 (무대 가운데 띠 없음) ② 보스 공격마다 할 일 한 줄(.blCall) ③ 🎓 싸우는 법 연습 (기다리는 방) — 단계 · 다시 · 선생님이 시작하면 진짜로
  ④ 🙋 내 이름이 없어요 → 이름 + 반 → 명단(nw) · 같은 이름이면 그 아이 · 이상한 이름 막기"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1194, "height": 834}, service_workers="block", has_touch=True); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host = await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H " + str(e))); await boot(host)
        room = await host.evaluate("()=>{ Raid.MIN=1000; return Raid.host('g34',['vest','cap','glove','beard','belt'], 0, null, 250); }")
        k = await ctx.new_page(); k.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(k)
        E = k.evaluate
        async def until(js, n=60):
            for _ in range(n):
                if await E(js): return True
                await k.wait_for_timeout(100)
            return False
        await E(f"()=>{{ G.char='knight'; Raid.FAST=0; Raid.join('{room}','민준'); }}"); await host.wait_for_timeout(900)
        # ③ 기다리는 방 — 연습 단추
        ok(await E("()=>!!document.querySelector('#scRaid [data-rdtut].new') && !document.getElementById('arena')"), "기다리는 방: 🎓 싸우는 법 연습 (처음이면 반짝 · 시험 브라우저에선 저절로 안 열림)")
        m0 = await E("()=>{ BossLive.manual=false; return BossLive.manual; }")   # 시험 도구(boot)가 true 로 둠 → 실제처럼 false 에서
        await E("()=>document.querySelector('#scRaid [data-rdtut]').click()"); await k.wait_for_timeout(500)
        r = await E("()=>[!!document.getElementById('arena'), !!(Arena.o&&Arena.o.tut), !!document.getElementById('rtBox'), BossLive.manual===true, RaidTut.s]")
        ok(r == [True, True, True, True, 0], f"연습 열림 (보스는 저절로 공격 안 함) {r}")
        await E("()=>document.getElementById('rtGo').click()"); await k.wait_for_timeout(200)
        ok(await E("()=>RaidTut.s===1 && /단어 카드/.test(document.getElementById('rtT').innerText) && document.getElementById('rtGo').hidden"), "① 단어 카드를 톡 = 스킬")
        ok(await E("()=>Arena.cast && Arena.cast.dur>1e8"), "연습 중엔 주문 막대가 안 참 (폭발 없음)")
        await E("()=>{ const q=Arena.q; BossLive.S.busy=0; Arena.tap(q.opts.findIndex(o=>!o.fake && o.en===q.w.en)); }")
        ok(await until("()=>RaidTut.s===2"), "정답 → ② ⚔️ 공격")
        ok(await E("()=>document.querySelector('#bpCtl [data-bp=atk]').classList.contains('rtHot')"), "공격 단추가 반짝")
        await E("()=>{ BossLive.S.busy=0; BossLive.press('atk'); }")
        ok(await until("()=>RaidTut.s===3"), "⚔️ → ③ 그림자 피하기")
        ok(await until("()=>!!(BossLive.S.A && BossLive.S.A.kind==='slam')"), "그림자 공격 (천천히)")
        c = await E("()=>{ const e=document.querySelector('.blCall'); return e ? e.innerText : ''; }")
        ok("옆 칸" in c, f"공격 안내 한 줄 '{c}'")
        await E("()=>{ BossLive.S.busy=0; BossLive.press(BossLive.S.pos>0 ? 'L' : 'R'); }")
        ok(await until("()=>RaidTut.s===4", 80), "옆으로 피함 → ④ 휩쓸기")
        ok(await until("()=>!!(BossLive.S.A && BossLive.S.A.kind==='sweep') && BossLive.S.pos>=1"), "휩쓸기 (가운데 칸에서 시작)")
        ok("맨 왼쪽" in await E("()=>document.querySelector('.blCall').innerText"), "휩쓸기 안내 = 맨 왼쪽 칸")
        await E("()=>{ const S=BossLive.S; S.busy=0; S.pos=0; BossLive.place(S); }")
        ok(await until("()=>RaidTut.s===5", 80), "왼쪽 끝 → ⑤ 공 3개 막기")
        ok(await until("()=>!!(BossLive.S.A && BossLive.S.A.kind==='burst')"), "공 3개")
        ok(await until("()=>/다시 해 봐요/.test(document.getElementById('rtT').innerText)", 80), "안 막으면 '다시 해 봐요' (맞아도 하트 안 줄고 다시)")
        await E("()=>RaidTut.step(6)"); await k.wait_for_timeout(800)
        ok(await E("()=>RaidTut.s===6 && Arena.q.opts.some(o=>o.fake)") or await E("()=>RaidTut.s===6"), "⑥ 가짜 카드")
        # 선생님이 시작 → 진짜 아레나로
        await host.evaluate("()=>Raid.hostAct('start')")
        ok(await until("()=>!!(Arena.o && Arena.o.raid) && !document.getElementById('rtBox')", 80), "선생님이 시작 → 연습 닫고 진짜 레이드 아레나")
        r = await E("()=>[BossLive.manual, RaidTut.done()]")
        ok(r == [False, True], f"보스 공격 다시 저절로 · 이 기기는 연습함으로 기억 {r}")
        # ① 빈칸 문장은 말풍선 안 · ② 공격 안내
        await E("()=>{ BossLive.manual=true; const w=WORD_BANK.find(x=>x.en==='crab'); const st={pre:'We saw a red ', post:' under a big rock.', ko:'우리는 큰 바위 밑에서 빨간 게를 봤어요.'}; Arena.o.q=()=>({w, ko:w.ko, emo:'', opts:[w,{en:'sure',ko:'x'},{en:'crb',ko:'',fake:1}], ko2:true, st}); Arena.next(); }")
        await k.wait_for_timeout(300)
        r = await E("()=>{ const Q=document.getElementById('arQ'), s=Q.querySelector('.arSent'), b=document.querySelector('#arStage .rsBoss, #arStage .rsBossIn'); const qr=Q.getBoundingClientRect(), br=b?b.getBoundingClientRect():null; return [!!s, document.querySelectorAll('#arStage > .arSent').length, br ? (qr.right<=br.left || qr.bottom<=br.top) : null]; }")
        ok(r[0] and r[1] == 0, f"빈칸 문장 = 말풍선 안 (무대 가운데 띠 없음) {r}")
        ok(r[2] in (True, None), f"말풍선이 보스를 안 가림 {r}")
        await E("()=>{ const S=BossLive.S; if(S.A){ BossLive.clear(); S.A=null; } BossLive.launch(performance.now(),'burst'); }")
        ok("🛡" in await E("()=>(document.querySelector('.blCall')||{}).innerText||''"), "공 3개 안내 = 🛡")
        await E("()=>{ const S=BossLive.S; BossLive.clear(); S.A=null; }")
        ok(await E("()=>!document.querySelector('.blCall')"), "공격이 끝나면 안내 사라짐")
        await host.evaluate("()=>Raid.hostAct('end')"); await k.wait_for_timeout(500)

        # ④ 🙋 명단에 없는 아이
        await E("()=>{ try{ Raid.leave(); }catch(e){} Kid.clear(); return FB.set('/hy/roster', {t:{a1:{n:'A1',e:'🍎'}, b2:{n:'B2',e:'🍊'}}, k:{k1:{n:'민준',t:'a1'}}}).then(()=>HyBoss.refresh(true)); }"); await k.wait_for_timeout(500)
        await E("()=>{ window._kp=null; KidPick.open(v=>{ window._kp=v; }); }"); await k.wait_for_timeout(200)
        ok(await E("()=>!!document.querySelector('#kidPick [data-kpnew]')"), "이름 고르기에 🙋 내 이름이 없어요")
        await E("()=>document.querySelector('#kidPick [data-kpnew]').click()"); await k.wait_for_timeout(200)
        await k.fill("#kpNm", "1"); await E("()=>document.querySelector('#kidPick [data-kpok]').click()")
        ok("2~8" in await E("()=>document.getElementById('kpMsg').innerText"), "이상한 이름은 막음")
        await k.fill("#kpNm", "유이홍"); await E("()=>document.querySelector('#kidPick [data-kpt=b2]').click()"); await E("()=>document.querySelector('#kidPick [data-kpok]').click()"); await k.wait_for_timeout(400)
        r = await E("()=>{ const K=HyBoss.kids(), id=Object.keys(K).find(k=>K[k].n==='유이홍'); return [!!id, id && K[id].t, id && !!K[id].nw, (Kid.get()||{}).n, window._kp && window._kp.n, !document.getElementById('kidPick')]; }")
        ok(r == [True, "b2", True, "유이홍", "유이홍", True], f"유이홍 → B2 반 명단에 들어가고(🆕) 바로 그 이름으로 시작 {r}")
        srv = await E("()=>FB.get('/hy/roster/k', true).then(v=>Object.values(v||{}).filter(x=>x.n==='유이홍').length)")
        ok(srv == 1, f"서버 명단에도 {srv}")
        await E("()=>{ Kid.clear(); KidPick.open(v=>{ window._kp=v; }); }"); await k.wait_for_timeout(200)
        ok(await E("()=>[...document.querySelectorAll('#kidPick .kpK')].some(b=>b.innerText==='유이홍')"), "다음부터는 명단에서 바로 고름")
        await E("()=>document.querySelector('#kidPick [data-kpnew]').click()"); await k.fill("#kpNm", "민준"); await E("()=>document.querySelector('#kidPick [data-kpt=a1]').click()"); await E("()=>document.querySelector('#kidPick [data-kpok]').click()"); await k.wait_for_timeout(300)
        r = await E("()=>[(Kid.get()||{}).id, Object.values(HyBoss.kids()).filter(x=>x.n==='민준').length]")
        ok(r == ["k1", 1], f"같은 반 같은 이름이면 새로 안 만들고 그 아이 {r}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
