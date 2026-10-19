"""(v354) 사용자: 「📅 오늘 한 아이」에 안 나오는 아이 — 교실 배틀·레이드·시험만 한 아이는 기록이 없었다
  → 배틀 끝·레이드 끝·시험 제출 때 /hy/day/<날짜>/<고른 아이> 에 c(수업) +1 (cb 배틀 · cr 레이드 · ce 시험) · 공용 패드여도 그 판에서 고른 아이 이름
  · 선생님 카드에 🏫 수업 칸 · 같은 판은 한 번만 · 선생님 화면(레이드 TV)은 기록 안 함"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1180, "height": 820})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate("()=>FB.set('/hy/roster', {t:{a:{n:'초등반'}}, k:{k1:{n:'박유범',t:'a'}, k2:{n:'빈',t:'a'}, k3:{n:'서연',t:'a'}}}).then(()=>HyBoss.refresh(true))")
        # 공용 패드 — 패드에 남은 이름은 서연인데 배틀은 박유범으로 들어옴
        await K.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양 행복'); Kid.set({id:'k3', n:'서연', t:'a'}); }")
        await K.evaluate("""()=>FB.set('/battle/6464', {cfg:{set:'elem', from:0, to:2, words:[], dur:300, qt:['mean'], lvl:'easy', made:Date.now()}, st:{s:'run', t0:Date.now()-5000}, p:{k1:{n:'박유범', sc:30, ok:3, ng:1}}})""")
        await K.evaluate("()=>{ Battle.join('6464', {id:'k1', n:'박유범', t:'all'}); }"); await K.wait_for_timeout(1200)
        await K.evaluate("()=>{ Battle.ok=3; Battle.ng=1; Battle.sc=30; return FB.update('/battle/6464/st', {s:'end', endAt:Date.now()}); }"); await K.wait_for_timeout(3800)
        await K.evaluate("()=>{ Battle._finish(['k1']); }"); await K.wait_for_timeout(300)   # 두 번 불러도 한 번만
        d = await K.evaluate("()=>FB.get('/hy/day/'+HyDay.key())")
        print("day", d)
        ok(d and d.get("k1", {}).get("cb") == 1 and d["k1"].get("c") == 1 and d["k1"].get("n") == "박유범" and d["k1"].get("t") == "a" and d["k1"].get("lk") == "c", f"배틀 끝 → 박유범 (고른 아이 · 반 a) 수업 1 {d and d.get('k1')}")
        ok(not (d or {}).get("k3"), "패드에 남은 이름(서연)으로 기록되지 않음")
        await K.evaluate("()=>{ Battle.role=null; clearInterval(Battle.t); if(Battle.h) Battle.h.close(); Battle.h=null; }")
        # 레이드 끝 (아이)
        await K.evaluate("()=>{ Raid.role='kid'; Raid.room='7171'; Raid.pick={id:'k2', n:'빈', t:'a'}; Raid.me='k2'; Raid.hits=4; Raid.miss=1; Raid.blk=0; Raid.dmg=40; Raid.shk=0; Raid._dy=null; try{ Raid.finish(); }catch(e){ return String(e); } }")
        await K.evaluate("()=>{ Raid.ended=false; try{ Raid.finish(); }catch(e){} }"); await K.wait_for_timeout(400)
        d = await K.evaluate("()=>FB.get('/hy/day/'+HyDay.key()+'/k2')")
        ok(d and d.get("cr") == 1 and d.get("c") == 1 and d.get("n") == "빈", f"레이드 끝 → 빈 수업 1 (한 번만) {d}")
        # 선생님(레이드 TV)은 기록 안 함
        await K.evaluate("()=>{ Raid.role='host'; Raid.pick=null; Raid.room='7272'; Raid.hits=5; Raid._dy=null; try{ Raid.finish(); }catch(e){} Raid.role=null; }"); await K.wait_for_timeout(300)
        d = await K.evaluate("()=>FB.get('/hy/day/'+HyDay.key()).then(D=>Object.keys(D||{}))")
        ok(sorted(d) == ["k1", "k2"], f"선생님 화면은 기록 안 함 {d}")
        # 시험 제출
        await K.evaluate("""()=>{ const qs=[{t:'intro'},{t:'k2e', w:{en:'cat'}, _r:1},{t:'k2e', w:{en:'dog'}, _r:0}]; try{ HyExam.done({ex:{id:'exd1', kid:{id:'k3', n:'서연', t:'a'}}, qs, secs:()=>30, view(){}, path(){}}, true); }catch(e){} }""")
        await K.wait_for_timeout(400)
        d = await K.evaluate("()=>FB.get('/hy/day/'+HyDay.key()+'/k3')")
        ok(d and d.get("ce") == 1 and d.get("c") == 1, f"시험 제출 → 서연 수업 1 {d}")
        # 선생님 카드
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ window.confirm=()=>true; Admin.open(); }"); await T.wait_for_timeout(1500)
        r = await T.evaluate("()=>{ const t=document.querySelector('.dyT'); const h=t && t.closest('.adCard').querySelector('h3'); return t ? [h.innerText, [...t.querySelectorAll('tr')].map(x=>x.innerText.replace(/\\s+/g,' '))] : null; }")
        print("card", r)
        ok(r and "3명" in r[0] and "수업(배틀·레이드·시험) 3" in r[0], f"카드 위: 3명 · 수업 3 {r and r[0]}")
        ok(r and any("박유범" in x and "배틀" in x for x in r[1]) and any("빈" in x and "레이드" in x for x in r[1]) and any("서연" in x and "시험" in x for x in r[1]), "아이 줄에 배틀·레이드·시험")
        await T.screenshot(path=OUT + "day354.png")
        # 서버 규칙이 하루 기록을 막으면(401) — 비어 있을 때 써 보고 안내
        r = await T.evaluate("""()=>{ const f0=window.fetch, r0=FB.ready, b0=FB.base, g0=FB.get; window._calls=[];
            FB.ready=()=>Promise.resolve('fb'); FB.base=()=>'https://x.test'; FB.get=()=>Promise.resolve(null);
            window.fetch=(u,o)=>{ _calls.push([(o||{}).method||'GET', String(u)]); return Promise.resolve({ok:false, status:401}); };
            HyDay._pr=null; HyDay.D={}; return HyDay.load(HyDay.key()).then(()=>{ const h=HyDay.card(); window.fetch=f0; FB.ready=r0; FB.base=b0; FB.get=g0; HyDay._pr=null; return [HyDay.pst, h.indexOf('저장을 막고')>=0, _calls.map(c=>c[0]+' '+c[1].replace(/.*\/hy\//,'hy/'))]; }); }""")
        print("probe", r)
        ok(r[0] == "deny" and r[1] and any("_probe" in c for c in r[2]), f"규칙이 막으면 카드에 안내 {r}")
        r = await T.evaluate("""()=>{ const f0=window.fetch, r0=FB.ready, b0=FB.base, g0=FB.get; window._calls=[];
            FB.ready=()=>Promise.resolve('fb'); FB.base=()=>'https://x.test'; FB.get=()=>Promise.resolve(null);
            window.fetch=(u,o)=>{ _calls.push((o||{}).method||'GET'); return Promise.resolve({ok:true, status:200}); };
            HyDay._pr=null; HyDay.pst=null; HyDay.D={}; return HyDay.load(HyDay.key()).then(()=>{ const h=HyDay.card(); window.fetch=f0; FB.ready=r0; FB.base=b0; FB.get=g0; HyDay._pr=null; return [HyDay.pst, h.indexOf('저장을 막고')>=0, _calls]; }); }""")
        ok(r[0] == "ok" and not r[1] and r[2] == ["PUT", "DELETE"], f"규칙이 되면 써 보고 바로 지움 · 안내 없음 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
