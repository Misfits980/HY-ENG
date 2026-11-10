# v634 점검 고치기 묶음 — 휴대폰 가로 끝 화면 두 칸 · 고르기 버튼 붙음 · 수업 번호판/소식지 · 가로 「짐작해 봐요」 두 칸
#   · head 그림 · 유치원 그림 보기 쉬운 말만 · 패드 도감 크기 · 처음 켠 기기 환영 · 미끼 글 · 랭킹 규칙 한 줄
import asyncio, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/fix634_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

BTNS = """()=>[...document.querySelectorAll('#scStudy #stDoneIn button')].filter(b=>b.offsetParent).map(b=>{ const r=b.getBoundingClientRect(); return [b.textContent.trim().slice(0,10), Math.round(r.top), Math.round(r.bottom)]; })"""

async def endscreen(pg, book):
    await pg.evaluate("(bk)=>{ Online.on=()=>false; const s=Study.load(); s.book=bk; Study.save(); StudyUI.open(); StudyUI.start(0,false); }", book); await pg.wait_for_timeout(800)
    for k in range(140):
        if await pg.evaluate("()=>!StudyUI.qs[StudyUI.i]"): break
        await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(40)
    await pg.wait_for_timeout(1500)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # ① 끝 화면: 가로 휴대폰 3가지 + 세로 — 버튼이 다 화면 안 · 스크롤 없음
        for (w, h), book in (((915, 412), "g12"), ((844, 390), "g34"), ((667, 375), "k"), ((390, 844), "g12"), ((1180, 820), "g56")):
            pg = await b.new_page(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await boot(pg); await endscreen(pg, book)
            bs = await pg.evaluate(BTNS)
            sc = await pg.evaluate("()=>{ const S=document.getElementById('scStudy'); return [S.scrollHeight-S.clientHeight, S.classList.contains('vLand'), !!document.querySelector('#stDoneIn > .vColL')]; }")
            land = w > h and h <= 520
            z = await pg.evaluate("()=>parseFloat(document.getElementById('stDoneIn').style.zoom||'1')")
            ok(len(bs) >= 2 and all(x[2] <= h + 1 for x in bs) and sc[0] <= 2 and (sc[1] == land or (w > h and sc[1])) and sc[2] == sc[1] and z >= .7,
               f"{w}×{h} {book} 끝 화면 버튼 다 보임 · 스크롤 {sc[0]} · 두 칸 {sc[1]} · 줄임 {z} {bs}")
            if land and w == 915: await pg.screenshot(path=f"{OUT}end_{w}.png")
            e = real_errs(errs); ok(not e, f"{w}×{h} 오류 없음 {e[:2]}")
            await pg.close()
        # ② 가로: 달리기 책 고르기 「전부 섞어서 ▶」 · 수업 번호판 · 소식지 버튼
        pg = await b.new_page(viewport={"width": 915, "height": 412}, is_mobile=True, has_touch=True); await boot(pg)
        await pg.evaluate("()=>{ document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>document.querySelector('#selRule [data-v=normal]').click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>document.getElementById('btnStepNext').click()"); await pg.wait_for_timeout(700)
        for k in range(2):
            await pg.evaluate("()=>{ const t=[...document.querySelectorAll('[id^=sel] [data-v]')].find(e=>e.offsetParent && e.getBoundingClientRect().width>0); if(t) t.click(); }"); await pg.wait_for_timeout(700)
        r = await pg.evaluate("()=>{ const g=document.getElementById('bkGo'); const r=g.getBoundingClientRect(); const e=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return [Math.round(r.top), Math.round(r.bottom), g.contains(e)]; }")
        ok(r[1] <= 412 and r[2], f"가로: 책 고른 뒤 시작 버튼 화면 안 · 누를 수 있음 {r}")
        await pg.screenshot(path=OUT + "book_phL.png")
        await pg.evaluate("()=>{ document.querySelectorAll('#scSetup .tsec.on .stepNext').forEach(()=>{}); goStep && goStep(0); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>document.querySelector('[data-v=join]').click()"); await pg.wait_for_timeout(900)
        r = await pg.evaluate("()=>{ const g=[...document.querySelectorAll('.rdJoinIn button')].find(b=>/들어가기 ▶/.test(b.textContent)); const z=[...document.querySelectorAll('.rjK')].find(b=>b.textContent==='0'); const a=g.getBoundingClientRect(), c=z.getBoundingClientRect(); return [Math.round(a.bottom), Math.round(c.bottom)]; }")
        ok(r[0] <= 412 and r[1] <= 412, f"가로: 수업 번호판 「들어가기」·「0」 화면 안 {r}")
        await pg.screenshot(path=OUT + "join_phL.png")
        await pg.close()
        pg = await b.new_page(viewport={"width": 844, "height": 390}, is_mobile=True, has_touch=True)
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1600)
        r = await pg.evaluate("()=>{ const g=document.getElementById('btnNewsOk'); const r=g.getBoundingClientRect(); return [document.getElementById('shNews').classList.contains('on'), Math.round(r.bottom)]; }")
        ok(r[0] and r[1] <= 390, f"가로: 소식지 「확인했어요」 화면 안 {r}")
        await pg.close()
        # ③ 가로 「짐작해 봐요」 = 두 칸 (문제 왼쪽 · 돌 오른쪽) · 세로는 그대로
        for (w, h), two in (((1180, 820), True), ((915, 412), True), ((820, 1180), False)):
            pg = await b.new_page(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True); await boot(pg)
            await pg.evaluate("()=>{ Online.on=()=>false; const s=Study.load(); s.book='g12'; Study.save(); StudyUI.open(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(900)
            r = await pg.evaluate("""()=>{ const q=StudyUI.qs[StudyUI.i], Q=document.getElementById('stQ'); const pr=Q.querySelector('.stPrompt').getBoundingClientRect(); const o=[...Q.querySelectorAll('.stOpt')].map(x=>x.getBoundingClientRect());
                const fs=[...Q.querySelectorAll('.stOpt')].map(x=>x.scrollWidth<=x.clientWidth+2); return {t:q.t, two:Q.classList.contains('two'), right:o.every(x=>x.left>=pr.right-4), fit:fs.every(Boolean)}; }""")
            ok(r["t"] == "intro" and (r["right"] == two) and r["fit"], f"{w}×{h} 짐작해 봐요 두 칸={two} {r}")
            if w == 915: await pg.screenshot(path=OUT + "guess_phL.png")
            await pg.close()
        # ④ head 그림 · 유치원 그림 보기
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        r = await pg.evaluate("""async ()=>{ Online.on=()=>false; const out={}; for(const bk of ['k','g12']){ const s=Study.load(); s.book=bk; Study.save(); StudyUI.open(); await new Promise(z=>setTimeout(z,400)); StudyUI.start(0,false);
              const h=(StudyUI.qs||[]).find(q=>q.w && q.w.en==='head'); out[bk]=h ? String(h.w.emoji||'') : 'none'; } return out; }""")
        ok(all("head.webp" in v for v in r.values()), f"head = 직접 그린 그림 (🗣️ 아님) {r}")
        r = await pg.evaluate("""async ()=>{ const s=Study.load(); s.book='k'; Study.save(); StudyUI.open(); await new Promise(z=>setTimeout(z,400)); const L={}, ex=new Set(); let n=0;
              for(let st=0; st<8; st++) for(let rep=0; rep<3; rep++){ try{ StudyUI.start(st,false); }catch(e){ continue; }
                (StudyUI.qs||[]).forEach(q=>{ if(q.t!=='pic' || !q.opts) return; n++; q.opts.forEach(o=>{ if(o.en===q.w.en) return; const l=o.level||0; L[l]=(L[l]||0)+1; if(l>1) ex.add(o.en); }); }); }
              return {n, L, ex:[...ex].slice(0,8)}; }""")
        ok(r["n"] >= 20 and not any(int(k) > 1 for k in r["L"]), f"유치원 그림 고르기 보기 = 쉬운 그림 단어만 {r}")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:2]}")
        await pg.close()
        # ⑤ 패드 세로 도감 = 상점과 같은 배율
        pg = await b.new_page(viewport={"width": 820, "height": 1180}, is_mobile=True, has_touch=True); await boot(pg)
        r = []
        for bid in ("btnDex", "btnShop"):
            await pg.evaluate("(i)=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); document.getElementById(i).click(); }", bid); await pg.wait_for_timeout(800)
            r.append(await pg.evaluate("()=>{ const s=document.querySelector('.sheet.on > .sheetIn'); return [Math.round(s.getBoundingClientRect().width), getComputedStyle(s).zoom]; }"))
        ok(r[0][1] == r[1][1] and float(r[0][1]) > 1.2 and r[0][0] >= 600, f"패드 도감 크기 = 상점과 같음 {r}")
        await pg.screenshot(path=OUT + "dex_pad.png")
        await pg.close()
        # ⑥ 처음 켠 기기 = 환영 한 장 (소식지 아님) · 「첫 공부 시작」 = 오늘의 30 · 다시 켜면 안 나옴
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("window.HY_HELLO=true")
        pg = await ctx.new_page(); await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1800)
        r = await pg.evaluate("()=>[!!document.getElementById('helloMt'), document.getElementById('shNews').classList.contains('on')]")
        ok(r == [True, False], f"처음 켠 기기 = 환영 · 소식지 안 뜸 {r}")
        await pg.screenshot(path=OUT + "hello.png")
        await pg.evaluate("()=>document.querySelector('#helloMt [data-d]').click()"); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("()=>document.getElementById('scStudy').classList.contains('on')"), "「첫 공부 시작」 = 오늘의 30 열림")
        await pg.reload(); await pg.wait_for_timeout(1800)
        r = await pg.evaluate("()=>[!!document.getElementById('helloMt'), document.getElementById('shNews').classList.contains('on')]")
        ok(r == [False, False], f"다시 켜면 환영도 소식지도 안 뜸 {r}")
        await ctx.close()
        # ⑦ 미끼 글 (마을 점검 중) · 랭킹 규칙 한 줄 · Daily 30 카드 글
        pg = await b.new_page(viewport={"width": 390, "height": 844}); await boot(pg)
        r = await pg.evaluate("()=>{ window.HY_TOWN_SHUT=1; return [Town.baitHtml(5), townOpen()]; }")
        ok("새 마을에서 써요" in r[0] and r[1] is False, f"마을 닫힘 = 「미끼 · 새 마을에서 써요」 {r}")
        r = await pg.evaluate("()=>[LiveRank.RULE.study.replace(/<[^>]+>/g,'').length, document.querySelector('#selRule [data-v=daily] small').textContent]")
        ok(r[0] < 60 and "30단어" not in r[1], f"랭킹 규칙 짧게 · Daily 30 카드 글 {r}")
        await pg.close()
        await b.close()
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pic_audit.py")], capture_output=True, text=True)
    ok(r.returncode == 0 and "| 그림 |" in r.stdout, "헷갈리는 그림 찾기 도구 (tools/pic_audit.py)")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
