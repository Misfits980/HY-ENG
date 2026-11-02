# v548 관리 화면 — 카드 접고 펼치기 · 기억 · 모두 펼치기/접기 · 탭 밑판 · 안의 단추
import asyncio, sys
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
OUT="/tmp/claude-0/adm/"
R=[]
def ok(c,m): R.append(bool(c)); print(("✅ " if c else "❌ ")+m)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T=await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(T); E=T.evaluate
        await E("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); localStorage.removeItem('hyeng_admin_acc'); }")
        await T.reload(); await T.wait_for_timeout(1500); await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        await E("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); }")
        await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); Admin._tab('work'); }"); await T.wait_for_timeout(1500)
        st=await E("()=>[...document.querySelectorAll('#adBody section.adCard.acc')].map(s=>(s.classList.contains('shut')?'-':'+')+s.dataset.acc)")
        print(st)
        ok(len(st)>=5, f"숙제·시험 카드 {len(st)}개 접기 가능")
        ok(any(x.startswith('-') and '시험지' in x for x in st) and any(x.startswith('+') and '숙제내기' in x for x in st), "처음: 숙제 내기 펼침 · 시험지 접힘")
        ok(await E("()=>!!document.getElementById('adAccBar')"), "모두 펼치기·접기 줄")
        H=lambda k: E("(k)=>{ const s=[...document.querySelectorAll('#adBody section.adCard.acc')].find(x=>x.dataset.acc.includes(k)); return s ? [s.classList.contains('shut'), Math.round(s.getBoundingClientRect().height)] : null; }", k)
        h0=await H("시험지")
        await E("()=>[...document.querySelectorAll('#adBody section.adCard.acc')].find(x=>x.dataset.acc.includes('시험지')).querySelector('h3').click()")
        await T.wait_for_timeout(160); mid=await H("시험지")
        await T.screenshot(path=OUT+"acc_mid.png")
        await T.wait_for_timeout(700); h1=await H("시험지")
        print(h0, mid, h1)
        ok(not h1[0] and h1[1]>h0[1]+40 and h0[1]<mid[1]<h1[1], f"제목 누르면 촤라락 펼침 (높이 {h0[1]} → {mid[1]} → {h1[1]})")
        await T.screenshot(path=OUT+"acc_open.png")
        # 안의 단추가 그대로 동작
        await E("()=>{ const b=[...document.querySelectorAll('#adBody [data-ad]')].find(x=>/시험지 만들기/.test(x.textContent)); b.click(); }"); await T.wait_for_timeout(800)
        ok(await E("()=>!!document.getElementById('paper')"), "펼친 카드 안 「시험지 만들기」 단추 동작")
        await E("()=>Paper.close()")
        # 다시 그려도 그대로 · 닫았다 열어도 기억
        await E("()=>Admin._tab('work')"); await T.wait_for_timeout(600)
        ok((await H("시험지"))[0] is False, "다시 그려도 펼친 채로")
        await E("()=>{ Admin.close(); Admin.open(); }"); await T.wait_for_timeout(800)
        ok((await H("시험지"))[0] is False, "닫았다 열어도 기억")
        # 모두 접기
        await E("()=>document.querySelector('#adAccBar [data-acc=\"0\"]').click()"); await T.wait_for_timeout(1200)
        n=await E("()=>[...document.querySelectorAll('#adBody section.adCard.acc')].filter(s=>!s.classList.contains('shut')).length")
        ok(n==0, f"모두 접기 → 펼친 카드 {n}")
        sh=await E("()=>document.querySelector('#shAdmin .sheetIn').scrollHeight")
        ok(sh<1100, f"모두 접으면 짧아짐 (높이 {sh})")
        await T.screenshot(path=OUT+"acc_allshut.png")
        await E("()=>document.querySelector('#adAccBar [data-acc=\"1\"]').click()"); await T.wait_for_timeout(1400)
        n=await E("()=>[...document.querySelectorAll('#adBody section.adCard.acc')].filter(s=>s.classList.contains('shut')).length")
        ok(n==0, f"모두 펼치기 → 접힌 카드 {n}")
        # 접힌 칸 안은 탭 키로 안 들어감
        await E("()=>[...document.querySelectorAll('#adBody section.adCard.acc')].find(x=>x.dataset.acc.includes('숙제내기')).querySelector('h3').click()"); await T.wait_for_timeout(800)
        vis=await E("()=>{ const s=[...document.querySelectorAll('#adBody section.adCard.acc')].find(x=>x.dataset.acc.includes('숙제내기')); return getComputedStyle(s.querySelector('.adAccIn')).visibility; }")
        ok(vis=="hidden", f"접힌 칸은 숨김 (visibility {vis})")
        # 키보드
        await E("()=>{ const h=[...document.querySelectorAll('#adBody section.adCard.acc')].find(x=>x.dataset.acc.includes('숙제내기')).querySelector('h3'); h.focus(); }")
        await T.keyboard.press("Enter"); await T.wait_for_timeout(700)
        ok((await H("숙제내기"))[0] is False, "Enter 로 펼침")
        # 탭 밑판
        ind=await E("()=>{ const i=document.querySelector('#adTabs .adTabInd'), on=document.querySelector('#adTabs button.on'); return i&&on ? [Math.round(i.getBoundingClientRect().left), Math.round(on.getBoundingClientRect().left), Math.round(i.offsetWidth), on.offsetWidth] : null; }")
        ok(ind and abs(ind[0]-ind[1])<=2 and abs(ind[2]-ind[3])<=2, f"탭 밑판이 고른 탭 위 {ind}")
        await E("()=>document.querySelector('#adTabs [data-t=class]').click()"); await T.wait_for_timeout(120)
        await T.screenshot(path=OUT+"acc_tabslide.png"); await T.wait_for_timeout(900)
        ind=await E("()=>{ const i=document.querySelector('#adTabs .adTabInd'), on=document.querySelector('#adTabs button.on'); return [Math.round(i.getBoundingClientRect().left), Math.round(on.getBoundingClientRect().left)]; }")
        ok(abs(ind[0]-ind[1])<=2, f"아이들 탭으로 미끄러짐 {ind}")
        tm=await E("()=>document.querySelectorAll('#adBody section.adTm.acc').length")
        ok(tm==0, "반 명단 카드(제목에 단추)는 접기 없음")
        hh=await E("()=>document.querySelector('#shAdmin .sheetIn').getBoundingClientRect().height")
        await E("()=>Admin._tab('time')"); await T.wait_for_timeout(600)
        hh2=await E("()=>document.querySelector('#shAdmin .sheetIn').getBoundingClientRect().height")
        ok(abs(hh-hh2)<2, f"탭을 바꿔도 창 높이 그대로 ({hh:.0f} / {hh2:.0f})")
        # 잠금 화면은 짧게
        await E("()=>document.getElementById('adLockBtn').click()"); await T.wait_for_timeout(200); await E("()=>Admin.open()"); await T.wait_for_timeout(400)
        lk=await E("()=>[document.querySelector('#shAdmin .sheetIn').classList.contains('okd'), !!document.getElementById('adPin'), getComputedStyle(document.getElementById('btnAdminClose')).display]")
        ok(lk[0] is False and lk[1] and lk[2]!='none', f"잠금 화면은 예전처럼 {lk}")
        ok(not errs, f"오류 없음 {errs}")
        await br.close()
    print(f"{sum(R)}/{len(R)}")
asyncio.run(main())
