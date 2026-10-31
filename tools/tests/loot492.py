"""(v492) 달리기 손맛 — ⭐ 별 줄 · ❓ 상자 · 🔥 FEVER · 💗 연속 정답 회복 · ⚡ RUSH 보이기 · 콤보 글자 단계
   ① 봇이 40문제를 달리며 별을 줍고 정답을 고름 → 별·FEVER 가 실제로 생기고 오류 없음 · 별이 함정 자리에 놓이지 않음
   ② 별 줄은 정답 줄과 상관없음 (힌트가 아님) — 400번 만들어 같은 줄일 확률이 1/줄 수 근처
   ③ 연속 정답 10개 → 하트 +1 (쉬움은 없음) · 콤보 글자에 「💗 n」
   ④ 콤보 글자 — 5·10·15 단계 클래스 · 글자색이 배경과 다름 (예전 버그: 노란 배경에 노란 글자)
   ⑤ 🛡️ 방패가 넘어짐 한 번을 막음 · 🐢 천천히가 문을 느리게 · 🔥 FEVER 정답 점수 2배
   ⑥ 2인용·레이스·보스전은 별·상자 없음 · 판이 끝나면 FEVER·속도선이 꺼짐"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

DRIVE = """()=>{ renderer.setAnimationLoop(null); G._ft=performance.now(); G._ftP=0;
  window._bot=()=>{ const s=activeSet(); if(!s) return; const n=s.gates.length;
    const ans=laneOfX(s.gates[s.q.answer].root.position.x, n), dist=P.z-s.group.position.z; let t=ans;
    if(dist > G.spawnDist*0.45){ const st=Loot.S.list.filter(it=>it.z<P.z+0.5 && it.z>P.z-8).sort((a,b)=>b.z-a.z)[0];
      if(st) t=clamp(Math.round(st.x/CFG.LANE_W+(G.lanes-1)/2),0,G.lanes-1); }
    P.x=laneX(t,G.lanes); P.vx=0; };
  window._run=(frames)=>{ for(let f=0;f<frames;f++){ G.inv=99; _bot(); G._ft+=16.7; G.hitStop=0; loopBody(); if(!G.running) break; } };
  window._bad=[]; const os=Loot.onSet.bind(Loot);
  Loot.onSet=(s)=>{ const b=Loot.S.list.length; os(s); Loot.S.list.slice(b).forEach(it=>{
      Hazards.list.forEach(h=>{ if(!h || h.type==='ice' || h.type==='puddle') return; const hz=h.tile?h.tile.logicZ:(h.z!=null?h.z:null); if(hz==null) return;
        const hx=h.cx!=null?h.cx:(h.lane!=null?laneX(h.lane,G.lanes):null); if(hx==null) return;
        if(Math.abs(hz-it.z)<(h.len||2)/2+1.2 && Math.abs(hx-it.x)<(h.halfW||CFG.LANE_W*.5)+.5) _bad.push([it.type,h.type]); }); }); };
  return true; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)

        # ① 봇 달리기
        await pg.evaluate("()=>{ G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; G.char='hero'; startGame(); }")
        await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ G.maxLives=99; G.lives=99; }")
        await pg.evaluate(DRIVE)
        r = None
        for k in range(40):
            await pg.evaluate("()=>_run(240)")
            r = await pg.evaluate("()=>({st:G.stage, sol:G.solved, right:G.right, run:G.running, stats:Loot.stats(), list:Loot.S.list.length, g:Loot.S.gauge, fever:Loot.S.fever, bad:_bad.length, badx:_bad.slice(0,3), fx:document.body.classList.contains('fever'), fb:!document.getElementById('feverBar').hidden})")
            if r["sol"] >= 40 or not r["run"]: break
        print("봇", r)
        ok(r["sol"] >= 25, f"봇이 여러 문제를 풀었음 {r['sol']}")
        ok(r["stats"]["stars"] >= 10, f"별을 주움 {r['stats']}")
        ok(r["stats"]["fevers"] >= 1, f"FEVER 가 한 번 이상 {r['stats']}")
        ok(r["bad"] == 0, f"별·상자가 함정 자리에 없음 {r['badx']}")
        ok(r["fb"], "🔥 게이지 막대가 보임")
        ok(r["stats"]["boxes"] == 0, f"❓ 상자는 아직 꺼져 있음 (사용자: 아이템은 아직 끄자) {r['stats']}")

        # ② 별 줄 ↔ 정답 줄 독립
        r = await pg.evaluate("""()=>{ let same=0, tot=0, n=0; const keep=G.stage;
          for(let i=0;i<400;i++){ clearSets(); Hazards.clear(); G.stage=5; spawnSet(); const s=activeSet(); n=s.gates.length;
            const st=Loot.S.list.find(it=>it.type==='star'); if(!st) continue; tot++;
            if(Math.abs(st.x - s.gates[s.q.answer].root.position.x) < 0.3) same++; }
          G.stage=keep; return {same, tot, n, rate: same/Math.max(1,tot)}; }""")
        print("별 줄 = 정답 줄", r)
        ok(r["tot"] > 300 and abs(r["rate"] - 1/r["n"]) < 0.09, f"별 줄은 정답과 상관없음 {r}")

        # ③ 연속 정답 회복
        r = await pg.evaluate("""()=>{ clearSets(); Loot.clearItems(); G.maxLives=3; G.lives=1; G.combo=9; G.falling=false; G.dead=false; spawnSet(); updateHUD();
          const tag=document.getElementById('comboTag').textContent;
          const s=activeSet(); const ans=laneOfX(s.gates[s.q.answer].root.position.x, s.gates.length); G.lane=ans; P.x=laneX(ans,G.lanes); judge(s);
          return {tag, lives:G.lives, combo:G.combo, heals:Loot.stats().heals}; }""")
        print("회복", r)
        ok("💗 1" in r["tag"], f"콤보 글자에 하트까지 남은 수 {r['tag']}")
        ok(r["lives"] == 2 and r["combo"] == 10, f"10연속 → 하트 +1 {r}")
        r = await pg.evaluate("""()=>{ G.diff='easy'; clearSets(); G.lives=1; G.combo=19; spawnSet(); const s=activeSet(); const ans=laneOfX(s.gates[s.q.answer].root.position.x, s.gates.length); G.lane=ans; P.x=laneX(ans,G.lanes); judge(s); const L=G.lives; G.diff='normal'; return L; }""")
        ok(r == 1, f"쉬움은 연속 회복 없음 (지대 회복 따로) {r}")

        # ④ 콤보 글자
        r = await pg.evaluate("""()=>{ const out={}; [3,5,10,15].forEach(c=>{ G.combo=c; G.lives=G.maxLives; updateHUD(); const el=document.getElementById('comboTag'), cs=getComputedStyle(el);
            out[c]={cls:el.className, col:cs.color, bg:cs.backgroundColor, bgi:cs.backgroundImage.slice(0,30), fs:cs.fontSize}; }); return out; }""")
        print("콤보 글자", json.dumps(r, ensure_ascii=False))
        ok("t5" in r["5"]["cls"] and "t10" in r["10"]["cls"] and "t15" in r["15"]["cls"], "콤보 단계 클래스")
        ok(r["5"]["col"] == "rgb(42, 27, 0)" and r["10"]["col"] == "rgb(42, 27, 0)", f"5·10연속 글자는 진한 색 {r['5']['col']} {r['10']['col']}")
        ok(r["5"]["fs"] == "13px", "글자 크기 13px")

        # ⑤ 방패 · 천천히 · FEVER 점수
        r = await pg.evaluate("""()=>{ G.lives=2; G.maxLives=3; Loot.S.shield=1; updateHUD(); const sh=document.getElementById('uLives').innerHTML.indexOf('🛡')>=0;
          G.dead=false; G.falling=true; onDead(); const L=G.lives; return {sh, L, left:Loot.S.shield}; }""")
        await pg.wait_for_timeout(500)
        print("방패", r)
        ok(r["sh"] and r["L"] == 2 and r["left"] == 0, f"방패가 하트를 지킴 {r}")
        r = await pg.evaluate("""()=>{ G.dead=false; G.falling=false; clearSets(); Loot.S.slow=1; spawnSet(); const s=activeSet(); return {slow:Loot.S.slow, time:s.time, base:approachTime(G.stage)}; }""")
        print("천천히", r)
        ok(r["slow"] == 0 and r["time"] > r["base"] * 1.12, f"🐢 다음 문이 느리게 {r}")
        r = await pg.evaluate("""()=>{ Loot.endFever(); Loot.S.gauge=0; clearSets(); G.combo=0; spawnSet(); let s=activeSet(); let ans=laneOfX(s.gates[s.q.answer].root.position.x, s.gates.length); G.lane=ans; P.x=laneX(ans,G.lanes); P.z=0;
            let a=G.score; judge(s); const g1=G.score-a;
            clearSets(); G.combo=0; Loot.S.fever=5; spawnSet(); s=activeSet(); ans=laneOfX(s.gates[s.q.answer].root.position.x, s.gates.length); G.lane=ans; P.x=laneX(ans,G.lanes); P.z=0;
            a=G.score; judge(s); const g2=G.score-a; Loot.endFever(); return {g1,g2}; }""")
        print("FEVER 점수", r)
        ok(r["g2"] == r["g1"] * 2, f"FEVER 정답 점수 2배 {r}")

        # ⑥ 레이스·보스전 없음 · 끝나면 꺼짐
        r = await pg.evaluate("""()=>{ clearSets(); Loot.clearItems(); G.race=true; spawnSet(); const a=Loot.S.list.length; G.race=false;
          clearSets(); Loot.clearItems(); Boss.active=true; spawnSet(); const b=Loot.S.list.length; Boss.active=false;
          Loot.startFever(); const f1=document.body.classList.contains('fever'); Loot.endRun();
          return {race:a, boss:b, f1, f2:document.body.classList.contains('fever'), rush:document.getElementById('rushFx').style.opacity}; }""")
        print("끝", r)
        ok(r["race"] == 0 and r["boss"] == 0, f"레이스·보스전 별·상자 없음 {r}")
        ok(r["f1"] and not r["f2"] and r["rush"] in ("0", ""), f"판이 끝나면 FEVER·속도선 꺼짐 {r}")

        # ⑤-2 상자: 보통 1장은 하트·방패 없음 (회복 없음 규칙) · 쉬움은 나옴
        r = await pg.evaluate("""()=>{ const cnt=(diff,stage)=>{ G.diff=diff; G.stage=stage; G.zone=zoneIndex(stage); let hs=0;
            for(let i=0;i<60;i++){ G.maxLives=3; G.lives=1; Loot.S.shield=0; Loot.S.magnet=0; Loot.S.fever=0; const L0=G.lives; Loot.pick({type:'box', x:0, z:0}); if(G.lives>L0 || Loot.S.shield) hs++; }
            return hs; };
          const a=cnt('normal',20), b=cnt('easy',20), c=cnt('normal',60); G.diff='normal'; G.stage=5; G.zone=zoneIndex(5); Loot.endFever(); return {normal1:a, easy:b, normal2:c}; }""")
        print("상자", r)
        ok(r["normal1"] == 0 and r["easy"] > 10 and r["normal2"] > 10, f"상자 하트·방패는 쉬움·2장부터 {r}")

        # ⑦ 결과 화면 한 줄
        r = await pg.evaluate("""()=>{ Online.on=()=>false; G.running=true; G.rule='normal'; G.versus=false; Loot.S.stars=12; Loot.S.fevers=1; Loot.S.heals=2; Loot.S.boxes=0;
          G.testRun=false; G.practice=false; G.cleared=false; G.quit=true; G.running=false; G.skipOutro=true; G.overFade=false; G._overDone=false; gameOver(); G.skipOutro=false;
          const el=document.getElementById('oLoot'); return {t:el.textContent, hid:el.hidden}; }""")
        await pg.wait_for_timeout(300)
        print("결과 줄", r)
        ok((not r["hid"]) and "별 12" in r["t"] and "FEVER 1번" in r["t"] and "회복 2번" in r["t"] and "상자" not in r["t"], f"결과 화면에 별·FEVER·회복 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
    sys.exit(1 if bad else 0)
asyncio.run(main())
