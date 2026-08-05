import type {
  Article,
  ArticlesListForAdminParams,
  ArticlesListForAdminResBody,
  ArticlesListForReaderParams,
  ArticlesListForReaderResBody,
  CreateArticleReqBody,
  PublicArticle,
  UpdateArticleReqBody,
} from "~/schemas/articles";
import { apiClient } from "./apiClient";

export async function getArticleById(id: string): Promise<Article> {
  return apiClient<Article>(`/articles/id/${id}`);
}

export async function createArticle(data: CreateArticleReqBody): Promise<void> {
  return apiClient<void>("/articles", {
    method: "POST",
    body: data,
  });
}

export async function updateArticle(
  id: string,
  data: UpdateArticleReqBody,
): Promise<void> {
  return apiClient<void>(`/articles/${id}`, {
    method: "PATCH",
    body: data,
  });
}

export async function getPublicArticles(
  params: ArticlesListForReaderParams,
): Promise<ArticlesListForReaderResBody> {
  return apiClient<ArticlesListForReaderResBody>(`/articles/list/reader`, {
    method: "GET",
    params,
  });
}

export async function getPublicArticleBySlug(
  slug: string,
): Promise<PublicArticle> {
  return apiClient<PublicArticle>(`/articles/slug/${slug}`, {
    method: "GET",
  });
}

export async function getAdminArticles(
  params: ArticlesListForAdminParams,
): Promise<ArticlesListForAdminResBody> {
  return apiClient<ArticlesListForAdminResBody>("/articles/list/admin", {
    method: "GET",
    params,
  });
}
