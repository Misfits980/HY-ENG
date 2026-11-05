"""(v600) 사용자: 「단어랑 뜻·문장이 같이 나올 때 소리 안 듣고 넘겨 버림」 → 먼저 기록부터
   ① 오늘의 30 새 단어 카드: 본 장 수 · 소리가 끝날 만큼 본 장 수 · 한 장 평균 초 → 시트 줄(cn · cf · cs)
   ② 같은 카드를 다시 그려도 두 번 세지 않음 · 문제 화면은 세지 않음
   ③ 🏝 마이타운 시간: 화면이 보이는 동안만 그날 합계에 더함 · 숨은 시간은 안 셈 · 5분마다/숨을 때 시트로 (type mt)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":820,"height":1180})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("""()=>{ window._subs=[]; Online.on=()=>true; Online.submit=o=>window._subs.push(o);
            const real=Date.now.bind(Date); window._dt=0; Date.now=()=>real()+window._dt;
            StudyUI.open(); StudyUI.book='g34'; StudyUI.set='g34'; StudyUI.path(); StudyUI.start(0,false); }""")
        await pg.wait_for_timeout(300)
        # 처음 만나는 새 단어 카드 3장: 0.4초 · 8초 · 2초 보고 넘김 (문장 있는 카드는 소리 끝 ≈ 5~7초)
        seen=[]; waits=[0.4, 8, 2]
        for _ in range(80):
            q=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q ? [q.t, q.hd||'', !!q.use, (q.ws||[]).length, StudyUI._cd ? +StudyUI._cd.need.toFixed(1) : 0] : null; }")
            if not q: break
            if q[0]=="intro" and not q[1] and len(seen)<3:
                w=waits[len(seen)]; seen.append([w, q[4]])
                if len(seen)==2: await pg.evaluate("()=>{ StudyUI.show(); }")   # 같은 카드를 다시 그림 (두 번 세면 안 됨)
                await pg.evaluate("(s)=>{ window._dt+=s*1000; }", w)
            r=await pg.evaluate(SOLVE, False)
            if r=="none": break
            await pg.wait_for_timeout(30)
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
        await pg.wait_for_timeout(400)
        sub=await pg.evaluate("()=>window._subs.filter(o=>/^study/.test(o.rule||'')).slice(-1)[0]||null")
        n_intro=await pg.evaluate("()=>StudyUI.qs.filter(q=>q.t==='intro' && !q.hd).length")
        print("cards", seen, "intro", n_intro, "sub", {k:sub.get(k) for k in ("cn","cf","cs","set")} if sub else None)
        exp_full=sum(1 for w,need in seen if w>=need)
        ok(sub is not None and sub.get("cn")==n_intro, f"① 새 단어 카드 수 = 이 판 카드 {n_intro}장 (같은 카드 다시 그려도 한 번) · 보낸 값 {sub and sub.get('cn')}")
        ok(sub is not None and sub.get("cf",-1)>=exp_full and sub.get("cf")<=n_intro and len(seen)==3 and seen[0][0]<seen[0][1], f"① 끝까지 본 카드 · 0.4초에 넘긴 건 안 셈 {seen} → {sub and sub.get('cf')}")
        ok(sub is not None and 0<sub.get("cs",0)<20, f"① 한 장 평균 초 {sub and sub.get('cs')}")
        ok(not real_errs(errs), f"오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    # ③ 마이타운 시간 (house.html)
    os.environ["HY_REAL3D"]="1"
    from fakefb import fake
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True); pg=await ctx.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        posts=[]
        async def sheet(r):
            if r.request.method=="POST": posts.append(json.loads(r.request.post_data or "{}"))
            await r.fulfill(status=200, body='{"ok":true}', content_type="application/json")
        await pg.route("**/*", fake); await pg.route("https://script.google.com/**", sheet)
        await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_dev','devRUA1'); localStorage.setItem('hyeng_tag','0021'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.removeItem('hyeng_mt_sec'); }")
        await pg.reload(); await pg.wait_for_timeout(2400)
        r=await pg.evaluate("""()=>{ const H=HOUSE, M=H.MTL; M.force=true; M.id=null; M.a=0; M.last=0; H.MTS.at=0; H.MTS.sent='';
            const real=Date.now.bind(Date); window._dt=0; Date.now=()=>real()+window._dt; const id=H.mtId(); const step=(ms,fin)=>{ window._dt+=ms; H.mtLog(!!fin); };
            H.mtLog(true); for(let i=0;i<12;i++) step(60000);            // 12분 놀기 (1분마다)
            const a=JSON.parse(localStorage.getItem('hyeng_mt_sec'))[id];
            step(1000, true); M.a=0;                                        // 화면 숨김 → 끝
            window._dt+=40*60000;                                           // 40분 숨어 있음 (안 셈)
            step(0, true); for(let i=0;i<3;i++) step(60000);               // 다시 3분
            step(1000, true);
            const b=JSON.parse(localStorage.getItem('hyeng_mt_sec'))[id]; return [id, +(a.s/60).toFixed(1), a.g, +(b.s/60).toFixed(1), b.g]; }""")
        ok(r[0] and abs(r[1]-12)<.2 and abs(r[3]-15)<.3 and r[4]==2, f"③ 보이는 동안만 셈: 12분 → 숨은 40분 빼고 15분 · 들어온 번 2 {r}")
        await pg.wait_for_timeout(500)
        mt=[x for x in posts if x.get("type")=="mt"]
        ok(len(mt)>=2 and mt[-1].get("min")==r[3] and mt[-1].get("segs")==2 and mt[-1].get("dev")=="devRUA1" and mt[-1].get("tag")=="0021" and mt[-1].get("key")=="HYENG" and mt[-1].get("nick")=="루아" and len(mt[-1].get("day",""))==10,
           f"③ 시트로 보냄 (그날 합계 · 기기 · 태그 · 이름 · 날짜) {mt[-1] if mt else None} · {len(mt)}번")
        n0=len(mt)
        await pg.evaluate("()=>{ window._dt+=60000; HOUSE.mtLog(false); window._dt+=60000; HOUSE.mtLog(false); }"); await pg.wait_for_timeout(300)
        ok(len([x for x in posts if x.get("type")=="mt"])==n0, "③ 5분이 안 지났으면 1분마다 보내지 않음")
        ok(not real_errs(errs), f"오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__=="__main__": asyncio.run(main())
