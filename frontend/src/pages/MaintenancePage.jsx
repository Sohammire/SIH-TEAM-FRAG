import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Wrench } from 'lucide-react';
import RiskBadge from '../components/common/RiskBadge';
import DataSourceBadge from '../components/common/DataSourceBadge';
import { mockMaintenance } from '../data/mockMaintenance';
import { formatPressure, formatTemp, formatTKPH } from '../utils/formatters';

export default function MaintenancePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-500">
            Priority ranking: severe damage + pressure loss outranks TKPH-only warning.
            priority_score = risk_score × criticality × data_confidence
          </p>
        </div>
        <DataSourceBadge source="simulator" />
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-surface-600)]">
                {['#', 'Tyre ID', 'Truck', 'Risk', 'Score', 'Main Reason', 'Damage',
                  'Pressure', 'Temp', 'TKPH', 'Confidence', 'Recommended Action'].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400 whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mockMaintenance.map((item, i) => (
                <motion.tr
                  key={item.tyre_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`border-b border-[var(--color-surface-600)] hover:bg-[var(--color-surface-700)] transition-colors
                    ${item.risk_label === 'HIGH' ? 'bg-red-500/[0.03]' : ''}`}
                >
                  <td className="px-3 py-3">
                    <span className={`w-7 h-7 inline-flex items-center justify-center rounded-full text-xs font-bold
                      ${item.priority <= 2 ? 'bg-red-500/20 text-red-400' :
                        item.priority <= 4 ? 'bg-amber-500/20 text-amber-400' :
                        'bg-slate-500/20 text-slate-400'}`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-3 py-3">
                    <Link to={`/tyres/${item.tyre_id}`} className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors">
                      {item.tyre_id}
                    </Link>
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-400">
                    <Link to={`/fleet/${item.truck_id}`} className="hover:text-white transition-colors">{item.truck_id}</Link>
                  </td>
                  <td className="px-3 py-3">
                    <RiskBadge level={item.risk_label} size="sm" />
                  </td>
                  <td className="px-3 py-3 text-xs font-bold text-white">{item.risk_score}</td>
                  <td className="px-3 py-3 text-xs text-slate-300 max-w-48 truncate">{item.main_reason}</td>
                  <td className="px-3 py-3 text-xs text-slate-400">{item.damage}</td>
                  <td className="px-3 py-3 text-xs text-slate-300">{formatPressure(item.pressure_kpa)}</td>
                  <td className="px-3 py-3 text-xs text-slate-300">{formatTemp(item.temperature_c)}</td>
                  <td className="px-3 py-3 text-xs text-slate-300">
                    {formatTKPH(item.tkph_current)}
                    <span className="text-slate-500">/{item.tkph_rated}</span>
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-300">{(item.data_confidence * 100).toFixed(0)}%</td>
                  <td className="px-3 py-3">
                    <span className={`text-[10px] font-semibold px-2 py-1 rounded ${
                      item.risk_label === 'HIGH' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                      item.risk_label === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                    }`}>
                      {item.recommended_action}
                    </span>
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
