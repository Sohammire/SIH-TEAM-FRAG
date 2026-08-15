import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * A dashboard stat card with value, label, icon, and optional trend.
 */
export default function StatCard({ label, value, icon: Icon, color = 'blue', trend, suffix, delay = 0 }) {
  const colorMap = {
    blue: 'from-blue-500/20 to-blue-600/5 border-blue-500/20 text-blue-400',
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20 text-emerald-400',
    amber: 'from-amber-500/20 to-amber-600/5 border-amber-500/20 text-amber-400',
    red: 'from-red-500/20 to-red-600/5 border-red-500/20 text-red-400',
    violet: 'from-violet-500/20 to-violet-600/5 border-violet-500/20 text-violet-400',
    cyan: 'from-cyan-500/20 to-cyan-600/5 border-cyan-500/20 text-cyan-400',
    slate: 'from-slate-500/20 to-slate-600/5 border-slate-500/20 text-slate-400',
  };

  const iconBgMap = {
    blue: 'bg-blue-500/15 text-blue-400',
    emerald: 'bg-emerald-500/15 text-emerald-400',
    amber: 'bg-amber-500/15 text-amber-400',
    red: 'bg-red-500/15 text-red-400',
    violet: 'bg-violet-500/15 text-violet-400',
    cyan: 'bg-cyan-500/15 text-cyan-400',
    slate: 'bg-slate-500/15 text-slate-400',
  };

  const TrendIcon = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus;
  const trendColor = trend > 0 ? 'text-emerald-400' : trend < 0 ? 'text-red-400' : 'text-slate-500';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.05 }}
      className={`card bg-gradient-to-br ${colorMap[color]} border`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">{label}</p>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-white">{value}</span>
            {suffix && <span className="text-sm text-slate-400">{suffix}</span>}
          </div>
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-lg ${iconBgMap[color]}`}>
            <Icon size={20} />
          </div>
        )}
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 mt-2 text-xs ${trendColor}`}>
          <TrendIcon size={12} />
          <span>{Math.abs(trend)}% from last shift</span>
        </div>
      )}
    </motion.div>
  );
}
