import type { LoginReqBody } from "~/schemas/auth";
import { apiClient } from "./apiClient";

export async function login(data: LoginReqBody): Promise<void> {
  return apiClient<void>("/auth/login", {
    method: "POST",
    body: data,
  });
}
