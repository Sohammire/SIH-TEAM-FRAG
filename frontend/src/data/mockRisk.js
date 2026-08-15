/**
 * Mock risk data matching: GET /api/v1/tyres/{tyre_id}/risk
 * Source: SIMULATED DATA — MODEL OUTPUT
 * Note: The risk score is NOT a calibrated probability of failure.
 */

export const mockRiskResults = {
  'TYRE_03_RRO': {
    tyre_id: 'TYRE_03_RRO',
    timestamp: new Date().toISOString(),
    risk_score: 88,
    risk_label: 'HIGH',
    reasons: [
      'TKPH is 1.18× the rated value',
      'Temperature continues rising despite reduced speed',
      'Moderate sidewall cut detected (confidence: 0.91)',
      'Pressure loss rate: 8 kPa/h',
    ],
    recommended_action: 'STOP AND INSPECT BEFORE NEXT LOADED CYCLE',
    data_confidence: 0.91,
    stress_inputs: {
      thermal_stress: 72,
      pressure_stress: 68,
      tkph_stress: 78,
      damage_stress: 75,
      wear_stress: 35,
      impact_stress: 20,
    },
    source: 'fuzzy_risk_engine',
  },
  'TYRE_07_RRI': {
    tyre_id: 'TYRE_07_RRI',
    timestamp: new Date().toISOString(),
    risk_score: 76,
    risk_label: 'HIGH',
    reasons: [
      'Rapid pressure loss detected (12 kPa/h)',
      'Pressure below minimum safe threshold',
      'Temperature elevated at 85°C',
    ],
    recommended_action: 'IMMEDIATE INSPECTION — CHECK FOR PUNCTURE OR VALVE LEAK',
    data_confidence: 0.88,
    stress_inputs: {
      thermal_stress: 55,
      pressure_stress: 85,
      tkph_stress: 40,
      damage_stress: 30,
      wear_stress: 25,
      impact_stress: 15,
    },
    source: 'fuzzy_risk_engine',
  },
  'TYRE_02_FL': {
    tyre_id: 'TYRE_02_FL',
    timestamp: new Date().toISOString(),
    risk_score: 58,
    risk_label: 'MEDIUM',
    reasons: [
      'TKPH exceedance ratio 1.12×',
      'Temperature trend slightly elevated',
      'No structural damage detected',
    ],
    recommended_action: 'REDUCE SPEED OR PAYLOAD — INSPECT AT NEXT MAINTENANCE WINDOW',
    data_confidence: 0.93,
    stress_inputs: {
      thermal_stress: 48,
      pressure_stress: 25,
      tkph_stress: 65,
      damage_stress: 0,
      wear_stress: 30,
      impact_stress: 20,
    },
    source: 'fuzzy_risk_engine',
  },
};

// Default low-risk result for tyres not in the map
export const defaultRiskResult = {
  risk_score: 22,
  risk_label: 'LOW',
  reasons: [
    'All telemetry within normal range',
    'No damage detected',
    'TKPH below rated capacity',
  ],
  recommended_action: 'CONTINUE MONITORING — NO ACTION REQUIRED',
  data_confidence: 0.95,
  stress_inputs: {
    thermal_stress: 15,
    pressure_stress: 10,
    tkph_stress: 20,
    damage_stress: 0,
    wear_stress: 18,
    impact_stress: 8,
  },
  source: 'fuzzy_risk_engine',
};

export function getRiskForTyre(tyreId) {
  return mockRiskResults[tyreId] || {
    ...defaultRiskResult,
    tyre_id: tyreId,
    timestamp: new Date().toISOString(),
  };
}

export default mockRiskResults;
