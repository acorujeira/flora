/* Service worker: keeps the app shell and the botanical plates on the device, so the app
   opens fast and works with no signal. It never touches Google's sign-in or the Sheets API;
   the plant data has its own offline copy in IndexedDB.
   Change VERSION after any code change: every device fetches the shell afresh and reloads once.
   Change PLATES_VERSION only when plate images change, since it makes every device download them all again. */
const VERSION = "v10", PLATES_VERSION = "v6";
const SHELL = "flora-shell-" + VERSION, PLATES = "flora-plates-" + PLATES_VERSION, FONTS = "flora-fonts-v1";
const SHELL_FILES = ["./", "index.html", "manifest.webmanifest", "plates.json", "map/", "map/index.html",
  "shell/config.js", "shell/store.js", "shell/auth.js", "shell/sheets.js", "shell/shell.js",
  "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png"];

self.addEventListener("install", e => {
  /* cache: "reload" skips the browser's own HTTP cache (GitHub Pages keeps files up to 10 minutes),
     so a new version stores the new files. */
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES.map(u => new Request(u, { cache: "reload" })))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith("flora-") && ![SHELL, PLATES, FONTS].includes(k)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

/* Answer from the cache at once and fetch a fresh copy for next time. */
function staleWhileRevalidate(req, cacheName, opts) {
  return caches.open(cacheName).then(cache => cache.match(req, opts).then(hit => {
    const fresh = fetch(req, { cache: "no-cache" }).then(res => { if (res && res.ok) cache.put(req, res.clone()); return res; });
    if (hit) { fresh.catch(() => {}); return hit; }
    return fresh;
  }));
}
/* Fetch the page fresh so updates show on the next open; fall back to the saved copy
   if there is no signal, or the network takes longer than `wait` milliseconds. */
function networkFirst(req, cacheName, wait) {
  return caches.open(cacheName).then(cache => {
    const fresh = fetch(req, { cache: "no-cache" }).then(res => { if (res && res.ok) cache.put(req, res.clone()); return res; });
    const slow = new Promise(r => setTimeout(r, wait)).then(() => cache.match(req)).then(hit => hit || fresh);
    return Promise.race([fresh.catch(() => cache.match(req)), slow]);
  });
}
/* Answer from the cache; fetch only what is missing. */
function cacheFirst(req, cacheName) {
  return caches.open(cacheName).then(cache => cache.match(req).then(hit => hit ||
    fetch(req).then(res => { if (res && (res.ok || res.type === "opaque")) cache.put(req, res.clone()); return res; })));
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin) {
    if (url.pathname.includes("/plates/")) e.respondWith(cacheFirst(req, PLATES));
    else if (req.mode === "navigate" && /\/map\/?(index\.html)?$/.test(url.pathname)) e.respondWith(networkFirst(new Request("map/index.html"), SHELL, 3000));
    else if (req.mode === "navigate") e.respondWith(networkFirst(new Request("index.html"), SHELL, 3000));
    else e.respondWith(staleWhileRevalidate(req, SHELL, { ignoreSearch: true }));
  } else if (url.hostname === "fonts.googleapis.com") e.respondWith(staleWhileRevalidate(req, FONTS));
  else if (url.hostname === "fonts.gstatic.com") e.respondWith(cacheFirst(req, FONTS));
});

/* The page asks for this once it is up: fetch every plate not yet on the device, a few at a time. */
async function cachePlates() {
  const res = await staleWhileRevalidate(new Request("plates.json"), SHELL);
  const plates = await res.clone().json(), urls = new Set();
  for (const k in plates) {
    const p = plates[k];
    if (p.url) urls.add(p.url);
    if (p.habit) { if (p.habit.url) urls.add(p.habit.url); if (p.habit.bare) urls.add(p.habit.bare); }
  }
  const cache = await caches.open(PLATES), todo = [];
  for (const u of urls) if (!(await cache.match(u))) todo.push(u);
  while (todo.length) {
    await Promise.all(todo.splice(0, 6).map(u => fetch(u).then(r => { if (r.ok) return cache.put(u, r); }).catch(() => {})));
  }
}
self.addEventListener("message", e => { if (e.data === "cache-plates") e.waitUntil(cachePlates()); });
