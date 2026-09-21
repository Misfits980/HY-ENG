/* HY ENG 서비스워커 — 게임 파일을 캐시해 두 번째부터는 오프라인에서도 실행됩니다.
   게임을 수정한 뒤에는 아래 VERSION 숫자를 꼭 올리세요. 그래야 새 버전이 반영됩니다. */
const VERSION = "hyeng-v64";
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
  "./mountains-volcano.webp", "./mountains-night.webp"
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
  e.respondWith((async () => {
    const hit = await caches.match(e.request);
    if (hit) return hit;
    try {
      const res = await fetch(e.request);
      // CDN 으로 받아온 three.js 도 한 번 받으면 캐시해 둔다
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
