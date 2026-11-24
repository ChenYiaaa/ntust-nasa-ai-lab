export class ApiError extends Error {
  constructor(code, message, context) {
    super(message);
    this.code = code;
    this.context = context;
  }
}

export async function api(path, params, signal) {
  const response = await fetch('/api/' + path + (params ? '?' + new URLSearchParams(params) : ''), { signal });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(body?.error?.error_code ?? 'HTTP_' + response.status,
      body?.error?.message ?? 'Unexpected server failure.', body?.error?.input_context);
  }
  if (body?.status !== 'ok' || !body.data || !body.provenance) {
    throw new ApiError('INVALID_RESPONSE', 'Unexpected API response.');
  }
  return body;
}

export function latestRequest() {
  let current;
  return {
    cancel() { current?.abort(); current = undefined; },
    begin() {
      current?.abort();
      const request = new AbortController();
      current = request;
      return { signal: request.signal, active: () => current === request };
    },
  };
}

export function chartPoints(points) {
  if (!points.every((point, i) => Number.isSafeInteger(point.cycle) &&
      Number.isFinite(point.value) && (!i || points[i - 1].cycle < point.cycle))) {
    throw new ApiError('INVALID_RESPONSE', 'History contains invalid or unordered points.');
  }
  return points.map(({ cycle, value }) => [cycle, value]);
}

export function statistics(pairs, start, end) {
  const count = pairs.length;
  const missing = end - start + 1 - count;
  if (!count) return { count, min: null, max: null, mean: null, deviation: null, slope: null, missing };
  const mean = pairs.reduce((sum, [, y]) => sum + y, 0) / count;
  const center = pairs.reduce((sum, [x]) => sum + x, 0) / count;
  let min = Infinity, max = -Infinity, variance = 0, covariance = 0, cycleVariance = 0;
  for (const [x, y] of pairs) {
    min = Math.min(min, y);
    max = Math.max(max, y);
    variance += (y - mean) ** 2;
    covariance += (x - center) * (y - mean);
    cycleVariance += (x - center) ** 2;
  }
  return { count, min, max, mean, deviation: count > 1 ? Math.sqrt(variance / (count - 1)) : null,
    slope: cycleVariance ? covariance / cycleVariance : null, missing };
}

export const format = value => value == null ? 'N/A' : String(value);
