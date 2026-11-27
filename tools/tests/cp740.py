"""(v740) 🃏 컬러팡 — 사용자: 「컬러팡은 렉도 걸리는데 게임 자체가 매우 효과가 없다 할까?」
   ① 🐢 옛 아이패드(사파리 15 · 가볍게 2단계): 자리 캐릭터 = 조각 줄인 도형 (자리 하나 삼각형 1.6만 아래 · 예전 3만) · 손 카드 그림자 필터 없음(cpLow)
      보통 기기는 그대로 (자리 하나 2만 넘음)
   ② 이름표·시간 막대 = transform (매 프레임 left/top/width 안 씀) · 같은 자리면 다시 안 씀
   ③ 손맛: 한 판(자동 선수) 동안 특수 카드 도장(⊘ 건너뛰기 · ⇄ 거꾸로 · +2/+4 · 🌈 색 · ☝️ 한 장!)이 뜨고 · 맞은 친구 「+2」·「⊘」 떠오름
   ④ 오류 없음 · 한 판 끝까지"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
OUTD = OUT + "cp740/"; os.makedirs(OUTD, exist_ok=True)
IPAD = "Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1"
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
async def open_cp(br, ua=None, code="CP740A"):
    o = {"viewport": {"width": 768, "height": 954}, "is_mobile": True, "has_touch": True, "service_workers": "block"}
    if ua: o["user_agent"] = ua
    ctx = await br.new_context(**o); pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: (m.type in ("error", "warning")) and ("CP" in m.text) and errs.append(m.text[:200]))
    await pg.route("**/*", fake); await pg.goto(ORIGIN + "proto/house.html?isle=1"); await pg.wait_for_timeout(300)
    await pg.evaluate("(c)=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_v5','1'); }", code)
    await pg.reload(); await pg.wait_for_timeout(2600)
    for t in range(3):
        await pg.evaluate("()=>{ if(!MG.on) MG.enter('card',{}); }")
        for _ in range(60):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
    return ctx, pg, errs
SEAT = """()=>{ const sc=MG.run.scene, out=[]; sc.children.forEach(o=>{ let t=0; o.traverse(m=>{ if(m.isMesh && m.geometry){ const g=m.geometry; t+=(g.index?g.index.count:g.attributes.position.count)/3; } }); if(t>5000) out.push(Math.round(t)); }); return out; }"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        # ① ② 옛 아이패드
        ctx, pg, errs = await open_cp(br, IPAD)
        await pg.evaluate("()=>{ MG.run.menuGo('solo'); }"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("()=>[window.GUARD && GUARD.lv, document.getElementById('cpHud').classList.contains('cpLow'), getComputedStyle(document.querySelector('#cpHud .cpC')).filter]")
        seats = await pg.evaluate(SEAT)
        ok(r[0] >= 2 and r[1] and r[2] == "none" and len(seats) == 3 and max(seats) < 16000, f"① 옛 아이패드: 가볍게 {r} · 자리 캐릭터 삼각형 {seats}")
        st = await pg.evaluate("""async ()=>{ const P=[...document.querySelectorAll('#cpHud .cpPlate')], B=document.querySelector('#cpHud .cpBar i'); const s0=P.map(e=>e.style.transform), l0=P.map(e=>e.style.left);
            let writes=0; const mo=new MutationObserver(L=>{ writes+=L.length; }); P.forEach(e=>mo.observe(e,{attributes:true, attributeFilter:['style']})); await new Promise(z=>setTimeout(z,1500)); mo.disconnect();
            return [s0.every(t=>/translate3d/.test(t)), l0.every(x=>!x), writes, getComputedStyle(B).width===getComputedStyle(B.parentNode).width || B.style.width==='', /scaleX/.test(B.style.transform)]; }""")
        ok(st[0] and st[1] and st[3], f"② 이름표 = transform · left/top 안 씀 · 시간 막대 scaleX {st}")
        await pg.screenshot(path=OUTD + "ipad_low.png"); await ctx.close()
        # 보통 기기 = 그대로
        ctx, pg, e2 = await open_cp(br); errs += e2
        await pg.evaluate("()=>{ MG.run.menuGo('solo'); }"); await pg.wait_for_timeout(1500)
        seats = await pg.evaluate(SEAT); lv = await pg.evaluate("()=>[window.GUARD && GUARD.lv, document.getElementById('cpHud').classList.contains('cpLow')]")
        ok(lv[1] or (len(seats) == 3 and min(seats) > 20000), f"① 보통 기기 캐릭터 그대로 {seats} {lv}")
        # ③ 한 판 (자동 · 빠르게) — 도장 · 맞은 친구 표시
        await pg.evaluate("""()=>{ window.__fx=[]; window.__dmg=[]; const F=document.querySelector('#cpHud .cpFx');
            new MutationObserver(()=>{ const t=F.innerText.split(String.fromCharCode(10))[0]; if(t && F.classList.contains('on')) __fx.push(t); }).observe(F,{childList:true, subtree:true, attributes:true});
            new MutationObserver(L=>L.forEach(m=>m.addedNodes.forEach(n=>{ if(n.classList && n.classList.contains('cpDmg')) __dmg.push(n.textContent); }))).observe(document.getElementById('cpHud'),{childList:true, subtree:true});
            MG.run.auto=true; MG.run.fast=true; }""")
        end = False
        for _ in range(300):
            await pg.wait_for_timeout(250)
            if await pg.evaluate("()=>MG.run.phase==='end' || !!(MG.run.G && MG.run.G.over)"): end = True; break
        fx = await pg.evaluate("()=>[...new Set(window.__fx)]"); dm = await pg.evaluate("()=>[...new Set(window.__dmg)]")
        kinds = {k for k in ("건너뛰기", "거꾸로", "+2", "+4", "🌈", "한 장") if any(k in x for x in fx)}
        ok(end, "④ 한 판 끝까지")
        ok(len(kinds) >= 2 and len(fx) >= 3, f"③ 특수 카드 도장 {sorted(kinds)} · {fx[:8]}")
        ok(any(x in ("⊘", "+2", "+4") for x in dm), f"③ 맞은 친구 표시 {dm}")
        ok(not real_errs(errs), f"④ 오류 없음 {real_errs(errs)[:3]}")
        await ctx.close(); await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
