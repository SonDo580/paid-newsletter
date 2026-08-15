import z from "zod";
import type { PrimitiveParam } from "./shared";

export const loginSchema = z.object({
  email: z.email(),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export interface LoginReqBody {
  email: string;
  redirect_path?: string;
}

export type OAuthAction = "connect" | "login";

export interface OAuthAuthorizeParams {
  action: OAuthAction;
  redirect_path?: string;
  [key: string]: PrimitiveParam;
}

export type OAuthProvider = "google";

export interface OAuthAccount {
  provider: OAuthProvider;
  identifier: string;
}

interface Reader {
  id: number;
  email: string;
  created_at: string;
  verified_at: string;
  has_stripe_profile: boolean;
  oauth_accounts: OAuthAccount[];
}

export interface CurrentUser {
  email: string;
  is_admin: boolean;
  reader?: Reader;
}
