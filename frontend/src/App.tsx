import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";

import { ProtectedRoute } from "./components/common/ProtectedRoute";
import { Layout } from "./components/layout/Layout";
import { useAuthStore } from "./store/authStore";

import LandingPage       from "./pages/LandingPage";
import LoginPage         from "./pages/LoginPage";
import TrackingPage      from "./pages/TrackingPage";
import DashboardPage     from "./pages/DashboardPage";
import ShipmentsPage     from "./pages/ShipmentsPage";
import DriversPage       from "./pages/DriversPage";
import WarehousesPage    from "./pages/WarehousesPage";
import CompaniesPage     from "./pages/CompaniesPage";
import AnalyticsPage     from "./pages/AnalyticsPage";
import NotificationsPage from "./pages/NotificationsPage";

export default function App() {
  const { isAuthenticated, fetchMe } = useAuthStore();
  const { i18n } = useTranslation();

  // Keep <html dir> in sync with language
  useEffect(() => {
    document.documentElement.dir  = i18n.language === "ar" ? "rtl" : "ltr";
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  // Re-hydrate user on hard refresh
  useEffect(() => {
    if (isAuthenticated) fetchMe();
  }, []);

  return (
    <BrowserRouter>
      <Toaster
        position={i18n.language === "ar" ? "top-left" : "top-right"}
        toastOptions={{
          duration: 3500,
          style: { fontFamily: "Cairo, Inter, sans-serif" },
        }}
      />
      <Routes>
        {/* Public */}
        <Route path="/"      element={<LandingPage />} />
        <Route path="/track" element={<TrackingPage />} />
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />

        {/* Protected app shell */}
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="/dashboard"     element={<DashboardPage />} />
          <Route path="/shipments"     element={<ShipmentsPage />} />
          <Route path="/drivers"       element={<ProtectedRoute roles={["super_admin","company_admin","warehouse_manager"]}><DriversPage /></ProtectedRoute>} />
          <Route path="/warehouses"    element={<ProtectedRoute roles={["super_admin","company_admin","warehouse_manager"]}><WarehousesPage /></ProtectedRoute>} />
          <Route path="/companies"     element={<ProtectedRoute roles={["super_admin"]}><CompaniesPage /></ProtectedRoute>} />
          <Route path="/analytics"     element={<ProtectedRoute roles={["super_admin","company_admin"]}><AnalyticsPage /></ProtectedRoute>} />
          <Route path="/notifications" element={<NotificationsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
