const CACHE_NAME = 'payday-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',
  '/static/icons/favicon-32x32.png',
  '/static/icons/favicon-16x16.png',
  '/static/icons/apple-icon-180x180.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
