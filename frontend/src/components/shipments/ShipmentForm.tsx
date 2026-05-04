import { useState } from "react";
import { useTranslation } from "react-i18next";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface Props {
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  onClose: () => void;
}

export function ShipmentForm({ onSubmit, onClose }: Props) {
  const { t } = useTranslation();
  const [form, setForm] = useState({
    recipient_name: "", recipient_phone: "", recipient_email: "",
    origin_address: "", origin_city: "",
    destination_address: "", destination_city: "",
    weight_kg: "", description: "", priority: "normal", is_fragile: false,
  });
  const [loading, setLoading] = useState(false);
  const set = (key: string, value: unknown) => setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit({ ...form, weight_kg: form.weight_kg ? Number(form.weight_kg) : undefined });
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white rounded-t-2xl z-10">
          <h2 className="text-lg font-bold">{t("shipments.createTitle")}</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
            <XMarkIcon className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Top accent */}
        <div className="h-1 bg-gradient-to-r from-brand-600 to-brand-400 -mt-px" />

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Recipient */}
          <fieldset>
            <legend className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center">1</span>
              {t("shipments.recipientSection")}
            </legend>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.name")} *</label>
                <input className="input" required value={form.recipient_name} onChange={(e) => set("recipient_name", e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.phone")} *</label>
                <input className="input" required value={form.recipient_phone} onChange={(e) => set("recipient_phone", e.target.value)} />
              </div>
              <div className="col-span-2">
                <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.email")}</label>
                <input className="input" type="email" value={form.recipient_email} onChange={(e) => set("recipient_email", e.target.value)} />
              </div>
            </div>
          </fieldset>

          {/* Origin */}
          <fieldset>
            <legend className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center">2</span>
              {t("shipments.originSection")}
            </legend>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.address")} *</label>
                <input className="input" required value={form.origin_address} onChange={(e) => set("origin_address", e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.city")} *</label>
                <input className="input" required value={form.origin_city} onChange={(e) => set("origin_city", e.target.value)} />
              </div>
            </div>
          </fieldset>

          {/* Destination */}
          <fieldset>
            <legend className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center">3</span>
              {t("shipments.destSection")}
            </legend>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.address")} *</label>
                <input className="input" required value={form.destination_address} onChange={(e) => set("destination_address", e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.city")} *</label>
                <input className="input" required value={form.destination_city} onChange={(e) => set("destination_city", e.target.value)} />
              </div>
            </div>
          </fieldset>

          {/* Package details */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.weight")}</label>
              <input className="input" type="number" step="0.1" value={form.weight_kg} onChange={(e) => set("weight_kg", e.target.value)} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.priority")}</label>
              <select className="input" value={form.priority} onChange={(e) => set("priority", e.target.value)}>
                {(["low", "normal", "high", "urgent"] as const).map((p) => (
                  <option key={p} value={p}>{t(`shipments.priorities.${p}`)}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end pb-2.5">
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer font-semibold">
                <input type="checkbox" checked={form.is_fragile} onChange={(e) => set("is_fragile", e.target.checked)} className="rounded accent-brand-600" />
                {t("shipments.fragile")}
              </label>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1">{t("shipments.description")}</label>
            <textarea className="input h-20 resize-none" value={form.description} onChange={(e) => set("description", e.target.value)} />
          </div>

          <div className="flex gap-3 justify-end pt-2 border-t">
            <button type="button" onClick={onClose} className="btn-secondary">{t("common.cancel")}</button>
            <button type="submit" disabled={loading} className="btn-primary shadow-lg shadow-brand-600/25">
              {loading ? t("shipments.creating") : t("shipments.createBtn")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
