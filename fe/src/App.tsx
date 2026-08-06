import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Article from "./pages/Article";
import AdminLayout from "./layouts/AdminLayout";
import AdminArticles from "./pages/admin/AdminArticles";
import NotFound from "./pages/NotFound";
import { PATHS } from "~/utils/paths";
import CreateArticle from "./pages/admin/CreateArticle";
import EditArticle from "./pages/admin/EditArticle";
import RootLayout from "./layouts/RootLayout";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";

function App() {
  return (
    <AuthProvider>
      <Toaster position="top-right" richColors />

      <BrowserRouter>
        <Routes>
          <Route element={<RootLayout />}>
            {/* Public */}
            <Route path={PATHS.HOME} element={<Home />} />
            <Route path={PATHS.LOGIN} element={<Login />} />
            <Route path="/articles/:slug" element={<Article />} />

            {/* Admin */}
            <Route element={<ProtectedRoute requireAdmin />}>
              <Route path={PATHS.ADMIN.ROOT} element={<AdminLayout />}>
                <Route
                  index
                  element={<Navigate to={PATHS.ADMIN.ARTICLES} replace />}
                />
                <Route path="articles" element={<AdminArticles />} />
                <Route path="articles/create" element={<CreateArticle />} />
                <Route path="articles/:id" element={<EditArticle />} />
              </Route>
            </Route>

            {/* Fallback */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
