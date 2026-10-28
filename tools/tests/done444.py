"""(v444) 사용자 사진 2장 — ① 유치원 🎈 처음 소리 글자 풍선이 그냥 색 타원 → 풍선 그림(미니게임 🧸 풍선 b0~3)
  ② Stage 끝 화면 개선: 내 캐릭터 축하 · 유치원은 💜 대신 🌟 (보라 별 없음) · ★ 3/3 겹침 뺌 · 다 만났으면 '5/5 만남' 막대 뺌
     · 내일 복습 = 작은 칩 · 💎 크게 톡 · 유치원은 「이름을 고르면 ⚔️ 공격 기회」 안내 안 함(유치원은 기회가 안 쌓여서 거짓 안내였음)"""
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
        for vw, vh, tag in [(390, 844, "ph"), (820, 1180, "pad")]:
            pg = await br.new_page(viewport={"width": vw, "height": vh})
            pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
            E = pg.evaluate
            await E("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(300)
            r = await E("""()=>{ const set='kinder', L=Study.lessons(set), les=L[0]; Study.ctx(set); let q=null;
                const w=les.ws[0], L0=w.en[0]; q={t:'bal', w, so:1, ans:L0, opts:[L0].concat(['u','v','l','m'].filter(c=>c!==L0).slice(0,3)), x:{mode:'bal'}};
                StudyUI.set=set; StudyUI.book='k'; StudyUI.les=les; StudyUI.qs=[q]; StudyUI.retryMode=true; StudyUI.begin();
                const bs=[...document.querySelectorAll('#stQ .stOpt.balO')]; return bs.map(b=>{ const c=getComputedStyle(b), r=b.getBoundingClientRect(); return [c.backgroundImage.slice(-14,-2), Math.round(r.width), Math.round(r.right)]; }); }""")
            ok(isinstance(r, list) and len(r) == 4 and all("webp" in x[0] for x in r) and max(x[2] for x in r) <= vw, f"① {tag} 풍선 그림 4개 · 화면 안 {r}")
            await pg.wait_for_timeout(400); await pg.screenshot(path=OUT + f"done444_bal_{tag}.png")
            # ② 유치원 ★3 완벽 끝 화면
            r = await E("""()=>{ const set='kinder', L=Study.lessons(set), k=1, x=L[k]; const s=Study.load(); s.seen={}; x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[Study.key(set,x.n)]=2; Study.save();
                StudyUI.set=set; StudyUI.book='k'; StudyUI.start(k,false); StudyUI.first=StudyUI.total; StudyUI.best=5; StudyUI.finish(true);
                const d=document.getElementById('stDoneIn'); return [d.querySelector('.stBigT').innerText, !!d.querySelector('.vHero .resCheer'), !!d.querySelector('.stDProg'), d.innerText.indexOf('★ 3 / 3')>=0, !!d.querySelector('.stGem.gpop'), d.innerText.indexOf('공격 기회')>=0]; }""")
            await pg.wait_for_timeout(1500)
            ok(r[0].startswith("🌟") and r[1] and not r[2] and not r[3] and not r[5], f"② {tag} 유치원 끝 화면 제목 {r[0]!r} · 캐릭터 {r[1]} · 만남 막대 {r[2]} · ★3/3 {r[3]} · 💎 {r[4]} · 공격 안내 {r[5]}")
            await pg.screenshot(path=OUT + f"done444_kid_{tag}.png")
            # 초등 끝 화면 (G3-4 ★1 처음)
            r = await E("""()=>{ const set='elem', L=Study.lessons(set), x=L[0]; const s=Study.load(); s.seen={}; s.lv={}; Study.save(); StudyUI.set=set; StudyUI.book='g34'; StudyUI.start(0,false); StudyUI.first=StudyUI.total; StudyUI.finish(true);
                const d=document.getElementById('stDoneIn'); return [d.querySelector('.stBigT').innerText, !!d.querySelector('.vHero'), d.innerText.slice(0,160).replace(/\\n/g,' | ')]; }""")
            await pg.wait_for_timeout(1500)
            ok(r[1], f"② {tag} 초등 끝 화면 {r[0]!r} · {r[2][:120]!r}")
            await pg.screenshot(path=OUT + f"done444_g34_{tag}.png")
            await pg.close()
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
