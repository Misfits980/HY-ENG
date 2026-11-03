"""(v566) 사용자 캡처 (아이폰 · 가구 가게):
   ① 머리 💎·🪙 가 네 줄로 꺾임 → 오른쪽에 작은 알약 두 개 한 줄
   ② 종류 칩이 세 줄을 차지 → 수납형: 한 줄 가로 밀기 + 「▾ 모두」 누르면 촤라락 펼침 · 고르면 다시 접힘 · 고른 칩이 보이게 가로 스크롤
   폰 390×844 · 패드 820×1180 · 페이지 가로 스크롤 없음"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        for W,H in [(390,844),(820,1180)]:
            ctx=await br.new_context(viewport={"width":W,"height":H}, is_mobile=W<500, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(500)
            await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('AAAAA')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
            await pg.reload(); await pg.wait_for_timeout(2500)
            await pg.evaluate("()=>{ gems=11186; saveBag(); TECO.setCoin(0); openFurn('furn'); furnCat='wall'; drawFurn(); }"); await pg.wait_for_timeout(500)
            t=f"[{W}]"
            r=await pg.evaluate("""()=>{ const F=document.getElementById('furnGem'), X=document.getElementById('furnDone'), b=F.getBoundingClientRect(), x=X.getBoundingClientRect();
                const pills=[...F.querySelectorAll('.cur')].map(e=>e.getBoundingClientRect());
                return [pills.length, Math.round(b.height), pills.every(p=>Math.abs(p.top-pills[0].top)<2), Math.round(x.left-b.right), F.innerText.replace(/\\s+/g,' ')]; }""")
            ok(r[0]==2 and r[1]<=34 and r[2] and 0<=r[3]<=20, f"{t} ① 머리 = 💎·🪙 알약 두 개 한 줄 · ✕ 바로 옆 {r}")
            r=await pg.evaluate("""()=>{ const B=document.querySelector('#furnBody .cBar'), sc=B.querySelector('.fCat'), on=sc.querySelector('.chip.on'), o=on.getBoundingClientRect(), s=sc.getBoundingClientRect(), tg=B.querySelector('.cTog').getBoundingClientRect();
                return [B.classList.contains('open'), Math.round(sc.getBoundingClientRect().height), sc.scrollWidth>sc.clientWidth, o.left>=s.left-1 && o.right<=tg.left+2, document.documentElement.scrollWidth<=innerWidth]; }""")
            ok(not r[0] and r[1]<=56 and (r[2] or W>500) and r[3] and r[4], f"{t} ② 접힘 = 한 줄 · 가로 밀기 · 고른 「🖼 벽」 이 보임(▾ 단추에 안 가림) · 페이지 가로 스크롤 없음 {r}")
            await pg.screenshot(path=OUT+f"furn566_{W}_closed.png")
            await pg.click("#furnBody .cTog"); await pg.wait_for_timeout(600)
            r=await pg.evaluate("()=>{ const B=document.querySelector('#furnBody .cBar'), sc=B.querySelector('.fCat'); return [B.classList.contains('open'), Math.round(sc.getBoundingClientRect().height), B.querySelector('.cTog').innerText, sc.querySelectorAll('.chip').length, document.documentElement.scrollWidth<=innerWidth]; }")
            ok(r[0] and r[1]>56 and "접기" in r[2] and r[3]==11 and r[4], f"{t} ② ▾ 모두 → 촤라락 펼침 (여러 줄) · ▴ 접기 {r}")
            await pg.screenshot(path=OUT+f"furn566_{W}_open.png")
            await pg.click("#furnBody [data-fc=plant]"); await pg.wait_for_timeout(400)
            r=await pg.evaluate("()=>{ const B=document.querySelector('#furnBody .cBar'); return [B.classList.contains('open'), furnCat, B.querySelector('.chip.on').dataset.fc, document.querySelectorAll('#furnBody .sRow').length]; }")
            ok(not r[0] and r[1]=="plant" and r[2]=="plant" and r[3]>0, f"{t} ② 고르면 다시 접히고 그 종류 가구 {r}")
            await pg.evaluate("()=>{ furnTab='yard'; drawFurn(); }"); await pg.wait_for_timeout(300)
            r=await pg.evaluate("()=>[!!document.querySelector('#furnBody .cBar[data-cbar=yc]'), document.querySelectorAll('#furnBody [data-yc]').length]")
            ok(r[0] and r[1]==6, f"{t} 🌳 마당 칩도 같은 수납형 {r}")
            await ctx.close()
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
