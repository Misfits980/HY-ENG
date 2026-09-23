/* HY ENG 서비스워커 — 게임 파일을 캐시해 두 번째부터는 오프라인에서도 실행됩니다.
   게임을 수정한 뒤에는 아래 VERSION 숫자를 꼭 올리세요. 그래야 새 버전이 반영됩니다. */
const VERSION = "hyeng-v86";
const CORE = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png"
];
const OPTIONAL = [                    // 없으면 그냥 건너뜀
  "./three.min.js", "./versus.html",
  "./assets/mountains-meadow.webp", "./assets/mountains-desert.webp",
  "./assets/mountains-ice.webp",    "./assets/mountains-volcano.webp",
  "./assets/mountains-night.webp",
  "./mountains-meadow.webp", "./mountains-desert.webp", "./mountains-ice.webp",
  "./mountains-volcano.webp", "./mountains-night.webp",
  "./hole-meadow.webp", "./quicksand-desert.webp", "./lava-pit.webp", "./crumble-volcano.webp",
  "./floor-meadow.webp", "./floor-desert.webp", "./floor-ice.webp", "./floor-volcano.webp", "./floor-night.webp",
  "./props-meadow.webp", "./props-desert.webp", "./props-ice.webp", "./props-volcano.webp", "./props-night.webp",
  "./hole-night.webp", "./crumble-night.webp", "./ice-night.webp", "./cloud-fog.webp", "./blocks.webp",
  "./gate-meadow.webp", "./gate-desert.webp", "./gate-ice.webp", "./gate-volcano.webp", "./gate-night.webp",
  "./sign-meadow.webp", "./sign-desert.webp", "./sign-ice.webp", "./sign-volcano.webp", "./sign-night.webp",
  "./logo.webp", "./ui-panel.webp", "./ui-wide.webp", "./ui-round.webp", "./icon-maskable-512.png",
  "./char-hero.webp", "./char-explorer.webp", "./char-archer.webp", "./char-mage.webp", "./char-knight.webp", "./char-scholar.webp", "./char-ghost.webp", "./char-cat.webp", "./char-wolf.webp",
  "./skin-hero.png", "./skin-explorer.png", "./skin-archer.png", "./skin-mage.png", "./skin-knight.png", "./skin-scholar.png", "./skin-ghost.png", "./skin-cat.png", "./skin-wolf.png"
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
