# v717 🎮 파티 보드 미니게임 2단계 — 시안 v2 ② (사용자: 「이대로 만들기」)
# 🎨 페인트 땅따먹기 (돌 바닥 · 물감 튀김 · 🪣 9칸 · 🖌 한 줄 · 색마다 칸 수) / 🚀 로켓 연타 (하늘 → 우주 · 10번마다 ✨ · 불꽃) / 🚦 신호등 빨리 반응 (기다림 짧게 · 결과 동그라미 · 내 최고) / ⏱ 딱 멈추기 3번 (mg715)
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
MOUNT = """([k,w,h])=>{ const old=document.getElementById('tg'); if(old) old.remove(); const d=document.createElement('div'); d.id='tg'; d.style.cssText='position:fixed;left:0;top:0;width:'+w+'px;height:'+h+'px;z-index:999;display:flex;flex-direction:column;background:#123'; d.innerHTML='<div class="mgG" id="tgG" style="flex:1"></div>'; document.body.appendChild(d);
    const S=MiniG.seq(Study.lessons('elem')[0].ws, k); window._g=MiniG.mount(document.getElementById('tgG'), k, S, 'e', {i:0,k:0,col:Board.COL[0]}); window._g.adv(.02); return 1; }"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(H)
        r = await H.evaluate("()=>['tug','light','paint','stop'].map(k=>MiniG.L[k][0])")
        ok(r == ["🚀 로켓 연타", "🚦 신호등 빨리 반응", "🎨 페인트 땅따먹기", "⏱ 딱 멈추기 3번"], f"이름 {r}")
        for (w, h, nm) in ((820, 1180, "패드"), (410, 560, "한 패드 4명 자리")):
            # 🎨
            await H.evaluate(MOUNT, ["paint", w, h])
            r = await H.evaluate("""()=>{ const g=window._g, c=g.cells[5]; g.tap(c); g.sh.set(7, 1); g.sh.set(8, 1); g.draw(); const cs=getComputedStyle(c), af=getComputedStyle(c, '::after');
                return [cs.backgroundImage.includes('tile'), (af.webkitMaskImage||af.maskImage||'').includes('pt_splat'), af.backgroundColor, [...document.querySelectorAll('#tg .mgPtB span')].map(e=>e.textContent), g.sc]; }""")
            ok(r[0] and r[1] and r[2] != "rgba(0, 0, 0, 0)" and r[3][:2] == ["2", "나 1"] and r[4] == 1, f"🎨 {nm}: 돌 바닥 · 내 색 물감 튀김 · 아래 색마다 칸 수 {r}")
            r = await H.evaluate("""()=>{ const g=window._g; for(let i=0;i<70 && !g.pw;i++) g.adv(1/30); const P=g.pw; if(!P) return null; const el=g.cells[P.i], img=el.querySelector('img');
                const L=g.area(P.i, P.k), s0=g.sc, n=g.tap(el); return {k:P.k, img:!!img && img.src.includes('pt_'+P.k), area:L.length, n, gain:g.sc-s0, row:P.k==='roller' ? L.every(j=>Math.floor(j/6)===Math.floor(P.i/6)) : true, gone:!g.pw && !el.querySelector('img')}; }""")
            ok(r and r["img"] and r["gain"] >= 1 and r["gain"] == r["n"] and r["row"] and r["gone"] and (r["area"] == 6 if r["k"] == "roller" else r["area"] in (4, 6, 9)), f"🎨 {nm}: 2초쯤 뒤 🪣/🖌 나옴 · 누르면 둘레/한 줄 · 사라짐 {r}")
            r = await H.evaluate("""()=>{ const g=window._g; const out=[]; ['bucket','roller'].forEach(k=>{ out.push(g.area(0,k).length, g.area(27,k).length); }); return out; }""")
            ok(r == [4, 9, 6, 6], f"🎨 {nm}: 🪣 = 둘레 9칸(모서리 4) · 🖌 = 한 줄 6칸 {r}")
            r = await H.evaluate("()=>{ const g=window._g; let t=0; for(let i=0;i<200;i++){ g.adv(.1); if(g.pw) t++; } return t; }")
            ok(20 <= r <= 140, f"🎨 {nm}: 20초 동안 🪣/🖌 보이는 때 {r/10:.1f}초 (4초마다 2.5초)")
            # 🚀
            await H.evaluate(MOUNT, ["tug", w, h])
            r = await H.evaluate("""()=>{ const g=window._g, K=g.K; const p0=getComputedStyle(K).backgroundPositionY; for(let i=0;i<9;i++) g.tap(); g.adv(.02); const f9=g.F.style.transform;
                g.tap(); g.adv(.02); const x10=[g.X.classList.contains('on'), g.X.textContent, g.Lb.textContent]; for(let i=0;i<20;i++) g.tap(); g.adv(.02);
                return {p0, p30:K.style.backgroundPositionY, f9, x10, sc:g.sc, st:+g.Sx.style.opacity, c:g.C.textContent, n:g.N.textContent}; }""")
            ok(r["sc"] == 30 and r["n"] == "30" and r["x10"][0] and "지붕" in r["x10"][1] and r["p30"] and float(r["p30"].rstrip("%")) < 50 and r["st"] > 0 and "빨라" in r["c"], f"🚀 {nm}: 30번 = 30점 · 배경이 위로 · 10번에 ✨🏠 · 별 보임 · 빨리 누르면 🔥 {r}")
            await H.screenshot(path=OUT + "mg717_tug_%s.png" % ("pad" if w > 600 else "q"), clip={"x": 0, "y": 0, "width": w, "height": h})
            # 🚦
            await H.evaluate(MOUNT, ["light", w, h])
            r = await H.evaluate("""()=>{ const g=window._g, T=g.T; const waits=[]; for(let j=1;j<T.length;j++) waits.push(+(T[j]-T[j-1]-g.GW-0.4).toFixed(2)); const n22=T.filter(x=>x<22).length;
                let hit=0, foul=0; for(let i=0;i<22*30;i++){ g.adv(1/30); if(g.st==='go' && hit<3){ g.tap(); hit++; } else if(g.st==='wait' && foul<1 && g.t>3){ g.tap(); foul++; g.lock=0; } }
                return {wmin:Math.min(...waits), wmax:Math.max(...waits), n22, dots:[...g.D.children].map(e=>e.className), best:!g.Bs.hidden && g.Bs.textContent, sz:Math.round(g.host.querySelector('.mgLtL').getBoundingClientRect().width), sc:g.sc}; }""")
            ok(r["wmin"] >= 0.79 and r["wmax"] <= 2.21 and r["n22"] >= 7 and "g" in r["dots"] and "r" in r["dots"] and "n" in r["dots"] and r["best"] and "최고" in r["best"] and r["sz"] >= (130 if w > 600 else 90),
               f"🚦 {nm}: 기다림 {r['wmin']}~{r['wmax']}초 · 22초에 {r['n22']}판(예전 5판쯤) · 결과 동그라미 {r['dots']} · {r['best']} · 신호등 {r['sz']}px")
            await H.screenshot(path=OUT + "mg717_light_%s.png" % ("pad" if w > 600 else "q"), clip={"x": 0, "y": 0, "width": w, "height": h})
            # ⏱ 화면
            await H.evaluate(MOUNT, ["stop", w, h])
            r = await H.evaluate("""()=>{ const H=document.getElementById('tgG').getBoundingClientRect(); const els=[...document.querySelectorAll('#tg .mgSwG, #tg .mgSwT, #tg .mgSwR > div, #tg .mgSwB')];
                return els.every(e=>{ const r=e.getBoundingClientRect(); return r.width>0 && r.top>=H.top-1 && r.bottom<=H.bottom+1 && r.left>=H.left-1 && r.right<=H.right+1; }); }""")
            ok(r, f"⏱ {nm}: 목표 · 시계 · 3칸 · STOP 모두 자리 안")
            await H.screenshot(path=OUT + "mg717_stop_%s.png" % ("pad" if w > 600 else "q"), clip={"x": 0, "y": 0, "width": w, "height": h})
        # 한 패드 4명(MG.open) 땅따먹기 — 🪣 로 칠한 칸이 다른 자리에도 보임
        r = await H.evaluate("""async()=>{ const c={set:'elem',from:0,to:3,words:[],qt:['mean']}, x=Object.create(Battle); x._ws=null; x.cfg=()=>c;
              const P=[{n:'K1',ch:0},{n:'K2',ch:3},{n:'K3',ch:4},{n:'K4',ch:7}].map((p,i)=>Object.assign(p,{i,col:Board.COL[i]}));
              MG.open({title:'t', sub:'s', P, ctx:x, kind:'paint', sec:12}, sc=>window._r=sc);
              for(let i=0;i<80 && !(MG.o && MG.o.inst && MG.o.inst.length===4);i++) await new Promise(r=>setTimeout(r, 200));
              const g=MG.o.inst[0], h=MG.o.inst[1]; g.pwOn(); const P0=g.pw; const n=g.tap(g.cells[P0.i]); h.draw(); const seen=g.area(P0.i, P0.k).filter(j=>h.sh.get()[j]===0).length; return [n, seen, g.sc]; }""")
        ok(r[0] >= 1 and r[1] == r[0], f"🎨 한 패드 4자리: 🪣/🖌 로 칠한 칸이 다른 자리 판에도 같게 {r}")
        ok(not errs, f"오류 없음 {errs[:3]}")
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
