const CACHE_NAME = 'ipim-v6';
const OFFLINE_URL = './index.html';

// Daftar asset yang di-cache saat install
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  './images/icon-192.png',
  './images/icon-512.png'
];

// ========== INSTALL ==========
self.addEventListener('install', event => {
  console.log('[SW] Install event:', CACHE_NAME);
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Caching assets...');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[SW] All assets cached successfully');
        return self.skipWaiting();
      })
      .catch(err => {
        console.error('[SW] Failed to cache:', err);
      })
  );
});

// ========== ACTIVATE ==========
self.addEventListener('activate', event => {
  console.log('[SW] Activate event:', CACHE_NAME);
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[SW] Taking control of clients');
      return self.clients.claim();
    })
  );
});

// ========== FETCH ==========
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Skip: non-GET, chrome extension, analytics, API
  if (
    request.method !== 'GET' ||
    request.url.startsWith('chrome-extension') ||
    url.pathname.includes('/api/') ||
    url.pathname.includes('/firestore/')
  ) {
    return;
  }
  
  // Skip: file yang tidak perlu di-cache
  if (url.pathname.match(/\.(mp4|avi|zip|rar)$/)) {
    return;
  }
  
  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        // Cache hit - return cached version
        if (cachedResponse) {
          console.log('[SW] Cache hit:', url.pathname);
          return cachedResponse;
        }
        
        // Cache miss - fetch from network
        console.log('[SW] Cache miss:', url.pathname);
        const fetchRequest = request.clone();
        
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
                  console.log('[SW] Caching new asset:', url.pathname);
                  cache.put(request, responseClone);
                })
                .catch(err => {
                  console.error('[SW] Failed to cache:', url.pathname, err);
                });
            }
            return networkResponse;
          })
          .catch(error => {
            console.error('[SW] Fetch failed:', url.pathname, error);
            
            // Fallback untuk HTML
            if (request.headers.get('accept').includes('text/html')) {
              console.log('[SW] Serving offline fallback page');
              return caches.match(OFFLINE_URL);
            }
            
            // Fallback untuk gambar
            if (request.headers.get('accept').includes('image')) {
              console.log('[SW] Serving offline image fallback');
              // Optional: return gambar placeholder
              // return caches.match('./images/placeholder.png');
            }
            
            // Fallback umum
            return new Response('Offline - Konten tidak tersedia', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
          });
      })
  );
});

// ========== MESSAGE HANDLING (Opsional) ==========
self.addEventListener('message', event => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
  
  if (event.data === 'clearCache') {
    caches.delete(CACHE_NAME).then(() => {
      console.log('[SW] Cache cleared manually');
      event.ports[0].postMessage({ success: true });
    });
  }
});
