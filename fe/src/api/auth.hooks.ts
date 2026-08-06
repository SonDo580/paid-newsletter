import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { ApiError } from "./apiError";
import type { CurrentUser, LoginReqBody } from "~/schemas/auth";
import { getMe, login, logout } from "./auth";

export const authKeys = {
  profile: ["me"] as const,
};

export function useCurrentUserQuery() {
  return useQuery<CurrentUser, ApiError>({
    queryKey: authKeys.profile,
    queryFn: getMe,
    retry: false,
    staleTime: Infinity, // only explicit invalidation
  });
}

export function useLoginMutation() {
  const queryClient = useQueryClient();

  return useMutation<void, ApiError, LoginReqBody>({
    mutationFn: (data) => login(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.profile });
    },
  });
}

export function useLogoutMutation() {
  const queryClient = useQueryClient();

  return useMutation<void, ApiError, void>({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.clear();
    },
  });
}
