"""(v714) 🐢 옛 아이패드용 가벼운 섬 — 사용자: 「1번부터 해 보자」 (실제 기기 기록: 사파리 15 아이패드 섬 4~6fps · 가장 가볍게도 7~10fps · 마을 들어가자 튕김)
   ① 옛 아이패드(사파리 15 이하) = 처음부터 2단계(화소 1 · 그림자 끔) · 새 아이패드·PC = 그대로 · ?perf=0 = 그대로
   ② 가림 검사(0.1초마다 광선) — 큰 합친 덩어리는 격자로: 결과가 예전(three 광선 전부)과 똑같고 훨씬 빠름
   ③ 「빈 땅」 판 = 재질 1개 · 종류마다 한 덩어리 · 다리 판자·차양·무대·선착장 = 한 덩어리 (그림은 같음)
   ④ 아바타 = 마디마다 한 덩어리 (그림 같음 · 표정 6개 · 눈 깜빡임 · 옷 바꾸기 그대로)
   ⑤ 옛 아이패드 = 나무 줄임 · 큰 덩어리의 JS 사본 버림 · 그래픽이 끊겼다 돌아오면 다시 시작 카드"""
import asyncio, sys, os, json, base64, io
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"lite714"+os.sep; os.makedirs(D, exist_ok=True)
OLDUA="Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1"
DESK15="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
DESK26="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15"
DRAWS="""()=>new Promise(res=>{ const R=renderer, o=R.renderBufferDirect; let m=0, s=0, hero=0, n=0; const H=HOUSE.hero().g; const isIn=(x,p)=>{ for(let c=x;c;c=c.parent) if(c===p) return true; return false; };
  R.renderBufferDirect=function(cam, sc, geo, mat, obj){ const sh=mat && (mat.isMeshDepthMaterial||mat.isMeshDistanceMaterial); if(sh) s++; else m++; if(!sh && isIn(obj,H)) hero++; return o.apply(this, arguments); };
  const f=()=>{ dirty=true; if(++n<4) return requestAnimationFrame(f); R.renderBufferDirect=o; res({main:m/4, shadow:s/4, hero:hero/4}); }; requestAnimationFrame(f); })"""
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def kid(ua=None, q="?isle=1", vw=(768,1024), dpr=2, cores=8, touch=0):
            ctx=await br.new_context(viewport={"width":vw[0],"height":vw[1]}, device_scale_factor=dpr, is_mobile=bool(ua and "iPad;" in ua), has_touch=True, **({"user_agent":ua} if ua else {}))
            await ctx.add_init_script("Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>%d}); %s" % (cores, "Object.defineProperty(navigator,'maxTouchPoints',{get:()=>5});" if touch else ""))
            pg=await ctx.new_page(); pg.set_default_timeout(150000); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"+q); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify('QA714')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
            await pg.reload(); await pg.wait_for_timeout(2200); return pg, ctx
        async def isle(pg):
            await pg.evaluate("()=>ISLE.enter()")
            for _ in range(200):
                try:
                    if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
                except Exception: pass
                await pg.wait_for_timeout(250)
            await pg.wait_for_timeout(1500)
        LV="()=>({lv:GUARD.lv, fl:GUARD.floor||0, pr:renderer.getPixelRatio(), sh:sun.castShadow, old:OLDDEV})"
        # ── ① 기기마다 시작 단계
        A,ca=await kid(OLDUA, cores=4); r=await A.evaluate(LV)
        ok(r["old"] and r["lv"]==2 and r["pr"]==1 and not r["sh"], f"① 옛 아이패드(사파리 15) = 2단계 · 화소 1 · 그림자 끔 {r}")
        for ua,touch,want,nm in [(DESK15,1,2,"데스크톱 모드 아이패드 사파리 15"),(DESK26,1,0,"새 아이패드(사파리 26)"),(None,0,0,"PC 크롬")]:
            B,cb=await kid(ua, touch=touch); rr=await B.evaluate(LV); ok(rr["lv"]==want, f"① {nm} → {want}단계 {rr}"); await cb.close()
        B,cb=await kid(OLDUA, q="?isle=1&perf=0", cores=4); rr=await B.evaluate(LV); ok(rr["lv"]==0 and rr["pr"]==2, f"① ?perf=0 = 그대로(점검용) {rr}"); await cb.close()
        # ── ⑤ 옛 아이패드 섬: 나무 줄임 · JS 사본 버림 · 그리기 수
        await isle(A); await A.wait_for_timeout(800)
        r=await A.evaluate("""()=>{ let dropped=0, big=0; ISLE.G.children.forEach(c=>{ if(c.isMesh && !c.isInstancedMesh && c.geometry.attributes.position.count>=2000){ big++; const n=c.geometry.attributes.normal; if(n && n.array===null) dropped++; } }); return {trees:ISLE.trees().length, dropped, big}; }""")
        ok(r["trees"]<500 and r["dropped"]>=3, f"⑤ 옛 아이패드 섬: 나무 줄임 · 큰 덩어리 법선 JS 사본 버림 (그린 것만) {r}")
        d=await A.evaluate(DRAWS); ok(d["shadow"]==0 and d["main"]<140, f"⑤ 옛 아이패드 섬 그리기 = 그림자 없이 140번 아래 (v713: 442번) {d}")
        await A.screenshot(path=D+"old_ipad_isle.png")
        r=await A.evaluate("""async ()=>{ const ext=renderer.getContext().getExtension('WEBGL_lose_context'); if(!ext) return 'noext'; ext.loseContext(); await new Promise(r=>setTimeout(r,300)); ext.restoreContext(); await new Promise(r=>setTimeout(r,800)); return {card:!!document.getElementById('gdFatal'), sent:GUARD.sent.map(s=>s.k+':'+(s.m||'')).slice(-3)}; }""")
        ok(r=="noext" or r["card"], f"⑤ 옛 아이패드: 그래픽이 끊겼다 돌아오면 다시 시작 카드 {r}")
        await ca.close()
        # ── ②③④ 보통 기기(PC · 그림자 켬)
        C,cc=await kid(None, q="?isle=1&perf=0", vw=(820,1180), dpr=1); await isle(C)
        r=await C.evaluate("""()=>{ const g=ISLE.G, rc=new THREE.Raycaster(); rc.camera=camera; let n=0, same=0, fs=0, tOld=0, tNew=0, hid=0; const anc=h=>{ let o=h.object; while(o.parent && o.parent!==g) o=o.parent; return o; }; let s=714; const rnd=()=>{ s=(s*9301+49297)%233280; return s/233280; };
            for(let pass=0;pass<2;pass++){ if(pass===1){ n=same=fs=hid=0; tOld=tNew=0; s=714; } for(let k=0;k<160;k++){ const x=40+rnd()*200, z=40+rnd()*200, yaw=rnd()*6.28, dist=8+rnd()*14, cam=new THREE.Vector3(x+Math.sin(yaw)*dist*.7, dist*.75, z+Math.cos(yaw)*dist*.7);
              [0.22,0.45,1.15].forEach(hy=>{ const to=new THREE.Vector3(x,hy,z), dir=to.clone().sub(cam), dd=dir.length(); rc.set(cam, dir.normalize()); rc.far=Math.max(.1,dd-.35); occRc.set(cam, dir.clone()); occRc.far=rc.far;
                let t=performance.now(); const H0=rc.intersectObject(g,true); tOld+=performance.now()-t; t=performance.now(); const H1=OCC.hits(g,true); tNew+=performance.now()-t;
                const hd=H=>H.some(h=>{ const o=anc(h); return h.object.isMesh && !h.object.isInstancedMesh && !o.userData.npc && !(h.object.material && h.object.material.transparent); }), fd=H=>[...new Set(H.map(anc).filter(o=>o.parent===g && !o.userData.npc && !o.userData.noFade).map(o=>o.uuid))].sort().join();
                n++; if(hd(H0)===hd(H1)) same++; if(hd(H0)) hid++; if(fd(H0)===fd(H1)) fs++; }); } }
            return {n, same, fs, hid, oldMs:+(tOld/n).toFixed(3), newMs:+(tNew/n).toFixed(3)}; }""")
        ok(r["n"]>=300 and r["same"]==r["n"] and r["fs"]==r["n"] and r["hid"]>=5 and r["newMs"]*3<r["oldMs"], f"② 가림 검사: 나를 가림(실루엣)·흐릴 집이 예전과 {r['same']}/{r['n']} · {r['fs']}/{r['n']} 같음 · 광선 하나 {r['oldMs']}ms → {r['newMs']}ms {r}")
        r=await C.evaluate("""()=>{ const g=ISLE.G; let boards=[], multi=0, bigGrp=0, baked=0; g.children.forEach(c=>{ if(c.userData.boards) boards.push(c.geometry.attributes.position.count/24); if(c.isMesh && Array.isArray(c.material) && c.geometry.parameters && c.geometry.parameters.depth===.06) multi++;
              if(!c.isMesh && c.name!=='vil' && !Object.values(g.userData).includes(c) && c.children.filter(k=>k.isMesh).length>30) bigGrp++; c.traverse(m=>{ if(m.userData.baked) baked+=m.userData.baked; }); });
            const lots=ISLE.lots.filter(L=>!L.owner).length; return {boards, lots, multi, bigGrp, baked}; }""")
        ok(len(r["boards"])>=1 and sum(r["boards"])==r["lots"] and r["multi"]==0, f"③ 「빈 땅」 판 {r['lots']}개 = 덩어리 {len(r['boards'])}개 (재질 6개짜리 판 없음) {r}")
        ok(r["bigGrp"]==0 and r["baked"]>=500, f"③ 다리·차양·무대·선착장 조각 {r['baked']}개 → 한 덩어리씩 (조각 30개 넘는 묶음 없음) {r}")
        d=await C.evaluate(DRAWS); ok(d["main"]+d["shadow"]<260 and d["hero"]<=30, f"③④ 섬 그리기 (화면+그림자) {d['main']+d['shadow']}번 (v713 442번) · 나 {d['hero']}번 (v713 80번) {d}")
        # ④ 아바타: 표정 6개 · 깜빡임 · 옷 바꾸기
        r=await C.evaluate("""async ()=>{ const h=HOUSE.hero(); const cnt=()=>{ let n=0; h.g.traverse(m=>{ if(m.isMesh) n++; }); return n; }; const out={baked:h.baked, n:cnt(), ex:[]};
            for(const k of ['smile','grin','wink','wow','cat','cool']){ h.setExpr(k); out.ex.push([k, h.eyesG.children.length, h.mouthG.children.length, h.expr]); }
            h.setExpr('smile'); h.eyes.scale.y=.1; out.blink=h.eyesG.scale.y; h.eyes.scale.y=1;
            let lathe=0; h.g.traverse(m=>{ if(m.isMesh && m.geometry && (m.geometry.type==='LatheGeometry' || (m.geometry.userData.src||[]).includes('LatheGeometry'))) lathe++; }); out.lathe=lathe; return out; }""")
        ok(r["baked"]>=40 and r["n"]<=32 and all(e[1]>=1 and e[1]<=6 and e[3]==e[0] for e in r["ex"]) and r["blink"]<0.2 and r["lathe"]>=1, f"④ 아바타 조각 {r['n']}개(합친 조각 {r['baked']}) · 표정 6개 다시 그림 · 눈 깜빡임 · 몸통 돌림체 그대로 {r}")
        # ④ 그림 비교: 합치기 끔(?avbake=0) vs 켬 — 아바타 6명
        CFG=[{"hat":"straw"},{"hat":"none","hair":"spiky","style":"hoodie","acc":"glasses","expr":"grin"},{"hat":"cap","style":"overalls","acc":"backpack","expr":"wink"},{"hat":"none","hair":"pigtails","style":"dress","acc":"ribbon","expr":"wow","skin":2,"hc":3},{"hat":"crown","hair":"long","acc":"flower","expr":"cat","skin":1},{"hat":"beanie","hair":"bun","style":"hoodie","expr":"cool","top":4,"pc":2}]
        JS="""(cfg)=>{ const S=new THREE.Scene(); S.background=new THREE.Color(0xf1e2c8); S.add(new THREE.HemisphereLight(0xfff4e0,0x6a5a8a,.75)); S.add(new THREE.AmbientLight(0xffffff,.18)); const l=new THREE.DirectionalLight(0xffe2b8,.85); l.position.set(2,5,4); S.add(l);
          let draws=0; cfg.forEach((c,i)=>{ const P=buildAvatar(c); P.g.position.set((i%3-1)*1.1, i<3?0.9:-0.9, 0); P.g.rotation.y=i%2?0.5:-0.4; if(i===2){ P.armR.rotation.x=-2.4; P.legL.rotation.x=.5; } S.add(P.g); });
          const cam=new THREE.PerspectiveCamera(30, renderer.domElement.width/renderer.domElement.height, .1, 50); cam.position.set(0,1.0,6.2); cam.lookAt(0,0.9,0);
          renderer.info.autoReset=false; renderer.info.reset(); renderer.render(S, cam); draws=renderer.info.render.calls; renderer.info.autoReset=true; return {url:renderer.domElement.toDataURL('image/png'), draws}; }"""
        from PIL import Image, ImageChops
        ims=[]
        for q in ("?avbake=0","?"):
            E,ce=await kid(None, q=q, vw=(700,700), dpr=1); rr=await E.evaluate(JS, CFG); ims.append((Image.open(io.BytesIO(base64.b64decode(rr["url"].split(",")[1]))).convert("RGB"), rr["draws"])); await ce.close()
        (a,da),(b,db)=ims; dif=ImageChops.difference(a,b); px=sum(1 for v in dif.convert("L").getdata() if v>24)
        cmp=Image.new("RGB",(a.width*2,a.height)); cmp.paste(a,(0,0)); cmp.paste(b,(a.width,0)); cmp.save(D+"avatars_off_on.png")
        ok(px<a.width*a.height*0.002 and db*3<da, f"④ 아바타 6명 그림 같음 (다른 점 {px}px) · 그리기 {da} → {db}번")
        # ④ 옷 바꾸기 = 새로 만들어도 합침 · 앞 아바타 도형은 버려짐(오류 없음)
        r=await C.evaluate("()=>{ const a=HOUSE.av(); a.hat=a.hat==='cap'?'straw':'cap'; try{ localStorage.setItem('hyeng_proto_av', JSON.stringify(a)); }catch(e){} makeHero(); const h=HOUSE.hero(); return {baked:h.baked, vis:h.g.visible, parent:!!h.g.parent}; }")
        ok(r["baked"]>=40 and r["parent"], f"④ 옷 바꾸기(다시 만들기) 뒤에도 합침 {r}")
        await C.screenshot(path=D+"pc_isle.png"); await cc.close()
        await br.close()
    ok(not real_errs(errs), f"페이지 오류 없음 {real_errs(errs)[:3]}")
    print("\n결과:", "모두 통과" if not bad else f"{len(bad)}개 실패"); sys.exit(1 if bad else 0)
asyncio.run(main())
