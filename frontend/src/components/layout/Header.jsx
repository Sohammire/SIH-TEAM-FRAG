import { Bell, Search, Database } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { USE_MOCK_DATA } from '../../utils/constants';

const pageTitles = {
  '/': 'Overview Dashboard',
  '/fleet': 'Live Fleet Monitor',
  '/tyres': 'Tyre Monitoring',
  '/vision': 'Computer Vision',
  '/hotspots': 'Mine Road Hotspots',
  '/maintenance': 'Maintenance Priority',
  '/alerts': 'Alert Center',
  '/data-quality': 'Data Quality',
};

export default function Header() {
  const location = useLocation();
  // Match the base path for nested routes
  const basePath = '/' + (location.pathname.split('/')[1] || '');
  const title = pageTitles[basePath] || 'TyreIQ';

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-[var(--color-surface-600)]"
      style={{ background: 'var(--color-surface-800)' }}>
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
        {USE_MOCK_DATA && (
          <span className="source-badge source-badge--simulator">
            <Database size={10} />
            SIMULATED DATA
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative hidden md:block">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search trucks, tyres..."
            className="w-56 pl-9 pr-3 py-1.5 rounded-lg text-sm bg-[var(--color-surface-700)] border border-[var(--color-surface-600)] text-slate-300 placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 transition-colors"
          />
        </div>

        {/* Alert bell */}
        <button className="relative p-2 rounded-lg hover:bg-[var(--color-surface-700)] text-slate-400 hover:text-slate-200 transition-colors">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full pulse-dot" />
        </button>

        {/* User avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-xs font-bold text-white">
          OP
        </div>
      </div>
    </header>
  );
}
