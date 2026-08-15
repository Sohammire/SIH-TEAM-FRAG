import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Bell, AlertTriangle, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import DataSourceBadge from '../components/common/DataSourceBadge';
import { mockAlerts } from '../data/mockAlerts';
import { formatTimestamp, formatRelativeTime } from '../utils/formatters';

const severityIcons = {
  critical: { icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/10' },
  high: { icon: AlertCircle, color: 'text-orange-400', bg: 'bg-orange-500/10' },
  medium: { icon: Info, color: 'text-amber-400', bg: 'bg-amber-500/10' },
  low: { icon: Info, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
};

export default function AlertPage() {
  const [statusFilter, setStatusFilter] = useState('all');

  const counts = useMemo(() => ({
    critical: mockAlerts.filter(a => a.severity === 'critical' && a.status === 'active').length,
    high: mockAlerts.filter(a => a.severity === 'high' && a.status === 'active').length,
    medium: mockAlerts.filter(a => a.severity === 'medium' && a.status === 'active').length,
    resolved: mockAlerts.filter(a => a.status === 'resolved').length,
  }), []);

  const filtered = useMemo(() => {
    if (statusFilter === 'all') return mockAlerts;
    if (statusFilter === 'resolved') return mockAlerts.filter(a => a.status === 'resolved');
    return mockAlerts.filter(a => a.severity === statusFilter && a.status === 'active');
  }, [statusFilter]);

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { key: 'critical', label: 'Critical', count: counts.critical, color: 'red' },
          { key: 'high', label: 'High', count: counts.high, color: 'orange' },
          { key: 'medium', label: 'Medium', count: counts.medium, color: 'amber' },
          { key: 'resolved', label: 'Resolved', count: counts.resolved, color: 'emerald' },
        ].map(c => (
          <motion.button
            key={c.key}
            onClick={() => setStatusFilter(statusFilter === c.key ? 'all' : c.key)}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`card text-left transition-all ${statusFilter === c.key ? 'ring-2 ring-blue-500/50' : ''}`}
          >
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">{c.label}</p>
            <p className={`text-3xl font-bold mt-1 text-${c.color}-400`}>{c.count}</p>
          </motion.button>
        ))}
      </div>

      {/* Alert list */}
      <div className="space-y-3">
        {filtered.map((alert, i) => {
          const sev = severityIcons[alert.severity] || severityIcons.medium;
          const Icon = sev.icon;

          return (
            <motion.div
              key={alert.alert_id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
              className={`card flex gap-4 alert-severity--${alert.severity} ${
                alert.status === 'resolved' ? 'opacity-60' : ''
              }`}
            >
              <div className={`w-10 h-10 rounded-lg ${sev.bg} flex items-center justify-center flex-shrink-0`}>
                {alert.status === 'resolved'
                  ? <CheckCircle2 size={20} className="text-emerald-400" />
                  : <Icon size={20} className={sev.color} />}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs font-bold ${sev.color}`}>
                    {alert.type.replace(/_/g, ' ')}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded capitalize ${
                    alert.status === 'resolved'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-red-500/10 text-red-400 border border-red-500/20'
                  }`}>
                    {alert.status}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded capitalize
                    ${alert.severity === 'critical' ? 'bg-red-500/10 text-red-400' :
                      alert.severity === 'high' ? 'bg-orange-500/10 text-orange-400' :
                      'bg-amber-500/10 text-amber-400'}`}>
                    {alert.severity}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">{alert.message}</p>

                <div className="flex items-center gap-3 mt-2">
                  <Link to={`/fleet/${alert.truck_id}`} className="text-[10px] text-blue-400 hover:text-blue-300 transition-colors">
                    {alert.truck_id}
                  </Link>
                  {alert.tyre_id && (
                    <Link to={`/tyres/${alert.tyre_id}`} className="text-[10px] text-blue-400 hover:text-blue-300 transition-colors">
                      {alert.tyre_id}
                    </Link>
                  )}
                  <DataSourceBadge source={alert.source} />
                </div>
              </div>

              <div className="text-right flex-shrink-0">
                <p className="text-[10px] text-slate-500">{formatRelativeTime(alert.timestamp)}</p>
                <p className="text-[10px] text-slate-600 mt-0.5">{formatTimestamp(alert.timestamp)}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
