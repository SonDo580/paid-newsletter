import type { FieldValues, FormState } from "react-hook-form";

export const VALIDATION_MSG = {
  min: (field: string, count: number) =>
    `${field} must have at least ${count} character(s)`,
  max: (field: string, count: number) =>
    `${field} can have at most ${count} character(s)`,
  required: (field: string) => `${field} is required`,
};

// Extract only field values that were modified by user.
export function getDirtyValues<T extends FieldValues>(
  dirtyFields: FormState<T>["dirtyFields"],
  allValues: T,
): Partial<T> {
  const dirtyValues: Partial<T> = {};
  (Object.keys(dirtyFields) as Array<keyof T>).forEach((key) => {
    if (dirtyFields[key as keyof typeof dirtyFields]) {
      dirtyValues[key] = allValues[key];
    }
  });
  return dirtyValues;
}
