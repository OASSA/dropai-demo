import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import { LogoFull } from "../components/common/Logo";
import { LanguageSwitcher } from "../components/common/LanguageSwitcher";
import toast from "react-hot-toast";

export default function LoginPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        t("auth.loginFailed");
      toast.error(msg);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-orange-50 flex items-center justify-center p-4">
      {/* Language switcher top-right */}
      <div className="fixed top-4 end-4">
        <LanguageSwitcher />
      </div>

      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-3">
            <LogoFull iconSize={52} textSize="xl" />
          </div>
          <p className="text-gray-500 text-sm">{t("auth.platform")}</p>
        </div>

        <div className="card shadow-xl border-brand-100/60">
          {/* Card header accent */}
          <div className="h-1 -mt-6 -mx-6 mb-6 rounded-t-2xl bg-gradient-to-r from-brand-600 to-brand-400" />

          <h2 className="text-xl font-bold text-gray-900 mb-1">{t("auth.welcome")}</h2>
          <p className="text-sm text-gray-500 mb-6">{t("auth.subtitle")}</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">{t("auth.email")}</label>
              <input
                type="email"
                required
                className="input"
                placeholder={t("auth.emailPlaceholder")}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                dir="ltr"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">{t("auth.password")}</label>
              <input
                type="password"
                required
                className="input"
                placeholder={t("auth.passwordPlaceholder")}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                dir="ltr"
              />
            </div>
            <button type="submit" disabled={isLoading} className="btn-primary w-full justify-center py-3 text-base shadow-lg shadow-brand-600/25">
              {isLoading ? t("auth.signingIn") : t("auth.signIn")}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-5">
            {t("auth.trackLink")}{" "}
            <Link to="/track" className="text-brand-600 font-semibold hover:underline">
              {t("auth.trackHere")}
            </Link>
          </p>
        </div>

        <p className="text-center text-xs text-gray-400 mt-4 font-mono">
          {t("auth.defaultCredentials")}
        </p>
      </div>
    </div>
  );
}
