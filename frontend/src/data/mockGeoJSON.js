/**
 * Mock GeoJSON mine-road network for the hotspot map.
 * Source: SIMULATED DATA — configurable mine/route layer.
 *
 * This is NOT hardcoded Chandrapur/Umred operational data.
 * Replace with actual mine-road coordinates when available.
 *
 * Center: approximately 20.123°N, 79.048°E (demo coordinates)
 */

// Road segments as LineString features
export const mockMineRoads = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { segment_id: 'RS_01', name: 'Main Haul Road - Section A', road_type: 'haul' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.040, 20.118], [79.042, 20.120], [79.045, 20.122],
          [79.048, 20.123], [79.052, 20.124],
        ],
      },
    },
    {
      type: 'Feature',
      properties: { segment_id: 'RS_02', name: 'Pit Ramp - North', road_type: 'ramp' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.048, 20.123], [79.049, 20.126], [79.050, 20.129],
          [79.051, 20.131],
        ],
      },
    },
    {
      type: 'Feature',
      properties: { segment_id: 'RS_03', name: 'Waste Dump Access', road_type: 'access' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.052, 20.124], [79.055, 20.125], [79.058, 20.126],
          [79.060, 20.127],
        ],
      },
    },
    {
      type: 'Feature',
      properties: { segment_id: 'RS_04', name: 'Loading Area Connector', road_type: 'connector' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.045, 20.122], [79.044, 20.119], [79.043, 20.116],
        ],
      },
    },
    {
      type: 'Feature',
      properties: { segment_id: 'RS_05', name: 'South Bench Road', road_type: 'bench' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.043, 20.116], [79.046, 20.115], [79.049, 20.114],
          [79.052, 20.115],
        ],
      },
    },
    {
      type: 'Feature',
      properties: { segment_id: 'RS_06', name: 'Crusher Circuit Road', road_type: 'haul' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.052, 20.115], [79.054, 20.117], [79.056, 20.120],
          [79.057, 20.122],
        ],
      },
    },
    {
      type: 'Feature',
      properties: { segment_id: 'RS_07', name: 'Pit Ramp - South', road_type: 'ramp' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.043, 20.116], [79.041, 20.114], [79.040, 20.111],
          [79.039, 20.109],
        ],
      },
    },
    {
      type: 'Feature',
      properties: { segment_id: 'RS_08', name: 'Maintenance Yard Access', road_type: 'service' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [79.057, 20.122], [79.059, 20.123], [79.061, 20.124],
        ],
      },
    },
  ],
};

// Mine boundary polygon
export const mockMineBoundary = {
  type: 'Feature',
  properties: { mine_id: 'MINE_ALPHA', name: 'Demo Mine Alpha' },
  geometry: {
    type: 'Polygon',
    coordinates: [[
      [79.035, 20.107], [79.065, 20.107], [79.065, 20.135],
      [79.035, 20.135], [79.035, 20.107],
    ]],
  },
};

// Impact event locations for map markers
export const mockImpactLocations = [
  { lat: 20.1200, lon: 79.0440, peak_g: 2.8, segment_id: 'RS_01', severity: 'medium' },
  { lat: 20.1225, lon: 79.0460, peak_g: 3.5, segment_id: 'RS_01', severity: 'high' },
  { lat: 20.1260, lon: 79.0495, peak_g: 4.1, segment_id: 'RS_02', severity: 'high' },
  { lat: 20.1280, lon: 79.0500, peak_g: 2.2, segment_id: 'RS_02', severity: 'medium' },
  { lat: 20.1250, lon: 79.0550, peak_g: 3.2, segment_id: 'RS_03', severity: 'high' },
  { lat: 20.1190, lon: 79.0435, peak_g: 5.0, segment_id: 'RS_04', severity: 'high' },
  { lat: 20.1160, lon: 79.0440, peak_g: 3.8, segment_id: 'RS_04', severity: 'high' },
  { lat: 20.1155, lon: 79.0465, peak_g: 2.0, segment_id: 'RS_05', severity: 'low' },
  { lat: 20.1170, lon: 79.0545, peak_g: 3.0, segment_id: 'RS_06', severity: 'medium' },
  { lat: 20.1120, lon: 79.0415, peak_g: 4.5, segment_id: 'RS_07', severity: 'high' },
  { lat: 20.1100, lon: 79.0400, peak_g: 3.9, segment_id: 'RS_07', severity: 'high' },
];

// Map center (configurable)
export const MAP_CENTER = [20.121, 79.048];
export const MAP_ZOOM = 14;

export default mockMineRoads;
