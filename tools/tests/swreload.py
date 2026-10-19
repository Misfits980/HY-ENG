"""새 버전이 들어왔을 때 언제 새로고침하나 (v251 · v322 · v347)
(v347) 보고 있는 화면은 어디든(첫 화면·길 화면 포함) 새로고침하지 않는다 → 앱을 내렸을 때(안 보일 때)만.
       화면이 이미 새 버전이면(서비스워커가 같은 버전이라고 답하면) 내려도 새로고침하지 않는다.
       달리는 중·일시정지·공부 문제·레이드·보스 화면·이름 고르기·보상 창은 내려도 미룬다."""
import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
FAKE="""(()=>{ const et=new EventTarget(); et.controller={postMessage(m){ window.__asked=(window.__asked||0)+1; }}; et.register=()=>Promise.resolve({update(){}}); Object.defineProperty(navigator,'serviceWorker',{value:et,configurable:true}); window.__loads=(+sessionStorage.getItem('L')||0)+1; sessionStorage.setItem('L',window.__loads); })()"""
FIRE="()=>navigator.serviceWorker.dispatchEvent(new Event('controllerchange'))"
HIDE="()=>{ Object.defineProperty(document,'hidden',{get:()=>true,configurable:true}); document.dispatchEvent(new Event('visibilitychange')); }"
SAME="()=>navigator.serviceWorker.dispatchEvent(new MessageEvent('message',{data:{hyVer:'hyeng-'+GAME_VER}}))"
NEWS="()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ StudyUI.FAST=0; }catch(e){} }"
bad=[]
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        async def fresh():
            ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
            await ctx.add_init_script(FAKE.replace("window.__loads", "window.HY_FB_LOCAL=true; window.__loads", 1))
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
            await pg.evaluate(NEWS); return pg
        L=lambda pg: pg.evaluate("()=>window.__loads")

        # 1) 공부 중 → 길 화면(보이는 중) → 내림
        pg=await fresh()
        await pg.evaluate("()=>{ StudyUI.open(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        await pg.evaluate(FIRE); await pg.wait_for_timeout(2500); ok(await L(pg)==1, "공부 중: 새로고침 안 함")
        ok(await pg.evaluate("()=>window.__asked||0")>=1, "새 서비스워커에게 버전을 물음")
        await pg.evaluate("()=>document.getElementById('stQuit').click()"); await pg.wait_for_timeout(4500)
        ok(await L(pg)==1, "길 화면을 보고 있는 동안: 새로고침 안 함 (v347)")
        await pg.evaluate("()=>{ show('scStart'); }"); await pg.wait_for_timeout(4500)
        ok(await L(pg)==1, "첫 화면을 보고 있는 동안: 새로고침 안 함 (v347)")
        await pg.evaluate(HIDE); await pg.wait_for_timeout(2500)
        ok(await L(pg)==2, "앱을 내리면 새로고침 (%s)" % await L(pg))

        # 2) 달리는 중 내림 → 미룸 → 결과·첫 화면(보임) → 안 함 → 내림 → 새로고침
        pg=await fresh()
        await pg.evaluate("()=>{ G.set='basic'; G.diff='normal'; G.rule='normal'; startGame(); }"); await pg.wait_for_timeout(1500)
        await pg.evaluate(FIRE); await pg.evaluate("()=>{ Object.defineProperty(document,'hidden',{get:()=>true,configurable:true}); document.dispatchEvent(new Event('visibilitychange')); }")
        await pg.wait_for_timeout(2500); ok(await L(pg)==1 and await pg.evaluate("()=>G.running"), "달리는 중 내려도 미룸")
        await pg.evaluate("()=>{ Object.defineProperty(document,'hidden',{get:()=>false,configurable:true}); document.dispatchEvent(new Event('visibilitychange')); gameOver(); }")
        await pg.wait_for_timeout(3000); ok(await L(pg)==1, "결과 화면: 안 함")
        await pg.evaluate("()=>document.getElementById('btnMain').click()"); await pg.wait_for_timeout(4500); ok(await L(pg)==1, "첫 화면(보임): 안 함")
        await pg.evaluate(HIDE); await pg.wait_for_timeout(2500); ok(await L(pg)==2, "내리면 새로고침")

        # 3) 이미 같은 버전이면 내려도 새로고침 안 함
        pg=await fresh()
        await pg.evaluate(FIRE); await pg.evaluate(SAME); await pg.evaluate(HIDE); await pg.wait_for_timeout(4500)
        ok(await L(pg)==1, "화면이 이미 새 버전이면 새로고침 안 함")

        # 4) 보스 화면·이름 고르기·보상 창·레이드는 내려도 미루고, 닫은 뒤 내려 있으면 새로고침
        SETUP="""()=>FB.set('/hy/roster',{t:{},k:{k1:{n:'민준'}}}).then(()=>HyBoss.setup({on:true,team:false,split:'eq',restart:true})).then(()=>{ Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',6); show('scStart'); })"""
        cases=[("보스 화면", "()=>WeekBoss.open()", "()=>WeekBoss.close()"),
               ("이름 고르기", "()=>KidPick.open()", "()=>KidPick.close()"),
               ("보상 창", "()=>WeekBoss.gain(2,'study')", "()=>{ const d=document.getElementById('wbPop'); if(d) d.remove(); }"),
               ("레이드", "()=>{ Raid.role='host'; }", "()=>{ Raid.role=null; }")]
        for name, op, cl in cases:
            pg=await fresh(); await pg.evaluate(SETUP); await pg.wait_for_timeout(300)
            await pg.evaluate(op); await pg.wait_for_timeout(400); await pg.evaluate(FIRE); await pg.evaluate(HIDE); await pg.wait_for_timeout(4500)
            ok(await L(pg)==1, name+": 내려도 미룸")
            await pg.evaluate(cl); await pg.wait_for_timeout(4500)
            ok(await L(pg)==2, name+": 닫으면(내려 있는 동안) 새로고침")
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:2]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 "+str(bad))
asyncio.run(main())
