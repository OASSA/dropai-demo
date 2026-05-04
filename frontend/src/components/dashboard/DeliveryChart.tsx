import { useTranslation } from "react-i18next";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { DeliveryTrendPoint } from "../../types";

interface Props {
  data: DeliveryTrendPoint[];
}

export function DeliveryChart({ data }: Props) {
  const { t } = useTranslation();
  const formatted = data.map((d) => ({
    ...d,
    date: d.date.slice(5),
  }));

  return (
    <div className="card">
      <h3 className="text-base font-bold text-gray-900 mb-5">{t("dashboard.deliveryTrend")}</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={formatted} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="gradDelivered" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#cc3318" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#cc3318" stopOpacity={0}    />
            </linearGradient>
            <linearGradient id="gradFailed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}   />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{ borderRadius: "12px", border: "1px solid #f0f0f0", fontSize: 12 }}
          />
          <Legend />
          <Area
            type="monotone" dataKey="delivered" name={t("shipments.statuses.delivered")}
            stroke="#cc3318" fill="url(#gradDelivered)" strokeWidth={2.5}
          />
          <Area
            type="monotone" dataKey="failed" name={t("shipments.statuses.failed")}
            stroke="#f59e0b" fill="url(#gradFailed)" strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
