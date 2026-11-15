"""(v680) 사용자: 「고등꺼는 중학교꺼로 살짝 수준 맞춰서」 — 문제 은행(data/hsq.json) 어법 심화 12가지의 lv2·lv3 168문제를 중학교 내신 수준으로
   ① lv2 120 · lv3 48 그대로 (번호 자리 그대로 → 본 문제 기록 유지) ② lv2 6~12단어 · lv3 9~16단어 · 과거완료 없음
   ③ lv3 (A)(B) 자리 · 보기 2개씩 · 틀린 이유 둘 다 ④ 화면: 심화 도전 (A)(B) 문제 48개 모두 보기 4개 · 정답 있음 · 틀린 조합마다 이유
   ⑤ 휴대폰에서 (A)(B) 문제 화면이 옆으로 넘치지 않음 ⑥ 중등 문법 코스(gram.json mid)의 ★ 고르기가 새 문제"""
import asyncio, sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
HS = ["part", "voice", "agree", "what", "reladv", "ifp", "verb2", "caus", "adj", "indq", "it", "paral"]

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    H = json.load(open(os.path.join(ROOT, "data", "hsq.json"), encoding="utf-8"))
    W = lambda s: len(re.findall(r"[A-Za-z'.]+", s))
    cnt = {k: (sum(1 for x in H if x["k"] == k and x["lv"] == 2), sum(1 for x in H if x["k"] == k and x["lv"] == 3)) for k in HS}
    ok(len(H) == 609 and all(v == (10, 4) for v in cnt.values()), f"① 609문제 · 주제마다 lv2 10 · lv3 4 {set(cnt.values())}")
    L2 = [x for x in H if x["lv"] == 2]; L3 = [x for x in H if x["lv"] == 3]
    n2 = [W(x["s"].replace("___", x["o"][0])) for x in L2]; n3 = [W(x["s"].replace("(A)___", x["A"][0]).replace("(B)___", x["B"][0])) for x in L3]
    pp = [x["s"] for x in L2 + L3 if re.search(r"\bhad (been|\w+ed|done|gone|seen|eaten|taken|written|known|made|lost|found|bought)\b", x["s"] + " " + " ".join(x.get("o") or x["A"] + x["B"]))]
    ok(max(n2) <= 12 and min(n2) >= 6 and max(n3) <= 16 and min(n3) >= 9 and not pp, f"② 길이 lv2 {min(n2)}~{max(n2)} (평균 {sum(n2)/len(n2):.1f}) · lv3 {min(n3)}~{max(n3)} · 과거완료 {pp[:2]}")
    b3 = [x["s"] for x in L3 if x["s"].count("(A)___") != 1 or x["s"].count("(B)___") != 1 or len(set(x["A"])) != 2 or len(set(x["B"])) != 2 or not x.get("wA") or not x.get("wB")]
    b2 = [x["s"] for x in L2 if x["s"].count("___") != 1 or len(set(x["o"])) != 3 or set((x.get("w") or {})) != set(x["o"][1:])]
    ok(not b3 and not b2, f"③ 자리·보기·틀린 이유 {b2[:2]} {b3[:2]}")
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        await E("()=>{ Study.hsqLoad(); Paper.open({set:'mid',from:0,to:3}); }"); await pg.wait_for_timeout(4000); await E("()=>Paper.close()")
        r = await E("""()=>fetch('data/hsq.json').then(r=>r.json()).then(H=>{ const L=Study.lessons('mv1'), li=L.map((x,i)=>[x,i]).filter(a=>!a[0].fin).pop()[1], out=[];
            H.forEach((x,i)=>{ if(x.lv!==3) return; const seen={}; H.forEach((y,j)=>{ if(j!==i) seen[j]=1; }); localStorage.setItem('hyeng_hsq_seen', JSON.stringify(seen));
              let q=null; for(let t=0;t<6 && !(q && q.x && q.x.sh);t++) q=Study._up('mv1', li, 3);
              const sh=q && q.x && q.x.sh || ''; out.push([i, !!q, (sh.match(/abBx/g)||[]).length, q ? q.opts.length : 0, q ? new Set(q.opts).size : 0, q ? q.opts.indexOf(q.ans)>=0 : false, q && q.x.wr ? Object.keys(q.x.wr).length : 0, q && q.ans===(x.A[0]+' – '+x.B[0])]); });
            localStorage.removeItem('hyeng_hsq_seen'); return out; })""")
        badq = [x for x in r if not (x[1] and x[2] == 2 and x[3] == 4 and x[4] == 4 and x[5] and x[6] == 3 and x[7])]
        ok(len(r) == 48 and not badq, f"④ 심화 도전 (A)(B) {len(r)}개 · 보기 4 · 정답 · 틀린 조합 이유 3 · 이상 {badq[:3]}")
        await E("()=>{ const v=GNote.st(); [].concat(...GNote.LV.map(x=>x[1])).forEach(k=>v.seen[k]=1); GNote.put(v); }")
        wide = []
        for i in [x[0] for x in r][::6]:
            w = await E("""(i)=>fetch('data/hsq.json').then(r=>r.json()).then(H=>{ const seen={}; H.forEach((y,j)=>{ if(j!==i) seen[j]=1; }); localStorage.setItem('hyeng_hsq_seen', JSON.stringify(seen));
                const L=Study.lessons('mv1'), li=L.map((x,k)=>[x,k]).filter(a=>!a[0].fin).pop()[1]; let q=null; for(let t=0;t<6 && !(q && q.x && q.x.sh);t++) q=Study._up('mv1', li, 3);
                try{ if(!StudyUI.qs || !StudyUI.qs.length){ Study.ctx('mv1'); StudyUI.open(); StudyUI.start(0,false); } }catch(e){}
                StudyUI.locked=false; StudyUI.qs.splice(StudyUI.i,0,q); StudyUI.show(); localStorage.removeItem('hyeng_hsq_seen');
                const d=document.documentElement; return [d.scrollWidth, innerWidth, [...document.querySelectorAll('.stOpt')].map(b=>b.getBoundingClientRect().right).reduce((a,b)=>Math.max(a,b),0), document.querySelectorAll('.abBx').length]; })""", i)
            if not (w[0] <= w[1] and w[2] <= w[1] + 1 and w[3] == 2): wide.append((i, w))
        await pg.wait_for_timeout(300); await pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "hsq680.png"))
        ok(not wide, f"⑤ 휴대폰 (A)(B) 화면 옆 넘침 없음 {wide[:2]}")
        G = json.load(open(os.path.join(ROOT, "data", "gram.json"), encoding="utf-8"))
        hd = [q["s"] for u in G["mid"] if u.get("gk") in HS for q in u["qs"] if q.get("hd")]; new2 = set(x["s"] for x in L2)
        ok(len(hd) == 120 and set(hd) == new2, f"⑥ 중등 문법 코스 ★ 고르기 {len(hd)}개 = 새 lv2")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
