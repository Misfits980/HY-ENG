"""(v336) 공격 기회 +n 을 받고 바로 보스 화면을 열면 서버 더하기가 끝나기 전에 읽어 옛 값(0)으로 덮던 것
   — 서버가 늦게(옛 값으로) 답해도 이 기기에서 방금 쌓은 기회가 남아야 한다. 1분 지나면 서버 값을 그대로 믿는다."""
import asyncio, sys, os
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
        await pg.evaluate("""()=>{ localStorage.setItem('hyeng_nick','한양패드'); return FB.set('/hy/roster',{t:{},k:{k1:{n:'민준'}}}).then(()=>HyBoss.setup({on:true,team:false,split:'eq',restart:true})).then(()=>{ Kid.set({id:'k1',n:'민준',t:'all'}); return HyBoss.refresh(true); }); }""")
        await pg.wait_for_timeout(300)
        # 서버 사진(더하기 전) 을 찍어 두고, 기회 +2 → 서버가 옛 사진으로 답하게 해서 다시 읽기
        r = await pg.evaluate("""()=>{ const bid=HyBoss.B.id; return FB.get('/hy/dmg/'+bid).then(old=>{ const n=HyBoss.earn(Kid.get(), 'run', 2), a=HyBoss.stock('k1');
            const g=FB.get; FB.get=(path,s)=> path==='/hy/dmg/'+bid ? Promise.resolve(JSON.parse(JSON.stringify(old||{}))) : g(path,s);
            return HyBoss.refresh(true).then(()=>{ const b=HyBoss.stock('k1'); FB.get=g; return [n, a.r, b.r]; }); }); }""")
        print("earn/stock", r)
        ok(r == [2, 2, 2], f"늦게 온 옛 값에도 기회 그대로 {r}")
        # 공격으로 하나 쓴 뒤에도 (ur) 옛 값이 덮지 않음
        r = await pg.evaluate("""()=>{ const bid=HyBoss.B.id; return FB.get('/hy/dmg/'+bid).then(old=>{ HyBoss.use(Kid.get()); const a=HyBoss.stock('k1');
            const g=FB.get; FB.get=(path,s)=> path==='/hy/dmg/'+bid ? Promise.resolve(old) : g(path,s);
            return HyBoss.refresh(true).then(()=>{ const b=HyBoss.stock('k1'); FB.get=g; return [a.r, b.r]; }); }); }""")
        ok(r == [1, 1], f"쓴 뒤 옛 값에도 1 그대로 {r}")
        # 1분 지나면 서버 값을 믿음 (다른 기기에서 쓴 것 반영)
        r = await pg.evaluate("""()=>{ HyBoss._myT.k1=Date.now()-61000; const bid=HyBoss.B.id; return FB.update('/hy/dmg/'+bid+'/k1', {ur:2}).then(()=>HyBoss.refresh(true)).then(()=>HyBoss.stock('k1').r); }""")
        ok(r == 0, f"1분 뒤엔 서버 값 (다른 기기에서 하나 더 씀) {r}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
