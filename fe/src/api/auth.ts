import type { CurrentUser, LoginReqBody } from "~/schemas/auth";
import { apiClient } from "./apiClient";

export async function login(data: LoginReqBody): Promise<void> {
  return apiClient<void>("/auth/login", {
    method: "POST",
    body: data,
  });
}

export async function logout(): Promise<void> {
  return apiClient<void>("/auth/logout", {
    method: "POST",
  });
}

export async function getMe(): Promise<CurrentUser> {
  return apiClient<CurrentUser>("/users/me", {
    method: "GET",
  });
}
