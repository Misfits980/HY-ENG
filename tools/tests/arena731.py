"""(v731) 💦 물총 아레나 점검 고침 + 🎯 연습장 + 따라잡기 — 사용자 「물총아레나는 버그가 많을 수 있어 확인을 하나씩 해 봐」 · 「패드 세로 물총 작게」 · 「연습장 + 따라잡기」
   ① 워터파크 다리 위 나오는 자리 = 다리 위 (전: 높이 0 = 파란 덩어리 속) · 아이템도 다리 위
   ② 같은 화면에서 새 판 = 모두 1단계부터 (전: 봇이 앞 판 단계 그대로 → 몇 초 만에 끝)
   ③ 봇: 벽에 붙은 막힘 칸 · 갈 수 없는 상대 → 멈추지 않고 다른 곳으로 (맵 3 × 2분 · 4초 넘게 멈춘 봇 0)
   ④ 화면 5가지: 단추·글자 화면 안 · 안 겹침 (전: 휴대폰 세로 「☰ 메뉴」+무기 줄 · 패드 세로 쏘기+점프 · 낮은 가로 안내+슬라이드) · 패드 세로 물총 0.74배
   ⑤ 🎯 연습장: 혼자 하기 카드(처음 = 연습장 먼저) → 걷기 → 둘러보기 → 풍선 5개 → 슬라이드 점프 → 🪙5 한 번 → 바로 대결
   ⑥ 따라잡기: 1~2단계에서 두 번 연속 흠뻑 → 다시 나오면 다음 무기 · 처음 기기 = 🐣 쉬움 · 혼자 앞선 사람을 봇이 더 노림"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from arena599 import boot
from playwright.async_api import async_playwright

PLAY = """(df)=>{ const R=MG.run; if(df) R.SET.diff=df; R.beginSolo(); for(let i=0;i<200 && R.phase!=='play';i++) MG.step(.05,false); for(let i=0;i<90 && R.time.cd>0;i++) MG.step(.05,false); return R.phase; }"""
CHK = """()=>{ const q=s=>[...document.querySelectorAll(s)].filter(e=>{ const r=e.getBoundingClientRect(), cs=getComputedStyle(e); return r.width>0 && r.height>0 && cs.visibility!=='hidden' && cs.display!=='none' && +cs.opacity>0.05; });
  const N={fire:'#mgUI [data-b=fire]', jump:'#mgUI [data-b=jump]', slide:'#mgUI [data-b=slide]', pz:'#mgUI .aPzB', clock:'#mgUI .aClock', lad:'#mgUI .aLad', board:'#mgUI .aBd', soak:'#mgUI .aSoak', wpn:'#mgUI .aWpn', hint:'#mgUI .aHint'};
  const R={}; for(const k in N){ const e=q(N[k])[0]; if(e){ const r=e.getBoundingClientRect(); R[k]=[r.left,r.top,r.right,r.bottom]; } }
  const out=[], ov=(a,b)=>a[0]<b[2]-2 && b[0]<a[2]-2 && a[1]<b[3]-2 && b[1]<a[3]-2, ks=Object.keys(R);
  for(const k of ks){ const r=R[k]; if(r[0]<-1||r[1]<-1||r[2]>innerWidth+1||r[3]>innerHeight+1) out.push('밖:'+k); }
  for(let i=0;i<ks.length;i++) for(let j=i+1;j<ks.length;j++) if(ov(R[ks[i]],R[ks[j]])) out.push(ks[i]+'+'+ks[j]);
  return [out, Object.keys(R).length, +MG.run.VM.scale.x.toFixed(2)]; }"""
AIMAT = """(tp)=>{ const R=MG.run, me=R.me, e=new THREE.Vector3(me.p.x, me.p.y+1.48, me.p.z), dx=tp[0]-e.x, dy=tp[1]-e.y, dz=tp[2]-e.z; me.yaw=Math.atan2(-dx,-dz); me.pitch=Math.atan2(dy, Math.hypot(dx,dz)); }"""

async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx, P, errs = await boot(br, 844, 390); E = P.evaluate
        await E("()=>MG.lobby('arena')"); await P.wait_for_timeout(1600)
        # ⑥ 처음 기기 = 쉬움
        r = await E("()=>[MG.run.SET.diff, document.querySelector('#mgUI .aSide [data-c=solo] small').textContent]")
        ok(r[0] == "easy" and "쉬움" in r[1], f"⑥ 처음 하는 기기 = 🐣 쉬움 {r}")
        # ① 다리 위 나오는 자리 · 아이템
        r = await E("""()=>{ const R=MG.run; R.setMap('pool'); const me=R.me; const out=[]; for(const s of [[-19,-4],[19,4]]){ const gy=R.groundY(s[0],s[1]); out.push(+gy.toFixed(2)); } const q=R.pkSpawn('shoe', [-19,-4]); const y=q?+q.g.position.y.toFixed(2):-1; if(q){ R.PKS.splice(R.PKS.indexOf(q),1); R.scene.remove(q.g); } return [out, y]; }""")
        ok(r[0] == [2.4, 2.4] and r[1] == 2.4, f"① 워터파크 다리 위 자리 높이 2.4 · 아이템도 다리 위 {r}")
        r = await E("""()=>{ const R=MG.run, me=R.me, B=R.BOX; let ins=0, n=0; for(let k=0;k<60;k++){ R.spawn(me); n++; const p=me.p; if(B.some(b=>p.x-.3<b.x1&&p.x+.3>b.x0&&p.y+.05<b.y1&&p.y+1.7>b.y0&&p.z-.3<b.z1&&p.z+.3>b.z0)) ins++; } return [n, ins]; }""")
        ok(r[1] == 0, f"① 나오기 60번 · 상자 속 0 {r}")
        # ② 새 판 = 처음부터
        await E(PLAY, "normal")
        await E("()=>{ const R=MG.run; R.ACT.forEach(a=>{ a.wi=6; a.kills=9; }); R.time.over=true; }")
        await E(PLAY, "normal")
        r = await E("()=>{ const R=MG.run; return [R.ACT.map(a=>a.wi).join(','), R.ACT.map(a=>a.kills).join(','), R.time.over, Math.round(R.time.left)]; }")
        ok(r[0] == "0,0,0,0,0,0" and r[1] == "0,0,0,0,0,0" and r[2] is False and r[3] == 300, f"② 다시 시작 = 모두 1단계 · 0명 · 5분 {r}")
        # ③ 봇 멈춤 없음 (맵 3 × 120초 · 나는 안 젖음)
        STILL = """([mp])=>{ const R=MG.run; R.setMap(mp); R.SET.diff='easy'; R.beginSolo(); for(let i=0;i<200 && R.phase!=='play';i++) MG.step(.05,false); for(let i=0;i<90 && R.time.cd>0;i++) MG.step(.05,false); R.D.dm=0;
            const st=new Map(R.ACT.map(a=>[a,{lp:a.p.clone(), s:0, mx:0}])); for(let t=0;t<120 && !R.time.over;t+=.05){ MG.step(.05,false); for(const a of R.ACT){ if(!a.bot || !a.alive) continue; const s=st.get(a); if(a.p.distanceTo(s.lp)<.02){ s.s+=.05; s.mx=Math.max(s.mx,s.s); } else s.s=0; s.lp.copy(a.p); } }
            return Math.max(...[...st.values()].map(s=>s.mx)).toFixed(1); }"""
        for mp in ("pool", "sand", "toy"):
            r = await E(STILL, [mp]); ok(float(r) <= 4, f"③ {mp}: 가장 오래 멈춘 봇 {r}초 (4초 아래)")
        await E("()=>{ const el=document.querySelector('#mgUI .puR'); if(el) el.remove(); MG.run.setMap('pool'); }")
        # ⑥ 따라잡기 — 두 번 연속 흠뻑 → 다시 나오면 다음 무기
        await E(PLAY, "normal")
        r = await E("""()=>{ const R=MG.run, me=R.me, b=R.ACT.find(a=>a.bot); me.wi=0; R.vmSet(0); me.chain=0; const out=[];
            for(let k=0;k<2;k++){ me.prot=0; me.alive=true; R.hurt(me, 150, b, 0, false, b.p, true); for(let i=0;i<70;i++) MG.step(.05,false); out.push(me.wi); } return out; }""")
        await P.wait_for_timeout(3200)
        r2 = await E("()=>{ for(let i=0;i<4;i++) MG.step(.05,false); return MG.run.me.wi; }")
        ok(r[0] == 0 and r2 == 1, f"⑥ 1단계에서 두 번 연속 흠뻑 → 다음 무기 (한 번 뒤 {r[0]} · 두 번 뒤 {r2})")
        # ⑤ 연습장
        await E("()=>{ const el=document.querySelector('#mgUI .puR'); if(el) el.remove(); }")
        await E("()=>MG.run.card('solo')"); await P.wait_for_timeout(150)
        r = await E("()=>[...document.querySelectorAll('#mgUI .aCard [data-go]')].map(b=>b.dataset.go).join(',')")
        ok(r.startswith("prac,solo"), f"⑤ 처음 = 혼자 하기 카드에 연습장 먼저 {r}")
        c0 = await E("()=>TECO.coins()")
        await E("()=>document.querySelector('#mgUI .aCard [data-go=prac]').click()"); await P.wait_for_timeout(300)
        r = await E("()=>{ const R=MG.run; return [R.phase, R.ACT.length, document.getElementById('mgUI').classList.contains('aPrac'), getComputedStyle(document.querySelector('#mgUI .aClock')).display, document.querySelector('#mgUI .aPr').textContent.includes('동그라미')]; }")
        ok(r == ["prac", 1, True, "none", True], f"⑤ 연습장: 봇 없음 · 시계·무기 줄 숨김 · ① 걷기 안내 {r}")
        await P.screenshot(path=OUT + "arena731_prac.png")
        r = await E("""()=>{ const R=MG.run, me=R.me, I=MG.I, m=R.PR.mk.position; let k=0; for(;k<500 && R.PR.step===0 && !(R.PR.wait>0);k++){ const dx=m.x-me.p.x, dz=m.z-me.p.z; me.yaw=Math.atan2(-dx,-dz); I.my=1; MG.step(.016,false); } I.my=0; for(let i=0;i<70;i++) MG.step(.016,false); return R.PR.step; }""")
        ok(r == 1, f"⑤ 동그라미까지 걸으면 ② 둘러보기 {r}")
        b = await E("()=>{ const b=MG.run.PR.look; return [b.c.x,b.c.y,b.c.z]; }"); await E(AIMAT, b)
        r = await E("()=>{ for(let i=0;i<80;i++) MG.step(.016,false); return MG.run.PR.step; }")
        ok(r == 2, f"⑤ 풍선을 보면 ③ 쏘기 {r}")
        for i in range(8):
            b = await E("()=>{ const R=MG.run, b=R.PR && R.PR.step===2 && R.PR.bal[0]; return b?[b.c.x,b.c.y,b.c.z]:null; }")
            if not b: break
            await E(AIMAT, b); await E("()=>{ const R=MG.run, I=MG.I; R.me.cd=0; I.fire=1; MG.step(.016,false); I.fire=0; for(let i=0;i<25;i++) MG.step(.016,false); }")
        r = await E("()=>{ const R=MG.run; for(let i=0;i<80;i++) MG.step(.016,false); return [R.PR.step, R.PR.n]; }")
        ok(r[0] == 3 and r[1] >= 5, f"⑤ 풍선 5개 → ④ 슬라이드 점프 {r}")
        r = await E("""()=>{ const R=MG.run, me=R.me, I=MG.I; let by=0, bd=-1; for(let j=0;j<24;j++){ const y=j*Math.PI/12; let d=1; for(;d<16;d+=.5){ const x=me.p.x-Math.sin(y)*d, z=me.p.z-Math.cos(y)*d; if(!R.sees(new THREE.Vector3(me.p.x,me.p.y+.6,me.p.z), new THREE.Vector3(x,me.p.y+.6,z)) || Math.abs(R.groundY(x,z)-me.p.y)>.3) break; } if(d>bd){ bd=d; by=y; } } me.yaw=by;
            let k=0; for(;k<300;k++){ I.my=1; if(k===50) I.slideP=1; if(k===56) I.jumpP=1; MG.step(.016,false); if(R.PR && R.PR.wait>0) break; } I.my=0; for(let i=0;i<90;i++) MG.step(.016,false); return [document.querySelector('#mgUI .aCardW').classList.contains('on'), document.querySelector('#mgUI .aCard').textContent.slice(0,30)]; }""")
        c1 = await E("()=>TECO.coins()")
        ok(r[0] and "연습 끝" in r[1] and c1 == c0 + 5, f"⑤ 슬라이드 점프 → 연습 끝 · 🪙 {c0}→{c1} {r}")
        await P.screenshot(path=OUT + "arena731_prac_done.png")
        await E("()=>document.querySelector('#mgUI .aCard [data-go=solo2]').click()")
        r = await E("()=>{ const R=MG.run; for(let i=0;i<200 && R.phase!=='play';i++) MG.step(.05,false); return [R.phase, R.ACT.length, !!R.PR, document.getElementById('mgUI').classList.contains('aPrac')]; }")
        ok(r == ["play", 6, False, False], f"⑤ 「혼자 대결 시작」 → 봇 5명 판 {r}")
        await E("()=>MG.run.card('solo')"); await P.wait_for_timeout(100)
        r = await E("()=>[...document.querySelectorAll('#mgUI .aCard [data-go]')].map(b=>b.dataset.go).join(',')")
        ok(r.startswith("solo,prac"), f"⑤ 다음부터는 바로 시작이 먼저 · 연습장은 다시 하기 {r}")
        # 연습장 두 번째 = 🪙 없음
        await E("()=>document.querySelector('#mgUI .aCard [data-go=prac]').click()")
        r = await E("()=>{ const R=MG.run; R.PR.step=3; R.PR.wait=0; const c=TECO.coins(); R.me.sl=true; for(let i=0;i<3;i++) MG.step(.016,false); R.me.sl=false; R.me.onG=false; R.me.v.set(8,4,0); MG.step(.016,false); for(let i=0;i<90;i++) MG.step(.016,false); return [document.querySelector('#mgUI .aCard').textContent.includes('🪙'), TECO.coins()-c]; }")
        ok(r == [False, 0], f"⑤ 연습장 두 번째 = 🪙 없음 {r}")
        # (v734) 크롬 실제 화면: ⭕ 가 워터파크 다리 위(2.4m)에 놓여 아래서는 안 보였음 → 내 바닥 높이 · 눈에서 보임 (맵 3 × 나오는 자리 20)
        r = await E("""()=>{ const R=MG.run, out={}; let root=R.cam; while(root.parent) root=root.parent; const rc=new THREE.Raycaster(); rc.camera=R.cam;
          for(const m of ['pool','sand','toy']){ R.setMap(m); let hi=0, hid=0, n=0; for(let k=0;k<20;k++){ R.pracStart(); const me=R.me, mk=R.PR.mk; if(!mk) continue; n++; const p=mk.position;
              if(Math.abs(p.y-me.p.y)>.3) hi++; mk.visible=false; const o=new THREE.Vector3(me.p.x, me.p.y+1.5, me.p.z), t=new THREE.Vector3(p.x, p.y+.3, p.z), d=t.clone().sub(o), L=d.length(); rc.set(o, d.normalize()); rc.far=L-.2;
              if(rc.intersectObjects(root.children, true).some(h=>h.object.visible && h.object.type==='Mesh' && !(h.object.material && h.object.material.transparent))) hid++; mk.visible=true; }
            out[m]=[n, hi, hid]; } R.setMap('pool'); return out; }""")
        ok(all(v[0] == 20 and v[1] == 0 and v[2] <= 1 for v in r.values()), f"⑤ 연습장 ⭕ = 내 바닥 높이 · 눈에서 보임 (나옴·높음·가림) {r}")
        # (v734) 연습장 중에 바로 시작 / 친구랑 → 연습 안내·숨긴 시계가 남지 않음 (크롬 실제 화면에서 찾음)
        r = await E("""()=>{ const R=MG.run, u=document.getElementById('mgUI'), a=[]; R.pracStart(); R.beginSolo(); a.push(!R.PR, !u.classList.contains('aPrac')); R.pracStart(); R.goCo(); a.push(!R.PR, !u.classList.contains('aPrac')); return a; }""")
        ok(r == [True, True, True, True], f"⑤ 연습장 중 혼자 시작·친구랑 = 연습 끝남 {r}")
        E1 = real_errs(errs); await ctx.close()
        # ④ 화면 5가지
        E2 = []
        for nm, w, h in (("phoneP", 390, 844), ("phoneL", 844, 390), ("padP", 820, 1180), ("padL", 1180, 820), ("smallL", 667, 375)):
            ctx, Q, e3 = await boot(br, w, h)
            await Q.evaluate("()=>MG.lobby('arena')"); await Q.wait_for_timeout(1400); await Q.evaluate(PLAY, "normal"); await Q.evaluate("()=>{ MG.I.touch=true; }"); await Q.wait_for_timeout(600)
            r = await Q.evaluate(CHK)
            ok(not r[0] and r[1] >= 8 and (r[2] == .74 if nm == "padP" else r[2] == 1), f"④ {nm}: 겹침·밖 없음 · 물총 크기 {r[2]} {r[0]}")
            await Q.screenshot(path=OUT + f"arena731_{nm}.png")
            E2 += real_errs(e3); await ctx.close()
        ok(not E1 and not E2, f"오류 없음 {(E1+E2)[:3]}")
        await br.close()
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
