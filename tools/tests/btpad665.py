# v665 🏫 교실 배틀 아이 화면 — 패드에서 크게 + 성 테마 UI (점수 배틀만 · 휴대폰·깃발 레이스는 그대로)
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
ANS = "(g)=>{ const q=Battle.q; if(!q||q.done) return -1; let i=q.ans!=null ? q.ans : q.opts.findIndex(o=>o.en===q.w.en); if(!g) i=(i+1)%q.opts.length; Battle.answer(i); return i; }"
MEAS = """()=>{ const S=document.getElementById('scRaid'), B=document.getElementById('rdB'); const o=[...S.querySelectorAll('.rdOpts .stOpt')]; const r=o.map(b=>b.getBoundingClientRect()); const cs=o[0] ? getComputedStyle(o[0]) : null; const pr=S.querySelector('.rdPr'), pk=pr && pr.firstElementChild; const L=S.querySelector('.btLive');
  const btns=[...S.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.getBoundingClientRect());
  return {pad:S.classList.contains('btPad'), over:S.scrollHeight-S.clientHeight, bOver:B.scrollHeight-B.clientHeight, out:btns.filter(x=>x.bottom>innerHeight+1||x.right>innerWidth+1||x.left<-1).length, n:o.length, h:r.length?Math.round(Math.min(...r.map(x=>x.height))):0, top:r.length?Math.round(r[0].top):0, fs:cs?parseFloat(cs.fontSize):0, bi:cs?cs.borderImageSource:'', ov:o.filter(b=>b.scrollHeight>b.clientHeight+1||b.scrollWidth>b.clientWidth+1).length,
    prFs:pk?parseFloat(getComputedStyle(pk).fontSize):0, prOv:pk?pk.scrollWidth>pr.clientWidth+2:false, two:!!(L && L.classList.contains('two')), rows:L?L.querySelectorAll('.btLvR').length:0, lk:L?[...L.querySelectorAll('.btLvR > i')].map(i=>i.className).join(','):'', liveH:L?Math.round(L.getBoundingClientRect().height):0, bg:getComputedStyle(S).backgroundImage.includes('world-meadow')}; }"""
async def join(ctx, room, nm, vp, i, errs):
    k = await ctx.new_page(); k.on("pageerror", lambda e, n=nm: errs.append(n + " " + str(e))); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
    await k.evaluate(f"()=>{{ const k0=Kid.k.bind(Kid); Kid.k=b=>k0(b)+'@t{i}'; RaidJoin.open(); }}"); await k.wait_for_timeout(100)
    await k.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='{nm}'; document.querySelector('[data-rj=go]').click(); }}"); await k.wait_for_timeout(450); return k
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1920, "height": 1080}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        errs = []; H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e))); await boot(H)
        room = await H.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:120, team:false, lbl:'G5-6'})")
        VP = [("패드 세로", (768, 1024)), ("패드 가로", (1024, 768)), ("휴대폰", (390, 844)), ("큰 패드", (820, 1180))] + [("친구%d" % i, (390, 844)) for i in range(4)]
        K = [await join(ctx, room, nm, vp, i, errs) for i, (nm, vp) in enumerate(VP)]
        w = await K[0].evaluate(MEAS); ok(w["pad"] and w["bg"] and w["over"] <= 2 and w["out"] == 0, f"패드 기다림: 성 테마 바탕 · 스크롤 없음 {w['over']} {w['out']}")
        await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_function("()=>Battle.st().s==='run' && Battle.left()>0", timeout=12000); await H.wait_for_timeout(900)
        tops = {}
        for r in range(5):
            for i, k in enumerate(K):
                try: await k.wait_for_function("()=>Battle.q && !Battle.q.done && Date.now()>=Battle.lockTo", timeout=6000)
                except Exception: continue
                await k.wait_for_timeout(120)
                if i < 4 and r in (0, 3):
                    m = await k.evaluate(MEAS); nm = VP[i][0]
                    if i == 2:
                        ok(m["fs"] <= 17 and m["bi"] == "none" and not m["bg"], f"{nm}: 예전 그대로 (보기 {m['fs']}px · 보석 단추 아님)")
                    else:
                        ok(m["pad"] and "btn_b" in m["bi"] and m["fs"] >= 24 and m["prFs"] >= 40, f"{nm} r{r}: 보석 단추 · 보기 {m['fs']}px · 낱말 {m['prFs']}px")
                        ok(m["h"] >= (60 if i == 1 else 84) and m["ov"] == 0 and not m["prOv"], f"{nm} r{r}: 보기 높이 {m['h']}px · 글자 안 넘침")
                        ok(m["over"] <= 2 and m["bOver"] <= 2 and m["out"] == 0, f"{nm} r{r}: 스크롤·화면 밖 단추 없음 {m['over']} {m['bOver']} {m['out']}")
                        if r == 3:
                            ok("lk1" in m["lk"] and (m["rows"] <= 3 or m["two"]) and (i == 1 or m["liveH"] <= 190), f"{nm}: 순위 왕관/메달 · {m['rows']}줄이면 두 칸 · 높이 {m['liveH']}px")
                        if r == 0: tops[i] = m["top"]
                if i == 0 and r == 1: tops[0] = (await k.evaluate(MEAS))["top"]   # 같은 문제에서 답하기 전 자리
                await k.evaluate(ANS, not (i == 0 and r == 1)); await k.wait_for_timeout(110)
                if i == 0 and r == 1:
                    m = await k.evaluate(MEAS); res = await k.evaluate("()=>{ const e=document.querySelector('#rdB .rdRes.bad'), o=document.querySelector('#rdB .stOpt.bad'); return [!!e, !!o && getComputedStyle(o).borderImageSource.includes('btn_r'), !!document.querySelector('#rdB .stOpt.ok') && getComputedStyle(document.querySelector('#rdB .stOpt.ok')).borderImageSource.includes('btn_g')]; }")
                    ok(res == [True, True, True] and abs(m["top"] - tops[0]) <= 3 and m["bOver"] <= 2, f"패드 세로 틀림: 빨강/초록 보석 · 정답 줄이 떠도 단추 안 움직임 {res} {tops[0]}→{m['top']}")
                await k.wait_for_timeout(180)
        await H.evaluate("()=>{ try{ Battle.hostAct('end'); }catch(e){} }"); await H.wait_for_timeout(4500)
        for i in (0, 1):
            m = await K[i].evaluate(MEAS); e = await K[i].evaluate("()=>{ const g=document.querySelector('#rdB .rdEnd .stGo'); return g ? [Math.round(g.getBoundingClientRect().bottom), innerHeight, getComputedStyle(g).borderImageSource.includes('btn_g')] : null; }")
            ok(e and e[0] <= e[1] and e[2] and m["over"] <= 2 and m["bOver"] <= 2, f"{VP[i][0]} 끝: 결과 카드·나가기 단추가 화면 안 {e}")
        # 🚩 깃발 레이스는 그대로 (btPad 안 붙음)
        await K[0].evaluate("()=>Battle.leave()"); await H.evaluate("()=>Battle.leave()"); await H.wait_for_timeout(300)
        room2 = await H.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:60, mode:'flag', team:true, lbl:'깃발'})"); F = await join(ctx, room2, "깃발아이", (768, 1024), 9, errs)
        await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_timeout(4200)
        try: await F.wait_for_function("()=>!!document.querySelector('#rdB .rdOpts .stOpt')", timeout=9000)
        except Exception: pass
        f = await F.evaluate("()=>{ const S=document.getElementById('scRaid'), o=S.querySelector('.rdOpts .stOpt'); return [S.classList.contains('btPad'), o ? getComputedStyle(o).borderImageSource : 'none', getComputedStyle(S).backgroundImage.includes('world-meadow')]; }")
        ok(f == [False, "none", False], f"🚩 깃발 레이스 아이 화면은 예전 그대로 {f}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3])); await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
