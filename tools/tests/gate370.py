"""(v370) 아이폰 측정 보고서(v369)로 고친 것 + 사용자: 첫 번째 문 단어가 가려짐
  ① 바깥 문 단어판이 카메라 쪽으로 돌아도 판 전체가 문틀 그림(z -0.12)보다 앞 (가려지지 않음)
  ② 문 단어판·빛·문틀 모양은 같이 씀 (문마다 새 모양을 GPU 에 올리지 않음 · 문 치워도 안 지움)
  ③ 다음 지대 그림은 두세 단계 전부터 쉬는 틈에 미리 올림
  ④ 화면 갱신 시각으로 dt · 튀는 한 프레임은 몇 프레임에 나눔 (전체 시간은 같음)
  ⑤ 📊 측정기: 판정·문 생성·지대 바꿈 등 걸린 시간(ms)도 적음"""
import asyncio, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ G.set='elem'; G.diff='hard'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(1500)
        # ① 단어판이 문틀 앞에
        r = await pg.evaluate("""()=>{ const s=G.sets.find(s=>!s.judged); if(!s) return null; camera.position.x=0; updateGates(0.016);
            return s.gates.map(g=>{ const th=g.sign.rotation.y; return {n:s.gates.length, th:+th.toFixed(3), z:+g.sign.position.z.toFixed(3), back:+(g.sign.position.z-(g.sw/2)*Math.abs(Math.sin(th))).toFixed(3), hz:+g.halo.position.z.toFixed(3)}; }); }""")
        print("signs", r)
        ok(r and all(x["back"] >= -0.07 for x in r) and any(x["z"] > 0 for x in r), f"돌아간 단어판의 안쪽 끝도 문틀(-0.12)보다 앞 {r}")
        # ② 모양 같이 쓰기
        r = await pg.evaluate("""()=>{ const d0=THREE.__geoDisposed||0; const s1=G.sets[0]; const a=s1.gates.map(g=>g.sign.geometry);
            clearSets(); spawnSet(); const s2=G.sets[0]; const b=s2.gates.map(g=>g.sign.geometry);
            return {same:a[0]===b[0] && b.every(x=>x===b[0]), halo:s2.gates[0].halo.geometry===s2.gates[1].halo.geometry, shared:!!(b[0].userData&&b[0].userData.shared)}; }""")
        ok(r["same"] and r["halo"] and r["shared"], f"단어판·빛 모양은 문끼리 같이 씀 · 문을 치워도 그대로 {r}")
        # ③ 다음 지대 그림 미리
        r = await pg.evaluate("""()=>new Promise(res=>{ const zi=ZONES.findIndex(z=>zoneArt(z)==='desert'); const keep=Object.assign({}, TrapArt.tex);
            TrapArt.tex['gate-desert']={image:{width:8}}; TrapArt.tex['floor-desert']={image:{width:8}}; TrapArt.tex['gate-ice']={image:{width:8}}; TrapArt.tex['props-desert']={};
            const got=[]; const f=renderer.initTexture; renderer.initTexture=t=>got.push(t); GLWarm._zd={}; G.running=true; GLWarm.zone(zi); GLWarm.zone(zi);
            setTimeout(()=>{ renderer.initTexture=f; const names=got.map(t=>Object.keys(TrapArt.tex).find(k=>TrapArt.tex[k]===t)).filter(Boolean); TrapArt.tex=keep; res({zi, names}); }, 700); })""")
        ok(r["zi"] >= 0 and "gate-desert" in r["names"] and "floor-desert" in r["names"] and all(n.endswith("-desert") for n in r["names"]) and len(set(r["names"])) == len(r["names"]), f"다음 지대(사막) 그림만 한 장씩 미리 · 한 번만 {r}")
        r = await pg.evaluate("""()=>{ const zi=ZONES.findIndex(z=>zoneArt(z)==='desert'); const st=[...Array(200).keys()].find(n=>zoneIndex(n)===zi); const c=[]; const z0=GLWarm.zone; GLWarm.zone=x=>c.push(x);
            G.stage=st-2; G.zone=zoneIndex(G.stage); const s=G.sets.find(s=>!s.judged); G.lane=s.q.answer; P.x=laneX(s.q.answer, G.lanes); try{ judge(s); }catch(e){ GLWarm.zone=z0; return 'err '+e; } GLWarm.zone=z0; return [c, zi, G.stage]; }""")
        ok(isinstance(r, list) and r[1] in r[0], f"지대 바뀌기 전에 미리 부름 {r}")
        # ④ dt
        r = await pg.evaluate("""()=>{ renderer.setAnimationLoop(null); G.running=true; G.paused=false; G._dtS=0; G._ftP=0;
            const T=[1000]; for(let i=1;i<30;i++) T.push(T[i-1]+(i===10?33.4:16.7)); const out=[];
            T.forEach(t=>{ G._ft=t; G.hitStop=0; loopBody(); out.push(G.rawDt); }); renderer.setAnimationLoop(loop);
            return {spike:out[10], before:out[9], sum:out.slice(1).reduce((a,b)=>a+b,0), want:(T[T.length-1]-T[0])/1000}; }""")
        print("dt", r)
        ok(abs(r["before"] - 0.0167) < 0.001 and r["spike"] < 0.025 and abs(r["sum"] - r["want"]) < 0.01, f"튀는 프레임을 나눔 · 전체 시간 같음 {r}")
        # ⑤ 측정기 시간
        await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(800)
        r = await pg.evaluate("()=>{ spawnSet(); const c=Object.assign({}, Perf.cur); return [Object.keys(c).filter(k=>k[0]==='⏱'), Perf.tagTxt('⏱문 생성', 12.4), Perf.tagTxt('먼지', 2)]; }")
        ok("⏱문 생성" in r[0] and "⏱문 만들기" in r[0] and r[1] == "문 생성 12ms" and r[2] == "먼지×2", f"걸린 시간 적기 {r}")
        await pg.evaluate("()=>localStorage.removeItem('hyeng_perf')")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
