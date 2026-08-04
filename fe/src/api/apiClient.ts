import type { QueryParams } from "~/schemas/shared";
import { ApiError } from "./apiError";

const BASE_URL = import.meta.env.VITE_API_BASE_URL.replace(/\/+$/, "");

interface FetchOptions extends RequestInit {
  body?: any;
  params?: QueryParams;
}

function buildUrl(endpoint: string, params?: QueryParams): string {
  const url = new URL(`${BASE_URL}/${endpoint.replace(/^\/+/, "")}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null) {
        return;
      }

      if (Array.isArray(value)) {
        value.forEach((item) => {
          if (item !== undefined && item !== null) {
            url.searchParams.append(key, String(item));
          }
        });
      } else {
        url.searchParams.append(key, String(value));
      }
    });
  }

  return url.toString();
}

export async function apiClient<T>(
  endpoint: string,
  { body, params, headers, ...extraConfig }: FetchOptions = {},
): Promise<T> {
  const url = buildUrl(endpoint, params);
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
