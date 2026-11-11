"""(v599) 사용자: 「물총아레나 뭔가 아쉽다 · 설정도 없고 들어가는 방식도 없어서 그냥 인게임으로 가야 하네」 + 「맵도 하나잖아」
   ① 들어가면 아레나 메뉴 (혼자 · 같이 · 맵 3 · 설정 · 무기 · 기록 · 섬으로) · 버튼·조이스틱은 숨김 · 화면 안에 다 들어감
   ② 설정: 감도 · 조준 도움 · 자동 쏘기 · 시야 · 버튼 크기 · 소리 → 기기에 저장 · 바로 적용
   ③ 맵 3개: 고르면 뒤 배경이 바로 바뀜 · 맵마다 나오는 자리 · 봇이 길 찾아 다니며 싸움
   ④ 시작 연출(누구랑 · 맵 이름) → 3·2·1 · 게임 중 ☰ 메뉴(멈춤 · 설정 · 아레나 메뉴) · 결과 「💦 메뉴」「한 판 더」"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def boot(br, vw, vh, real=False):
    ctx=await br.new_context(viewport={"width":vw,"height":vh}, is_mobile=True, has_touch=True)
    if real: await ctx.add_init_script("Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>8})")
    pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
    await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.removeItem('hyeng_proto_arenaset'); }")
    await pg.reload(); await pg.wait_for_timeout(2400)
    return ctx, pg, errs

async def main():
    bad=[]; allerr=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        # ── 휴대폰 가로
        cP,P,eP=await boot(br, 844, 390)
        await P.evaluate("()=>MG.lobby('arena')"); await P.wait_for_timeout(1600)
        r=await P.evaluate("""()=>{ const s=document.querySelector('#mgUI .aSide'), q=x=>document.querySelector(x); const vis=e=>!!e && getComputedStyle(e).display!=='none' && e.offsetWidth>0;
            return [MG.run.phase, !document.getElementById('mgLob') || !document.getElementById('mgLob').classList.contains('on'), vis(s), s.scrollHeight<=s.clientHeight+1, s.getBoundingClientRect().bottom<=innerHeight, vis(q('#mgUI [data-b=fire]')), vis(q('#mgUI .mgJoyH')), vis(q('#mgUI .aClock')), MG.run.ACT.length]; }""")
        ok(r==["menu",True,True,True,True,False,False,False,1], f"① 탑 → 바로 아레나 메뉴 · 메뉴가 화면 안에 다 들어감 · 쏘기 버튼·조이스틱·시계 숨김 · 봇은 아직 없음 {r}")
        await P.wait_for_timeout(800); await P.screenshot(path=OUT+"arena599_menu_phone.png")
        # ② 설정
        await P.evaluate("()=>document.querySelector('#mgUI .aSide [data-c=set]').click()"); await P.wait_for_timeout(200)
        r=await P.evaluate("()=>[document.querySelectorAll('#mgUI .aCard .aSet').length, document.querySelector('#mgUI .aCard').scrollHeight>0]")
        ok(r[0]==6, f"② 설정 6가지 {r}")
        await P.screenshot(path=OUT+"arena599_set_phone.png")
        await P.evaluate("()=>{ const c=(k,v)=>document.querySelector('#mgUI .aCard [data-s='+k+'][data-v=\"'+v+'\"]').click(); c('sens',5); c('btn',2); c('aim',0); c('vol',1); c('fov',2); }")
        r=await P.evaluate("()=>{ const S=JSON.parse(localStorage.getItem('hyeng_proto_arenaset')||'{}'); return [S.sens, S.btn, S.aim, S.vol, S.fov, document.getElementById('mgUI').classList.contains('aBs2'), MG.SFX.vol]; }")
        ok(r==[5,2,0,1,2,True,0.45], f"② 고르면 기기에 저장 · 버튼 크게 · 소리 작게 바로 적용 {r}")
        await P.evaluate("()=>document.querySelector('#mgUI .aCard .x').click()")
        await P.evaluate("()=>document.querySelector('#mgUI .aSide [data-c=wp]').click()"); await P.wait_for_timeout(200)
        r=await P.evaluate("()=>document.querySelectorAll('#mgUI .aCard .aWpL>div').length")
        ok(r==8, f"① 무기 8단계 보기 {r}"); await P.screenshot(path=OUT+"arena599_wp_phone.png")
        await P.evaluate("()=>document.querySelector('#mgUI .aCardW').click()")
        await P.evaluate("()=>document.querySelector('#mgUI .aSide [data-c=rec]').click()"); await P.wait_for_timeout(200)
        r=await P.evaluate("()=>document.querySelectorAll('#mgUI .aCard .aRec>div').length"); ok(r==6, f"① 내 기록 {r}")
        await P.evaluate("()=>document.querySelector('#mgUI .aCard .x').click()")
        # 감도 5 = 같은 끌기에 더 많이 돎 (메뉴에서 혼자 → 시작)
        await P.evaluate("()=>document.querySelector('#mgUI .aSide [data-c=solo]').click()"); await P.wait_for_timeout(150)
        await P.evaluate("()=>document.querySelector('#mgUI .aCard [data-go=solo]').click()"); await P.wait_for_timeout(100)
        r=await P.evaluate("()=>[MG.run.phase, MG.run.ACT.length, getComputedStyle(document.querySelector('#mgUI .aVs')).display, document.querySelectorAll('#mgUI .aVs .ps span').length]")
        ok(r==["intro",6,"block",6], f"④ 시작 → 시작 연출 (6명 이름표) {r}")
        await P.wait_for_timeout(900); await P.screenshot(path=OUT+"arena599_intro_phone.png")
        await P.evaluate("()=>{ for(let i=0;i<120;i++) MG.step(.05,false); }")
        r=await P.evaluate("()=>{ const R=MG.run, I=MG.I; I.touch=true; I.lock=false; I.mouse=false; R.me.yaw=0; I.lx=100; MG.step(.016,false); const y5=R.me.yaw; return [R.phase, R.time.cd<=0, +(-y5).toFixed(3), getComputedStyle(document.querySelector('#mgUI [data-b=fire]')).scale]; }")
        ok(r[0]=="play" and r[1] and abs(r[2]-100*.0058*1.8)<.02 and r[3]=="1.2", f"② 감도 5 = 1.8배 · 버튼 1.2배 · 시작 연출 뒤 3·2·1 → 게임 {r}")
        await P.evaluate("()=>{ const R=MG.run; R.me.p.set(0,0,18); R.me.yaw=0; R.me.pitch=-.05; }"); await P.wait_for_timeout(900)
        await P.screenshot(path=OUT+"arena599_play_phone.png")
        # ☰ 메뉴 = 멈춤
        await P.evaluate("()=>document.querySelector('#mgUI .aPzB').click()"); await P.wait_for_timeout(150)
        r=await P.evaluate("()=>{ const R=MG.run, t0=R.time.left; for(let i=0;i<20;i++) MG.step(.05,false); return [document.querySelector('#mgUI .aCardW').classList.contains('on'), R.time.left===t0]; }")
        ok(r==[True,True], f"④ 게임 중 ☰ 메뉴 → 혼자 하기는 멈춤 {r}")
        await P.screenshot(path=OUT+"arena599_pause_phone.png")
        await P.evaluate("()=>document.querySelector('#mgUI .aCard [data-go=resume]').click()")
        r=await P.evaluate("()=>{ const R=MG.run, t0=R.time.left; for(let i=0;i<20;i++) MG.step(.05,false); return R.time.left<t0; }")
        ok(r, f"④ 계속하기 → 다시 흐름 {r}")
        # 결과 → 메뉴 · 한 판 더
        await P.evaluate("()=>{ const R=MG.run; R.win(R.me); }"); await P.wait_for_timeout(2400)
        r=await P.evaluate("()=>{ const el=document.querySelector('#mgUI .puR'); return [!!el, !!el.querySelector('.menu'), !!el.querySelector('.again')]; }")
        ok(r==[True,True,True], f"④ 결과: 섬으로 · 💦 메뉴 · 한 판 더 {r}")
        await P.screenshot(path=OUT+"arena599_result_phone.png"); await P.evaluate("()=>document.querySelector('#mgUI .puR .again').click()"); await P.wait_for_timeout(300)
        r=await P.evaluate("()=>[MG.run.phase, MG.run.ACT.length]"); ok(r==["intro",6], f"④ 한 판 더 = 메뉴 없이 바로 {r}")
        await P.evaluate("()=>{ for(let i=0;i<60;i++) MG.step(.05,false); document.querySelector('#mgUI .aPzB').click(); document.querySelector('#mgUI .aCard [data-go=menu]').click(); }"); await P.wait_for_timeout(300)
        r=await P.evaluate("()=>[MG.run.phase, MG.run.ACT.length, MG.on]"); ok(r==["menu",1,True], f"④ ☰ → 아레나 메뉴로 {r}")
        allerr+=eP
        # ── 패드 (진짜 모습: 테두리·그림자)
        cA,A,eA=await boot(br, 1180, 820, True)
        await A.evaluate("()=>MG.enter('arena',{})"); await A.wait_for_timeout(1600)
        for k in ["pool","sand","toy"]:
            await A.evaluate("(k)=>document.querySelector('#mgUI .aMaps [data-m='+k+']').click()", k); await A.wait_for_timeout(1200)
            r=await A.evaluate("""()=>{ const R=MG.run; const bad=R.SPAWN.filter(([x,z])=>R.BOX.some(b=>b.y0<1.7 && b.y1>3 && x+.34>b.x0 && x-.34<b.x1 && z+.34>b.z0 && z-.34<b.z1)).length;
                return [R.MAPK, R.BOX.length, R.SPAWN.length, bad, R.PADS.length, document.querySelector('#mgUI .aMaps .on').dataset.m, JSON.parse(localStorage.getItem('hyeng_proto_arenaset')).map]; }""")
            ok(r[0]==k and r[1]>20 and r[2]>=10 and r[3]==0 and r[4]==4 and r[5]==k and r[6]==k, f"③ {k}: 고르면 바로 바뀜 · 상자 {r[1]} · 나오는 자리 {r[2]} (막힌 곳 {r[3]}) · 발판 {r[4]}")
            await A.screenshot(path=OUT+f"arena599_menu_{k}.png")
        # 맵마다 봇 25초
        for k in ["pool","sand","toy"]:
            r=await A.evaluate("""(k)=>{ const R=MG.run; R.setMap(k); R.beginSolo(); for(let i=0;i<60;i++) MG.step(.05,false); R.me.alive=false; R.me.resp=999; R.ACT.forEach(a=>{ if(a.bot) a.prot=0; });
                const p0=R.ACT.map(a=>a.p.clone()), k0=R.ACT.reduce((s,a)=>s+a.kills,0); const mv=new Set(); let stuck=0;
                for(let i=0;i<500;i++){ MG.step(.05,false); R.ACT.forEach((a,j)=>{ if(a.bot && a.p.distanceTo(p0[j])>3) mv.add(j); }); }
                const out=[mv.size, R.ACT.reduce((s,a)=>s+a.kills,0)-k0, R.ACT.filter(a=>a.bot && (a.p.y<-.5 || Math.abs(a.p.x)>25 || Math.abs(a.p.z)>25)).length];
                R.me.resp=0; MG.step(.05,false); return out; }""", k)
            ok(r[0]>=4 and r[1]>=2 and r[2]==0, f"③ {k}: 봇이 길 찾아 다니며 싸움 (움직인 봇 {r[0]} · 흠뻑 {r[1]} · 밖으로 나감 {r[2]})")
            await A.evaluate("""()=>{ const R=MG.run, me=R.me; R.ACT.forEach(a=>{ if(a.bot){ a.alive=true; a.prot=0; a.brain.think=99; a.G.visible=true; } }); me.alive=true; me.soak=0; const s=R.SPAWN[0]; me.p.set(s[0],0,s[1]); me.yaw=Math.atan2(s[0],s[1]); me.pitch=-.08; }""")
            await A.wait_for_timeout(1300); await A.screenshot(path=OUT+f"arena599_play_{k}.png")
            await A.evaluate("()=>MG.run.time.over=true")
            await A.evaluate("()=>{ document.getElementById('mgRes') && document.getElementById('mgRes').classList.remove('on'); }")
            await A.evaluate("()=>MG.run.menuUI && 0")
            await A.evaluate("()=>{ const a=document.querySelector('#mgUI .aPzB'); a.click(); document.querySelector('#mgUI .aCard [data-go=menu]').click(); }"); await A.wait_for_timeout(500)
        allerr+=eA
        # ── 패드 세로
        cV,V,eV=await boot(br, 820, 1180, True)
        await V.evaluate("()=>MG.enter('arena',{})"); await V.wait_for_timeout(2000)
        r=await V.evaluate("()=>{ const s=document.querySelector('#mgUI .aSide').getBoundingClientRect(); return [s.bottom<=innerHeight+1, s.top>innerHeight*.35]; }")
        ok(r==[True,True], f"① 패드 세로: 메뉴는 아래 · 캐릭터는 위 {r}")
        await V.screenshot(path=OUT+"arena599_menu_portrait.png")
        await V.evaluate("()=>document.querySelector('#mgUI .aSide [data-c=set]').click()"); await V.wait_for_timeout(300)
        await V.screenshot(path=OUT+"arena599_set_portrait.png")
        allerr+=eV
        await br.close()
    ok(not allerr, f"오류 없음 {allerr[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__=="__main__": asyncio.run(main())
