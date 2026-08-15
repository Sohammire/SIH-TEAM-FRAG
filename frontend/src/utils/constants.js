// ─── Risk Level Constants ───────────────────────────────────────
export const RISK_LEVELS = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
};

export const RISK_COLORS = {
  LOW: { bg: '#064e3b', text: '#34d399', border: '#065f46', accent: '#10b981' },
  MEDIUM: { bg: '#78350f', text: '#fbbf24', border: '#92400e', accent: '#f59e0b' },
  HIGH: { bg: '#7f1d1d', text: '#f87171', border: '#991b1b', accent: '#ef4444' },
};

// ─── Tyre Positions ─────────────────────────────────────────────
export const TYRE_POSITIONS = [
  'front_left',
  'front_right',
  'rear_left_inner',
  'rear_left_outer',
  'rear_right_inner',
  'rear_right_outer',
];

// ─── Damage Types ───────────────────────────────────────────────
export const DAMAGE_TYPES = [
  'cut', 'crack', 'puncture', 'embedded_object',
  'tear', 'abrasion', 'unknown',
];

export const DAMAGE_LOCATIONS = [
  'tread', 'shoulder', 'sidewall', 'bead', 'unknown',
];

export const SEVERITY_LEVELS = ['minor', 'moderate', 'severe'];

// ─── TKPH Thresholds ────────────────────────────────────────────
export const TKPH_THRESHOLDS = {
  NORMAL: 0.80,
  MONITOR: 1.00,
  WARNING: 1.15,
};

// ─── Data Source Labels ─────────────────────────────────────────
export const DATA_SOURCES = {
  SIMULATOR: 'simulator',
  SENSOR: 'sensor',
  MANUAL: 'manual_inspection',
  INFERRED: 'inferred',
  OPERATOR: 'operator_confirmed',
};

// ─── Alert Severity ─────────────────────────────────────────────
export const ALERT_TYPES = {
  PRESSURE_LOSS: 'PRESSURE_LOSS',
  HIGH_TEMPERATURE: 'HIGH_TEMPERATURE',
  TKPH_EXCEEDED: 'TKPH_EXCEEDED',
  SEVERE_DAMAGE: 'SEVERE_TYRE_DAMAGE',
  HIGH_IMPACT: 'HIGH_IMPACT',
  SENSOR_FAILURE: 'SENSOR_FAILURE',
  DATA_QUALITY: 'DATA_QUALITY_WARNING',
};

// ─── API Config ─────────────────────────────────────────────────
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
export const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK === 'true';

// ─── Chart Colors ───────────────────────────────────────────────
export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
  muted: '#64748b',
  pressure: '#3b82f6',
  temperature: '#ef4444',
  tkph: '#f59e0b',
  speed: '#8b5cf6',
  payload: '#06b6d4',
  wear: '#10b981',
};

// ─── Truck Status ───────────────────────────────────────────────
export const TRUCK_STATUS = {
  ACTIVE: 'active',
  IDLE: 'idle',
  MAINTENANCE: 'maintenance',
  OFFLINE: 'offline',
};
