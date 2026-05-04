import { useTranslation } from "react-i18next";
import { Shipment } from "../../types";
import { ShipmentStatusBadge } from "./ShipmentStatusBadge";
import { format } from "date-fns";

interface Props {
  shipments: Shipment[];
  onSelect: (s: Shipment) => void;
  isLoading: boolean;
}

export function ShipmentTable({ shipments, onSelect, isLoading }: Props) {
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className="card flex items-center justify-center h-48">
        <div className="animate-spin h-8 w-8 rounded-full border-2 border-gray-200 border-t-brand-600" />
      </div>
    );
  }

  return (
    <div className="card p-0 overflow-hidden">
      <table className="min-w-full divide-y divide-gray-100">
        <thead className="bg-gray-50">
          <tr>
            {(["tracking", "recipient", "route", "status", "priority", "eta", "created"] as const).map((h) => (
              <th key={h} className="table-header">{t(`shipments.${h}`)}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {shipments.length === 0 ? (
            <tr>
              <td colSpan={7} className="text-center py-14 text-gray-400">{t("shipments.noShipments")}</td>
            </tr>
          ) : (
            shipments.map((s) => (
              <tr
                key={s.id}
                className="hover:bg-brand-50/40 cursor-pointer transition-colors"
                onClick={() => onSelect(s)}
              >
                <td className="table-cell font-mono text-brand-600 font-semibold text-xs">{s.tracking_number}</td>
                <td className="table-cell">
                  <div className="font-semibold text-gray-900">{s.recipient_name}</div>
                  <div className="text-xs text-gray-400">{s.recipient_phone}</div>
                </td>
                <td className="table-cell text-gray-600">
                  <div className="text-xs text-gray-400">{s.origin_city}</div>
                  <div className="text-xs font-semibold">→ {s.destination_city}</div>
                </td>
                <td className="table-cell"><ShipmentStatusBadge status={s.status} /></td>
                <td className="table-cell">
                  <span className={`badge text-xs ${
                    s.priority === "urgent" ? "bg-red-100 text-red-700"
                    : s.priority === "high"   ? "bg-orange-100 text-orange-700"
                    : "bg-gray-100 text-gray-600"
                  }`}>
                    {t(`shipments.priorities.${s.priority}`)}
                  </span>
                </td>
                <td className="table-cell text-xs text-gray-500">
                  {s.predicted_eta ? format(new Date(s.predicted_eta), "MMM d, HH:mm") : "—"}
                </td>
                <td className="table-cell text-xs text-gray-400">
                  {format(new Date(s.created_at), "MMM d, yyyy")}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
