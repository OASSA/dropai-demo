interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  color?: "red" | "green" | "blue" | "orange" | "purple";
  trend?: { value: number; label: string };
}

const colorMap = {
  red:    { ring: "bg-brand-100",  icon: "text-brand-600"  },
  green:  { ring: "bg-green-100",  icon: "text-green-600"  },
  blue:   { ring: "bg-blue-100",   icon: "text-blue-600"   },
  orange: { ring: "bg-orange-100", icon: "text-orange-600" },
  purple: { ring: "bg-purple-100", icon: "text-purple-600" },
};

export function StatsCard({ title, value, subtitle, icon: Icon, color = "red", trend }: Props) {
  const c = colorMap[color];
  return (
    <div className="card flex items-start gap-4 hover:shadow-md transition-shadow">
      <div className={`${c.ring} rounded-xl p-3 shrink-0`}>
        <Icon className={`w-6 h-6 ${c.icon}`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide">{title}</p>
        <p className="text-2xl font-extrabold text-gray-900 mt-0.5">{value}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
        {trend && (
          <p className={`text-xs mt-1 font-semibold ${trend.value >= 0 ? "text-green-600" : "text-red-600"}`}>
            {trend.value >= 0 ? "↑" : "↓"} {Math.abs(trend.value)}% {trend.label}
          </p>
        )}
      </div>
    </div>
  );
}
