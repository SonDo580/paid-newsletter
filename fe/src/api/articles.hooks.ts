import {
  keepPreviousData,
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  type Article,
  type ArticlesListForAdminParams,
  type CreateArticleReqBody,
  type PublicArticle,
  type UpdateArticleReqBody,
} from "~/schemas/articles";
import type { ApiError } from "./apiError";
import {
  createArticle,
  getAdminArticles,
  getArticleById,
  getPublicArticleBySlug,
  getPublicArticles,
  updateArticle,
} from "./articles";

export const articleKeys = {
  all: ["articles"] as const,
  publicList: () => [...articleKeys.all, "publicList"] as const,
  adminList: (params: ArticlesListForAdminParams) =>
    [...articleKeys.all, "adminList", params] as const,
  detail: (idOrSlug: string) =>
    [...articleKeys.all, "detail", idOrSlug] as const,
};

export function useArticleByIdQuery(id?: string) {
  return useQuery<Article, ApiError>({
    queryKey: articleKeys.detail(id),
    queryFn: () => getArticleById(id),
    enabled: Boolean(id),
  });
}

export function usePublicArticleBySlugQuery(
  slug?: string,
  checkoutSuccess?: boolean,
) {
  const query = useQuery<PublicArticle, ApiError>({
    queryKey: articleKeys.detail(slug),
    queryFn: () => getPublicArticleBySlug(slug),
    enabled: Boolean(slug),
    refetchInterval: (queryState) => {
      const article = queryState.state.data;
      const isLocked = Boolean(article && article.access_status === "teaser");
      if (checkoutSuccess && isLocked) {
        return 1500; // poll every 1.5 seconds
      }
      return false; // stop polling
    },
  });

  // (optional) remove `checkoutSuccess` search param
  const [, setSearchParams] = useSearchParams();
  const article = query.data;
  const unlocked = Boolean(article && article.access_status !== "teaser");
  useEffect(() => {
    if (checkoutSuccess && unlocked) {
      setSearchParams(
        (prevParams) => {
          const newParams = new URLSearchParams(prevParams);
          newParams.delete("checkoutSuccess");
          return newParams;
        },
        { replace: true },
      );
    }
  }, [checkoutSuccess, unlocked, setSearchParams]);

  return query;
}

export function usePublicArticlesInfiniteQuery(limit: number = 10) {
  return useInfiniteQuery({
    queryKey: articleKeys.publicList(),
    queryFn: ({ pageParam }) => getPublicArticles({ limit, cursor: pageParam }),
    initialPageParam: undefined,
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
  });
}

export function useAdminArticlesQuery(params: ArticlesListForAdminParams) {
  return useQuery({
    queryKey: articleKeys.adminList(params),
    queryFn: () => getAdminArticles(params),
    placeholderData: keepPreviousData,
  });
}

export function useCreateArticleMutation() {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, CreateArticleReqBody>({
    mutationFn: (data) => createArticle(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: articleKeys.all });
    },
  });
}

export function useUpdateArticleMutation(id: string) {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, UpdateArticleReqBody>({
    mutationFn: (data) => updateArticle(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: articleKeys.all });
    },
  });
}
