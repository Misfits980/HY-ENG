"""(v681) 사용자: 「초등은 기준점 다잡았나?」 → 「이번에 싹 다 만들어 보자」 — 초등 문법 문제 기준점
   ① 예문 기준: 초3-4 9단어 · 초5-6 10단어 · 현재완료·수동태·관계사절·since·가정법 빼기 (tired·closed·born 같은 말은 괜찮음) · 중등은 그대로
   ② G3-4 · G5-6 Daily 30 문법 빈칸(진행형·조동사·위치·이어 주는 말·비교·시제·전치사)이 모두 기준 안
   ③ 전치사: 초3-4 at·on·in 만 · 초5-6 + for (보기 for·at·on) · during·since 는 중등
   ④ 🔼 초5-6 도전(G3-4 책) = G5-6 문법 코스 직접 쓴 고르기 · 앞 Stage = 앞 단원 · 뒤 Stage = 뒤 단원
   ⑤ 🔼 중등 도전(G5-6 책) = 중등 문제 은행 쉬운 것(lv0) · 동명사·to부정사 → 완료·수동 → 관계대명사·접속사 · 12단어 안
   ⑥ 문법 노트: 기간(for·since)은 중등"""
import asyncio, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 1280, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Study.hsqLoad(); Gram.load(); }"); await pg.wait_for_timeout(5000)
        C = [("We have studied Korean history for two years.", "g56", False), ("The bookstore was closed on Sunday.", "g56", True), ("English is spoken in many countries.", "g56", False),
             ("A man who plays the violin is my uncle.", "g56", False), ("I was born in 2015.", "g34", True), ("If I were a bird, I would fly.", "g56", False),
             ("I have lived here since 2020.", "g56", False), ("I am excited about the trip.", "g34", True), ("My class visited the zoo last week.", "g56", True),
             ("Mina finished her art project at midnight last night and felt proud.", "g56", False), ("Mina finished her art project at midnight last night and felt proud.", "mid", True),
             ("The children are playing in the park now.", "g34", True), ("I usually finish all my homework before dinner on weekdays.", "g34", False), ("I usually finish my homework before dinner on weekdays.", "g34", True)]
        r = await E("(C)=>C.map(c=>Study._el(c[0], c[1]))", [[a, b] for a, b, _ in C])
        wrong = [(C[i][0], C[i][1], r[i]) for i in range(len(C)) if r[i] != C[i][2]]
        ok(not wrong, f"① 예문 기준 {len(C)}가지 {wrong[:3]}")
        r = await E("""()=>{ const W=s=>(s.match(/[A-Za-z0-9][A-Za-z0-9'’.-]*/g)||[]).length, out={g34:[0,0,[],{}], g56:[0,0,[],{}]}, S=q=>q && q.st ? ((q.st.pre||'')+q.ans+(q.st.post||'')).replace(/\\s+/g,' ').trim() : null;
            for(const [set, gr, T] of [['elem','g34',['gx','gx','gx']], ['g56','g56',['tense','prep','gx','gx','gx']], ['rd2','g56',['tense','prep','gx','gx']]]){ const L=Study.lessons(set);
              L.forEach(les=>{ if(les.fin) return; const own=les.ws.map(w=>w.en); les.ws.forEach(w=>T.forEach(t=>{ let q=null; try{ q=Study.paperQ(t, w.en, set, own); }catch(e){} const s=S(q); if(!s) return; const o=out[gr]; o[0]++;
                if(!Study._el(s, gr)) { o[1]++; if(o[2].length<3) o[2].push(s); } if(t==='prep') (q.opts||[]).forEach(x=>o[3][x.toLowerCase()]=1); })); }); }
            return out; }""")
        ok(r["g34"][0] > 50 and r["g56"][0] > 400 and r["g34"][1] == 0 and r["g56"][1] == 0, f"② Daily 30 문법 빈칸 기준 밖 0 — G3-4 {r['g34'][:2]} {r['g34'][2]} · G5-6 {r['g56'][:2]} {r['g56'][2]}")
        p34 = sorted(r["g34"][3]); p56 = sorted(r["g56"][3])
        ok(set(p34) <= {"at", "on", "in"} and set(p56) <= {"at", "on", "in", "for"} and "during" not in p56 and "since" not in p56, f"③ 전치사 보기 G3-4 {p34} · G5-6 {p56}")
        r = await E("""()=>{ const L=Study.lessons('elem'), live=L.map((x,i)=>[x,i]).filter(a=>!a[0].fin), U=Gram.list('g56').slice().sort((a,b)=>(a.at|0)-(b.at|0)).map(g=>g.id), out=[];
            live.forEach(([x,i],k)=>{ const q=Study._up('elem', i, 3); out.push([k/live.length, q ? q.upNm : null, q && q.x ? q.x.gid : null, q ? q.opts.indexOf(q.ans)>=0 : false, q ? U.indexOf(q.x.gid) : -1]); }); return {out, n:U.length}; }""")
        O = r["out"]; got = [x for x in O if x[2]]; n = r["n"]
        early = [x[4] for x in O if x[0] < 0.3 and x[2]]; late = [x[4] for x in O if x[0] > 0.7 and x[2]]
        ok(len(got) == len(O) and all(x[1] == "초5-6" and x[3] for x in got) and early and late and max(early) < 4 and min(late) >= 8, f"④ 초5-6 도전 {len(got)}/{len(O)} · G5-6 문법 코스 · 앞 단원 {sorted(set(early))} · 뒤 단원 {sorted(set(late))}")
        r = await E("""()=>fetch('data/hsq.json').then(r=>r.json()).then(H=>{ const out=[]; for(const set of ['g56','rd1']){ const L=Study.lessons(set), live=L.map((x,i)=>[x,i]).filter(a=>!a[0].fin);
            live.forEach(([x,i],k)=>{ const q=Study._up(set, i, 3); const s=q && q.st ? (q.st.pre+q.ans+q.st.post) : ''; const h=q ? H.find(y=>y.s===q.st.pre+'___'+q.st.post && y.k===q.x.hk) : null;
              out.push([k/live.length, q ? q.upNm : null, h ? h.k : null, h ? h.lv : null, (s.match(/[A-Za-z0-9][A-Za-z0-9'’.-]*/g)||[]).length]); }); } return out; })""")
        got = [x for x in r if x[2]]; e = set(x[2] for x in r if x[0] < 0.3 and x[2]); l = set(x[2] for x in r if x[0] > 0.7 and x[2])
        ok(len(got) >= len(r) * 0.95 and all(x[1] == "중등" and x[3] == 0 and x[4] <= 12 for x in got) and e <= {"ger", "inf"} and l <= {"rel", "conj", "pass", "perf"},
           f"⑤ 중등 도전 {len(got)}/{len(r)} · 은행 lv0 · 12단어 안 · 앞 {sorted(e)} · 뒤 {sorted(l)}")
        r = await E("()=>[GNote.LV[1][1].indexOf('dur'), GNote.LV[2][1].indexOf('dur')]")
        ok(r[0] < 0 and r[1] >= 0, f"⑥ 문법 노트 기간(for·since) = 중등 {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
