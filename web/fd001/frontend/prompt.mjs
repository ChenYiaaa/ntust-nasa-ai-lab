import { chartPoints, format, statistics } from './model.mjs';

const keys = ['split', 'unit_id', 'sensor_id', 'cycle_start', 'cycle_end'];
const positive = value => Number.isSafeInteger(value) && value > 0;

export function evidencePrompt(response, selection) {
  const { status, data, provenance } = response ?? {};
  const require = (condition, message) => { if (!condition) throw new Error(message); };
  require(status === 'ok' && data && provenance && selection, 'A verified History response is required.');
  const { split, unit_id, sensor_id, cycle_start, cycle_end, points } = data;
  require(data.dataset_id === 'FD001' && provenance.contract_version === '1.0.0' &&
    ['train', 'test'].includes(split) && [unit_id, sensor_id, cycle_start, cycle_end].every(positive) &&
    sensor_id <= 21 && cycle_start <= cycle_end, 'Invalid evidence identity.');
  require(keys.every(key => data[key] === selection[key] && data[key] === provenance[key]),
    'History does not match the current selection and provenance.');
  require(Array.isArray(points) && points.length > 0 && data.observation_count === points.length &&
    points.length === cycle_end - cycle_start + 1, 'History observation count or coverage is inconsistent.');
  const source = provenance.sources?.[0];
  require(Array.isArray(provenance.sources) && provenance.sources.length === 1 &&
    source?.source_filename === split + '_FD001.txt' && typeof source.source_sha256 === 'string' &&
    /^[a-f0-9]{64}$/.test(source.source_sha256) && provenance.verification_status === 'VERIFIED_LOCAL_SOURCE' &&
    provenance.index_base === 1 && provenance.source_row_reference === '/data/points' &&
    provenance.column_name === 'sensor_' + sensor_id && provenance.column_position === sensor_id + 5 &&
    provenance.calculation_method === 'Direct source lookup', 'Invalid source provenance.');
  require(points.every((point, index) => point && point.cycle === cycle_start + index &&
    positive(point.source_record_index) && positive(point.source_physical_line) &&
    point.source_physical_line >= point.source_record_index && point.column_position === provenance.column_position),
  'Invalid Cycle or source row locator.');
  require(new Set(points.map(point => point.source_record_index)).size === points.length &&
    new Set(points.map(point => point.source_physical_line)).size === points.length, 'Duplicate source row locator.');
  const pairs = chartPoints(points);
  const stats = statistics(pairs, cycle_start, cycle_end);
  require(Object.values(stats).every(value => value === null || Number.isFinite(value)), 'Invalid derived statistic.');

  return [
    'FD001 evidence for analysis', '', 'Evidence identity',
    'Dataset ID: ' + data.dataset_id, 'Contract version: ' + provenance.contract_version,
    'Split: ' + split, 'Engine Unit ID: ' + unit_id, 'Sensor ID: ' + sensor_id,
    'Cycle Start: ' + cycle_start, 'Cycle End: ' + cycle_end, 'Observation count: ' + points.length,
    '', 'Observed source data',
    'Source filename: ' + source.source_filename, 'Source SHA256: ' + source.source_sha256,
    'Source verification status: ' + provenance.verification_status,
    'Source lookup method: ' + provenance.calculation_method,
    'Cycle | Sensor value | Source record index | Source physical line | Source column position',
    ...points.map(point => [point.cycle, point.value, point.source_record_index,
      point.source_physical_line, point.column_position].join(' | ')),
    '', 'Calculated statistics',
    ...[['Count', stats.count], ['Minimum', stats.min], ['Maximum', stats.max],
      ['Mean', stats.mean], ['Sample standard deviation', stats.deviation],
      ['OLS trend slope', stats.slope], ['Missing count', stats.missing]].map(([label, value]) => label + ': ' + format(value)),
    'Basis: arithmetic mean of observed values, sample deviation with n − 1, OLS with intercept against observed Cycle.',
    'Missing count is the inclusive requested range length minus observed count.',
    'N/A means insufficient observations for sample deviation or insufficient Cycle variance for slope.',
    '', 'Analysis instructions',
    'Treat observed values and computed statistics as evidence. Distinguish observations, calculations and interpretations.',
    'Describe variation or trends only when supported by observations. Sensor physical units are UNKNOWN unless explicitly defined in the contract.',
    'Do not claim a fault without validated evidence or invent Health Scores, Failure Probabilities or RUL predictions.',
    'Do not invent missing Cycles or interpolate values.',
  ].join('\n');
}
