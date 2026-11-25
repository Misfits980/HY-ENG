"""(v730) 💦 물총 아레나 손맛 — 사용자 「저격총이 에임이 없더라 줌하면 · 공격한다는 느낌도 없어 · 좀 더 잘 다듬어 줘야 할 듯」
   ① 🎯 저격 줌 = 조준경(원 · 십자선 · 빨간 점 · 「떼면 쏴요!」) · 조준점이 상대 위면 초록 「지금 떼요!」(머리면 ⭐) · 떼면 쏘고 조준경 사라짐
   ② 쏠 때: 카메라가 살짝 튐(무기마다) · 총 끝 물보라 · 내 물줄기 굵게 · 맞히면 X 가 「톡」
   ③ 흠뻑 적시면 0.16초 흔들림 · 움직임 줄이기 설정이면 흔들림 없음
   ④ 휴대폰 세로 · 패드 세로에서도 조준경 원이 화면 안 · 봇 판 1분 오류 0"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from arena599 import boot
from playwright.async_api import async_playwright

GO = """()=>{ const R=MG.run; R.setMap('pool'); R.beginSolo(); for(let i=0;i<200 && R.phase!=='play';i++) MG.step(.05,false); for(let i=0;i<80 && R.time.cd>0;i++) MG.step(.05,false);
  const me=R.me; me.p.set(0,0,19); me.yaw=0; me.pitch=0; R.ACT.forEach((a,i)=>{ if(a.bot){ a.brain.think=1e9; a.prot=0; if(i!==1){ a.alive=false; a.G.visible=false; a.resp=1e9; } } });
  const b=R.ACT[1]; b.alive=true; b.G.visible=true; b.p.set(0,0,10); b.v.set(0,0,0); b.soak=0; b.rb=true; R.D.dm=0; return R.phase; }"""   # 과녁 봇은 가만히 (맞으면 되쏘며 움직여 조준이 흔들리던 것) · 나는 안 젖음
AIM = """(dy0)=>{ const R=MG.run, me=R.me, b=R.ACT[1]; b.alive=true; b.G.visible=true; b.prot=0; b.soak=Math.min(b.soak,40); b.brain.think=1e9; b.p.set(0,0,10); b.v.set(0,0,0); const dx=b.p.x-me.p.x, dz=b.p.z-me.p.z, dy=(b.p.y+dy0)-(me.p.y+1.48); me.yaw=Math.atan2(-dx,-dz); me.pitch=Math.atan2(dy, Math.hypot(dx,dz)); }"""
SC = "()=>{ const e=document.querySelector('#mgUI .aScope'); return [+(+e.style.opacity||0).toFixed(2), e.classList.contains('lock'), e.querySelector('b').textContent, +(+getComputedStyle(document.querySelector('#mgUI .aCx')).opacity).toFixed(2)]; }"
WI = "(w)=>{ const R=MG.run; while(R.me.wi<w) R.up(R.me); R.me.cd=0; }"

async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx, P, errs = await boot(br, 844, 390); E = P.evaluate
        await E("()=>MG.enter('arena',{})"); await P.wait_for_timeout(2500)
        ok(await E(GO) == "play", "판 시작")
        await E("()=>{ MG.I.touch=true; MG.I.lock=false; MG.I.mouse=false; }")
        # ② 물권총 한 발
        await E(AIM, 1.0)
        r = await E("""()=>{ const R=MG.run, I=MG.I; R.me.cd=0; const k0=R.camK; I.fire=1; MG.step(.016,false); I.fire=0; const k1=R.camK, fl=R.vmFl.visible, pop=document.querySelector('#mgUI .aHm').classList.contains('pop'); for(let i=0;i<40;i++) MG.step(.016,false); return [k0, +k1.toFixed(4), fl, pop, +R.camK.toFixed(4), R.vmFl.visible]; }""")
        ok(r[1] > r[0] and r[2] and r[3] and r[4] < r[1] * .2 and not r[5], f"② 쏘면 카메라 살짝 튐 → 돌아옴 · 총 끝 물보라(잠깐) · 맞힘 X 톡 {r}")
        r = await E("""()=>{ const R=MG.run, I=MG.I, out={}; for(const [w,k] of [[2,'shot'],[3,'smg']]){ while(R.me.wi<w) R.up(R.me); R.me.cd=0; for(let i=0;i<60;i++) MG.step(.016,false); I.fire=1; MG.step(.016,false); I.fire=0; out[k]=+R.camK.toFixed(4); } return out; }""")
        ok(r["shot"] > r["smg"] > 0, f"② 무기마다 튀는 크기 다름 (물대포 > 연발) {r}")
        # ① 저격 조준경
        await E(WI, 4); await E(AIM, 1.0); await E("()=>{ for(let i=0;i<30;i++) MG.step(.016,false); }")
        r0 = await E(SC)
        await E("()=>{ MG.I.fire=1; for(let i=0;i<30;i++) MG.step(.016,false); }")
        r1 = await E(SC)
        ok(r0[0] == 0 and r1[0] >= .9 and r1[3] == 0, f"① 꾹 누르면 조준경이 나오고 작은 조준점은 숨김 (전 {r0[0]} → {r1[0]})")
        ok(r1[1] and "지금" in r1[2], f"① 조준점이 상대 몸 위 → 초록 「지금 떼요!」 {r1}")
        await E(AIM, 1.5); await E("()=>{ for(let i=0;i<8;i++) MG.step(.016,false); }"); rh = await E(SC)
        ok(rh[1] and "머리" in rh[2], f"① 머리 위 → 「머리! 지금 떼요 ⭐」 {rh}")
        await E("()=>{ const me=MG.run.me; me.yaw+=.4; for(let i=0;i<8;i++) MG.step(.016,false); }"); r2 = await E(SC)
        ok(not r2[1] and r2[2] == "떼면 쏴요!", f"① 비켜 보면 빨간 점 「떼면 쏴요!」 {r2}")
        await E(AIM, 1.0); await E("()=>{ for(let i=0;i<8;i++) MG.step(.016,false); }")
        r = await E("()=>{ const R=MG.run, b=R.ACT[1], s0=b.soak, a0=b.alive; MG.I.fire=0; MG.step(.016,false); const fired=b.soak>s0 || !b.alive; for(let i=0;i<40;i++) MG.step(.016,false); return [fired, a0]; }")
        r3 = await E(SC)
        ok(r[0] and r3[0] == 0, f"① 떼면 쏨 → 맞음 · 조준경 사라짐 {r} {r3}")
        await P.screenshot(path=OUT + "arena730_after.png")
        # ③ 흠뻑 = 흔들림
        await E(WI, 4); await E("()=>{ const R=MG.run; R.me.wi=0; R.vmSet(0); }")
        r = await E("""()=>{ const R=MG.run, b=R.ACT[1]; b.alive=true; b.G.visible=true; b.soak=95; b.prot=0; b.p.set(0,0,10); const me=R.me, dx=b.p.x-me.p.x, dz=b.p.z-me.p.z; me.yaw=Math.atan2(-dx,-dz); me.pitch=Math.atan2(1-1.48, Math.hypot(dx,dz)); me.cd=0;
            MG.I.fire=1; MG.step(.016,false); MG.I.fire=0; const s1=R.shk, al=b.alive; for(let i=0;i<20;i++) MG.step(.016,false); return [al, +s1.toFixed(2), +R.shk.toFixed(2)]; }""")
        ok(r[0] is False and r[1] > .5 and r[2] == 0, f"③ 흠뻑 적시면 잠깐 흔들림 → 멈춤 {r}")
        # 봇 판 1분 (오류 0)
        await E("()=>{ const R=MG.run; R.D.dm=.85; R.ACT.forEach(a=>{ if(a.bot){ a.rb=false; a.brain.think=0; a.resp=.5; } }); for(let i=0;i<1200 && !R.time.over;i++) MG.step(.05,false); }")
        E1 = real_errs(errs); ok(not E1, f"봇 판 1분 · 오류 0 {E1[:3]}")
        await ctx.close()
        # ③ 움직임 줄이기 → 흔들림 없음 · 튐 작게
        ctx = await br.new_context(viewport={"width": 844, "height": 390}, is_mobile=True, has_touch=True, reduced_motion="reduce")
        from fakefb import fake
        R2 = await ctx.new_page(); errs2 = []; R2.on("pageerror", lambda e: errs2.append(str(e)))
        await R2.route("**/*", fake); await R2.goto(ORIGIN + "proto/house.html?isle=1"); await R2.wait_for_timeout(300)
        await R2.evaluate("()=>{ localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }"); await R2.reload(); await R2.wait_for_timeout(2400)
        await R2.evaluate("()=>MG.enter('arena',{})"); await R2.wait_for_timeout(2500); await R2.evaluate(GO); await R2.evaluate("()=>{ MG.I.touch=true; }")
        r = await R2.evaluate("""()=>{ const R=MG.run, b=R.ACT[1]; b.alive=true; b.soak=95; b.prot=0; b.p.set(0,0,10); const me=R.me, dx=b.p.x-me.p.x, dz=b.p.z-me.p.z; me.yaw=Math.atan2(-dx,-dz); me.pitch=Math.atan2(1-1.48, Math.hypot(dx,dz)); me.cd=0;
            MG.I.fire=1; MG.step(.016,false); MG.I.fire=0; return [b.alive, R.shk, +R.camK.toFixed(4)]; }""")
        ok(r[0] is False and r[1] == 0 and r[2] < .006, f"③ 움직임 줄이기: 흔들림 0 · 튐 작게 {r}")
        await ctx.close()
        # ④ 세로 화면 조준경 원
        for nm, w, h in (("phoneP", 390, 844), ("padP", 820, 1180)):
            ctx, Q, e3 = await boot(br, w, h); E = Q.evaluate
            await E("()=>MG.enter('arena',{})"); await Q.wait_for_timeout(2500); await E(GO); await E("()=>{ MG.I.touch=true; }")
            await E(WI, 4); await E(AIM, 1.0); await E("()=>{ MG.I.fire=1; for(let i=0;i<30;i++) MG.step(.016,false); }")
            r = await E("()=>{ const g=document.querySelector('#mgUI .aScope .ring').getBoundingClientRect(); return [Math.round(g.left), Math.round(g.top), Math.round(g.right), Math.round(g.bottom), innerWidth, innerHeight]; }")
            ok(r[0] >= 0 and r[1] >= 0 and r[2] <= r[4] and r[3] <= r[5] and (r[2] - r[0]) >= min(r[4], r[5]) * .7, f"④ {nm}: 조준경 원이 화면 안 · 크게 {r}")
            await Q.wait_for_timeout(300); await Q.screenshot(path=OUT + f"arena730_scope_{nm}.png")
            errs2 += e3; await ctx.close()
        E2 = real_errs(errs2); ok(not E2, f"오류 없음 {E2[:3]}")
        await br.close()
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
