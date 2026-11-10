# v640 🧪 단어 연구소 (중등) — 재료 검사 · 로드맵 단추 · 주문 8개 풀기(맞힘·다른 발견·없는 단어·철자 고르기) · 결과·보석 · 발견 노트 · 5 화면 스크롤 없음
import asyncio, sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/lab640_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
D = json.load(open(os.path.join(ROOT, "data", "lab.json")))

def data_check():
    R = D["r"]; ok(len(R) >= 600, f"재료 {len(R)}개")
    res = [r[3] for r in R]; ok(len(res) == len(set(res)), "만든 단어 겹침 없음")
    badr = [r for r in R if not all(r[:6]) or r[2] not in D["a"] or not re.fullmatch(r"[a-z]+", r[3])]
    ok(not badr, f"칸 빠짐 없음 {badr[:3]}")
    # 철자 규칙이 실제로 맞는지 (규칙 + 뿌리 + 붙는 말 → 결과)
    def make(r):
        b, a, rl = r[0], r[2], r[5]
        if a.endswith("-"): return a[:-1] + b
        s = a[1:]
        return {"+" : b + s, "e": b[:-1] + s, "y": b[:-1] + "i" + s, "d": b + b[-1] + s, "l": b[:-1] + "y"}[rl]
    wrong = [r for r in R if make(r) != r[3]]
    ok(not wrong, f"규칙대로 만들면 결과와 같음 {wrong[:3]}")
    for w in ("chicken", "later", "resource", "spaceship"):
        ok(w not in res, f"억지 단어 없음: {w}")

GO = """async (want)=>{ const g=Lab.g, r=g.r; const pick=(k,v)=>document.querySelector('#labMt [data-lb='+k+'][data-v="'+v+'"]').click();
  if(want==='wrong'){ const b=g.c.b.find(x=>x!==r[0]), a=g.c.a.find(x=>!Lab.find(b,x)); if(b && a){ pick('b',b); pick('a',a); document.querySelector('#labMt [data-lb=mix]').click(); } }
  pick('b', r[0]); pick('a', r[2]); document.querySelector('#labMt [data-lb=mix]').click(); await new Promise(z=>setTimeout(z,60));
  let sp=false; if(Lab.g.ph==='sp'){ sp=true; document.querySelector('#labMt [data-lb=sp][data-v="'+r[3]+'"]').click(); }
  return {ph:Lab.g.ph, sp, w:r[3]}; }"""

async def main():
    data_check()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        # 중등 로드맵 단추
        await pg.evaluate("()=>{ StudyUI.open(); StudyUI.book='mid'; StudyUI.set='mid'; StudyUI.path(); }"); await pg.wait_for_timeout(500)
        has = await pg.evaluate("()=>{ const b=document.querySelector('.mdLab'); return b && b.textContent; }")
        ok(has and "단어 연구소" in has, f"중등 로드맵에 🧪 단추 {has}")
        await pg.screenshot(path=OUT + "map_ph.png")
        if has:
            await pg.click(".mdLab"); await pg.wait_for_timeout(800)
        else:
            await pg.evaluate("()=>Lab.open()"); await pg.wait_for_timeout(800)
        ok(await pg.evaluate("()=>!!document.querySelector('#labMt .lbHome')"), "연구소 첫 화면")
        await pg.screenshot(path=OUT + "home_ph.png")
        g0 = await pg.evaluate("()=>Wallet.gems()")
        await pg.click("#labMt [data-lb=start]"); await pg.wait_for_timeout(200)
        L = await pg.evaluate("()=>Lab.g.L.map(r=>r.slice())")
        ok(len(L) == 8 and len({r[3] for r in L}) == 8, f"주문 8개 다 다름 {[r[3] for r in L]}")
        ok(all(r[5] == "+" for r in L[:3]), "앞 3개는 철자 안 바뀌는 쉬운 주문")
        # 카드: 정답 뿌리·붙는 말이 들어 있고 4장씩
        c = await pg.evaluate("()=>({b:Lab.g.c.b, a:Lab.g.c.a, r:Lab.g.r})")
        ok(len(c["b"]) == 4 and len(c["a"]) == 4 and c["r"][0] in c["b"] and c["r"][2] in c["a"] and len(set(c["b"])) == 4 and len(set(c["a"])) == 4, f"카드 4+4 · 정답 포함 {c['b']} {c['a']}")
        await pg.evaluate("()=>{ document.querySelector('#labMt [data-lb=b]').click(); document.querySelector('#labMt [data-lb=a]').click(); }")
        await pg.screenshot(path=OUT + "pick_ph.png")
        await pg.evaluate("()=>{ Lab.g.b=null; Lab.g.a=null; Lab.draw(); }")
        # 없는 단어 → 흔들림 · 2번 틀리면 힌트
        r = await pg.evaluate("""()=>{ const g=Lab.g, r=g.r; let n=0; for(const b of g.c.b) for(const a of g.c.a){ if(n>=2) break; if(!Lab.find(b,a)){ g.b=b; g.a=a; Lab.mix(); n++; } }
            return {fx:g.fx, msg:g.msg, hint:!!document.querySelector('#labMt .lbG button.hint'), tries:g.tries}; }""")
        ok(r["fx"] == "bad" and "없어요" in r["msg"] and r["hint"] and r["tries"] == 2, f"없는 단어 2번 → 힌트 {r}")
        await pg.screenshot(path=OUT + "bad_ph.png")
        # 다른 진짜 단어 = 💡 발견 (주문은 그대로)
        r = await pg.evaluate("""()=>{ const g=Lab.g, r=g.r; const alt=Lab.D.r.find(x=>x!==r && Lab.D.r.indexOf(x)>=0 && x[0]!==r[0]); g.c.b[g.c.b.indexOf(g.c.b.find(x=>x!==r[0]))]=alt[0]; if(g.c.a.indexOf(alt[2])<0) g.c.a[g.c.a.findIndex(x=>x!==r[2])]=alt[2];
            g.b=alt[0]; g.a=alt[2]; Lab.mix(); return {fx:g.fx, msg:g.msg, ph:g.ph, f:!!Lab.st().f[alt[3]], w:alt[3]}; }""")
        ok(r["fx"] == "alt" and r["ph"] == "pick" and r["f"] and r["w"] in r["msg"], f"다른 단어 = 💡 발견 · 주문 그대로 {r}")
        await pg.screenshot(path=OUT + "alt_ph.png")
        # 철자 고르기 단계가 있는 주문을 하나 찾아 확인
        r = await pg.evaluate("""()=>{ const s=Lab.D.r.find(x=>x[5]==='e'); const g=Lab.g; g.L[g.i]=s; Lab.next(g.i); g.b=s[0]; g.a=s[2]; Lab.mix();
            const o=[...document.querySelectorAll('#labMt [data-lb=sp]')].map(b=>b.dataset.v); return {ph:g.ph, o, w:s[3], naive:s[0]+s[2].slice(1)}; }""")
        ok(r["ph"] == "sp" and r["w"] in r["o"] and r["naive"] in r["o"], f"철자 고르기 {r}")
        await pg.screenshot(path=OUT + "spell_ph.png")
        await pg.click(f"#labMt [data-lb=sp][data-v=\"{r['naive']}\"]")
        r2 = await pg.evaluate("()=>({ph:Lab.g.ph, miss:Lab.g.spMiss, dis:document.querySelector('#labMt [data-lb=sp].bad')?.disabled})")
        ok(r2["ph"] == "sp" and r2["miss"] == 1 and r2["dis"], f"틀린 철자 = 줄 긋고 다시 {r2}")
        await pg.click(f"#labMt [data-lb=sp][data-v=\"{r['w']}\"]"); await pg.wait_for_timeout(100)
        r2 = await pg.evaluate("()=>({ph:Lab.g.ph, t:document.querySelector('#labMt .lbRes').textContent, ok:Lab.g.ok})")
        ok(r2["ph"] == "ok" and "e 가 빠져요" in r2["t"] and r2["ok"] == 0, f"결과 + 규칙 설명 · 한 번에 아님 {r2}")
        await pg.screenshot(path=OUT + "res_ph.png")
        # 나머지 7개는 한 번에
        await pg.click("#labMt [data-lb=nx]")
        for i in range(7):
            r = await pg.evaluate(GO, "ok")
            ok(r["ph"] == "ok", f"주문 {i+2} {r}")
            await pg.click("#labMt [data-lb=nx]")
        r = await pg.evaluate("()=>({t:document.querySelector('#labMt .lbEnd')?.textContent, g:Wallet.gems()})")
        ok(r["t"] and "7" in r["t"] and r["g"] - g0 == 2, f"결과 7/8 · 💎2 {r['g']-g0}")
        await pg.screenshot(path=OUT + "end_ph.png")
        # 같은 날 두 번째 판 = 보석 없음
        await pg.click("#labMt [data-lb=start]")
        for i in range(8):
            await pg.evaluate(GO, "ok"); await pg.click("#labMt [data-lb=nx]")
        ok(await pg.evaluate("()=>Wallet.gems()") - g0 == 2, "하루 한 번만 💎")
        # 발견 노트
        await pg.click("#labMt .lbEnd [data-lb=book]"); await pg.wait_for_timeout(100)
        r = await pg.evaluate("()=>({n:document.querySelectorAll('#labMt .lbAf button').length, on:document.querySelectorAll('#labMt .lbAf button:not(.z)').length})")
        ok(r["n"] >= 25 and r["on"] >= 3, f"노트 붙는 말 칸 {r}")
        await pg.screenshot(path=OUT + "book_ph.png")
        await pg.click("#labMt .lbAf button:not(.z)"); await pg.wait_for_timeout(100)
        r = await pg.evaluate("()=>document.querySelectorAll('#labMt .lbWl span:not(.q)').length")
        ok(r >= 1, f"붙는 말 눌러 찾은 단어 {r}")
        await pg.screenshot(path=OUT + "book2_ph.png")
        # 발견 30개 = 💎5 (한 번)
        r = await pg.evaluate("""()=>{ const g=Wallet.gems(); const s=Lab.st(); const L=Lab.D.r.filter(x=>!s.f[x[3]]); let i=0; while(Lab.found()<31) Lab.disc(L[i++][3]); const a=Wallet.gems()-g; Lab.disc(L[i++][3]); return [a, Wallet.gems()-g]; }""")
        ok(r == [5, 5], f"발견 30개 💎5 한 번 {r}")
        await pg.click("#labMt [data-lb=x]")
        ok(await pg.evaluate("()=>!document.getElementById('labMt')"), "✕ 닫기")
        # 인터넷 끊김 = 안내
        await pg.evaluate("()=>{ Lab.D=null; Lab._p=null; window._f=window.fetch; window.fetch=()=>Promise.reject(new Error('x')); }")
        await pg.evaluate("()=>Lab.open()"); await pg.wait_for_timeout(300)
        t = await pg.evaluate("()=>document.querySelector('#labMt').textContent")
        ok("인터넷" in t, f"자료 못 받으면 안내 {t[:40]}")
        await pg.evaluate("()=>{ window.fetch=window._f; Lab.close(); }")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await pg.close()
        for nm, vp in (("ph", (390, 844)), ("pad", (820, 1180)), ("tv", (1920, 1080)), ("phL", (915, 412)), ("padL", (1180, 820)), ("se", (320, 568))):
            pg = await b.new_page(viewport={"width": vp[0], "height": vp[1]}, is_mobile=nm != "tv", has_touch=nm != "tv"); await boot(pg)
            await pg.evaluate("async ()=>{ await Lab.open(); }"); await pg.wait_for_timeout(300)
            res = {}
            for stg in ("home", "pick", "sp", "ok", "end", "book"):
                if stg == "pick": await pg.evaluate("()=>{ Lab.start(); const g=Lab.g; g.b=g.c.b[0]; g.a=g.c.a[0]; g.tries=2; g.fx='alt'; g.msg='💡 <b>example</b> (보기) 발견! 노트에 넣었어요. 하지만 주문한 뜻은 아니에요'; Lab.draw(); }")
                if stg == "sp": await pg.evaluate("()=>{ const s=Lab.D.r.find(x=>x[5]==='y'); const g=Lab.g; g.L[g.i]=s; Lab.next(g.i); g.b=s[0]; g.a=s[2]; Lab.mix(); }")
                if stg == "ok": await pg.evaluate("()=>{ Lab.win(); }")
                if stg == "end": await pg.evaluate("()=>{ Lab.g.ok=6; Lab.g.nw=Lab.D.r.slice(0,10); Lab.end(); }")
                if stg == "book": await pg.evaluate("()=>{ Lab.book(); }")
                await pg.wait_for_timeout(120)
                r = await pg.evaluate("""()=>{ const d=document.querySelector('#labMt .lbIn'); const over=[...d.querySelectorAll('button, .lbOrd, .lbRes, .lbNw, .lbHero')].filter(e=>{ const r=e.getBoundingClientRect(); return r.bottom>innerHeight+1 || r.right>innerWidth+1 || r.left<-1; }).length;
                    return {sh:d.scrollHeight-d.clientHeight, over, w:document.documentElement.scrollWidth-innerWidth}; }""")
                res[stg] = r
                ok(r["sh"] <= 2 and r["over"] == 0 and r["w"] <= 0, f"{nm} {stg} 한 화면 {r}")
                await pg.screenshot(path=f"{OUT}{nm}_{stg}.png")
            await pg.close()
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
