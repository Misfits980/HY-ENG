"""(v736) 🎨 그림 맞히기 — 사용자 「그림 그리기 게임은 가로세로 크기가 안 맞고 그림 그리기 도구가 부족해」
   ① 칠판 = 늘 4:3 · 남은 자리에 꽉 (패드 가로 · PC 는 칠판 왼쪽 + 도구 오른쪽) · 도구·단추가 화면 안 · 옆으로 안 넘침
   ② 새 도구: 색 15 + 🌈 · 굵기 4 · 🪣 채우기(동그라미 안만 칠함 · 되돌리기 됨) · ⭐ 도장(그려 보기만) · 🧽 지우개
   ③ 같이 하기 글(enc/dec) 그대로 오감 · 같이 하기에는 도장 없음"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot, menu
from playwright.async_api import async_playwright
OUTD=OUT+"dw736/"; os.makedirs(OUTD, exist_ok=True)
VPS=[(390,844),(375,667),(844,390),(667,375),(820,1180),(1180,820),(768,1024),(1024,768),(1366,768),(1024,700),(1280,600)]
MEAS="""()=>{ const c=document.querySelector('#mgUI .dwBd canvas'), b=c.getBoundingClientRect(); const vis=e=>e && e.offsetParent!==null && getComputedStyle(e).display!=='none';
  const els=[...document.querySelectorAll('#mgUI .dwTl button, #mgUI .dwKb button, #mgUI .dwBar')].filter(vis); let out=0; els.forEach(e=>{ const r=e.getBoundingClientRect(); if(r.bottom>innerHeight+1 || r.right>innerWidth+1 || r.left<-1) out++; });
  let ov=0; const bb=[b.left,b.top,b.right,b.bottom]; els.forEach(e=>{ const r=e.getBoundingClientRect(); if(r.left<bb[2]-2 && bb[0]<r.right-2 && r.top<bb[3]-2 && bb[1]<r.bottom-2) ov++; });
  return {w:Math.round(b.width), h:Math.round(b.height), r:+(b.width/b.height).toFixed(3), out, ov, sx:document.documentElement.scrollWidth>innerWidth+1}; }"""
TAP="""([x,y])=>{ const c=document.querySelector('#mgUI .dwBd canvas'), b=c.getBoundingClientRect(), cx=b.left+x/1000*b.width, cy=b.top+y/750*b.height;
  const o={clientX:cx, clientY:cy, pointerId:7, bubbles:true, pointerType:'touch'}; c.dispatchEvent(new PointerEvent('pointerdown',o)); c.dispatchEvent(new PointerEvent('pointerup',o)); }"""
BTN="""(sel)=>{ const b=document.querySelector('#mgUI .dwTl '+sel); if(!b) return false; b.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); return true; }"""
PIX="""([x,y])=>{ const c=document.querySelector('#mgUI .dwBd canvas'); const d=c.getContext('2d').getImageData(x,y,1,1).data; return [d[0],d[1],d[2]]; }"""

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","DW736A", vp={"width":390,"height":844}, isle=False)
        await menu(pg)
        await pg.evaluate("()=>{ MG.run.menuGo('sketch'); }"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>MG.run.pick(0)"); await pg.wait_for_timeout(300)
        # ① 크기
        res={}
        for w,h in VPS:
            await pg.set_viewport_size({"width":w,"height":h}); await pg.wait_for_timeout(700)
            res[(w,h)]=await pg.evaluate(MEAS)
            if (w,h) in ((390,844),(1180,820),(667,375),(820,1180)): await pg.screenshot(path=OUTD+f"sketch_{w}x{h}.png")
        ok(all(abs(v["r"]-1.333)<.012 for v in res.values()), "① 칠판 늘 4:3 "+str({k:v["r"] for k,v in res.items()}))
        ok(all(v["out"]==0 and v["ov"]==0 and not v["sx"] for v in res.values()), "① 도구 화면 안 · 칠판과 안 겹침 · 옆 넘침 없음 "+str({k:(v["out"],v["ov"],v["sx"]) for k,v in res.items() if v["out"] or v["ov"] or v["sx"]}))
        ok(res[(1180,820)]["w"]>=760 and res[(820,1180)]["w"]>=760 and res[(1366,768)]["w"]>=800 and res[(390,844)]["w"]>=360, "① 큰 화면에서 칠판이 큼 "+str({k:res[k]["w"] for k in [(1180,820),(820,1180),(1366,768),(390,844)]}))
        await pg.set_viewport_size({"width":820,"height":1180}); await pg.wait_for_timeout(600)
        # ② 도구
        n=await pg.evaluate("()=>[document.querySelectorAll('#mgUI .dwTl .r.cl button').length, document.querySelectorAll('#mgUI .dwTl button.s').length, !!document.querySelector('#mgUI .dwTl [data-m=fill]'), !!document.querySelector('#mgUI .dwTl [data-m=stamp]'), !!document.querySelector('#mgUI .dwTl [data-m=erase]')]")
        ok(n[0]==16 and n[1]==4 and n[2] and n[3] and n[4], f"② 색 16(🌈 포함) · 굵기 4 · 🪣 · ⭐ · 🧽 {n}")
        # 동그라미 그리고 안을 채우기
        await pg.evaluate("()=>MG.run.demo(1)")
        await pg.evaluate(BTN, "[data-c='1']"); await pg.evaluate(BTN, "[data-m=fill]")
        await pg.evaluate(TAP, [500,375]); await pg.wait_for_timeout(100)
        inside=await pg.evaluate(PIX, [500,375]); outside=await pg.evaluate(PIX, [60,60])
        ok(inside[0]>230 and inside[1]<120 and outside==[255,255,255], f"② 🪣 동그라미 안만 빨강 {inside} · 밖 흰색 {outside}")
        await pg.evaluate(BTN, "[data-t=undo]"); await pg.wait_for_timeout(100)
        back=await pg.evaluate(PIX, [500,375])
        ok(back==[255,255,255], f"② 되돌리기 → 다시 흰색 {back}")
        # 도장
        await pg.evaluate(BTN, "[data-m=stamp]"); await pg.evaluate(BTN, "[data-e='1']")
        n0=await pg.evaluate("()=>MG.run.MY.length"); await pg.evaluate(TAP, [200,200]); n1=await pg.evaluate("()=>[MG.run.MY.length, MG.run.MY[MG.run.MY.length-1].S]")
        ok(n1[0]==n0+1 and n1[1]["s"]>=21, f"② ⭐ 도장 찍힘 {n1}")
        # 무지개 · 지우개 한 줄
        await pg.evaluate(BTN, "[data-c='30']")
        await pg.evaluate("""()=>{ const c=document.querySelector('#mgUI .dwBd canvas'), b=c.getBoundingClientRect(); const P=(t,x,y)=>c.dispatchEvent(new PointerEvent(t,{clientX:b.left+x/1000*b.width, clientY:b.top+y/750*b.height, pointerId:8, bubbles:true}));
            P('pointerdown',100,650); for(let x=100;x<=900;x+=20) P('pointermove',x,650); P('pointerup',900,650); }""")
        cols=await pg.evaluate("()=>{ const c=document.querySelector('#mgUI .dwBd canvas').getContext('2d'); const s=new Set(); for(let x=120;x<880;x+=60){ const d=c.getImageData(x,650,1,1).data; s.add(d[0]>>5|d[1]>>5<<3|d[2]>>5<<6); } return s.size; }")
        ok(cols>=4, f"② 🌈 무지개 줄 = 여러 색 {cols}")
        await pg.screenshot(path=OUTD+"tools_820.png")
        # ③ 글 주고받기
        r=await pg.evaluate("""()=>{ const R=MG.run; const L=R.MY.map(x=>x.S); return L.map(S=>{ const e=R.enc?R.enc(S):null; return e; }); }""")
        await br.close()
    print("오류", errs[:4])
    if errs: bad.append("errors")
    print("BAD: %d" % len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
