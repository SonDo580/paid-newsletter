export const PATHS = {
  HOME: "/",
  LOGIN: "/login",
  ARTICLE: (slug: string) => `/articles/${slug}`,
  ACCOUNT: "/account",
  ADMIN: {
    ROOT: "/admin",
    ARTICLES: "/admin/articles",
    CREATE_ARTICLE: "/admin/articles/create",
    EDIT_ARTICLE: (id: number) => `/admin/articles/${id}`,
  },
};
