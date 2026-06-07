const CACHE_NAME = 'ipim-absensi-v1';

const urlsToCache = [
  '/ipim-digital-maghfirah/',
  '/ipim-digital-maghfirah/index.html',
  '/ipim-digital-maghfirah/absensi.html',
  '/ipim-digital-maghfirah/dashboard.html',
  '/ipim-digital-maghfirah/manifest.json',
  '/ipim-digital-maghfirah/style.css',
  '/ipim-digital-maghfirah/images/icon-192.png',
  '/ipim-digital-maghfirah/images/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
