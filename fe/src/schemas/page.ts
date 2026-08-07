import z from "zod";

export const loginPageQuerySchema = z.object({
  redirect: z.string().optional(),
});

export type LoginPageQuery = z.infer<typeof loginPageQuerySchema>;

export const checkoutPageQuerySchema = z.object({
  articleId: z.coerce.number().optional(),
  redirect: z.string(),
});

export type CheckoutPageQuery = z.infer<typeof checkoutPageQuerySchema>;
