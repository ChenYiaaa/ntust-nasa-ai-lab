import assert from 'node:assert/strict';
import test from 'node:test';
import { api, chartPoints, format, latestRequest, statistics } from '../frontend/model.mjs';

test('negative decimal points and unrounded statistics', () => {
  const points = chartPoints([{ cycle: 1, value: -2.5 }, { cycle: 3, value: 1.5 }]);
  assert.deepEqual(points, [[1, -2.5], [3, 1.5]]);
  assert.deepEqual(statistics(points, 1, 3),
    { count: 2, min: -2.5, max: 1.5, mean: -.5, deviation: Math.sqrt(8), slope: 2, missing: 1 });
});

test('empty and singleton statistics are inapplicable where required', () => {
  assert.equal(statistics([], 1, 3).mean, null);
  assert.equal(statistics([], 1, 3).missing, 3);
  assert.equal(statistics([[1, 0]], 1, 1).slope, null);
  assert.equal(statistics([[1, 0]], 1, 1).deviation, null);
  assert.equal(format(null), 'N/A');
  assert.equal(format(0), '0');
  assert.throws(() => chartPoints([{ cycle: 1, value: null }]), { code: 'INVALID_RESPONSE' });
});

test('latest request cancels and invalidates prior generations', () => {
  const gate = latestRequest(), original = gate.begin(), next = gate.begin();
  assert.equal(original.active(), false);
  assert.equal(original.signal.aborted, true);
  assert.equal(next.active(), true);
  gate.cancel();
  assert.equal(next.active(), false);
});

test('API preserves data and provenance and surfaces structured errors', async t => {
  const provenance = { verification_status: 'VERIFIED_LOCAL_SOURCE' };
  const body = { status: 'ok', data: { points: [] }, provenance };
  const fetch = t.mock.method(globalThis, 'fetch', async () => Response.json(body));
  assert.deepEqual(await api('history', { split: 'train' }), body);
  assert.equal(fetch.mock.calls[0].arguments[0], '/api/history?split=train');
  for (const [code, status] of Object.entries({
    INVALID_SPLIT: 400, INVALID_PARAMETER: 400, UNKNOWN_UNIT: 404, UNKNOWN_SENSOR: 404,
    CYCLE_OUT_OF_RANGE: 422, SOURCE_NOT_VERIFIED: 503, RUL_MAPPING_INVALID: 503,
  })) {
    fetch.mock.mockImplementation(async () => Response.json({ error: { error_code: code,
      message: 'test', input_context: { split: 'test' } } }, { status }));
    await assert.rejects(api('history'), { code, context: { split: 'test' } });
  }
  fetch.mock.mockImplementation(async () => new Response('oops', { status: 500 }));
  await assert.rejects(api('history'), { code: 'HTTP_500' });
});
