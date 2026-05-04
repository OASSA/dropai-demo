import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { BuildingStorefrontIcon, MapPinIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { Header } from "../components/layout/Header";
import api from "../services/api";
import { Warehouse } from "../types";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import toast from "react-hot-toast";

export default function WarehousesPage() {
  const { t } = useTranslation();
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", code: "", address: "", city: "", country: "" });

  useEffect(() => {
    api.get("/warehouses").then((r) => setWarehouses(r.data.items)).finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { data } = await api.post<Warehouse>("/warehouses", form);
      setWarehouses((w) => [data, ...w]);
      setShowForm(false);
      setForm({ name: "", code: "", address: "", city: "", country: "" });
      toast.success(t("warehouses.createSuccess"));
    } catch {
      toast.error(t("warehouses.createError"));
    }
  };

  const fields = ["name", "code", "address", "city", "country"] as const;

  return (
    <div>
      <Header title={t("warehouses.title")} />
      <div className="p-6">
        <div className="flex justify-end mb-5">
          <button onClick={() => setShowForm(true)} className="btn-primary">
            {t("warehouses.addWarehouse")}
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-16"><LoadingSpinner size="lg" /></div>
        ) : (
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {warehouses.map((w) => (
              <div key={w.id} className="card hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-11 h-11 rounded-xl bg-brand-100 flex items-center justify-center">
                    <BuildingStorefrontIcon className="w-6 h-6 text-brand-600" />
                  </div>
                  <span className={`badge ${w.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                    {w.is_active ? t("common.active") : t("common.inactive")}
                  </span>
                </div>
                <h3 className="font-bold text-gray-900 text-base">{w.name}</h3>
                <p className="text-xs font-mono text-brand-600 mt-0.5">{w.code}</p>
                <div className="flex items-center gap-1.5 mt-3 text-sm text-gray-500">
                  <MapPinIcon className="w-4 h-4 text-brand-400 shrink-0" />
                  {w.city}, {w.country}
                </div>
                <p className="text-xs text-gray-400 mt-1 leading-relaxed">{w.address}</p>
                {w.capacity && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-xs text-gray-500">
                      {t("warehouses.capacity")}: <strong>{w.capacity.toLocaleString()}</strong> {t("warehouses.capacityUnit")}
                    </p>
                  </div>
                )}
              </div>
            ))}
            {warehouses.length === 0 && (
              <div className="col-span-3 text-center py-16 text-gray-400">{t("warehouses.noWarehouses")}</div>
            )}
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-bold">{t("warehouses.createTitle")}</h2>
              <button onClick={() => setShowForm(false)} className="p-1.5 rounded-lg hover:bg-gray-100">
                <XMarkIcon className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <div className="h-1 bg-gradient-to-r from-brand-600 to-brand-400" />
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              {fields.map((field) => (
                <div key={field}>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5 capitalize">
                    {t(`warehouses.${field}`)} *
                  </label>
                  <input
                    className="input"
                    required
                    value={form[field]}
                    onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
                  />
                </div>
              ))}
              <div className="flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">{t("common.cancel")}</button>
                <button type="submit" className="btn-primary">{t("warehouses.create")}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
