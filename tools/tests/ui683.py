"""(v683) 사용자: 「크롬으로 화면이 제대로 나오는지 다 체크」 — 선생님 크롬(PC 1920 · 패드 세로 820×1180 · 휴대폰 390 · 패드 가로 1180×820)에서 찾은 것
   ① 달리기 먼지 입자가 네모(□) → 둥근 빛 점 (map 있음)
   ② 패드 가로·PC 두 칸 지도: 「숲 구역」 띠가 두 칸을 가로질러 위에 · Stage 1·2 가 나란히 같은 줄
   ③ 패드 가로 유치원 「그림 고르기」: 그림이 다시 크게 (19px → 40px 넘게)
   ④ 패드 가로 짧은 글: 문장 줄 폭이 모두 같음 (왼쪽 끝·🔊 가 한 줄로)
   ⑤ 휴대폰 주간 보스: 「+N명 같이 싸우는 중」 띠가 위로 — 내 이름표를 안 가림
   ⑥ 휴대폰 레이드: 단어 카드 세 장이 모두 화면 안"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        # ── 패드 가로
        pg = await br.new_page(viewport={"width": 1180, "height": 820}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        r = await E("()=>{ try{ return !!(dust && dust.material && dust.material.map); }catch(e){ return 'ERR '+e.message; } }")
        ok(r is True, f"① 먼지 입자 둥근 점(map) {r}")
        await E("()=>{ Study.ctx('elem'); StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.open(); StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.view('stPath'); }"); await pg.wait_for_timeout(1200)
        r = await E("""()=>{ const M=document.querySelector('#scStudy .stMap.wm'); if(!M) return {body:document.body.className, cls:document.getElementById('scStudy').className}; const z=M.querySelector('.zBan'), B=[...M.querySelectorAll(':scope > .stWBox')].slice(0,2).map(b=>b.getBoundingClientRect()), m=M.getBoundingClientRect(), zr=z && z.getBoundingClientRect();
            return {body:document.body.className.indexOf('tabL')>=0, zc: zr ? Math.round((zr.x+zr.width/2)-(m.x+m.width/2)) : null, zAbove: zr && B[0] ? zr.bottom<=B[0].top+2 : null, sameRow: B.length===2 ? Math.abs(B[0].top-B[1].top) : null, lr: B.length===2 ? B[0].left<B[1].left : null}; }""")
        ok(r["body"] and r["zc"] is not None and abs(r["zc"]) < 30 and r["zAbove"] and r["sameRow"] is not None and r["sameRow"] < 3 and r["lr"], f"② 두 칸 지도 구역 띠 가운데 위 · Stage 1·2 나란히 {r}")
        await E("""()=>{ Study.ctx('kinder'); StudyUI.set='kinder'; StudyUI.start(0,false); const L=Study.lessons('kinder'); const w=L[0].ws[0]; const q={t:'pic', w, opts:L[0].ws.slice(0,4)}; }""")
        r = await E("""async ()=>{ for(let n=0;n<60;n++){ const q=StudyUI.qs[StudyUI.i]; if(q && /pic/.test(q.t) && !StudyUI.locked) break; try{ const U=StudyUI; if(U.locked||q.t==='intro'){ document.getElementById('stCheck').click(); } else { const k=q.opts ? q.opts.findIndex(o=>o.en===q.w.en) : 0; const b=document.querySelector('#stQ .stOpt[data-k="'+Math.max(0,k)+'"]'); if(b) b.click(); else document.getElementById('stCheck').click(); } }catch(e){} await new Promise(z=>setTimeout(z,150)); }
            const o=document.querySelector('#stQ .stOpt.pic'); return o ? [StudyUI.qs[StudyUI.i].t, parseFloat(getComputedStyle(o).fontSize), document.getElementById('stQ').className] : null; }""")
        ok(r and r[1] >= 40, f"③ 패드 가로 그림 보기 글자(그림) 크기 {r}")
        await E("""()=>{ Study.ctx('mv1'); StudyUI.open(); StudyUI.set='mv1'; const L=Study.lessons('mv1'); const x=L.find(l=>!l.fin && Study.storyFor('mv1', l)); StudyUI.readStory(Study.storyFor('mv1', x), x); }"""); await pg.wait_for_timeout(800)
        r = await E("()=>[...document.querySelectorAll('#stQ .rdCard .rdS')].filter(e=>e.offsetParent).map(e=>{ const b=e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.width)]; })")
        ok(len(r) >= 3 and len(set(x[0] for x in r)) == 1 and len(set(x[1] for x in r)) == 1, f"④ 짧은 글 줄 왼쪽 끝·폭 같음 {r[:4]}")
        await pg.close()
        # ── 휴대폰 (주간 보스 띠 · 레이드 카드 — 레이드는 이 기기 안에서만 도는 방 HY_FB_LOCAL 로)
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); await boot(T); K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append(str(e))); await boot(K, iso=1); E = K.evaluate
        r = await E("""()=>{ const s=document.createElement('div'); s.className='rs'; s.style.cssText='position:relative;width:360px;height:220px'; const mo=document.createElement('b'); mo.className='rsMore'; mo.textContent='+3명'; s.appendChild(mo); document.body.appendChild(s); const c=getComputedStyle(mo); const r=[c.top, c.bottom]; s.remove(); return r; }""")
        ok(r[0] == "10px", f"⑤ 「같이 싸우는 중」 띠가 위쪽(top 10px) — 아래 이름표를 안 가림 {r}")
        room = await T.evaluate("()=>{ Raid.host('g34', [], 0, null, 900, 'all'); return Raid.room; }"); await T.wait_for_timeout(800)
        await E("()=>RaidJoin.open()"); await K.wait_for_timeout(200)
        await E("(r)=>{ document.getElementById('rdRoomIn').value=r; document.getElementById('rdNameIn').value='미나'; document.querySelector('[data-rj=go]').click(); }", room); await K.wait_for_timeout(1200)
        await E("()=>{ try{ RaidTut.open(); }catch(e){} }")
        r = await E("""async ()=>{ for(let n=0;n<40;n++){ const L=document.getElementById('arLanes'); if(L && L.children.length===3 && L.children[0].offsetWidth) break; await new Promise(z=>setTimeout(z,200)); }
            const L=document.getElementById('arLanes'); if(!L || L.children.length!==3) return 'nolanes'; return [...L.children].map(c=>{ const b=c.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.right)]; }).concat([[innerWidth]]); }""")
        ok(isinstance(r, list) and all(x[0] >= 0 and x[1] <= r[-1][0] for x in r[:-1]), f"⑥ 휴대폰 레이드 단어 카드 화면 안 {r}")
        await ctx.close()
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
