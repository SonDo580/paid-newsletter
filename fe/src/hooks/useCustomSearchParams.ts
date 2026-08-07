import { useSearchParams } from "react-router-dom";
import type z from "zod";

/* Extract and validate URL search parameters against a Zod schema */
export function useCustomSearchParams<T extends z.ZodType>(schema: T): z.infer<T> {
  const [searchParams] = useSearchParams();
  const rawParams: Record<string, string> = {};
  searchParams.forEach((value, key) => {
    rawParams[key] = value;
  });
  return schema.parse(rawParams);
}
