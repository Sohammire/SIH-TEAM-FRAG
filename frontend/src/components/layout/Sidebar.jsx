import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, Truck, CircleDot, Eye, Map, Wrench,
  Bell, ShieldCheck, ChevronLeft, ChevronRight, Activity
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/fleet', icon: Truck, label: 'Fleet Monitor' },
  { to: '/tyres', icon: CircleDot, label: 'Tyre Monitoring' },
  { to: '/vision', icon: Eye, label: 'Computer Vision' },
  { to: '/hotspots', icon: Map, label: 'Mine Hotspots' },
  { to: '/maintenance', icon: Wrench, label: 'Maintenance' },
  { to: '/alerts', icon: Bell, label: 'Alert Center' },
  { to: '/data-quality', icon: ShieldCheck, label: 'Data Quality' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-screen z-40 flex flex-col"
      style={{ background: 'var(--color-surface-800)', borderRight: '1px solid var(--color-surface-600)' }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-[var(--color-surface-600)]">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center flex-shrink-0">
          <Activity size={20} className="text-white" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="overflow-hidden whitespace-nowrap"
            >
              <h1 className="text-base font-bold text-white tracking-tight">TyreIQ</h1>
              <p className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">Mining Intelligence</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group
              ${isActive
                ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[var(--color-surface-700)] border border-transparent'
              }`
            }
          >
            <Icon size={19} className="flex-shrink-0" />
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="overflow-hidden whitespace-nowrap"
                >
                  {label}
                </motion.span>
              )}
            </AnimatePresence>
          </NavLink>
        ))}
      </nav>

      {/* Collapse button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center py-4 border-t border-[var(--color-surface-600)] text-slate-500 hover:text-slate-300 transition-colors"
      >
        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>
    </motion.aside>
  );
}
