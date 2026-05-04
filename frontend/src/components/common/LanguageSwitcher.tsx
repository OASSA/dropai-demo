import { useTranslation } from "react-i18next";

interface Props {
  variant?: "light" | "dark";
}

export function LanguageSwitcher({ variant = "light" }: Props) {
  const { i18n } = useTranslation();
  const isAr = i18n.language === "ar";

  const toggle = () => i18n.changeLanguage(isAr ? "en" : "ar");

  const baseClass =
    "flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors select-none cursor-pointer";

  const colorClass =
    variant === "dark"
      ? "border-white/20 text-white hover:bg-white/10"
      : "border-gray-200 text-gray-600 hover:bg-gray-100";

  return (
    <button onClick={toggle} className={`${baseClass} ${colorClass}`} title="Switch language">
      <span className={!isAr ? "opacity-40" : ""}  >ع</span>
      <span className="opacity-30">|</span>
      <span className={isAr ? "opacity-40" : ""}>EN</span>
    </button>
  );
}
