# v667 🔥 오늘의 대결 (랭킹 「오늘」 탭 · 추월 연출 · v670 첫 화면 = 다시 「실시간」 한 줄 + 오늘 줄) + 선생님 📊 랭킹 통계 카드 (+ 서버 gs_today667.js)
import asyncio, sys, os, re, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
OUT = os.environ.get("HY_OUT", "/tmp/today667_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
DATA = re.search(r'DATA = r"""(.*?)"""', open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rank618.py"), encoding="utf-8").read(), re.S).group(1)
TD = r"""(o)=>{ o=o||{}; const B=Object.assign({}, LiveRank.B), key=new Date(Date.now()+9*3600e3).toISOString().slice(0,10);
  let L=[["스트로베리","0008",720,"wolf"],["주호","0011",o.me||420,"explorer"],["단우","0015",330,"cat"],["김지후","0007",220,"mage"],["루아","0014",180,"ghost"],["라언","0009",150,"archer"],["빈","0012",110,"hero"],["SEOWON","0017",60,"scholar"]];
  if(o.many) for(let i=0;i<7;i++) L.push(["친구"+(i+1),"01"+(20+i),o.manyHi?900-i*20:50-i*5,""]);
  if(o.noMe) L=L.filter(x=>x[1]!=="0011"); if(o.empty) L=[];
  L=L.map(x=>({nick:x[0],tag:x[1],score:x[2],ch:x[3],n:2})).sort((a,b)=>b.score-a.score);
  B.today={key:o.oldKey?"2020-01-01":key, of:L.length, list:L, aw:o.empty?{}:{up:{nick:"주호",tag:"0011",ch:"explorer",v:3}, acc:{nick:"라언",tag:"0009",ch:"archer",v:98}, word:{nick:"단우",tag:"0015",ch:"cat",v:12}}};
  B.me=Object.assign({}, B.me); const i=L.findIndex(x=>x.tag==="0011");
  if(i>=0) B.me.today=Object.assign({}, L[i], {rank:i+1, of:L.length, above:i>0?{nick:L[i-1].nick,score:L[i-1].score}:null, below:i<L.length-1?{nick:L[i+1].nick,score:L[i+1].score}:null}); else delete B.me.today;
  B.who = o.who!==undefined ? o.who : LiveRank.who().key; LiveRank.set(B); }"""
ROWS = """()=>[...document.querySelectorAll('#rankList .tdyRow')].map(r=>({i:+r.dataset.i, me:r.classList.contains('me'), y:Math.round(new DOMMatrix(getComputedStyle(r).transform).m42), nm:r.querySelector('.nm').textContent.trim(), sc:r.querySelector('.sc span').textContent, rk:r.querySelector('.rk').textContent.trim()||r.querySelector('.rk i').className, gp:r.querySelector('.gp').classList.contains('on') ? r.querySelector('.gp').textContent : ''})).sort((a,b)=>a.y-b.y)"""
FIT = "()=>{ const s=document.querySelector('.screen.on'); return [s.id, s.scrollHeight-s.clientHeight, document.documentElement.scrollWidth-innerWidth]; }"
VW = {"ph": (390, 844), "pad": (820, 1180), "tv": (1920, 1080), "lph": (915, 412), "lpad": (1180, 820), "se": (375, 667), "ipad": (768, 1024), "lipad": (1024, 768)}
REP = {"at": 0, "d": {"nicks": [], "rk": {"at": 0, "today": "2026-11-12", "per": [
    {"k": "w0", "name": "이번 주", "from": "2026-11-09", "to": "2026-11-15", "dn": 3, "rows": [
        {"n": "김지후", "g": "", "tag": "0007", "d1": 2, "w1": 0, "rk": 1, "days": 4, "q": 3690, "ok": 88, "r": 123, "sc": 31200},
        {"n": "최선아", "g": "스트로베리", "tag": "0008", "d1": 1, "w1": 0, "rk": 3, "days": 4, "q": 990, "ok": 88, "r": 21, "sc": 6100},
        {"n": "찬겸 박", "g": "", "tag": "0021", "d1": 0, "w1": 0, "rk": 0, "days": 1, "q": 240, "ok": 71, "r": 0, "sc": 0}]},
    {"k": "w1", "name": "지난주", "from": "2026-11-02", "to": "2026-11-08", "dn": 7, "rows": []},
    {"k": "m0", "name": "이번 달", "from": "2026-11-01", "to": "2026-11-30", "dn": 10, "rows": [
        {"n": "김지후", "g": "", "tag": "0007", "d1": 6, "w1": 1, "rk": 0, "days": 9, "q": 7200, "ok": 89, "r": 240, "sc": 61000},
        {"n": "빈", "g": "", "tag": "0012", "d1": 4, "w1": 0, "rk": 0, "days": 8, "q": 5100, "ok": 90, "r": 170, "sc": 43000}]},
    {"k": "m1", "name": "지난달", "from": "2026-10-01", "to": "2026-10-31", "dn": 31, "rows": []}]}}}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        async def page(vw):
            pg = await b.new_page(viewport={"width": vw[0], "height": vw[1]}); pg.on("pageerror", lambda e: errs.append(str(e)[:300])); await boot(pg)
            await pg.evaluate(DATA); await pg.wait_for_timeout(1500); await pg.evaluate("()=>{ const d=document.getElementById('rkAnn'); if(d) d.remove(); try{ localStorage.removeItem(TodayRank.KS()); }catch(e){} }"); return pg
        pg = await page(VW["ph"]); E = pg.evaluate
        # ① 옛 서버 (today 없음) = 예전 그대로
        IT = "()=>LiveRank.it.map(x=>x[0]+':'+x[1])"
        TX = "()=>LiveRank.it.map(x=>{ const d=document.createElement('div'); d.innerHTML=LiveRank.rowH(x); return d.textContent.replace(/\\s+/g,' ').trim(); })"
        OPEN = "()=>{ LiveRank.i=LiveRank.it.findIndex(x=>x[0]==='today'); document.getElementById('lrBar').click(); }"
        r = await E("()=>{ RANK_VIEW.range='today'; showRank('study'); const o=[!document.getElementById('tdyCard'), document.getElementById('lrBar').hidden, getComputedStyle(document.querySelector('#selRankRange [data-v=today]')).display, RANK_VIEW.range, !!document.querySelector('#rankList .rkPod'), document.querySelector('#selRankRange [data-v=hof] b').textContent, LiveRank.it.some(x=>x[0]==='today')]; document.getElementById('btnRankBack').click(); return o; }")
        ok(r == [True, False, "none", "week", True, "🏛 명예의 전당", False], f"옛 서버: 오늘 줄·탭 없음 · 실시간 줄 · 이번 주 그대로 {r}")
        n0 = len(await E(IT))
        # ② 새 서버 · 오늘 안 한 아이 — (v670) 카드는 없고 「실시간」 줄에 오늘 1·2·3등이 섞임
        await E(TD, {"noMe": True}); await pg.wait_for_timeout(200)
        it = await E(IT); tx = await E(TX); r = await E("()=>[document.getElementById('lrBar').hidden, !document.getElementById('tdyCard')]")
        ok(r == [False, True] and it[0] == "today:0" and [x for x in it if x.startswith("today")] == ["today:0", "today:1", "today:2"] and len(it) == n0 + 3, f"안 한 아이: 실시간 줄 + 오늘 1~3등 (나 줄 없음) {it[:6]}")
        ok(tx[0].startswith("🔥 오늘") and "1" in tx[0] and "스트로베리" in tx[0] and "720점" in tx[0], f"오늘 1등 줄 글 {tx[0]}")
        # ③ 어제 받아 둔 것 = 오늘 줄 없음
        await E(TD, {"oldKey": True}); await pg.wait_for_timeout(150)
        ok(not [x for x in await E(IT) if x.startswith("today")], "어제 받아 둔 오늘 순위는 안 굴림")
        # ④ 나 2등 — 「⭐ 나 🔥 오늘 2위 · 1등까지 300점」
        await E(TD, {}); await pg.wait_for_timeout(200)
        it = await E(IT); tx = await E(TX); k = it.index("today:-1") if "today:-1" in it else -1
        ok(k > 0 and it[k - 1].endswith(":0") and "⭐ 나" in tx[k] and "오늘 2위" in tx[k] and "1등까지 300점" in tx[k], f"내 오늘 줄 {tx[k] if k >= 0 else it[:8]}")
        f = await E(FIT); ok(f[1] <= 0 and f[2] <= 0, f"첫 화면 스크롤 없음 {f}")
        # ④-2 굴러감 — 3초마다 한 줄 · 줄 높이 그대로
        a = await E("()=>[LiveRank.i, document.querySelector('#lrRoll .lrIt').textContent, Math.round(document.getElementById('lrBar').getBoundingClientRect().height)]")
        await pg.wait_for_timeout(3400); c = await E("()=>[LiveRank.i, document.querySelector('#lrRoll .lrIt').textContent, Math.round(document.getElementById('lrBar').getBoundingClientRect().height)]")
        ok(c[0] != a[0] and c[1] != a[1] and c[2] == a[2] and c[2] <= 48, f"실시간 줄이 굴러감 · 높이 그대로 {a} → {c}")
        await E(TD, {"empty": True}); await pg.wait_for_timeout(200)
        it = await E(IT); ok(len(it) == n0 and not [x for x in it if x.startswith("today")] and not await E("()=>document.getElementById('lrBar').hidden"), f"오늘 아무도 안 했으면 예전 줄 그대로 ({len(it)}줄)")
        await E(TD, {}); await pg.wait_for_timeout(200)
        # ④-3 누르기 — 오늘 줄 = 랭킹 「🔥 오늘」 · 다른 줄 = 예전처럼 펼침
        r = await E("()=>{ LiveRank.i=LiveRank.it.findIndex(x=>x[0]==='words'); document.getElementById('lrBar').click(); const o=[!!document.getElementById('lrPanel'), document.getElementById('scRank').classList.contains('on')]; const d=document.getElementById('lrPanel'); if(d) d.remove(); return o; }")
        ok(r == [True, False], f"다른 줄을 누르면 예전처럼 펼침 {r}")
        # ⑤ 오늘 탭 — 처음 본 것 = 0점에서 올라오는 연출
        await E(OPEN); await pg.wait_for_timeout(250)
        r = await E("()=>[document.getElementById('scRank').classList.contains('on'), RANK_VIEW.range, document.querySelector('#selRankRange .sel').dataset.v, getComputedStyle(document.querySelector('#selRankRange [data-v=today]')).display!=='none', document.querySelector('#selRankRange [data-v=hof] b').textContent]")
        ok(r == [True, "today", "today", True, "🏛 전당"], f"오늘 줄을 누르면 랭킹 「🔥 오늘」 {r}")
        R = await E(ROWS); ok(len(R) == 8 and R[-1]["me"] and R[-1]["sc"] == "0" and R[-1]["rk"] == "–" and "첫 판" in await E("()=>document.querySelector('.tdyMy .t1').textContent"), f"처음: 내 줄이 맨 아래 0점에서 {R[-1]}")
        await pg.wait_for_timeout(4600); R = await E(ROWS)
        ok([x["nm"].replace(" 나", "") for x in R][:3] == ["스트로베리", "주호", "단우"] and R[1]["me"] and R[1]["sc"] == "420" and R[0]["gp"] == "300점 앞" and R[2]["gp"] == "90점 뒤", f"끝: 2등 자리 · 420점 · 앞뒤 차이 {[(x['nm'],x['sc'],x['gp']) for x in R[:3]]}")
        r = await E("()=>[document.querySelector('.tdyMy .tdyBd').textContent, document.querySelector('.tdyMy .t1').textContent, document.querySelector('.tdyMy .up').textContent, document.querySelector('.tdyMy .gp').textContent, document.querySelector('.tdyCta').textContent, [...document.querySelectorAll('.tdyAwC')].map(x=>x.textContent), document.querySelector('.tdyTm').textContent]")
        ok(r[0] == "2등" and r[1] == "오늘 2등!" and r[2] == "▲6" and "1등 스트로베리까지 300점" in r[3] and "300점 넘으면 1등" in r[4] and len(r[5]) == 3 and "(나!)" in r[5][0] and "98%" in r[5][1] and "밤 12시까지" in r[6], f"머리줄·버튼·오늘의 상(있는 것만 3개) {r}")
        await pg.screenshot(path=OUT + "ph_today.png")
        # ⑥ 다시 그려도 연출 안 함 · 점수가 오르면 그때만
        await E("()=>{ RANK_VIEW.range='week'; drawRankScreen(); RANK_VIEW.range='today'; drawRankScreen(); }"); await pg.wait_for_timeout(250); R = await E(ROWS)
        ok(R[1]["me"] and R[1]["sc"] == "420" and R[0]["gp"] == "300점 앞", "다시 열면 연출 없이 바로")
        await E("()=>{ localStorage.setItem(TodayRank.KS(), JSON.stringify({k:TodayRank.dkey(), s:120, r:6})); document.getElementById('btnRankBack').click(); LiveRank.draw(); }"); await pg.wait_for_timeout(150)
        tx = await E(TX); r = [x for x in tx if "⭐ 나" in x and "🔥 오늘" in x]; ok(len(r) == 1 and "▲4" in r[0], f"첫 화면 내 오늘 줄: ▲4 {r}")
        await E(OPEN); await pg.wait_for_timeout(250); R = await E(ROWS)
        ok(R[5]["me"] and R[5]["sc"] == "120" and R[5]["rk"] == "6" and "6등" in await E("()=>document.querySelector('.tdyMy .tdyBd').textContent"), f"점수가 올랐을 때: 예전 자리(6등 · 120점)에서 시작 {R[5]}")
        await pg.wait_for_timeout(2500); r = await E("()=>[document.querySelector('.tdyOvt').classList.contains('on'), document.querySelector('.tdyOvt').textContent, document.querySelector('.tdyMy .up').textContent]"); ok(r == [True, "▲4 추월!", "▲4"], f"▲4 추월! {r}")
        await pg.wait_for_timeout(2200); R = await E(ROWS); tx = [x for x in await E(TX) if "⭐ 나" in x and "🔥 오늘" in x]; ok(R[1]["me"] and R[1]["sc"] == "420" and len(tx) == 1 and "▲" not in tx[0], f"연출 뒤 2등 자리 · 첫 화면 줄의 ▲ 는 꺼짐 {tx}")
        # ⑦ 8명 넘으면 접기
        await E(TD, {"many": True}); await pg.wait_for_timeout(300); R = await E(ROWS)
        ok(len(R) == 7 and await E("()=>document.querySelector('.tdyMore').textContent") == "모두 보기 · 15명" and not await E("()=>!!document.querySelector('.tdyDots')"), f"15명 · 내가 위쪽: 7줄 + 모두 보기 {len(R)}")
        await E(TD, {"many": True, "manyHi": True}); await pg.wait_for_timeout(300); R = await E(ROWS)
        ok([x["rk"] for x in R][3:] == ["8", "9", "10"] and R[4]["me"] and await E("()=>!!document.querySelector('.tdyDots')"), f"내가 9등: 1~3등 ⋯ 8·9·10등 {[x['rk'] for x in R]}")
        await E("()=>document.querySelector('.tdyMore').click()"); await pg.wait_for_timeout(250); R = await E(ROWS)
        ok(len(R) == 15 and await E("()=>document.querySelector('.tdyMore').textContent") == "접기", "모두 보기 → 15줄 · 접기")
        await E("()=>document.querySelector('.tdyMore').click()"); await pg.wait_for_timeout(200)
        # ⑧ 안 한 아이 · 아무도 없음 · 버튼
        await E(TD, {"noMe": True}); await pg.wait_for_timeout(250)
        r = await E("()=>[document.querySelector('.tdyMy').classList.contains('idle'), document.querySelector('.tdyMy .t1').textContent, document.querySelector('.tdyCta').textContent, document.querySelectorAll('.tdyRow').length]"); ok(r == [True, "오늘 아직 안 했어요", "📚 한 판 하러 가기", 7], f"안 한 아이 탭 {r}")
        await E(TD, {"empty": True}); await pg.wait_for_timeout(250)
        ok("지금 하면 1등" in await E("()=>document.querySelector('.tdyNone').textContent") and not await E("()=>!!document.querySelector('.tdyAwBox')"), "아무도 안 했을 때: 지금 하면 1등 · 상 없음")
        await E("()=>document.querySelector('.tdyCta').click()"); await pg.wait_for_timeout(500)
        ok(await E("()=>document.getElementById('scStudy').classList.contains('on') && !document.getElementById('scRank').classList.contains('on')"), "📚 버튼 → 오늘의 30")
        # ⑨ 판이 서버에 적히면 바로 새 순위 (fresh=1)
        r = await E("""()=>new Promise(res=>{ const urls=[]; const of=window.fetch; window.fetch=(u,o)=>{ urls.push([String(u), o&&o.body]); return Promise.resolve({json:()=>Promise.resolve({ok:true})}); };
          let n=0; LiveRank.fetch=function(){ n++; }; const b0=LiveRank._fresh;
          Online.submit({nick:'주호', score:270, diff:'study', rule:'study', right:27, wrong:3, clear:1}).then(()=>Online.submit({nick:'주호', score:100, diff:'normal', rule:'normal'})).then(()=>setTimeout(()=>{ window.fetch=of; res([LiveRank._fresh>b0, n, LiveRank._f]); }, 1800)); })""")
        ok(r[0] and r[1] == 1 and r[2] == 0, f"공부 판이 적히면 한 번 새로 받음 (달리기 판은 아님) {r}")
        # ⑨-2 공용 패드: 고른 아이 이름으로 「나」 · 아이가 바뀌면 앞 아이의 「나」 줄을 빼고 그 아이로 다시 받음 (한 번)
        await E("()=>{ show('scStart'); }"); await pg.wait_for_timeout(200); await E(TD, {}); await pg.wait_for_timeout(150)
        r = await E("""()=>{ let n=0; LiveRank.fetch=function(){ n++; }; localStorage.setItem('hyeng_nick','한양패드1'); const sh=Kid.shared(); sessionStorage.setItem('hyeng_kid', JSON.stringify({id:'k9', n:'단우', at:Date.now()}));
          const w=LiveRank.who(), had=LiveRank.it.filter(x=>x[1]<0).length; LiveRank._ask=0; LiveRank._askK=null; LiveRank.draw(); LiveRank.draw(); return [sh, w.tag, w.nick, n, had>0, LiveRank.it.filter(x=>x[1]<0).length, LiveRank.it.filter(x=>x[0]==='today').length]; }""")
        ok(r == [True, "", "단우", 1, True, 0, 3], f"공용 패드: 「나」 = 고른 아이(단우) · 앞 아이 줄은 빼고 한 번만 다시 받음 · 오늘 1~3등은 그대로 {r}")
        r = await E("""()=>{ const B=Object.assign({}, LiveRank.B), L=B.today.list, i=L.findIndex(x=>x.nick==='단우'); B.me={today:Object.assign({}, L[i], {rank:i+1, of:L.length, above:{nick:L[i-1].nick, score:L[i-1].score}, below:L[i+1]?{nick:L[i+1].nick, score:L[i+1].score}:null})}; B.who=LiveRank.who().key; LiveRank.set(B);
          const x=LiveRank.it.find(x=>x[0]==='today' && x[1]<0), d=document.createElement('div'); d.innerHTML=x ? LiveRank.rowH(x) : ''; const o=[d.textContent, RankUI.isMe({nick:'단우', tag:''}), RankUI.isMe({nick:'주호', tag:'0011'})]; localStorage.removeItem('hyeng_nick'); sessionStorage.removeItem('hyeng_kid'); return o; }""")
        ok("오늘 3위" in r[0] and "2등까지 90점" in r[0] and r[1] is True and r[2] is False, f"공용 패드: 고른 아이의 오늘 줄 {r}")
        await pg.close()
        # ⑩ 화면 크기마다 — 가로 넘침 · 첫 화면 스크롤 · 글자 잘림
        for nm, vw in VW.items():
            pg = await page(vw); E = pg.evaluate; await E(TD, {}); await pg.wait_for_timeout(250)
            f0 = await E(FIT); base = {"se": 20}.get(nm, 0)   # 작은 휴대폰 첫 화면은 예전에도 17px 넘침
            c = await E("""()=>{ const c=document.getElementById('lrBar'), r=c.getBoundingClientRect(), R=document.getElementById('lrRoll'), bad=[]; clearTimeout(LiveRank._t);
              LiveRank.it.filter(x=>x[0]==='today').forEach(x=>{ R.innerHTML=LiveRank.rowH(x); const it=R.firstChild, n=it.querySelector('.n'), q=it.getBoundingClientRect(); const rk=it.querySelector('.r'), w=it.parentNode.parentNode.getBoundingClientRect(), k=rk.getBoundingClientRect(); if(it.scrollWidth>it.clientWidth+1 || n.getBoundingClientRect().width<24 || q.right>r.right+1 || k.right>w.right+1 || n.scrollWidth>n.clientWidth+1 && x[1]<0) bad.push(it.textContent); });
              LiveRank.draw(); return [Math.round(r.width), Math.round(r.height), r.left>=0 && r.right<=innerWidth+1, bad]; }""")
            ok(f0[1] <= base and f0[2] <= 0 and c[2] and not c[3] and c[1] <= 48, f"{nm}: 첫 화면 실시간 줄 {c} · 스크롤 {f0}")
            await pg.screenshot(path=f"{OUT}{nm}_start.png")
            await E("()=>{ localStorage.setItem(TodayRank.KS(), JSON.stringify({k:TodayRank.dkey(), s:420, r:2})); LiveRank.i=LiveRank.it.findIndex(x=>x[0]==='today'); document.getElementById('lrBar').click(); }"); await pg.wait_for_timeout(350)
            t = await E("""()=>{ const d=document.querySelector('.tdyDay').getBoundingClientRect(), cut=[...document.querySelectorAll('.tdyRow .nm, .tdyMy .gp, .tdyCta, .tdyAwC b, .tdyAwC span')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent);
              const rows=[...document.querySelectorAll('.tdyRow')].map(r=>r.getBoundingClientRect()), lap=rows.some((a,i)=>rows.some((b,j)=>j>i && a.top<b.bottom-1 && b.top<a.bottom-1)), cta=document.querySelector('.tdyCta').getBoundingClientRect(), last=rows.reduce((m,r)=>Math.max(m,r.bottom),0);
              return [d.left>=0 && d.right<=innerWidth+1, cut, lap, cta.top>=last-1, Math.round(cta.bottom), innerHeight, Math.round(rows[0].height)]; }""")
            f1 = await E(FIT)
            ok(t[0] and not t[1] and not t[2] and t[3] and f1[2] <= 0, f"{nm}: 오늘 탭 — 넘침·잘림·겹침 없음 {t} {f1}")
            if nm in ("ph", "pad", "tv", "lpad", "ipad"): ok(t[4] <= t[5], f"{nm}: 내 등수·순위표·한 판 더 버튼이 한 화면 안 (버튼 아래 {t[4]} ≤ {t[5]})")
            await pg.screenshot(path=f"{OUT}{nm}_today.png"); await pg.close()
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        # ⑪ 선생님 📊 랭킹 통계 카드
        for nm, vp in (("pad", (820, 1180)), ("ph", (390, 844))):
            ctx = await b.new_context(viewport={"width": vp[0], "height": vp[1]}, is_mobile=True, has_touch=True); T = await ctx.new_page(); await boot(T)
            await T.evaluate("(r)=>{ r.at=Date.now(); localStorage.setItem('hyeng_admin_rep', JSON.stringify(r)); sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }", REP)
            await T.reload(); await T.wait_for_timeout(1500)
            await T.evaluate("(R)=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); Online.on=()=>true; Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:R.d} : {ok:true}); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); window._clip=''; try{ Object.defineProperty(navigator, 'clipboard', {value:{writeText:t=>{ window._clip=t; return Promise.resolve(); }}, configurable:true}); }catch(e){} Admin.open(); }", REP)
            await T.wait_for_timeout(500); await T.click('#adTabs [data-t="rec"]'); await T.wait_for_timeout(800)
            GET = "()=>{ const t=document.querySelector('#adBody table.rkStat'); if(t) t.scrollIntoView({block:'center'}); return [[...document.querySelectorAll('#adBody .adSeg button')].map(x=>x.textContent+(x.classList.contains('on')?'*':'')), t ? [...t.rows].map(r=>[...r.cells].map(c=>c.textContent.trim())) : null, document.getElementById('adBody').scrollWidth-document.getElementById('adBody').clientWidth]; }"
            r = await T.evaluate(GET)
            ok(r[0] == ["이번 주*", "지난주", "이번 달", "지난달"] and r[1] and r[1][0][:5] == ["아이", "🥇 하루 1등", "주 순위", "📅 한 날", "✏️ 푼 문제"] and r[1][1][:5] == ["김지후", "2번", "1위", "4일", "3,690"] and r[1][2][0] == "최선아 스트로베리" and r[1][3][1:3] == ["–", "–"] and r[2] <= 1, f"{nm}: 이번 주 표 {r[1] and r[1][:2]} 넘침 {r[2]}")
            await T.screenshot(path=f"{OUT}admin_{nm}.png")
            await T.click('#adBody [data-ad="rkCopy"]'); await T.wait_for_timeout(200); cp = await T.evaluate("()=>window._clip")
            ok("이번 주 (2026-11-09 ~ 2026-11-15)" in cp and "김지후\t2번\t1위\t4일\t3690\t88%\t123\t31200" in cp, f"{nm}: 📋 표 복사 {cp[:60]!r}")
            await T.click('#adBody .adSeg [data-i="2"]'); await T.wait_for_timeout(300); r = await T.evaluate(GET)
            ok(r[0][2] == "이번 달*" and r[1][0][2] == "🏆 주 1등" and r[1][1][:5] == ["김지후", "6번", "1번", "9일", "7,200"] and r[1][2][2] == "–", f"{nm}: 이번 달 표 (주 1등 칸) {r[1][:3]}")
            await T.click('#adBody .adSeg [data-i="1"]'); await T.wait_for_timeout(300)
            ok("기록이 없어요" in await T.evaluate("()=>document.querySelector('#adBody .adSeg').parentElement.textContent"), f"{nm}: 기록 없는 기간")
            await ctx.close()
        # 옛 서버 리포트(rk 없음) = 올리는 법 안내
        ctx = await b.new_context(viewport={"width": 390, "height": 844}); T = await ctx.new_page(); await boot(T)
        await T.evaluate("()=>{ localStorage.setItem('hyeng_admin_rep', JSON.stringify({at:Date.now(), d:{nicks:[]}})); sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); Online.on=()=>true; Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:{nicks:[]}} : {ok:true, v:22}); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }")
        await T.wait_for_timeout(500); await T.click('#adTabs [data-t="rec"]'); await T.wait_for_timeout(800)
        tx = await T.evaluate("()=>{ const c=[...document.querySelectorAll('#adBody .adCard')].find(x=>/랭킹 통계/.test(x.textContent)); return c ? c.textContent : ''; }")
        ok("v23" in tx and "새 Code.gs 복사" in tx, "옛 서버: 랭킹 통계 카드에 서버 올리는 법")
        await ctx.close(); await b.close()
    g = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gs_today667.js")], capture_output=True, text=True); ok(g.returncode == 0, "Code.gs v23 (gs_today667.js)")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
