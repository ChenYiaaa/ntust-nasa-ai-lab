import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium } from './local_only/node_modules/playwright-core/index.mjs';

const origin = 'http://127.0.0.1:8766';
const privateDir = new URL('./local_only/', import.meta.url);
const screenshot = new URL('../../../outputs/M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1/PUBLIC_SAFE/browser-initial.png', import.meta.url);
await mkdir(new URL('.', screenshot), { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1240, height: 900 } });
await page.context().grantPermissions(['clipboard-read', 'clipboard-write'], { origin });
const unexpected = [], consoleErrors = [], evidence = {};
page.on('pageerror', error => unexpected.push(error.message));
page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
const select = (id, value) => page.locator('#' + id).selectOption(value);
const visibleState = state => page.locator('#status[data-state="' + state + '"]').waitFor();
const recap = label => console.log('OK', label);
const generate = page.locator('#generate-prompt');
const copy = page.locator('#copy-prompt');
const preview = page.locator('#prompt-preview');

async function promptCleared() {
  assert.equal(await generate.isDisabled(), true);
  assert.equal(await copy.isDisabled(), true);
  assert.equal(await preview.inputValue(), '');
}

async function checkPrompt(actual, expected, points) {
  assert.equal(await copy.isDisabled(), true);
  await generate.click();
  const text = await preview.inputValue();
  const { data, provenance } = actual;
  for (const [name, value] of Object.entries({
    'Dataset ID': data.dataset_id, 'Contract version': provenance.contract_version, Split: data.split,
    'Engine Unit ID': data.unit_id, 'Sensor ID': data.sensor_id, 'Cycle Start': data.cycle_start,
    'Cycle End': data.cycle_end, 'Observation count': points.length,
    'Source filename': provenance.sources[0].source_filename,
    'Source SHA256': provenance.sources[0].source_sha256,
    'Source verification status': 'VERIFIED_LOCAL_SOURCE',
  })) assert.ok(text.split('\n').includes(name + ': ' + value), name);
  assert.deepEqual(text.split('\n').filter(line => /^\d+ \|/.test(line))
    .map(line => line.split(' | ').map(Number)), points.map(p =>
      [p.cycle, p.value, p.source_record_index, p.source_physical_line, p.column_position]));
  const labels = ['Count', 'Minimum', 'Maximum', 'Mean', 'Sample standard deviation', 'OLS trend slope', 'Missing count'];
  expected.forEach((value, i) => {
    const field = text.split('\n').find(line => line.startsWith(labels[i] + ': '));
    assert.ok(field, 'Prompt statistic missing: ' + labels[i]);
    const rendered = field.slice(labels[i].length + 2);
    if (value === null) assert.equal(rendered, 'N/A');
    else assert.ok(Math.abs(Number(rendered) - value) < 1e-7);
  });
  await copy.click();
  await page.getByText('Copied to clipboard.', { exact: true }).waitFor();
  const clipboard = await page.evaluate(() => navigator.clipboard.readText());
  // Windows writes native CRLF to the clipboard. HTML textarea values use LF.
  assert.ok(clipboard === text || (process.platform === 'win32' &&
    clipboard === text.replaceAll('\n', '\r\n')), 'Clipboard differs from preview');
  return text;
}

async function choose(split, unit) {
  const response = page.waitForResponse(r => r.url().endsWith('/api/units?split=' + split));
  await select('split', split);
  const units = await (await response).json();
  await page.waitForFunction(() => document.querySelector('#unit').options.length > 1);
  const options = await page.locator('#unit option').evaluateAll(nodes => nodes.slice(1).map(n => Number(n.value)));
  assert.deepEqual(options, units.data.unit_ids);
  assert.equal(await page.locator('#unit').inputValue(), '');
  await select('unit', unit);
  await page.waitForFunction(() => document.querySelector('#bounds').textContent.startsWith('Confirmed Cycle range'));
  await select('sensor', '7');
}

async function query(split, unit, start, end) {
  await page.locator('#start').fill(String(start));
  await page.locator('#end').fill(String(end));
  const path = '/api/history?' + new URLSearchParams({ split, unit, sensor: 7, start, end });
  const responsePromise = page.waitForResponse(r => r.url() === origin + path);
  await page.locator('#run').click();
  const response = await responsePromise;
  assert.equal(response.status(), 200);
  const actual = await response.json();
  const direct = await (await fetch('http://127.0.0.1:8765' + path)).json();
  assert.deepEqual(actual, direct);
  await visibleState('success');
  const points = actual.data.points;
  assert.equal(points.length, end - start + 1);
  assert.deepEqual(points.map(p => p.cycle), Array.from({ length: points.length }, (_, i) => i + start));
  const drawn = JSON.parse(await page.locator('#chart').getAttribute('data-points'));
  assert.deepEqual(drawn, points.map(p => [p.cycle, p.value]));
  const drawCalls = await page.evaluate(() => window.chartCalls);
  assert.equal(drawCalls.length, points.length);
  assert.ok(drawCalls.every(([x, y], i) => Number.isFinite(y) && (!i || x > drawCalls[i-1][0])));
  const values = points.map(p => p.value), n = values.length;
  const sum = values.reduce((a, b) => a + b, 0);
  const squares = values.reduce((a, b) => a + b * b, 0);
  const sx = points.reduce((a, p) => a + p.cycle, 0);
  const sx2 = points.reduce((a, p) => a + p.cycle ** 2, 0);
  const sxy = points.reduce((a, p) => a + p.cycle * p.value, 0);
  const expected = [n, Math.min(...values), Math.max(...values), sum / n,
    n > 1 ? Math.sqrt((squares - sum * sum / n) / (n - 1)) : null,
    n > 1 ? (n * sxy - sx * sum) / (n * sx2 - sx * sx) : null, 0];
  const stats = await page.locator('#stats dd').allTextContents();
  expected.forEach((x, i) => x === null ? assert.equal(stats[i], 'N/A') :
    assert.ok(Math.abs(Number(stats[i]) - x) < 1e-7, 'Statistic mismatch'));
  const prov = actual.provenance;
  assert.deepEqual(await page.locator('#provenance dd').allTextContents(), [
    'FD001', split, String(unit), '7', start + '–' + end, start + '–' + end,
    prov.sources[0].source_filename, prov.sources[0].source_sha256,
    prov.verification_status, prov.calculation_method,
  ]);
  await page.locator('#records summary').click();
  assert.deepEqual(await page.locator('#rows tr').evaluateAll(rows => rows.map(row =>
    Array.from(row.cells, cell => Number(cell.textContent)))), points.map(p =>
    [p.cycle, p.value, p.source_record_index, p.source_physical_line, p.column_position]));
  const prompt = await checkPrompt(actual, expected, points);
  evidence[split + '-' + n] = { actual, drawn, stats, expected, prompt };
  recap(split + ' ' + n + ' points, real canvas marks, statistics and provenance');
}

try {
  await page.addInitScript(() => {
    const proto = CanvasRenderingContext2D.prototype;
    const scale = proto.scale, arc = proto.arc;
    window.chartCalls = [];
    proto.scale = function (...args) {
      if (this.canvas.id === 'chart') window.chartCalls = [];
      return scale.apply(this, args);
    };
    proto.arc = function (...args) {
      if (this.canvas.id === 'chart') window.chartCalls.push(args.slice(0, 2));
      return arc.apply(this, args);
    };
  });
  const moduleRequest = page.waitForResponse(r => r.url() === origin + '/prompt.mjs');
  await page.goto(origin);
  const moduleResponse = await moduleRequest;
  assert.equal(moduleResponse.status(), 200);
  assert.equal(moduleResponse.headers()['content-type'], 'text/javascript; charset=utf-8');
  assert.equal(await preview.getAttribute('readonly'), '');
  await promptCleared();
  await visibleState('initial');
  assert.equal(await page.locator('#unit').isDisabled(), true);
  assert.equal(await page.locator('#results').isHidden(), true);
  assert.equal(await page.locator('#sensor option').count(), 22);
  assert.match(await page.locator('#sensor option[value="7"]').textContent(), /UNKNOWN/);
  await page.screenshot({ path: fileURLToPath(screenshot) });
  recap('Initial state, metadata, safe screenshot');
  await choose('train', '1');
  await query('train', 1, 1, 20);
  await choose('test', '2');
  await promptCleared();
  assert.equal(await page.locator('#results').isHidden(), true);
  await query('test', 2, 3, 5);
  await query('test', 2, 3, 3);
  await page.locator('#start').fill('5');
  await page.locator('#end').fill('3');
  await page.locator('#run').click();
  await visibleState('error');
  assert.match(await page.locator('#status').textContent(), /CYCLE_OUT_OF_RANGE/);
  await page.locator('#start').fill('3');
  await page.locator('#end').fill('5');

  const routePattern = '**/api/history?*end=5';
  let release;
  const hold = new Promise(resolve => { release = resolve; });
  await page.route(routePattern, async route => {
    const response = await route.fetch();
    await hold;
    await route.fulfill({ response }).catch(() => {});
  });
  await page.locator('#run').click();
  await visibleState('loading');
  await select('split', 'train');
  await page.waitForFunction(() => !document.querySelector('#unit').disabled);
  release();
  await page.unrouteAll({ behavior: 'wait' });
  await visibleState('initial');
  assert.equal(await page.locator('#results').isHidden(), true);
  assert.equal(await page.locator('#unit').inputValue(), '');
  recap('Loading and stale History rejected on split change');

  await select('unit', '1');
  await page.waitForFunction(() => !document.querySelector('#start').disabled);
  await page.locator('#end').fill('5');
  for (const [code, status] of [['SOURCE_NOT_VERIFIED', 503], ['RUL_MAPPING_INVALID', 503],
    ['INVALID_SPLIT', 400], ['UNKNOWN_UNIT', 404], ['UNKNOWN_SENSOR', 404], ['INVALID_PARAMETER', 400],
    ['CYCLE_OUT_OF_RANGE', 422], ['HTTP_500', 500], ['NETWORK_ERROR', 0]]) {
    await page.route(routePattern, route => !status ? route.abort() : route.fulfill({
      status, json: code === 'HTTP_500' ? {} : { status: 'error', error: { error_code: code, message: 'Controlled test' } },
    }));
    await page.locator('#run').click();
    await visibleState('error');
    assert.ok((await page.locator('#status').textContent()).includes(code));
    assert.equal(await page.locator('#results').isHidden(), true);
    await promptCleared();
    await page.unroute(routePattern);
  }
  await page.route(routePattern, route => route.fulfill({ json: {
    status: 'ok', data: { points: [], observation_count: 0 }, provenance: {},
  } }));
  await page.locator('#run').click();
  await visibleState('empty');
  assert.equal(await page.locator('#results').isHidden(), true);
  await promptCleared();
  await page.unroute(routePattern);
  recap('Controlled HTTP errors, network failure and empty result');

  for (const path of ['/data/FD001/train_FD001.txt', '/api/rul', '/serve.mjs', '/%2e%2e%2fdata/FD001/test_FD001.txt']) {
    assert.equal((await page.request.get(origin + path)).status(), 404);
  }
  assert.equal((await page.request.post(origin + '/api/history')).status(), 405);
  const badPath = '/api/history?split=train&unit=1&sensor=7&start=2&end=1';
  const [via, direct] = await Promise.all([fetch(origin + badPath), fetch('http://127.0.0.1:8765' + badPath)]);
  assert.equal(via.status, 422);
  assert.equal(await via.text(), await direct.text());
  await page.setViewportSize({ width: 375, height: 800 });
  await query('train', 1, 1, 5);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  await page.reload();
  await visibleState('initial');
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'split');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Tab');
  await page.waitForFunction(() => document.querySelector('#unit').options.length > 1);
  assert.equal(await page.locator('#split').inputValue(), 'train');
  recap('Private paths and write requests blocked, real HTTP error preserved, mobile and keyboard');
  for (const path of ['/', '/style.css', '/app.mjs', '/model.mjs', '/prompt.mjs']) {
    const response = await page.request.get(origin + path);
    assert.equal(response.status(), 200);
    assert.equal(response.headers()['cache-control'], 'no-store');
    assert.equal(response.headers()['x-content-type-options'], 'nosniff');
  }
  for (const path of ['/nonexistent', '/prompt.mjs/extra', '/%2e%2e%2fprompt.mjs']) {
    assert.equal((await page.request.get(origin + path)).status(), 404);
  }
  assert.equal((await page.request.get(origin, { headers: { host: 'invalid.example:8766' } })).status(), 400);
  for (const path of ['/api/health', '/api/catalog', '/api/units?split=train',
    '/api/history?split=train&unit=1&sensor=7&start=1&end=20']) {
    const [via, direct] = await Promise.all([fetch(origin + path), fetch('http://127.0.0.1:8765' + path)]);
    assert.equal(via.status, 200);
    assert.equal(await via.text(), await direct.text());
  }
  await select('unit', '1');
  await page.waitForFunction(() => !document.querySelector('#start').disabled);
  await select('sensor', '7');
  await query('train', 1, 1, 20);
  await select('unit', '2');
  await promptCleared();
  await select('unit', '1');
  await page.waitForFunction(() => !document.querySelector('#start').disabled);
  await query('train', 1, 1, 20);
  await select('sensor', '8');
  await promptCleared();
  await select('sensor', '7');
  await query('train', 1, 1, 20);
  await page.locator('#start').fill('2');
  await promptCleared();
  await query('train', 1, 1, 20);
  await page.locator('#end').fill('5');
  await promptCleared();
  await page.route(routePattern, async route => {
    const response = await route.fetch();
    const body = await response.json();
    delete body.data.points[0].source_record_index;
    await route.fulfill({ response, json: body });
  });
  await page.locator('#run').click();
  await page.getByText('This History response does not qualify for a prompt.').waitFor();
  await promptCleared();
  await page.unroute(routePattern);
  recap('M4 static and proxy routes, selection invalidation, invalid provenance and actual clipboard readback');
  if (process.env.FD001_NEGATIVE_ORIGIN) {
    const isolated = await browser.newPage();
    const health = isolated.waitForResponse(r => r.url().endsWith('/api/health'));
    await isolated.goto(process.env.FD001_NEGATIVE_ORIGIN);
    assert.equal((await health).status(), 503);
    await isolated.locator('#status[data-state="error"]').waitFor();
    assert.match(await isolated.locator('#status').textContent(), /SOURCE_NOT_VERIFIED/);
    assert.equal(await isolated.locator('#results').isHidden(), true);
    assert.equal(await isolated.locator('#generate-prompt').isDisabled(), true);
    assert.equal(await isolated.locator('#copy-prompt').isDisabled(), true);
    await isolated.close();
    recap('Real HTTP 503 retained by the proxy and shown in the browser');
  }
  assert.deepEqual(unexpected, []);
  assert.ok(consoleErrors.every(message => /Failed to load resource/.test(message)), consoleErrors.join('\n'));
  await writeFile(new URL('browser-comparisons.json', privateDir), JSON.stringify(evidence, null, 2));
  console.log('Edge', browser.version(), '| JavaScript exceptions', unexpected.length,
    '| resource errors from expected error paths or favicon', consoleErrors.length);
} finally { await browser.close(); }
