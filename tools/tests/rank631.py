# v631 🏆 아이마다 랭킹 단계 — 관리자 👥 아이들 탭 카드 · 고르면 바로 저장(tagLv) · 한꺼번에 · 빼기 · 옛 서버 안내 · 아이 화면 🔒 · 휴대폰/패드/가로
import asyncio, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/rank631_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

MOCK = """(v)=>{ window._posts=[]; window._lv={'0007':'G3-4','0009':'빼기'};
  Online.submit=o=>{ _posts.push(JSON.parse(JSON.stringify(o)));
    if(o.type==='report') return Promise.resolve({ok:true, rep:{nicks:[], weekly:[['아이','들어온 날'],['가온','4']]}});
    if(o.type==='check') return Promise.resolve({ok:true, v:v});
    if(o.type==='tags'){ if(v<4) return Promise.resolve({ok:false, err:'type'});
      return Promise.resolve({ok:true, v:v, list:[{tag:'0000',dev:'',first:'',nick:'',memo:'나'},{tag:'0001',dev:'p1',first:'한양패드1',nick:'한양패드1'},
        {tag:'0006',dev:'dA',first:'가온',nick:'가온',rlv:_lv['0006']||'',auto:'G1-2'},{tag:'0007',dev:'dB',first:'나래',nick:'나래',rlv:_lv['0007']||'',auto:'G5-6'},
        {tag:'0008',dev:'dC',first:'다솜',nick:'다솜',rlv:_lv['0008']||'',auto:''},{tag:'0009',dev:'dD',first:'라온',nick:'라온',rlv:_lv['0009']||'',auto:'G3-4'},
        {tag:'0010',dev:'',first:'',nick:'',memo:''},{tag:'0011',dev:'',first:'선생님',nick:'(안 씀)',memo:'안 씀 — 선생님 기기가 #0000 이 되기 전에 받은 번호'}]}); }
    if(o.type==='tagLv'){ if(v<15) return Promise.resolve({ok:false, err:'type'}); o.tags.forEach(t=>_lv[t]=o.lv==='자동'?'':o.lv); return Promise.resolve({ok:true, n:o.tags.length}); }
    return Promise.resolve({ok:true}); };
  Notice.fetch=()=>Promise.resolve({v:v, notices:[]}); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); window.confirm=()=>true; }"""

OPEN = """async ()=>{ Admin.open(); Admin._tab('class'); await new Promise(z=>setTimeout(z,1500));
  const h=[...document.querySelectorAll('#adBody .adCard > h3')].find(x=>/랭킹 단계/.test(x.textContent)); if(h && h.parentNode.classList.contains('shut')){ h.click(); await new Promise(z=>setTimeout(z,500)); }
  const c=[...document.querySelectorAll('#adBody .adCard')].find(x=>/랭킹 단계/.test((x.querySelector('h3')||{textContent:''}).textContent)); if(c) c.scrollIntoView(); return !!c; }"""
CARD = """()=>{ const c=[...document.querySelectorAll('#adBody .adCard')].find(x=>/랭킹 단계/.test((x.querySelector('h3')||{textContent:''}).textContent)); if(!c) return null;
  return {h:c.querySelector('h3').textContent, t:c.textContent, rows:[...c.querySelectorAll('select[data-rlv]')].map(s=>[s.dataset.rlv, s.value, s.classList.contains('on')]),
    w:c.scrollWidth-c.clientWidth, docW:document.documentElement.scrollWidth-innerWidth}; }"""

async def setup(b, vp, v=15, **kw):
    pg = await b.new_page(viewport=vp, **kw); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await boot(pg)
    await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','선생님'); localStorage.setItem('hyeng_tag','0000'); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }")
    await pg.reload(); await pg.wait_for_timeout(1500)
    await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }")
    await pg.evaluate(MOCK, v)
    return pg, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg, errs = await setup(b, {"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        ok(await pg.evaluate(OPEN), "👥 아이들 탭에 🏆 랭킹 단계 카드")
        c = await pg.evaluate(CARD)
        rows = {r[0]: r for r in c["rows"]}
        ok(set(rows) == {"0006", "0007", "0008", "0009"}, f"아이만 (선생님 #0000 · 공용 패드 · 빈 태그 빼고) {list(rows)}")
        ok(rows["0006"][1] == "자동" and not rows["0006"][2] and rows["0007"][1] == "G3-4" and rows["0007"][2] and rows["0009"][1] == "빼기", f"지금 단계 보임 {c['rows']}")
        ok("자동 (G1-2)" in c["t"] and "정한 아이 2명" in c["h"] and "시트" in c["t"], f"자동 = 지금 자동 학년 · 정한 아이 수 · 시트 안내 {c['h']}")
        ok(c["docW"] <= 0, f"휴대폰 가로 넘침 없음 {c['docW']}")
        await pg.screenshot(path=OUT + "ph.png")
        # 고르면 바로 저장
        await pg.select_option('select[data-rlv="0006"]', "G3-4"); await pg.wait_for_timeout(600)
        P = [x for x in await pg.evaluate("()=>_posts") if x.get("type") == "tagLv"]
        ok(P and P[-1]["tags"] == ["0006"] and P[-1]["lv"] == "G3-4" and P[-1].get("tk") == "testkey", f"고르면 바로 tagLv {P[-1:] }")
        c = await pg.evaluate(CARD); rows = {r[0]: r for r in c["rows"]}
        m = await pg.evaluate("()=>document.getElementById('adMsg').textContent")
        ok(rows["0006"][1] == "G3-4" and rows["0006"][2] and "정한 아이 3명" in c["h"] and "G3-4" in m, f"저장 뒤 표시 · 알림 {m}")
        # 찾기
        await pg.fill("#adRlvQ", "다솜"); await pg.wait_for_timeout(400)
        c = await pg.evaluate(CARD); ok([r[0] for r in c["rows"]] == ["0008"], f"찾기 = 다솜만 {c['rows']}")
        ok(await pg.evaluate("()=>document.activeElement && document.activeElement.id==='adRlvQ'"), "찾는 칸 글쓰기 그대로 (포커스)")
        # 한꺼번에: 모두(찾은 아이만) → 중등
        await pg.click('[data-ad="rlvAll"]'); await pg.wait_for_timeout(300)
        await pg.fill("#adRlvQ", ""); await pg.wait_for_timeout(300)
        await pg.click('[data-ad="rlvPick"][data-tag="0007"]'); await pg.wait_for_timeout(300)
        await pg.select_option("#adRlvTo", "중등"); await pg.click('[data-ad="rlvSet"]'); await pg.wait_for_timeout(600)
        P = [x for x in await pg.evaluate("()=>_posts") if x.get("type") == "tagLv"]
        ok(sorted(P[-1]["tags"]) == ["0007", "0008"] and P[-1]["lv"] == "중등", f"한꺼번에 2명 → 중등 {P[-1]}")
        c = await pg.evaluate(CARD); rows = {r[0]: r for r in c["rows"]}
        ok(rows["0007"][1] == "중등" and rows["0008"][1] == "중등" and rows["0006"][1] == "G3-4", f"바뀐 뒤 {c['rows']}")
        ok(await pg.evaluate("()=>document.querySelectorAll('[data-ad=rlvPick]:checked').length") == 0, "바꾼 뒤 고르기 풀림")
        # 자동으로 되돌리기
        await pg.select_option('select[data-rlv="0009"]', "자동"); await pg.wait_for_timeout(600)
        P = [x for x in await pg.evaluate("()=>_posts") if x.get("type") == "tagLv"]
        c = await pg.evaluate(CARD); rows = {r[0]: r for r in c["rows"]}
        ok(P[-1]["lv"] == "자동" and rows["0009"][1] == "자동" and not rows["0009"][2], "빼기 → 자동")
        await pg.screenshot(path=OUT + "ph_after.png")
        # 아이 화면 🔒
        r = await pg.evaluate("""()=>{ Admin.close && Admin.close(); LiveRank.B={study:[{nick:'가온',tag:'0006',score:55,n:1}], words:[], run:[], me:{study:{nick:'가온',tag:'0006',score:55,n:1,rank:1,of:1,lv:'G3-4',fix:1}}};
            const a=rankWeekRows('study'); LiveRank.B.me.study.fix=0; const b2=rankWeekRows('study'); return [a, b2]; }""")
        ok("🔒 선생님이 정함" in r[0] and "🔒" not in r[1] and "G3-4" in r[0], "아이 랭킹: 선생님이 정하면 🔒 · 자동이면 없음")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await pg.close()
        # 옛 서버 (v14) → 안내 · 바꾸기 못 함
        pg, errs = await setup(b, {"width": 820, "height": 1180}, v=14)
        await pg.evaluate(OPEN)
        c = await pg.evaluate(CARD)
        ok(c and "v15" in c["t"] and not c["rows"], f"옛 서버 = 새 Code.gs 붙여 넣기 안내 {c and c['t'][:80]}")
        await pg.close()
        # 패드 · 가로 휴대폰 · 가로 패드 · TV
        for nm, vp, kw in (("pad", {"width": 820, "height": 1180}, {"is_mobile": True, "has_touch": True}), ("phL", {"width": 915, "height": 412}, {"is_mobile": True, "has_touch": True}),
                           ("padL", {"width": 1180, "height": 820}, {"is_mobile": True, "has_touch": True}), ("tv", {"width": 1920, "height": 1080}, {})):
            pg, errs = await setup(b, vp, **kw)
            await pg.evaluate(OPEN); await pg.wait_for_timeout(300)
            c = await pg.evaluate(CARD)
            box = await pg.evaluate("""()=>{ const c=[...document.querySelectorAll('#adBody .adCard')].find(x=>/랭킹 단계/.test((x.querySelector('h3')||{textContent:''}).textContent)); const r=c.getBoundingClientRect(); const s=c.querySelector('select[data-rlv]').getBoundingClientRect(); return [Math.round(r.width), Math.round(s.right-r.right), Math.round(s.height)]; }""")
            ok(c and len(c["rows"]) == 4 and c["docW"] <= 0 and box[1] <= 0 and box[2] >= 24, f"{nm} 카드 · 넘침 없음 · 고르기 칸 안 잘림 {box} {c and c['docW']}")
            await pg.screenshot(path=f"{OUT}{nm}.png")
            e = real_errs(errs); ok(not e, f"{nm} 오류 없음 {e[:3]}")
            await pg.close()
        await b.close()
    r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gs_rank631.js")], capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[:300])
    ok(r.returncode == 0, "서버 Code.gs 랭킹 단계 (gs_rank631.js)")
    r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gs_own657.js")], capture_output=True, text=True)
    print(r.stdout[-600:])
    ok(r.returncode == 0, "서버 v22 🧸 주인 패드 아이 유치원 책도 랭킹 (gs_own657.js)")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
