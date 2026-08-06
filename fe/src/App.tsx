import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";
import { PATHS } from "~/utils/paths";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";
import AdminLayout from "./layouts/AdminLayout";
import RootLayout from "./layouts/RootLayout";
import AdminArticlesPage from "./pages/admin/AdminArticlesPage";
import CreateArticlePage from "./pages/admin/CreateArticlePage";
import EditArticlePage from "./pages/admin/EditArticlePage";
import ArticlePage from "./pages/ArticlePage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";

function App() {
  return (
    <AuthProvider>
      <Toaster position="top-right" richColors />

      <BrowserRouter>
        <Routes>
          <Route element={<RootLayout />}>
            {/* Public */}
            <Route path={PATHS.HOME} element={<HomePage />} />
            <Route path={PATHS.LOGIN} element={<LoginPage />} />
            <Route path="/articles/:slug" element={<ArticlePage />} />

            {/* Admin */}
            <Route element={<ProtectedRoute requireAdmin />}>
              <Route path={PATHS.ADMIN.ROOT} element={<AdminLayout />}>
                <Route
                  index
                  element={<Navigate to={PATHS.ADMIN.ARTICLES} replace />}
                />
                <Route path="articles" element={<AdminArticlesPage />} />
                <Route path="articles/create" element={<CreateArticlePage />} />
                <Route path="articles/:id" element={<EditArticlePage />} />
              </Route>
            </Route>

            {/* Fallback */}
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
