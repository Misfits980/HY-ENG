# v716 🎮 파티 보드 미니게임 크게 — 시안 v2 ② (사용자: 「보드게임 게임들이 전체적으로 업그레이드되어야겠는데?」 · 앞서 「빼지 말고 다 고치기」)
# ⚡ 스피드 퀴즈 흰 카드 · 낱말 크게 · 맞아요/아니에요 · 🔥 연속 / 🃏 카드 8장 · 글자 2배 / 🎣 물고기 낱말 크게 / 🏮 랜턴 1.6배 / 🍎 바구니 1.5배(받는 너비도) / 🏃 캐릭터 크게
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
MOUNT = """([k,w,h])=>{ const old=document.getElementById('tg'); if(old) old.remove(); const d=document.createElement('div'); d.id='tg'; d.style.cssText='position:fixed;left:0;top:0;width:'+w+'px;height:'+h+'px;z-index:999;display:flex;flex-direction:column;background:#123'; d.innerHTML='<div class="mgG" id="tgG" style="flex:1"></div>'; document.body.appendChild(d);
    const S=MiniG.seq(Study.lessons('elem')[0].ws, k); window._g=MiniG.mount(document.getElementById('tgG'), k, S, 'e', {i:0,k:0,col:Board.COL[0]}); window._g.adv(.05); return 1; }"""
FS = "(sel)=>{ const e=document.querySelector('#tg '+sel); return e ? parseFloat(getComputedStyle(e).fontSize) : 0; }"
IN = """(sel)=>{ const H=document.getElementById('tgG').getBoundingClientRect(); return [...document.querySelectorAll('#tg '+sel)].every(e=>{ const r=e.getBoundingClientRect(); return r.width>0 && r.left>=H.left-1 && r.right<=H.right+1 && r.top>=H.top-1 && r.bottom<=H.bottom+1; }); }"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(H)
        for (w, h, nm) in ((820, 1180, "패드"), (410, 560, "한 패드 4명 자리")):
            big = w > 600
            # ⚡ 스피드 퀴즈
            await H.evaluate(MOUNT, ["ox", w, h])
            fe = await H.evaluate(FS, ".mgOxC .mgOxE"); fk = await H.evaluate(FS, ".mgOxC .mgOxK"); inn = await H.evaluate(IN, ".mgOxC, .mgOxB button")
            lab = await H.evaluate("()=>[...document.querySelectorAll('#tg .mgOxB small')].map(e=>e.textContent)")
            ok(fe >= (80 if big else 30) and fk >= (40 if big else 20) and inn and lab == ["맞아요", "아니에요"], f"⚡ {nm}: 낱말 {fe}px · 뜻 {fk}px (예전 46·30 → 경기장에 작게) · 카드·단추 칸 안 · {lab}")
            await H.evaluate("()=>{ const g=window._g; g.auto(); g.adv(.3); }"); await H.wait_for_timeout(260)
            await H.evaluate("()=>{ const g=window._g; g.auto(); g.adv(.3); }"); await H.wait_for_timeout(260)
            r = await H.evaluate("()=>{ const g=window._g; return [g.sc, g.st, (document.querySelector('#tg .mgOxSt')||{}).textContent||'']; }")
            ok(r[0] == 2 and r[1] == 2 and "2연속" in r[2], f"⚡ {nm}: 맞히면 +1 · 🔥 연속 {r}")
            r = await H.evaluate("()=>{ const g=window._g; g.wrong(); return [g.sc, g.st]; }")
            ok(r == [2, 0], f"⚡ {nm}: 틀리면 연속 0 {r}")
            # 🃏 카드 뒤집기
            await H.evaluate(MOUNT, ["memory", w, h])
            r = await H.evaluate("()=>{ const M=document.querySelector('#tg .mgMm'); return [M.children.length, M.className]; }")
            await H.evaluate("()=>document.querySelectorAll('#tg .mgC').forEach(c=>c.classList.add('on'))"); await H.wait_for_timeout(500)
            fe = await H.evaluate("()=>Math.min(...[...document.querySelectorAll('#tg .mgCe')].map(e=>parseFloat(e.style.fontSize)||0))")
            inn = await H.evaluate(IN, ".mgC")
            ok(r[0] == 8 and inn and fe >= (36 if big else 18), f"🃏 {nm}: 카드 {r[0]}장 ({r[1]}) · 영어 글자 {fe}px (예전 12장 · 22px) · 칸 안")
            await H.evaluate("()=>document.querySelectorAll('#tg .mgC').forEach(c=>c.classList.remove('on'))"); await H.wait_for_timeout(400)
            r = await H.evaluate("()=>{ const g=window._g; for(let i=0;i<4;i++){ g.auto(); g.lock=0; } return [g.sc, g.left]; }")
            ok(r[0] == 6, f"🃏 {nm}: 4쌍 다 찾으면 +4 + 보너스 2 {r}")
            # 🎣 단어 낚시
            await H.evaluate(MOUNT, ["fish", w, h]); await H.evaluate("()=>{ for(let i=0;i<120;i++) window._g.adv(1/60); }")
            fs = await H.evaluate("()=>Math.max(...[...document.querySelectorAll('#tg .mgFi span')].map(e=>parseFloat(e.style.fontSize)||0))")
            ok(fs >= (28 if big else 18), f"🎣 {nm}: 물고기 낱말 {fs}px (예전 20)")
            # 🏮 랜턴
            await H.evaluate(MOUNT, ["balloon", w, h]); await H.evaluate("()=>{ for(let i=0;i<60;i++) window._g.adv(1/60); }")
            bw = await H.evaluate("()=>{ const b=document.querySelector('#tg .mgB'); return b ? Math.round(b.getBoundingClientRect().width) : 0; }")
            ok(bw >= (190 if big else 90), f"🏮 {nm}: 랜턴 {bw}px (예전 최대 124)")
            # 🍎 과일 받기 — 바구니가 커진 만큼 받음 · 바구니 밖은 안 받음
            await H.evaluate(MOUNT, ["fruit", w, h])
            r = await H.evaluate("""()=>{ const g=window._g; g.x=g.tx=50; g.adv(.05); const kw=g.K.getBoundingClientRect().width, W=g.F.clientWidth, hw=g.hw();
                const drop=dx=>{ const o=g.spawn(); o.ty='f'; o.x=50+dx; o.el.style.left=o.x+'%'; o.y=70; o.v=40; const s0=g.sc; for(let i=0;i<30 && !o.got && o.y<104;i++) g.adv(1/30); return g.sc>s0; };
                return [Math.round(kw), Math.round(hw*10)/10, drop(hw*.8), drop(hw+6)]; }""")
            ok((r[0] >= 230 if big else 100 <= r[0] <= 160) and r[2] and not r[3], f"🍎 {nm}: 바구니 {r[0]}px · 받는 너비 ±{r[1]}% · 가장자리 받음 {r[2]} · 밖은 안 받음 {not r[3]}")
            # 🏃 점프
            await H.evaluate(MOUNT, ["jump", w, h])
            cw = await H.evaluate("()=>Math.round(document.querySelector('#tg .mgJpC').getBoundingClientRect().width)")
            ok((cw >= 140) if big else (64 <= cw <= 100), f"🏃 {nm}: 캐릭터 {cw}px (예전 최대 124)")
            await H.screenshot(path=OUT + "mg716_%s.png" % ("pad" if big else "q"), clip={"x": 0, "y": 0, "width": w, "height": h})
        # 13가지 모두 자동 선수로 점수가 오름 (크기 바꾼 뒤에도)
        r = await H.evaluate("""()=>{ const out={}; MiniG.ACT.concat(MiniG.ENG).forEach(k=>{ const host=document.createElement('div'); host.className='mgG'; host.style.cssText='position:fixed;left:0;top:0;width:820px;height:1100px'; document.body.appendChild(host);
              const g=MiniG.mount(host, k, MiniG.seq(Study.lessons('elem')[0].ws, k), 'e', {i:0,k:0,col:'#f44'}); for(let i=0;i<90;i++) g.adv(1/30); let n=0; for(let i=0;i<5;i++){ g.lock=0; try{ if(g.auto()) n++; }catch(e){ out[k]='err '+e; } g.adv(.3); } out[k]=out[k]||g.sc; g.dead=1; host.remove(); }); return out; }""")
        ok(all(isinstance(v, (int, float)) and v > 0 for v in r.values()), f"13가지 자동 선수 점수 {r}")
        ok(not errs, f"오류 없음 {errs[:3]}")
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
