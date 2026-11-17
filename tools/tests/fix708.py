"""(v708) 사용자: 「따라쓰기 줄 쓰는 거에 g 나 y 가 공중에 떠 있는 경우가 있네」
   흐린 글씨 자리를 「빨간 줄 − .9em」 어림으로 잡던 것 → 쓰는 글꼴을 재서 밑선 = 빨간 줄 · 소문자 몸통 = 점선~빨간 줄
   ① 단어 따라쓰기 (첫 칸 흐린 글씨) · 변화형 작은 줄 · 문장 따라쓰기: 모든 흐린 글씨 밑선이 빨간 줄에서 ±0.12칸 안
   ② 소문자 몸통(x) 높이 = 점선~빨간 줄 칸의 0.9~1.15 · 머리(l) 가 맨 윗줄을 안 넘음 · 꼬리(g)가 맨 아랫줄을 안 넘음
   ③ 휴대폰 미리보기(transform)에서도 같음 · 글자 재기를 못 하면 예전 CSS 그대로(오류 없음)
   (v709) 흐린 글씨 = 학교 손글씨 글꼴 HY Trace (Edu SA Beginner · OFL · 똑바로 세움) — 꼬리가 맨 아랫줄 가까이"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

MEAS = r"""()=>{ const out=[]; const c=document.createElement('canvas').getContext('2d');
  document.querySelectorAll('#ppWrap .kjT').forEach(t=>{ if(!t.offsetParent) return; const s=t.closest('.kjStrip'); const R=e=>e.getBoundingClientRect();
    const z=R(s).height/Math.max(1,s.offsetHeight); const g1=R(s.querySelector('.g1')).top, g2=R(s.querySelector('.g2')).top, g3=R(s.querySelector('.g3')).top, g4=R(s.querySelector('.g4')).top, sp=(g3-g2);
    const m=document.createElement('span'); m.style.cssText='display:inline-block;width:0;height:0;vertical-align:baseline'; t.appendChild(m); const b=R(m).top; m.remove();
    const cs=getComputedStyle(t), fs=parseFloat(cs.fontSize)*z; c.font=cs.fontWeight+' '+fs+'px '+cs.fontFamily;
    const xh=c.measureText('x').actualBoundingBoxAscent, asc=c.measureText('l').actualBoundingBoxAscent, dsc=c.measureText('g').actualBoundingBoxDescent;
    out.push({t:t.textContent.slice(0,16), mini:s.classList.contains('kjMini'), off:(b-g3)/sp, xr:xh/sp, top:((b-asc)-g1)/sp, bot:(g4-(b+dsc))/sp, shrunk:!!t.style.fontSize}); });
  return out; }"""

async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for vw in (1280, 390):
            ctx=await br.new_context(viewport={"width":vw,"height":900}, is_mobile=vw<500, has_touch=vw<500); pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            await boot(pg); E=pg.evaluate
            await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({mode:'kw'}); }"); await pg.wait_for_timeout(3500)
            s=await E("()=>{ const L=Paper.psets().filter(s=>/5-6/.test(Study.label(s)) && /리딩 2/.test(Study.label(s))); return L[0]||Paper.psets()[0]; }")
            await E("(s)=>{ const S=document.getElementById('ppSet'); S.value=s; S.dispatchEvent(new Event('change',{bubbles:true})); }", s); await pg.wait_for_timeout(1500)
            await E("()=>{ const c=[...document.querySelectorAll('#paper input[type=checkbox]')].find(x=>/흐린/.test(x.parentNode.textContent) && x.offsetParent); if(c && !c.checked) c.click(); }"); await pg.wait_for_timeout(2500)
            info=await E("()=>Paper._kjInfo")
            ok(bool(info) and info.get("font")=="HY Trace" and 2.2 < info["F"] < 2.6 and 0.6 < info["B"] < 1.1 and info["dsc"]/info["xh"] > 0.75, f"{vw}px (v709) 흐린 글씨 = 손글씨 글꼴 HY Trace · 꼬리 긴 비율 {info}")
            r=await E("()=>{ const t=document.querySelector('#ppWrap .kjT'); return t ? [getComputedStyle(t).fontFamily.slice(0,12), document.fonts.check('600 20px \"HY Trace\"')] : null; }")
            ok(r and r[0].startswith('"HY Trace"') and r[1], f"{vw}px 글꼴 받음 {r}")
            for mode in ("kw", "ks"):
                if mode=="ks":
                    await E("()=>Paper.open({mode:'ks'})"); await pg.wait_for_timeout(2500)
                    await E("()=>{ const c=[...document.querySelectorAll('#paper input[type=checkbox]')].find(x=>/흐린/.test(x.parentNode.textContent) && x.offsetParent); if(c && !c.checked) c.click(); }"); await pg.wait_for_timeout(2500)
                L=await E(MEAS)
                gy=[x for x in L if any(ch in x["t"] for ch in "gyp")]
                far=[x for x in L if abs(x["off"])>0.12]
                ok(len(L)>=5 and len(gy)>=1 and not far, f"① {vw}px {mode}: 흐린 글씨 {len(L)}개 (g·y·p {len(gy)}) 밑선 = 빨간 줄 · 벗어남 {[(x['t'], round(x['off'],2)) for x in far[:4]]}")
                full=[x for x in L if not x["shrunk"]]
                xr=[x for x in full if not (0.9 <= x["xr"] <= 1.15)]
                tol = 0.06 if vw >= 1000 else 0.15   # 칸의 6% (줄 굵기 안쪽) · 휴대폰 미리보기는 0.46배로 줄여 그려 1px 반올림이 칸의 0.1 쯤
                over=[x for x in L if x["top"] < -tol or x["bot"] < -tol]
                ok(len(full)>=3 and not xr and not over, f"② {vw}px {mode}: 몸통 = 점선~빨간 줄 ({len(full)}개) · 윗줄/아랫줄 안 넘음 · 어긋남 {[(x['t'], round(x['xr'],2)) for x in xr[:3]]} 넘침 {[(x['t'], round(x['top'],2), round(x['bot'],2)) for x in over[:3]]}")
                mini=[x for x in L if x["mini"]]
                if mode=="kw": ok(len(mini)>=3, f"① {vw}px 변화형 작은 줄도 잼 {len(mini)}")
            await ctx.close()
        # ③ 글자 재기 못 하는 브라우저 = 예전 CSS (오류 없음)
        ctx=await br.new_context(viewport={"width":1280,"height":900}); pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await ctx.add_init_script("(()=>{ const o=CanvasRenderingContext2D.prototype.measureText; CanvasRenderingContext2D.prototype.measureText=function(s){ const m=o.call(this,s); return {width:m.width}; }; })()")
        await boot(pg); E=pg.evaluate
        await E("()=>{ try{ DexData.load(1); loadEasy(); }catch(e){} Paper.open({mode:'kw'}); }"); await pg.wait_for_timeout(3000)
        r=await E("()=>[!!document.getElementById('kjMet'), document.querySelectorAll('#ppWrap .kjB').length]")
        ok(r[0] is False and r[1] > 3, f"③ 못 재면 예전 CSS 그대로 · 종이는 나옴 {r}")
        await br.close()
    print("errs", errs[:3])
    print("BAD:", len(bad))
    sys.exit(1 if bad or errs else 0)
asyncio.run(main())
