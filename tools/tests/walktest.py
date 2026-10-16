"""(v306) 걷기 그림 캐릭터 9명 — run-<id> 그림이 오고, 앞(뒷모습)·오른쪽·왼쪽 대각, 뒤로 갈 때 뒷걸음질(프레임 거꾸로)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
IDS=["hero","explorer","archer","mage","knight","scholar","ghost","cat","wolf"]
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={"width":844,"height":390})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        for cid in IDS:
            ok=await pg.evaluate(f"""()=>new Promise(res=>{{ G.char='{cid}'; setCharacter('{cid}'); let n=0; const t=setInterval(()=>{{ n++; if(player.userData.walk || n>40){{ clearInterval(t); res(!!player.userData.walk); }} if(TrapArt.has('run-{cid}') && !player.userData.walk) setCharacter('{cid}'); }},100); }})""")
            if not ok: bad.append(f"{cid} 걷기 그림 없음")
        await pg.evaluate("()=>{ G.char='knight'; setCharacter('knight'); G.set='basic'; G.diff='easy'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(2500)
        # 앞으로 · 오른쪽 · 왼쪽 · 뒤로
        def st(): return pg.evaluate("()=>{ const w=player.userData.walk; return w ? [w.row, w.f] : null; }")
        async def hold(key, name):
            await pg.keyboard.down(key); seq=[]; await pg.wait_for_timeout(120)
            for i in range(14):
                await pg.wait_for_timeout(50); seq.append(await st())
            await pg.screenshot(path=OUT+f"walk_{name}.png")
            await pg.keyboard.up(key); await pg.wait_for_timeout(400); print(name, seq); return [x for x in seq if x]
        def back_ok(seq):
            fs=[x[1] for x in seq[1:9]]; steps=[(b-a)%6 for a,b in zip(fs,fs[1:]) if a!=b]
            return all(x[0]==0 for x in seq) and steps and sum(1 for v in steps if v==5)>=len(steps)*0.6
        checks=[("fwd","ArrowUp",lambda q: all(x[0]==0 for x in q[6:])),("right","ArrowRight",lambda q: any(x[0]==1 for x in q)),
                ("left","ArrowLeft",lambda q: any(x[0]==2 for x in q)),("back","ArrowDown",back_ok)]
        for name,key,fn in checks:   # 판 안에서 문·함정 때문에 잠깐 멈출 수 있어 세 번까지
            good=False
            for t in range(3):
                if name=="back": await pg.keyboard.down("ArrowUp"); await pg.wait_for_timeout(1200); await pg.keyboard.up("ArrowUp"); await pg.wait_for_timeout(150)   # 앞으로 나가 있어야 뒤로 갈 자리가 있음
                if fn(await hold(key,name)): good=True; break
                await pg.keyboard.press("ArrowUp" if name!="back" else "ArrowRight")
            if not good: bad.append(f"{name} 걷기 그림 줄·순서")
        print("errs", real_errs(errs)[:5]); await br.close()
    e=real_errs(errs)
    print("결과:", "통과 ✅" if not bad and not e else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or e: sys.exit(1)
asyncio.run(main())
