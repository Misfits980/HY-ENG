"""(v351) 사용자: 두 패드가 둘 다 1등 · 공용 패드에서 시험이 안 나옴 · 레이스 대결도 시험 기준 형태로
  ① 배틀 끝 순위 — 한 패드의 실시간 점수가 옛것이어도 끝나면 서버 점수로 (둘 다 1등 없음) · 선생님 TV 가 st.fin 순위를 써 둠
  ② 공용 패드: 앞 아이(다른 반) 이름이 남아 있어도 열린 시험이 보임 · 누르면 이름 다시 고르기 · 개인 기기는 우리 반 시험만
  ③ 📝 시험처럼 배틀: 모든 책에서 올림피아드 문제(A·B·C) · 정답이 보기에 · 화면에 코드 글 없음 · 문제마다 시간이 지나면 틀린 것으로 다음 문제"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

ROSTER = "()=>FB.set('/hy/roster', {t:{a:{n:'초등반'}, b:{n:'중등반'}}, k:{k1:{n:'민준',t:'a'}, k2:{n:'서연',t:'b'}, k3:{n:'하준',t:'a'}}})"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1180, "height": 820})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate(ROSTER); await T.evaluate("()=>{ window.confirm=()=>true; return HyBoss.refresh(true); }")
        K = await ctx.new_page(); await K.set_viewport_size({"width": 390, "height": 844}); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate("()=>{ window.confirm=()=>true; return HyBoss.refresh(true); }")

        # ① 배틀 끝 순위
        await T.evaluate("""()=>FB.set('/battle/7777', {cfg:{set:'elem', from:0, to:2, words:[], dur:300, qt:['mean'], lvl:'easy', made:Date.now()}, st:{s:'run', t0:Date.now()-5000},
            p:{k1:{n:'민준', sc:50, ok:5, ng:0, at:Date.now()}, k2:{n:'서연', sc:80, ok:8, ng:0, at:Date.now()}}})""")
        await K.evaluate("()=>{ Battle.join('7777', {id:'k1', n:'민준', t:'a'}); }"); await K.wait_for_timeout(1200)
        # 이 패드의 실시간 연결이 멈춘 것처럼 — 서연 점수가 옛것(30)
        await K.evaluate("""()=>{ const h=Battle.h, g=h.get.bind(h); h.get=()=>{ const t=JSON.parse(JSON.stringify(g()||{})); if(t.p && t.p.k2) t.p.k2.sc=30; return t; }; Battle.ok=5; Battle.sc=50; }""")
        r = await K.evaluate("()=>Battle.rank()[0]")
        ok(r == "k1", f"(멈춘 연결) 끝나기 전엔 이 패드가 자기가 1등이라고 봄 {r}")
        await T.evaluate("()=>{ Battle.reopen('7777'); }"); await T.wait_for_timeout(500)
        await T.evaluate("()=>FB.update('/battle/7777/st', {s:'end', endAt:Battle.now()})")
        await K.evaluate("()=>FB.update('/battle/7777/st', {s:'end', endAt:Date.now()})")
        await K.wait_for_timeout(4500)
        r = await K.evaluate("()=>[Battle.ended, Battle.rank().indexOf('k1')+1, document.querySelector('.rdEndT') && document.querySelector('.rdEndT').innerText, Battle._gems]")
        print("kid end", r)
        ok(r[0] and r[1] == 2 and "2등" in (r[2] or "") and r[3] == 3, f"끝나면 서버 점수로 — 민준 2등 · 💎3 {r}")
        fin = await T.evaluate("()=>FB.get('/battle/7777/st').then(s=>s && s.fin && s.fin.r)")
        ok(fin == ["k2", "k1"], f"선생님 TV 가 끝 순위를 써 둠 {fin}")
        # 한 판 더 → fin 지워짐 · 아이 화면 새 판
        await T.evaluate("()=>Battle.hostAct('again')"); await T.wait_for_timeout(1500)
        st = await T.evaluate("()=>FB.get('/battle/7777/st')")
        ok(st and st.get("s") == "wait" and not st.get("fin"), f"한 판 더: 끝 순위 지움 {st}")
        await K.wait_for_timeout(800)
        r = await K.evaluate("()=>[Battle.ended, Battle._finP]")
        ok(r == [False, None], f"아이 패드도 새 판 {r}")
        await T.evaluate("()=>{ Battle.role=null; clearInterval(Battle.t); if(Battle.h) Battle.h.close(); Battle.h=null; }")
        await K.evaluate("()=>{ Battle.role=null; clearInterval(Battle.t); if(Battle.h) Battle.h.close(); Battle.h=null; Battle._last=null; Battle._finP=null; show('scStart'); }")

        # ② 공용 패드 시험 — 중등반(b) 시험만 열림 · 패드에는 앞 아이(초등반 민준) 이름이 남아 있음
        await T.evaluate("""()=>{ const id='ex351'; return FB.set('/hy/exam/open/'+id, {id, on:1, st:'run', mode:'open', until:Date.now()+3600000, team:'b', set:'elem', from:0, to:3, n:12, title:'중등반 시험', at:Date.now()}); }""")
        await K.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드'); Kid.set({id:'k1',n:'민준',t:'a'}); show('scStart'); }")
        r = await K.evaluate("()=>HyExam.check(true).then(()=>{ HyExam.paint(); const b=document.getElementById('exChip'); return [HyExam.c && HyExam.c.team, !!b && !b.hidden]; })")
        ok(r == ["b", True], f"공용 패드: 다른 반 이름이 남아 있어도 시험이 보임 {r}")
        await K.evaluate("()=>{ const a=document.getElementById('exAsk'); if(a) a.remove(); HyExam.go(); }"); await K.wait_for_timeout(500)
        r = await K.evaluate("()=>[!!document.getElementById('kidPick'), Kid.get()]")
        ok(r[0] and r[1] is None, f"누르면 이름 다시 고르기 {r}")
        await K.evaluate("()=>{ try{ KidPick.close(); }catch(e){} }")
        # 개인 기기(공용 아님) — 다른 반 시험은 안 보임
        await K.evaluate("()=>{ localStorage.setItem('hyeng_nick','민준이'); Kid.set({id:'k1',n:'민준',t:'a'}); }")
        r = await K.evaluate("()=>HyExam.check(true).then(()=>{ HyExam.paint(); return HyExam.c && HyExam.c.team; })")
        ok(r is None, f"개인 기기: 다른 반 시험은 안 보임 {r}")
        # 첫 화면으로 돌아오면 바로 칩 (서버를 다시 읽기 전에도)
        await K.evaluate("()=>{ Kid.set({id:'k2',n:'서연',t:'b'}); HyExam._at=Date.now(); show('scStart'); }"); await K.wait_for_timeout(3500)
        r = await K.evaluate("()=>{ const b=document.getElementById('exChip'); return !!b && !b.hidden; }")
        ok(r, f"3초 안에 시험 칩 (다시 읽기 기다리지 않음) {r}")
        await T.evaluate("()=>FB.set('/hy/exam/open/ex351', null)")

        # ③ 📝 시험처럼 배틀 — 모든 책
        await K.evaluate("()=>HyExam.ready()")
        r = await K.evaluate("""()=>{ const out={n:0, t:{}, ab:{}, bad:[], code:[], err:[]}; const sets=[].concat(...Object.keys(Study.BOOKS).filter(k=>k!=="ph").map(k=>Study.BOOKS[k].sets));
            Battle.role='kid'; Battle.room='9999'; Battle.me='k1'; Battle.pick={id:'k1', n:'민준'}; Battle.h=null; Battle.screen();
            sets.forEach(set=>{ let L=[]; try{ L=Study.lessons(set); }catch(e){ return; }
              for(let a=0;a<L.length;a+=6){ Battle._ws=null; Battle._eq=null; Battle.q=null; Battle._last={cfg:{set, from:a, to:Math.min(L.length-1,a+2), qt:['mean'], lvl:'exam', dur:300}, st:{s:'run', t0:Date.now()-1000}, p:{}};
                for(let r=0;r<8;r++){ let q; try{ q=Battle.mkQ(); }catch(e){ out.err.push([set,String(e)]); break; } out.n++; out.t[q.t]=(out.t[q.t]||0)+1; if(q.ab) out.ab[q.ab]=(out.ab[q.ab]||0)+1;
                  if(!q.exq || !q.opts.some(o=>o.en===q.w.en)) out.bad.push([set,q.t,q.w.en]);
                  if(r<2){ Battle.q=q; Battle.qAt=Date.now(); Battle.draw(); const tx=document.getElementById('rdIn').innerText; if(/<img|undefined|null/.test(tx)) out.code.push([set,q.t,q.w.en]); } } } });
            Battle.q=null; return out; }""")
        print("exam battle", r["n"], r["t"], r["ab"], r["bad"][:3], r["code"][:3], r["err"][:2])
        ok(r["n"] > 400 and not r["bad"] and not r["code"] and not r["err"], f"시험처럼 문제 {r['n']}개: 정답 없음 {len(r['bad'])} · 코드 글 {len(r['code'])} · 오류 {len(r['err'])}")
        ok(all(r["t"].get(t, 0) > 0 for t in ["opic", "k2e", "talk", "sent", "sent2"]) and set(r["ab"]) == {"A", "B", "C"}, f"문제 종류 A·B·C 다 나옴 {r['t']}")
        # 사용자: 예문 식 문제가 안 나옴 → 문장 문제(대화·문장 빈칸)가 반 이상
        r = await K.evaluate("""()=>{ const out={}; ['elem','g56','mid','basic'].forEach(set=>{ Battle._ws=null; Battle._eq=null; Battle.q=null; Battle._last={cfg:{set, from:0, to:3, qt:['mean'], lvl:'exam', dur:300}, st:{s:'run', t0:Date.now()-1000}, p:{}};
            let n=0, sn=0; for(let i=0;i<60;i++){ const q=Battle.mkQ(); Battle.q=q; n++; if(['talk','sent','sent2'].indexOf(q.t)>=0) sn++; } out[set]=Math.round(sn/n*100); }); Battle.q=null; return out; }""")
        ok(all(v >= 50 for v in r.values()), f"문장 문제 비율 % {r}")
        # 화면: 대화 빈칸 + 시간 막대 · 시간이 지나면 틀린 것 → 다음 문제
        await K.evaluate("()=>{ Battle._ws=null; Battle._eq=null; Battle.q=null; Battle._last={cfg:{set:'elem', from:0, to:5, qt:['mean'], lvl:'exam', dur:300}, st:{s:'run', t0:Date.now()-1000}, p:{k1:{n:'민준',sc:0}}}; Battle.ng=0; Battle.loop(); }")
        await K.wait_for_timeout(500)
        r = await K.evaluate("()=>{ const q=Battle.q; return [q && q.exq, q && q.sec, !!document.getElementById('btQTi')]; }")
        ok(r[0] and r[1] >= 5 and r[2], f"문제마다 시간 막대 {r}")
        talk = await K.evaluate("""()=>{ const q0=Battle._eq.find(q=>q.t==='talk'); if(!q0) return 'none'; Battle.q=Object.assign({}, q0, {exq:1, sec:q0.sec}); Battle.qAt=Battle.now(); Battle.draw();
            return [document.querySelectorAll('.stTalk p').length, document.querySelectorAll('#rdOpts .stOpt').length]; }""")
        ok(talk == "none" or (talk[0] == 2 and talk[1] >= 3), f"대화 빈칸 화면 {talk}")
        await K.screenshot(path=OUT + "race351_talk.png")
        await K.evaluate("()=>{ Battle.qAt=Battle.now()-Battle.q.sec*1000-100; }"); await K.wait_for_timeout(600)
        r = await K.evaluate("()=>[Battle.q.done, Battle.q.to, Battle.ng, document.querySelector('.rdRes.bad') && document.querySelector('.rdRes.bad').innerText.slice(0,20)]")
        ok(r[0] and r[1] and r[2] == 1 and "시간" in (r[3] or ""), f"시간이 지나면 틀린 것 {r}")
        q1 = await K.evaluate("()=>Battle.q.w.en"); await K.wait_for_timeout(1800)
        r = await K.evaluate("()=>[!Battle.q.done, Battle.q.exq]")
        ok(r == [True, 1], f"1.5초 뒤 다음 문제 {r}")
        await K.evaluate("()=>{ clearInterval(Battle.t); Battle.role=null; Battle.q=null; Battle._last=null; }")
        # 선생님 양식: 📝 시험처럼 기본 · cfg.lvl
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ window.confirm=()=>true; Admin.open(); }"); await T.wait_for_timeout(400)
        await T.evaluate("()=>{ const b=document.querySelector('#adTabs [data-t=\"play\"]'); if(b) b.click(); }"); await T.wait_for_timeout(600)
        lv = await T.evaluate("()=>{ const s=document.getElementById('adBtLvl'); return s ? s.value : null; }")
        ok(lv == "exam", f"배틀 만들기 기본 = 시험처럼 {lv}")
        await T.evaluate("()=>document.querySelector('[data-ad=\"btGo\"]').click()"); await T.wait_for_timeout(1500)
        c = await T.evaluate("()=>Battle.room && FB.get('/battle/'+Battle.room+'/cfg').then(c=>c && c.lvl)")
        ok(c == "exam", f"방 설정 lvl {c}")
        hd = await T.evaluate("()=>document.getElementById('rdA') && document.getElementById('rdA').innerText")
        ok("시험처럼" in (hd or ""), "TV 위에 「시험처럼」")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
