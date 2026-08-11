import {
  keepPreviousData,
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useEffect, useState } from "react";
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
  returnedFromBilling?: boolean,
) {
  const [, setSearchParams] = useSearchParams();
  const [isTimedOut, setIsTimedOut] = useState(false);
  const shouldSync = returnedFromBilling && !isTimedOut;

  // stop polling after 10 seconds if backend hasn't updated
  useEffect(() => {
    if (shouldSync) {
      const timer = setTimeout(() => {
        setIsTimedOut(true);
      }, 10000);

      return () => clearTimeout(timer);
    }
  }, [shouldSync]);

  const query = useQuery<PublicArticle, ApiError>({
    queryKey: articleKeys.detail(slug),
    queryFn: () => getPublicArticleBySlug(slug),
    enabled: Boolean(slug),
    refetchInterval: (queryState) => {
      const article = queryState.state.data;
      const isLocked = Boolean(article && article.access_status === "teaser");
      if (shouldSync && isLocked) {
        return 1500; // poll every 1.5 seconds
      }
      return false; // stop polling
    },
  });

  const article = query.data;
  const unlocked = Boolean(article && article.access_status !== "teaser");

  // (optional) remove `returnedFromBilling` search param when unlocked or timed out
  useEffect(() => {
    if ((shouldSync && unlocked) || isTimedOut) {
      setSearchParams(
        (prevParams) => {
          const newParams = new URLSearchParams(prevParams);
          newParams.delete("returnedFromBilling");
          return newParams;
        },
        { replace: true },
      );
    }
  }, [shouldSync, unlocked, isTimedOut, setSearchParams]);

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
