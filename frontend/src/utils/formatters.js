/**
 * Formatters and utility functions for the Mining Tyre Intelligence dashboard.
 */

/**
 * Format a number with fixed decimal places
 */
export function formatNumber(value, decimals = 1) {
  if (value == null || isNaN(value)) return '—';
  return Number(value).toFixed(decimals);
}

/**
 * Format temperature with °C suffix
 */
export function formatTemp(value) {
  if (value == null) return '—';
  return `${formatNumber(value)}°C`;
}

/**
 * Format pressure with kPa suffix
 */
export function formatPressure(value) {
  if (value == null) return '—';
  return `${formatNumber(value, 0)} kPa`;
}

/**
 * Format speed with km/h suffix
 */
export function formatSpeed(value) {
  if (value == null) return '—';
  return `${formatNumber(value, 0)} km/h`;
}

/**
 * Format payload with tonnes suffix
 */
export function formatPayload(value) {
  if (value == null) return '—';
  return `${formatNumber(value, 0)} t`;
}

/**
 * Format TKPH value
 */
export function formatTKPH(value) {
  if (value == null) return '—';
  return formatNumber(value, 0);
}

/**
 * Format percentage
 */
export function formatPercent(value) {
  if (value == null) return '—';
  return `${formatNumber(value, 1)}%`;
}

/**
 * Format a timestamp to a readable string
 */
export function formatTimestamp(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

/**
 * Format relative time (e.g. "2 min ago")
 */
export function formatRelativeTime(ts) {
  if (!ts) return '—';
  const now = Date.now();
  const diff = now - new Date(ts).getTime();
  const seconds = Math.floor(diff / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

/**
 * Format risk score to display string
 */
export function formatRiskScore(score) {
  if (score == null) return '—';
  return `${Math.round(score)}/100`;
}

/**
 * Get risk label color class
 */
export function getRiskColorClass(label) {
  switch (label?.toUpperCase()) {
    case 'HIGH': return 'text-red-400';
    case 'MEDIUM': return 'text-amber-400';
    case 'LOW': return 'text-emerald-400';
    default: return 'text-slate-400';
  }
}

/**
 * Get risk background class
 */
export function getRiskBgClass(label) {
  switch (label?.toUpperCase()) {
    case 'HIGH': return 'bg-red-900/40 border-red-800';
    case 'MEDIUM': return 'bg-amber-900/40 border-amber-800';
    case 'LOW': return 'bg-emerald-900/40 border-emerald-800';
    default: return 'bg-slate-800 border-slate-700';
  }
}

/**
 * Capitalize first letter
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}

/**
 * Format wheel position for display
 */
export function formatPosition(pos) {
  if (!pos) return '—';
  return pos
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

/**
 * Clamp a value between min and max
 */
export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}
