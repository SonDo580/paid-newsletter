export type PrimitiveParam = string | number | boolean | undefined | null;
export type QueryParams = Record<string, PrimitiveParam | PrimitiveParam[]>;

export type SortOrder = "asc" | "desc";
