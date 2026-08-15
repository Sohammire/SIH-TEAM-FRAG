import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft, ShieldAlert, Thermometer, Gauge, Activity, TrendingUp,
  AlertTriangle, Wrench, Eye, RefreshCw
} from 'lucide-react';
import RiskBadge from '../components/common/RiskBadge';
import DataSourceBadge from '../components/common/DataSourceBadge';
import RadarChartComponent from '../components/charts/RadarChartComponent';
import TrendChart from '../components/charts/TrendChart';
import {
  fetchTyreDetails, fetchTyreRisk, fetchTKPHAnalytics,
  fetchTemperaturePrediction, fetchWearProjection
} from '../api';
import { formatTemp, formatPressure } from '../utils/formatters';
import { CHART_COLORS } from '../utils/constants';

export default function TyreDetailPage() {
  const { id } = useParams();
  const tyreId = id || 'TYRE_03_RRO';

  const [tyre, setTyre] = useState(null);
  const [risk, setRisk] = useState(null);
  const [tkph, setTkph] = useState(null);
  const [tempPred, setTempPred] = useState(null);
  const [wearProj, setWearProj] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(false);

  const loadTyreData = async () => {
    setLoading(true);
    const tyreRes = await fetchTyreDetails(tyreId);
    const riskRes = await fetchTyreRisk(tyreId);
    const tkphRes = await fetchTKPHAnalytics(tyreId);
    const tempRes = await fetchTemperaturePrediction(tyreId);
    const wearRes = await fetchWearProjection(tyreId);

    setTyre(tyreRes.data);
    setRisk(riskRes.data);
    setTkph(tkphRes.data);
    setTempPred(tempRes.data);
    setWearProj(wearRes.data);
    setIsLive(tyreRes.isLive);
    setLoading(false);
  };

  useEffect(() => {
    loadTyreData();
  }, [tyreId]);

  if (loading && !tyre) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3 text-slate-400">
          <RefreshCw size={24} className="animate-spin text-blue-500" />
          <p className="text-xs font-medium">Fetching Tyre Intelligence Data for {tyreId}...</p>
        </div>
      </div>
    );
  }

  const stressInputs = risk?.stress_inputs || {
    thermal_stress: 85,
    pressure_stress: 70,
    tkph_stress: 90,
    damage_stress: 88,
    wear_stress: 40,
    impact_stress: 30
  };

  const radarData = [
    { subject: 'Thermal', value: stressInputs.thermal_stress, fullMark: 100 },
    { subject: 'Pressure', value: stressInputs.pressure_stress, fullMark: 100 },
    { subject: 'TKPH', value: stressInputs.tkph_stress, fullMark: 100 },
    { subject: 'Damage', value: stressInputs.damage_stress, fullMark: 100 },
    { subject: 'Wear', value: stressInputs.wear_stress, fullMark: 100 },
    { subject: 'Impact', value: stressInputs.impact_stress, fullMark: 100 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link to="/tyre-monitoring" className="p-2 rounded-lg bg-[var(--color-surface-700)] text-slate-400 hover:text-white transition-colors">
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-white">{tyreId}</h1>
              <RiskBadge level={risk?.risk_label || 'HIGH'} size="lg" />
              <DataSourceBadge source={isLive ? "sensor" : "simulator"} />
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Installed on <span className="text-white font-medium">{tyre?.truck_id || 'DUMPER_03'}</span> ({tyre?.position || 'rear_right_outer'}) • {tyre?.manufacturer || 'Michelin'} {tyre?.model || 'XDR3'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/vision" className="btn-secondary text-xs">
            <Eye size={14} /> Run Vision Inspection
          </Link>
          <button onClick={loadTyreData} className="btn-secondary text-xs">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Refresh
          </button>
        </div>
      </div>

      {/* Recommended Action Alert */}
      {risk?.recommended_action && (
        <div className={`p-4 rounded-xl border flex items-center justify-between gap-4 ${
          risk.risk_label === 'HIGH'
            ? 'bg-red-500/10 border-red-500/30 text-red-300'
            : risk.risk_label === 'MEDIUM'
            ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
        }`}>
          <div className="flex items-center gap-3">
            <ShieldAlert size={20} />
            <div>
              <p className="text-xs font-semibold text-white">Recommended Safety Action:</p>
              <p className="text-xs font-bold mt-0.5">{risk.recommended_action}</p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-slate-400 block">Data Confidence</span>
            <span className="text-xs font-bold text-white">{Math.round((risk.data_confidence || 0.91) * 100)}%</span>
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="card text-center">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Fuzzy Risk Score</span>
          <p className="text-2xl font-black text-red-400 mt-1">{risk?.risk_score || 88.0}</p>
          <span className="text-[10px] text-slate-500">Defuzzified Centroid</span>
        </div>
        <div className="card text-center">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Chamber Pressure</span>
          <p className="text-2xl font-bold text-white mt-1">{formatPressure(tyre?.current_pressure_kpa || 580)}</p>
          <span className="text-[10px] text-red-400">Low (Target 735)</span>
        </div>
        <div className="card text-center">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Temperature</span>
          <p className="text-2xl font-bold text-white mt-1">{formatTemp(tyre?.current_temp_c || 92)}</p>
          <span className="text-[10px] text-amber-400">Slope: +{tempPred?.temperature_slope_c_per_h || 120}°C/h</span>
        </div>
        <div className="card text-center">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Current TKPH</span>
          <p className="text-2xl font-bold text-white mt-1">{tkph?.tkph_current || 2124}</p>
          <span className="text-[10px] text-red-400">{tkph?.tkph_exceedance_ratio || 1.18}× Rated</span>
        </div>
        <div className="card text-center">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Current Tread</span>
          <p className="text-2xl font-bold text-white mt-1">{wearProj?.current_tread_mm || 65} mm</p>
          <span className="text-[10px] text-slate-500">Initial: 85 mm</span>
        </div>
        <div className="card text-center">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider">Wear Rate</span>
          <p className="text-lg font-bold text-white mt-1">{wearProj?.wear_rate_mm_per_hour || 0.005} mm/h</p>
          <span className="text-[10px] text-blue-400">Wear Projection</span>
        </div>
      </div>

      {/* Main Grid: Stress Radar & Explanations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mamdani Stress Radar */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white">Mamdani Stress Inputs Radar</h3>
            <DataSourceBadge source="fuzzy_risk_engine" />
          </div>
          <p className="text-xs text-slate-400 mb-4">6 normalized stress dimensions (0-100) feeding into centroid defuzzification.</p>
          <RadarChartComponent data={radarData} height={280} />
        </motion.div>

        {/* Explainable Reasons */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Explainable Risk Reasons</h3>
            <span className="text-xs text-slate-400">Rule Base Evaluation</span>
          </div>
          <div className="space-y-3">
            {risk?.reasons?.map((reason, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-[var(--color-surface-700)] border border-[var(--color-surface-600)]">
                <AlertTriangle size={16} className="text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-white">{reason}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">Mamdani Safety Rule #{idx + 1} Triggered</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Thermal Anomaly & Wear Projection */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Thermal Model Prediction */}
        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-2">First-Order Thermal Prediction Model</h3>
          <p className="text-xs text-slate-400 mb-4">Calibrated Ridge Regression with 70/30 chronological split.</p>
          <div className="grid grid-cols-3 gap-3 p-3 rounded-lg bg-[var(--color-surface-700)] mb-4">
            <div>
              <span className="text-[10px] text-slate-400 block">Actual Temp</span>
              <span className="text-sm font-bold text-white">{tempPred?.current_temperature_c || 92}°C</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 block">Model Predicted</span>
              <span className="text-sm font-bold text-blue-400">{tempPred?.predicted_temperature_c || 83.5}°C</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 block">Thermal Residual</span>
              <span className="text-sm font-bold text-red-400">+{tempPred?.residual_c || 8.5}°C</span>
            </div>
          </div>
          {tempPred?.abnormal_trajectory && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-300">
              <span className="font-bold">Abnormal Trajectory Detected: </span>
              {tempPred.abnormal_reasons?.join('; ')}
            </div>
          )}
        </div>

        {/* Wear Projection (NOT RUL) */}
        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-2">Tread Wear Projection</h3>
          <p className="text-xs text-slate-400 mb-4">Extrapolated remaining operational hours band (Huber Regressor).</p>
          <div className="p-4 rounded-lg bg-[var(--color-surface-700)] space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Projected Remaining Hours:</span>
              <span className="font-bold text-white">{wearProj?.wear_projection?.projected_remaining_hours || 9000} h</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Confidence Band (85%-115%):</span>
              <span className="font-bold text-blue-400">
                {wearProj?.wear_projection?.confidence_band_hours?.[0] || 7650} h - {wearProj?.wear_projection?.confidence_band_hours?.[1] || 10350} h
              </span>
            </div>
            <div className="p-2.5 rounded bg-[var(--color-surface-800)] text-[10px] text-slate-400 border border-[var(--color-surface-600)]">
              ℹ️ Disclaimer: This output is a wear projection based on linear regression extrapolation, NOT a validated RUL prediction.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
