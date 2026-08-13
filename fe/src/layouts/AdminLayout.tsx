import { NavLink, Outlet } from "react-router-dom";
import { PATHS } from "~/paths";

export default function AdminLayout() {
  const getNavItemCls = ({ isActive }: { isActive: boolean }) => `
    rounded-md px-2 py-2 ${isActive ? "bg-blue-50 text-blue-700" : "text-gray-700 hover:bg-gray-100"}
    `;

  return (
    <div className="flex">
      <aside className="w-48 shrink-0 border-r border-gray-200 bg-white p-3">
        <h3 className="mb-6 text-xl font-bold tracking-tight">Admin Panel</h3>
        <nav className="flex flex-col gap-2">
          <NavLink to={PATHS.ADMIN.ARTICLES} className={getNavItemCls} end>
            All Articles
          </NavLink>
        </nav>
      </aside>

      <main className="flex-1 min-w-0 p-6">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-xs">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
