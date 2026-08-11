import type { QueryParams } from "~/schemas/shared";
import { buildUrl } from "~/utils/url";
import { ApiError } from "./apiError";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

interface FetchOptions extends RequestInit {
  body?: any;
  params?: QueryParams;
}

export async function apiClient<T>(
  endpoint: string,
  { body, params, headers, ...extraConfig }: FetchOptions = {},
): Promise<T> {
  const url = buildUrl(API_BASE_URL, endpoint, params);
  const config: RequestInit = {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    ...extraConfig,
  };
  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(url, config);
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new ApiError(response.status, errorData);
  }
  if (response.status === 204) {
    return null as T;
  }
  return response.json();
}
