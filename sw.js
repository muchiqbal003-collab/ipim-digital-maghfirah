const CACHE_NAME = 'ipim-v5'; // Update version

const urlsToCache = [
  './',  // Root path
  './index.html',
  './manifest.json',
  './images/icon-192.png',
  './images/icon-512.png'
];

// Install Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Caching assets...');
        return cache.addAll(urlsToCache);
      })
      .catch(err => {
        console.error('Failed to cache:', err);
      })
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
            console.log('Deleting old cache:', key);
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
  // Skip non-GET requests and chrome-extension
  if (event.request.method !== 'GET' || event.request.url.startsWith('chrome-extension')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        // Return cached response if found
        if (cachedResponse) {
          return cachedResponse;
        }

        // Clone request karena bisa dipakai dua kali
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest)
          .then(networkResponse => {
            // Only cache valid responses
            if (
              networkResponse &&
              networkResponse.status === 200 &&
              networkResponse.type === 'basic'
            ) {
              const responseClone = networkResponse.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseClone);
                });
            }
            return networkResponse;
          })
          .catch(() => {
            // Fallback untuk offline
            if (event.request.url.match(/\.html$/)) {
              return caches.match('./index.html');
            }
            // Untuk asset yang tidak ada cache, return error 404
            return new Response('Offline - Konten tidak tersedia', {
              status: 404,
              statusText: 'Not Found'
            });
          });
      })
  );
});
