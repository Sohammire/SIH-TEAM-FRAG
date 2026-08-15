import { motion } from 'framer-motion';
import {
  ShieldCheck, AlertTriangle, Wifi, WifiOff, Database,
  Clock, Camera, Radio, CheckCircle2, XCircle
} from 'lucide-react';
import DataSourceBadge from '../components/common/DataSourceBadge';
import { mockTrucks } from '../data/mockTrucks';
import { mockTyres } from '../data/mockTyres';

// Mock data quality metrics
const dataQuality = {
  overall_score: 87,
  total_sensors: 48,
  active_sensors: 45,
  stale_sensors: 2,
  dropout_sensors: 1,
  avg_confidence: 0.92,
  missing_values_pct: 3.2,
  simulated_pct: 100,
  real_pct: 0,
  last_updated: new Date().toISOString(),
};

const sensorHealth = [
  { truck_id: 'DUMPER_01', sensors: 6, active: 6, stale: 0, dropout: 0, status: 'healthy' },
  { truck_id: 'DUMPER_02', sensors: 6, active: 6, stale: 0, dropout: 0, status: 'healthy' },
  { truck_id: 'DUMPER_03', sensors: 6, active: 6, stale: 0, dropout: 0, status: 'healthy' },
  { truck_id: 'DUMPER_04', sensors: 6, active: 5, stale: 1, dropout: 0, status: 'warning' },
  { truck_id: 'DUMPER_05', sensors: 6, active: 6, stale: 0, dropout: 0, status: 'healthy' },
  { truck_id: 'DUMPER_06', sensors: 6, active: 6, stale: 0, dropout: 0, status: 'healthy' },
  { truck_id: 'DUMPER_07', sensors: 6, active: 5, stale: 1, dropout: 0, status: 'warning' },
  { truck_id: 'DUMPER_08', sensors: 6, active: 5, stale: 0, dropout: 1, status: 'critical' },
];

const qualityChecks = [
  { name: 'Timestamp Sync', status: 'pass', detail: 'All readings within ±2s of server time' },
  { name: 'Pressure Range', status: 'pass', detail: 'All values within 400–900 kPa expected range' },
  { name: 'Temperature Range', status: 'pass', detail: 'All values within 20–120°C expected range' },
  { name: 'GPS Validity', status: 'pass', detail: 'All coordinates within mine boundary' },
  { name: 'IMU Calibration', status: 'warning', detail: 'DUMPER_01 IMU shows constant zero — needs calibration' },
  { name: 'Sensor Freshness', status: 'warning', detail: '2 sensors have not reported in >10 minutes' },
  { name: 'Image Quality', status: 'pass', detail: 'No blurred or dark images in recent batch' },
  { name: 'ID Consistency', status: 'pass', detail: 'All tyre_id → truck_id → fitment mappings valid' },
];

export default function DataQualityPage() {
  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="card md:col-span-1">
          <h3 className="text-sm font-semibold text-white mb-4">Overall Data Quality</h3>
          <div className="flex items-center justify-center">
            <div className="relative w-36 h-36">
              <svg className="w-36 h-36 -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="52" fill="none" stroke="#1e293b" strokeWidth="8" />
                <circle cx="60" cy="60" r="52" fill="none"
                  stroke={dataQuality.overall_score >= 80 ? '#10b981' : dataQuality.overall_score >= 50 ? '#f59e0b' : '#ef4444'}
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${(dataQuality.overall_score / 100) * 327} 327`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-3xl font-bold text-white">{dataQuality.overall_score}</p>
                  <p className="text-[10px] text-slate-500">/ 100</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="card md:col-span-2">
          <h3 className="text-sm font-semibold text-white mb-4">Data Source Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg bg-[var(--color-surface-700)]">
              <p className="text-[10px] text-slate-500 uppercase">Active Sensors</p>
              <p className="text-xl font-bold text-emerald-400">{dataQuality.active_sensors}/{dataQuality.total_sensors}</p>
            </div>
            <div className="p-3 rounded-lg bg-[var(--color-surface-700)]">
              <p className="text-[10px] text-slate-500 uppercase">Stale</p>
              <p className="text-xl font-bold text-amber-400">{dataQuality.stale_sensors}</p>
            </div>
            <div className="p-3 rounded-lg bg-[var(--color-surface-700)]">
              <p className="text-[10px] text-slate-500 uppercase">Dropout</p>
              <p className="text-xl font-bold text-red-400">{dataQuality.dropout_sensors}</p>
            </div>
            <div className="p-3 rounded-lg bg-[var(--color-surface-700)]">
              <p className="text-[10px] text-slate-500 uppercase">Avg Confidence</p>
              <p className="text-xl font-bold text-white">{(dataQuality.avg_confidence * 100).toFixed(0)}%</p>
            </div>
          </div>

          {/* Simulated vs Real */}
          <div className="mt-4 p-4 rounded-lg bg-violet-500/10 border border-violet-500/20">
            <div className="flex items-center gap-2 mb-2">
              <Database size={14} className="text-violet-400" />
              <p className="text-xs font-semibold text-violet-400">Data Source Distribution</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-4 rounded-full bg-[var(--color-surface-600)] overflow-hidden">
                <div className="h-full bg-violet-500 rounded-full" style={{ width: `${dataQuality.simulated_pct}%` }} />
              </div>
              <span className="text-xs text-slate-400 whitespace-nowrap">
                {dataQuality.simulated_pct}% Simulated
              </span>
            </div>
            <p className="text-[10px] text-slate-500 mt-2">
              All current data is from the telemetry simulator. Dashboard clearly distinguishes simulated from real data.
            </p>
          </div>
        </motion.div>
      </div>

      {/* Quality Checks */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
        className="card">
        <h3 className="text-sm font-semibold text-white mb-4">Quality Checks</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {qualityChecks.map(check => (
            <div key={check.name}
              className={`flex items-start gap-3 p-3 rounded-lg bg-[var(--color-surface-700)] ${
                check.status === 'warning' ? 'border border-amber-500/20' :
                check.status === 'fail' ? 'border border-red-500/20' : 'border border-transparent'
              }`}>
              {check.status === 'pass' ? (
                <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0 mt-0.5" />
              ) : check.status === 'warning' ? (
                <AlertTriangle size={16} className="text-amber-400 flex-shrink-0 mt-0.5" />
              ) : (
                <XCircle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <p className="text-xs font-semibold text-white">{check.name}</p>
                <p className="text-[10px] text-slate-400 mt-0.5">{check.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Per-truck sensor health */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        className="card p-0 overflow-hidden">
        <div className="p-4 border-b border-[var(--color-surface-600)]">
          <h3 className="text-sm font-semibold text-white">Sensor Health by Truck</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-surface-600)]">
                {['Truck', 'Sensors', 'Active', 'Stale', 'Dropout', 'Status'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sensorHealth.map(row => (
                <tr key={row.truck_id} className="border-b border-[var(--color-surface-600)] hover:bg-[var(--color-surface-700)] transition-colors">
                  <td className="px-4 py-2.5 text-xs font-semibold text-white">{row.truck_id}</td>
                  <td className="px-4 py-2.5 text-xs text-slate-300">{row.sensors}</td>
                  <td className="px-4 py-2.5 text-xs text-emerald-400">{row.active}</td>
                  <td className="px-4 py-2.5 text-xs text-amber-400">{row.stale}</td>
                  <td className="px-4 py-2.5 text-xs text-red-400">{row.dropout}</td>
                  <td className="px-4 py-2.5">
                    <span className={`flex items-center gap-1.5 text-[10px] font-semibold uppercase
                      ${row.status === 'healthy' ? 'text-emerald-400' :
                        row.status === 'warning' ? 'text-amber-400' : 'text-red-400'
                      }`}>
                      {row.status === 'healthy' ? <Wifi size={12} /> :
                       row.status === 'critical' ? <WifiOff size={12} /> : <AlertTriangle size={12} />}
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
