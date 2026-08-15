/**
 * Risk level badge component.
 * Displays LOW / MEDIUM / HIGH with appropriate colors.
 */
export default function RiskBadge({ level, score, size = 'md' }) {
  const label = (level || 'unknown').toUpperCase();
  const sizeClass = size === 'sm' ? 'text-[10px] px-2 py-0.5' : size === 'lg' ? 'text-sm px-4 py-1.5' : 'text-xs px-3 py-1';

  const classMap = {
    LOW: 'risk-badge risk-badge--low',
    MEDIUM: 'risk-badge risk-badge--medium',
    HIGH: 'risk-badge risk-badge--high',
  };

  return (
    <span className={`${classMap[label] || 'risk-badge'} ${sizeClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${
        label === 'HIGH' ? 'bg-red-400 pulse-dot' :
        label === 'MEDIUM' ? 'bg-amber-400' : 'bg-emerald-400'
      }`} />
      {label}
      {score !== undefined && <span className="ml-1 opacity-75">{Math.round(score)}</span>}
    </span>
  );
}
