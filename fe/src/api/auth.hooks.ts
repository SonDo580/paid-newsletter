import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import type {
  CurrentUser,
  LoginReqBody,
  OAuthAction,
  OAuthAuthorizeParams,
  OAuthProvider,
} from "~/schemas/auth";
import { buildUrl } from "~/utils/url";
import { API_BASE_URL } from "./apiClient";
import type { ApiError } from "./apiError";
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
      queryClient.setQueryData(authKeys.profile, null);
      queryClient.removeQueries({
        predicate: (query) => query.queryKey[0] !== authKeys.profile[0],
      });
    },
  });
}

interface StartOAuthOptions {
  provider: OAuthProvider;
  action: OAuthAction;
  redirectPath?: string;
}

export function useOAuthFlow() {
  const [pendingProvider, setPendingProvider] = useState<OAuthProvider | null>(
    null,
  );

  const startOAuth = ({
    provider,
    action,
    redirectPath,
  }: StartOAuthOptions) => {
    setPendingProvider(provider);

    const params: OAuthAuthorizeParams = {
      action,
      redirect_path: redirectPath,
    };
    const authorizeUrl = buildUrl(
      API_BASE_URL,
      `/auth/${provider}/authorize`,
      params,
    );

    window.location.href = authorizeUrl;
  };

  return {
    startOAuth,
    pendingProvider,
  };
}
