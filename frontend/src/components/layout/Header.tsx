import { BellIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "react-i18next";
import { LanguageSwitcher } from "../common/LanguageSwitcher";
import { useAuthStore } from "../../store/authStore";

interface Props {
  title: string;
}

export function Header({ title }: Props) {
  const { user } = useAuthStore();
  const { t } = useTranslation();

  return (
    <header className="flex items-center justify-between h-16 px-6 bg-white border-b border-gray-100 sticky top-0 z-10">
      <h1 className="text-xl font-bold text-gray-900">{title}</h1>
      <div className="flex items-center gap-2.5">
        <div className="relative hidden md:block">
          <MagnifyingGlassIcon className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={t("common.search")}
            className="ps-9 pe-4 py-1.5 text-sm rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-500 w-52"
          />
        </div>
        <LanguageSwitcher />
        <button className="relative p-2 rounded-xl hover:bg-gray-100 text-gray-500 transition-colors">
          <BellIcon className="w-5 h-5" />
          <span className="absolute top-1.5 end-1.5 w-2 h-2 rounded-full bg-brand-600" />
        </button>
        <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-xs font-bold text-white">
          {user?.first_name[0]}{user?.last_name[0]}
        </div>
      </div>
    </header>
  );
}
