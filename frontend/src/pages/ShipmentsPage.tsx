import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Header } from "../components/layout/Header";
import { ShipmentTable } from "../components/shipments/ShipmentTable";
import { ShipmentForm } from "../components/shipments/ShipmentForm";
import { useShipmentStore } from "../store/shipmentStore";
import { Shipment } from "../types";
import { ShipmentStatusBadge } from "../components/shipments/ShipmentStatusBadge";
import { format } from "date-fns";
import toast from "react-hot-toast";
import { useAuthStore } from "../store/authStore";

const STATUS_FILTER_KEYS = ["all", "pending", "assigned", "in_transit", "delivered", "failed"] as const;

export default function ShipmentsPage() {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const { shipments, total, isLoading, fetchShipments, createShipment } = useShipmentStore();
  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState<Shipment | null>(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);

  const canCreate = user && ["super_admin", "company_admin", "warehouse_manager"].includes(user.role.name);

  useEffect(() => {
    fetchShipments(page, statusFilter === "all" ? undefined : statusFilter);
  }, [page, statusFilter]);

  const handleCreate = async (data: Record<string, unknown>) => {
    await createShipment(data as Partial<Shipment>);
    toast.success(t("shipments.createdSuccess"));
  };

  return (
    <div>
      <Header title={t("shipments.title")} />
      <div className="p-6 space-y-4">
        {/* Filters + action */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex gap-2 flex-wrap">
            {STATUS_FILTER_KEYS.map((s) => (
              <button
                key={s}
                onClick={() => { setStatusFilter(s); setPage(1); }}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold capitalize transition-colors ${
                  statusFilter === s
                    ? "bg-brand-600 text-white shadow-sm"
                    : "bg-white text-gray-600 border border-gray-200 hover:border-brand-300 hover:text-brand-600"
                }`}
              >
                {t(`shipments.statuses.${s}`)}
              </button>
            ))}
          </div>
          {canCreate && (
            <button onClick={() => setShowForm(true)} className="btn-primary">
              {t("shipments.newShipment")}
            </button>
          )}
        </div>

        <p className="text-xs text-gray-400">{total} {t("shipments.totalCount")}</p>

        <ShipmentTable shipments={shipments} onSelect={setSelected} isLoading={isLoading} />

        {/* Pagination */}
        <div className="flex items-center justify-end gap-3">
          <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-40">
            ← {t("common.prev")}
          </button>
          <span className="text-xs text-gray-500">{t("common.page")} {page}</span>
          <button disabled={shipments.length < 20} onClick={() => setPage((p) => p + 1)} className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-40">
            {t("common.next")} →
          </button>
        </div>
      </div>

      {showForm && <ShipmentForm onSubmit={handleCreate} onClose={() => setShowForm(false)} />}

      {/* Detail modal */}
      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" onClick={() => setSelected(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-brand-600 font-bold text-lg">{selected.tracking_number}</span>
              <ShipmentStatusBadge status={selected.status} />
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm mb-4">
              <div><span className="text-gray-400">{t("shipments.recipient")}:</span> <span className="font-semibold">{selected.recipient_name}</span></div>
              <div><span className="text-gray-400">{t("shipments.phone")}:</span> {selected.recipient_phone}</div>
              <div className="col-span-2">
                <span className="text-gray-400">{t("shipments.from")}:</span> {selected.origin_city} →{" "}
                <strong>{selected.destination_city}</strong>
              </div>
              <div><span className="text-gray-400">{t("shipments.priority")}:</span> <span className="capitalize">{t(`shipments.priorities.${selected.priority}`)}</span></div>
              {selected.weight_kg && (
                <div><span className="text-gray-400">{t("shipments.weight")}:</span> {selected.weight_kg} {t("shipments.km")}</div>
              )}
              {selected.predicted_eta && (
                <div className="col-span-2">
                  <span className="text-gray-400">{t("shipments.predictedETA")}:</span>{" "}
                  {format(new Date(selected.predicted_eta), "PPpp")}
                </div>
              )}
              {selected.predicted_distance_km && (
                <div><span className="text-gray-400">{t("shipments.distance")}:</span> {selected.predicted_distance_km} {t("shipments.km")}</div>
              )}
            </div>

            {selected.tracking_logs && selected.tracking_logs.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="text-sm font-bold mb-3">{t("shipments.trackingHistory")}</h3>
                <div className="space-y-2.5 max-h-44 overflow-y-auto pe-1">
                  {[...selected.tracking_logs].reverse().map((log) => (
                    <div key={log.id} className="flex items-start gap-2.5 text-xs">
                      <div className="w-2 h-2 rounded-full bg-brand-600 mt-1 shrink-0" />
                      <div>
                        <span className="font-semibold capitalize">{t(`shipments.statuses.${log.status}`)}</span>
                        {log.message && <span className="text-gray-400"> — {log.message}</span>}
                        <div className="text-gray-300">{format(new Date(log.created_at), "MMM d, HH:mm")}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <button onClick={() => setSelected(null)} className="btn-secondary w-full justify-center mt-4">
              {t("common.close")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
