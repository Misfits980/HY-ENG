# v718 🔢 숫자 빨리 누르기 — 사용자 사진(수업): 누른 칸(초록) 그림이 칸보다 크게 왼쪽 위만 보이고 오른쪽 줄은 화면 밖
# 원인: .mgNu button.ok{background:var(--me)} 줄임 속성이 그림 크기·자리·반복을 처음값으로 돌려놓음 → 초록·빨강 칸도 회색 칸과 같은 크기
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        for sk in ("e", "k"):
            for vp in ((768, 954), (1024, 698)):
                ctx = await br.new_context(viewport={"width": vp[0], "height": vp[1]}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
                H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(H)
                r = await H.evaluate("""(sk)=>{ const d=document.createElement('div'); d.id='board'; d.className='bdModePad sk-'+sk; d.innerHTML='<div class="bpMG" id="bpMG"><div class="bpMgHd"><em>0</em><span>8</span></div><div class="mgG" id="bpG"></div></div>'; document.body.appendChild(d);
                    const S=MiniG.seq(Study.lessons('elem')[0].ws, 'num'); const g=MiniG.mount(document.getElementById('bpG'), 'num', S, sk, {i:0,k:0,col:Board.COL[0]}); for(let i=0;i<4;i++){ g.lock=0; g.auto(); } g.lock=0; g.wrong();
                    const cs=b=>{ const c=getComputedStyle(b); return [c.backgroundSize, c.backgroundPosition, c.backgroundRepeat]; };
                    const B=[...g.G.children], okB=B.find(b=>b.classList.contains('ok')), noB=B.find(b=>b.classList.contains('no')), plain=B.find(b=>!b.classList.contains('ok') && !b.classList.contains('no'));
                    const out=B.filter(b=>{ const r=b.getBoundingClientRect(); return r.right>innerWidth+1 || r.bottom>innerHeight+1 || r.left<-1; }).length;
                    return {ok:cs(okB), no:noB ? cs(noB) : null, plain:cs(plain), out}; }""", sk)
                want = ["100% 100%", "50% 50%", "no-repeat"]
                ok(r["ok"] == want and (r["no"] is None or r["no"] == want) and r["plain"] == want and r["out"] == 0, f"🔢 {sk} {vp}: 누른 칸·틀린 칸 그림 = 회색 칸과 같은 크기·자리 · 화면 밖 칸 없음 {r}")
                if sk == "e" and vp[0] == 768: await H.screenshot(path=OUT + "mg718_num.png")
                await ctx.close()
        ok(not errs, f"오류 없음 {errs[:3]}")
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
