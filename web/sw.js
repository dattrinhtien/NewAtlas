/**
 * ACUATLAS 3D PRO - SERVICE WORKER
 * Cung cấp khả năng Offline & Caching PWA tối ưu cho Mobile & Desktop
 */

const STATIC_CACHE = 'acuatlas3d-static-v18';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo-icon.png',
  '/logo-icon-hd.png',
  '/logo-full.png',
  '/css/style.css',
  '/assets/index-C5F3MQx3.css?v=master_z48',
  '/assets/index-CGRTTg94.js?v=master_z51',
  '/js/vendor/three.module.js',
  '/js/vendor/GLTFLoader.js',
  '/js/utils/BufferGeometryUtils.js',
  '/js/storageManager.js',
  '/js/dissectionStudio.js',
  '/data/acupoints.json',
  '/data/anatomyDictionary.json',
  '/data/osteologyDictionary.json',
  '/data/organDictionary.json',
  '/js/data/anatomyDictionary.json',
  '/js/data/osteologyDictionary.json',
  '/js/data/organDictionary.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(async (cache) => {
      for (const asset of ASSETS_TO_CACHE) {
        try {
          await cache.add(asset);
        } catch (err) {
          // Tiếp tục kể cả khi 1 tệp phụ chưa sẵn sàng
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== STATIC_CACHE && key !== 'acuatlas3d-models-v9-manifold-neck') {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const requestUrl = new URL(event.request.url);

  // Không chặn các request API Supabase hay VietQR
  if (
    requestUrl.origin.includes('supabase.co') ||
    requestUrl.origin.includes('vietqr.io') ||
    event.request.method !== 'GET'
  ) {
    return;
  }

  // Model GLB đã được quản lý chuyên dụng trong CacheStorage (Ru) và IndexedDB (storageManager.js)
  if (requestUrl.pathname.endsWith('.glb')) {
    return;
  }

  // Chiến lược Stale-While-Revalidate cho các tệp JS/CSS/JSON/Images để mở siêu tốc (<0.1s) ở lần truy cập sau
  const isFastStatic =
    requestUrl.pathname.startsWith('/js/') ||
    requestUrl.pathname.startsWith('/data/') ||
    requestUrl.pathname.startsWith('/assets/') ||
    requestUrl.pathname.startsWith('/css/') ||
    requestUrl.pathname.endsWith('.png') ||
    requestUrl.pathname.endsWith('.mp3') ||
    requestUrl.pathname.endsWith('.mp4');

  if (isFastStatic) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              const responseToCache = networkResponse.clone();
              caches.open(STATIC_CACHE).then((cache) => {
                cache.put(event.request, responseToCache);
              });
            }
            return networkResponse;
          })
          .catch(() => cachedResponse);
        return cachedResponse || fetchPromise;
      })
    );
    return;
  }

  // Network First, Fallback to Cache cho trang HTML chính
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(STATIC_CACHE).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});
