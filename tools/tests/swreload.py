import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
FAKE="""(()=>{ const et=new EventTarget(); et.controller={}; et.register=()=>Promise.resolve({update(){}}); Object.defineProperty(navigator,'serviceWorker',{value:et,configurable:true}); window.__loads=(+sessionStorage.getItem('L')||0)+1; sessionStorage.setItem('L',window.__loads); })()"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script(FAKE)
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        L=lambda: pg.evaluate("()=>window.__loads")
        fire="()=>navigator.serviceWorker.dispatchEvent(new Event('controllerchange'))"
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        await pg.evaluate(fire); await pg.wait_for_timeout(2500); print('in lesson -> loads', await L())
        for k in range(3): await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(50)
        await pg.wait_for_timeout(2200); print('still in lesson ->', await L())
        await pg.evaluate("()=>document.getElementById('stQuit').click()"); await pg.wait_for_timeout(5000)
        print('back to path ->', await L())
        # run game case
        await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='basic'; G.diff='normal'; G.rule='normal'; startGame(); }"); await pg.wait_for_timeout(1500)
        await pg.evaluate(fire); await pg.wait_for_timeout(2500); print('in run ->', await L(), await pg.evaluate("()=>G.running"))
        await pg.evaluate("()=>{ gameOver(); }"); await pg.wait_for_timeout(3000); print('result screen ->', await L())
        await pg.evaluate("()=>document.getElementById('btnMain').click()"); await pg.wait_for_timeout(5000); print('main menu ->', await L())
        print(errs[:3])
        # (v322) 첫 화면이어도 보스 화면·이름 고르기·보상 창 위, 레이드 중(화면이 가려져도)에는 미뤄야 한다
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        await ctx.add_init_script(FAKE.replace("window.__loads", "window.HY_FB_LOCAL=true; window.__loads", 1))
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        L=lambda: pg.evaluate("()=>window.__loads")
        SETUP="""()=>FB.set('/hy/roster',{t:{},k:{k1:{n:'민준'}}}).then(()=>HyBoss.setup({on:true,team:false,split:'eq',restart:true})).then(()=>{ Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',6); show('scStart'); })"""
        cases=[("boss view", "()=>WeekBoss.open()", "()=>WeekBoss.close()"),
               ("kid picker", "()=>KidPick.open()", "()=>KidPick.close()"),
               ("gain popup", "()=>WeekBoss.gain(2,'study')", "()=>{ const d=document.getElementById('wbPop'); if(d) d.remove(); }"),
               ("raid + hidden", "()=>{ Raid.role='host'; Object.defineProperty(document,'hidden',{get:()=>true,configurable:true}); document.dispatchEvent(new Event('visibilitychange')); }",
                                 "()=>{ Raid.role=null; }")]
        for name, op, cl in cases:
            await pg.evaluate(SETUP); await pg.wait_for_timeout(300); n0=await L()
            await pg.evaluate(op); await pg.wait_for_timeout(400); await pg.evaluate(fire); await pg.wait_for_timeout(5000)
            n1=await L(); print(name, 'loads', n0, '->', n1)
            if n1!=n0: print("BAD reloaded while", name)
            await pg.evaluate(cl); await pg.wait_for_timeout(5000)
            n2=await L(); print(name, 'closed -> loads', n2)
            if n2==n1: print("BAD did not reload after closing", name)
            await pg.wait_for_timeout(600); await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ StudyUI.FAST=0; }catch(e){} }")
        print('errs', real_errs(errs)[:3]); await br.close()
asyncio.run(main())
