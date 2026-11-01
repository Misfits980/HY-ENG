"""(v506) C안 HUD — 시안 a18 대로
   ① 위 줄: 하트 왼쪽 · STAGE 가운데 · 점수 오른쪽 + 멈춤 — 휴대폰(360·390)·패드에서 서로 안 겹침, 판(배경) 없음
   ② 맞으면 문제 글자 초록 + 점수 밑 「+N」 · 「Correct!」 큰 글자 없음
   ③ 틀리면 빨강 + 그 자리에 정답 · COMBO 줄은 숨김 · 「Wrong!」 없음 · 다음 문제는 잠깐 뒤에
   ④ 안내 글은 같은 종류 처음 3문제만 · 사라짐 경고는 늘
   ⑤ 긴 뜻은 글자를 줄이거나 두 줄 — 화면 밖으로 안 나감
   ⑥ FEVER: 문제 글자 주황 형광 · 점수 밑 ×2 · 맞히면 「+N ×2」
   ⑦ COMBO: 0 은 흐리게(자리 고정) · 10 금 · 20 하늘 · 30 보라
   ⑧ 지대 이름: 영어 부제 대신 한글 한 줄 (RUINS 겹침 버그)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

START = "()=>{ G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; G.char='hero'; startGame(); G.inv=99; }"
PICK = """(right)=>{ const s=activeSet(); const n=s.gates.length; const ans=laneOfX(s.gates[s.q.answer].root.position.x, n);
  const l = right ? ans : (ans+1)%n; G.lane=l; P.x=laneX(l,G.lanes); judge(s); return s; }"""
RECTS = """()=>{ const r=id=>{ const b=document.getElementById(id).getBoundingClientRect(); return {l:b.left,r:b.right,t:b.top,b:b.bottom,w:b.width}; };
  return {life:r('uLives'), stage:r('chipStage'), score:r('uScore'), pause:r('pauseBtn'), ww:innerWidth,
          bg:getComputedStyle(document.getElementById('chipScore')).backgroundImage+'|'+getComputedStyle(document.getElementById('chipScore')).backgroundColor}; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        # ① 위 줄 — 세 가지 화면
        for (w, h) in ((360, 740), (390, 844), (820, 1180)):
            ctx = await br.new_context(viewport={"width": w, "height": h}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
            await pg.evaluate(START)
            await pg.evaluate("()=>{ G.stage=88; G.score=1234567; G.zone=zoneIndex(G.stage); updateHUD(); }")
            r = await pg.evaluate(RECTS)
            print(w, json.dumps(r))
            ok(r["life"]["l"] < r["stage"]["l"] and r["life"]["r"] <= r["stage"]["l"] + 1, f"{w}: 하트가 STAGE 왼쪽 · 안 겹침")
            ok(r["score"]["l"] >= r["stage"]["r"] - 1, f"{w}: 점수가 STAGE 오른쪽 · 안 겹침 (큰 점수)")
            ok(abs((r["stage"]["l"] + r["stage"]["r"]) / 2 - r["ww"] / 2) < 6, f"{w}: STAGE 가운데")
            ok(r["score"]["r"] <= r["pause"]["l"] + 1 and r["pause"]["r"] <= r["ww"], f"{w}: 점수 → 멈춤 순서 · 화면 안")
            ok(r["bg"].startswith("none|rgba(0, 0, 0, 0)"), f"{w}: 위 줄은 판 없이 글자만 {r['bg']}")
            await ctx.close()

        ctx = await br.new_context(viewport={"width": 390, "height": 844}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate(START); await pg.wait_for_timeout(200)
        await pg.add_style_tag(content="*{transition:none!important}")   # 색이 바뀌는 중간값 말고 끝 색을 읽게

        # ② 맞힘
        r = await pg.evaluate("""(PICK)=>{ const pick=eval(PICK); clearSets(); G.combo=4; spawnSet(); const before=document.getElementById('ptext').textContent;
            const s=pick(true); const w=document.getElementById('promptWrap'); const v=document.getElementById('verdict');
            return {ok:w.classList.contains('ok'), col:getComputedStyle(document.getElementById('ptext')).color, v:v.classList.contains('show'),
                    gain:document.getElementById('uGain').textContent, same:document.getElementById('ptext').textContent===before}; }""", PICK)
        print("맞힘", r)
        ok(r["ok"] and r["col"] == "rgb(93, 255, 158)", f"맞으면 문제 글자 초록 {r['col']}")
        ok(not r["v"], "「Correct!」 큰 글자 없음")
        ok(r["gain"].startswith("+") and "×2" not in r["gain"], f"점수 밑 +N {r['gain']}")
        await pg.wait_for_timeout(450)
        r = await pg.evaluate("()=>{ const w=document.getElementById('promptWrap'); return {ok:w.classList.contains('ok'), t:document.getElementById('ptext').textContent, q:activeSet()&&activeSet().q.prompt}; }")
        ok(not r["ok"] and r["q"] and r["t"].replace(" ", "").lower().endswith(str(r["q"]).replace(" ", "").lower()), f"잠깐 뒤 다음 문제로 {r}")

        # ③ 틀림
        r = await pg.evaluate("""(PICK)=>{ const pick=eval(PICK); clearSets(); G.combo=6; spawnSet(); const s=pick(false);
            const w=document.getElementById('promptWrap'), a=document.getElementById('pans'), c=document.querySelector('.cRow');
            const ans = s.q.dir==='k2e' ? s.q.word.en.toUpperCase() : s.q.word.ko;
            return {no:w.classList.contains('no'), col:getComputedStyle(document.getElementById('ptext')).color, ans, shown:a.querySelector('b').textContent,
                    adisp:getComputedStyle(a).display, cdisp:getComputedStyle(c).display, v:document.getElementById('verdict').classList.contains('show')}; }""", PICK)
        print("틀림", r)
        ok(r["no"] and r["col"] == "rgb(255, 90, 79)", f"틀리면 빨강 {r['col']}")
        ok(r["adisp"] == "block" and r["shown"] == r["ans"], f"그 자리에 정답 {r['shown']} / {r['ans']}")
        ok(r["cdisp"] == "none" and not r["v"], "COMBO 줄 숨김 · 「Wrong!」 없음")
        await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ G.falling=false; G.dead=false; G.lives=3; clearSets(); Hazards.clear(); spawnSet(); }")
        await pg.wait_for_timeout(60)
        r = await pg.evaluate("()=>document.getElementById('promptWrap').className")
        ok("no" not in r, f"새 문제에서 빨강 풀림 {r}")

        # ④ 안내 글
        r = await pg.evaluate("""()=>{ startGame(); G.inv=99; HudC.holdTo=0; const out=[], seen={}; for(let i=0;i<10;i++){ clearSets(); G.nextQ=null; spawnSet();
              const base=activeSet().q.dir==='k2e' ? '뜻에 맞는 단어' : '단어의 뜻'; seen[base]=(seen[base]||0)+1;
              out.push([seen[base], document.getElementById('plabel').classList.contains('labOff')]); } return out; }""")
        print("안내 글", r)
        r2 = await pg.evaluate("()=>{ const cs=getComputedStyle(document.getElementById('plabel')); return [document.getElementById('plabel').className, cs.borderTopWidth, cs.backgroundColor, cs.paddingTop]; }")
        ok(r2[1] == "0px" and r2[2] == "rgba(0, 0, 0, 0)" and r2[3] == "0px", f"(v507) 안내 글 숨긴 칸에 알약 테두리 없음 {r2}")
        ok(all((not m) for n, m in r if n <= 2) and all(m for n, m in r if n >= 5), f"같은 종류 처음 몇 문제만 안내 글 {r}")   # (시작 때 미리 나온 문제 1개가 섞일 수 있어 3·4번째는 안 봄)
        r = await pg.evaluate("""()=>{ const q={dir:'k2e', prompt:'소파', promptIsEn:false, word:{en:'sofa',ko:'소파'}}; G.labSeen={'뜻에 맞는 단어':9}; HudC.holdTo=0;
            showQuestion(q, {hideMode:'flash'}); return document.getElementById('plabel').classList.contains('labOff'); }""")
        ok(r is False, "사라짐 경고가 있으면 안내 글은 늘 보임")

        # ⑤ 긴 뜻
        r = await pg.evaluate("""()=>{ const out={}; for(const t of ['벽','물병, 주전자','자연스럽게 행동하다, 침착하다','TEMPERATURE','EXTRAORDINARY']){
              HudC.holdTo=0; showQuestion({dir:/[A-Z]/.test(t)?'e2k':'k2e', prompt:t, promptIsEn:/[A-Z]/.test(t), word:{en:'x',ko:t}}, null);
              const el=document.getElementById('ptext'), b=el.getBoundingClientRect(); out[t]={fs:el.style.fontSize, l:b.left, r:b.right, sw:el.scrollWidth, cw:el.clientWidth, h:b.height}; }
            return out; }""")
        print("긴 뜻", json.dumps(r, ensure_ascii=False))
        for k, v in r.items():
            ok(v["l"] >= 0 and v["r"] <= 390 and v["sw"] <= v["cw"] + 2, f"「{k}」 화면 안 {v}")
        ok(int(r["벽"]["fs"][:-2]) >= 50, "짧은 뜻은 큰 글자")
        ok(int(r["물병, 주전자"]["fs"][:-2]) >= 36, f"「물병, 주전자」 한 줄 크게 {r['물병, 주전자']['fs']}")

        # ⑥ FEVER
        r = await pg.evaluate("""(PICK)=>{ const pick=eval(PICK); startGame(); G.inv=99; G.stage=56; clearSets(); spawnSet(); Loot.startFever(); updateHUD();
            HudC.holdTo=0; HudC.state(''); const pt=getComputedStyle(document.getElementById('ptext')); const x2=getComputedStyle(document.getElementById('uX2'));
            const neon={col:pt.color, ts:pt.textShadow.slice(0,60), x2:x2.display};
            pick(true); const g=document.getElementById('uGain').textContent; Loot.endFever(); updateHUD();
            return {neon, g, x2off:getComputedStyle(document.getElementById('uX2')).display}; }""", PICK)
        print("FEVER", r)
        ok("rgb(255, 250, 240)" == r["neon"]["col"] and "255, 208, 96" in r["neon"]["ts"], f"FEVER 문제 글자 형광 {r['neon']}")
        ok(r["neon"]["x2"] == "block" and r["x2off"] == "none", "점수 밑 ×2 — FEVER 동안만")
        ok("×2" in r["g"], f"FEVER 정답은 「+N ×2」 {r['g']}")

        # ⑦ COMBO
        r = await pg.evaluate("""()=>{ const out={}; for(const n of [0,1,6,10,20,30]){ G.combo=n; updateHUD(); const el=document.getElementById('comboTag'), cs=getComputedStyle(el);
              out[n]={t:el.textContent, op:cs.opacity, col:cs.color, cls:el.className, vis:cs.display}; } return out; }""")
        print("COMBO", json.dumps(r, ensure_ascii=False))
        ok(r["0"]["t"] == "0 COMBO" and float(r["0"]["op"]) < 0.5 and r["0"]["vis"] != "none", "0 COMBO 는 흐리게 자리 지킴")
        ok(r["6"]["t"] == "6 COMBO" and r["6"]["op"] == "1" and r["6"]["col"] == "rgb(255, 255, 255)", "6 COMBO 흰색")
        ok(r["10"]["col"] == "rgb(255, 216, 74)" and r["20"]["col"] == "rgb(111, 211, 255)" and r["30"]["col"] == "rgb(199, 155, 255)", "10 금 · 20 하늘 · 30 보라")

        # ⑧ 지대 이름
        r = await pg.evaluate("()=>{ zoneBanner(ZONES[1]); return document.getElementById('zoneTag').innerHTML; }")
        print("지대", r)
        ok("RUINS" not in r and "사막 유적" in r and "<em>" in r, f"영어 부제 대신 한글 안내 {r}")

        await br.close()
    e = real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad))
    sys.exit(1 if bad else 0)

asyncio.run(main())
