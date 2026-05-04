import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../store/authStore";
import { LogoFullWhite } from "../common/Logo";
import { LanguageSwitcher } from "../common/LanguageSwitcher";
import {
  HomeIcon, TruckIcon, BuildingOfficeIcon, UserGroupIcon,
  BuildingStorefrontIcon, BellIcon, ChartBarIcon, ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";

const navKeys = [
  { key: "dashboard",     href: "/dashboard",     icon: HomeIcon,                roles: ["super_admin","company_admin","warehouse_manager","driver"] },
  { key: "shipments",     href: "/shipments",     icon: TruckIcon,               roles: ["super_admin","company_admin","warehouse_manager","driver"] },
  { key: "drivers",       href: "/drivers",       icon: UserGroupIcon,           roles: ["super_admin","company_admin","warehouse_manager"] },
  { key: "warehouses",    href: "/warehouses",    icon: BuildingStorefrontIcon,  roles: ["super_admin","company_admin","warehouse_manager"] },
  { key: "companies",     href: "/companies",     icon: BuildingOfficeIcon,      roles: ["super_admin"] },
  { key: "analytics",     href: "/analytics",     icon: ChartBarIcon,            roles: ["super_admin","company_admin"] },
  { key: "notifications", href: "/notifications", icon: BellIcon,                roles: ["super_admin","company_admin","warehouse_manager","driver"] },
];

export function Sidebar() {
  const { t } = useTranslation();
  const { user, logout } = useAuthStore();
  const role = user?.role.name;
  const filtered = navKeys.filter((item) => role && item.roles.includes(role));

  return (
    <aside className="flex flex-col w-64 min-h-screen bg-gray-950 text-white shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10">
        <LogoFullWhite iconSize={34} textSize="md" />
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {filtered.map(({ key, href, icon: Icon }) => (
          <NavLink
            key={href}
            to={href}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 ${
                isActive
                  ? "bg-brand-600 text-white shadow-md shadow-brand-900/30"
                  : "text-gray-300 hover:bg-white/8 hover:text-white"
              }`
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {t(`nav.${key}`)}
          </NavLink>
        ))}
      </nav>

      {/* Bottom: lang switcher + user */}
      <div className="px-3 pb-4 border-t border-white/10 pt-3 space-y-2">
        <div className="px-1">
          <LanguageSwitcher variant="dark" />
        </div>
        <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-white/5">
          <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-xs font-bold shrink-0">
            {user?.first_name[0]}{user?.last_name[0]}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-gray-400 truncate">{role?.replace("_", " ")}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-xl text-sm text-gray-400 hover:bg-white/8 hover:text-white transition-colors"
        >
          <ArrowRightOnRectangleIcon className="w-5 h-5 rtl-flip" />
          {t("nav.signOut")}
        </button>
      </div>
    </aside>
  );
}
