import { z } from "zod";
import { VALIDATION_MSG } from "~/utils/form";
import type { PrimitiveParam, SortOrder } from "./shared";

const minTitleLength = 10;
const maxTitleLength = 150;
const minContentLength = 100;
const minSlugLength = 3;
const maxSlugLength = 150;
const slugRegex = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

const titleSchema = z
  .string()
  .trim()
  .min(minTitleLength, VALIDATION_MSG.min("Title", minTitleLength))
  .max(maxTitleLength, VALIDATION_MSG.max("Title", maxTitleLength));

const contentSchema = z
  .string()
  .trim()
  .min(minContentLength, VALIDATION_MSG.min("Content", minContentLength));

export const articleFormSchema = z.object({
  title: titleSchema,
  content: contentSchema,
  slug: z
    .string()
    .trim()
    .min(minSlugLength, VALIDATION_MSG.min("Slug", minSlugLength))
    .max(maxSlugLength, VALIDATION_MSG.max("Slug", maxSlugLength))
    .regex(
      slugRegex,
      "Slug must contains only lowercase letters, numbers, in-between hyphens.",
    ),
  is_free: z.boolean(),
  is_published: z.boolean(),
});

export type ArticleFormValues = z.infer<typeof articleFormSchema>;

export type CreateArticleReqBody = ArticleFormValues;
export type UpdateArticleReqBody = Partial<Omit<ArticleFormValues, "slug">>;

export interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  is_free: boolean;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  published_at?: string | null;
}

export type ArticlesListForReaderParams = {
  limit?: number;
  cursor?: string;
  [key: string]: PrimitiveParam;
};

interface ArticlesListItemForReader {
  title: string;
  slug: string;
}

export interface ArticlesListForReaderResBody {
  items: ArticlesListItemForReader[];
  next_cursor: string | null;
}

type AccessStatus = "full" | "teaser";

export interface PublicArticle {
  title: string;
  slug: string;
  content: string;
  published_at: string; // ISO datetime string
  access_status: AccessStatus;
}

export type ArticleSortBy =
  "id" | "title" | "created_at" | "updated_at" | "published_at";

export interface ArticlesListForAdminParams {
  page?: number;
  page_size?: number;
  keyword?: string;
  is_free?: boolean;
  is_published?: boolean;
  sort_by?: ArticleSortBy;
  sort_order?: SortOrder;
  [key: string]: PrimitiveParam;
}

export interface ArticlesListItemForAdmin {
  id: number;
  title: string;
  slug: string;
  is_free: boolean;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  published_at: string | null;
}

export interface ArticlesListForAdminResBody {
  items: ArticlesListItemForAdmin[];
  total: number;
}
