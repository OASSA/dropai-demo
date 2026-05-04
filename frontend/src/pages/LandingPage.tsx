import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { LogoFull } from "../components/common/Logo";
import { LanguageSwitcher } from "../components/common/LanguageSwitcher";

const featureKeys = ["eta", "route", "assign", "tracking", "analytics", "alerts"] as const;
const featureIcons = ["🤖", "🗺️", "📦", "📡", "📊", "🔔"];

const statsData = [
  { value: "99.9%", key: "uptime" },
  { value: "2x",    key: "faster" },
  { value: "40%",   key: "cost" },
  { value: "50k+",  key: "shipments" },
];

export default function LandingPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-gray-100 sticky top-0 bg-white/95 backdrop-blur z-20">
        <LogoFull iconSize={38} textSize="md" />
        <div className="flex items-center gap-5">
          <a href="#features" className="hidden md:block text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors">
            {t("landing.nav_features")}
          </a>
          <a href="#stats" className="hidden md:block text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors">
            {t("landing.nav_why")}
          </a>
          <LanguageSwitcher />
          <Link to="/login" className="btn-primary text-sm px-5 py-2">
            {t("landing.nav_signin")}
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-8 pt-20 pb-24 text-center">
        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-50 text-brand-600 text-xs font-bold mb-7 border border-brand-100">
          {t("landing.badge")}
        </span>
        <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight mb-5">
          {t("landing.hero_title")}{" "}
          <span className="text-brand-600">{t("landing.hero_title_highlight")}</span>
        </h1>
        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          {t("landing.hero_desc")}
        </p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link to="/login" className="btn-primary text-base px-7 py-3 shadow-lg shadow-brand-600/25">
            {t("landing.cta_primary")}
          </Link>
          <Link to="/track" className="btn-secondary text-base px-7 py-3">
            {t("landing.cta_track")}
          </Link>
        </div>

        {/* Hero visual hint */}
        <div className="mt-16 grid grid-cols-3 gap-4 max-w-sm mx-auto">
          {["📦 12,480", "✅ 98.2%", "⚡ 2.4h"].map((s) => (
            <div key={s} className="bg-brand-50 border border-brand-100 rounded-2xl p-4 text-center">
              <p className="text-sm font-bold text-gray-800">{s.split(" ")[1]}</p>
              <p className="text-xs text-gray-400 mt-0.5">{s.split(" ")[0]}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats bar */}
      <section id="stats" className="bg-brand-600 py-12">
        <div className="max-w-5xl mx-auto px-8 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {statsData.map((s) => (
            <div key={s.key}>
              <div className="text-4xl font-extrabold text-white">{s.value}</div>
              <div className="text-brand-200 text-sm mt-1">{t(`landing.stats.${s.key}`)}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-5xl mx-auto px-8 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-extrabold text-gray-900">{t("landing.features_title")}</h2>
          <p className="text-gray-500 mt-3 max-w-2xl mx-auto leading-relaxed">
            {t("landing.features_subtitle")}
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-5">
          {featureKeys.map((key, i) => (
            <div key={key} className="card hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 group">
              <div className="text-3xl mb-3">{featureIcons[i]}</div>
              <h3 className="font-bold text-gray-900 mb-2 group-hover:text-brand-600 transition-colors">
                {t(`landing.features.${key}.title`)}
              </h3>
              <p className="text-sm text-gray-500 leading-relaxed">{t(`landing.features.${key}.desc`)}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA section */}
      <section className="bg-gray-950 py-16 text-center">
        <div className="max-w-2xl mx-auto px-8">
          <div className="flex justify-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center">
              <span className="text-2xl">🚀</span>
            </div>
          </div>
          <h2 className="text-3xl font-extrabold text-white mb-4">
            {t("landing.cta_section_title")}
          </h2>
          <p className="text-gray-400 mb-8 leading-relaxed">{t("landing.cta_section_desc")}</p>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-brand-600 text-white font-bold hover:bg-brand-700 transition-colors text-base shadow-lg shadow-brand-900/40"
          >
            {t("landing.cta_button")}
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-950 border-t border-white/5 py-6">
        <div className="max-w-5xl mx-auto px-8 flex flex-col md:flex-row items-center justify-between gap-3">
          <LogoFull iconSize={28} textSize="sm" className="[&_span]:text-white" />
          <p className="text-xs text-gray-500">
            © {new Date().getFullYear()} DropAI Inc. {t("landing.footer")}
          </p>
        </div>
      </footer>
    </div>
  );
}
