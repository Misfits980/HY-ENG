"""(v404) 🏷 태그 — 사용자: "이름 바꿀 때 태그 — 구글 시트도 애들도 다 · #0000 나 · #0001~#0005 공용 패드 · 이름만 바꾸고 태그는 못 바꾸게"
  ① 이름을 처음 정하면 시트 서버에 태그 요청 → 기기에 저장 · 설정 이름 카드에 '이름#번호' (태그 바꾸는 칸 없음)
  ② 이름을 바꿔도 태그 그대로 · 모든 기록(판·이름·구매)에 tag · 조치 받기에 tag
  ③ 공용 패드 = pad:1 (#0001~) · 기록 tag 는 비움(여러 아이가 씀)
  ④ 랭킹 줄에 #번호 · 내 줄 = 태그로
  ⑤ 서버 Code.gs 태그 (node tools/tests/gs_tag.js)"""
import asyncio, sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
MOCK="""()=>{ window.__log=[]; window.__map={}; Online.on=()=>true;
  Online.post=b=>{ __log.push(JSON.parse(JSON.stringify(b))); if(b.type==='tag'){ if(!b.nick) return Promise.resolve({ok:false, err:'noname'}); let t=__map[b.dev]; if(!t){ t=b.pad ? '0001' : String(6+Object.values(__map).filter(x=>x>='0006').length).padStart(4,'0'); __map[b.dev]=t; } return Promise.resolve({ok:true, tag:t}); } return Promise.resolve({ok:true}); }; }"""
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={"width":390,"height":844})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_tag'); localStorage.removeItem('hyeng_nick'); localStorage.removeItem('hyeng_name_v1'); }")
        await pg.evaluate(MOCK)
        ok(await pg.evaluate("()=>Tag.sync()")=="" and not any(x.get("type")=="tag" for x in await pg.evaluate("()=>__log")), "이름이 없으면 태그를 안 받음")
        await pg.evaluate("()=>{ openSettings(); document.getElementById('nick').value='스트로베리'; NameCard.click('ok'); }")
        await pg.wait_for_timeout(1200)
        ok(await pg.evaluate("()=>Tag.get()")=="0006", "처음 이름을 정하면 태그 #0006")
        t=await pg.evaluate("()=>document.getElementById('nmRow').innerText")
        ok("스트로베리#0006" in t.replace(" ","").replace("🏷","") and "바꿔도 그대로" in t, f"설정 이름 카드에 이름#번호 {t!r}")
        ok(await pg.evaluate("()=>!document.querySelector('#nmRow input')"), "태그를 바꾸는 칸은 없음")
        await pg.evaluate("()=>{ NameCard.give(1); NameCard.click('edit'); document.getElementById('nick').value='딸기'; NameCard.click('ok'); }"); await pg.wait_for_timeout(1200)
        ok(await pg.evaluate("()=>NameCard.cur()")=="딸기" and await pg.evaluate("()=>Tag.get()")=="0006", "이름을 딸기로 바꿔도 태그 #0006 그대로")
        L=await pg.evaluate("()=>__log")
        nm=[x for x in L if x.get("type")=="name"]
        ok(len(nm)==2 and nm[1]["tag"]=="0006" and nm[1]["old"]=="스트로베리", "이름 기록(시트 '이름' 탭)에 태그")
        await pg.evaluate("()=>Online.submit({nick:'딸기', score:100, diff:'easy', rule:'normal'})")
        L=await pg.evaluate("()=>__log"); ok(L[-1].get("tag")=="0006", "판 기록(scores)에 태그 칸")
        ok("tag=0006" in await pg.evaluate("()=>{ let u=''; const f=window.fetch; window.fetch=x=>{ u=String(x); return Promise.reject(); }; Online.acts(); window.fetch=f; return u; }"), "조치 받기에 태그 (대상 #0006)")
        h=await pg.evaluate("()=>onlineRows([{nick:'딸기', tag:'0006', score:900, me:true},{nick:'민준', tag:'0007', score:800},{nick:'옛날', score:10}])")
        ok("#0006" in h and "#0007" in h and h.count("rkTag")==2, "랭킹 줄에 #번호 (태그 없는 옛 기록은 이름만)")
        # 공용 패드
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드1'); localStorage.removeItem('hyeng_tag'); __map={}; Tag._busy=null; }")
        await pg.evaluate("()=>Tag.sync()")
        L=await pg.evaluate("()=>__log"); tg=[x for x in L if x.get("type")=="tag"][-1]
        ok(tg.get("pad")==1 and await pg.evaluate("()=>Tag.get()")=="0001", "공용 패드 = pad:1 → #0001")
        await pg.evaluate("()=>Online.submit({nick:'한양패드1', score:5, diff:'easy', rule:'normal'})")
        L=await pg.evaluate("()=>__log"); ok(L[-1].get("tag")=="", "공용 패드 기록의 태그 칸은 비움 (여러 아이가 써서)")
        # ⑥ 관리 화면 — 이 기기 태그 · #0000 · 태그 목록 · 옮기기
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','선생님'); localStorage.setItem('hyeng_tag','0009'); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }")
        await pg.reload(); await pg.wait_for_timeout(1500); await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }")
        await pg.evaluate("""()=>{ window._posts=[]; Online.submit=o=>{ window._posts.push(o); if(o.type==='report') return Promise.resolve({ok:true, rep:{nicks:[], weekly:[['아이','들어온 날'],['민준','4']]}});
            if(o.type==='tags') return Promise.resolve({ok:true, list:[{tag:'0000',dev:'',first:'',nick:'',memo:'나 (선생님)'},{tag:'0001',dev:'p1',first:'한양패드1',nick:'한양패드1'},{tag:'0006',dev:'dA',first:'스트로베리',nick:'딸기'},{tag:'0007',dev:'dB',first:'민준',nick:'민준'}]});
            if(o.type==='check') return Promise.resolve({ok:true, v:4}); return Promise.resolve({ok:true, tag:'0000'}); };
          Notice.fetch=()=>Promise.resolve({v:4, notices:[]}); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); window.confirm=()=>true; }""")
        await pg.evaluate("()=>{ Admin.open(); Admin._tab('dev'); }"); await pg.wait_for_timeout(1500)
        t=await pg.evaluate("()=>document.querySelector('.adMeTag') ? document.querySelector('.adMeTag').innerText : ''")
        if not t: print("DBG", (await pg.evaluate("()=>document.body.innerText"))[:600]); await pg.screenshot(path=OUT+"tag_dbg.png")
        ok("#0009" in t and "#0000" in t, f"📊 이 기기: 태그 #0009 · 「이 기기 = #0000」 {t!r}")
        await pg.click('[data-ad="tagMe"]'); await pg.wait_for_timeout(600)
        ok(any(x.get("type")=="tagMe" for x in await pg.evaluate("()=>_posts")) and await pg.evaluate("()=>Tag.get()")=="0000", "#0000 (선생님) 으로")
        await pg.evaluate("()=>Admin._tab('class')"); await pg.wait_for_timeout(2000)
        t=await pg.evaluate("()=>document.body.innerText")
        ok("🏷 태그" in t and "#0006" in t and "딸기" in t and "스트로베리" in t, "📋 우리 반: 🏷 태그 목록 (지금 이름 · 처음 이름)")
        await pg.evaluate("()=>{ const d=document.querySelector('.adMore summary'); document.querySelectorAll('details.adMore').forEach(x=>x.open=true); }")
        await pg.fill("#adTagT", "0007"); await pg.fill("#adTagD", "newdevB"); await pg.click('[data-ad="tagMove"]'); await pg.wait_for_timeout(500)
        mv=[x for x in await pg.evaluate("()=>_posts") if x.get("type")=="tagSet"]
        ok(mv and mv[-1]["tag"]=="0007" and mv[-1]["dev"]=="newdevB", "태그에 기기 더하기 (#0007 ← 새 기기)")
        await pg.screenshot(path=OUT+"tag_admin.png", full_page=False)
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:2]))
        await br.close()
    r=subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)),"gs_tag.js")], capture_output=True, text=True); print(r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr)
    ok(r.returncode==0, "서버 Code.gs 태그 (gs_tag.js)")
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
