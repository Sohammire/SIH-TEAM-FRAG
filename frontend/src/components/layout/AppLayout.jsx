import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

export default function AppLayout() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      {/* Main content — left margin matches sidebar width (animated via CSS) */}
      <div className="flex-1 ml-[260px] flex flex-col min-h-screen transition-all duration-200">
        <Header />
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
