import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

const COLORS = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#ef4444',
};

/**
 * Risk distribution donut chart.
 */
export default function RiskDistributionChart({ data, height = 220 }) {
  // data should be [{ name: 'LOW', value: N }, ...]
  const total = data.reduce((s, d) => s + d.value, 0);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const { name, value } = payload[0];
    return (
      <div className="rounded-lg px-3 py-2 text-xs shadow-xl border border-[var(--color-surface-600)]"
        style={{ background: 'var(--color-surface-700)' }}>
        <p className="font-medium" style={{ color: COLORS[name] }}>{name}: {value} tyres</p>
        <p className="text-slate-400">{((value / total) * 100).toFixed(0)}%</p>
      </div>
    );
  };

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
            strokeWidth={0}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || '#64748b'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      {/* Center label */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{total}</p>
          <p className="text-xs text-slate-400">Total Tyres</p>
        </div>
      </div>
    </div>
  );
}
