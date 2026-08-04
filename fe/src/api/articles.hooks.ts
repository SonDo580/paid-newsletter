import {
  type Article,
  type CreateArticleReqBody,
  type UpdateArticleReqBody,
} from "~/schemas/articles";
import type { ApiError } from "./apiError";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createArticle, getArticleById, updateArticle } from "./articles";

export const articleKeys = {
  all: ["articles"] as const,
  lists: () => [...articleKeys.all, "list"] as const,
  details: () => [...articleKeys.all, "detail"] as const,
  detail: (id: string) => [...articleKeys.details(), id] as const,
};

export function useArticleQuery(id: string) {
  return useQuery<Article, ApiError>({
    queryKey: articleKeys.detail(id),
    queryFn: () => getArticleById(id),
    enabled: !!id,
  });
}

export function useCreateArticleMutation() {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, CreateArticleReqBody>({
    mutationFn: (data) => createArticle(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });
    },
  });
}

export function useUpdateArticleMutation(id: string) {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, UpdateArticleReqBody>({
    mutationFn: (data) => updateArticle(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });
      queryClient.invalidateQueries({ queryKey: articleKeys.detail(id) });
    },
  });
}
