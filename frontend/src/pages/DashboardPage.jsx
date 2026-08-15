import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Truck, CircleDot, AlertTriangle, Wrench, Thermometer,
  Gauge, Activity, MapPin, ShieldAlert, ShieldCheck, Shield, RefreshCw
} from 'lucide-react';
import StatCard from '../components/common/StatCard';
import RiskBadge from '../components/common/RiskBadge';
import DataSourceBadge from '../components/common/DataSourceBadge';
import RiskDistributionChart from '../components/charts/RiskDistributionChart';
import TrendChart from '../components/charts/TrendChart';
import { fetchDashboardSummary, fetchAlerts, fetchMaintenancePriorities } from '../api';
import { mockDashboardTrends } from '../data/mockTelemetry';
import { formatRelativeTime, formatTemp, formatPressure } from '../utils/formatters';
import { CHART_COLORS } from '../utils/constants';
import { Link } from 'react-router-dom';

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(false);

  const loadDashboardData = async () => {
    setLoading(true);
    const sumRes = await fetchDashboardSummary();
    const alertRes = await fetchAlerts();
    const maintRes = await fetchMaintenancePriorities();

    setSummary(sumRes.data);
    setAlerts(alertRes.data || []);
    setMaintenance(maintRes.data || []);
    setIsLive(sumRes.isLive);
    setLoading(false);
  };

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3 text-slate-400">
          <RefreshCw size={24} className="animate-spin text-blue-500" />
          <p className="text-xs font-medium">Connecting to TyreIQ Intelligence Backend...</p>
        </div>
      </div>
    );
  }

  const riskDistribution = [
    { name: 'LOW', value: summary?.low_risk_tyres || 36 },
    { name: 'MEDIUM', value: summary?.medium_risk_tyres || 8 },
    { name: 'HIGH', value: summary?.high_risk_tyres || 4 },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner with live connection status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <DataSourceBadge source={isLive ? "sensor" : "simulator"} />
          <span className="text-xs text-slate-400">
            {isLive ? "Live FastAPI Backend Connected" : "Operating with Local Fallback"}
          </span>
        </div>
        <button
          onClick={loadDashboardData}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--color-surface-700)] text-xs text-slate-300 hover:text-white hover:bg-[var(--color-surface-600)] transition-colors border border-[var(--color-surface-600)]"
        >
          <RefreshCw size={12} className={loading ? "animate-spin" : ""} /> Refresh
        </button>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        <StatCard label="Total Trucks" value={summary?.total_trucks || 8} icon={Truck} color="blue" delay={0} />
        <StatCard label="Active Trucks" value={summary?.active_trucks || 6} icon={Truck} color="emerald" delay={1} />
        <StatCard label="Total Tyres" value={summary?.total_tyres || 48} icon={CircleDot} color="violet" delay={2} />
        <StatCard label="High Risk" value={summary?.high_risk_tyres || 4} icon={ShieldAlert} color="red" delay={3} />
        <StatCard label="Medium Risk" value={summary?.medium_risk_tyres || 8} icon={Shield} color="amber" delay={4} />
        <StatCard label="Low Risk" value={summary?.low_risk_tyres || 36} icon={ShieldCheck} color="emerald" delay={5} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Active Alerts" value={summary?.active_alerts || 6} icon={AlertTriangle} color="red" delay={6} />
        <StatCard label="Critical Maint." value={summary?.critical_maintenance || 4} icon={Wrench} color="amber" delay={7} />
        <StatCard label="Avg Temperature" value={formatTemp(summary?.avg_temperature_c || 66.4)} icon={Thermometer} color="red" delay={8} />
        <StatCard label="Avg Pressure" value={formatPressure(summary?.avg_pressure_kpa || 728.5)} icon={Gauge} color="blue" delay={9} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="card">
          <h3 className="text-sm font-semibold text-white mb-4">Risk Distribution</h3>
          <RiskDistributionChart data={riskDistribution} />
          <div className="flex justify-center gap-4 mt-3">
            {riskDistribution.map(d => (
              <div key={d.name} className="flex items-center gap-2 text-xs">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  d.name === 'HIGH' ? 'bg-red-400' : d.name === 'MEDIUM' ? 'bg-amber-400' : 'bg-emerald-400'
                }`} />
                <span className="text-slate-400">{d.name}: {d.value}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Temperature Trend */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="card">
          <h3 className="text-sm font-semibold text-white mb-4">Temperature Trend (24h)</h3>
          <TrendChart
            data={mockDashboardTrends.temperature}
            dataKey="value"
            secondaryKey="avg"
            color={CHART_COLORS.temperature}
            secondaryColor={CHART_COLORS.muted}
            unit="°C"
            height={200}
            showArea
          />
        </motion.div>

        {/* TKPH Trend */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="card">
          <h3 className="text-sm font-semibold text-white mb-4">TKPH Trend (24h)</h3>
          <TrendChart
            data={mockDashboardTrends.tkph}
            dataKey="value"
            referenceValue={1800}
            referenceLabel="Rated"
            color={CHART_COLORS.tkph}
            unit=""
            height={200}
            showArea
          />
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
          className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Recent Alerts</h3>
            <Link to="/alerts" className="text-xs text-blue-400 hover:text-blue-300 transition-colors">View All →</Link>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {alerts.filter(a => a.status === 'active').slice(0, 5).map(alert => (
              <div key={alert.alert_id}
                className={`p-3 rounded-lg bg-[var(--color-surface-700)] alert-severity--${alert.severity}`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-white">{alert.type.replace(/_/g, ' ')}</span>
                  <span className="text-[10px] text-slate-500">{formatRelativeTime(alert.timestamp)}</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{alert.message}</p>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="text-[10px] text-slate-500">{alert.truck_id}</span>
                  {alert.tyre_id && <span className="text-[10px] text-slate-500">{alert.tyre_id}</span>}
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Maintenance Priority */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}
          className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Maintenance Priority</h3>
            <Link to="/maintenance" className="text-xs text-blue-400 hover:text-blue-300 transition-colors">View All →</Link>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {maintenance.slice(0, 5).map(item => (
              <div key={item.tyre_id}
                className="flex items-center gap-3 p-3 rounded-lg bg-[var(--color-surface-700)]">
                <span className="w-7 h-7 flex items-center justify-center rounded-full bg-[var(--color-surface-600)] text-xs font-bold text-white">
                  {item.priority}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Link to={`/tyres/${item.tyre_id}`} className="text-xs font-semibold text-white hover:text-blue-400 transition-colors">
                      {item.tyre_id}
                    </Link>
                    <RiskBadge level={item.risk_label} size="sm" />
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5 truncate">{item.main_reason}</p>
                </div>
                <span className="text-[10px] text-slate-500">{item.truck_id}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
