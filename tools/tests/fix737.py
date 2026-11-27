"""(v737) 사용자 사진(아이폰 관리 화면) + 데일리 30 새 단어 카드
   ① 새 단어 카드: Stage 뜻이 첫 뜻이 아니면(fair = 박람회, 축제) 도감 비슷한 말·반대말(just 공정한 · unfair) 안 보임 · 첫 뜻이면 그대로
   ② 🤔 짐작해 봐요: science fair 문장에 「대회」(contest) 뜻 보기가 안 나옴 · 보기 3개
   ③ 관리 화면 휴대폰: 맨 위 바 그림자 없음 · 끝에서 더 끌어도 안 튕김(overscroll-behavior) · 열려 있는 동안 뒤 화면 스크롤 막힘 · 닫으면 풀림 · 옆 넘침 없음"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch()
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(1200)
        r=await pg.evaluate("""async ()=>{ try{ Voice.speak=()=>{}; }catch(e){} loadBex(); loadTalk(); for(let k=0;k<60 && (Object.keys(BEX).length<500 || Object.keys(TALK).length<500);k++) await new Promise(r=>setTimeout(r,100));
          const set='g56'; const s=Study.load(); s.book=Study.bookOf(set); s.set=set; Study.save(); StudyUI.open(); StudyUI.book=Study.bookOf(set); StudyUI.set=set; await new Promise(r=>setTimeout(r,400));
          const L=Study.lessons(set), i=L.findIndex(x=>Study.stageNo(set,x.n)==='6-1'); const out={card:[], grp:[], guess:[], gn:0};
          for(let rep=0; rep<6; rep++){ StudyUI.start(i,false); await new Promise(r=>setTimeout(r,200)); const U=StudyUI;
            for(let k=0;k<U.qs.length;k++){ const q=U.qs[k];
              if(q.t==='intro' && !q.hd && q.w && q.w.en==='fair'){ U.i=k; U.locked=false; U.show(); await new Promise(r=>setTimeout(r,80)); out.card.push(document.getElementById('stQ').innerText.replace(/\\s+/g,' ')); }
              if(q.t==='intro' && q.hd==='grp'){ (q.x.rows||[]).forEach(r=>{ if(r[0]==='fair') out.grp.push(r.join(' ')); }); }
              if(q.t==='intro' && q.hd==='guess' && q.w.en==='fair'){ out.gn++; out.guess.push((q.x.sent||'')+' | '+q.opts.join(' / ')); } } }
          /* 첫 뜻이면 비슷한 말이 그대로 나오는지 — 같은 함수로 */
          const W=(en)=>Study.word ? Study.word(en) : null;
          out.rel=[Study.relSense({en:'fair', ko:'박람회, 축제'}, 'just (공정한)'), Study.relSense({en:'fair', ko:'공정한'}, 'just (공정한)'), Study.relSense({en:'fair', ko:'공정한'}, 'unfair (불공평한)', true)];
          return out; }""")
        ok(len(r["card"])>=3 and all("just" not in t and "공정한" not in t for t in r["card"]), f"① fair(박람회) 새 단어 카드에 just(공정한) 없음 {[t[:80] for t in r['card'][:2]]}")
        ok(all("unfair" not in t and "just" not in t for t in r["grp"]), f"① 묶어서 기억해요에도 다른 뜻 짝 없음 {r['grp'][:3]}")
        ok(r["rel"]==[False, True, True], f"① 첫 뜻(공정한)이면 비슷한 말·반대말 그대로 {r['rel']}")
        ok(r["gn"]>=3 and all("대회" not in g for g in r["guess"]) and all(len(g.split(' | ')[1].split(' / '))==3 for g in r["guess"]), f"② 짐작해 봐요 보기에 대회 없음 · 보기 3개 {r['guess'][:3]}")
        await ctx.close()
        # ③ 관리 화면 휴대폰
        os.environ["HY_ADM_PH"]="1"
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T=await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e)))
        await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        pre=await T.evaluate("()=>[getComputedStyle(document.documentElement).overflowY, getComputedStyle(document.body).overflowY]")
        await T.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); Admin._tab('today'); }"); await T.wait_for_timeout(1500)
        m=await T.evaluate("""()=>{ const sc=document.querySelector('#shAdmin .sheetIn'), top=document.querySelector('#shAdmin .adTop'), cs=getComputedStyle(sc);
          return {ph:document.getElementById('shAdmin').classList.contains('adPh'), osb:cs.overscrollBehaviorY, sh:getComputedStyle(top).boxShadow, ho:getComputedStyle(document.documentElement).overflowY, bo:getComputedStyle(document.body).overflowY, nb:!!sc._nb,
            sx:document.documentElement.scrollWidth-innerWidth, ix:sc.scrollWidth-sc.clientWidth}; }""")
        ok(m["ph"] and m["sh"]=="none", f"③ 휴대폰 관리 화면 · 맨 위 바 그림자 없음 {m['sh']}")
        ok(m["osb"]=="none" and m["nb"], f"③ 끝에서 더 끌어도 안 튕김 (overscroll none · 옛 사파리 손 막기) {m['osb']} {m['nb']}")
        ok(m["ho"]=="hidden" and m["bo"]=="hidden", f"③ 열려 있는 동안 뒤 화면 스크롤 막힘 {m['ho']} {m['bo']}")
        ok(m["sx"]<=0 and m["ix"]<=0, f"③ 옆 넘침 없음 {m['sx']} {m['ix']}")
        # 맨 아래에서 위로 끌기 = 막힘 · 가운데에선 그대로
        await T.evaluate("()=>{ const f=document.createElement('div'); f.id='fill737'; f.style.height='2400px'; document.getElementById('adBody').appendChild(f); }"); await T.wait_for_timeout(200)
        r=await T.evaluate("""()=>{ const sc=document.querySelector('#shAdmin .sheetIn'); const mk=(y0,y1)=>{ const t0=new Touch({identifier:1,target:sc,clientX:200,clientY:y0}), t1=new Touch({identifier:1,target:sc,clientX:200,clientY:y1});
            sc.dispatchEvent(new TouchEvent('touchstart',{touches:[t0],bubbles:true,cancelable:true})); const e=new TouchEvent('touchmove',{touches:[t1],bubbles:true,cancelable:true}); sc.dispatchEvent(e); return e.defaultPrevented; };
          sc.scrollTop=sc.scrollHeight; const atEnd=mk(600,400); sc.scrollTop=Math.max(1,(sc.scrollHeight-sc.clientHeight)/2); const mid=mk(600,400); sc.scrollTop=0; const atTop=mk(300,500); return [atEnd, mid, atTop, sc.scrollHeight>sc.clientHeight]; }""")
        ok(r[3] and r[0] and not r[1] and r[2], f"③ 끝·맨 위에서 더 끌기만 막고 가운데 스크롤은 그대로 {r}")
        await T.evaluate("()=>{ document.querySelector('#shAdmin .adHead button[data-ad=close], #adClose, #shAdmin .adX') ? 0 : 0; Admin.close ? Admin.close() : document.getElementById('shAdmin').classList.remove('on'); }"); await T.wait_for_timeout(300)
        r=await T.evaluate("()=>[document.getElementById('shAdmin').classList.contains('on'), getComputedStyle(document.documentElement).overflowY, getComputedStyle(document.body).overflowY]")
        ok(r[0] is False and r[1:]==pre, f"③ 닫으면 뒤 화면 스크롤 원래대로 {r} (열기 전 {pre})")
        await br.close()
    print("오류", real_errs(errs)[:4])
    if real_errs(errs): bad.append("errors")
    print("BAD: %d" % len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
