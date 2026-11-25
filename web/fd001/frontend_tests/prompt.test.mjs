import assert from 'node:assert/strict';
import test from 'node:test';
import { evidencePrompt } from '../frontend/prompt.mjs';

// Synthetic structural input for unit tests. Real readings are verified by browser UAT.
const selection = { split: 'train', unit_id: 1, sensor_id: 7, cycle_start: 1, cycle_end: 2 };
const valid = {
  status: 'ok',
  data: { dataset_id: 'FD001', ...selection, observation_count: 2, points: [
    { cycle: 1, value: -0.25, source_record_index: 1, source_physical_line: 2, column_position: 12 },
    { cycle: 2, value: 0.75, source_record_index: 2, source_physical_line: 3, column_position: 12 },
  ] },
  provenance: { ...selection, contract_version: '1.0.0', verification_status: 'VERIFIED_LOCAL_SOURCE',
    sources: [{ source_filename: 'train_FD001.txt', source_sha256: 'a'.repeat(64) }],
    column_name: 'sensor_7', column_position: 12, calculation_method: 'Direct source lookup',
    index_base: 1, source_row_reference: '/data/points' },
};

test('deterministic prompt preserves signed decimal values, locators and statistics', () => {
  const text = evidencePrompt(valid, selection);
  assert.equal(text, evidencePrompt(structuredClone(valid), { ...selection }));
  for (const value of ['1 | -0.25 | 1 | 2 | 12', '2 | 0.75 | 2 | 3 | 12',
    'Mean: 0.25', 'OLS trend slope: 1', 'Missing count: 0']) assert.ok(text.includes(value));
});

test('singleton keeps zero and uses N/A for slope and sample deviation', () => {
  const response = structuredClone(valid), current = { ...selection, cycle_end: 1 };
  response.data.cycle_end = response.provenance.cycle_end = 1;
  response.data.points.splice(1);
  response.data.observation_count = 1;
  response.data.points[0].value = 0;
  const text = evidencePrompt(response, current);
  assert.match(text, /Sample standard deviation: N\/A/);
  assert.match(text, /OLS trend slope: N\/A/);
  assert.match(text, /Minimum: 0/);
});

test('reject every independently mismatched selection field', () => {
  for (const key of Object.keys(selection)) {
    assert.throws(() => evidencePrompt(valid, { ...selection, [key]: null }), /current selection/);
  }
});

test('reject malformed identity, empty data, invalid points and provenance', () => {
  for (const change of [
    r => { r.status = 'error'; },
    r => { r.data.points = []; },
    r => { r.data.observation_count = 1; },
    r => { r.data.points.reverse(); },
    r => { r.data.points[1].cycle = 1; },
    r => { r.data.points[0].value = null; },
    r => { r.data.points[0].value = Infinity; },
    r => { r.data.points[0].source_record_index = null; },
    r => { r.data.points[0].source_physical_line = 0; },
    r => { r.data.points[0].column_position = 11; },
    r => { r.provenance.sources[0].source_sha256 = 'invalid'; },
    r => { r.provenance.sources[0].source_filename = 'test_FD001.txt'; },
    r => { delete r.provenance.verification_status; },
    r => { r.provenance.cycle_end = 3; },
  ]) {
    const response = structuredClone(valid);
    change(response);
    assert.throws(() => evidencePrompt(response, selection));
  }
});
