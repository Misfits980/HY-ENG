"""(v738) ⏱ 성능 재기 — 사용자: 「이제 게임 자체 최적화 및 오류 고치는 거에 집중」 · 「점검 도구들도 … 새로 만들거나」
   옛 아이패드처럼 CPU 를 4배 느리게(CDP) 해 놓고 화면마다 잰다 (통과/실패 시험이 아니라 숫자를 남기는 도구):
   · 첫 화면까지 걸린 시간 · 그동안 메인 스레드를 오래 잡은 작업(50ms 넘는 것) 합
   · JS 메모리 · DOM 수 · 돌고 있는 CSS 애니메이션 수(안 보이는 화면 것까지) · 켜져 있는 setInterval 수 · 불러온 그림 수·크기
   화면: 첫 화면 → Daily 30 → 관리 수업 탭 → 교실 배틀 TV(아이 9명) → 레이드 TV(아이 9명)
   결과: out/perf_<GAME_VER>.json · 「python3 perf738.py」 · 두 버전 비교 = 「python3 perf738.py --cmp out/perf_v737.json out/perf_v738.json」"""
import asyncio, sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
RATE = float(os.environ.get("HY_CPU", "4"))
INIT = """(()=>{ window.__lt=[]; try{ new PerformanceObserver(l=>{ l.getEntries().forEach(e=>__lt.push(e.duration)); }).observe({type:'longtask', buffered:true}); }catch(e){}
  const si=window.setInterval, ci=window.clearInterval; window.__iv=new Set();
  window.setInterval=function(f,t,...a){ const id=si.call(window,f,t,...a); __iv.add(id); return id; }; window.clearInterval=function(id){ __iv.delete(id); return ci.call(window,id); }; })();"""
SNAP = """()=>{ const A=document.getAnimations(), vis=A.filter(a=>{ const t=a.effect && a.effect.target; if(!t || !t.isConnected) return false; const r=t.getBoundingClientRect(); return r.width>0 && r.height>0 && getComputedStyle(t).visibility!=='hidden'; });
  const img=performance.getEntriesByType('resource').filter(r=>/\\.(webp|png|jpg|jpeg|gif)(\\?|$)/.test(r.name));
  const lt=(window.__lt||[]); return {heapMB: performance.memory ? +(performance.memory.usedJSHeapSize/1e6).toFixed(1) : null, dom:document.getElementsByTagName('*').length,
    anim:A.filter(a=>a.playState==='running').length, animHidden:A.filter(a=>a.playState==='running').length-vis.filter(a=>a.playState==='running').length, iv:(window.__iv||new Set()).size,
    img:img.length, imgKB:Math.round(img.reduce((s,r)=>s+(r.transferSize||r.encodedBodySize||0),0)/1e3), longN:lt.length, longMs:Math.round(lt.reduce((s,x)=>s+x,0))}; }"""
async def main():
    if "--cmp" in sys.argv:
        a, b = [json.load(open(x)) for x in sys.argv[sys.argv.index("--cmp")+1:][:2]]
        for k in b:
            if k == "ver": continue
            print("%-10s" % k, "  ".join("%s %s→%s" % (m, a.get(k, {}).get(m), b[k].get(m)) for m in b[k]))
        return
    out = {}
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 1024, "height": 768}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true;" + INIT)
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        cdp = await ctx.new_cdp_session(pg); await cdp.send("Emulation.setCPUThrottlingRate", {"rate": RATE})
        await pg.route("**/*", route)
        t0 = time.time(); await pg.goto(ORIGIN + "index.html")
        await pg.wait_for_function("()=>document.getElementById('scStart') && document.getElementById('scStart').classList.contains('on')", timeout=120000)
        ready = time.time() - t0; await pg.wait_for_timeout(3000)
        ver = await pg.evaluate("()=>typeof GAME_VER!=='undefined' ? GAME_VER : '?'")
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        s = await pg.evaluate(SNAP); s["readyS"] = round(ready, 2); out["start"] = s
        await pg.evaluate("()=>{ window.__lt=[]; }")
        await pg.evaluate("()=>{ try{ Voice.speak=()=>{}; }catch(e){} StudyUI.open(); }"); await pg.wait_for_timeout(2500); out["daily30"] = await pg.evaluate(SNAP)
        await pg.evaluate("()=>{ window.__lt=[]; StudyUI.close && StudyUI.close(); show('scStart'); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }")
        await pg.evaluate("()=>{ Admin.open(); Admin._tab('now'); }"); await pg.wait_for_timeout(2500); out["admin"] = await pg.evaluate(SNAP)
        KN = ["토토","별사탕","콩콩","젤리","마루","쿠키","포포","방울","몽글"]; CH = ["hero","explorer","archer","mage","knight","scholar","ghost","cat","wolf"]
        await pg.evaluate("()=>{ window.__lt=[]; document.getElementById('shAdmin').classList.remove('on'); }")
        room = await pg.evaluate("()=>Battle.host({set:'g56', from:20, to:23, words:[], dur:300, team:false, mode:'score', qt:['mean'], lbl:'G5-6', cls:'all'})"); await pg.wait_for_timeout(800)
        await pg.evaluate("([r,K,C])=>K.forEach((n,i)=>FB.update('/battle/'+r+'/p/k'+i, {n, c:C[i], at:Date.now()}))", [room, KN, CH]); await pg.wait_for_timeout(2500)
        out["battleTV"] = await pg.evaluate(SNAP)
        await pg.evaluate("()=>{ Battle.hostAct('start'); }"); await pg.wait_for_timeout(6000); out["battleRun"] = await pg.evaluate(SNAP)
        await pg.evaluate("()=>{ try{ Battle.leave(); }catch(e){} window.__lt=[]; }"); await pg.wait_for_timeout(800)
        room = await pg.evaluate("()=>{ Raid.MIN=1000; return Raid.host('g56', [], 0, null, 900, 'all'); }"); await pg.wait_for_timeout(800)
        await pg.evaluate("([r,K,C])=>K.forEach((n,i)=>FB.update('/raids/'+r+'/p/k'+i, {n, c:C[i], e:'🙂', d:0, b:0, sh:0, h:0, m:0, t:'all', at:Raid.now()}))", [room, KN, CH]); await pg.wait_for_timeout(2500)
        out["raidTV"] = await pg.evaluate(SNAP)
        await br.close()
    out["ver"] = ver
    print("버전 %s · CPU ×%g 느리게" % (ver, RATE))
    for k, v in out.items():
        if k != "ver": print("%-10s %s" % (k, "  ".join("%s=%s" % x for x in v.items())))
    e = real_errs(errs); print("오류", e[:3])
    json.dump(out, open(OUT + "perf_%s.json" % ver, "w"), ensure_ascii=False, indent=1)
asyncio.run(main())
