import { Navigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";
import { UserRole } from "../../types";

interface Props {
  children: React.ReactNode;
  roles?: UserRole[];
}

export function ProtectedRoute({ children, roles }: Props) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (roles && user && !roles.includes(user.role.name)) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}
