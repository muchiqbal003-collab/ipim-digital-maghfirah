const CACHE_NAME = 'ipim-v8';
const BASE_URL = '/ipim-digital-maghfirah';

const urlsToCache = [
  BASE_URL + '/',
  BASE_URL + '/index.html',
  BASE_URL + '/manifest.json',
  BASE_URL + '/images/icon-192.png',
  BASE_URL + '/images/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => 
      Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) return caches.delete(key);
      }))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(() => caches.match(BASE_URL + '/index.html'))
  );
});
