"""(v698) 사용자: 「6번은 늘열림으로 … 나머지한번해줘봐」 — 연구 제안 ⑦ ③ ① ⑤
   ⑦ 🔥 연속 = 토·일이 비어도 안 끊김 (금 → 월 그대로 · 월요일을 빠지면 끊김)
   ③ 놀이 속 복습 = 달리기 문제에 내 복습 단어가 섞임 · 그날 처음 푼 결과만 「며칠 뒤 맞힘」 + 시트 줄 rvo/rvn · 오늘의 30·수업·틀린 단어 판에는 안 섞음
   ① 유치원·G1-2 새 단어 = 소리 조각 맞추기 (HY_SB=1) · 조각 소리는 사전 발음기호에서 (glue · said · they · circle · walk …) · 틀린 조각 = 흔들림만
   ⑤ 🤝 짝 퀘스트 = 랭킹 답 me.pq → 오늘의 30 지도 칩 · 창(둘의 Stage · 응원 3개 · 다 채우면 💎15 한 번) · 지난주 답 · 다른 아이 답 = 칩 없음
   ② 🧭 이야기 = 판 3개 통과마다 지도 칩 · 장면(교재·사전 예문 빈칸) · 그림(G1-4)/글자(G5-6) · 틀리면 「Hmm… not ○○」 · 💎2 한 번 (HY_STY=1)
   ④ 수업 게임 = 🎁 상자(+5 · 다음 정답 2배, HY_CHEST=1) · 빠름 +1 · 선생님 「어느 범위?」 하나가 레이스·배틀·레이드에 같이"""
import asyncio, sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright


async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    ME = {}; POSTS = []
    async def sheet(r):
        u = r.request.url
        if r.request.method == "POST":
            try: POSTS.append(json.loads(r.request.post_data or "{}"))
            except Exception: pass
            return await r.fulfill(status=200, content_type="application/json", body='{"ok":true}')
        if "board=1" in u:
            return await r.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "v": 25, "boards": {"study": [], "words": [], "run": []}, "me": ME}))
        return await r.fulfill(status=200, content_type="application/json", body='{"ok":true,"list":[]}')
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 820, "height": 1180})
        await ctx.add_init_script("window.HY_SB=1; window.HY_STY=1; window.HY_CHEST=1; localStorage.setItem('hyeng_nick','민준'); localStorage.setItem('hyeng_tag','0006');")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.route("https://script.google.com/**", sheet)
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1300)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ StudyUI.FAST=0; }catch(e){} ['helloMt','rkAnn'].forEach(i=>{ const d=document.getElementById(i); if(d) d.remove(); }); }")
        E = pg.evaluate

        # ── ⑦ 🔥 연속 — 주말
        r = await E("""()=>{ const t=Study.today(); let F=t; while(new Date(F*864e5).getUTCDay()!==5) F--;   // 지난 금요일
            const S=Study.load(); S.days={last:F, n:4, hs:6, hb:6}; Study.save();
            const o=[Study.streak(F), Study.streak(F+1), Study.streak(F+2), Study.streak(F+3), Study.streak(F+4)];
            S.days={last:F-2, n:1, hs:3}; Study.save(); o.push(Study.streak(F));   // 수 → 금 (목요일 빠짐)
            S.days={last:F-1, n:1, hs:3}; Study.save(); o.push(Study.streak(F+1));  // 목 → 토 (금요일 빠짐)
            S.days={}; Study.save(); return o; }""")
        ok(r[:5] == [6, 6, 6, 6, 0], f"⑦ 금요일까지 6일 → 토·일·월 6 그대로 · 화요일(월요일 빠짐) 0 {r[:5]}")
        ok(r[5] == 0 and r[6] == 0, f"⑦ 평일을 빠지면 끊김 {r[5:]}")

        # ── ③ 놀이 속 복습
        await E("""()=>{ const S=Study.load(), t=Study.today(); S.srs=S.srs||{}; ['tiger','orange','window'].forEach((en,i)=>{ S.srs[en]=[2, t-1]; }); S.rt={}; S.rtd={}; Study.save(); }""")
        due = await E("()=>Study.due(null).filter(en=>['tiger','orange','window'].indexOf(en)>=0).sort()")
        ok(len(due) >= 2, f"③ 준비: 복습할 단어 {due}")
        r = await E("""()=>{ G.set='g56'; G.book='rd1'; G.tag=null; G.lesson=0; G.rule='normal'; G.diff='normal'; G.versus=false; DueMix.RATE=0; startGame(); G.running=false;   // 첫 문제(25%)가 미리 하나 쓰지 않게
            DueMix.RATE=1; const got=[]; for(let k=0;k<6;k++){ const q=makeQuestion(); got.push(q.word.en); if(q.answer<0 || q.options.length<2) return 'BADQ'; }
            DueMix.RATE=0.25; return got; }""")
        mixed = [w for w in r if w in due] if isinstance(r, list) else []
        ok(isinstance(r, list) and sorted(set(mixed)) == due and len(mixed) == len(due), f"③ 달리기 문제에 복습 단어가 한 번씩 섞임 {r}")
        r = await E("""(due)=>{ DueMix.hit(due[0], true); DueMix.hit(due[0], true); DueMix.hit(due[1], false); DueMix.hit('apple', true);
            const S=Study.load(), D=(S.rt||{})[Study.today()]||{}; let n=0, c=0; Object.keys(D).forEach(b=>{ c+=D[b][0]; n+=D[b][1]; });
            return [G.rvN, G.rvOk, n, c, (S.srs[due[0]]||[])[1]>Study.today()]; }""", due)
        ok(r[:4] == [2, 1, 2, 1] and r[4], f"③ 처음 푼 것만 셈 (같은 단어 두 번·섞이지 않은 단어 = 안 셈) · 맞힌 단어는 다음 날로 {r}")
        POSTS.clear()
        await E("""()=>{ Object.assign(G,{right:6, wrong:2, score:1200, stage:20, zone:2, bestCombo:3, wrongWords:[], quit:true}); G.running=false; G.skipOutro=true; G.overFade=false; G._overDone=false; gameOver(); G.skipOutro=false; }""")
        await pg.wait_for_timeout(900)
        row = [b for b in POSTS if not b.get("type") and b.get("score") == 1200]
        ok(row and row[-1].get("rvn") == 2 and row[-1].get("rvo") == 1, f"③ 시트 줄에 rvo/rvn {[(b.get('rvo'), b.get('rvn')) for b in row]}")
        r = await E("""()=>{ const o=[]; const t=(f)=>{ f(); o.push(DueMix.ok()); };
            t(()=>{ G.rule='daily'; }); t(()=>{ G.rule='normal'; G.lesson=3; }); t(()=>{ G.lesson=0; G.set='wrong'; }); t(()=>{ G.set='g56'; G.versus=true; }); t(()=>{ G.versus=false; });
            return o; }""")
        ok(r == [False, False, False, False, True], f"③ 오늘의 도전·수업 단원·틀린 단어·대결 = 안 섞음 {r}")

        # ── ① 소리 조각 — 발음기호로 맞춘 소리
        L = await E("""()=>{ const D={glue:'/ɡluː/', said:'/sed/', they:'/ðeɪ/', circle:'/ˈsɜːrkəl/', find:'/faɪnd/', walk:'/wɔːk/', store:'/stɔːr/', away:'/əˈweɪ/', cake:'/keɪk/', year:'/jɪr/', box:'/bɑːks/'};
            const o={}; Object.keys(D).forEach(en=>{ const a=SoundBuild.split(en); o[en]=a.map((c,i)=>c+'='+SoundBuild.labs(a, D[en], 'basic')[i]).join(' '); });
            ['nod','pale','born'].forEach(en=>{ const a=SoundBuild.split(en); o[en]=a.map((c,i)=>c+'='+SoundBuild.labs(a, '', 'short')[i]).join(' '); });
            const a=SoundBuild.split('snow'); o.noipa=SoundBuild.labs(a, '', 'basic').join('');
            return o; }""")
        want = {"glue": "g=그 l=르 ue=우", "said": "s=스 ai=에 d=드", "they": "th=드 ey=에이", "circle": "c=스 ir=어(r) c=크 le=을",
                "find": "f=프 i=아이 n=느 d=드", "walk": "w=워 a=오 l=소리 없음 k=크", "store": "s=스 t=트 o=오 r=르 e=소리 없음",
                "away": "a=어 w=워 ay=에이", "cake": "c=크 a=에이 k=크 e=소리 없음", "year": "y=이 ea=이 r=르", "box": "b=브 o=아 x=크스",
                "nod": "n=느 o=아 d=드", "pale": "p=프 a=에이 l=르 e=소리 없음", "born": "b=브 or=오(r) n=느"}
        miss = {k: (L.get(k), v) for k, v in want.items() if L.get(k) != v}
        ok(not miss, f"① 조각 소리 = 발음기호대로 {miss or list(L.items())[:3]}")
        ok(L.get("noipa") == "", f"① 발음기호가 없는 낱말(파닉스 묶음 밖) = 소리 표시 없이 글자만 {L.get('noipa')!r}")

        # ① 실제 화면 — 유치원 새 단어
        await E("""()=>{ const S=Study.load(); S.srs={}; S.seen={}; S.lv={}; S.cp={}; S.wuSkip=Study.today(); S.book='k'; Study.save(); StudyUI.set='kinder'; StudyUI.book='k'; StudyUI.open(); StudyUI.start(0,false); }""")
        await pg.wait_for_timeout(600)
        got = None
        for _ in range(60):
            got = await E("()=>{ const U=StudyUI, q=U.qs[U.i]; return q && q.sb ? {en:q.w.en, ch:q.sb.ch, lab:q.sb.lab} : null; }")
            if got: break
            await E(SOLVE, False); await pg.wait_for_timeout(80)
        ok(bool(got), f"① 유치원 새 단어 카드 = 소리 조각 {got}")
        if got:
            r = await E("""()=>{ const c=document.querySelector('#stQ .stCard'), b=document.getElementById('stCheck'), vis=el=>!!el && getComputedStyle(el).display!=='none';
                return {sb:c.classList.contains('sbOn'), en:vis(c.querySelector('.stEn')), pic:vis(c.querySelector('.stPic')), dis:b.disabled, tiles:c.querySelectorAll('.sbT').length, slots:c.querySelectorAll('.sbS').length}; }""")
            ok(r["sb"] and not r["en"] and r["pic"] and r["dis"] and r["tiles"] == len(got["ch"]) == r["slots"], f"① 처음엔 단어·뜻 숨김 · 그림·조각만 · 다음 단추 꺼짐 {r}")
            if len(set(got["ch"])) > 1:
                r = await E("""()=>{ const S=StudyUI.qs[StudyUI.i].sb, w=[...document.querySelectorAll('#stQ .sbT')].find(b=>S.ch[+b.dataset.i]!==S.ch[0]); w.click(); return [w.classList.contains('no'), S.at, w.classList.contains('used')]; }""")
                ok(r == [True, 0, False], f"① 틀린 조각 = 흔들리기만 (점수·하트 없음) {r}")
            for k in range(len(got["ch"])):
                await E("(k)=>{ const S=StudyUI.qs[StudyUI.i].sb; const b=[...document.querySelectorAll('#stQ .sbT:not(.used)')].find(x=>S.ch[+x.dataset.i]===S.ch[S.at]); b.click(); }", k)
                await pg.wait_for_timeout(60)
            r = await E("""()=>{ const c=document.querySelector('#stQ .stCard'), vis=el=>!!el && getComputedStyle(el).display!=='none'; return {done:c.classList.contains('sbDone'), on:c.querySelectorAll('.sbS.on').length, en:vis(c.querySelector('.stEn')), say:(c.querySelector('.sbSay')||{}).textContent||'', dis:document.getElementById('stCheck').disabled}; }""")
            ok(r["done"] and r["on"] == len(got["ch"]) and r["en"] and r["dis"], f"① 다 놓으면 단어가 나타나고 소리를 들려주는 동안 단추는 꺼짐 {r}")
            for _ in range(40):
                d = await E("()=>{ const b=document.getElementById('stCheck'); return [b.disabled, b.textContent]; }")
                if not d[0]: break
                await pg.wait_for_timeout(250)
            ok(d == [False, "알겠어요 ▶"], f"① 소리가 끝나면 「알겠어요 ▶」 {d}")
            i0 = await E("()=>StudyUI.i")
            await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(400)
            ok(await E("()=>StudyUI.i") != i0, "① 「알겠어요」 → 다음 문제")
        # 자동 시험(webdriver) 기본 = 예전 카드
        r = await E("""()=>{ window.HY_SB=0; const w={en:'head', ko:'머리'}; return SoundBuild.ok('kinder', w); }""")
        ok(r is False, f"① HY_SB 없으면 예전 카드 {r}")
        r = await E("()=>[SoundBuild.ok('elem',{en:'head'}), (window.HY_SB=1, SoundBuild.ok('elem',{en:'head'})), SoundBuild.ok('basic',{en:'butterfly'}), SoundBuild.ok('basic',{en:'ice cream'})]")
        ok(r == [False, False, False, False], f"① G3-4 · 긴 단어 · 띄어쓰기 = 예전 카드 {r}")

        # ── ⑤ 🤝 짝 퀘스트
        await E("()=>{ StudyUI.close&&StudyUI.close(); }")
        g34 = await E("()=>Study.BOOKS.g34.sets[0]")
        await E("(set)=>{ const S=Study.load(); S.book='g34'; Study.save(); StudyUI.set=set; StudyUI.book='g34'; StudyUI.open(); }", g34)
        await pg.wait_for_timeout(500)
        now = int(time.time() * 1000)
        ME.clear(); ME.update({"pq": {"ws": now - 2 * 864e5, "goal": 15, "sum": 9, "mem": [{"n": "민준", "c": 4, "me": 1}, {"n": "서연", "c": 5}], "ch": [["서연", 0, now - 3600e3]]}})
        FETCH = "()=>{ LiveRank._f=0; LiveRank._busy=0; LiveRank._fresh=0; LiveRank.fetch(); }"
        await E(FETCH); await pg.wait_for_timeout(700)
        chip = await E("()=>{ const c=document.querySelector('#stHead .stPq'); return c ? c.textContent : null; }")
        ok(chip == "🤝 서연 9/15", f"⑤ 오늘의 30 지도 칩 = 짝 이름 · 둘이 합친 Stage {chip!r}")
        await E("()=>document.querySelector('#stHead .stPq').click()"); await pg.wait_for_timeout(300)
        r = await E("""()=>{ const d=document.getElementById('pqMt'); if(!d) return null; return {mem:[...d.querySelectorAll('.pqMem div')].map(x=>x.innerText.replace(/\\s+/g,' ')), n:d.querySelector('.pqN').textContent, ch:(d.querySelector('.pqCh')||{}).innerText||'', btn:d.querySelectorAll('[data-ch]').length, rw:!!d.querySelector('[data-rw]')}; }""")
        ok(r and r["mem"][0].startswith("민준 (나) 4") and r["mem"][1].startswith("서연 5") and "6개 더" in r["n"] and "같이 하자" in r["ch"] and r["btn"] == 3 and not r["rw"],
           f"⑤ 창 = 둘의 Stage · 6개 더 · 받은 응원 · 응원 단추 3개 · 아직 보상 없음 {r}")
        POSTS.clear()
        await E("()=>document.querySelector('#pqMt [data-ch=\"1\"]').click()"); await pg.wait_for_timeout(500)
        ch = [b for b in POSTS if b.get("type") == "cheer"]
        ok(ch and ch[-1].get("m") == 1 and ch[-1].get("tag") == "0006", f"⑤ 응원 보내기 = type cheer · 정해진 말 번호만 {[(b.get('m'), b.get('tag'), b.get('nick')) for b in ch]}")
        ok(not any("text" in b or "msg" in b for b in ch), "⑤ 응원에 아이가 쓴 글 없음")
        # 다 채움 → 💎15 한 번
        ME["pq"]["sum"] = 16; ME["pq"]["mem"][0]["c"] = 8; ME["pq"]["mem"][1]["c"] = 8
        await E(FETCH); await pg.wait_for_timeout(700)
        chip = await E("()=>{ const c=document.querySelector('#stHead .stPq'); return c ? [c.textContent, c.classList.contains('full')] : null; }")
        ok(chip == ["🤝 서연 15/15 🎁", True], f"⑤ 다 채우면 칩이 초록 + 🎁 {chip}")
        g0 = await E("()=>Wallet.gems()")
        await E("()=>{ const b=document.querySelector('#pqMt [data-rw]'); if(b) b.click(); }"); await pg.wait_for_timeout(300)
        g1 = await E("()=>Wallet.gems()")
        await E("()=>{ PairQ.claim(); }"); g2 = await E("()=>Wallet.gems()")
        rw = await E("()=>{ const b=document.querySelector('#pqMt [data-rw]'); return b ? [b.disabled, b.textContent] : null; }")
        ok(g1 - g0 == 15 and g2 == g1 and rw and rw[0], f"⑤ 💎15 한 번만 (두 번 눌러도) {g0}->{g1}->{g2} {rw}")
        chip = await E("()=>{ const c=document.querySelector('#stHead .stPq'); return c ? c.textContent : null; }")
        ok(chip == "🤝 서연 15/15", f"⑤ 받은 뒤 칩의 🎁 사라짐 {chip!r}")
        await E("()=>{ const d=document.getElementById('pqMt'); d.querySelector('[data-x]').click(); }")
        ok(await E("()=>!document.getElementById('pqMt')"), "⑤ 닫기")
        # 지난주 답 · 다른 아이 · 옛 서버
        ME["pq"]["ws"] = now - 8 * 864e5; await E(FETCH); await pg.wait_for_timeout(700)
        ok(await E("()=>!document.querySelector('#stHead .stPq')"), "⑤ 지난주 짝 답 = 칩 없음")
        ME["pq"]["ws"] = now - 864e5; await E(FETCH); await pg.wait_for_timeout(700)
        ok(await E("()=>!!document.querySelector('#stHead .stPq')"), "⑤ 이번 주 답 = 다시 칩")
        r = await E("()=>{ LiveRank.B.who='#9999'; PairQ.paint(); return !document.querySelector('#stHead .stPq'); }")
        ok(r, "⑤ 받아 둔 답이 다른 아이 것(공용 패드에서 바뀜) = 칩 없음")
        del ME["pq"]; await E(FETCH); await pg.wait_for_timeout(700)
        ok(await E("()=>!document.querySelector('#stHead .stPq')"), "⑤ 옛 서버(pq 없음) = 칩 없음")
        # 폰 넓이에서 칩이 머리 줄을 넘지 않음
        ME["pq"] = {"ws": now - 864e5, "goal": 22, "sum": 3, "mem": [{"n": "민준", "c": 1, "me": 1}, {"n": "서연", "c": 1}, {"n": "하윤", "c": 1}], "ch": []}
        await pg.set_viewport_size({"width": 390, "height": 844}); await E("(set)=>{ StudyUI.open(); }", g34); await pg.wait_for_timeout(300)
        await E(FETCH); await pg.wait_for_timeout(700)
        r = await E("()=>{ const c=document.querySelector('#stHead .stPq'), v=[...document.querySelectorAll('#stHead .stPq, #sbChips [data-sbk=\"pq\"]')].find(x=>x.getBoundingClientRect().width>0); if(!c || !v) return [c && c.textContent, null]; const b=v.getBoundingClientRect(); return [c.textContent, v.textContent, Math.round(b.left), Math.round(b.right), innerWidth]; }")
        ok(r and r[0] == "🤝 서연·하윤 3/22" and r[1] and "3/22" in r[1] and r[2] >= 0 and r[3] <= r[4], f"⑤ 셋 짝 = 이름 둘 · 목표 22 · 폰에서 보이는 칩이 화면 안 {r}")
        await pg.screenshot(path=OUT + "/fix698_pq_phone.png")
        await E("()=>{ const v=[...document.querySelectorAll('#stHead .stPq, #sbChips [data-sbk=\"pq\"]')].find(x=>x.getBoundingClientRect().width>0); v.click(); }"); await pg.wait_for_timeout(300)
        ok(await E("()=>!!document.getElementById('pqMt')"), "⑤ 폰에서 보이는 칩을 누르면 창")
        await pg.screenshot(path=OUT + "/fix698_pq_modal.png")
        r = await E("()=>{ const b=document.querySelector('#pqMt .tmB').getBoundingClientRect(); return [Math.round(b.left), Math.round(b.right), innerWidth, Math.round(b.bottom), innerHeight]; }")
        ok(r[0] >= 0 and r[1] <= r[2] and r[3] <= r[4], f"⑤ 창이 폰 화면 안 {r}")

        # ── ② 🧭 이야기
        await pg.set_viewport_size({"width": 820, "height": 1180})
        await E("()=>{ const d=document.getElementById('pqMt'); if(d) d.remove(); }")
        ME.clear()
        for _ in range(40):
            if await E("()=>DexData.st[1]==='ok' && DexData.st[2]==='ok'"): break
            await pg.wait_for_timeout(200)
        PASS3 = """(set)=>{ const S=Study.load(); S.lv=S.lv||{}; S.sty={}; Study.lessons(set).filter(x=>!x.fin).slice(0,3).forEach(x=>{ S.lv[Study.key(set,x.n)]=1; }); Study.save(); }"""
        await E(PASS3, "basic")
        await E("()=>{ const S=Study.load(); S.book='g12'; Study.save(); StudyUI.set='basic'; StudyUI.book='g12'; StudyUI.open(); }"); await pg.wait_for_timeout(500)
        chip = await E("()=>{ const c=document.querySelector('#stHead .stSty'); return c ? c.textContent : null; }")
        ok(chip == "🧭 이야기 1", f"② 판 3개 통과 → 지도에 🧭 이야기 칩 {chip!r}")
        g0 = await E("()=>Wallet.gems()")
        await E("()=>document.querySelector('#stHead .stSty').click()"); await pg.wait_for_timeout(300)
        r = await E("()=>{ const d=document.getElementById('styMt'); return d ? [d.querySelector('.styT').textContent, d.querySelector('.stySay p').textContent, !!d.querySelector('.styGo')] : null; }")
        ok(r and "강가" in r[0] and "river" in r[1] and r[2], f"② 시작 장면 = 테마 · 인물 말 · 시작 단추 {r}")
        await E("()=>document.querySelector('#styMt .styGo').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>{ const S=StoryQ.S, d=document.getElementById('styMt'); return {pics:S.pics, n:S.sc.length, tiles:d.querySelectorAll('.styIt').length, pic:d.querySelectorAll('.styIt .styPic').length, blank:!!d.querySelector('.stySay p u'), go:d.querySelector('.styGo').disabled}; }")
        ok(r["pics"] and r["n"] >= 3 and r["tiles"] >= 3 and r["pic"] == r["tiles"] and r["blank"] and r["go"], f"② G1-2 = 빈칸 문장 + 그림 고르기 · 다음 단추 꺼짐 {r}")
        # 첫 장면 일부러 틀리기
        r = await E("""()=>{ const S=StoryQ.S, q=S.sc[S.i], k=q.opts.findIndex(w=>w.en!==q.w.en); document.querySelector('#styMt .styIt[data-k="'+k+'"]').click();
            const d=document.getElementById('styMt'), b=d.querySelector('.styIt[data-k="'+k+'"]'); return [b.classList.contains('no'), b.disabled, d.querySelector('.stySay').innerText, !!d.querySelector('.stySay p u'), S.i, q.opts[k].en]; }""")
        ok(r[0] and r[1] and ("Hmm… not " + r[5]) in r[2].replace(r[5][0].upper()+r[5][1:], r[5]) and r[3] and r[4] == 0, f"② 틀리면 「Hmm… not ○○」 + 빈칸 문장 그대로 · 다음으로 안 넘어감 {r[:5]}")
        n = await E("()=>StoryQ.S.sc.length")
        for i in range(n):
            await E("""()=>{ const S=StoryQ.S, q=S.sc[S.i], k=q.opts.findIndex(w=>w.en===q.w.en); document.querySelector('#styMt .styIt[data-k="'+k+'"]').click(); }""")
            await pg.wait_for_timeout(120)
            if i == 0:
                r = await E("()=>{ const d=document.getElementById('styMt'); return [!!d.querySelector('.styGot'), !!d.querySelector('.stySay p em'), (d.querySelector('.stySay .ko')||{}).textContent||'', d.querySelector('.styGo').disabled, d.querySelector('.styGo').textContent]; }")
                ok(r[0] and r[1] and r[2] and not r[3] and r[4] == "다음 장면 ▶", f"② 맞히면 단어가 들어간 문장 + 해석 · 다음 장면 ▶ {r}")
            await E("()=>document.querySelector('#styMt .styGo').click()"); await pg.wait_for_timeout(120)
        r = await E("()=>{ const d=document.getElementById('styMt'); return [d.querySelector('.styWin h3').textContent, d.querySelector('.styWin').innerText, StoryQ.S.star, (Study.load().sty||{}).basic]; }")
        g1 = await E("()=>Wallet.gems()")
        ok(r[0] == "이야기 끝!" and r[2] == n - 1 and r[3] == 1 and g1 - g0 == 2, f"② 끝 = ⭐ 한 번에 {r[2]}/{n} · 💎2 · 기록 {r[3]} · {g0}->{g1}")
        await E("()=>document.querySelector('#styMt .styGo').click()"); await pg.wait_for_timeout(400)
        ok(await E("()=>!document.getElementById('styMt') && !document.querySelector('#stHead .stSty')"), "② 지도로 → 다음 3판 전에는 칩 없음")
        # 다시 열어도(같은 이야기 번호) 💎 는 한 번
        await E("()=>{ const S=Study.load(); S.sty={}; Study.save(); }")
        await E("()=>{ StoryQ.open('basic'); StoryQ.intro=false; const S=StoryQ.S; S.sc.forEach(q=>{ q.ok=q.w.en; q.tries=1; }); S.i=S.sc.length-1; StoryQ.go(); }")
        ok(await E("()=>Wallet.gems()") == g1, "② 같은 이야기를 또 끝내도 💎 는 한 번")
        await E("()=>StoryQ.close()")
        await pg.screenshot(path=OUT + "/fix698_sty_map.png")
        # G5-6 = 글자
        await E(PASS3, "g56")
        await E("()=>{ const S=Study.load(); S.book='g56'; Study.save(); StudyUI.set='g56'; StudyUI.book='g56'; StudyUI.open(); }"); await pg.wait_for_timeout(500)
        await E("()=>document.querySelector('#stHead .stSty').click()"); await pg.wait_for_timeout(200)
        await E("()=>document.querySelector('#styMt .styGo').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>{ const S=StoryQ.S, d=document.getElementById('styMt'); return {pics:S.pics, wd:d.querySelectorAll('.styIt.wd').length, pic:d.querySelectorAll('.styPic').length, t:d.querySelector('.styT').textContent}; }")
        ok(r["pics"] is False and r["wd"] >= 3 and r["pic"] == 0 and "원정대" in r["t"], f"② G5-6 = 글자 고르기 · 원정대 {r}")
        await pg.screenshot(path=OUT + "/fix698_sty_g56.png")
        await pg.set_viewport_size({"width": 390, "height": 844}); await pg.wait_for_timeout(200)
        r = await E("()=>{ const b=document.querySelector('#styMt .styB').getBoundingClientRect(); return [Math.round(b.left), Math.round(b.right), innerWidth, document.documentElement.scrollWidth]; }")
        ok(r[0] >= 0 and r[1] <= r[2] and r[3] <= r[2], f"② 폰 넓이 안 {r}")
        await pg.screenshot(path=OUT + "/fix698_sty_phone.png")
        await E("()=>StoryQ.close()")
        r = await E("()=>{ window.HY_STY=0; const a=StoryQ.on(); window.HY_STY=1; return a; }")
        ok(r is False, "② 자동 시험(webdriver) 기본 = 이야기 없음 (HY_STY=1 일 때만)")

        # ── ④ 교실 배틀 🎁 상자 · 빠름 +1
        r = await E("""()=>{ const B=Battle, keep={running:B.running, left:B.left, dbl:B.dbl, draw:B.draw, cfg:B.cfg, now:B.now}, inc=FB.inc, rnd=Math.random; const out={};
            B.running=()=>true; B.left=()=>100; B.dbl=()=>false; B.draw=()=>{}; B.cfg=()=>({mode:'score'}); FB.inc=()=>Promise.resolve(); B.room='T'; B.me='me'; B.lockTo=0; B.sc=0; B.streak=0; B._x2=0;
            const one=(seq, fast)=>{ let i=0; Math.random=()=>seq[Math.min(i++, seq.length-1)]; const q={w:{en:'apple',ko:'사과'}, opts:[{en:'apple'},{en:'dog'}]}; B.q=q; B.qAt=B.now()-(fast?800:6000); const s0=B.sc; B.answer(0); Math.random=rnd; return [B.sc-s0, q.chest||'', !!q.x2]; };
            out.base=one([0.99], false); B.streak=0; out.fast=one([0.99], true); B.streak=0; out.plus=one([0, 0.1], false); B.streak=0; out.x2=one([0, 0.9], false); B.streak=0; out.after=one([0.99], false);
            Object.assign(B, keep); FB.inc=inc; return [out, B.CHEST]; }""")
        o = r[0]
        ok(o["base"][0] == 10 and o["fast"][0] == 11 and o["plus"] == [15, "p", False] and o["x2"] == [10, "x2", False] and o["after"] == [20, "", True] and abs(r[1] - 1/7) < 1e-9,
           f"④ 빠름 +1 · 🎁 +5 · 🎁 다음 정답 2배 (잃는 칸 없음) · 1/7 {r}")
        ok(await E("()=>Board.GEMS.join(',')") == "10,8,8,8", "④ 보드 💎 = 우승 10 · 나머지 모두 8")

        ok(not real_errs(errs), f"화면 오류 없음 {real_errs(errs)[:3]}")
        await br.close()

    # ── ④ 선생님 「어느 범위?」
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append("A " + str(e))); await boot(pg)
        await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); localStorage.removeItem('hyeng_admin_pref'); }")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); }")
        E = pg.evaluate
        await E("()=>{ Admin.open(); Admin._tab('now'); }"); await pg.wait_for_timeout(900)
        r = await E("()=>{ const s=document.getElementById('adNowSet'); return s ? [s.value, document.getElementById('adBtSet').value, !!document.querySelector('#adNowFromPick')] : null; }")
        ok(r and r[0] == r[1] and r[2], f"④ 지금 수업 탭에 「어느 범위?」 = 배틀 범위에서 시작 · Stage 칸 {r}")
        await E("()=>{ const s=document.getElementById('adNowSet'); s.value='basic'; s.dispatchEvent(new Event('change')); }"); await pg.wait_for_timeout(200)
        await E("()=>{ const f=document.getElementById('adNowFrom'), t=document.getElementById('adNowTo'); f.value='2'; t.value='5'; f.dispatchEvent(new Event('change')); t.dispatchEvent(new Event('change')); }"); await pg.wait_for_timeout(300)
        r = await E("()=>['adBtSet','adBtFrom','adBtTo','adRrSet','adRrBk','adRrFrom','adRrTo','adRdBook'].map(id=>document.getElementById(id).value)")
        ok(r == ["basic", "2", "5", "stg", "basic", "2", "5", "g12"], f"④ 범위를 바꾸면 배틀·레이스(책·Stage) · 레이드(책) 칸에 같이 {r}")
        r = await E("()=>[document.getElementById('adSum_bt').textContent, document.getElementById('adSum_rr').textContent, document.getElementById('adSum_rd').textContent]")
        ok(all("1-2" in x or "G1-2" in x or "Grade 1-2" in x for x in r), f"④ 놀이 칸 요약도 같은 범위 {r}")
        P = await E("()=>JSON.parse(localStorage.getItem('hyeng_admin_pref')||'{}')")
        ok(P.get("adBtSet") == "basic" and P.get("adBtTo") == "5" and P.get("adRdBook") == "g12", f"④ 다음에 열어도 그대로 (설정 저장) {[P.get(k) for k in ('adBtSet','adBtTo','adRdBook')]}")
        r = await E("()=>[document.getElementById('adNowRngTx').textContent, document.querySelector('.adRngD').open]")
        ok(r[0].startswith("Stage 1-3") and r[0].endswith("바꾸기") and not r[1], f"④ 범위는 한 줄(눌러서 바꾸기) {r}")
        await pg.screenshot(path=OUT + "/fix698_admin_rng.png", full_page=False)
        await E("()=>{ document.querySelector('.adRngD').open=true; }"); await pg.wait_for_timeout(150)
        await pg.screenshot(path=OUT + "/fix698_admin_rng_open.png", full_page=False)
        ok(not real_errs(errs), f"관리 화면 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("FAIL" if bad else "PASS", len(bad))
    sys.exit(1 if bad else 0)

asyncio.run(main())
