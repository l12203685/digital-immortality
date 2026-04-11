const CACHE_NAME = 'eai-v2-pages';
const STATIC_ASSETS = ['listen.html', 'manifest.json'];
const NTFY_ORIGIN = 'https://ntfy.sh';
const OFFLINE_QUEUE_KEY = 'eai-offline-queue';

// Install: cache static assets
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: cache-first for static, network-first for ntfy
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  // Never cache ntfy SSE/polling or POST/PUT requests
  if (url.origin === NTFY_ORIGIN || e.request.method !== 'GET') return;

  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((response) => {
        if (response.ok && url.origin === self.location.origin) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
        }
        return response;
      });
    }).catch(() => {
      // Offline fallback for navigation
      if (e.request.mode === 'navigate') {
        return caches.match('listen.html');
      }
    })
  );
});

// Message handler: queue ntfy messages when offline
self.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'QUEUE_NTFY') {
    enqueueMessage(e.data.payload);
  }
});

async function enqueueMessage(payload) {
  try {
    const response = await fetch(payload.url, {
      method: payload.method,
      headers: payload.headers,
      body: payload.body
    });
    if (response.ok) return;
  } catch (_) {
    // Offline — queue it
  }
  // Store in IndexedDB-like storage via cache API workaround
  const queue = await getQueue();
  queue.push(payload);
  await saveQueue(queue);
}

async function getQueue() {
  try {
    const cache = await caches.open(CACHE_NAME);
    const resp = await cache.match('/__offline_queue__');
    if (resp) return await resp.json();
  } catch (_) {}
  return [];
}

async function saveQueue(queue) {
  const cache = await caches.open(CACHE_NAME);
  await cache.put(
    '/__offline_queue__',
    new Response(JSON.stringify(queue), { headers: { 'Content-Type': 'application/json' } })
  );
}

// Flush queue when back online
self.addEventListener('sync', (e) => {
  if (e.tag === 'flush-ntfy') {
    e.waitUntil(flushQueue());
  }
});

// Also flush periodically on fetch success
async function flushQueue() {
  const queue = await getQueue();
  if (queue.length === 0) return;
  const remaining = [];
  for (const payload of queue) {
    try {
      const response = await fetch(payload.url, {
        method: payload.method,
        headers: payload.headers,
        body: payload.body
      });
      if (!response.ok) remaining.push(payload);
    } catch (_) {
      remaining.push(payload);
    }
  }
  await saveQueue(remaining);
}
