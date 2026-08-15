import { Database, Radio, Cpu, UserCheck } from 'lucide-react';

/**
 * Badge that clearly distinguishes data source:
 * SIMULATED DATA / REAL DATA / MODEL OUTPUT / ENGINEERING RULE / DEMO ASSUMPTION
 */
const sourceConfig = {
  simulator: { label: 'SIMULATED', icon: Database, className: 'source-badge source-badge--simulator' },
  sensor: { label: 'REAL DATA', icon: Radio, className: 'source-badge source-badge--sensor' },
  vision_model: { label: 'MODEL OUTPUT', icon: Cpu, className: 'source-badge source-badge--model' },
  fuzzy_risk_engine: { label: 'MODEL OUTPUT', icon: Cpu, className: 'source-badge source-badge--model' },
  inferred: { label: 'INFERRED', icon: Cpu, className: 'source-badge source-badge--model' },
  operator_confirmed: { label: 'CONFIRMED', icon: UserCheck, className: 'source-badge source-badge--sensor' },
  manual_inspection: { label: 'MANUAL', icon: UserCheck, className: 'source-badge source-badge--sensor' },
};

export default function DataSourceBadge({ source }) {
  const config = sourceConfig[source] || sourceConfig.simulator;
  const Icon = config.icon;

  return (
    <span className={config.className}>
      <Icon size={10} />
      {config.label}
    </span>
  );
}
