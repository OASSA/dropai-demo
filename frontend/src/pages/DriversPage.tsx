import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Header } from "../components/layout/Header";
import { driverService } from "../services/driverService";
import { Driver } from "../types";
import { LoadingSpinner } from "../components/common/LoadingSpinner";

const statusColor: Record<string, string> = {
  available:   "bg-green-100 text-green-700",
  on_delivery: "bg-blue-100 text-blue-700",
  off_duty:    "bg-gray-100 text-gray-500",
  suspended:   "bg-red-100 text-red-700",
};

const vehicleEmoji: Record<string, string> = {
  motorcycle: "🏍️", car: "🚗", van: "🚐", truck: "🚛",
};

export default function DriversPage() {
  const { t } = useTranslation();
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    driverService.list(page).then((r) => {
      setDrivers(r.items);
      setTotal(r.total);
    }).finally(() => setLoading(false));
  }, [page]);

  return (
    <div>
      <Header title={t("drivers.title")} />
      <div className="p-6">
        <p className="text-sm text-gray-400 mb-5">{total} {t("drivers.totalDrivers")}</p>

        {loading ? (
          <div className="flex justify-center py-16"><LoadingSpinner size="lg" /></div>
        ) : (
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {drivers.map((d) => (
              <div key={d.id} className="card hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
                <div className="flex items-start justify-between mb-4">
                  <span className="text-3xl">{vehicleEmoji[d.vehicle_type] ?? "🚗"}</span>
                  <span className={`badge ${statusColor[d.status]}`}>
                    {t(`drivers.statuses.${d.status}`)}
                  </span>
                </div>
                <p className="font-bold text-gray-900 text-base">{d.license_number}</p>
                <p className="text-sm text-gray-500">{d.vehicle_model || d.vehicle_type} • {d.vehicle_plate}</p>

                <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                  <div className="bg-gray-50 rounded-xl p-2.5">
                    <p className="text-lg font-extrabold text-gray-900">{d.total_deliveries}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{t("drivers.deliveries")}</p>
                  </div>
                  <div className="bg-green-50 rounded-xl p-2.5">
                    <p className="text-lg font-extrabold text-green-600">{d.success_rate}%</p>
                    <p className="text-xs text-gray-400 mt-0.5">{t("dashboard.successRate")}</p>
                  </div>
                  <div className="bg-brand-50 rounded-xl p-2.5">
                    <p className="text-lg font-extrabold text-brand-600">{d.performance_score.toFixed(0)}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{t("drivers.score")}</p>
                  </div>
                </div>

                {/* Performance bar */}
                <div className="mt-4">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="text-gray-500 font-semibold">{t("drivers.performance")}</span>
                    <span className="font-bold text-brand-600">{d.performance_score.toFixed(1)}/100</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-600 to-brand-400 rounded-full transition-all duration-500"
                      style={{ width: `${d.performance_score}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
            {drivers.length === 0 && (
              <div className="col-span-3 text-center py-16 text-gray-400">{t("drivers.noDrivers")}</div>
            )}
          </div>
        )}

        <div className="flex justify-end gap-3 mt-6">
          <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-40">
            ← {t("common.prev")}
          </button>
          <span className="text-xs text-gray-500 self-center">{t("common.page")} {page}</span>
          <button disabled={drivers.length < 20} onClick={() => setPage((p) => p + 1)} className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-40">
            {t("common.next")} →
          </button>
        </div>
      </div>
    </div>
  );
}
