const CACHE_NAME = 'ipim-absensi-v1'
const urlsToCache = [
  '/absensi-kampus/',
  '/absensi-kampus/index.html',
  '/absensi-kampus/absensi.html',
  '/absensi-kampus/manifest.json',
  '/absensi-kampus/images/icon-192.png',
  '/absensi-kampus/images/icon-512.png'
]

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  )
})

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  )
})