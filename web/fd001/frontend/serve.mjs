import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';

const port = Number(process.env.FD001_FRONTEND_PORT ?? 8766);
const backend = Number(process.env.FD001_BACKEND_PORT ?? 8765);
const routes = new Set(['/api/health', '/api/catalog', '/api/units', '/api/history']);
const assets = new Map([
  ['/', ['index.html', 'text/html']], ['/style.css', ['style.css', 'text/css']],
  ['/app.mjs', ['app.mjs', 'text/javascript']], ['/model.mjs', ['model.mjs', 'text/javascript']],
]);
const send = (res, status, type, body) => res.writeHead(status, {
  'Content-Type': type, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
}).end(body);
const server = createServer(async (req, res) => {
  if (!['127.0.0.1', 'localhost'].some(host => req.headers.host === host + ':' + port)) {
    return send(res, 400, 'text/plain', 'Invalid host');
  }
  if (req.method !== 'GET') return send(res, 405, 'text/plain', 'GET required');
  const path = req.url.split('?')[0];
  try {
    if (routes.has(path)) {
      const upstream = await fetch('http://127.0.0.1:' + backend + req.url, {
        redirect: 'manual', signal: AbortSignal.timeout(10000),
      });
      return send(res, upstream.status, upstream.headers.get('content-type'),
        Buffer.from(await upstream.arrayBuffer()));
    }
    const asset = assets.get(path);
    if (!asset) return send(res, 404, 'text/plain', 'Not found');
    return send(res, 200, asset[1] + '; charset=utf-8', await readFile(new URL(asset[0], import.meta.url)));
  } catch {
    return send(res, 502, 'application/json', JSON.stringify({
      status: 'error', error: { error_code: 'UPSTREAM_UNAVAILABLE', message: 'Local API unavailable.' },
    }));
  }
});
server.listen(port, '127.0.0.1', () => console.log('Frontend http://127.0.0.1:' + port));
for (const signal of ['SIGINT', 'SIGBREAK', 'SIGTERM']) process.on(signal, () => server.close());
