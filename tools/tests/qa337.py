"""(v337) QA v336 보고서 고친 것 — 💜 이어 하기(틀린 직후 닫기 · 새 문제 칸) · 문장 순서 다른 정답 · 주간 보스(처치 보상 · 오프라인 기회 · 공용 패드) ·
   📝 시험 이어 보기 · ⭕❌ 문법 · 선생님 열쇠 · 휴대폰 가로 첫 화면 · 3D 텍스처 누수"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

LES = """(dl)=>{ Voice.broken=false; Voice.noVoice=false; StudyUI.open(); const st='elem'; StudyUI.book=Study.bookOf(st); StudyUI.set=st;
  const L=Study.lessons(st), x=L[2], K=Study.key(st,x.n), s=Study.load(); x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[K]=dl+1; s.ck=s.ck||{}; s.ck[K]=1; s.dp=s.dp||{}; s.dp[K]=1; s.dg={d:Study.today(), n:0}; Study.save();
  StudyUI.start(2, false); return StudyUI.qs.length; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.wait_for_timeout(800)

        # ① 💜3 틀린 직후 닫기 → 다시 열면 틀린 것 그대로 · 그 문제는 지나감
        await pg.evaluate(LES, 3)
        r = await pg.evaluate("""()=>{ const U=StudyUI; let i=U.qs.findIndex((q,k)=>k>0 && q.t!=='intro'); U.i=i; U.locked=false; U.show(); U.sel=-1; U.result(false);
            const before={i:U.i, wrong:U.wrong}; U._out=0; clearTimeout(U._adv); clearTimeout(U._outT);
            U.qs=[]; U.i=0; U.wrong=0;   /* 새로고침 흉내 */
            const okR=U.resume(); return {okR, before, after:{i:U.i, wrong:U.wrong}}; }""")
        print("resume after wrong", r)
        ok(r["okR"] and r["after"]["wrong"] == r["before"]["wrong"] and r["after"]["wrong"] >= 1 and r["after"]["i"] == r["before"]["i"] + 1, "💜 틀린 직후 닫기 → 오답 그대로 · 다음 문제부터")

        # ② 새 💜 문제(⭕❌ · 🔍) 이어 하기에서 안 깨짐
        for want, dl in (("oxs", 1), ("err", 3)):
            found = None
            for li in range(12):
                f = await pg.evaluate("""([want,dl,li])=>{ Voice.broken=false; const st=want==='err'?'g56':'elem'; StudyUI.open(); StudyUI.book=Study.bookOf(st); StudyUI.set=st; const L=Study.lessons(st).filter(y=>!y.fin), x=L[li%L.length], K=Study.key(st,x.n), s=Study.load();
                    x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[K]=dl+1; s.ck=s.ck||{}; s.ck[K]=1; s.dp=s.dp||{}; s.dp[K]=1; s.dg={d:Study.today(), n:0}; Study.save(); StudyUI.start(Study.lessons(st).indexOf(x), false);
                    const i=StudyUI.qs.findIndex(q=>want==='err' ? q.err : q.t==='oxs'); if(i<0) return null; StudyUI.i=i; StudyUI.locked=false; StudyUI.show();
                    const h0=document.getElementById('stQ').innerText; StudyUI.qs=[]; StudyUI.resume(); return [h0, document.getElementById('stQ').innerText, StudyUI.qs[StudyUI.i].t]; }""", [want, dl, li])
                if f: found = f; break
            print(want, found and found[1][:80].replace("\n", " / "))
            ok(found and "undefined" not in found[1] and found[0] == found[1], f"이어 하기 {want} 화면 그대로")

        # ③ 문장 만들기 — 다른 순서도 정답
        r = await pg.evaluate("""()=>{ const O=(f,g)=>StudyUI.odOk({full:f}, g); return [
            O('I like sweet and warm milk.', 'I like warm and sweet milk'), O('On hot days, we swim in the pool.', 'we swim in the pool on hot days'),
            O('I play soccer today.', 'today I play soccer'), O('Yesterday I went to the park.', 'I went to the park yesterday'),
            O('I play soccer today.', 'soccer play I today'), O('I like sweet and warm milk.', 'I like milk sweet and warm')]; }""")
        print("order alts", r)
        ok(r == [True, True, True, True, False, False], "문장 순서: and 바꾸기 · 앞 구 옮기기 · 시간 말 앞뒤 = 정답, 틀린 순서는 오답")

        # ④ ⭕❌ — 관사·한정사·고유명사가 깨진 문장 없음
        r = await pg.evaluate("""()=>{ const bad=[]; let n=0; for(const st of ['basic','elem','g56']) for(const x of Study.lessons(st)) for(const w of x.ws){ let q=null; try{ q=Study._oxs(w.en, st); }catch(e){} if(!q || q.truth) continue; n++;
            const d=q.dw.en, prev=(q.st.pre.trim().split(/\\s+/).pop()||'').toLowerCase();
            if((prev==='a'||prev==='an') && ((/^[aeiou]/.test(d)?'an':'a')!==prev)) bad.push(q.sent);
            if(isProper(w.en)!==isProper(d)) bad.push(q.sent); } return [n, bad.slice(0,5), bad.length]; }""")
        print("oxs", r)
        ok(r[0] > 100 and r[2] == 0, f"⭕❌ 바꾼 문장 {r[0]}개 · 관사/고유명사 깨짐 {r[2]}")

        # ⑤ 주간 보스 — 보스 → 🧪 → 다른 보스: 처치 보상 남음 · 새 칸
        await pg.evaluate("""()=>{ HyBoss.live(); localStorage.setItem('hyeng_nick','민준폰'); return FB.set('/hy/roster',{t:{},k:{k1:{n:'민준'},k2:{n:'서연'}}}).then(()=>HyBoss.setup({on:true,team:false,split:'eq',restart:true})); }""")
        await pg.wait_for_timeout(400)
        r = await pg.evaluate("""()=>{ Kid.set({id:'k1',n:'민준',t:'all',pk:Date.now()}); HyBoss.CAP=1e9; const me=Kid.get(); const b=HyBoss.B, id0=b.id;
            HyBoss.earn(me,'study',30); HyBoss.add(me, b.max.all+10, 'study'); HyBoss.markDead(b, 'all', '민준');
            return HyBoss.testWeek(true).then(()=>HyBoss.pickWeek(3)).then(()=>({id0, id:HyBoss.B.id, dead0:!!((HyBoss.C.dead||{})[id0]||{}).all, old:(HyBoss.O||[]).map(o=>o.id), hp:HyBoss.state('all').hp, max:HyBoss.B.max.all})); }""")
        print("boss reuse", r)
        ok(r["id"] != r["id0"] and r["dead0"] and r["id0"] in r["old"] and r["hp"] == r["max"], "보스→🧪→다른 보스: 새 칸 · 옛 처치 기록·보상 그대로 · 새 보스 체력 가득")

        # ⑥ 오프라인 — 못 보낸 쓰기가 남아 있으면 1분이 지나도 이 기기 값 유지
        r = await pg.evaluate("""()=>{ const B=HyBoss.B.id; HyBoss._myT={k1:Date.now()-5*60000}; HyBoss._mtB=B; HyBoss.D=Object.assign({}, HyBoss.D, {k1:{er:9, ur:7, n:'민준'}});
            const keep=FB.pending; FB.pending=()=>1; const a=HyBoss.keepMine({k1:{er:9, ur:3}}, B).k1.ur; FB.pending=()=>0; const b=HyBoss.keepMine({k1:{er:9, ur:3}}, B).k1.ur; FB.pending=keep; return [a,b]; }""")
        print("pending keep", r)
        ok(r == [7, 3], "못 보낸 쓰기가 있으면 쓴 기회 유지 (없으면 서버 값)")

        # ⑦ 공용 패드 — 보스 화면을 열 때 3분 넘었으면 '민준 맞아요?' (한 번 '네' 했어도)
        r = await pg.evaluate("""()=>{ try{ KidPick.close(); }catch(e){} localStorage.setItem('hyeng_nick','한양패드'); Kid.set({id:'k1',n:'민준',t:'all',pk:Date.now()-10*60000, ok:1, okAt:Date.now()-10*60000});
            WeekBoss.open(); const ask=!!document.getElementById('kidAsk'), open0=WeekBoss.isOpen(); const y=document.querySelector('#kidAsk [data-ka=y]'); if(y) y.click();
            const open1=WeekBoss.isOpen(); WeekBoss.close(); WeekBoss.open(); const ask2=!!document.getElementById('kidAsk'); WeekBoss.close(); localStorage.setItem('hyeng_nick','민준폰'); return [ask, open0, open1, ask2]; }""")
        print("shared pad", r)
        ok(r == [True, False, True, False], "공용 패드: 보스 화면 열 때 이름 확인 → 네 → 열림 · 바로 다시 열면 안 물음")

        # ⑧ 📝 시험 — 새로고침해도 그 자리부터 (푼 답 그대로)
        r = await pg.evaluate("""()=>{ const ws=[].concat(...Study.lessons('elem').slice(0,3).map(x=>x.ws.map(w=>w.en))).slice(0,12); const c={id:'ex1', set:'elem', ws, title:'테스트'}, me={id:'k1', n:'민준', t:'all'};
            const U=StudyUI; if(!U.exam(c, me)) return 'no exam'; let i=U.qs.findIndex(q=>q.t!=='intro'); U.i=i; U.locked=false; U.show(); U.sel=-1; U.result(false);
            const n0=U.qs.filter(q=>q._r!=null).length, i0=U.i; U.tStop && U.tStop(); clearTimeout(U._adv); U.qs=[]; U.ex=null;
            const okR=U.exResume('ex1','k1'); const keep=U.qs.filter(q=>q._r===0).length; const r=[okR, n0, keep, U.i>i0, !!U.ex, document.getElementById('stQ').innerText.indexOf('undefined')<0];
            U.tStop && U.tStop(); U.exClear(); return r; }""")
        print("exam resume", r)
        ok(r == [True, 1, 1, True, True, True], "시험 이어 보기: 틀린 답 그대로 · 다음 문제부터")

        # ⑨ 선생님 열쇠 — 새 열쇠는 PIN 과 상관없는 긴 값 · 옮기기(백업)에 안 들어감
        r = await pg.evaluate("""()=>{ localStorage.setItem('hyeng_admin_key', 'ab'.repeat(24)); const keys=[]; for(let i=0;i<localStorage.length;i++) keys.push(localStorage.key(i)); localStorage.removeItem('hyeng_admin_key'); return keys.indexOf('hyeng_admin_key')>=0; }""")
        ok(r, "열쇠 저장 칸")
        src = open(os.path.join(SITE, "index.html"), encoding="utf8").read()
        ok('k!=="hyeng_admin_key") out.push(k)' in src and 'k!=="hyeng_admin_key" && typeof o.data[k]' in src, "선생님 열쇠는 옮기기·백업에서 빠짐")

        e = real_errs(errs); print("errs", e[:3]); ok(not e, "오류 없음")
        await ctx.close()

        # ⑩ 휴대폰 가로 — 「이어서 하기」가 전체화면 버튼·톱니와 안 겹침 · PC 가로 첫 화면 스크롤 없음
        for w, h, mob in [(568, 320, True), (640, 360, True), (780, 360, True), (1366, 657, False), (1180, 820, False)]:
            c2 = await br.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob); p2 = await c2.new_page(); await boot(p2)
            r = await p2.evaluate("""()=>{ localStorage.setItem('hyeng_last_kind','study'); show('scStart'); refreshResume();
                const R=e=>{ if(!e) return null; const s=getComputedStyle(e); if(s.display==='none') return null; const r=e.getBoundingClientRect(); return r.width?r:null; }, hit=(a,b)=>a&&b&&a.left<b.right&&b.left<a.right&&a.top<b.bottom&&b.top<a.bottom;
                const fs=R(document.getElementById('btnFsHome')), gear=R(document.querySelector('#scStart .gearBtn')), bad=[];
                document.querySelectorAll('#scStart .mitem, #scStart .dmBtn').forEach(e=>{ const r=R(e); if(!r) return; if(hit(r,fs)||hit(r,gear)) bad.push(e.id||e.className); });
                const sc=document.getElementById('scStart'); return [bad, sc.scrollHeight-sc.clientHeight]; }""")
            ok(not r[0] and (mob or r[1] <= 2), f"첫 화면 {w}×{h}: 겹침 {r[0]} · 넘침 {r[1]}px")
            await c2.close()
        await br.close()

    # ⑪ 3D 텍스처 누수 — 진짜 엔진으로 판 4번 (판마다 늘지 않아야)
    os.environ["HY_REAL3D"] = "1"
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
            pg = await br.new_page(viewport={"width": 800, "height": 600}); await boot(pg); await pg.wait_for_timeout(1500)
            n = []
            for k in range(4):
                await pg.evaluate("()=>{ G.set='basic'; G.lesson=0; G.rule='normal'; G.diff='normal'; startGame(); }"); await pg.wait_for_timeout(2500)
                n.append(await pg.evaluate("()=>renderer.info.memory.textures"))
                await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; G.running=false; try{ gameOver(); }catch(e){} G.skipOutro=false; show('scStart'); }"); await pg.wait_for_timeout(600)
            print("textures", n)
            ok(n[-1] - n[1] <= 1, f"텍스처 수가 판마다 늘지 않음 {n}")
            await br.close()
    finally:
        os.environ.pop("HY_REAL3D", None)
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
