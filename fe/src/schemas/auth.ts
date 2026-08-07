import z from "zod";

export const loginSchema = z.object({
  email: z.email(),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export interface LoginReqBody {
  email: string;
  redirect_path?: string;
}

export interface CurrentUser {
  email: string;
  is_admin: boolean;
}
