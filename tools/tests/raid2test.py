"""(v322) ⚔️ 수업 레이드 점검 고친 것 — 선생님 TV 1 · 아이 1 (+ 가짜 아이들), 이 기기 안 방(BroadcastChannel)
   · 시작 뒤 들어온 아이 → 보스 체력 늘어남 + TV 소식 「들어옴 · 보스 체력 +」
   · 새로고침(다시 들어오기) → 데미지·막기·맞힘·틀림 이어서 · 점수는 서버에서 더하기(두 번 보내도 덮어쓰지 않음)
   · 같은 이름이 다른 기기에서 접속 중이면 막음 · 내 기기는 그대로
   · TV 새로고침 → 📺 방 다시 열기(점수 그대로) · 30초 지난 소식 지우기
   · 멈춘 채 TV 가 사라지면 아이는 10분 뒤 끝 · 참가 💎 · 시상식 상 💎10 글자
   · 📚 단어책(cfg.book)으로 문제 채우기 · 뜻 고르기 문제는 저절로 소리 안 냄"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ANS="""(ok)=>{ const R=Raid, q=R.atk ? R.atk.q : R.q; if(!q || q.done || (R.atk && !R.atk.shown)) return 'none'; let k=q.opts.findIndex(o=>o.en===q.w.en); if(!ok) k=(k+1)%q.opts.length; R.answer(k); return (R.atk?'blk':q.sh?'sh':(ok?'hit':'miss')); }"""
ME="""()=>{ const P=RaidNet.get().p||{}; const k=Object.keys(P).find(x=>P[x].n==='민준'); const p=P[k]||{}; return [p.d|0, p.b|0, p.h|0, p.m|0]; }"""
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1024,"height":768})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e))); await boot(host)
        room=await host.evaluate("()=>Raid.host('g56',[], 0, null, 900)"); print("room", room)
        k=await ctx.new_page(); k.on("pageerror", lambda e: errs.append("K "+str(e))); await k.set_viewport_size({"width":390,"height":844}); await boot(k)
        await k.evaluate(f"()=>{{ Raid.join('{room}','민준'); Raid.FAST=0; }}"); await host.wait_for_timeout(600)
        # 📚 단어책 — 처음 하는 아이(본 단어 없음)는 선생님이 고른 G5-6 단어로
        pool=await k.evaluate("()=>{ Raid._pool=null; const P=Raid.pool(), B={}; Study.BOOKS.g56.sets.forEach(s=>Study.lessons(s).forEach(x=>x.ws.forEach(w=>{ B[w.en]=1; }))); return [P.length, P.filter(w=>B[w.en]).length]; }")
        print("pool", pool)
        if pool[0]<8 or pool[1]<pool[0]*0.8: bad.append(f"단어책 g56 로 안 채움 {pool}")
        await host.evaluate("()=>Raid.hostAct('start')"); await host.wait_for_timeout(500)
        m0=await host.evaluate("()=>Raid.calc().max"); print("max 1명", m0)
        if m0!=2000: bad.append(f"시작 체력 {m0}")
        # 시작 뒤 3명 더 → 4 × 900 = 3600
        await host.evaluate("()=>{ ['a','b','c'].forEach((x,i)=>RaidNet.write('/p/late'+x, {n:'늦은'+i, e:'🙂', c:'hero', d:0, at:Raid.now()}, true)); }")
        await host.wait_for_timeout(700)
        g=await host.evaluate("()=>{ const c=Raid.calc(), E=RaidNet.get().ev||{}, gr=Object.values(E).filter(e=>e&&e.k==='grow'); return [c.max, c.hp, gr.map(e=>[e.n, e.v]), document.querySelector('.rdFeed').innerText]; }")
        print("grow", g[:3])
        if g[0]!=3600 or g[1]!=3600: bad.append(f"늦게 들어온 아이 체력 {g[:2]}")
        if not g[2] or g[2][-1][1]!=1600 or "늦은0" not in g[2][-1][0] or "보스 체력" not in g[3]: bad.append(f"TV 체력 소식 {g[2]} {g[3][:80]}")
        # 풀기 → 새로고침 → 이어서
        for i in range(12):
            await k.evaluate(ANS, i%3!=0); await k.wait_for_timeout(1600)
        before=await host.evaluate(ME); print("server before reload", before)
        await k.reload(); await k.wait_for_timeout(1300)
        await k.evaluate(f"()=>{{ Raid.join('{room}','민준'); Raid.FAST=0; }}"); await k.wait_for_timeout(1200)
        loc=await k.evaluate("()=>[Raid.dmg, Raid.blk, Raid.hits, Raid.miss]"); print("kid after rejoin", loc)
        if loc!=before: bad.append(f"다시 들어오면 이어서 {loc} != {before}")
        # 서버에서 더하기 — 한꺼번에 두 번 보내도 +2
        await k.evaluate("()=>{ Raid.bump({h:1}); Raid.bump({h:1}); }"); await k.wait_for_timeout(500)
        h2=await host.evaluate(ME); print("inc", h2)
        if h2[2]!=before[2]+2: bad.append(f"맞힘 더하기 {before[2]} → {h2[2]}")
        # 같은 이름 — 다른 기기면 막음, 내 기기(새로고침)는 들어감
        k2=await ctx.new_page(); k2.on("pageerror", lambda e: errs.append("K2 "+str(e))); await k2.set_viewport_size({"width":390,"height":844}); await boot(k2)
        await k2.evaluate("()=>{ Raid.dev=()=>'otherdev1'; RaidJoin.open(); }"); await k2.wait_for_timeout(200)
        await k2.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='민준'; document.querySelector('[data-rj=go]').click(); }}"); await k2.wait_for_timeout(700)
        dup=await k2.evaluate("()=>[(document.getElementById('rdJoinMsg')||{}).textContent||'', Raid.role]"); print("dup", dup)
        if "이미 들어온 이름" not in dup[0] or dup[1]: bad.append(f"같은 이름 막기 {dup}")
        await k2.evaluate("()=>{ RaidJoin.close(); }")
        await k2.evaluate("()=>{ Raid.dev=()=>'otherdev2'; RaidJoin.open(); }"); await k2.wait_for_timeout(200)
        await k2.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='서연'; document.querySelector('[data-rj=go]').click(); }}"); await k2.wait_for_timeout(700)
        if await k2.evaluate("()=>Raid.role")!="kid": bad.append("다른 이름이 못 들어감")
        last=await k2.evaluate("()=>RaidJoin.last()"); print("last", last)
        if not last or last.get("r")!=room: bad.append(f"마지막 방 저장 {last}")
        # 3시간 지난 방 번호 → 「끝난 방이에요」
        await host.evaluate("()=>FB.set('/raids/9998', {cfg:{book:'g34', made:Date.now()-4*3600e3}, st:{s:'end', made:Date.now()-4*3600e3}})"); await host.wait_for_timeout(300)
        await k2.evaluate("()=>{ Raid.leave(); RaidJoin.open(); }"); await k2.wait_for_timeout(300)
        await k2.evaluate("()=>{ document.getElementById('rdRoomIn').value='9998'; const n=document.getElementById('rdNameIn'); if(n) n.value='서연'; document.querySelector('[data-rj=go]').click(); }"); await k2.wait_for_timeout(700)
        old=await k2.evaluate("()=>[(document.getElementById('rdJoinMsg')||{}).textContent||'', Raid.role]"); print("old room", old)
        if "끝난 방" not in old[0] or old[1]: bad.append(f"3시간 지난 방 {old}")
        await k2.close()
        # 📺 TV 새로고침 → 다시 열기 (방을 새로 쓰지 않음)
        P0=await host.evaluate("()=>[Object.keys(RaidNet.get().p||{}).length, Raid.calc().max, Raid.calc().sum]")
        await host.reload(); await host.wait_for_timeout(1300)
        tv=await host.evaluate("()=>TvRoom.get()"); print("tv saved", tv)
        if not tv or tv.get("r")!=room: bad.append(f"TV 방 저장 {tv}")
        ok=await host.evaluate("()=>TvRoom.open()"); await host.wait_for_timeout(700)
        P1=await host.evaluate("()=>[Object.keys(RaidNet.get().p||{}).length, Raid.calc().max, Raid.calc().sum]"); print("reopen", ok, P0, P1)
        if not ok or await host.evaluate("()=>Raid.role")!="host" or P1[0]!=P0[0] or P1[1]!=P0[1] or P1[2]<P0[2]: bad.append(f"TV 다시 열기 {ok} {P0} {P1}")
        # 30초 지난 소식은 TV 가 지움
        await host.evaluate("()=>{ const now=Raid.now(), ev={}; for(let i=0;i<300;i++) ev['old'+i]={n:'늦은0', k:'hit', v:10, t:now-60000-i}; RaidNet.write('/ev', ev, true); }"); await host.wait_for_timeout(300)
        n1=await host.evaluate("()=>Object.keys(RaidNet.get().ev||{}).length"); await host.evaluate("()=>Raid.evGc(Raid.now())"); await host.wait_for_timeout(400)
        n2=await host.evaluate("()=>Object.keys(RaidNet.get().ev||{}).length"); print("ev", n1, "→", n2)
        if n1<300 or n2>40: bad.append(f"지난 소식 지우기 {n1} → {n2}")
        # 뜻 고르기 문제는 저절로 소리 안 냄
        said=await k.evaluate("()=>{ let n=0; const o=DexDet.say; DexDet.say=()=>{ n++; }; for(let i=0;i<20;i++){ const q=Raid.mkQ(false); q.t='e2k'; Raid.q=q; Raid._hrdB=null; Raid.drawKid(); } DexDet.say=o; return n; }")
        print("auto say", said)
        if said: bad.append(f"뜻 고르기 문제가 저절로 소리 {said}")
        # 멈춘 채 TV 가 사라짐 → 아이는 10분 뒤 끝 + 참가 💎 + 시상식 💎10 글자
        await host.evaluate("()=>Raid.hostAct('pause')"); await host.wait_for_timeout(500)
        await host.close()
        await k.wait_for_timeout(600)
        s1=await k.evaluate("()=>[Raid.st().s, Raid.ended]"); print("paused", s1)
        if s1!=["pause", False]: bad.append(f"멈춤 {s1}")
        await k.evaluate("()=>{ Raid.off=(Raid.off|0)+11*60000; }"); await k.wait_for_timeout(800)
        s2=await k.evaluate("()=>[Raid.ended, Raid._gems, (document.querySelector('#rdB .stGem')||{}).textContent||'']"); print("after 11min", s2)
        if not s2[0] or s2[1]!=15 or "(참가)" not in s2[2]: bad.append(f"멈춤 10분 뒤 끝·참가 보석 {s2}")
        await k.wait_for_timeout(6500)
        aw=await k.evaluate("()=>[(Raid._myAw||[]).length, (document.querySelector('.rdAwMe')||{}).textContent||'']"); print("aw", aw)
        if not aw[0] or ("+"+str(aw[0]*10)) not in aw[1]: bad.append(f"시상식 보석 글자 {aw}")
        await k.screenshot(path=OUT+"raid2_kid_end.png")
        print("errs", errs[:5]); await br.close()
    e=real_errs(errs)
    print("결과:", "통과 ✅" if not bad and not e else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or e: sys.exit(1)
asyncio.run(main())
