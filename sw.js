/* HY ENG 서비스워커 — 게임 파일을 캐시해 두 번째부터는 오프라인에서도 실행됩니다.
   게임을 수정한 뒤에는 아래 VERSION 숫자를 꼭 올리세요. 그래야 새 버전이 반영됩니다. */
const VERSION = "hyeng-v428";
/* (v322) 그림(assets/)은 버전마다 다시 받지 않게 이름이 고정된 캐시에 따로 둔다 — 업데이트마다 그림 130개(약 22MB)를 다시 받았다.
   그림 파일을 '같은 이름으로' 새로 바꿨을 때만 아래 숫자를 올리세요 (새 이름의 그림은 그냥 올리면 됨). */
const ART = "hyeng-art-v1";
/* (v385) 발음 파일(audio/*.mp3 · 15MB)은 이름이 고정된 캐시에 따로 둔다 — 업데이트마다 다시 받지 않게. 같은 이름으로 새로 바꿨을 때만 숫자를 올리세요 */
const AUDIO = "hyeng-audio-v1";
const isAudio = u => /\/audio\/[^/]+\.mp3$/.test(new URL(u, self.location.href).pathname);
async function fillAudio() {
  try {
    const list = await (await fetch("./audio/list.json", {cache: "no-cache"})).json();
    const c = await caches.open(AUDIO);
    const have = new Set((await c.keys()).map(r => new URL(r.url).pathname));
    const todo = list.filter(k => !have.has(new URL("./audio/" + k + ".mp3", self.location.href).pathname));
    let i = 0;
    const work = async () => { while (i < todo.length) { const k = todo[i++]; try { const u = "./audio/" + k + ".mp3"; const r = await fetch(u); if (r && r.ok) await c.put(u, r); } catch (e) {} } };
    await Promise.all([work(), work(), work(), work(), work(), work()]);
  } catch (e) {}
}
const isArt = u => new URL(u, self.location.href).pathname.indexOf("/assets/") >= 0;
const isData = u => /\/data\/[^/]+\.json$/.test(new URL(u, self.location.href).pathname);
const CORE = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./three.min.js",                    // (v289) 3D 엔진 — 인터넷 없이도 켜지게 꼭 저장
  "./lib/CopyShader.js", "./lib/LuminosityHighPassShader.js", "./lib/EffectComposer.js", "./lib/RenderPass.js",
  "./lib/ShaderPass.js", "./lib/MaskPass.js", "./lib/UnrealBloomPass.js"
];
const OPTIONAL = [                    // 없으면 그냥 건너뜀 — 그림은 assets/ 아래 갈래별 폴더
  "./versus.html", "./icon-maskable-512.png", "./audio/list.json",
  "./assets/boss/hb1.webp", "./assets/boss/hb2.webp", "./assets/boss/hb3.webp", "./assets/boss/hb4.webp", "./assets/boss/hb5.webp",
  "./assets/boss/boss-gate-bars.webp", "./assets/boss/boss-knight-2.webp", "./assets/boss/boss-knight-parts.webp", "./assets/boss/boss-knight.webp",
  "./assets/boss/boss-shield-2.webp", "./assets/boss/boss-shield.webp", "./assets/boss/boss-spike.webp", "./assets/boss/boss-warden.webp",
  "./assets/chars/char-archer.webp", "./assets/chars/char-cat.webp", "./assets/chars/char-cheer.webp", "./assets/chars/char-explorer.webp",
  "./assets/chars/char-ghost.webp", "./assets/chars/char-hero.webp", "./assets/chars/char-knight.webp", "./assets/chars/char-mage.webp",
  "./assets/chars/char-portraits.webp", "./assets/chars/char-scholar.webp", "./assets/chars/char-wolf.webp", "./assets/chars/outfit-hero-lava.webp", "./data/dex1.json", "./data/dex2.json", "./data/dex3.json", "./data/easy.json", "./data/talk.json", "./data/bex.json", "./data/mid.json", "./data/gram.json", "./assets/chars/outfit-hero-lava-card.webp", "./assets/traps/bee.webp",
  "./assets/traps/block-castle.webp", "./assets/traps/block-hall.webp", "./assets/traps/block-plaza.webp", "./assets/traps/block-rampart.webp",
  "./assets/traps/blocks.webp", "./assets/traps/chandelier-hall.webp", "./assets/traps/cloud-fog.webp", "./assets/traps/crack-castle.webp",
  "./assets/traps/crumble-castle.webp", "./assets/traps/crumble-night.webp", "./assets/traps/crumble-volcano.webp", "./assets/traps/geyser-night.webp",
  "./assets/traps/hole-meadow.webp", "./assets/traps/hole-night.webp", "./assets/traps/ice-chunk.webp", "./assets/traps/ice-night.webp",
  "./assets/traps/knight-hall.webp", "./assets/traps/lava-pit.webp", "./assets/traps/quicksand-desert.webp", "./assets/traps/rock-castle.webp",
  "./assets/traps/rocks.webp", "./assets/traps/salamander-volcano.webp", "./assets/traps/statue-castle.webp", "./assets/traps/sunflower.webp",
  "./assets/ui/card-desert.webp", "./assets/ui/card-ice.webp", "./assets/ui/card-meadow.webp", "./assets/ui/card-night.webp",
  "./assets/ui/card-volcano.webp", "./assets/ui/hud-icons.webp", "./assets/ui/logo.webp", "./assets/ui/menu-icons.webp",
  "./assets/ui/rv-chest-open.webp", "./assets/ui/rv-chest-sleep.webp", "./assets/ui/rv-chest-empty.webp", "./assets/ui/sign-day.webp",
  "./assets/ui/sign-day-ready.webp", "./assets/ui/sign-day-done.webp", "./assets/ui/boss-mound.webp", "./assets/ui/ic-pin.webp",
  "./assets/ui/ic-flag.webp", "./assets/ui/ic-target.webp", "./assets/ui/ic-swords.webp", "./assets/ui/ic-gift.webp",
  "./assets/ui/ic-sleep.webp", "./assets/ui/ic-fire.webp", "./assets/ui/ic-gem.webp", "./assets/ui/deco-bush.webp",
  "./assets/ui/deco-flowers.webp", "./assets/ui/deco-rock.webp", "./assets/ui/deco-tree.webp", "./assets/ui/deco-mushroom.webp",
  "./assets/ui/deco-pond.webp",   // (v331) 지도 속 캠프 그림
  "./assets/ui/stone-g0.webp", "./assets/ui/stone-g1.webp", "./assets/ui/stone-g2.webp", "./assets/ui/stone-y0.webp", "./assets/ui/stone-y1.webp", "./assets/ui/stone-y2.webp", "./assets/ui/stone-p0.webp", "./assets/ui/stone-p1.webp", "./assets/ui/stone-p2.webp",   // (v332) Stage 돌 그림
  "./assets/ui/result-badges.webp", "./assets/ui/ui-panel.webp", "./assets/ui/ui-round.webp", "./assets/ui/ui-wide.webp",
  "./assets/world/floor-castle.webp", "./assets/world/floor-desert.webp", "./assets/world/floor-hall.webp", "./assets/world/floor-ice.webp",
  "./assets/world/floor-meadow.webp", "./assets/world/floor-night.webp", "./assets/world/floor-plaza.webp", "./assets/world/floor-rampart.webp",
  "./assets/world/floor-volcano.webp", "./assets/world/gate-castle.webp", "./assets/world/gate-desert.webp", "./assets/world/gate-hall.webp",
  "./assets/world/gate-ice.webp", "./assets/world/gate-meadow.webp", "./assets/world/gate-night.webp", "./assets/world/gate-plaza.webp",
  "./assets/world/gate-rampart.webp", "./assets/world/gate-volcano.webp", "./assets/world/mountains-castle.webp", "./assets/world/mountains-desert.webp",
  "./assets/world/mountains-hall.webp", "./assets/world/mountains-ice.webp", "./assets/world/mountains-meadow.webp", "./assets/world/mountains-night.webp",
  "./assets/world/mountains-plaza.webp", "./assets/world/mountains-rampart.webp", "./assets/world/mountains-volcano.webp", "./assets/world/props-castle.webp",
  "./assets/world/props-desert.webp", "./assets/world/props-hall.webp", "./assets/world/props-ice.webp", "./assets/world/props-meadow.webp",
  "./assets/world/props-night.webp", "./assets/world/props-plaza.webp", "./assets/world/props-rampart.webp", "./assets/world/props-volcano.webp",
  "./assets/world/sign-castle.webp", "./assets/world/sign-desert.webp", "./assets/world/sign-hall.webp", "./assets/world/sign-ice.webp",
  "./assets/world/sign-meadow.webp", "./assets/world/sign-night.webp", "./assets/world/sign-plaza.webp", "./assets/world/sign-rampart.webp",
  "./assets/world/sign-volcano.webp",
  /* (v322) v298 뒤에 들어온 그림 — 첫 화면 카드·교재 표지·보스 공격 그림·달리기 캐릭터. (걷기 그림 walk/·이모지 emoji/ 는 쓸 때 받아 그림 캐시에 둔다) */
  "./assets/world/world-desert.webp", "./assets/world/world-ice.webp", "./assets/world/world-meadow.webp", "./assets/world/world-night.webp", "./assets/world/world-town.webp",
  "./assets/world/world-volcano.webp", "./assets/books/book-abc.webp", "./assets/books/book-all.webp", "./assets/books/book-basic.webp",
  "./assets/books/book-digr.webp", "./assets/books/book-elem.webp", "./assets/books/book-g56h.webp", "./assets/books/book-g56v.webp",
  "./assets/books/book-jl.webp", "./assets/books/book-kinder.webp", "./assets/books/book-long.webp", "./assets/books/book-mid.webp",
  "./assets/books/book-mv1.webp", "./assets/books/book-rd1.webp", "./assets/books/book-rd2.webp", "./assets/books/book-rd3.webp",
  "./assets/books/book-short.webp", "./assets/books/book-sight.webp", "./assets/books/book-vowel2.webp", "./assets/ui/mode-e2k.webp",
  "./assets/ui/mode-k2e.webp", "./assets/ui/mode-mix.webp", "./assets/items/item-heart.webp", "./assets/items/item-hint.webp",
  "./assets/items/item-shield.webp", "./assets/items/item-slow.webp", "./assets/chars/run-archer.webp", "./assets/chars/run-cat.webp",
  "./assets/chars/bs-hero.webp", "./assets/chars/bs-knight.webp", "./assets/chars/bs-wolf.webp",   // (v335) 주간 보스 공격 그림
  "./assets/chars/run-explorer.webp", "./assets/chars/run-ghost.webp", "./assets/chars/run-hero.webp", "./assets/chars/run-knight.webp",
  "./assets/chars/run-mage.webp", "./assets/chars/run-scholar.webp", "./assets/chars/run-wolf.webp", "./assets/boss/hb1-a.webp",
  "./assets/boss/hb1-b.webp", "./assets/boss/hb1-c.webp", "./assets/boss/hb2-a.webp", "./assets/boss/hb2-b.webp",
  "./assets/boss/hb2-c.webp", "./assets/boss/hb3-a.webp", "./assets/boss/hb3-b.webp", "./assets/boss/hb3-c.webp",
  "./assets/boss/hb4-a.webp", "./assets/boss/hb4-b.webp", "./assets/boss/hb4-c.webp", "./assets/boss/hb5-a.webp",
  "./assets/boss/hb5-b.webp", "./assets/boss/hb5-c.webp", "./assets/boss/hbS-a.webp", "./assets/boss/hbS-b.webp",
  "./assets/boss/hbS-c.webp", "./assets/boss/hbS.webp"
];

/* (v322) 설치할 때 HTTP 캐시(깃허브 페이지 max-age 10분)를 건너뛰고 서버에서 새로 받는다 (cache:'reload').
   예전엔 새 버전 캐시에 옛 data/*.json 이 그대로 들어가서, 업데이트해도 단어·대화 자료가 옛것이었다 */
const fresh = u => new Request(u, {cache: "reload"});
self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(VERSION), art = await caches.open(ART);
    await c.addAll(CORE.map(fresh));
    for (const url of OPTIONAL) {
      try {
        if (isArt(url)) { if (!(await art.match(url))) await art.add(url); }   // 그림은 이미 있으면 건너뜀 · (v337) QA: 그림은 이름이 안 바뀌니 보통 요청 (첫 방문에 첫 화면이 받은 그림을 또 받던 것 — 39MB)
        else await c.add(fresh(url));
      } catch (err) {}
    }
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== VERSION && k !== ART && k !== AUDIO).map(k => caches.delete(k)));   // (v322) 그림 캐시는 남긴다
    self.clients.claim();
  })());
});

/* (v347) 화면이 「너 몇 버전이야?」 하고 물으면 답한다 — 화면이 이미 같은 버전이면 다시 고치지 않게 */
self.addEventListener("message", e => {
  try { if (e.data === "hyVer" && e.source) e.source.postMessage({hyVer: VERSION}); } catch (err) {}
  try { if (e.data === "hyAudio") e.waitUntil(fillAudio()); } catch (err) {}
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  /* (v360) 큰 버그: 학원 서버(Firebase) 읽기도 아래 「그림·스크립트는 저장해 둔 것 먼저」에 걸려, 처음 읽은 값을 버전이 바뀔 때까지 계속 돌려줬다
     (숙제가 사라졌다 나타남 · 숙제 끄기 실패 · 오늘 한 아이 0명 · 새로 넣은 아이가 일부 패드에 안 보임 · 배틀 「한 판 더」 옛 점수 · 실시간 연결이 옛 내용을 되풀이)
     → 다른 주소는 CDN 스크립트만 저장하고 나머지(Firebase · 실시간 연결 · 그 밖)는 손대지 않음 */
  const accept = (e.request.headers && e.request.headers.get("accept")) || "";
  if (accept.indexOf("text/event-stream") >= 0) return;
  if (url.origin !== self.location.origin && !/^(cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|fonts\.(googleapis|gstatic)\.com)$/.test(url.hostname)) return;
  // 학원 랭킹(구글 시트)은 저장하지 않는다 — 항상 최신 순위
  if (url.hostname.indexOf("script.google") >= 0 || url.hostname.indexOf("googleusercontent") >= 0) return;
  // 게임 화면(HTML)은 항상 새로 받아온다 — 올린 즉시 새 버전이 보이게.
  // 인터넷이 없을 때만 저장해 둔 것을 쓴다.
  const isPage = e.request.mode === "navigate" || url.pathname.endsWith(".html") || url.pathname.endsWith("/");
  /* (v322) data/*.json(단어·대화 자료)도 인터넷이 되면 새로 받는다 (바뀐 게 없으면 서버가 짧게 '그대로'라고만 답함). 안 되면 저장해 둔 것 */
  if (isPage || (url.origin === self.location.origin && isData(e.request.url))) {
    e.respondWith((async () => {
      try {
        /* (v337) QA: 켤 때마다 index.html(약 570KB)을 통째로 다시 받고(no-store) 기다리는 시간 제한이 없어 느린 학원 와이파이에서 첫 화면이 늦었다
           → 바뀌었는지만 묻고(no-cache · 안 바뀌면 짧은 답) · 화면은 6초 넘게 걸리면 저장해 둔 것을 먼저 보여 줌 (받던 것은 끝까지 받아 저장) */
        const net = fetch(e.request, {cache: "no-cache"}).then(res => {
          if (res && res.ok) { const cp = res.clone(); caches.open(VERSION).then(c => c.put(e.request, cp)).catch(() => {}); }
          return res; });
        if (isPage) {
          const hit = (await caches.match(e.request, {ignoreSearch: true})) || (await caches.match("./index.html"));
          if (hit) {
            const slow = new Promise(r => setTimeout(() => r(null), 6000));
            const won = await Promise.race([net.catch(() => null), slow]);
            if (won) return won;
            e.waitUntil(net.catch(() => {}));
            return hit;
          }
        }
        return await net;
      } catch (err) {
        const hit = await caches.match(e.request, {ignoreSearch: true});
        if (hit) return hit;
        return isPage ? (await caches.match("./index.html")) : Response.error();
      }
    })());
    return;
  }
  // (v385) 발음 파일 — 저장해 둔 것 먼저, 없으면 받아서 저장
  if (url.origin === self.location.origin && isAudio(e.request.url)) {
    e.respondWith((async () => {
      const c = await caches.open(AUDIO), hit = await c.match(e.request);
      if (hit) return hit;
      try { const res = await fetch(e.request); if (res && res.ok) c.put(e.request, res.clone()); return res; } catch (err) { return Response.error(); }
    })());
    return;
  }
  // 그림·스크립트는 저장해 둔 것을 먼저 쓴다 (빠르게)
  e.respondWith((async () => {
    const hit = await caches.match(e.request);
    if (hit) return hit;
    try {
      const res = await fetch(e.request);
      if (res && (res.ok || res.type === "opaque")) {
        const c = await caches.open(url.origin === self.location.origin && isArt(e.request.url) ? ART : VERSION);   // (v322) 그림은 그림 캐시에
        c.put(e.request, res.clone());
      }
      return res;
    } catch (err) {
      // (v289) 그림·스크립트·자료에 웹페이지(index.html)를 대신 주면 스크립트로 읽다 문법 오류가 난다 → 그냥 실패로 돌려준다
      return Response.error();
    }
  })());
});
