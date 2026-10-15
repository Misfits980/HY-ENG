"""(v274) 소리 겹침 — 보기를 누르면(그 보기 읽기) 바로 정답을 또 읽어서, 80ms 미룬 말이 뒤늦게 같이 나오던 것 (headache 두 번·뭉개짐).
   가짜 speechSynthesis 로 실제로 '말한' 것만 센다: 연달아 부르면 마지막 말 하나만, 끊은 뒤 80ms 안에는 바로 말하지 않기."""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

FAKE = """(()=>{ const said=[]; window.__said=said; let cur=null, q=[], tEnd=null;
  const next=()=>{ cur=q.shift()||null; if(!cur) return; said.push({t:cur.text, at:Math.round(performance.now()), qt:cur.qt}); try{ cur.onstart&&cur.onstart({}); }catch(e){}
    tEnd=setTimeout(()=>{ const u=cur; cur=null; try{ u.onend&&u.onend({}); }catch(e){} next(); }, 300+String(u0(cur)).length*40); };
  const u0=u=>u?u.text:"";
  window.SpeechSynthesisUtterance=function(t){ this.text=t; };
  Object.defineProperty(window, 'speechSynthesis', {configurable:true, value:{ get speaking(){ return !!cur; }, get pending(){ return q.length>0; },
    speak(u){ if(!String(u.text).trim()) return; q.push(u); if(!cur) next(); },
    cancel(){ q=[]; clearTimeout(tEnd); if(cur){ const u=cur; cur=null; try{ u.onerror&&u.onerror({error:"interrupted"}); }catch(e){} } window.__cancelAt=performance.now(); },
    resume(){}, getVoices(){ return [{lang:"en-US", name:"fake", localService:true}]; }, onvoiceschanged:null }});
})();"""

async def main():
    bad = []
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script(FAKE)
        await boot(pg)
        # ① 말하는 중에 두 번 연달아 → 마지막 하나만
        r = await pg.evaluate("""async()=>{ __said.length=0; Voice.speak("apple"); await new Promise(r=>setTimeout(r,50));
            Voice.speak("headache"); Voice.speak("headache"); await new Promise(r=>setTimeout(r,900)); return __said.map(x=>x.t); }""")
        print("rapid", r)
        if r != ["apple", "headache"]: bad.append("연달아 부르기 %s" % r)
        # ② 보기 누르기(보기 읽기) → 바로 정답 읽기: 한 번만
        r = await pg.evaluate("""async()=>{ await new Promise(r=>setTimeout(r,600)); __said.length=0; Voice.speak("headache");
            await new Promise(r=>setTimeout(r,100)); Voice.speak("fever"); Voice.speak("headache"); await new Promise(r=>setTimeout(r,1500)); return __said.map(x=>x.t); }""")
        print("option→answer", r)
        if r != ["headache", "headache"]: bad.append("보기→정답 %s" % r)
        # ③ 끈 뒤(Voice.stop) 미뤄 둔 말이 나오지 않음
        r = await pg.evaluate("""async()=>{ await new Promise(r=>setTimeout(r,800)); __said.length=0; Voice.speak("one"); await new Promise(r=>setTimeout(r,30));
            Voice.speak("two"); Voice.stop(); await new Promise(r=>setTimeout(r,500)); return __said.map(x=>x.t); }""")
        print("stop", r)
        if r != ["one"]: bad.append("끈 뒤 %s" % r)
        # ④ 공부 화면: 문제를 풀 때 같은 말이 겹쳐 나오지 않음 (100ms 안에 같은 말 두 번 시작 없음)
        await pg.evaluate("""()=>{ StudyUI.open(); StudyUI.book='g56'; StudyUI.set='g56'; StudyUI.path(); __said.length=0; StudyUI.start(0,false);
            const o=Voice.speak.bind(Voice); Voice.speak=function(t,r,op){ window.__qt=(StudyUI.qs[StudyUI.i]||{}).t; return o(t,r,op); };
            const sh=StudyUI.show.bind(StudyUI); StudyUI.show=function(){ window.__shownAt=performance.now(); return sh(); }; window.__shownAt=performance.now();
            const sp=speechSynthesis.speak.bind(speechSynthesis); speechSynthesis.speak=u=>{ u.qt=window.__qt; return sp(u); }; }""")
        for k in range(30):   # 아이처럼 문제 소리를 듣고 나서 답한다 (봇이 0.1초 만에 답하면 문제 소리를 정답 소리가 끊는 건 정상)
            await pg.wait_for_function("()=>window.__shownAt && performance.now()-window.__shownAt>600", timeout=8000)
            await pg.evaluate(SOLVE, k % 4 == 1); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>__said")
        dup = [(a["t"], b["t"]) for a, b in zip(r, r[1:]) if b["at"] - a["at"] < 120 and "drag" not in (a.get("qt"), b.get("qt"))]   # 끌기는 테스트가 칩을 한꺼번에 놓아서 빼고 본다
        print("study said", len(r), "overlaps", dup[:5])
        for k,(a,b) in enumerate(zip(r, r[1:])):
            if b["at"]-a["at"]<120 and "drag" not in (a.get("qt"), b.get("qt")): print("  겹침 앞뒤", r[max(0,k-2):k+3])
        if dup: bad.append("공부 화면 겹침 %s" % dup[:3])
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        if bad: print("BAD", bad)
        await br.close()
asyncio.run(main())
