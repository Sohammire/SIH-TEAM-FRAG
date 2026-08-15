import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine, Area, AreaChart
} from 'recharts';
import { CHART_COLORS } from '../../utils/constants';

/**
 * Reusable trend chart for telemetry data.
 * Supports single or dual lines, reference lines, and area fill.
 */
export default function TrendChart({
  data,
  dataKey = 'value',
  secondaryKey,
  referenceValue,
  referenceLabel,
  color = CHART_COLORS.primary,
  secondaryColor = CHART_COLORS.muted,
  height = 200,
  title,
  unit = '',
  showArea = false,
  showDots = false,
}) {
  if (!data || data.length === 0) return null;

  const formatXAxis = (ts) => {
    if (!ts) return '';
    const d = new Date(ts);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="rounded-lg px-3 py-2 text-xs shadow-xl border border-[var(--color-surface-600)]"
        style={{ background: 'var(--color-surface-700)' }}>
        <p className="text-slate-400 mb-1">{formatXAxis(label)}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.stroke || p.color }} className="font-medium">
            {p.name}: {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}{unit}
          </p>
        ))}
      </div>
    );
  };

  const ChartComponent = showArea ? AreaChart : LineChart;

  return (
    <div>
      {title && <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">{title}</p>}
      <ResponsiveContainer width="100%" height={height}>
        <ChartComponent data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="timestamp" tickFormatter={formatXAxis} tick={{ fontSize: 10 }} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 10 }} width={45} />
          <Tooltip content={<CustomTooltip />} />

          {referenceValue !== undefined && (
            <ReferenceLine
              y={referenceValue}
              stroke="#ef4444"
              strokeDasharray="5 3"
              label={{ value: referenceLabel || '', position: 'right', fill: '#ef4444', fontSize: 10 }}
            />
          )}

          {showArea ? (
            <Area
              type="monotone"
              dataKey={dataKey}
              name={dataKey}
              stroke={color}
              fill={color}
              fillOpacity={0.1}
              strokeWidth={2}
              dot={showDots}
            />
          ) : (
            <Line
              type="monotone"
              dataKey={dataKey}
              name={dataKey}
              stroke={color}
              strokeWidth={2}
              dot={showDots}
              activeDot={{ r: 4, strokeWidth: 0 }}
            />
          )}

          {secondaryKey && (
            <Line
              type="monotone"
              dataKey={secondaryKey}
              name={secondaryKey}
              stroke={secondaryColor}
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={false}
            />
          )}
        </ChartComponent>
      </ResponsiveContainer>
    </div>
  );
}
