import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  TruckIcon, CheckCircleIcon, ExclamationCircleIcon,
  UserGroupIcon, ClockIcon,
} from "@heroicons/react/24/outline";
import { Header } from "../components/layout/Header";
import { StatsCard } from "../components/dashboard/StatsCard";
import { DeliveryChart } from "../components/dashboard/DeliveryChart";
import { dashboardService } from "../services/dashboardService";
import { DashboardStats } from "../types";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { useAuthStore } from "../store/authStore";
import { format } from "date-fns";

export default function DashboardPage() {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<{ id: number; action: string; description: string; timestamp: string }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([dashboardService.getStats(), dashboardService.getActivity(8)])
      .then(([s, a]) => { setStats(s); setActivity(a); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      <Header title={t("dashboard.title")} />
      <div className="p-6 space-y-6">
        {/* Welcome banner */}
        <div className="bg-gradient-to-r from-brand-600 to-brand-700 rounded-2xl p-6 text-white">
          <h2 className="text-xl font-bold mb-1">
            {t("dashboard.greeting")} {user?.first_name} 👋
          </h2>
          <p className="text-brand-100 text-sm">{t("dashboard.greetingDesc")}</p>
        </div>

        {/* KPI Cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatsCard
              title={t("dashboard.totalShipments")}
              value={stats.shipments.total.toLocaleString()}
              icon={TruckIcon}
              color="red"
              subtitle={`${stats.shipments.in_transit} ${t("dashboard.inTransit")}`}
            />
            <StatsCard
              title={t("dashboard.delivered")}
              value={stats.shipments.delivered.toLocaleString()}
              icon={CheckCircleIcon}
              color="green"
              subtitle={`${stats.shipments.delivery_success_rate}% ${t("dashboard.successRate")}`}
            />
            <StatsCard
              title={t("dashboard.failedCancelled")}
              value={(stats.shipments.failed + stats.shipments.cancelled).toLocaleString()}
              icon={ExclamationCircleIcon}
              color="orange"
              subtitle={`${stats.shipments.failed} ${t("dashboard.failedCount")}`}
            />
            <StatsCard
              title={t("dashboard.activeDrivers")}
              value={stats.drivers.on_delivery}
              icon={UserGroupIcon}
              color="blue"
              subtitle={`${stats.drivers.available} ${t("dashboard.available")}`}
            />
          </div>
        )}

        {/* Chart + Activity feed */}
        <div className="grid lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2">
            {stats && <DeliveryChart data={stats.delivery_trend} />}
          </div>

          <div className="card">
            <h3 className="text-base font-bold text-gray-900 mb-4">{t("dashboard.recentActivity")}</h3>
            <div className="space-y-3">
              {activity.length === 0 && (
                <p className="text-sm text-gray-400">{t("dashboard.noActivity")}</p>
              )}
              {activity.map((a) => (
                <div key={a.id} className="flex items-start gap-3">
                  <div className="w-7 h-7 rounded-full bg-brand-50 flex items-center justify-center flex-shrink-0 mt-0.5 border border-brand-100">
                    <ClockIcon className="w-3.5 h-3.5 text-brand-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-gray-800 truncate">
                      {a.action.replace(/_/g, " ")}
                    </p>
                    <p className="text-xs text-gray-400 truncate">{a.description}</p>
                    <p className="text-xs text-gray-300 mt-0.5">
                      {format(new Date(a.timestamp), "MMM d, HH:mm")}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top performer */}
        {stats?.drivers.top_performer_name && (
          <div className="card border-brand-100 bg-gradient-to-r from-brand-50 to-orange-50">
            <h3 className="text-base font-bold text-gray-900 mb-3">{t("dashboard.topPerformer")}</h3>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-brand-600 flex items-center justify-center text-2xl shadow-md shadow-brand-600/30">
                🏆
              </div>
              <div>
                <p className="font-bold text-gray-900">{stats.drivers.top_performer_name}</p>
                <p className="text-sm text-gray-500">
                  {t("dashboard.performanceScore")}:{" "}
                  <strong className="text-brand-600">{stats.drivers.top_performer_score?.toFixed(1)}</strong>/100
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
