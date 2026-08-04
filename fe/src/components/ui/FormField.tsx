import type { ReactNode } from "react";

interface FormFieldProps {
  label: string;
  error?: string;
  children: ReactNode;
}

export function FormField({ label, error, children }: FormFieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label>{label}</label>
      {children}
      {error && <span className="text-sm text-red-600">{error}</span>}
    </div>
  );
}
