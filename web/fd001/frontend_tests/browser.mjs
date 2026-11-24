import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium } from './local_only/node_modules/playwright-core/index.mjs';

const origin = 'http://127.0.0.1:8766';
const privateDir = new URL('./local_only/', import.meta.url);
const screenshot = new URL('../../../outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/frontend/PUBLIC_SAFE/browser-initial.png', import.meta.url);
await mkdir(new URL('.', screenshot), { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1240, height: 900 } });
const unexpected = [], consoleErrors = [], evidence = {};
page.on('pageerror', error => unexpected.push(error.message));
page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
const select = (id, value) => page.locator('#' + id).selectOption(value);
const visibleState = state => page.locator('#status[data-state="' + state + '"]').waitFor();
const recap = label => console.log('OK', label);

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
  evidence[split + '-' + n] = { actual, drawn, stats, expected };
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
  await page.goto(origin);
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
    await page.unroute(routePattern);
  }
  await page.route(routePattern, route => route.fulfill({ json: {
    status: 'ok', data: { points: [], observation_count: 0 }, provenance: {},
  } }));
  await page.locator('#run').click();
  await visibleState('empty');
  assert.equal(await page.locator('#results').isHidden(), true);
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
  if (process.env.FD001_NEGATIVE_ORIGIN) {
    const isolated = await browser.newPage();
    const health = isolated.waitForResponse(r => r.url().endsWith('/api/health'));
    await isolated.goto(process.env.FD001_NEGATIVE_ORIGIN);
    assert.equal((await health).status(), 503);
    await isolated.locator('#status[data-state="error"]').waitFor();
    assert.match(await isolated.locator('#status').textContent(), /SOURCE_NOT_VERIFIED/);
    assert.equal(await isolated.locator('#results').isHidden(), true);
    await isolated.close();
    recap('Real HTTP 503 retained by the proxy and shown in the browser');
  }
  assert.deepEqual(unexpected, []);
  assert.ok(consoleErrors.every(message => /Failed to load resource/.test(message)), consoleErrors.join('\n'));
  await writeFile(new URL('browser-comparisons.json', privateDir), JSON.stringify(evidence, null, 2));
  console.log('Edge', browser.version(), '| JavaScript exceptions', unexpected.length,
    '| resource errors from expected error paths or favicon', consoleErrors.length);
} finally { await browser.close(); }
