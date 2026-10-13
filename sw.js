/* HY ENG 서비스워커 — 게임 파일을 캐시해 두 번째부터는 오프라인에서도 실행됩니다.
   게임을 수정한 뒤에는 아래 VERSION 숫자를 꼭 올리세요. 그래야 새 버전이 반영됩니다. */
const VERSION = "hyeng-v214";
const CORE = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png"
];
const OPTIONAL = [                    // 없으면 그냥 건너뜀 — 그림은 assets/ 아래 갈래별 폴더
  "./versus.html", "./icon-maskable-512.png",
  "./assets/boss/boss-gate-bars.webp", "./assets/boss/boss-knight-2.webp", "./assets/boss/boss-knight-parts.webp", "./assets/boss/boss-knight.webp",
  "./assets/boss/boss-shield-2.webp", "./assets/boss/boss-shield.webp", "./assets/boss/boss-spike.webp", "./assets/boss/boss-warden.webp",
  "./assets/chars/char-archer.webp", "./assets/chars/char-cat.webp", "./assets/chars/char-cheer.webp", "./assets/chars/char-explorer.webp",
  "./assets/chars/char-ghost.webp", "./assets/chars/char-hero.webp", "./assets/chars/char-knight.webp", "./assets/chars/char-mage.webp",
  "./assets/chars/char-portraits.webp", "./assets/chars/char-scholar.webp", "./assets/chars/char-wolf.webp", "./assets/chars/outfit-hero-lava.webp", "./data/dex1.json", "./data/dex2.json", "./assets/chars/outfit-hero-lava-card.webp", "./assets/traps/bee.webp",
  "./assets/traps/block-castle.webp", "./assets/traps/block-hall.webp", "./assets/traps/block-plaza.webp", "./assets/traps/block-rampart.webp",
  "./assets/traps/blocks.webp", "./assets/traps/chandelier-hall.webp", "./assets/traps/cloud-fog.webp", "./assets/traps/crack-castle.webp",
  "./assets/traps/crumble-castle.webp", "./assets/traps/crumble-night.webp", "./assets/traps/crumble-volcano.webp", "./assets/traps/geyser-night.webp",
  "./assets/traps/hole-meadow.webp", "./assets/traps/hole-night.webp", "./assets/traps/ice-chunk.webp", "./assets/traps/ice-night.webp",
  "./assets/traps/knight-hall.webp", "./assets/traps/lava-pit.webp", "./assets/traps/quicksand-desert.webp", "./assets/traps/rock-castle.webp",
  "./assets/traps/rocks.webp", "./assets/traps/salamander-volcano.webp", "./assets/traps/statue-castle.webp", "./assets/traps/sunflower.webp",
  "./assets/ui/card-desert.webp", "./assets/ui/card-ice.webp", "./assets/ui/card-meadow.webp", "./assets/ui/card-night.webp",
  "./assets/ui/card-volcano.webp", "./assets/ui/hud-icons.webp", "./assets/ui/logo.webp", "./assets/ui/menu-icons.webp",
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
  "./assets/world/sign-volcano.webp"
];

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(VERSION);
    await c.addAll(CORE);
    for (const url of OPTIONAL) { try { await c.add(url); } catch (err) {} }
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)));
    self.clients.claim();
  })());
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  // 학원 랭킹(구글 시트)은 저장하지 않는다 — 항상 최신 순위
  if (url.hostname.indexOf("script.google") >= 0 || url.hostname.indexOf("googleusercontent") >= 0) return;
  // 게임 화면(HTML)은 항상 새로 받아온다 — 올린 즉시 새 버전이 보이게.
  // 인터넷이 없을 때만 저장해 둔 것을 쓴다.
  const isPage = e.request.mode === "navigate" || url.pathname.endsWith(".html") || url.pathname.endsWith("/");
  if (isPage) {
    e.respondWith((async () => {
      try {
        const res = await fetch(e.request, {cache: "no-store"});
        if (res && res.ok) {
          const c = await caches.open(VERSION);
          c.put(e.request, res.clone());
        }
        return res;
      } catch (err) {
        return (await caches.match(e.request)) || (await caches.match("./index.html"));
      }
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
        const c = await caches.open(VERSION);
        c.put(e.request, res.clone());
      }
      return res;
    } catch (err) {
      return caches.match("./index.html");
    }
  })());
});
