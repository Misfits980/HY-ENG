# v626 ② 헷갈린 문법 먼저 섞기 + 간격 · ③ 듣고 푸는 문법 (⭕❌ 듣기)
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/learn626_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

PLAY = """async (wrongIds)=>{ const G=GramUI; let k=0;
  while(k++<300 && G.mode!=='end'){
    if(G.mode==='quiz'){ const q=G.qs[G.qi]; if(!q.res){ const w=wrongIds.indexOf(q.gid)>=0 && !q.again;
        if(q.k==='pick') G.pick(w ? q.opts.findIndex(o=>o!==q.a) : q.opts.indexOf(q.a)); else if(q.k==='ox') G.ox((q.ok!==w)?'o':'x');
        else if(q.k==='fix'){ const ts=q.s.split(' '); G.fixTap(w ? ts.findIndex(t=>t.replace(/[.,!?]/g,'')!==q.bad) : ts.findIndex(t=>t.replace(/[.,!?]/g,'')===q.bad)); }
        else { q.pickd=q.w.map((x,i)=>i); G.ochk(); } } G.qnext(); }
    else break; await new Promise(r=>setTimeout(r,10)); }
  return G.mode; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ Online.on=()=>false; return Gram.load(); }")
        # ② 순서: 섞기 날이 된 것 먼저 → 그중 많이 틀린 것 먼저
        r = await pg.evaluate("""()=>{ const D=864e5, now=Date.now(), T=[
            {id:'a', at:now-3*D, ml:0, acc:.9}, {id:'b', at:now-3*D, ml:0, acc:.3}, {id:'c', at:now-1*36e5, ml:2, acc:.1},
            {id:'d', at:0, ml:0, acc:.6}, {id:'e', at:now-5*D, ml:3, acc:.2}, {id:'f', at:now-8*D, ml:3, acc:.5}];
            return GramUI.mixOrder(T, now).map(t=>t.id).join(''); }""")
        ok(r == "bfda", f"섞기 순서 = 날 된 것 중 많이 틀린 것부터 (c 방금 · e 7일 안 됨 빠짐) {r}")
        r = await pg.evaluate("()=>[GramUI.mixDue({at:0},Date.now()), GramUI.mixDue({at:Date.now()-20*36e5, ml:0},Date.now()), GramUI.mixDue({at:Date.now()-20*36e5, ml:1},Date.now())]")
        ok(r == [True, True, False], f"간격: 처음 = 바로 · 0칸 = 하루 · 1칸 = 이틀 {r}")
        # 섞어 풀기 결과 → 간격 칸 (80% 넘으면 +1, 아니면 0)
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_gram_v1'); ['g34-1','g34-2','g34-3'].forEach(id=>Gram.put(id,{s:2, last:90})); }")
        await pg.evaluate("()=>GramUI.mixStart('g34')"); await pg.wait_for_timeout(800)
        r = await pg.evaluate("()=>GramUI.mixT.map(t=>t.id).sort().join(',')"); ok(r == "g34-1,g34-2,g34-3", f"섞기 문법 3개 {r}")
        m = await pg.evaluate(PLAY, ["g34-2"])
        r = await pg.evaluate("()=>['g34-1','g34-2','g34-3'].map(id=>{ const s=Gram.st(id); return [s.ml, s.mn>0, s.mo<=s.mn]; })")
        ok(m == "end" and r[0][0] == 1 and r[2][0] == 1 and r[1][0] == 0 and all(x[1] and x[2] for x in r), f"다 맞힌 문법 = 1칸 · 틀린 문법 = 0칸(내일) {m} {r}")
        t = await pg.evaluate("()=>document.querySelector('#stGram .grEndNx').textContent")
        ok("내일 또" in t, f"끝 화면에 「내일 또 섞어 줄게요」 {t}")
        await pg.screenshot(path=OUT + "mix_end.png")
        # 다음 날: 틀린 g34-2 가 먼저 · 많이 틀린 문법일수록 문제 많이
        await pg.evaluate("()=>{ const D=864e5; ['g34-1','g34-3'].forEach(id=>Gram.put(id,{mx:Date.now()-1.1*D})); Gram.put('g34-2',{mx:Date.now()-1.1*D}); Gram.put('g34-4',{s:1,last:100}); }")
        r = await pg.evaluate("""()=>GramUI.mixPool('g34').then(T=>{ const o=GramUI.mixOrder(T); return [o.map(t=>t.id), o.map(t=>+t.acc.toFixed(2))]; })""")
        ok(r[0][0] == "g34-2" and "g34-1" not in r[0][:1], f"틀린 문법이 다음 날 맨 앞 {r}")
        cnt = await pg.evaluate("""async ()=>{ const c={}; for(let i=0;i<12;i++){ GramUI.mixStart('g34'); await new Promise(z=>setTimeout(z,150)); GramUI.qs.forEach(q=>{ c[q.gid]=(c[q.gid]||0)+1; }); } return c; }""")
        ok(cnt.get("g34-2", 0) > cnt.get("g34-4", 0), f"많이 틀린 g34-2 문제가 다 맞힌 g34-4 보다 많이 {cnt}")
        # ③ 듣기: ★3 판 = ⭕❌ 2개 듣기
        await pg.evaluate("()=>{ Voice.broken=false; Voice.fails=0; Gram.put('g34-1',{s:2}); const s=Study.load(); s.book='g34'; s.set=Gram.MAIN.g34; Study.save(); StudyUI.open(); GramUI.start('g34-1'); }"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ if(GramUI.mode!=='quiz'){ GramUI.build(); GramUI.draw(); } }")
        r = await pg.evaluate("()=>({tier:GramUI.tier, ls:GramUI.qs.filter(q=>q.ls).length, ox:GramUI.qs.filter(q=>q.k==='ox').length, sup:Voice.supported()})")
        ok(r["tier"] == 3 and r["ls"] == min(2, r["ox"]) and r["ls"] >= 1, f"★3 듣기 문제 {r}")
        said = await pg.evaluate("""async ()=>{ const G=GramUI, i=G.qs.findIndex(q=>q.ls); G.qi=i; const L=[]; const o=Voice.speak; Voice.speak=(t)=>L.push(t); G.draw(); await new Promise(z=>setTimeout(z,700));
            const el=document.querySelector('#stGram'), q=G.qs[i], hid=!el.querySelector('.grS') && !!el.querySelector('.grLs') && el.textContent.indexOf(q.s)<0;
            const lbl=el.querySelector('.grQK').textContent; Voice.speak=o; return {L, s:q.s, hid, lbl}; }""")
        ok(said["L"] and said["L"][0] == said["s"] and said["hid"] and "듣고" in said["lbl"], f"듣기 = 글자 숨김 · 저절로 읽어 줌 {said}")
        await pg.screenshot(path=OUT + "listen_ph.png")
        r = await pg.evaluate("()=>{ document.querySelector('#stGram [data-gr=lstxt]').click(); const q=GramUI.cur(); return document.querySelector('#stGram .grS').textContent===q.s; }")
        ok(r, "「글자로 볼래요」 = 문장 보임")
        r = await pg.evaluate("()=>{ const G=GramUI, i=G.qs.findIndex((q,j)=>q.ls && j!==G.qi); if(i<0) return 'skip'; G.qi=i; G.draw(); const q=G.qs[i]; G.ox(q.ok?'o':'x'); return [q.res, document.querySelector('#stGram .grS.ls').textContent===q.s]; }")
        ok(r == "skip" or r == ["ok", True], f"듣기 답한 뒤 문장 보임 {r}")
        # 섞어 풀기에도 듣기 · 목소리 없는 기기는 듣기 없음
        r = await pg.evaluate("async ()=>{ Voice.broken=false; GramUI.mixStart('g34'); await new Promise(z=>setTimeout(z,300)); const a=GramUI.qs.filter(q=>q.ls).length; Voice.broken=true; GramUI.mixStart('g34'); await new Promise(z=>setTimeout(z,300)); const b2=GramUI.qs.filter(q=>q.ls).length; Voice.broken=false; return [a, b2, GramUI.qs.filter(q=>q.k==='ox').length]; }")
        ok(r[1] == 0 and (r[0] >= 1 or r[2] == 0), f"섞기 듣기 · 목소리 고장이면 없음 {r}")
        # 패드
        await pg.set_viewport_size({"width": 820, "height": 1180})
        await pg.evaluate("async ()=>{ Voice.broken=false; StudyUI.open(); for(let k=0;k<6;k++){ GramUI.mixStart('g34'); await new Promise(z=>setTimeout(z,200)); if(GramUI.qs.some(q=>q.ls)) break; } const G=GramUI; const i=G.qs.findIndex(q=>q.ls); if(i>=0){ G.qi=i; G.draw(); } }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT + "listen_pad.png")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
