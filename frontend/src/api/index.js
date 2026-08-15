import apiClient from './client';
import { mockTrucks } from '../data/mockTrucks';
import { mockTyres } from '../data/mockTyres';
import { mockAlerts } from '../data/mockAlerts';
import { mockMaintenance } from '../data/mockMaintenance';
import { mockHotspots } from '../data/mockHotspots';
import { getRiskForTyre } from '../data/mockRisk';

/**
 * Generic safe API call wrapper with fallback to mock data on network error.
 */
async function safeApiCall(apiFunc, mockFallback) {
  try {
    const response = await apiFunc();
    return { data: response.data, isLive: true, error: null };
  } catch (err) {
    console.warn('[API Fallback] Live backend call failed, falling back to mock dataset:', err.message);
    return { data: mockFallback, isLive: false, error: err.message };
  }
}

export const fetchDashboardSummary = () =>
  safeApiCall(
    () => apiClient.get('/dashboard/summary'),
    {
      total_trucks: mockTrucks.length,
      active_trucks: mockTrucks.filter(t => t.status === 'active').length,
      total_tyres: mockTyres.length,
      high_risk_tyres: mockTyres.filter(t => t.risk_label === 'HIGH').length,
      medium_risk_tyres: mockTyres.filter(t => t.risk_label === 'MEDIUM').length,
      low_risk_tyres: mockTyres.filter(t => t.risk_label === 'LOW').length,
      active_alerts: mockAlerts.filter(a => a.status === 'active').length,
      critical_maintenance: mockMaintenance.filter(m => m.risk_label === 'HIGH').length,
      avg_temperature_c: 66.4,
      avg_pressure_kpa: 728.5,
      avg_tkph: 1465.0,
      road_hotspot_count: 3
    }
  );

export const fetchTrucks = () =>
  safeApiCall(
    () => apiClient.get('/trucks'),
    mockTrucks
  );

export const fetchTruckDetails = (truckId) =>
  safeApiCall(
    () => apiClient.get(`/trucks/${truckId}`),
    mockTrucks.find(t => t.truck_id === truckId) || mockTrucks[0]
  );

export const fetchTruckLive = (truckId) =>
  safeApiCall(
    () => apiClient.get(`/trucks/${truckId}/live`),
    {
      truck_id: truckId,
      status: 'active',
      current_speed_kmh: 28.0,
      current_payload_t: 280.0,
      gps_lat: 20.1234,
      gps_lon: 79.0456,
      tyres: mockTyres.filter(t => t.truck_id === truckId),
      last_update: new Date().toISOString()
    }
  );

export const fetchTyres = () =>
  safeApiCall(
    () => apiClient.get('/tyres'),
    mockTyres
  );

export const fetchTyreDetails = (tyreId) =>
  safeApiCall(
    () => apiClient.get(`/tyres/${tyreId}`),
    mockTyres.find(t => t.tyre_id === tyreId) || mockTyres[0]
  );

export const fetchTyreRisk = (tyreId) =>
  safeApiCall(
    () => apiClient.get(`/tyres/${tyreId}/risk`),
    getRiskForTyre(tyreId)
  );

export const fetchTKPHAnalytics = (tyreId) =>
  safeApiCall(
    () => apiClient.get(`/analytics/tkph/${tyreId}`),
    {
      tkph_current: 1968.8,
      tkph_shift: 1968.8,
      awss_kmh: 28.2,
      mean_tyre_load_t: 69.8,
      rated_tkph: 1800.0,
      tkph_exceedance_ratio: 1.09,
      exceedance_minutes: 5.0,
      workload_status: 'WARNING'
    }
  );

export const fetchTemperaturePrediction = (tyreId) =>
  safeApiCall(
    () => apiClient.get(`/analytics/temperature-prediction/${tyreId}`),
    {
      current_temperature_c: 92.0,
      predicted_temperature_c: 83.5,
      residual_c: 8.5,
      temperature_slope_c_per_h: 120.0,
      abnormal_trajectory: true,
      abnormal_reasons: ['Temperature 92.0°C exceeds critical threshold (90°C)']
    }
  );

export const fetchWearProjection = (tyreId) =>
  safeApiCall(
    () => apiClient.get(`/analytics/wear-projection/${tyreId}`),
    {
      tyre_id: tyreId,
      initial_tread_mm: 85.0,
      current_tread_mm: 65.0,
      min_safe_tread_mm: 20.0,
      operating_hours: 500.0,
      wear_rate_mm_per_hour: 0.005,
      wear_projection: {
        projected_remaining_hours: 9000.0,
        confidence_band_hours: [7650.0, 10350.0]
      }
    }
  );

export const predictVision = async (formData) => {
  try {
    const res = await apiClient.post('/vision/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return { data: res.data, isLive: true, error: null };
  } catch (err) {
    console.warn('[Vision API Error] Falling back to staged result:', err.message);
    return {
      data: {
        inspection_id: 'INS_DEMO_01',
        image_id: 'IMG_DEMO_01',
        tyre_id: 'TYRE_03_RRO',
        truck_id: 'DUMPER_03',
        damage_present: true,
        damage_type: 'cut',
        location: 'sidewall',
        severity: 'moderate',
        confidence: 0.91,
        bbox: [145.0, 95.0, 355.0, 275.0],
        model_version: 'yolov8n-tyredmg-v0.1',
        source: 'vision_model',
        image_quality_status: 'good',
        quality_warning: null
      },
      isLive: false,
      error: err.message
    };
  }
};

export const fetchHotspots = (trafficMultiplier = 1.0) =>
  safeApiCall(
    () => apiClient.get(`/hotspots?traffic_multiplier=${trafficMultiplier}`),
    mockHotspots
  );

export const fetchMaintenancePriorities = () =>
  safeApiCall(
    () => apiClient.get('/maintenance/priorities'),
    mockMaintenance
  );

export const fetchAlerts = () =>
  safeApiCall(
    () => apiClient.get('/alerts'),
    mockAlerts
  );

export const triggerSimulation = (scenarioId, truckId = 'DUMPER_01', tyreId = 'TYRE_01_FL') =>
  safeApiCall(
    () => apiClient.post('/telemetry/simulate', {
      scenario_id: scenarioId,
      truck_id: truckId,
      tyre_id: tyreId,
      duration_seconds: 60
    }),
    { status: 'started', scenario_id: scenarioId, generated_records: 60 }
  );
