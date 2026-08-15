import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Popup, LayersControl } from 'react-leaflet';
import { mockMineRoads, mockMineBoundary, mockImpactLocations, MAP_CENTER, MAP_ZOOM } from '../data/mockGeoJSON';
import { mockHotspots } from '../data/mockHotspots';
import DataSourceBadge from '../components/common/DataSourceBadge';

function getSegmentColor(segmentId) {
  const hs = mockHotspots.find(h => h.road_segment_id === segmentId);
  if (!hs) return '#475569';
  const score = hs.hotspot_score;
  if (score >= 70) return '#ef4444';
  if (score >= 40) return '#f59e0b';
  return '#10b981';
}

function getSegmentWeight(segmentId) {
  const hs = mockHotspots.find(h => h.road_segment_id === segmentId);
  if (!hs) return 3;
  return Math.max(3, Math.min(8, hs.hotspot_score / 12));
}

export default function HotspotPage() {
  const [selectedLayer, setSelectedLayer] = useState('all');

  const filteredImpacts = useMemo(() => {
    if (selectedLayer === 'all') return mockImpactLocations;
    const segments = mockHotspots
      .filter(h => h.hotspot_type === selectedLayer)
      .map(h => h.road_segment_id);
    return mockImpactLocations.filter(i => segments.includes(i.segment_id));
  }, [selectedLayer]);

  const roadStyle = (feature) => ({
    color: getSegmentColor(feature.properties.segment_id),
    weight: getSegmentWeight(feature.properties.segment_id),
    opacity: 0.8,
    dashArray: feature.properties.road_type === 'service' ? '5 5' : null,
  });

  const onEachRoad = (feature, layer) => {
    const segId = feature.properties.segment_id;
    const hs = mockHotspots.find(h => h.road_segment_id === segId);
    if (!hs) return;

    layer.bindPopup(`
      <div style="font-family: Inter, sans-serif; min-width: 220px;">
        <h4 style="margin: 0 0 8px; font-size: 13px; font-weight: 700;">${hs.name}</h4>
        <table style="font-size: 11px; width: 100%; border-collapse: collapse;">
          <tr><td style="color: #94a3b8; padding: 2px 0;">Segment ID</td><td style="font-weight: 600; text-align: right;">${hs.road_segment_id}</td></tr>
          <tr><td style="color: #94a3b8; padding: 2px 0;">Truck-km</td><td style="font-weight: 600; text-align: right;">${hs.truck_km.toLocaleString()}</td></tr>
          <tr><td style="color: #94a3b8; padding: 2px 0;">Impact Events</td><td style="font-weight: 600; text-align: right;">${hs.impact_events}</td></tr>
          <tr><td style="color: #94a3b8; padding: 2px 0;">Damage Events</td><td style="font-weight: 600; text-align: right;">${hs.damage_events}</td></tr>
          <tr><td style="color: #94a3b8; padding: 2px 0;">Failure Events</td><td style="font-weight: 600; text-align: right;">${hs.failure_events}</td></tr>
          <tr style="border-top: 1px solid #334155;"><td style="color: #94a3b8; padding: 4px 0 2px;">Impact Rate</td><td style="font-weight: 600; text-align: right;">${hs.impact_rate_per_100_truck_km.toFixed(2)}/100 tk-km</td></tr>
          <tr><td style="color: #94a3b8; padding: 2px 0;">Damage Rate</td><td style="font-weight: 600; text-align: right;">${hs.damage_rate_per_100_truck_km.toFixed(2)}/100 tk-km</td></tr>
          <tr><td style="color: #94a3b8; padding: 2px 0;">Failure Rate</td><td style="font-weight: 600; text-align: right;">${hs.failure_rate_per_100_truck_km.toFixed(2)}/100 tk-km</td></tr>
          <tr style="border-top: 1px solid #334155;"><td style="color: #94a3b8; padding: 4px 0 2px;">Hotspot Score</td><td style="font-weight: 700; text-align: right; color: ${hs.hotspot_score >= 70 ? '#ef4444' : hs.hotspot_score >= 40 ? '#f59e0b' : '#10b981'};">${hs.hotspot_score}/100</td></tr>
          <tr><td style="color: #94a3b8; padding: 2px 0;">Hotspot Type</td><td style="font-weight: 600; text-align: right; text-transform: capitalize;">${hs.hotspot_type || 'none'}</td></tr>
        </table>
        <p style="font-size: 9px; color: #64748b; margin-top: 6px;">Rates are exposure-normalized per 100 truck-km.</p>
      </div>
    `);
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-xs text-slate-500">Layer:</span>
        {['all', 'impact', 'damage', 'failure'].map(l => (
          <button key={l} onClick={() => setSelectedLayer(l)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all
              ${selectedLayer === l
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-400 hover:text-white bg-[var(--color-surface-700)] border border-transparent'
              }`}>
            {l === 'all' ? 'All Layers' : `${l} Hotspot`}
          </button>
        ))}
        <div className="ml-auto">
          <DataSourceBadge source="simulator" />
        </div>
      </div>

      {/* Map */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-0 overflow-hidden" style={{ height: '500px' }}>
        <MapContainer center={MAP_CENTER} zoom={MAP_ZOOM} style={{ height: '100%', width: '100%' }} className="rounded-xl">
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'
          />

          {/* Mine roads */}
          <GeoJSON data={mockMineRoads} style={roadStyle} onEachFeature={onEachRoad} />

          {/* Impact markers */}
          {filteredImpacts.map((imp, i) => (
            <CircleMarker
              key={i}
              center={[imp.lat, imp.lon]}
              radius={Math.max(4, imp.peak_g * 1.5)}
              pathOptions={{
                color: imp.severity === 'high' ? '#ef4444' : imp.severity === 'medium' ? '#f59e0b' : '#06b6d4',
                fillColor: imp.severity === 'high' ? '#ef4444' : imp.severity === 'medium' ? '#f59e0b' : '#06b6d4',
                fillOpacity: 0.6,
                weight: 1,
              }}
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '11px' }}>
                  <p style={{ fontWeight: 700 }}>Impact Event</p>
                  <p>Peak: {imp.peak_g}g · {imp.severity}</p>
                  <p>Segment: {imp.segment_id}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </motion.div>

      {/* Hotspot Table */}
      <div className="card p-0 overflow-hidden">
        <div className="p-4 border-b border-[var(--color-surface-600)]">
          <h3 className="text-sm font-semibold text-white">Road Segment Scores</h3>
          <p className="text-[10px] text-slate-500 mt-1">Rates are exposure-normalized per 100 truck-km. Do not rank by raw event count alone.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-surface-600)]">
                {['Segment', 'Name', 'Truck-km', 'Impacts', 'Damages', 'Failures',
                  'Impact Rate', 'Damage Rate', 'Failure Rate', 'Score', 'Type'].map(h => (
                  <th key={h} className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...mockHotspots].sort((a, b) => b.hotspot_score - a.hotspot_score).map(hs => (
                <tr key={hs.road_segment_id} className="border-b border-[var(--color-surface-600)] hover:bg-[var(--color-surface-700)] transition-colors">
                  <td className="px-3 py-2.5 text-xs font-semibold text-white">{hs.road_segment_id}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">{hs.name}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{hs.truck_km.toLocaleString()}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{hs.impact_events}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{hs.damage_events}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{hs.failure_events}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{hs.impact_rate_per_100_truck_km.toFixed(2)}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{hs.damage_rate_per_100_truck_km.toFixed(2)}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-300">{hs.failure_rate_per_100_truck_km.toFixed(2)}</td>
                  <td className="px-3 py-2.5">
                    <span className={`text-xs font-bold ${
                      hs.hotspot_score >= 70 ? 'text-red-400' : hs.hotspot_score >= 40 ? 'text-amber-400' : 'text-emerald-400'
                    }`}>{hs.hotspot_score}</span>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-400 capitalize">{hs.hotspot_type || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
        <p className="text-[10px] text-amber-400 font-semibold uppercase mb-1">⚠ Configuration Note</p>
        <p className="text-xs text-slate-400">
          Map coordinates are demo/configurable — not hardcoded operational data. Replace the GeoJSON
          layer with actual mine-road coordinates when available.
        </p>
      </div>
    </div>
  );
}
