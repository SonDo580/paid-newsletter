import { useMutation } from "@tanstack/react-query";
import type { ApiError } from "./apiError";
import type { LoginReqBody } from "~/schemas/auth";
import { login } from "./auth";

export function useLoginMutation() {
  return useMutation<void, ApiError, LoginReqBody>({
    mutationFn: (data) => login(data),
  });
}