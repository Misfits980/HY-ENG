# v715 🎮 파티 보드 미니게임 — 사용자: 「10초 멈추기 게임에 근사치가 1등 해야 하는 거 아닌가?」
# ① ⏱ 10초 딱 멈추기: 1초 넘게 어긋나도 가까운 순서대로 점수 (예전 = 모두 0점 → 순서 아무렇게나) · 진짜 시각으로 잼 (느린 패드에서 시계가 느려지지 않음)
# ② 미니게임 한 프레임이 길어도(느린 패드) 게임 시간이 실제와 같게 (0.05초씩 나눠서)
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
MOUNT = """(k)=>{ const old=document.getElementById('tg'); if(old) old.remove(); const d=document.createElement('div'); d.id='tg'; d.style.cssText='position:fixed;inset:0;z-index:999;display:flex'; d.innerHTML='<div class="mgG" id="tgG" style="flex:1"></div>'; document.body.appendChild(d);
    const S=MiniG.seq(Study.lessons('elem')[0].ws, k); window._g=MiniG.mount(document.getElementById('tgG'), k, S, 'e', {i:0,k:0,col:Board.COL[0]}); return 1; }"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(H)
        # ① 점수 — 가까울수록 언제나 높음
        T = [10.0, 10.03, 9.9, 10.5, 9.0, 11.2, 8.3, 12.5, 6.0, 14.4]
        r = await H.evaluate("(T)=>T.map(t=>{ const g=MiniG.G.stop; return g.score(Math.abs(t-10)); })", T)
        ds = [abs(t - 10) for t in T]
        mono = all((ds[i] < ds[j]) <= (r[i] > r[j]) for i in range(len(T)) for j in range(len(T)) if abs(ds[i] - ds[j]) >= 0.1)
        ok(mono and min(r) >= 1 and r[0] == 100, f"① 점수: 10초에 가까울수록 높음 · 4초 넘게 어긋나도 1점 이상 {dict(zip(T, r))}")
        await H.evaluate(MOUNT, "stop")
        r = await H.evaluate("()=>{ const g=window._g; g.stopIt(11.3); return [g.sc, g.host.innerText.replace(/\\n/g,' ')]; }")
        ok(r[0] == 47 and "+1.30초" in r[1], f"① 11.30초에 멈춤 = 47점 (예전 0점) {r}")
        await H.evaluate(MOUNT, "stop")
        r = await H.evaluate("()=>{ const g=window._g; g.t0-=15800; g.step(.02); return [g.sc, g.done, g.host.innerText.replace(/\\n/g,' ')]; }")
        ok(r[0] == 0 and r[1] == 1 and "안 눌렀" in r[2], f"① 끝까지 안 누르면 0점 {r}")
        # 진짜 시각: 프레임이 듬성듬성(dt 작게 줘도) — 누른 순간의 실제 시간
        await H.evaluate(MOUNT, "stop")
        await H.wait_for_timeout(1700)
        r = await H.evaluate("()=>{ const g=window._g; for(let i=0;i<5;i++) g.step(0.05); const b=g.host.querySelector('.mgSwB'); b.dispatchEvent(new PointerEvent('pointerdown', {bubbles:true})); return [g.done, Math.round(g.t*100)/100]; }")
        ok(r[0] == 1 and 0.9 <= r[1] <= 1.6, f"① 1.7초 뒤 누름(그사이 프레임 0.25초어치) → 시계 {r[1]}초 (예전 = 프레임 합 0.25초 − 0.6)")
        # ② 느린 패드: 한 프레임 0.2초 = 0.05초 × 4
        r = await H.evaluate("()=>{ const g={dead:0, n:0, tot:0, step(s){ this.n++; this.tot+=s; }}; MiniG.mount.call; const host=document.createElement('div'); const k=MiniG.mount(host, 'mole', MiniG.seq(Study.lessons('elem')[0].ws, 'mole'), 'e', {}); let n=0, tot=0; const st=k.step.bind(k); k.step=s=>{ n++; tot+=s; st(s); }; k.adv(0.2); k.adv(0.016); k.dead=1; return [n, Math.round(tot*1000)/1000]; }")
        ok(r == [5, 0.216], f"② 한 프레임 0.2초 → 0.05초 4번 (게임 시간 = 실제) {r}")
        # 두더지 20초: 빠른 패드(60fps) vs 느린 패드(8fps) — 나온 두더지 수가 비슷
        r = await H.evaluate("""()=>{ const run=(fps, old)=>{ const host=document.createElement('div'); document.body.appendChild(host); host.style.cssText='position:fixed;left:0;top:0;width:400px;height:600px';
              const S=MiniG.seq(Study.lessons('elem')[0].ws, 'mole'); S.r=Array.from({length:400},(x,i)=>((i*7919)%1000)/1000); const g=MiniG.mount(host, 'mole', S, 'e', {}); let seen=0; const p0=g.pop.bind(g); g.pop=(h,ty)=>{ seen++; p0(h,ty); };
              for(let t=0;t<20;t+=1/fps){ if(old) g.step(Math.min(0.05, 1/fps)); else g.adv(1/fps); } g.dead=1; host.remove(); return seen; }; return [run(60), run(8), run(8, 1)]; }""")
        await H.wait_for_timeout(300)
        ok(r[0] > 30 and r[1] >= r[0] * 0.85 and r[2] < r[0] * 0.6, f"② 🔨 두더지 20초에 나온 수: 60fps {r[0]} · 8fps {r[1]} (예전 8fps = {r[2]})")
        ok(not errs, f"오류 없음 {errs[:3]}")
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
