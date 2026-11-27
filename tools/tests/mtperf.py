"""(v741) 🏝 My Town 성능 재기 — 사용자: 「마이타운 자체 최적화를 좀 고민해 보자」
   통과/실패 시험이 아니라 숫자를 남기는 도구 (perf738 처럼). 옛 아이패드(사파리 15 · 코어 4)로 속이고 CPU 를 HY_CPU 배(기본 4) 느리게:
   ① 켜기: 첫 프레임까지 시간 · 스크립트 실행/구문 시간 · 긴 작업 · 받은 파일(종류별 KB) · JS 메모리
   ② 섬: 그리기 수(화면·그림자) · 삼각형 · 도형/그림 수 · 그림 메모리(MB) · 장면 묶음별 조각·삼각형·버퍼 MB (안 보이는 묶음 포함)
   ③ 한 프레임 JS 시간 나눠 보기 (섬 tick · 마을 · 주민 · 가림 · 이름표 · 그리기 …) — 여러 자리로 옮겨 다니며
   ④ CPU 표본(Profiler) 상위 함수
   결과: out/mtperf_<GAME_VER>_<기기>.json · 「python3 mtperf.py [old|pad]」 · 비교 「python3 mtperf.py --cmp A.json B.json」"""
import asyncio, sys, os, json, time
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
RATE = float(os.environ.get("HY_CPU", "4"))
OLDUA = "Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1"
INIT = """(()=>{ window.__lt=[]; try{ new PerformanceObserver(l=>{ l.getEntries().forEach(e=>__lt.push([Math.round(e.startTime), Math.round(e.duration)])); }).observe({type:'longtask', buffered:true}); }catch(e){}
  window.__t0=performance.now(); })();"""
RES = """()=>{ const o={}; performance.getEntriesByType('resource').forEach(r=>{ const m=/\\.([a-z0-9]+)(\\?|#|$)/i.exec(r.name.split('/').pop()); const k=m?m[1].toLowerCase():'?'; o[k]=o[k]||[0,0]; o[k][0]++; o[k][1]+=(r.encodedBodySize||r.transferSize||0); });
  Object.keys(o).forEach(k=>o[k][1]=Math.round(o[k][1]/1e3)); return o; }"""
# 장면 묶음별 — 조각 수 · 삼각형 · 버퍼(MB) · 보임
SCENE = """()=>{ const out=[], seenG=new Set(); const tri=g=>(g.index?g.index.count:(g.attributes.position?g.attributes.position.count:0))/3;
  const buf=g=>{ if(seenG.has(g)) return 0; seenG.add(g); let b=g.index&&g.index.array?g.index.array.byteLength:0; for(const k in g.attributes){ const a=g.attributes[k]; if(a.array) b+=a.array.byteLength; else if(a.data&&a.data.array) b+=a.data.array.byteLength; } return b; };
  const walk=(root, name)=>{ let n=0, t=0, b=0, inst=0, vis=root.visible; root.traverse(m=>{ if(m.isMesh||m.isPoints||m.isLine){ n++; const k=m.isInstancedMesh?m.count:1; inst+=m.isInstancedMesh?1:0; t+=tri(m.geometry)*k; b+=buf(m.geometry); } }); return {name, vis, n, inst, tri:Math.round(t), MB:+(b/1e6).toFixed(2)}; };
  scene.children.forEach((c,i)=>{ if(c.isLight || c.isCamera) return; const r=walk(c, c.name || (c.type+'#'+i)); if(r.n) out.push(r); });
  if(window.ISLE && ISLE.G){ ISLE.G.children.forEach((c,i)=>{ const r=walk(c, 'isle/'+(c.name || (c.isInstancedMesh?'inst':c.type)+'#'+i)); if(r.n && (r.tri>3000 || r.MB>0.3 || r.n>40)) out.push(r); }); }
  out.sort((a,b)=>b.MB-a.MB); return out.slice(0,40); }"""
TEX = """()=>{ const T=new Map(); scene.traverse(m=>{ const ms=m.material ? (Array.isArray(m.material)?m.material:[m.material]) : []; ms.forEach(mt=>{ for(const k of ['map','normalMap','emissiveMap','alphaMap','aoMap','roughnessMap','gradientMap']){ const t=mt[k]; if(t && t.image) T.set(t.uuid, t); } }); });
  if(scene.background && scene.background.isTexture) T.set(scene.background.uuid, scene.background);
  let mb=0; const L=[]; T.forEach(t=>{ const i=t.image, w=i.width||i.videoWidth||0, h=i.height||i.videoHeight||0, m=w*h*4*(t.generateMipmaps!==false?1.33:1)/1e6; mb+=m; L.push([+m.toFixed(1), w+'x'+h, (t.name||(i.currentSrc||i.src||'').split('/').pop()||'canvas').slice(0,40)]); });
  L.sort((a,b)=>b[0]-a[0]); return {n:T.size, MB:+mb.toFixed(1), top:L.slice(0,10), info:renderer.info.memory, programs:(renderer.info.programs||[]).length}; }"""
DRAWS = """()=>new Promise(res=>{ const R=renderer, o=R.renderBufferDirect; let m=0, s=0, t=0, n=0;
  R.renderBufferDirect=function(cam, sc, geo, mat, obj, grp){ const sh=mat && (mat.isMeshDepthMaterial||mat.isMeshDistanceMaterial); if(sh) s++; else { m++; const c=geo.index?geo.index.count:(geo.attributes.position?geo.attributes.position.count:0); t+=(grp?grp.count:c)/3*(obj.isInstancedMesh?obj.count:1); } return o.apply(this, arguments); };
  const f=()=>{ dirty=true; if(++n<4) return requestAnimationFrame(f); R.renderBufferDirect=o; res({main:m/4, shadow:s/4, tri:Math.round(t/4)}); }; requestAnimationFrame(f); })"""
# 한 프레임 JS 시간 — 전역 함수·객체 함수를 감싸서 잼 (감싼 것은 끝나면 되돌림)
WRAP = """()=>{ const W=window.__W={t:{}, n:0, frame:[], keep:[]};
  const wrapG=(name)=>{ const f=window[name]; if(typeof f!=='function') return; window[name]=function(){ const a=performance.now(); try{ return f.apply(this, arguments); } finally{ W.t[name]=(W.t[name]||0)+performance.now()-a; } }; W.keep.push(()=>{ window[name]=f; }); };
  const wrapO=(o, k, name)=>{ if(!o || typeof o[k]!=='function') return; const f=o[k]; o[k]=function(){ const a=performance.now(); try{ return f.apply(this, arguments); } finally{ W.t[name]=(W.t[name]||0)+performance.now()-a; } }; W.keep.push(()=>{ o[k]=f; }); };
  ['updateHero','updDoors','updateFish','updWobble','updateNpcs','updEmotes','updOcclude','roomTick','yTick','yRide','updCam','vlTick','updLabels','updHud','updUI','envApply'].forEach(wrapG);
  wrapO(window.ISLE,'tick','ISLE.tick'); wrapO(window.VIL,'tick','VIL.tick'); wrapO(window.DAYR,'tick','DAYR.tick'); wrapO(window.GUEST,'tick','GUEST.tick'); wrapO(window.TFAC,'tick','TFAC.tick');
  wrapO(window.TOON,'draw','TOON.draw(그리기)'); wrapO(renderer,'render','renderer.render');
  const lb=window.loopBody; window.loopBody=function(now){ const a=performance.now(); try{ return lb.apply(this, arguments); } finally{ const d=performance.now()-a; W.n++; W.frame.push(d); } }; W.keep.push(()=>{ window.loopBody=lb; });
  const raf=[]; let last=0; W.gaps=raf; const tk=t=>{ if(!W.stop){ if(last) raf.push(t-last); last=t; requestAnimationFrame(tk); } }; requestAnimationFrame(tk);
  return true; }"""
UNWRAP = """()=>{ const W=window.__W; W.stop=1; W.keep.forEach(f=>f()); const F=W.frame.slice().sort((a,b)=>a-b), G=W.gaps.slice().sort((a,b)=>a-b), q=(A,p)=>A.length?+A[Math.min(A.length-1, Math.floor(A.length*p))].toFixed(1):null;
  const per={}; Object.keys(W.t).forEach(k=>per[k]=+(W.t[k]/Math.max(1,W.n)).toFixed(2)); return {frames:W.n, msAvg:+(F.reduce((s,x)=>s+x,0)/Math.max(1,F.length)).toFixed(2), msP50:q(F,.5), msP95:q(F,.95), fps:G.length?+(1000/(G.reduce((s,x)=>s+x,0)/G.length)).toFixed(1):null, gapP95:q(G,.95), per}; }"""
SPOTS = """()=>{ const S=[]; try{ const c=ISLE.plazaCell ? ISLE.plazaCell() : null; if(c) S.push(['광장', c[0]+.5, c[1]+.5]); }catch(e){}
  try{ (ISLE.lots||[]).slice(0,60).filter((L,i)=>i%15===0).forEach((L,i)=>{ const d=ISLE.doorOf ? ISLE.doorOf(L) : null; if(d) S.push(['집 '+i, d[0]+.5, d[1]+1.5]); }); }catch(e){}
  try{ if(window.VIL && VIL.C) S.push(['버섯 마을', VIL.C[0], VIL.C[1]]); }catch(e){}
  return S; }"""
async def main():
    if "--cmp" in sys.argv:
        a, b = [json.load(open(x)) for x in sys.argv[sys.argv.index("--cmp")+1:][:2]]
        for k in ("boot", "isle"):
            for m in b.get(k, {}):
                if isinstance(b[k][m], (int, float)): print("%-6s %-14s %s → %s" % (k, m, a.get(k, {}).get(m), b[k][m]))
        for i, s in enumerate(b.get("frames", [])):
            sa = (a.get("frames") or [{}]*99)[i] if i < len(a.get("frames", [])) else {}
            print("frame  %-10s ms %s → %s · fps %s → %s" % (s.get("at"), sa.get("msAvg"), s.get("msAvg"), sa.get("fps"), s.get("fps")))
        return
    want = [x for x in sys.argv[1:] if x in ("old", "pad")] or ["old"]
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--enable-precise-memory-info"])
        for dev in want:
            old = dev == "old"
            ctx = await br.new_context(viewport={"width": 768, "height": 1024} if old else {"width": 820, "height": 1180}, device_scale_factor=2, is_mobile=old, has_touch=True,
                                       service_workers="block", **({"user_agent": OLDUA} if old else {}))
            await ctx.add_init_script("Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>%d}); %s" % (4 if old else 8, INIT))
            pg = await ctx.new_page(); pg.set_default_timeout(240000); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            await pg.route("**/*", fake)
            q = "?isle=1" + ("" if old else "&perf=0")
            await pg.goto(ORIGIN + "proto/house.html" + q); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify('MT741')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_v5','1'); }")
            cdp = await ctx.new_cdp_session(pg); await cdp.send("Performance.enable")
            if RATE > 1: await cdp.send("Emulation.setCPUThrottlingRate", {"rate": RATE})
            t0 = time.time(); await pg.reload(wait_until="load"); tLoad = time.time() - t0
            # 첫 프레임 = fps 글자가 바뀜 / HOUSE 생김
            for _ in range(400):
                if await pg.evaluate("()=>!!(window.HOUSE && window.ISLE && renderer && renderer.info.render.frame>2)"): break
                await pg.wait_for_timeout(100)
            tFirst = time.time() - t0
            await pg.wait_for_timeout(3000)
            met = {m["name"]: m["value"] for m in (await cdp.send("Performance.getMetrics"))["metrics"]}
            boot = {"loadS": round(tLoad, 2), "firstFrameS": round(tFirst, 2), "scriptS": round(met.get("ScriptDuration", 0), 2), "taskS": round(met.get("TaskDuration", 0), 2),
                    "layoutS": round(met.get("LayoutDuration", 0) + met.get("RecalcStyleDuration", 0), 2), "heapMB": round(met.get("JSHeapUsedSize", 0) / 1e6, 1), "nodes": int(met.get("Nodes", 0))}
            lt = await pg.evaluate("()=>window.__lt||[]"); boot["longN"] = len(lt); boot["longMs"] = sum(x[1] for x in lt); boot["longTop"] = sorted(lt, key=lambda x: -x[1])[:6]
            boot["res"] = await pg.evaluate(RES)
            boot["place"] = await pg.evaluate("()=>HOUSE.place()"); boot["lv"] = await pg.evaluate("()=>[GUARD.lv, renderer.getPixelRatio(), sun.castShadow]")
            print("── %s 켜기" % dev, json.dumps(boot, ensure_ascii=False), flush=True)
            # ② 섬으로
            if boot["place"] != "isle":
                await pg.evaluate("()=>ISLE.enter()")
                for _ in range(300):
                    try:
                        if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
                    except Exception: pass
                    await pg.wait_for_timeout(250)
            await pg.wait_for_timeout(4000)
            met = {m["name"]: m["value"] for m in (await cdp.send("Performance.getMetrics"))["metrics"]}
            isle = {"heapMB": round(met.get("JSHeapUsedSize", 0) / 1e6, 1), "nodes": int(met.get("Nodes", 0)), "dom": await pg.evaluate("()=>document.getElementsByTagName('*').length"),
                    "labels": await pg.evaluate("()=>{ try{ const L=HOUSE.LBL(); return Array.isArray(L)?L.length:Object.keys(L||{}).length; }catch(e){ return -1; } }"),
                    "trees": await pg.evaluate("()=>ISLE.trees().length"), "lv": await pg.evaluate("()=>[GUARD.lv, renderer.getPixelRatio(), sun.castShadow]")}
            isle.update(await pg.evaluate(DRAWS)); tex = await pg.evaluate(TEX); isle["texN"] = tex["n"]; isle["texMB"] = tex["MB"]; isle["geoN"] = tex["info"]["geometries"]; isle["glTex"] = tex["info"]["textures"]; isle["programs"] = tex["programs"]
            sc = await pg.evaluate(SCENE)
            print("── %s 섬" % dev, json.dumps(isle, ensure_ascii=False), flush=True)
            print("   그림:", tex["top"], flush=True)
            print("   묶음(버퍼 MB 순):", flush=True)
            for r in sc[:26]: print("     %-32s %s 조각 %5d (inst %3d) 삼각형 %8d  %.2fMB" % (r["name"][:32], "보임" if r["vis"] else "숨김", r["n"], r["inst"], r["tri"], r["MB"]), flush=True)
            await pg.screenshot(path=OUT + "mtperf_%s.png" % dev)
            # ③ 자리마다 프레임 시간
            spots = await pg.evaluate(SPOTS); frames = []
            for nm, x, z in [["처음 자리", None, None]] + spots[:5]:
                if x is not None:
                    await pg.evaluate("([x,z])=>{ const h=HOUSE.hero(); h.g.position.x=x; h.g.position.z=z; try{ h.path=[]; }catch(e){} dirty=true; }", [x, z])
                    await pg.wait_for_timeout(1500)
                await pg.evaluate(WRAP); await pg.wait_for_timeout(3000); r = await pg.evaluate(UNWRAP); r["at"] = nm
                d = await pg.evaluate(DRAWS); r["draws"] = d["main"] + d["shadow"]; r["tri"] = d["tri"]
                frames.append(r)
                top = sorted(r["per"].items(), key=lambda kv: -kv[1])[:8]
                print("── %s 프레임 @%s: JS %sms (p95 %s) · %s fps · 그리기 %s · 삼각형 %s · %s" % (dev, nm, r["msAvg"], r["msP95"], r["fps"], r["draws"], r["tri"], " ".join("%s=%s" % kv for kv in top)), flush=True)
            # ④ CPU 표본
            await cdp.send("Profiler.enable"); await cdp.send("Profiler.setSamplingInterval", {"interval": 500}); await cdp.send("Profiler.start")
            await pg.wait_for_timeout(5000)
            prof = (await cdp.send("Profiler.stop"))["profile"]
            nodes = {n["id"]: n for n in prof["nodes"]}; cnt = {}
            for s in prof["samples"]: cnt[s] = cnt.get(s, 0) + 1
            agg = {}; tot = len(prof["samples"])
            for nid, c in cnt.items():
                cf = nodes[nid]["callFrame"]; k = "%s %s:%d" % (cf["functionName"] or "(anon)", cf["url"].split("/")[-1][:18], cf["lineNumber"] + 1)
                agg[k] = agg.get(k, 0) + c
            topf = sorted(agg.items(), key=lambda kv: -kv[1])[:22]
            print("── %s CPU 표본 상위 (%d 표본):" % (dev, tot), flush=True)
            for k, c in topf: print("     %5.1f%%  %s" % (100 * c / tot, k), flush=True)
            if RATE > 1: await cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
            ver = await pg.evaluate("()=>{ try{ return (window.GAME_VER||'') || ''; }catch(e){ return ''; } }") or os.popen("git -C %s rev-parse --short HEAD" % SITE).read().strip()
            json.dump({"ver": ver, "dev": dev, "boot": boot, "isle": isle, "scene": sc, "tex": tex, "frames": frames, "cpu": topf, "errs": real_errs(errs)[:5]},
                      open(OUT + "mtperf_%s_%s.json" % (ver, dev), "w"), ensure_ascii=False, indent=1)
            print("   오류:", real_errs(errs)[:3], "→ out/mtperf_%s_%s.json" % (ver, dev), flush=True)
            await ctx.close()
        await br.close()
asyncio.run(main())
