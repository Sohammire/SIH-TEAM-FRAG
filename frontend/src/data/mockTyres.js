/**
 * Mock tyre data matching the API contract: GET /api/v1/tyres
 * Source: SIMULATED DATA
 *
 * Traceability: truck_id → tyre_id → fitment_id → wheel_position → timestamp
 */

const now = new Date().toISOString();

const positions = [
  'front_left', 'front_right',
  'rear_left_inner', 'rear_left_outer',
  'rear_right_inner', 'rear_right_outer',
];

function makeTyres(truckId, truckIndex) {
  return positions.map((pos, i) => {
    const tyreIdx = truckIndex * 6 + i;
    const posAbbr = pos.split('_').map(w => w[0].toUpperCase()).join('');
    const tyreId = `TYRE_${String(truckIndex + 1).padStart(2, '0')}_${posAbbr}`;

    // Vary data realistically
    const basePressure = 700 + Math.floor(Math.random() * 60);
    const baseTemp = 55 + Math.floor(Math.random() * 40);
    const tkph = 1200 + Math.floor(Math.random() * 600);
    const ratedTkph = 1800;
    const wearRate = 0.002 + Math.random() * 0.008;
    const riskScore = Math.floor(Math.random() * 100);
    const riskLabel = riskScore > 70 ? 'HIGH' : riskScore > 40 ? 'MEDIUM' : 'LOW';

    return {
      tyre_id: tyreId,
      truck_id: truckId,
      fitment_id: `FIT_${tyreId}`,
      position: pos,
      manufacturer: i % 2 === 0 ? 'Michelin' : 'Bridgestone',
      model: i % 2 === 0 ? 'XDR3' : 'VRPS',
      size: '59/80R63',
      rated_tkph: ratedTkph,
      install_date: '2026-01-15',
      initial_tread_mm: 85,
      current_tread_mm: 85 - Math.floor(Math.random() * 30),
      cost: 45000 + Math.floor(Math.random() * 15000),
      status: 'active',
      current_pressure_kpa: basePressure,
      current_temp_c: baseTemp,
      ambient_temp_c: 34,
      tkph_current: tkph,
      tkph_rated: ratedTkph,
      tkph_exceedance_ratio: +(tkph / ratedTkph).toFixed(2),
      wear_rate_mm_per_h: +wearRate.toFixed(4),
      risk_score: riskScore,
      risk_label: riskLabel,
      last_update: now,
      source: 'simulator',
    };
  });
}

const truckIds = [
  'DUMPER_01', 'DUMPER_02', 'DUMPER_03', 'DUMPER_04',
  'DUMPER_05', 'DUMPER_06', 'DUMPER_07', 'DUMPER_08',
];

// Generate consistent mock tyres (seeded approach)
export const mockTyres = truckIds.flatMap((id, idx) => makeTyres(id, idx));

// Manually set some specific high-risk scenarios for demo
// DUMPER_03 rear_right_outer — severe sidewall cut + pressure loss
const d03RRO = mockTyres.find(t => t.truck_id === 'DUMPER_03' && t.position === 'rear_right_outer');
if (d03RRO) {
  d03RRO.risk_score = 88;
  d03RRO.risk_label = 'HIGH';
  d03RRO.current_pressure_kpa = 580;
  d03RRO.current_temp_c = 92;
  d03RRO.tkph_exceedance_ratio = 1.18;
  d03RRO.tkph_current = 2124;
}

// DUMPER_07 rear_right_inner — pressure leak scenario
const d07RRI = mockTyres.find(t => t.truck_id === 'DUMPER_07' && t.position === 'rear_right_inner');
if (d07RRI) {
  d07RRI.risk_score = 76;
  d07RRI.risk_label = 'HIGH';
  d07RRI.current_pressure_kpa = 610;
  d07RRI.current_temp_c = 85;
}

// DUMPER_02 front_left — TKPH exceedance
const d02FL = mockTyres.find(t => t.truck_id === 'DUMPER_02' && t.position === 'front_left');
if (d02FL) {
  d02FL.risk_score = 58;
  d02FL.risk_label = 'MEDIUM';
  d02FL.tkph_exceedance_ratio = 1.12;
  d02FL.tkph_current = 2016;
}

export default mockTyres;
