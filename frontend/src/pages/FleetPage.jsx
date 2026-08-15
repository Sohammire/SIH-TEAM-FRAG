import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { MapPin, Gauge, Thermometer, Zap, Weight, CircleDot, ArrowLeft } from 'lucide-react';
import RiskBadge from '../components/common/RiskBadge';
import DataSourceBadge from '../components/common/DataSourceBadge';
import TrendChart from '../components/charts/TrendChart';
import { mockTrucks } from '../data/mockTrucks';
import { mockTyres } from '../data/mockTyres';
import { mockPressureTrend, mockTemperatureTrend, mockSpeedTrend, mockPayloadTrend } from '../data/mockTelemetry';
import { formatSpeed, formatPayload, formatTemp, formatPressure, formatPosition } from '../utils/formatters';
import { CHART_COLORS } from '../utils/constants';

function TruckCard({ truck }) {
  const tyres = mockTyres.filter(t => t.truck_id === truck.truck_id);
  const statusColor = {
    active: 'bg-emerald-400',
    idle: 'bg-amber-400',
    maintenance: 'bg-blue-400',
    offline: 'bg-slate-500',
  };

  return (
    <Link to={`/fleet/${truck.truck_id}`}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.02 }}
        className="card cursor-pointer"
      >
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold text-white">{truck.truck_id}</h3>
            <p className="text-xs text-slate-400">{truck.model}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${statusColor[truck.status]}`} />
            <span className="text-xs text-slate-400 capitalize">{truck.status}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Gauge size={13} className="text-blue-400" />
            <span>{formatSpeed(truck.current_speed_kmh)}</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Weight size={13} className="text-cyan-400" />
            <span>{formatPayload(truck.current_payload_t)}</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <MapPin size={13} className="text-violet-400" />
            <span>{truck.gps_lat.toFixed(3)}, {truck.gps_lon.toFixed(3)}</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <CircleDot size={13} className="text-amber-400" />
            <span>{truck.total_tyres} tyres</span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-[var(--color-surface-600)]">
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-500">Highest risk:</span>
            <RiskBadge level={truck.highest_risk} size="sm" />
          </div>
          {truck.current_alert && (
            <span className="text-[10px] px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
              {truck.current_alert.replace(/_/g, ' ')}
            </span>
          )}
        </div>

        <div className="mt-2">
          <DataSourceBadge source={truck.source} />
        </div>
      </motion.div>
    </Link>
  );
}

function TruckDetailsView() {
  const { truckId } = useParams();
  const navigate = useNavigate();
  const truck = mockTrucks.find(t => t.truck_id === truckId);
  const tyres = mockTyres.filter(t => t.truck_id === truckId);

  if (!truck) {
    return (
      <div className="text-center py-20">
        <p className="text-slate-400">Truck not found.</p>
        <button onClick={() => navigate('/fleet')} className="mt-4 text-blue-400 text-sm">← Back to Fleet</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/fleet')}
        className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
        <ArrowLeft size={16} /> Back to Fleet
      </button>

      {/* Truck header */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">{truck.truck_id}</h2>
            <p className="text-sm text-slate-400">{truck.model} · {truck.mine_id}</p>
          </div>
          <DataSourceBadge source={truck.source} />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div><p className="text-[10px] text-slate-500 uppercase">Speed</p><p className="text-lg font-bold text-white">{formatSpeed(truck.current_speed_kmh)}</p></div>
          <div><p className="text-[10px] text-slate-500 uppercase">Payload</p><p className="text-lg font-bold text-white">{formatPayload(truck.current_payload_t)}</p></div>
          <div><p className="text-[10px] text-slate-500 uppercase">GPS</p><p className="text-lg font-bold text-white">{truck.gps_lat.toFixed(4)}, {truck.gps_lon.toFixed(4)}</p></div>
          <div><p className="text-[10px] text-slate-500 uppercase">Status</p><p className="text-lg font-bold text-white capitalize">{truck.status}</p></div>
        </div>
      </div>

      {/* Live telemetry charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <TrendChart data={mockSpeedTrend} color={CHART_COLORS.speed} title="Speed" unit=" km/h" showArea />
        </div>
        <div className="card">
          <TrendChart data={mockPayloadTrend} color={CHART_COLORS.payload} title="Payload" unit=" t" showArea />
        </div>
      </div>

      {/* Tyre positions */}
      <div className="card">
        <h3 className="text-sm font-semibold text-white mb-4">Tyre Positions</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {tyres.map(tyre => (
            <Link to={`/tyres/${tyre.tyre_id}`} key={tyre.tyre_id}
              className="p-3 rounded-lg bg-[var(--color-surface-700)] hover:bg-[var(--color-surface-600)] transition-colors border border-[var(--color-surface-600)] text-center">
              <p className="text-[10px] text-slate-500 uppercase">{formatPosition(tyre.position)}</p>
              <p className="text-xs font-bold text-white mt-1">{tyre.tyre_id}</p>
              <div className="mt-2 space-y-1">
                <div className="flex items-center justify-center gap-1 text-[10px] text-slate-400">
                  <Thermometer size={10} className="text-red-400" />
                  {formatTemp(tyre.current_temp_c)}
                </div>
                <div className="flex items-center justify-center gap-1 text-[10px] text-slate-400">
                  <Gauge size={10} className="text-blue-400" />
                  {formatPressure(tyre.current_pressure_kpa)}
                </div>
              </div>
              <div className="mt-2">
                <RiskBadge level={tyre.risk_label} score={tyre.risk_score} size="sm" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function FleetPage() {
  const { truckId } = useParams();
  const [filter, setFilter] = useState('all');

  if (truckId) return <TruckDetailsView />;

  const filtered = filter === 'all'
    ? mockTrucks
    : mockTrucks.filter(t => t.status === filter);

  return (
    <div className="space-y-6">
      {/* Filter tabs */}
      <div className="flex items-center gap-2">
        {['all', 'active', 'idle', 'maintenance', 'offline'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all
              ${filter === f
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-400 hover:text-white bg-[var(--color-surface-700)] border border-transparent'
              }`}
          >
            {f} {f === 'all' && `(${mockTrucks.length})`}
          </button>
        ))}
      </div>

      {/* Truck grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map(truck => (
          <TruckCard key={truck.truck_id} truck={truck} />
        ))}
      </div>
    </div>
  );
}
