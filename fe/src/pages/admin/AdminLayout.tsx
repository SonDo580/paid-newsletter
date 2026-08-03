import { NavLink, Outlet } from "react-router-dom";
import { PATHS } from "~/constants/paths";

export default function AdminLayout() {
  const getNavItemCls = ({ isActive }: { isActive: boolean }) => `
    rounded-md px-2 py-2 ${isActive ? "bg-blue-50 text-blue-700" : "text-gray-700 hover:bg-gray-100"}
    `;

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r border-gray-200 p-3">
        <h3 className="mb-6 text-xl font-bold tracking-tight">Admin Panel</h3>
        <nav className="flex flex-col gap-3">
          <NavLink to={PATHS.ADMIN.ARTICLES} className={getNavItemCls} end>
            All Articles
          </NavLink>
          <NavLink to={PATHS.ADMIN.CREATE_ARTICLE} className={getNavItemCls}>
            Create Article
          </NavLink>
          <hr className="my-2 border-gray-200" />
          <NavLink to={PATHS.HOME} className={getNavItemCls}>
            Back to Public Site
          </NavLink>
        </nav>
      </aside>

      <main className="flex-1 p-6">
        <div className="rounded-lg border border-gray-200 p-6 shadow-xs">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
