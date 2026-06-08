const CACHE_NAME = 'ipim-v2';

const urlsToCache = [
  '/ipim-digital-maghfirah/',
  '/ipim-digital-maghfirah/index.html',
  '/ipim-digital-maghfirah/style.css',
  '/ipim-digital-maghfirah/manifest.json',
  '/ipim-digital-maghfirah/images/icon-192.png',
  '/ipim-digital-maghfirah/images/icon-512.png'
];

// Install Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

// Activate Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    )
  );
  self.clients.claim();
});

// Fetch: Cache First + Auto Cache
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request)
        .then(networkResponse => {
          if (
            event.request.method === 'GET' &&
            networkResponse.status === 200
          ) {
            const responseClone = networkResponse.clone();

            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }

          return networkResponse;
        })
        .catch(() => {
          return caches.match('/ipim-digital-maghfirah/index.html');
        });
    })
  );
});
