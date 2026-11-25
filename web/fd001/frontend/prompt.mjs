import { chartPoints, format, statistics } from './model.mjs';

const keys = ['split', 'unit_id', 'sensor_id', 'cycle_start', 'cycle_end'];
const positive = value => Number.isSafeInteger(value) && value > 0;

export function evidencePrompt(response, selection, sensor) {
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
    provenance.column_position === sensor_id + 5 &&
    provenance.calculation_method === 'Direct source lookup', 'Invalid source provenance.');
  require(sensor?.sensor_id === sensor_id && sensor.column_name === provenance.column_name &&
    typeof sensor.column_name === 'string' && /^[a-z][a-z0-9_]*$/.test(sensor.column_name) &&
    sensor.column_position === provenance.column_position && sensor.source_field === sensor.column_position &&
    sensor.semantic_role === 'sensor' && sensor.dtype === 'number' && sensor.nullable === false &&
    sensor.unit_of_measure_if_known === 'UNKNOWN', 'Missing or inconsistent sensor Catalog metadata.');
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
    'SECTION A: DATASET & SELECTION',
    'Dataset ID: ' + data.dataset_id, 'Data Contract Version: ' + provenance.contract_version,
    'Split: ' + split, 'Engine Unit ID: ' + unit_id, 'Sensor ID: ' + sensor_id,
    'Cycle Start: ' + cycle_start, 'Cycle End: ' + cycle_end, 'Observation Count: ' + points.length,
    '', 'SECTION B: SOURCE PROVENANCE',
    'Source Filename: ' + source.source_filename, 'Source SHA256: ' + source.source_sha256,
    'Verification Status: ' + provenance.verification_status,
    'Source lookup method: ' + provenance.calculation_method,
    'Each Source Record Index, Source Physical Line and Source Column Position in Section D is 1-based and refers to this filename and SHA256.',
    '', 'SECTION C: COLUMN SEMANTICS',
    'Engine Unit: equipment identifier.',
    'Cycle: observation cycle or time index.',
    'Sensor: selected sensor column.',
    'Value: observed numeric reading for that Cycle.',
    'Raw Index: location of the original source record.',
    ...['sensor_id', 'column_name', 'column_position', 'semantic_role', 'dtype', 'source_field',
      'unit_of_measure_if_known', 'nullable'].map(key => key + ': ' + sensor[key]),
    '', 'SECTION D: OBSERVED DATA',
    'Cycle | Sensor Value | Source Record Index | Source Physical Line | Source Column Position',
    ...points.map(point => [point.cycle, point.value, point.source_record_index,
      point.source_physical_line, point.column_position].join(' | ')),
    '', 'SECTION E: DATA QUALITY', 'Evidence class: CALCULATED',
    ...[['Observation Count', stats.count], ['Minimum', stats.min], ['Maximum', stats.max],
      ['Mean', stats.mean], ['Sample standard deviation', stats.deviation],
      ['OLS trend slope', stats.slope], ['Missing count', stats.missing]].map(([label, value]) => label + ': ' + format(value)),
    'Sample standard deviation status: ' + (stats.deviation === null ? 'Not Applicable' : 'Applicable'),
    'OLS trend slope status: ' + (stats.slope === null ? 'Not Applicable' : 'Applicable'),
    'Verified Source Status: ' + provenance.verification_status,
    'Count is the number of returned observations. Mean is their arithmetic mean.',
    'Sample standard deviation uses n − 1. OLS slope fits an intercept against observed Cycle.',
    'Missing count is the inclusive requested range length minus observed count.',
    'For one observation, sample standard deviation and OLS slope are N/A. A slope also needs Cycle variance.',
    'Physical unit is ' + sensor.unit_of_measure_if_known + '. These statistics describe only the selected window.',
    'Verification checks the local source snapshot and record traceability. The statistics do not establish equipment condition or causality.',
    '', 'SECTION F: KNOWN FACTS', 'Evidence class: OBSERVED',
    'FD001 ' + split + ' Unit ' + unit_id + ' returned ' + points.length + ' observations for ' +
      sensor.column_name + ' over Cycles ' + cycle_start + '–' + cycle_end + '.',
    'Section D lists the readings and original row locators from the verified source in Section B.',
    'Section C gives the selected column definition from the FD001 Catalog.',
    '', 'SECTION G: INFERRED FINDINGS', 'Evidence class: INFERRED',
    'No additional inference established from the available evidence.',
    '', 'SECTION H: UNKNOWN / NOT ESTABLISHED', 'Evidence class: UNKNOWN',
    'Fault Status: NOT ESTABLISHED', 'Fault Type: NOT ESTABLISHED', 'Fault Cause: NOT ESTABLISHED',
    'RUL: NOT ESTIMATED', 'Health Score: NOT ESTABLISHED',
    'Physical Sensor Unit: ' + sensor.unit_of_measure_if_known, 'Physical Sensor Meaning: UNKNOWN',
    'These declarations state the limits of the available evidence.',
    '', 'SECTION I: INSTRUCTIONS TO EXTERNAL AI',
    '1. Distinguish OBSERVED, CALCULATED, INFERRED and UNKNOWN.',
    '2. Avoid turning statistical correlation into fault causality.',
    '3. Never invent Fault Type or Fault Cause.',
    '4. Never invent Failure Probability.',
    '5. Never invent RUL.',
    '6. Never invent Health Score.',
    '7. Never synthesize missing Cycles or Sensor Values.',
    '8. State when the evidence is insufficient.',
    '9. Link every supported judgment to specific evidence.',
    '10. Never claim to have executed an unperformed predictive model.',
  ].join('\n');
}
