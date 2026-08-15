import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Search, Filter, Thermometer, Gauge, Activity } from 'lucide-react';
import RiskBadge from '../components/common/RiskBadge';
import DataSourceBadge from '../components/common/DataSourceBadge';
import { mockTyres } from '../data/mockTyres';
import { formatTemp, formatPressure, formatTKPH, formatPosition } from '../utils/formatters';

export default function TyreMonitorPage() {
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [sortBy, setSortBy] = useState('risk_score');
  const [sortDir, setSortDir] = useState('desc');

  const filtered = useMemo(() => {
    let list = [...mockTyres];

    if (search) {
      const q = search.toLowerCase();
      list = list.filter(t =>
        t.tyre_id.toLowerCase().includes(q) ||
        t.truck_id.toLowerCase().includes(q) ||
        t.position.toLowerCase().includes(q)
      );
    }

    if (riskFilter !== 'all') {
      list = list.filter(t => t.risk_label === riskFilter);
    }

    list.sort((a, b) => {
      const aVal = a[sortBy] ?? 0;
      const bVal = b[sortBy] ?? 0;
      return sortDir === 'desc' ? bVal - aVal : aVal - bVal;
    });

    return list;
  }, [search, riskFilter, sortBy, sortDir]);

  const toggleSort = (col) => {
    if (sortBy === col) {
      setSortDir(d => d === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(col);
      setSortDir('desc');
    }
  };

  const SortHeader = ({ col, label }) => (
    <th
      onClick={() => toggleSort(col)}
      className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400 cursor-pointer hover:text-white transition-colors select-none"
    >
      {label} {sortBy === col && (sortDir === 'desc' ? '↓' : '↑')}
    </th>
  );

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search tyre, truck, position..."
            className="w-full pl-9 pr-3 py-2 rounded-lg text-sm bg-[var(--color-surface-700)] border border-[var(--color-surface-600)] text-slate-300 placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter size={14} className="text-slate-500" />
          {['all', 'HIGH', 'MEDIUM', 'LOW'].map(f => (
            <button
              key={f}
              onClick={() => setRiskFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                ${riskFilter === f
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-white bg-[var(--color-surface-700)] border border-transparent'
                }`}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>

        <span className="text-xs text-slate-500">{filtered.length} tyres</span>
      </div>

      {/* Table */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-surface-600)]">
                <th className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Tyre ID</th>
                <th className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Truck</th>
                <th className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Position</th>
                <th className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Manufacturer</th>
                <SortHeader col="current_pressure_kpa" label="Pressure" />
                <SortHeader col="current_temp_c" label="Temp" />
                <SortHeader col="tkph_current" label="TKPH" />
                <SortHeader col="wear_rate_mm_per_h" label="Wear Rate" />
                <SortHeader col="risk_score" label="Risk" />
                <th className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Source</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((tyre, i) => (
                <motion.tr
                  key={tyre.tyre_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.02 }}
                  className="border-b border-[var(--color-surface-600)] hover:bg-[var(--color-surface-700)] transition-colors"
                >
                  <td className="px-3 py-2.5">
                    <Link to={`/tyres/${tyre.tyre_id}`} className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors">
                      {tyre.tyre_id}
                    </Link>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">
                    <Link to={`/fleet/${tyre.truck_id}`} className="hover:text-white transition-colors">{tyre.truck_id}</Link>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">{formatPosition(tyre.position)}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">{tyre.manufacturer}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{formatPressure(tyre.current_pressure_kpa)}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{formatTemp(tyre.current_temp_c)}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{formatTKPH(tyre.tkph_current)}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{tyre.wear_rate_mm_per_h?.toFixed(4) || '—'}</td>
                  <td className="px-3 py-2.5">
                    <RiskBadge level={tyre.risk_label} score={tyre.risk_score} size="sm" />
                  </td>
                  <td className="px-3 py-2.5">
                    <DataSourceBadge source={tyre.source} />
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
