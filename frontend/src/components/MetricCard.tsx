import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    variant: 'success' | 'danger' | 'warning' | 'info' | 'neutral';
  };
  accentColor?: 'cyan' | 'blue' | 'emerald' | 'amber' | 'rose';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  accentColor = 'cyan',
}) => {
  const getAccentBorder = () => {
    switch (accentColor) {
      case 'emerald':
        return 'border-emerald-500/30 hover:border-emerald-500/50';
      case 'amber':
        return 'border-amber-500/30 hover:border-amber-500/50';
      case 'rose':
        return 'border-rose-500/30 hover:border-rose-500/50';
      case 'blue':
        return 'border-blue-500/30 hover:border-blue-500/50';
      case 'cyan':
      default:
        return 'border-cyan-500/30 hover:border-cyan-500/50';
    }
  };

  const getIconColor = () => {
    switch (accentColor) {
      case 'emerald':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'amber':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'rose':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'blue':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'cyan':
      default:
        return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20';
    }
  };

  const getBadgeStyle = () => {
    if (!badge) return '';
    switch (badge.variant) {
      case 'success':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'danger':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'warning':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'info':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div
      className={`bg-slate-900/80 backdrop-blur border rounded-xl p-5 shadow-lg transition-all duration-200 ${getAccentBorder()}`}
    >
      <div className="flex items-start justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2 rounded-lg border ${getIconColor()}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">
          {value}
        </span>
        {badge && (
          <span
            className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${getBadgeStyle()}`}
          >
            {badge.text}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-400 flex items-center gap-1">
          {subtitle}
        </p>
      )}
    </div>
  );
};
