import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Article from "./pages/Article";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminArticles from "./pages/admin/AdminArticles";
import ArticleForm from "./pages/admin/ArticleForm";
import NotFound from "./pages/NotFound";
import { PATHS } from "~/utils/paths";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path={PATHS.HOME} element={<Home />} />
        <Route path={PATHS.LOGIN} element={<Login />} />
        <Route path="/articles/:slug" element={<Article />} />

        {/* Admin */}
        <Route path={PATHS.ADMIN.ROOT} element={<AdminLayout />}>
          <Route
            index
            element={<Navigate to={PATHS.ADMIN.ARTICLES} replace />}
          />
          <Route path="articles" element={<AdminArticles />} />
          <Route path="articles/create" element={<ArticleForm />} />
          <Route path="articles/:id" element={<ArticleForm />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
