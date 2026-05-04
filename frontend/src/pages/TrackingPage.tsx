import { useState } from "react";
import { useTranslation } from "react-i18next";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";
import { shipmentService } from "../services/shipmentService";
import { Shipment } from "../types";
import { ShipmentStatusBadge } from "../components/shipments/ShipmentStatusBadge";
import { LogoFull } from "../components/common/Logo";
import { LanguageSwitcher } from "../components/common/LanguageSwitcher";
import { format } from "date-fns";

export default function TrackingPage() {
  const { t } = useTranslation();
  const [tracking, setTracking] = useState("");
  const [result, setResult] = useState<Shipment | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tracking.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await shipmentService.track(tracking.trim());
      setResult(data);
    } catch {
      setError(t("tracking.notFound"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-orange-50 flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white/90 backdrop-blur border-b border-gray-100">
        <Link to="/">
          <LogoFull iconSize={36} textSize="md" />
        </Link>
        <div className="flex items-center gap-3">
          <LanguageSwitcher />
          <Link to="/login" className="btn-secondary text-sm">{t("tracking.signIn")}</Link>
        </div>
      </nav>

      {/* Main */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        {/* Icon */}
        <div className="w-16 h-16 rounded-2xl bg-brand-600 flex items-center justify-center text-3xl mb-6 shadow-lg shadow-brand-600/30">
          📦
        </div>
        <h1 className="text-3xl font-extrabold text-gray-900 mb-2 text-center">{t("tracking.title")}</h1>
        <p className="text-gray-500 mb-8 text-center max-w-md">{t("tracking.subtitle")}</p>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex gap-3 w-full max-w-lg mb-6">
          <input
            className="input flex-1 text-base font-mono"
            placeholder={t("tracking.placeholder")}
            value={tracking}
            onChange={(e) => setTracking(e.target.value)}
            dir="ltr"
          />
          <button type="submit" disabled={loading} className="btn-primary px-5 shadow-lg shadow-brand-600/25">
            {loading ? (
              <div className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
            ) : (
              <MagnifyingGlassIcon className="w-5 h-5" />
            )}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-5 py-3.5 text-red-700 text-sm max-w-lg w-full text-center font-semibold">
            {error}
          </div>
        )}

        {/* Result card */}
        {result && (
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 mt-2 border border-gray-100">
            <div className="h-1 -mt-6 -mx-6 mb-5 rounded-t-2xl bg-gradient-to-r from-brand-600 to-brand-400" />
            <div className="flex items-center justify-between mb-5">
              <span className="font-mono text-brand-600 font-bold text-base">{result.tracking_number}</span>
              <ShipmentStatusBadge status={result.status} />
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm mb-5">
              <div>
                <span className="text-gray-400 text-xs">{t("tracking.from")}</span>
                <p className="font-semibold">{result.origin_city}</p>
              </div>
              <div>
                <span className="text-gray-400 text-xs">{t("tracking.to")}</span>
                <p className="font-semibold">{result.destination_city}</p>
              </div>
              <div>
                <span className="text-gray-400 text-xs">{t("tracking.recipient")}</span>
                <p className="font-semibold">{result.recipient_name}</p>
              </div>
              {result.predicted_eta && (
                <div>
                  <span className="text-gray-400 text-xs">{t("tracking.eta")}</span>
                  <p className="font-semibold">{format(new Date(result.predicted_eta), "PPp")}</p>
                </div>
              )}
            </div>

            {result.actual_delivery && (
              <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3 text-green-700 text-sm font-semibold mb-4">
                ✅ {t("tracking.deliveredOn")} {format(new Date(result.actual_delivery), "PPp")}
              </div>
            )}

            {result.tracking_logs && result.tracking_logs.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="text-sm font-bold mb-4">{t("tracking.history")}</h3>
                <ol className="relative border-s border-brand-200 ms-2 space-y-4">
                  {[...result.tracking_logs].reverse().map((log) => (
                    <li key={log.id} className="ms-4">
                      <div className="absolute -start-1.5 w-3 h-3 rounded-full bg-brand-600 border-2 border-white" />
                      <div className="text-xs font-bold capitalize">{log.status.replace("_", " ")}</div>
                      {log.message && <div className="text-xs text-gray-500">{log.message}</div>}
                      <div className="text-xs text-gray-300 mt-0.5">
                        {format(new Date(log.created_at), "PPp")}
                      </div>
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
