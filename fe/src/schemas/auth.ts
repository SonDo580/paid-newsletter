import z from "zod";

export const loginSchema = z.object({
  email: z.email(),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
export type LoginReqBody = LoginFormValues;
