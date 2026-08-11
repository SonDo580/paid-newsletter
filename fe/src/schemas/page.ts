import z from "zod";

export const loginPageQuerySchema = z.object({
  redirect: z.string().optional(),
});
export type LoginPageQuery = z.infer<typeof loginPageQuerySchema>;

export const articlePageQuerySchema = z.object({
  checkoutSuccess: z.coerce.boolean().optional(),
});
export type ArticlePageQuery = z.infer<typeof articlePageQuerySchema>;
