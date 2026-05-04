import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Header } from "../components/layout/Header";
import api from "../services/api";
import { format } from "date-fns";
import { BellIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

const typeStyle: Record<string, { bg: string; dot: string }> = {
  info:            { bg: "bg-blue-50 border-blue-100",     dot: "bg-blue-500"    },
  success:         { bg: "bg-green-50 border-green-100",   dot: "bg-green-500"   },
  warning:         { bg: "bg-yellow-50 border-yellow-100", dot: "bg-yellow-500"  },
  error:           { bg: "bg-red-50 border-red-100",       dot: "bg-red-500"     },
  assignment:      { bg: "bg-brand-50 border-brand-100",   dot: "bg-brand-600"   },
  delay_alert:     { bg: "bg-orange-50 border-orange-100", dot: "bg-orange-500"  },
  shipment_update: { bg: "bg-purple-50 border-purple-100", dot: "bg-purple-500"  },
  system:          { bg: "bg-gray-50 border-gray-100",     dot: "bg-gray-400"    },
};

export default function NotificationsPage() {
  const { t } = useTranslation();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadOnly, setUnreadOnly] = useState(false);

  const fetchNotifications = () => {
    setLoading(true);
    api.get("/notifications", { params: { unread_only: unreadOnly } })
      .then((r) => setNotifications(r.data.items))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchNotifications(); }, [unreadOnly]);

  const markAllRead = async () => {
    await api.put("/notifications/mark-all-read");
    fetchNotifications();
    toast.success(t("notifications.allMarked"));
  };

  const markRead = async (id: number) => {
    await api.put(`/notifications/${id}/read`);
    setNotifications((n) => n.map((notif) => notif.id === id ? { ...notif, is_read: true } : notif));
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div>
      <Header title={t("notifications.title")} />
      <div className="p-6">
        <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer font-semibold">
              <input
                type="checkbox"
                checked={unreadOnly}
                onChange={(e) => setUnreadOnly(e.target.checked)}
                className="rounded accent-brand-600"
              />
              {t("notifications.unreadOnly")}
            </label>
            {unreadCount > 0 && (
              <span className="badge bg-brand-100 text-brand-700">
                {unreadCount} {t("notifications.unreadBadge")}
              </span>
            )}
          </div>
          {unreadCount > 0 && (
            <button onClick={markAllRead} className="btn-secondary text-xs">
              {t("notifications.markAllRead")}
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="animate-spin h-8 w-8 rounded-full border-2 border-gray-200 border-t-brand-600" />
          </div>
        ) : (
          <div className="space-y-2.5 max-w-2xl">
            {notifications.length === 0 && (
              <div className="text-center py-20 text-gray-300">
                <BellIcon className="w-14 h-14 mx-auto mb-3" />
                <p className="text-gray-400 font-semibold">{t("notifications.noNotifications")}</p>
              </div>
            )}
            {notifications.map((n) => {
              const style = typeStyle[n.type] ?? typeStyle.info;
              return (
                <div
                  key={n.id}
                  onClick={() => !n.is_read && markRead(n.id)}
                  className={`flex items-start gap-4 border rounded-2xl p-4 cursor-pointer transition-all duration-150
                    ${style.bg} ${n.is_read ? "opacity-55" : "hover:shadow-sm"}`}
                >
                  <div className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${n.is_read ? "bg-gray-300" : style.dot}`} />
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-semibold ${n.is_read ? "text-gray-500" : "text-gray-900"}`}>{n.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{n.message}</p>
                  </div>
                  <div className="text-xs text-gray-400 shrink-0">
                    {format(new Date(n.created_at), "MMM d, HH:mm")}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
