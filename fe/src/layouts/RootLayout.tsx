import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useLogoutMutation } from "~/api/auth.hooks";
import { Button } from "~/components/ui/button";
import { Spinner } from "~/components/ui/spinner";
import { useAuth } from "~/contexts/AuthContext";
import { cn } from "~/lib/utils";
import { PATHS } from "~/utils/paths";

function Header() {
  const getNavItemCls = ({ isActive }: { isActive: boolean }) =>
    cn(
      "text-lg font-medium",
      isActive
        ? "text-blue-600 font-semibold"
        : "text-gray-600 hover:text-gray-900",
    );

  const { user, isAuthenticated, isLoading: authPending } = useAuth();
  const navigate = useNavigate();
  const { mutateAsync: logout, isPending: logoutPending } = useLogoutMutation();

  const handleLogout = async () => {
    try {
      await logout();
      navigate(PATHS.HOME);
    } catch (err) {
      toast.error(`Logout error: ${err}`);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/95 backdrop-blur-xs">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <nav className="flex items-center gap-6">
          <NavLink to={PATHS.HOME} className={getNavItemCls}>
            Home
          </NavLink>
          {user?.is_admin && (
            <NavLink to={PATHS.ADMIN.ROOT} className={getNavItemCls}>
              Admin
            </NavLink>
          )}
          {!authPending && !isAuthenticated && (
            <NavLink to={PATHS.LOGIN} className={getNavItemCls}>
              Login
            </NavLink>
          )}
        </nav>

        {user && (
          <div className="flex items-center gap-4 text-sm">
            <span className="text-gray-600">
              Hello <strong className="text-gray-900">{user.email}</strong>
            </span>
            <Button
              variant="default"
              size="sm"
              className="hover:bg-gray-600"
              onClick={handleLogout}
              disabled={logoutPending}
            >
              {logoutPending ? <Spinner /> : "Logout"}
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}

export default function RootLayout() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
