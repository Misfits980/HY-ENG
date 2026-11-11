# v666 👹 수업 레이드 아이 화면(기다림·끝) — 패드에서 크게 + 성 테마 UI · 휴대폰/가로도 끝 화면이 한 화면에(「나가기」까지)
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
ANS = """()=>{ if(BossLive.S && BossLive.S.A) patSolve(true); const R=Raid, q=R.atk ? R.atk.q : R.q; if(!q || q.done || (R.atk && !R.atk.shown)) return 'none'; R.answer(q.opts.findIndex(o=>o.en===q.w.en)); return 'hit'; }"""
M = """()=>{ const S=document.getElementById('scRaid'), B=document.getElementById('rdB'), k=B && B.firstElementChild, g=S.querySelector('#rdB .stGo'), x=S.querySelector('.rdTop .rdX'); const btns=[...S.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.getBoundingClientRect());
  return {over:S.scrollHeight-S.clientHeight, bOver:B.scrollHeight-B.clientHeight, w:document.documentElement.scrollWidth-innerWidth, out:btns.filter(r=>r.bottom>innerHeight+1||r.right>innerWidth+1||r.left<-1).length, z:k ? parseFloat(k.style.zoom||'1') : 0, kc:k ? k.className : '', go:g ? Math.round(g.getBoundingClientRect().bottom) : 0, goBi:g ? getComputedStyle(g).borderImageSource.includes('btn_g') : false, vh:innerHeight, aw:S.querySelectorAll('#rdB .rdAwC').length,
    gem:x ? getComputedStyle(x).backgroundImage.includes('close.webp') : false, bg:getComputedStyle(S).backgroundImage.includes('world-meadow'), stage:(()=>{ const r=S.querySelector('.rs'); return r && r.offsetParent ? Math.round(r.getBoundingClientRect().height) : 0; })(), end:S.classList.contains('rdKEnd')}; }"""
VP = [("패드 세로", (768, 1024)), ("패드 가로", (1024, 768)), ("휴대폰", (390, 844)), ("작은 휴대폰", (375, 667)), ("휴대폰 가로", (915, 412))]
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1280, "height": 720}); errs = []
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e))); await boot(H)
        room = await H.evaluate("()=>{ Raid.MIN=1000; return Raid.host('g34',['vest','cap','glove','beard','belt'], 0, null, 260); }"); K = []
        for i, (nm, vp) in enumerate(VP):
            k = await ctx.new_page(); k.on("pageerror", lambda e, n=nm: errs.append(n + " " + str(e))); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate(f"()=>{{ const k0=Kid.k.bind(Kid); Kid.k=b=>k0(b)+'@t{i}'; Raid.FAST=0; Raid.join('{room}','아이{i+1}'); }}"); K.append(k)
        await H.wait_for_timeout(900)
        for i, (nm, vp) in enumerate(VP):
            m = await K[i].evaluate(M); pad = i < 2
            ok(m["over"] <= 2 and m["bOver"] <= 2 and m["w"] <= 2 and m["out"] == 0, f"{nm} 기다림: 스크롤·화면 밖 단추 없음 {m['over']} {m['bOver']} {m['out']}")
            if pad: ok(m["gem"] and m["bg"] and m["z"] >= 1.25 and "rdWait" in m["kc"], f"{nm} 기다림: 성 테마(보석 닫기·바탕) · 카드 {m['z']:.2f}배")
            else: ok(not m["gem"] and not m["bg"], f"{nm} 기다림: 예전 모양 그대로")
        await H.evaluate("()=>Raid.hostAct('start')"); await H.wait_for_timeout(900)
        ar = await K[0].evaluate("()=>!!(Arena.o && Arena.o.raid===Raid)"); ok(ar, "싸우는 동안은 아레나 화면 그대로")
        for step in range(400):
            for k in K: await k.evaluate(ANS)
            await H.wait_for_timeout(110)
            if (await H.evaluate("()=>Raid.st().s")) == "end": break
        ok((await H.evaluate("()=>Raid.st().s")) == "end", "보스를 쓰러뜨려 끝남")
        for k in K:
            try: await k.wait_for_function("()=>document.querySelectorAll('#rdB .rdAwC').length>0", timeout=12000)
            except Exception: pass
        await H.wait_for_timeout(3800)
        for i, (nm, vp) in enumerate(VP):
            m = await K[i].evaluate(M); pad = i < 2
            ok(m["end"] and m["aw"] >= 1 and m["go"] > 0 and m["go"] <= m["vh"] and m["over"] <= 2 and m["bOver"] <= 2 and m["out"] == 0, f"{nm} 끝(시상 {m['aw']}개): 「나가기」까지 한 화면 {m['go']}/{m['vh']} · 스크롤 {m['over']} {m['bOver']}")
            if pad: ok(m["goBi"] and m["z"] >= 1.05 and 0 < m["stage"] < vp[1] * .2, f"{nm} 끝: 초록 보석 나가기 · 카드 {m['z']:.2f}배 · 무대 {m['stage']}px")
            elif i >= 3: ok(m["stage"] == 0 and m["z"] >= .72, f"{nm} 끝: 무대 접음 · 카드 {m['z']:.2f}배")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3])); await ctx.close()
        # ⚔️ 배틀 끝 화면 — 휴대폰 가로도 한 화면
        ctx = await br.new_context(viewport={"width": 1280, "height": 720}); await ctx.add_init_script("window.HY_FB_LOCAL=true;"); H = await ctx.new_page(); await boot(H)
        room = await H.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:60, team:false, lbl:'G5-6'})"); K = []
        for i, vp in enumerate([(915, 412), (390, 844), (390, 844), (390, 844), (390, 844)]):
            k = await ctx.new_page(); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate(f"()=>{{ const k0=Kid.k.bind(Kid); Kid.k=b=>k0(b)+'@t{i}'; RaidJoin.open(); }}"); await k.wait_for_timeout(100)
            await k.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='친구{i}'; document.querySelector('[data-rj=go]').click(); }}"); await k.wait_for_timeout(400); K.append(k)
        await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_function("()=>Battle.st().s==='run' && Battle.left()>0", timeout=12000); await H.wait_for_timeout(1200)
        q = await K[0].evaluate("()=>{ const S=document.getElementById('scRaid'); return S.scrollHeight-S.clientHeight; }"); ok(q <= 2, f"휴대폰 가로 배틀 문제 화면: 스크롤 없음 {q}")
        await H.evaluate("()=>Battle.hostAct('end')"); await H.wait_for_timeout(4600)
        m = await K[0].evaluate(M); ok(m["go"] > 0 and m["go"] <= m["vh"] and m["over"] <= 2, f"휴대폰 가로 배틀 끝: 「나가기」까지 한 화면 {m['go']}/{m['vh']} · 스크롤 {m['over']}")
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
