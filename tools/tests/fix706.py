"""(v706) 크롬 둘러보기(그래픽 위화감·글자) + 사용자 아이폰 사진(따라쓰기 미리보기 아래 잘림)
   ① 시험지·따라쓰기 휴대폰 미리보기: zoom → transform (zoom 이면 최소 글씨 크기 때문에 카드가 길어져 쪽 아래 카드가 숨었음) · 넘침 0 · 가로 스크롤 없음 · 아래 빈 스크롤 없음
   ② 결과 「다시 볼 단어」 글꼴 = 게임 글꼴 (고정폭 X) · 「1스테이지」 → Stage
   ③ 첫 화면 뒤 문이 카메라를 뚫고 지나가지 않음 (5.5 앞에서 새 문)
   ④ 오늘의 코스 동그라미 = 제목 줄 안
   ⑤ 주간 보스 옆모습 무대: 친구 이름표끼리 안 겹침 · 무대 밖으로 안 나감
   ⑥ 스크롤 막대 색 · 상점 옷 「학자 옷 · 」"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

HID = r"""()=>{ const W=document.getElementById('ppWrap'); const out=[];
  [...W.querySelectorAll('.kjBody,.ppCol')].forEach((b,i)=>{ const br=b.getBoundingClientRect(); let mx=br.top; b.querySelectorAll('*').forEach(e=>{ const r=e.getBoundingClientRect(); if(r.height>0 && r.bottom>mx) mx=r.bottom; });
    const z=br.height/Math.max(1,b.clientHeight); const h=(mx-br.bottom)/z/(96/25.4); if(h>0.5 || b.scrollHeight>b.clientHeight+1) out.push([i, +h.toFixed(1)]); });
  const V=W.parentNode; return {zoom:W.style.zoom, tf:W.style.transform, pages:W.querySelectorAll('.pp').length, bad:out, ox:getComputedStyle(V).overflowX, extra:V.scrollHeight - (W.getBoundingClientRect().height + 30)}; }"""
NAMES = r"""()=>{ const L=[...document.querySelectorAll('#wbStage .rsName')].filter(n=>n.offsetParent).map(n=>{ const r=n.getBoundingClientRect(); return {t:n.textContent, l:r.left, r:r.right, t2:r.top, b:r.bottom}; });
  const S=document.getElementById('wbStage').getBoundingClientRect(); const ov=[]; for(let i=0;i<L.length;i++) for(let j=i+1;j<L.length;j++){ const a=L[i], b=L[j]; if(a.l<b.r && a.r>b.l && a.t2<b.b && a.b>b.t2) ov.push(a.t+'/'+b.t); }
  return {n:L.length, ov, out:L.filter(x=>x.t2<S.top-1 || x.b>S.bottom+1).map(x=>x.t)}; }"""

async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch()
        # ① 휴대폰 미리보기 (사용자 사진과 같은 범위: G5-6 리딩 2 · 12-1~12-4 · 20단어 · 학원용)
        for vw in (390, 600):
            ctx=await br.new_context(viewport={"width":vw,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True); pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            await boot(pg); E=pg.evaluate
            await E("()=>localStorage.setItem('hyeng_pp_ver','school')")
            await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({mode:'kw'}); }"); await pg.wait_for_timeout(4000)
            s=await E("()=>{ const L=Paper.psets().filter(s=>/5-6/.test(Study.label(s)) && /리딩 2/.test(Study.label(s))); return L[0]||Paper.psets()[0]; }")
            await E("(s)=>{ const S=document.getElementById('ppSet'); S.value=s; S.dispatchEvent(new Event('change',{bubbles:true})); }", s); await pg.wait_for_timeout(600)
            rng=await E("()=>{ const o=[...document.getElementById('ppFrom').options]; const f=o.find(x=>/^\s*12-1/.test(x.textContent)), t=o.find(x=>/^\s*12-4/.test(x.textContent)); return f&&t ? [f.value,t.value] : [o[0].value, o[Math.min(3,o.length-1)].value]; }")
            for mode in ("kw","ks","test"):
                await E("(m)=>Paper.open({mode:m})", mode); await pg.wait_for_timeout(1200)
                await E("(a)=>{ const [s,fr,to]=a, $=id=>document.getElementById(id), S=$('ppSet'); if(S.value!==s){ S.value=s; S.dispatchEvent(new Event('change',{bubbles:true})); } $('ppFrom').value=fr; $('ppTo').value=to; const n=$('ppN'); if(n) n.value='20'; Paper._kjMix=false; Paper.make(); }", [s]+rng)
                await pg.wait_for_timeout(5000)
                r=await E(HID)
                ok(r["zoom"]=="" and r["tf"].startswith("scale(") and not r["bad"] and r["ox"]=="hidden" and r["extra"]<40, f"① {vw}px {mode}: transform 맞춤 · 숨은 카드 없음 · 가로 스크롤 없음 · 아래 빈 스크롤 없음 {r}")
            await ctx.close()
        # 넓은 화면 = 맞춤 없음
        ctx=await br.new_context(viewport={"width":1280,"height":800}); pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await boot(pg); E=pg.evaluate
        await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({mode:'kw'}); }"); await pg.wait_for_timeout(3500)
        r=await E("()=>{ const W=document.getElementById('ppWrap'); return [W.style.zoom, W.style.transform, W.style.marginBottom, getComputedStyle(W.parentNode).overflowX]; }")
        ok(r[0]=="" and r[1]=="" and r[2]=="", f"① 넓은 화면은 그대로 {r}")
        # print 모드에서 transform 이 꺼지는지 (CSS)
        css=await E("()=>[...document.styleSheets].flatMap(s=>{ try{ return [...s.cssRules]; }catch(e){ return []; } }).map(r=>r.cssText).filter(t=>/ppPrint \.ppWrap/.test(t)).join(' ')")
        ok("transform: none" in css, "① 인쇄 때는 transform 없음")
        await E("()=>Paper.close && Paper.close()")
        # ② 결과 글꼴 · Stage 말
        f=await E("()=>{ const d=document.createElement('div'); d.className='wcard'; d.innerHTML='<div class=txt><div class=en>STUDY</div></div>'; document.body.appendChild(d); const ff=getComputedStyle(d.querySelector('.en')).fontFamily; d.remove(); return ff; }")
        ok("monospace" not in f, f"② 다시 볼 단어 글꼴 {f}")
        src=open(os.path.join(SITE,"index.html"),encoding="utf-8").read()
        ok("스테이지 더 갔어요" not in src and "\"스테이지 — 다음엔" not in src and "단계까지 달리면" not in src and "→ 이번 Stage" in src, "② 결과 한 줄 = Stage")
        # ③ 첫 화면 문
        r=await E("()=>{ if(!Attract.set) Attract.spawn(); const g0=Attract.set.group; g0.position.z=camera.position.z-5.2; Attract.update(0.016); const a=Attract.set.group!==g0;  const g1=Attract.set.group; g1.position.z=camera.position.z-8; Attract.update(0.016); let op=1; g1.traverse(o=>{ if(o.material && !Array.isArray(o.material)) op=Math.min(op, o.material.opacity); }); return [a, Attract.set.group===g1, +op.toFixed(2)]; }")
        ok(r[0] and r[1] and r[2]<0.8, f"③ 카메라 5.5 앞이면 새 문 · 8 앞에선 흐려짐 {r}")
        # ④ 오늘의 코스 동그라미
        r=await E("()=>{ try{ Course.paint(); }catch(e){} const b=document.getElementById('crsBtn'); return b ? [!!b.querySelector('.tdL small .crsDots'), b.querySelectorAll('.crsDots').length] : null; }")
        ok(r is None or (r[0] and r[1]==1), f"④ 코스 동그라미 = 제목 줄 안 {r}")
        # ⑥ 스크롤 막대 · 상점 옷
        r=await E("()=>getComputedStyle(document.documentElement).scrollbarColor")
        ok(r and r!="auto", f"⑥ 스크롤 막대 색 {r}")
        ok("cname(o.ch)+' 옷 · '+o.note" in src, "⑥ 상점 옷 「학자 옷 · 」")
        await ctx.close()
        # ⑤ 주간 보스 이름표
        for vw,vh in ((1280,537),(894,585),(390,844)):
            ctx=await br.new_context(viewport={"width":vw,"height":vh}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
            await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }"""); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>{ WeekBoss.open(); }"); await pg.wait_for_timeout(1200)
            n=await pg.evaluate("()=>{ if(!RaidStage.el) return -1; RaidStage.allies({a:{n:'스트로베리',c:'hero'}, b:{n:'이무이무시완',c:'hero'}, c:{n:'김지후',c:'hero'}, d:{n:'유이홍',c:'hero'}}, null); return Object.keys(RaidStage.al).length; }")
            await pg.wait_for_timeout(700)
            r=await pg.evaluate(NAMES)
            ok(n>=3 and r["n"]>=3 and not r["ov"] and not r["out"], f"⑤ {vw}x{vh} 친구 이름표 안 겹침 {n} {r}")
            await ctx.close()
        await br.close()
    print("errs", errs[:3])
    print("BAD:", len(bad))
    sys.exit(1 if bad or errs else 0)
asyncio.run(main())
