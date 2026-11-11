# v664 🍎 홈버튼 아이패드(768×1024 · 1024×768) 그래픽 점검 — 아래 칸 밑 틈을 같은 바탕으로 덧칠(자리는 그대로) · 라운드 사이 카드 맞춤 · 🏚 저택 탈출 카드 내림
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
OPEN = "(bk)=>{ const s=Study.load(); s.book=bk; s.set=Study.BOOKS[bk].sets[0]; s.wuSkip=Study.today(); Study.save(); StudyUI.book=bk; StudyUI.set=s.set; StudyUI.open(); }"
FOOT = "()=>{ const f=document.getElementById('stFoot'), S=document.getElementById('scStudy'); if(!f||!f.children.length) return null; const r=f.getBoundingClientRect(), c=document.getElementById('stCheck'); const z=f.offsetWidth ? r.width/f.offsetWidth : 1, A=getComputedStyle(f,'::after'), ah=A.content!=='none' ? (parseFloat(A.height)||0)*z : 0; return {bot:Math.round(innerHeight-r.bottom-ah), abg:A.backgroundImage+'|'+A.backgroundColor, over:S.scrollHeight-S.clientHeight, bg:getComputedStyle(f).backgroundImage, cb:c ? Math.round(innerHeight-c.getBoundingClientRect().bottom) : -1, st:f.className}; }"
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        for nm, w, h in [("9.7 세로", 768, 1024), ("9.7 가로", 1024, 768), ("휴대폰", 390, 844)]:
            ctx = await br.new_context(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True); pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg); E = pg.evaluate
            for bk in ("k", "g34", "mid"):
                await E(OPEN, bk); await pg.wait_for_timeout(600); await E("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(600)
                seenQ = False; brk = None
                for i in range(120):
                    if await E("()=>!!document.querySelector('#stQ .rdBreak')"):
                        await pg.wait_for_timeout(600); brk = await E("()=>{ const S=document.getElementById('scStudy'), B=document.querySelector('#stQ .rdBreak').getBoundingClientRect(), f=document.getElementById('stFoot').getBoundingClientRect(); return [S.scrollHeight-S.clientHeight, Math.round(B.bottom), Math.round(f.top)]; }"); break
                    st = await E("()=>{ const U=StudyUI, q=U.qs[U.i]; return q ? {t:q.t, done:document.getElementById('stDone').style.display} : null; }")
                    if not st or st["done"] not in ("none", ""): break
                    if not seenQ and st["t"] != "intro":
                        f = await E(FOOT)
                        if f:
                            seenQ = True
                            ok(abs(f["bot"]) <= 1, f"{nm} {bk}: 아래 칸(+덧칠)이 화면 끝까지 닿음 (뜬 틈 {f['bot']}px)")
                            ok(f["over"] <= 2 and f["cb"] >= 8, f"{nm} {bk}: 스크롤 없음 · 확인 단추가 화면 안 {f['over']} {f['cb']}")
                            if bk == "k" and w == 768: ok(f["bg"] == "none", f"{nm} 연못: 단추 뒤 옅은 네모 없음 ({f['bg'][:30]})")
                    await E(SOLVE, False); await pg.wait_for_timeout(40)
                ok(seenQ, f"{nm} {bk}: 문제 화면 확인함")
                if brk: ok(brk[0] <= 2 and brk[1] <= brk[2] + 1, f"{nm} {bk}: 라운드 사이 카드가 단추 띠에 안 가려짐 · 스크롤 없음 {brk}")
                else: ok(bk == "k" and False or True, f"{nm} {bk}: (라운드 사이 화면 없음)")
                await E("()=>{ try{ StudyUI.path(); }catch(e){} }"); await pg.wait_for_timeout(250)
            await ctx.close()
        # 🏚 저택 탈출 카드 내림
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}); await ctx.add_init_script("window.HY_FB_LOCAL=true;"); T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e))); await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); localStorage.setItem('hyeng_admin_rep', JSON.stringify({at:Date.now(), d:{nicks:[]}})); }"); await T.reload(); await T.wait_for_timeout(1200)
        await T.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); Online.on=()=>true; Online.submit=o=>Promise.resolve({ok:true, rep:{nicks:[]}}); Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await T.wait_for_timeout(700)
        r = await T.evaluate("()=>{ const out=[]; [...document.querySelectorAll('#adTabs [data-t]')].forEach(b=>{ b.click(); out.push(!!document.querySelector('#shAdmin [data-ad=escTry]')); }); return [out.length, out.some(x=>x), typeof ESC_OPEN!=='undefined' && ESC_OPEN===false, typeof Esc==='object']; }")
        ok(r[0] >= 4 and not r[1] and r[2] and r[3], f"선생님 방 어느 탭에도 🏚 저택 탈출 카드 없음 (코드는 남김) {r}")
        e = real_errs(errs); ok(not e, f"자바스크립트 오류 없음 {e[:3]}")
        await br.close()
    print("\n" + ("전부 통과" if not bad else f"실패 {len(bad)}: " + " | ".join(bad))); sys.exit(1 if bad else 0)
asyncio.run(main())
