import type { QueryParams } from "~/schemas/shared";

function createSearchParams(params?: QueryParams): URLSearchParams {
  const searchParams = new URLSearchParams();
  if (!params) {
    return searchParams;
  }

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) {
      return;
    }

    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item !== undefined && item !== null) {
          searchParams.append(key, String(item));
        }
      });
    } else {
      searchParams.append(key, String(value));
    }
  });

  return searchParams;
}

export function buildPath(path: string, params?: QueryParams): string {
  const searchParams = createSearchParams(params);
  const queryString = searchParams.toString();
  return queryString ? `${path}?${queryString}` : path;
}

export function buildUrl(
  baseUrl: string,
  path: string,
  params?: QueryParams,
): string {
  const cleanBase = baseUrl.replace(/\/+$/, ""); // remove trailing slash
  const cleanPath = path.replace(/^\/+/, ""); // remove leading slash
  const url = new URL(`${cleanBase}/${cleanPath}`);

  const searchParams = createSearchParams(params);
  searchParams.forEach((value, key) => {
    url.searchParams.append(key, value);
  });

  return url.toString();
}
