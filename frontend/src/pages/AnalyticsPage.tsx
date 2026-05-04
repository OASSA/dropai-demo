import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Header } from "../components/layout/Header";
import { DeliveryChart } from "../components/dashboard/DeliveryChart";
import { dashboardService } from "../services/dashboardService";
import { DashboardStats } from "../types";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar,
} from "recharts";

const PIE_COLORS = ["#cc3318", "#22c55e", "#f59e0b", "#ef4444", "#6b7280"];

export default function AnalyticsPage() {
  const { t } = useTranslation();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService.getStats().then(setStats).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-24"><LoadingSpinner size="lg" /></div>;
  if (!stats) return null;

  const pieData = [
    { name: t("shipments.statuses.delivered"), value: stats.shipments.delivered },
    { name: t("shipments.statuses.in_transit"), value: stats.shipments.in_transit },
    { name: t("shipments.statuses.pending"),    value: stats.shipments.pending },
    { name: t("shipments.statuses.failed"),     value: stats.shipments.failed },
    { name: t("shipments.statuses.cancelled"),  value: stats.shipments.cancelled },
  ].filter((d) => d.value > 0);

  const radialData = [
    {
      name: t("analytics.deliveryRate"),
      value: stats.shipments.delivery_success_rate,
      fill: "#cc3318",
    },
    {
      name: t("analytics.availableNow"),
      value: stats.drivers.total_drivers > 0
        ? Math.round((stats.drivers.available / stats.drivers.total_drivers) * 100)
        : 0,
      fill: "#22c55e",
    },
  ];

  const summaryItems = [
    { label: t("analytics.totalShipments"), value: stats.shipments.total },
    { label: t("analytics.deliveryRate"),   value: `${stats.shipments.delivery_success_rate}%` },
    { label: t("analytics.totalDrivers"),   value: stats.drivers.total_drivers },
    { label: t("analytics.availableNow"),   value: stats.drivers.available },
  ];

  return (
    <div>
      <Header title={t("analytics.title")} />
      <div className="p-6 space-y-6">
        <div className="grid lg:grid-cols-2 gap-5">
          {/* Pie */}
          <div className="card">
            <h3 className="text-base font-bold text-gray-900 mb-5">{t("analytics.distribution")}</h3>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={pieData} cx="50%" cy="50%" outerRadius={95} dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: "12px", fontSize: 12 }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400 text-center py-16">{t("analytics.noData")}</p>
            )}
          </div>

          {/* Radial KPIs */}
          <div className="card">
            <h3 className="text-base font-bold text-gray-900 mb-5">{t("analytics.kpi")}</h3>
            <ResponsiveContainer width="100%" height={280}>
              <RadialBarChart
                cx="50%" cy="50%" innerRadius="25%" outerRadius="85%"
                data={radialData} startAngle={180} endAngle={-180}
              >
                <RadialBar
                  label={{ position: "insideStart", fill: "#fff", fontSize: 11, fontWeight: "bold" }}
                  dataKey="value"
                  cornerRadius={6}
                />
                <Legend />
                <Tooltip formatter={(v: number) => `${v.toFixed(1)}%`} />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <DeliveryChart data={stats.delivery_trend} />

        {/* Summary grid */}
        <div className="card">
          <h3 className="text-base font-bold text-gray-900 mb-5">{t("analytics.summary")}</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {summaryItems.map((item) => (
              <div key={item.label} className="bg-gradient-to-br from-brand-50 to-orange-50 border border-brand-100 rounded-2xl p-5 text-center">
                <div className="text-3xl font-extrabold text-brand-600">{item.value}</div>
                <div className="text-xs text-gray-500 mt-1 font-semibold">{item.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
