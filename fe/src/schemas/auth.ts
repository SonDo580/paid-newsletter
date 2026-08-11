import z from "zod";

export const loginSchema = z.object({
  email: z.email(),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export interface LoginReqBody {
  email: string;
  redirect_path?: string;
}

interface Reader {
  id: number;
  email: string;
  created_at: string;
  verified_at: string;
  has_stripe_profile: boolean;
}

export interface CurrentUser {
  email: string;
  is_admin: boolean;
  reader?: Reader;
}
