import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { BuildingOfficeIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { Header } from "../components/layout/Header";
import api from "../services/api";
import { Company } from "../types";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import toast from "react-hot-toast";

export default function CompaniesPage() {
  const { t } = useTranslation();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", phone: "", city: "", country: "" });

  useEffect(() => {
    api.get("/companies").then((r) => setCompanies(r.data.items)).finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { data } = await api.post<Company>("/companies", form);
      setCompanies((c) => [data, ...c]);
      setShowForm(false);
      toast.success(t("companies.createSuccess"));
    } catch {
      toast.error(t("companies.createError"));
    }
  };

  const textFields = ["name", "city", "country"] as const;
  const allFields = ["name", "email", "phone", "city", "country"] as const;

  return (
    <div>
      <Header title={t("companies.title")} />
      <div className="p-6">
        <div className="flex justify-end mb-5">
          <button onClick={() => setShowForm(true)} className="btn-primary">
            {t("companies.addCompany")}
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-16"><LoadingSpinner size="lg" /></div>
        ) : (
          <div className="card p-0 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-100">
              <thead className="bg-gray-50">
                <tr>
                  {(["colName", "colEmail", "colCity", "colPlan", "colStatus", "colSince"] as const).map((h) => (
                    <th key={h} className="table-header">{t(`companies.${h}`)}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {companies.map((c) => (
                  <tr key={c.id} className="hover:bg-brand-50/30 transition-colors">
                    <td className="table-cell">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-brand-100 flex items-center justify-center shrink-0">
                          <BuildingOfficeIcon className="w-4 h-4 text-brand-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-sm">{c.name}</p>
                          <p className="text-xs text-gray-400">{c.phone}</p>
                        </div>
                      </div>
                    </td>
                    <td className="table-cell text-gray-500">{c.email}</td>
                    <td className="table-cell text-gray-500">{c.city}</td>
                    <td className="table-cell">
                      <span className="badge bg-brand-50 text-brand-700 capitalize">{c.subscription_plan}</span>
                    </td>
                    <td className="table-cell">
                      <span className={`badge ${c.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-400"}`}>
                        {c.is_active ? t("common.active") : t("common.inactive")}
                      </span>
                    </td>
                    <td className="table-cell text-xs text-gray-400">
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
                {companies.length === 0 && (
                  <tr><td colSpan={6} className="text-center py-14 text-gray-400">{t("companies.noCompanies")}</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-bold">{t("companies.createTitle")}</h2>
              <button onClick={() => setShowForm(false)} className="p-1.5 rounded-lg hover:bg-gray-100">
                <XMarkIcon className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <div className="h-1 bg-gradient-to-r from-brand-600 to-brand-400" />
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              {allFields.map((f) => (
                <div key={f}>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5">
                    {t(`companies.${f}`)} {f !== "phone" ? "*" : ""}
                  </label>
                  <input
                    className="input"
                    required={f !== "phone"}
                    type={f === "email" ? "email" : "text"}
                    value={form[f]}
                    onChange={(e) => setForm((prev) => ({ ...prev, [f]: e.target.value }))}
                  />
                </div>
              ))}
              <div className="flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">{t("common.cancel")}</button>
                <button type="submit" className="btn-primary">{t("common.create")}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
