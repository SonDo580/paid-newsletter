import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "~/contexts/AuthContext";
import NotFound from "~/pages/NotFound";
import { PATHS } from "~/utils/paths";

interface ProtectedRouteProps {
  requireAdmin?: boolean;
}

export function ProtectedRoute({ requireAdmin = false }: ProtectedRouteProps) {
  const { user, authPending } = useAuth();

  if (authPending) {
    return <div>Loading...</div>;
  }
  if (!user) {
    return <Navigate to={PATHS.LOGIN} />;
  }
  if (requireAdmin && !user.is_admin) {
    return <NotFound />;
  }
  return <Outlet />;
}
