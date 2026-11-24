import { api, ApiError, chartPoints, format, latestRequest, statistics } from './model.mjs';

const $ = id => document.getElementById(id);
const split = $('split'), unit = $('unit'), sensor = $('sensor');
const start = $('start'), end = $('end'), run = $('run');
const units = latestRequest(), bounds = latestRequest(), history = latestRequest();
const sensors = new Map();
let range, plotted = [];

function state(kind, message) {
  $('status').dataset.state = kind;
  $('status').textContent = message;
}

function failure(error) {
  state('error', (error.code ?? 'NETWORK_ERROR') + ' · ' +
    (error instanceof ApiError ? error.message : 'Could not reach the local service.'));
}

function options(select, label, entries) {
  select.replaceChildren(new Option(label, ''), ...entries.map(([value, text]) => new Option(text, value)));
  select.disabled = !entries.length;
}

function clear() {
  history.cancel();
  plotted = [];
  $('results').hidden = true;
  $('records').open = false;
  for (const id of ['stats', 'provenance', 'rows']) $(id).replaceChildren();
  delete $('chart').dataset.points;
  const canvas = $('chart');
  canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
}

function resetRange() {
  bounds.cancel();
  range = undefined;
  start.value = end.value = '';
  start.disabled = end.disabled = run.disabled = true;
  $('bounds').textContent = 'Select an engine unit to confirm its Cycle range.';
}

split.addEventListener('change', async () => {
  clear();
  resetRange();
  const request = units.begin();
  options(unit, 'Select unit', []);
  if (!split.value) return state('initial', 'Select a dataset split.');
  state('loading', 'Loading engine units…');
  try {
    const { data } = await api('units', { split: split.value }, request.signal);
    if (!request.active()) return;
    options(unit, 'Select unit', data.unit_ids.map(id => [id, 'Unit ' + id]));
    state(data.unit_ids.length ? 'initial' : 'empty',
      data.unit_ids.length ? 'Select an engine unit.' : 'This split has no engine units.');
  } catch (error) { if (request.active()) failure(error); }
});

unit.addEventListener('change', async () => {
  clear();
  resetRange();
  if (!unit.value) return state('initial', 'Select an engine unit.');
  const request = bounds.begin();
  state('loading', 'Confirming Cycle range…');
  const selection = { split: split.value, unit: unit.value };
  try {
    // The accepted range error reports the observed boundaries for this exact unit.
    await api('history', { ...selection, sensor: sensors.keys().next().value, start: 1, end: 0 }, request.signal);
    throw new ApiError('INVALID_RESPONSE', 'Expected Cycle boundary information.');
  } catch (error) {
    if (!request.active()) return;
    const context = error.context;
    const low = context?.first_cycle, high = context?.last_observed_cycle;
    if (error.code !== 'CYCLE_OUT_OF_RANGE' || context?.split !== selection.split ||
        String(context.unit_id) !== selection.unit || !Number.isSafeInteger(low) ||
        !Number.isSafeInteger(high) || low < 1 || high < low) return failure(error);
    range = [low, high];
    for (const field of [start, end]) {
      field.min = low;
      field.max = high;
      field.disabled = false;
    }
    start.value = low;
    end.value = high;
    $('bounds').textContent = 'Confirmed Cycle range: ' + low + '–' + high;
    ready();
  }
});

function ready() {
  run.disabled = !range || !sensor.value;
  if (range) state('initial', sensor.value ? 'Set a Cycle range and query history.' : 'Select a sensor.');
}

for (const field of [sensor, start, end]) field.addEventListener(field === sensor ? 'change' : 'input', () => {
  clear();
  ready();
});

$('query').addEventListener('submit', async event => {
  event.preventDefault();
  clear();
  if (!range || !sensor.value) return;
  const first = start.valueAsNumber, last = end.valueAsNumber;
  if (!Number.isSafeInteger(first) || !Number.isSafeInteger(last)) {
    return state('error', 'INVALID_PARAMETER · Enter whole numbers for both Cycles.');
  }
  if (first > last || first < range[0] || last > range[1]) {
    return state('error', 'CYCLE_OUT_OF_RANGE · Choose an ordered range within the confirmed bounds.');
  }
  const request = history.begin();
  state('loading', 'Loading sensor history…');
  try {
    const body = await api('history', {
      split: split.value, unit: unit.value, sensor: sensor.value, start: first, end: last,
    }, request.signal);
    if (request.active()) render(body);
  } catch (error) {
    if (request.active()) { clear(); failure(error); }
  }
});

function descriptions(id, fields) {
  $(id).replaceChildren(...fields.map(([label, value]) => {
    const group = document.createElement('div');
    const term = document.createElement('dt'), detail = document.createElement('dd');
    term.textContent = label;
    detail.textContent = format(value);
    group.append(term, detail);
    return group;
  }));
}

function render({ data, provenance }) {
  const pairs = chartPoints(data.points);
  if (data.observation_count !== pairs.length) throw new ApiError('INVALID_RESPONSE', 'Observation count differs from History points.');
  if (!pairs.length) return state('empty', 'No observations in the returned range.');
  const stats = statistics(pairs, data.cycle_start, data.cycle_end);
  const rangeText = (a, b) => a + '–' + b;
  const metadata = sensors.get(data.sensor_id);
  $('selection').textContent = data.split + ' / Unit ' + data.unit_id + ' / Sensor ' + data.sensor_id +
    ' · Physical unit ' + metadata.unit_of_measure_if_known;
  descriptions('stats', [
    ['Observation count', stats.count], ['Minimum', stats.min], ['Maximum', stats.max],
    ['Mean', stats.mean], ['Sample standard deviation', stats.deviation], ['OLS trend slope', stats.slope],
    ['Missing count', stats.missing],
  ]);
  const source = provenance.sources[0];
  descriptions('provenance', [
    ['Dataset ID', data.dataset_id], ['Split', data.split], ['Unit ID', data.unit_id], ['Sensor ID', data.sensor_id],
    ['Requested Cycle range', rangeText(provenance.cycle_start, provenance.cycle_end)],
    ['Returned Cycle range', rangeText(pairs[0][0], pairs.at(-1)[0])],
    ['Source filename', source.source_filename], ['Source SHA256', source.source_sha256],
    ['Verification status', provenance.verification_status], ['Calculation method', provenance.calculation_method],
  ]);
  $('rows').replaceChildren(...data.points.map(point => {
    const row = document.createElement('tr');
    for (const key of ['cycle', 'value', 'source_record_index', 'source_physical_line', 'column_position']) {
      row.insertCell().textContent = format(point[key]);
    }
    return row;
  }));
  plotted = pairs;
  $('results').hidden = false;
  draw();
  state('success', pairs.length + ' observations returned.');
}

function draw() {
  if (!plotted.length) return;
  const canvas = $('chart'), width = canvas.clientWidth, height = canvas.clientHeight;
  const pixelRatio = window.devicePixelRatio || 1;
  canvas.width = width * pixelRatio;
  canvas.height = height * pixelRatio;
  const ctx = canvas.getContext('2d');
  ctx.scale(pixelRatio, pixelRatio);
  const left = 74, right = width - 18, top = 18, bottom = height - 48;
  const first = plotted[0][0], last = plotted.at(-1)[0];
  const values = plotted.map(point => point[1]);
  let low = Math.min(...values), high = Math.max(...values);
  const padding = high === low ? Math.max(Math.abs(low) * .025, .01) : (high - low) * .08;
  low -= padding;
  high += padding;
  ctx.font = '12px system-ui';
  for (let tick = 0; tick <= 4; tick++) {
    const y = bottom - tick * (bottom - top) / 4;
    ctx.strokeStyle = '#d7e4e8';
    ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(right, y); ctx.stroke();
    ctx.fillStyle = '#3d5967'; ctx.textAlign = 'right';
    ctx.fillText(String(Number((low + (high - low) * tick / 4).toPrecision(6))), left - 7, y + 4);
  }
  const cycles = new Set(Array.from({ length: 5 }, (_, i) => Math.round(first + (last - first) * i / 4)));
  const x = cycle => first === last ? (left + right) / 2 :
    left + 5 + (cycle - first) / (last - first) * (right - left - 10);
  ctx.textAlign = 'center';
  for (const cycle of cycles) ctx.fillText(String(cycle), x(cycle), bottom + 18);
  ctx.fillText('Cycle', (left + right) / 2, height - 8);
  ctx.save(); ctx.translate(13, (top + bottom) / 2); ctx.rotate(-Math.PI / 2);
  ctx.fillText('Sensor Value', 0, 0); ctx.restore();
  ctx.fillStyle = '#09655c';
  const drawn = [];
  for (const [cycle, value] of plotted) {
    ctx.beginPath();
    ctx.arc(x(cycle), bottom - (value - low) / (high - low) * (bottom - top), 3.5, 0, Math.PI * 2);
    ctx.fill();
    drawn.push([cycle, value]);
  }
  canvas.dataset.points = JSON.stringify(drawn);
}

new ResizeObserver(draw).observe($('chart'));

async function initialize() {
  try {
    await api('health');
    const { data } = await api('catalog');
    for (const item of data.sensor_catalog) sensors.set(item.sensor_id, item);
    options(split, 'Select split', data.available_splits.map(name => [name, name === 'train' ? 'Train' : 'Test']));
    options(sensor, 'Select sensor', data.sensor_catalog.map(item =>
      [item.sensor_id, 'Sensor ' + item.sensor_id + ' · ' + item.unit_of_measure_if_known]));
    $('service').textContent = 'Verified · Read-only';
    state('initial', 'Select a dataset split to begin.');
  } catch (error) {
    $('service').textContent = 'Service unavailable';
    failure(error);
  }
}

initialize();
