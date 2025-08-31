// Service Worker para cache offline - otimização mobile
const CACHE_NAME = 'vistoria-agil-v1';
const urlsToCache = [
    '/',
    '/css/style.css',
    '/js/app.js',
    '/favicon.svg',
    'https://unpkg.com/lucide@latest/dist/umd/lucide.js'
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Cache aberto');
                return cache.addAll(urlsToCache);
            })
    );
});

// Interceptar requisições
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Retornar cache se disponível, senão buscar na rede
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});

// Atualizar cache
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
