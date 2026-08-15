import { Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import FleetPage from './pages/FleetPage';
import TyreMonitorPage from './pages/TyreMonitorPage';
import TyreDetailPage from './pages/TyreDetailPage';
import VisionPage from './pages/VisionPage';
import HotspotPage from './pages/HotspotPage';
import MaintenancePage from './pages/MaintenancePage';
import AlertPage from './pages/AlertPage';
import DataQualityPage from './pages/DataQualityPage';

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/fleet" element={<FleetPage />} />
        <Route path="/fleet/:truckId" element={<FleetPage />} />
        <Route path="/tyres" element={<TyreMonitorPage />} />
        <Route path="/tyres/:tyreId" element={<TyreDetailPage />} />
        <Route path="/vision" element={<VisionPage />} />
        <Route path="/hotspots" element={<HotspotPage />} />
        <Route path="/maintenance" element={<MaintenancePage />} />
        <Route path="/alerts" element={<AlertPage />} />
        <Route path="/data-quality" element={<DataQualityPage />} />
      </Route>
    </Routes>
  );
}
