/**
 * Disaster Management Alert System - Service Worker
 * Ensures offline resilience for low/no internet disaster situations.
 */

const CACHE_NAME = "dmas-cache-v1";
const STATIC_ASSETS = [
  "/",
  "/static/css/style.css",
  "/static/js/citizen.js",
  "/static/js/admin.js",
  "/static/js/simulator.js",
  "/api/languages",
  "/api/hazards",
  "/api/districts"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[ServiceWorker] Caching static shell assets...");
      return cache.addAll(STATIC_ASSETS).catch((e) => {
        console.warn("[ServiceWorker] Some assets could not be cached immediately:", e);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log("[ServiceWorker] Removing old cache:", key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Network first with offline cache fallback for APIs
  if (event.request.url.includes("/api/")) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response.status === 200 && event.request.method === "GET") {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache first for assets
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request);
    })
  );
});
