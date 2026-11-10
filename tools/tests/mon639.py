# v639 📊 이달의 나 — 답·Stage·달리기가 달마다 쌓임 · 미션 창에서 열기 · 지난달 ◀ · 새 달 첫 주 자동 한 번 · 📸 그림 · 5 화면 스크롤 없음
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/mon639_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

SEED = """()=>{ const M=MonthCard, y=M.ym(), p=M.prev(y), [a]=M.span(y), [pa]=M.span(p);
  const o={}; o[y]={d:{1:1,2:1,3:1,5:1,8:1,9:1}, r:180, w:40, les:6, run:4}; o[p]={d:{2:1,3:1,4:1,10:1}, r:120, w:30, les:3, run:2};
  localStorage.setItem(M.key(), JSON.stringify(o)); M.o=null;
  const S=Study.load(); S.sd=S.sd||{}; ['apple','banana','grape','lemon','melon','peach','cherry','orange','tiger','lion'].forEach((en,i)=>S.sd[en]=a+i%5); S.sd.old=pa+1; S.sd.cat=pa+2;
  const W={ elephant:{r:3,w:3,l:'00111',d:a+2}, giraffe:{r:2,w:2,l:'0011',d:a+3}, monkey:{r:1,w:4,l:'10010',d:a+4}, zebra:{r:0,w:1,l:'0',d:a} };
  localStorage.setItem(Kid.k('hyeng_wstat_v1'), JSON.stringify(W)); try{ WStat.of('x'); }catch(e){}
  return y; }"""
FIT = """()=>{ const d=document.querySelector('#monMt .mnB'); if(!d) return null; const r=d.getBoundingClientRect();
  return {sh:d.scrollHeight-d.clientHeight, top:Math.round(r.top), bot:Math.round(r.bottom), ih:innerHeight, w:document.documentElement.scrollWidth-innerWidth}; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        # 쌓기: 답 · Stage · 달리기
        r = await pg.evaluate("""async ()=>{ localStorage.removeItem(MonthCard.key()); MonthCard.o=null; Rank.record('apple', true); Rank.record('apple', false); Rank.record('dog', true); DM.add('les', 1); DM.add('run', 1); DM.add('q', 9);
            await new Promise(z=>setTimeout(z,600)); MonthCard.o=null; return MonthCard.load()[MonthCard.ym()]; }""")
        ok(r and r["r"] == 2 and r["w"] == 1 and r["les"] == 1 and r["run"] == 1 and str(__import__('datetime').date.today().day) in r["d"], f"답·Stage·달리기 쌓임 {r}")
        y = await pg.evaluate(SEED)
        # 미션 창 → 📊 이달의 나
        await pg.evaluate("()=>DM.view()"); await pg.wait_for_timeout(200)
        await pg.click("#dmView [data-dmmon]"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>{ const d=document.querySelector('#monMt'); return d && {t:d.querySelector('h3').textContent, st:[...d.querySelectorAll('.mnSt b')].map(x=>x.textContent), on:d.querySelectorAll('.mnG i.on').length, k:d.querySelector('.mnCh.k')?.textContent, h:d.querySelector('.mnCh.h')?.textContent, vs:d.querySelector('.mnVs')?.textContent, dm:!!document.getElementById('dmView')}; }")
        ok(r and r["st"] == ["220", "82%", "10"] and r["on"] == 6 and not r["dm"], f"이번 달 요약 {r}")
        ok(r and "elephant" in (r["k"] or "") and "giraffe" in (r["k"] or "") and "monkey" in (r["h"] or "") and "zebra" not in (r["k"] or "") + (r["h"] or ""), f"잘 아는/다시 볼 단어 {r and (r['k'], r['h'])}")
        ok(r and r["vs"] and "70" in r["vs"], f"지난달 비교 {r and r['vs']}")
        await pg.screenshot(path=OUT + "cur_ph.png")
        # ◀ 지난달
        await pg.click("#monMt .mnHd button.mnNav"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({st:[...document.querySelectorAll('#monMt .mnSt b')].map(x=>x.textContent), on:document.querySelectorAll('#monMt .mnG i.on').length, nx:!!document.querySelector('#monMt .mnHd button.mnNav[aria-label=\"이번 달\"]')})")
        ok(r["st"] == ["150", "80%", "2"] and r["on"] == 4 and r["nx"], f"◀ 지난달 {r}")
        # 📸 그림
        r = await pg.evaluate("()=>{ const c=MonthCard.png(); const u=c.toDataURL('image/png'); return [c.width, c.height, u.length]; }")
        ok(r[0] == 1080 and r[1] == 1350 and r[2] > 30000, f"📸 그림 만들기 {r}")
        b64 = await pg.evaluate("()=>{ MonthCard.view=MonthCard.ym(); return MonthCard.png().toDataURL('image/png').split(',')[1]; }")
        import base64; open(OUT + "share.png", "wb").write(base64.b64decode(b64))
        async with pg.expect_download() as dl:
            await pg.click("#monMt [data-mn=save]")
        d = await dl.value; ok(d.suggested_filename.startswith("hyeng-"), f"저장 파일 {d.suggested_filename}")
        await pg.click("#monMt [data-mn=x]"); ok(await pg.evaluate("()=>!document.getElementById('monMt')"), "닫기")
        # 새 달 첫 주 자동 (한 번만 · 3일 미만이면 안 띄움)
        n = await pg.evaluate("""async ()=>{ window.HY_MON=1; MonthCard.early=()=>true; localStorage.removeItem(MonthCard.key()+'_seen'); const sh=()=>!!document.getElementById('monMt');
            MonthCard.auto(); await new Promise(z=>setTimeout(z,2900)); const a=sh(), t=a && document.querySelector('#monMt h3').textContent; MonthCard.close();
            MonthCard.auto(); await new Promise(z=>setTimeout(z,2900)); const b2=sh(); MonthCard.close();
            localStorage.removeItem(MonthCard.key()+'_seen'); const o=MonthCard.load(); o[MonthCard.prev(MonthCard.ym())].d={1:1,2:1}; MonthCard.save();
            localStorage.setItem('hyeng_stats_v1', '{}');
            MonthCard.auto(); await new Promise(z=>setTimeout(z,2900)); const c=sh(); MonthCard.close(); return [a, t, b2, c]; }""")
        ok(n[0] and not n[2] and not n[3], f"새 달 자동: 한 번만 · 2일이면 안 띄움 {n}")
        # 기록 없는 아이 = 빈 달 안내 · 오류 없음
        await pg.evaluate("()=>{ localStorage.removeItem(MonthCard.key()); MonthCard.o=null; MonthCard.open(); }"); await pg.wait_for_timeout(200)
        t = await pg.evaluate("()=>document.querySelector('#monMt .mnMsg').textContent")
        ok("첫 공부" in t or "쌓이고" in t, f"빈 달 안내 {t}")
        await pg.evaluate("()=>MonthCard.close()")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await pg.close()
        for nm, vp in (("ph", (390, 844)), ("pad", (820, 1180)), ("tv", (1920, 1080)), ("phL", (915, 412)), ("padL", (1180, 820)), ("se", (320, 568))):
            pg = await b.new_page(viewport={"width": vp[0], "height": vp[1]}, is_mobile=nm != "tv", has_touch=nm != "tv"); await boot(pg)
            await pg.evaluate(SEED); await pg.evaluate("()=>MonthCard.open()"); await pg.wait_for_timeout(300)
            r = await pg.evaluate(FIT)
            lim = 2 if nm != "se" else 400   # 아주 작은 화면은 창 안에서만 굴림
            ok(r and r["sh"] <= lim and r["top"] >= 0 and r["bot"] <= r["ih"] and r["w"] <= 0, f"{nm} 한 화면 {r}")
            await pg.screenshot(path=f"{OUT}{nm}.png")
            await pg.evaluate("()=>{ MonthCard.close(); DM.view(); }"); await pg.wait_for_timeout(200)
            r = await pg.evaluate("()=>{ const d=document.querySelector('#dmView .rdJoinIn'); return d.scrollHeight-d.clientHeight; }")
            ok(r <= 2 or nm == "se", f"{nm} 미션 창 (📊 단추 넣고도) 스크롤 없음 {r}")
            await pg.close()
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
