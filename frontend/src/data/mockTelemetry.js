/**
 * Mock telemetry time-series for charts.
 * Generates 60 data points (last 60 minutes) for each metric.
 * Source: SIMULATED DATA
 */

function generateTimeSeries(baseTime, count, generator) {
  const points = [];
  for (let i = 0; i < count; i++) {
    const ts = new Date(baseTime - (count - i) * 60000).toISOString();
    points.push({ timestamp: ts, ...generator(i, count) });
  }
  return points;
}

// Pressure trend — slight downward for demo leak scenario
export const mockPressureTrend = generateTimeSeries(Date.now(), 60, (i) => ({
  value: 720 - i * 0.8 + Math.sin(i / 5) * 5,
  predicted: 720 - i * 0.3,
  label: 'Pressure (kPa)',
}));

// Temperature trend — rising under load
export const mockTemperatureTrend = generateTimeSeries(Date.now(), 60, (i) => ({
  value: 55 + i * 0.5 + Math.sin(i / 8) * 3,
  predicted: 55 + i * 0.45,
  label: 'Temperature (°C)',
}));

// TKPH trend
export const mockTKPHTrend = generateTimeSeries(Date.now(), 60, (i) => ({
  value: 1400 + Math.sin(i / 10) * 200 + (i > 40 ? 300 : 0),
  rated: 1800,
  label: 'TKPH',
}));

// Speed trend
export const mockSpeedTrend = generateTimeSeries(Date.now(), 60, (i) => ({
  value: Math.max(0, 25 + Math.sin(i / 6) * 15 + (Math.random() - 0.5) * 5),
  label: 'Speed (km/h)',
}));

// Payload trend
export const mockPayloadTrend = generateTimeSeries(Date.now(), 60, (i) => ({
  value: i < 15 ? 0 : i < 45 ? 280 + (Math.random() - 0.5) * 20 : 0,
  label: 'Payload (t)',
}));

// Dashboard summary trends (last 24 hours, hourly)
export const mockDashboardTrends = {
  temperature: generateTimeSeries(Date.now(), 24, (i) => ({
    value: 60 + Math.sin(i / 4) * 15 + (i > 16 ? 10 : 0),
    avg: 65,
  })),
  pressure: generateTimeSeries(Date.now(), 24, (i) => ({
    value: 710 + Math.sin(i / 3) * 20,
    avg: 715,
  })),
  tkph: generateTimeSeries(Date.now(), 24, (i) => ({
    value: 1500 + Math.sin(i / 5) * 300,
    rated: 1800,
  })),
};

// Wear projection data
export const mockWearProjection = generateTimeSeries(
  Date.now(),
  90, // 90 days
  (i) => ({
    actual: i < 60 ? 85 - i * 0.15 : null,
    projected: 85 - i * 0.15,
    lower_bound: 85 - i * 0.18,
    upper_bound: 85 - i * 0.12,
    min_safe: 20,
  })
);

export default {
  mockPressureTrend,
  mockTemperatureTrend,
  mockTKPHTrend,
  mockSpeedTrend,
  mockPayloadTrend,
  mockDashboardTrends,
  mockWearProjection,
};
