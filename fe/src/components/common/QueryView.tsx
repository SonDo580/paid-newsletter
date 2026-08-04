import type { ReactNode } from "react";

interface QueryViewProps {
  isLoading: boolean;
  error: Error | null;
  children: ReactNode;
}

export function QueryView({ isLoading, error, children }: QueryViewProps) {
  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (error) {
    return <div className="text-read-600">{error.message}</div>;
  }
  return children;
}
