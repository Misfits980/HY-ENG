"""(v385) 미리 만든 발음 파일(audio/*.mp3): 파일이 있는 단어는 웹오디오로 틀고(읽기 엔진 안 씀) · 아이폰도 달리는 중 기본으로 읽음
  · 파일이 없는 말(문장)은 예전 방식 · 파일 받기 실패하면 예전 방식(아이폰 달리는 중엔 조용히)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

IPH = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mobile/15E148 Safari/604.1) AppleWebKit/605.1.15 Version/18.0"
SPY = "()=>{ window._said=[]; window._clip=0; const f=Voice.speak.bind(Voice); Voice.speak=function(t){ window._said.push(String(t)); return f.apply(this, arguments); }; Voice.broken=false; Voice.on=true; SFX.wake(); const cb=SFX.ctx.createBufferSource.bind(SFX.ctx); SFX.ctx.createBufferSource=function(){ const s=cb(); const st=s.start.bind(s); s.start=function(){ if(s.buffer && s.buffer.duration>0.1 && s.buffer.duration<4) window._clip++; return st.apply(this, arguments); }; return s; }; }"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    lst = json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "audio", "list.json")))
    ok(len(lst) == 3620 and len(set(lst)) == 3620, "목록 3,620개 · 겹침 없음")
    ok(all(os.path.exists(os.path.join(os.path.dirname(__file__), "..", "..", "audio", k + ".mp3")) for k in lst), "목록의 파일이 모두 있음")
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, user_agent=IPH)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.wait_for_timeout(800)
        ok(await pg.evaluate("()=>Voice.clipSet && Voice.clipSet.size") == 3620, "화면이 목록을 읽음")
        ok(await pg.evaluate("()=>[Voice.slug('Eiffel Tower'), Voice.slug('medium-rare'), Voice.slug('yo-yo'), Voice.hasClip('Monday'), Voice.hasClip('apple'), Voice.hasClip('What is your name?')]") == ["eiffel_tower", "medium_rare", "yo_yo", True, True, False], "이름 규칙 · 단어는 있음 · 문장은 없음")
        ok(await pg.evaluate("()=>RunVoice.ios() && RunVoice.on()"), "아이폰: 달리는 중 읽기가 기본 켜짐 (파일이 있으니)")
        await pg.evaluate(SPY)
        await pg.evaluate("()=>{ Voice.say('apple'); }"); await pg.wait_for_timeout(1200)
        r = await pg.evaluate("()=>[window._said, window._clip]")
        ok(r[0] == [] and r[1] == 1, f"단어는 파일로 틀고 읽기 엔진은 안 씀 {r}")
        await pg.evaluate("()=>{ Voice.say('How are you today?'); }"); await pg.wait_for_timeout(300)
        ok(len(await pg.evaluate("()=>window._said")) == 1, "문장은 예전 방식으로 읽음")
        # 달리는 중
        await pg.evaluate("()=>{ window._said=[]; window._clip=0; const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; G.dir='e2k'; startGame(); }")
        try: await pg.wait_for_function("()=>window._clip>=1 || window._said.length>0", timeout=4000)   # (v390) 첫 문 단어가 나올 때까지 (1.5초 고정은 가끔 모자람)
        except Exception: pass
        r = await pg.evaluate("()=>[window._said, window._clip]")
        ok(r[0] == [] and r[1] >= 1, f"아이폰 달리기: 읽기 엔진 없이 파일로 읽음 {r}")
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(300)
        # 파일 받기 실패 → 아이폰 달리기 중엔 조용 · 판 밖에서는 예전 방식
        await pg.route("**/audio/*.mp3", lambda r: r.abort())
        await pg.evaluate("()=>{ Voice._bufs.clear(); window._said=[]; window._clip=0; Voice.say('banana'); }"); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("()=>window._said") == ["banana"], "파일을 못 받으면 예전 방식으로 읽음")
        await pg.evaluate("()=>{ Voice._bufs.clear(); window._said=[]; G.running=true; Voice.say('grape'); }"); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("()=>window._said") == [], "아이폰 달리는 중에 못 받으면 조용 (멈춤 방지)")
        await pg.evaluate("()=>{ G.running=false; }")
        # 서비스워커
        sw = open(os.path.join(os.path.dirname(__file__), "..", "..", "sw.js"), encoding="utf-8").read()
        ok("hyeng-audio-v1" in sw and "hyAudio" in sw and "./audio/list.json" in sw and "k !== AUDIO" in sw, "서비스워커: 발음 캐시 따로 · 업데이트에도 남김 · 목록 저장")
        ok(not errs, f"스크립트 오류 없음 {errs[:2]}")
        await br.close()
    print("\nFAIL" if bad else "\nALL OK", bad)
    sys.exit(1 if bad else 0)
asyncio.run(main())
